#!/usr/bin/env python
"""오라클 없는 종단(end-to-end) 성능 — 헤드라인 표의 정확한 실현 수치.

docs/33_endtoend_prereg.md. 지금까지의 모든 개입 수치는 '어느 것이 방해인지 아는' 오라클 조건이었고,
실현(realized) 수치는 근사(낙관)뿐이었다. 여기서 정확값을 잰다.

컨트롤러 선택은 기존 loo{TAG}.jsonl의 저장된 margin으로 재현한다(사전 고정 규칙:
pick = argmax_i |margin(B_i) − margin(M)|). 재실행하는 것은 새 개입 조건 4개뿐:

  ORD_READ  : 진짜 관련(0번)만 남기고, 나머지의 '읽기'만 차단   ← 오라클 상한
  REAL_READ : 컨트롤러가 고른 이미지만 남기고, 나머지 읽기 차단  ← 실현 성능 (주 종점)
  ORD_KEEP  : 진짜 관련만 남기고 나머지 전면 차단
  REAL_KEEP : 고른 이미지만 남기고 나머지 전면 차단

M(무개입)은 loo에 이미 있으므로 재지 않는다. 분석 시 짝지어 사용.
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import torch
from sourcedepth.config import COCO_IMG_DIR, RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"endtoend{TAG}.jsonl"
ITEMS = RESULTS_DIR / "scale_auc_items.json"
NS = [1, 2, 3]
CONDS = ["ORD_READ", "REAL_READ", "ORD_KEEP", "REAL_KEEP"]


def load_picks():
    """loo{TAG}.jsonl → {(qid, n): pick}. 규칙은 docs/23과 동일, 사전 고정."""
    D = {}
    for x in read_jsonl(RESULTS_DIR / f"loo{TAG}.jsonl"):
        D.setdefault((x["question_id"], x["n_dist"]), {})[x["condition"]] = x["margin"]
    picks = {}
    for (qid, n), c in D.items():
        if "M" not in c or any(f"B{i}" not in c for i in range(n + 1)):
            continue
        d = [abs(c[f"B{i}"] - c["M"]) for i in range(n + 1)]
        picks[(qid, n)] = max(range(len(d)), key=lambda i: d[i])
    return picks


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("35_endtoend")
    if not torch.cuda.is_available(): blocked("35_e2e", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = json.loads(ITEMS.read_text())
    if args.limit: rows = rows[: args.limit]
    picks = load_picks()
    print(f"{len(rows)} 문항 × N∈{NS} × {len(CONDS)}조건, picks={len(picks)}")

    with stage("35_endtoend"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"], x["n_dist"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]
            q_multi, _ = questions_for(row)
            im1 = image_path(row["image1_id"], COCO_IMG_DIR)
            dis = [image_path(d, COCO_IMG_DIR) for d in row["distractors"]]
            for n in NS:
                if (qid, n) not in picks:
                    continue
                pick = picks[(qid, n)]
                todo = [c for c in CONDS if (qid, c, n) not in done]
                if not todo: continue
                inputs = build_inputs(processor, [im1] + dis[:n], q_multi, DEV, template)
                sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
                if len(sp) != n + 1:
                    blocked("35_e2e", f"span != {n+1}: {len(sp)}", {"qid": qid})
                seq = int(inputs["input_ids"].shape[1]); ts = (sp[-1][1] + 1, seq - 1)
                for cond in todo:
                    t0 = time.time()
                    keep = 0 if cond.startswith("ORD") else pick
                    others = [i for i in range(n + 1) if i != keep]
                    if cond.endswith("READ"):
                        ctrl.configure_pathway([(0, ts, sp[i]) for i in others])
                    else:
                        ctrl.configure_pathway([(0, None, sp[i]) for i in others])
                    try:
                        try: out = model(**inputs, use_cache=False)
                        except torch.cuda.OutOfMemoryError:
                            torch.cuda.empty_cache(); out = model(**inputs, use_cache=False)
                    finally: ctrl.disable()
                    p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                    append_jsonl(OUT, {"question_id": qid, "cell": row["cell"], "gt": row["gt"],
                                       "condition": cond, "n_dist": n, "pick": pick,
                                       "pick_correct": pick == 0, **p,
                                       "correct": p["pred"] == row["gt"], "n_layers": nlay,
                                       "seq_len": seq, "elapsed_ms": int(1000*(time.time()-t0)),
                                       "ts": iso_now()})
                    executed += 1; del out
                del inputs
                torch.cuda.empty_cache()
        print(f"executed {executed}")


if __name__ == "__main__": main()
