#!/usr/bin/env python
"""참조 결속(reference binding) 프로브 — 이미지 간 attention은 무엇에 쓰이는가 (docs/41_reference_binding_prereg.md).

기존 관찰(docs/40 §2.5): 이미지 간 차단은 서수 지시 질문("first image")에서만 AUC를 무너뜨렸다.
단, 그때는 (a) 경계 토큰까지 함께 끊었고 (b) 내용 지시 질문에서는 재지 않았다. 이 스크립트가 둘을 가른다.

PART A — 서수 지시, 사진 2장 (pairs.csv 셀1·2, 300행 × 배치 2종)
  orig  [관련, 방해] + "first image"   /   swap  [방해, 관련] + "second image"
  S_REL / S_DIST : 관련·방해 사진을 각각 단독으로 물은 margin (어느 사진을 읽는지 가늠하는 기준)
PART B — 내용 지시 (anchor_items 600문항, K=2·3): "In the image that contains {anchor}, ..."
PART C — 서수 지시, **PART B와 같은 사진·같은 객체·같은 정답** (지시 방식만 다름): "In the {ord} image, ..."

조건 (뒤 사진 j가 앞 사진 i를 보는 경로만 다룬다. 질문 토큰은 항상 전부 본다):
  M        무개입
  X_ALL    j 전체 → i 전체 (경계 토큰 포함)                = 기존 XIMG/ISO0
  X_COLD   j 전체 → i의 경계 토큰(vision_start/end)만      "앞 사진의 경계가 안 보임"
  X_COLP   j 전체 → i의 패치만                             "앞 사진의 내용이 안 보임"
  X_ROWD   j의 경계 토큰 → i 전체                          "뒤 사진의 경계가 앞을 못 봄"
  X_ROWP   j의 패치 → i 전체                               "뒤 사진의 패치가 앞을 못 봄"
  XF{L}    X_ALL을 L층부터만 (PART A)                      언제까지 필요한가
  XU{L}    X_ALL을 0..L-1층에서만 (PART A)                 언제부터 충분한가
  LBL_M / LBL_X_ALL   "Picture i:" 라벨 템플릿에서 무개입 / X_ALL   라벨이 서수를 대신하는가
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
import torch
from sourcedepth.config import (COCO_IMG_DIR, PAIRS_CSV, PROMPT_SINGLE, RESULTS_DIR, SEED, TAG,
                                TEMPLATE_CHOICE, TEMPLATE_FALLBACK)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"refbind{TAG}.jsonl"
ITEMS = RESULTS_DIR / "anchor_items.json"
ORD = ["first", "second", "third"]
P_ORD = "In the {ord} image, is there {obj}? Answer with Yes or No."
P_ANCHOR = "In the image that contains {anchor}, is there {obj}? Answer with Yes or No."
DEPTHS = [2, 4, 8, 12, 16]
SPLIT = ["X_ALL", "X_COLD", "X_COLP", "X_ROWD", "X_ROWP"]


def art(name): return "an" if name[0] in "aeiou" else "a"


def rules_for(cond, sp):
    """조건명 → (kind, rules). kind ∈ {None, 'pathway', 'band'}."""
    k = len(sp)
    pp = [(s + 1, e - 1) for s, e in sp]
    dl = [[(s, s), (e, e)] for s, e in sp]
    ji = [(j, i) for j in range(k) for i in range(j)]
    if cond in ("M", "LBL_M", "S_REL", "S_DIST"):
        return None, None
    if cond in ("X_ALL", "LBL_X_ALL"):
        return "pathway", [(0, sp[j], sp[i]) for j, i in ji]
    if cond == "X_COLD":
        return "pathway", [(0, sp[j], d) for j, i in ji for d in dl[i]]
    if cond == "X_COLP":
        return "pathway", [(0, sp[j], pp[i]) for j, i in ji]
    if cond == "X_ROWD":
        return "pathway", [(0, d, sp[i]) for j, i in ji for d in dl[j]]
    if cond == "X_ROWP":
        return "pathway", [(0, pp[j], sp[i]) for j, i in ji]
    if cond.startswith("XF"):
        return "pathway", [(int(cond[2:]), sp[j], sp[i]) for j, i in ji]
    if cond.startswith("XU"):
        return "band", [(0, int(cond[2:]) - 1, sp[j], sp[i]) for j, i in ji]
    blocked("41_refbind", f"unknown condition: {cond}", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--parts", default="ABC")
    args = ap.parse_args()
    dump_env("41_reference_binding")
    if not torch.cuda.is_available(): blocked("41_refbind", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]

    with stage("41_reference_binding"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["part"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0

        def run_item(qid, part, meta, paths, q, conds):
            """같은 (사진, 질문)에 대해 조건들을 차례로 실행. 라벨 조건은 입력을 따로 만든다."""
            nonlocal executed
            for tmpl, cs in ((template, [c for c in conds if not c.startswith("LBL_")]),
                             (TEMPLATE_FALLBACK, [c for c in conds if c.startswith("LBL_")])):
                cs = [c for c in cs if (qid, part, c) not in done]
                if not cs: continue
                inputs = build_inputs(processor, paths, q, DEV, tmpl)
                sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
                if len(sp) != len(paths):
                    blocked("41_refbind", f"span != {len(paths)}: {len(sp)}", {"qid": qid})
                seq = int(inputs["input_ids"].shape[1])
                for cond in cs:
                    t0 = time.time()
                    kind, rules = rules_for(cond, sp)
                    ctrl.reset_counter()
                    if kind == "pathway": ctrl.configure_pathway(rules)
                    elif kind == "band": ctrl.configure_band(rules)
                    else: ctrl.disable()
                    try:
                        try: out = model(**inputs, use_cache=False)
                        except torch.cuda.OutOfMemoryError:
                            torch.cuda.empty_cache(); out = model(**inputs, use_cache=False)
                    finally: ctrl.disable()
                    if kind is not None and sum(ctrl.fired.values()) == 0:
                        blocked("41_refbind", "마스크 미발화 (no-op)", {"qid": qid, "cond": cond})
                    p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                    append_jsonl(OUT, {"question_id": qid, "part": part, **meta, "condition": cond,
                                       **p, "correct": p["pred"] == meta["gt"], "n_layers": nlay,
                                       "seq_len": seq, "elapsed_ms": int(1000 * (time.time() - t0)),
                                       "ts": iso_now()})
                    executed += 1
                    del out
                del inputs
                torch.cuda.empty_cache()

        # ── PART A: 서수 지시, 사진 2장, 두 배치 ─────────────
        if "A" in args.parts:
            rows = [r for r in pd.read_csv(PAIRS_CSV).to_dict("records") if int(r["cell"]) in (1, 2)]
            if args.limit: rows = rows[: args.limit]
            conds = (["M"] + SPLIT + [f"XF{L}" for L in DEPTHS] + [f"XU{L}" for L in DEPTHS]
                     + ["LBL_M", "LBL_X_ALL"])
            print(f"PART A: {len(rows)} 행 × 배치 2 × {len(conds)} 조건 + 단독 2")
            for r in rows:
                qid = f"rb{r['question_id']}"
                phrase = obj_phrase(r["article"], r["object"])
                rel = image_path(int(r["image1_id"]), COCO_IMG_DIR)
                dis = image_path(int(r["image2_id"]), COCO_IMG_DIR)
                base = {"k": 2, "cell": int(r["cell"]), "gt": r["gt"]}
                run_item(qid, "S", {**base, "rel_pos": 0}, [rel], PROMPT_SINGLE.format(obj=phrase), ["S_REL"])
                run_item(qid, "S", {**base, "rel_pos": 0}, [dis], PROMPT_SINGLE.format(obj=phrase), ["S_DIST"])
                run_item(qid, "A_orig", {**base, "rel_pos": 0}, [rel, dis],
                         P_ORD.format(ord="first", obj=phrase), conds)
                run_item(qid, "A_swap", {**base, "rel_pos": 1}, [dis, rel],
                         P_ORD.format(ord="second", obj=phrase), conds)

        # ── PART B·C: 같은 사진 세트에서 지시 방식만 바꾼다 ──
        if "B" in args.parts or "C" in args.parts:
            rows = json.loads(ITEMS.read_text())
            if args.limit: rows = rows[: args.limit] + rows[-args.limit:]
            conds = ["M", "X_ALL", "X_COLD", "X_COLP", "LBL_M", "LBL_X_ALL"]
            print(f"PART B/C: {len(rows)} 문항 × {len(conds)} 조건 × 지시 방식 2")
            for r in rows:
                qid = r["question_id"]
                obj = obj_phrase(art(r["object"]), r["object"])
                paths = [image_path(i, COCO_IMG_DIR) for i in r["image_ids"]]
                meta = {"k": r["k"], "cell": r["cell"], "gt": r["gt"], "rel_pos": r["rel_pos"]}
                if "B" in args.parts:
                    run_item(qid, "B_content", meta, paths,
                             P_ANCHOR.format(anchor=obj_phrase(art(r["anchor"]), r["anchor"]), obj=obj), conds)
                if "C" in args.parts:
                    run_item(qid, "C_ordinal", meta, paths,
                             P_ORD.format(ord=ORD[r["rel_pos"]], obj=obj), conds)
        print(f"executed {executed}")


if __name__ == "__main__": main()
