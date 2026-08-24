#!/usr/bin/env python
"""일반화·안전성·통합 주장 (docs/35_generalize_prereg.md).

## A. do-no-harm + top-k 유지 — "모든 이미지가 필요한" 질문에서 우리 파이프라인이 해로운가
allof3_items (Do ALL of these images contain X?) — 3장 전부 봐야 답할 수 있다.
  M3 / B0..B2 (컨트롤러) / PIPE1 (top-1만 남기고 나머지 읽기 차단) / PIPE2 (top-2 유지)
PIPE1이 M3보다 나쁘면 → 무조건 적용 불가. PIPE2가 이를 회복하면 → **top-k가 일반화 축**.
사용자가 요구한 '여러 이미지가 관련인 경우' 대응의 첫 실측.

## B. 통합 주장 검정 — 우리 분해가 MIMIC(막기)·CAPL(열기) 양 진영을 설명하는가
pairs.csv 셀1·2, "first image".
  M / MIMIC (이미지↔이미지를 층 12~23 구간에서만 차단) / XIMG0 (0층부터 전부 차단) / READ (우리)
MIMIC식이 M보다 낫고 READ보다 나쁘면 → "둘 다 부분적으로 맞다"는 우리 설명이 지지된다.
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd, torch
from sourcedepth.config import (COCO_IMG_DIR, PAIRS_CSV, PROMPT_MULTI, RESULTS_DIR,
                                SEED, TAG, TEMPLATE_CHOICE)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"generalize{TAG}.jsonl"
ALL_ITEMS = RESULTS_DIR / "allof3_items.json"
Q_ALL = "Do all of these images contain {obj}? Answer with Yes or No."
MIMIC_LO, MIMIC_HI = 12, 23        # MIMIC(2601.07812)의 중간 층 구간 — 절대값 그대로


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("39_generalize")
    if not torch.cuda.is_available(): blocked("39_gen", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]

    with stage("39_generalize"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        prior = {}
        for x in read_jsonl(OUT):
            prior.setdefault(x["question_id"], {})[x["condition"]] = x["margin"]
        done = {(q, c) for q, m in prior.items() for c in m}
        executed = 0

        def run(qid, meta, paths, q, conds_fn):
            nonlocal executed
            inputs = build_inputs(processor, paths, q, DEV, template)
            sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
            if len(sp) != len(paths):
                blocked("39_gen", f"span != {len(paths)}: {len(sp)}", {"qid": qid})
            seq = int(inputs["input_ids"].shape[1]); ts = (sp[-1][1] + 1, seq - 1)
            margins = dict(prior.get(qid, {}))

            def fire(cond, setup):
                nonlocal executed
                t0 = time.time(); setup()
                try:
                    try: out = model(**inputs, use_cache=False)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache(); out = model(**inputs, use_cache=False)
                finally: ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                margins[cond] = p["margin"]
                append_jsonl(OUT, {"question_id": qid, **meta, "condition": cond, **p,
                                   "correct": p["pred"] == meta["gt"], "n_layers": nlay,
                                   "seq_len": seq, "elapsed_ms": int(1000*(time.time()-t0)),
                                   "ts": iso_now()})
                executed += 1; del out
            conds_fn(sp, ts, margins, fire)
            del inputs
            torch.cuda.empty_cache()

        # ── A. need-all (모든 이미지가 필요) ──
        if ALL_ITEMS.exists():
            rows = json.loads(ALL_ITEMS.read_text())
            if args.limit: rows = rows[: args.limit]
            print(f"A. need-all {len(rows)} 문항")
            for row in rows:
                qid = f"g{row['question_id']}"
                need = ["M3", "B0", "B1", "B2", "PIPE1", "PIPE2"]
                if all((qid, c) in done for c in need): continue
                paths = [image_path(int(i), COCO_IMG_DIR) for i in row["images"]]
                q = Q_ALL.format(obj=obj_phrase(row["article"], row["object"]))
                meta = {"part": "A", "gt": row["gt"], "kind": row.get("group", "")}

                def condsA(sp, ts, margins, fire):
                    K = len(sp)
                    if (qid, "M3") not in done: fire("M3", lambda: ctrl.disable())
                    for i in range(K):
                        if (qid, f"B{i}") not in done:
                            fire(f"B{i}", lambda i=i: ctrl.configure_pathway([(0, None, sp[i])]))
                    d = [abs(margins[f"B{i}"] - margins["M3"]) for i in range(K)]
                    order = sorted(range(K), key=lambda i: -d[i])
                    for nm, keepn in (("PIPE1", 1), ("PIPE2", 2)):
                        if (qid, nm) in done: continue
                        keep = set(order[:keepn])
                        fire(nm, lambda keep=keep: ctrl.configure_pathway(
                            [(0, ts, sp[i]) for i in range(K) if i not in keep]))
                run(qid, meta, paths, q, condsA)

        # ── B. 통합 주장 (MIMIC식 층 구간 차단 vs 우리) ──
        prs = [r for r in pd.read_csv(PAIRS_CSV).to_dict("records") if int(r["cell"]) in (1, 2)]
        if args.limit: prs = prs[: args.limit]
        print(f"B. 통합 {len(prs)} 문항")
        for row in prs:
            qid = f"u{row['question_id']}"
            need = ["M", "MIMIC", "XIMG0", "READ"]
            if all((qid, c) in done for c in need): continue
            paths = [image_path(int(row["image1_id"]), COCO_IMG_DIR),
                     image_path(int(row["image2_id"]), COCO_IMG_DIR)]
            q = PROMPT_MULTI.format(obj=obj_phrase(row["article"], row["object"]))
            meta = {"part": "B", "gt": row["gt"], "cell": int(row["cell"])}

            def condsB(sp, ts, margins, fire):
                if (qid, "M") not in done: fire("M", lambda: ctrl.disable())
                if (qid, "MIMIC") not in done:
                    fire("MIMIC", lambda: ctrl.configure_band(
                        [(MIMIC_LO, MIMIC_HI, sp[1], sp[0])]))
                if (qid, "XIMG0") not in done:
                    fire("XIMG0", lambda: ctrl.configure_pathway([(0, sp[1], sp[0])]))
                if (qid, "READ") not in done:
                    fire("READ", lambda: ctrl.configure_pathway([(0, ts, sp[1])]))
            run(qid, meta, paths, q, condsB)
        print(f"executed {executed}")


if __name__ == "__main__": main()
