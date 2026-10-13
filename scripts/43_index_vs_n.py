#!/usr/bin/env python
"""사진 수 N이 늘 때 **무개입 모델**의 서수 지시 대 내용 지시 — 탐색 파일럿 (docs/42_index_vs_n_pilot.md).

교수님 F1("큰 모델에서는 현상이 없다")에 개입 없이 답할 수 있는 유일한 측정:
7B가 사진이 많아지면 "k번째 사진"을 스스로 못 찾게 되는가, 그리고 "Picture k:" 라벨이 그걸 없애는가.

문항 (COCO val2014 보유 이미지, 자연 구성 — 적대 셀만 고르지 않는다):
  (anchor, obj) 쌍마다 정답 yes 1문항 + no 1문항 (질문 문구만으로는 못 맞히게 짝지음)
  관련 사진 R: anchor 포함. 정답 = R에 obj가 있는가.
  방해 사진 9장: anchor 미포함 중 무작위 (obj 포함 여부는 자연 비율, 문항에 기록).
  N장 버전 = 방해 앞 N-1장 + R, R의 위치는 N마다 무작위.
조건 (같은 사진 세트, 개입 없음):
  S        R 단독
  ORD      기본 템플릿 + "In the {k-th} image, is there {obj}?"
  CON      기본 템플릿 + "In the image that contains {anchor}, is there {obj}?"
  LBL_ORD  "Picture i:" 라벨 템플릿 + 같은 서수 질문
  LBL_PIC  라벨 템플릿 + "In Picture {k}, is there {obj}?"
  LBL_CON  라벨 템플릿 + 같은 내용 질문
개입이 없으므로 LM attention은 SDPA로 올린다(메모리). 실패하면 eager로 되돌리고 기록한다.
"""
import argparse, json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import torch
from sourcedepth.config import (COCO_IMG_DIR, COCO_INSTANCES, MODEL_ID, PROMPT_SINGLE, RESULTS_DIR,
                                SEED, TAG, TEMPLATE_FALLBACK, TEMPLATE_PRIMARY)
from sourcedepth.data.coco_index import build_indices
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs
from sourcedepth.model.load import load_model_and_processor, num_layers
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"idxn{TAG}.jsonl"
ITEMS = RESULTS_DIR / "idxn_items.json"
NS = [2, 3, 5, 8, 10]
N_PAIRS = 150            # 쌍당 yes 1 + no 1 → 300문항
MAX_PER_CAT = 5          # anchor·obj 범주별 상한 (person 등 쏠림 방지)
ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
P_ORD = "In the {ord} image, is there {obj}? Answer with Yes or No."
P_PIC = "In Picture {k}, is there {obj}? Answer with Yes or No."
P_CON = "In the image that contains {anchor}, is there {obj}? Answer with Yes or No."


def art(name): return "an" if name[0] in "aeiou" else "a"


def build_items():
    idx = build_indices(COCO_INSTANCES)
    have = sorted(i for i in idx.img2cats if image_path(i, COCO_IMG_DIR).exists())
    hs = set(have)
    rng = random.Random(SEED + 43)
    cats = sorted(idx.name2cat.items())
    withc = {c: set(i for i in have if c in idx.img2cats[i]) for _, c in cats}
    pairs = [(an, ac, qn, qc) for an, ac in cats for qn, qc in cats
             if ac != qc and (withc[ac] & withc[qc]) and (withc[ac] - withc[qc])
             and len(hs - withc[ac]) >= max(NS)]
    rng.shuffle(pairs)
    used_a, used_q, rows = {}, {}, []
    for an, ac, qn, qc in pairs:
        if len(rows) >= 2 * N_PAIRS: break
        if used_a.get(ac, 0) >= MAX_PER_CAT or used_q.get(qc, 0) >= MAX_PER_CAT: continue
        used_a[ac] = used_a.get(ac, 0) + 1; used_q[qc] = used_q.get(qc, 0) + 1
        for gt, pool in (("yes", withc[ac] & withc[qc]), ("no", withc[ac] - withc[qc])):
            rel = rng.choice(sorted(pool))
            ds = rng.sample(sorted(hs - withc[ac] - {rel}), max(NS) - 1)
            rows.append({"question_id": f"ix{len(rows)}", "gt": gt, "anchor": an, "anchor_cat": ac,
                         "object": qn, "category_id": qc, "rel": int(rel),
                         "distractors": [int(d) for d in ds],
                         "dist_has_obj": [int(qc in idx.img2cats[d]) for d in ds],
                         "rel_pos": {str(n): rng.randrange(n) for n in NS}})
    print(f"유효 쌍 {len(pairs)} · 보유 이미지 {len(have)} · 문항 {len(rows)}")
    if len(rows) < 2 * N_PAIRS * 0.8:
        blocked("43_idxn", f"문항 미달: {len(rows)}", {})
    ITEMS.write_text(json.dumps(rows, ensure_ascii=False))
    return rows


def load(lm_attn):
    """개입이 없는 측정이라 LM도 SDPA로 올린다. 지원하지 않으면 기존 로더(eager)로."""
    if lm_attn == "sdpa":
        try:
            from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
            model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                MODEL_ID, attn_implementation={"text_config": "sdpa", "vision_config": "sdpa"},
                torch_dtype=torch.bfloat16, device_map="cuda:0")
            model.eval(); torch.set_grad_enabled(False)
            return model, AutoProcessor.from_pretrained(MODEL_ID), "sdpa"
        except Exception as e:
            print(f"[load] LM SDPA 실패 ({type(e).__name__}: {e}) — eager로 진행")
    model, processor = load_model_and_processor(sdpa_vision=True)
    return model, processor, "eager"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--build-only", action="store_true")
    ap.add_argument("--lm-attn", default="sdpa")
    args = ap.parse_args()
    rows = json.loads(ITEMS.read_text()) if ITEMS.exists() else build_items()
    if args.build_only: return
    dump_env("43_index_vs_n")
    if not torch.cuda.is_available(): blocked("43_idxn", "GPU 없음", {})
    torch.manual_seed(SEED)
    if args.limit: rows = rows[: args.limit]

    with stage("43_index_vs_n"):
        model, processor, lm_attn = load(args.lm_attn)
        nlay = num_layers(model)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["n"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0

        def fire(row, n, cond, paths, q, tmpl, rel_pos, n_leak):
            nonlocal executed
            if (row["question_id"], n, cond) in done: return
            t0 = time.time()
            rec = {"question_id": row["question_id"], "n": n, "condition": cond, "gt": row["gt"],
                   "rel_pos": rel_pos, "n_leak": n_leak, "lm_attn": lm_attn, "n_layers": nlay}
            try:
                inputs = build_inputs(processor, paths, q, DEV, tmpl)
                try: out = model(**inputs, use_cache=False)
                except torch.cuda.OutOfMemoryError:
                    torch.cuda.empty_cache(); out = model(**inputs, use_cache=False)
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                rec.update(p); rec["correct"] = p["pred"] == row["gt"]
                rec["seq_len"] = int(inputs["input_ids"].shape[1])
                del out, inputs
            except torch.cuda.OutOfMemoryError:
                rec["oom"] = True
            rec["elapsed_ms"] = int(1000 * (time.time() - t0)); rec["ts"] = iso_now()
            append_jsonl(OUT, rec); executed += 1
            torch.cuda.empty_cache()

        for row in rows:
            obj = obj_phrase(art(row["object"]), row["object"])
            anchor = obj_phrase(art(row["anchor"]), row["anchor"])
            rel = image_path(row["rel"], COCO_IMG_DIR)
            fire(row, 1, "S", [rel], PROMPT_SINGLE.format(obj=obj), TEMPLATE_PRIMARY, 0, 0)
            for n in NS:
                pos = row["rel_pos"][str(n)]
                paths = [image_path(d, COCO_IMG_DIR) for d in row["distractors"][: n - 1]]
                paths.insert(pos, rel)
                leak = sum(row["dist_has_obj"][: n - 1])
                q_ord = P_ORD.format(ord=ORD[pos], obj=obj)
                q_con = P_CON.format(anchor=anchor, obj=obj)
                fire(row, n, "ORD", paths, q_ord, TEMPLATE_PRIMARY, pos, leak)
                fire(row, n, "CON", paths, q_con, TEMPLATE_PRIMARY, pos, leak)
                fire(row, n, "LBL_ORD", paths, q_ord, TEMPLATE_FALLBACK, pos, leak)
                fire(row, n, "LBL_PIC", paths, P_PIC.format(k=pos + 1, obj=obj), TEMPLATE_FALLBACK, pos, leak)
                fire(row, n, "LBL_CON", paths, q_con, TEMPLATE_FALLBACK, pos, leak)
        print(f"executed {executed} · lm_attn={lm_attn} · peak {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB")


if __name__ == "__main__": main()
