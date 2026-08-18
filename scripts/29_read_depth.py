#!/usr/bin/env python
"""읽기 경로 차단을 '몇 층부터' 걸어야 하는가 — 최소 개입 지점 탐색.

기존 READ 조건은 block_from=0, 즉 **전 층**에서 질문→무관이미지 읽기를 차단했다.
그런데 이미지 간 상호작용은 앞쪽 16층에 몰려 있음이 확인됐으므로(ISO0 −0.055 vs ISO16 −0.005),
읽기 역시 특정 구간에 몰려 있을 수 있다.

조건: M / READ0 / READ8 / READ16 / READ24  (숫자 = 차단 시작 층)
      + T0 (전면 차단, 상한 참조)

의미:
  READ16 ≈ READ0 이면 → 해로운 읽기는 뒤쪽에서 일어난다. 앞쪽 16층은 건드릴 필요 없다.
                        = 개입 범위가 절반 이하로 줄고, 앞쪽 KV는 그대로 재사용 가능
  READ16 << READ0 이면 → 해로운 읽기가 앞쪽부터 누적된다. 조기 개입이 필수.
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd, torch
from sourcedepth.config import (COCO_IMG_DIR, PAIRS_CSV, RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"readdepth{TAG}.jsonl"
LAYERS = [0, 8, 16, 24]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("29_read_depth")
    if not torch.cuda.is_available(): blocked("29_readdepth", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = [r for r in pd.read_csv(PAIRS_CSV).to_dict("records") if int(r["cell"]) in (1, 2)]
    if args.limit: rows = rows[: args.limit]
    CONDS = ["M", "T0"] + [f"READ{l}" for l in LAYERS]
    print(f"{len(rows)} 문항 × {len(CONDS)} 조건")
    with stage("29_read_depth"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = f"rd{row['question_id']}"
            todo = [c for c in CONDS if (qid, c) not in done]
            if not todo: continue
            q_multi, _ = questions_for(row)
            ims = [image_path(int(row["image1_id"]), COCO_IMG_DIR),
                   image_path(int(row["image2_id"]), COCO_IMG_DIR)]
            inputs = build_inputs(processor, ims, q_multi, DEV, template)
            sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
            if len(sp) != 2: blocked("29_readdepth", f"span != 2: {len(sp)}", {"qid": qid})
            seq = int(inputs["input_ids"].shape[1]); ts = (sp[-1][1] + 1, seq - 1)
            for cond in todo:
                t0 = time.time()
                if cond == "M": ctrl.disable()
                elif cond == "T0": ctrl.configure_pathway([(0, None, sp[1])])
                else: ctrl.configure_pathway([(int(cond[4:]), ts, sp[1])])
                try:
                    try: out = model(**inputs, use_cache=False)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache(); out = model(**inputs, use_cache=False)
                finally: ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "cell": int(row["cell"]), "gt": row["gt"],
                                   "condition": cond, **p, "correct": p["pred"] == row["gt"],
                                   "n_layers": nlay, "seq_len": seq,
                                   "elapsed_ms": int(1000*(time.time()-t0)), "ts": iso_now()})
                executed += 1; del out
            del inputs; torch.cuda.empty_cache()
        print(f"executed {executed}")

if __name__ == "__main__": main()
