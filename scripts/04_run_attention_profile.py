#!/usr/bin/env python
"""C-5 단계 4: M 조건 attention 프로파일링 재실행 (브리프 B-5, resume 내장)."""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch

from sourcedepth.config import (ATTN_PROFILE, COCO_IMG_DIR, PAIRS_CSV,
                                SANITY_FLAG, SEED, TEMPLATE_CHOICE)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.profiler import masses_from_attentions
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--num-shards", type=int, default=1)
    args = ap.parse_args()

    dump_env("04_profile")
    if not SANITY_FLAG.exists():
        blocked("04_profile", "SANITY_PASSED 부재", {})
    if not torch.cuda.is_available():
        blocked("04_profile", "GPU 없음", {})
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)

    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    pairs = pd.read_csv(PAIRS_CSV)
    rows = [r for i, r in enumerate(pairs.to_dict("records"))
            if i % args.num_shards == args.shard]
    done = {r["question_id"] for r in read_jsonl(ATTN_PROFILE)
            if r.get("template") == template}
    todo = [r for r in rows if r["question_id"] not in done]
    print(f"shard {args.shard}: {len(todo)}/{len(rows)} to profile (template={template})")

    with stage(f"04_profile_shard{args.shard}"):
        model, processor = load_model_and_processor()
        n = num_layers(model)
        resolve_decoder_layers(model)   # layer 검증만 (mask hook 불필요 — M 조건)
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        for k, row in enumerate(todo):
            t0 = time.time()
            q_multi, _ = questions_for(row)
            im1 = image_path(int(row["image1_id"]), COCO_IMG_DIR)
            im2 = image_path(int(row["image2_id"]), COCO_IMG_DIR)
            inp = build_inputs(processor, [im1, im2], q_multi, DEV, template)
            sp1, sp2 = find_vision_spans(inp["input_ids"], vs, ve, pad)
            with torch.no_grad():
                out = model(**inp, use_cache=False, output_attentions=True)
            masses = masses_from_attentions(out.attentions, sp1, sp2)
            p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
            append_jsonl(ATTN_PROFILE, {
                "question_id": row["question_id"], "cell": int(row["cell"]),
                "gt": row["gt"], "template": template, "n_layers": n,
                "masses": masses, "pred_reprofile": p["pred"],
                "seq_len": int(inp["input_ids"].shape[1]),
                "img1_span": list(sp1), "img2_span": list(sp2),
                "elapsed_ms": int(1000 * (time.time() - t0)), "ts": iso_now()})
            if (k + 1) % 50 == 0:
                print(f"  {k + 1}/{len(todo)} done")
    print("profiling complete")


if __name__ == "__main__":
    main()
