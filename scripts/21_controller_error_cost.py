#!/usr/bin/env python
"""컨트롤러가 틀렸을 때의 비용 — 손익분기 계산의 빠진 항.

17_scale_auc.py는 '방해 이미지를 맞게 차단했을 때'(T0/T4)만 쟀다. 컨트롤러를 실제로
끼우면 틀리는 경우가 있고, 그때는 **관련 이미지가 차단된다.** 그 비용을 모르면
"컨트롤러 정확도 몇 %부터 이득인가"를 계산할 수 없다.

같은 300문항·같은 N을 쓰되, 차단 대상만 바꾼다:
  Rel0 / Rel4 = 관련 이미지(1번)를 0층 / 4층부터 차단, 방해는 그대로 둠

손익분기:  a·AUC(T0) + (1−a)·AUC(Rel0)  ≥  AUC(M)   →  a ≥ (M−Rel0)/(T0−Rel0)
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import torch

from sourcedepth.config import (COCO_IMG_DIR, RESULTS_DIR, SEED, TAG,
                                TEMPLATE_CHOICE)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import (append_jsonl, blocked, dump_env, iso_now,
                                read_jsonl, stage)

DEV = "cuda:0"
OUT = RESULTS_DIR / f"errcost{TAG}.jsonl"
ITEMS = RESULTS_DIR / "scale_auc_items.json"
NS = [1, 2, 3]
CONDS = ["Rel0", "Rel4"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("21_controller_error_cost")
    if not torch.cuda.is_available():
        blocked("21_errcost", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    if not ITEMS.exists():
        blocked("21_errcost", "scale_auc_items.json 없음 — 17을 먼저 실행", {})
    rows = json.loads(ITEMS.read_text())
    if args.limit:
        rows = rows[: args.limit]
    todo_all = [(c, n) for n in NS for c in CONDS]
    print(f"{len(rows)} 문항 × {len(todo_all)} 조건 = {len(rows)*len(todo_all)}회")

    with stage("21_controller_error_cost"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"], x["n_dist"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]
            todo = [(c, n) for (c, n) in todo_all if (qid, c, n) not in done]
            if not todo:
                continue
            q_multi, _ = questions_for(row)
            im1 = image_path(row["image1_id"], COCO_IMG_DIR)
            dis = [image_path(d, COCO_IMG_DIR) for d in row["distractors"]]
            by_n = {}
            for c, n in todo:
                by_n.setdefault(n, []).append(c)
            for n in sorted(by_n):
                inputs = build_inputs(processor, [im1] + dis[:n], q_multi, DEV, template)
                sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
                if len(sp) != n + 1:
                    blocked("21_errcost", f"span 수 불일치 N={n}: {len(sp)}", {"qid": qid})
                for cond in by_n[n]:
                    t0 = time.time()
                    bf = 0 if cond == "Rel0" else int(cond[3:])
                    ctrl.configure_multi([(bf, sp[0])])      # ← 관련 이미지(1번)를 차단
                    try:
                        try:
                            out = model(**inputs, use_cache=False)
                        except torch.cuda.OutOfMemoryError:
                            torch.cuda.empty_cache()
                            out = model(**inputs, use_cache=False)
                    finally:
                        ctrl.disable()
                    p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                    append_jsonl(OUT, {"question_id": qid, "cell": row["cell"],
                                       "gt": row["gt"], "condition": cond, "n_dist": n,
                                       **p, "correct": p["pred"] == row["gt"],
                                       "n_layers": nlay,
                                       "seq_len": int(inputs["input_ids"].shape[1]),
                                       "elapsed_ms": int(1000 * (time.time() - t0)),
                                       "ts": iso_now()})
                    executed += 1
                    del out
                del inputs, sp
                torch.cuda.empty_cache()
        print(f"executed {executed}")


if __name__ == "__main__":
    main()
