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

from sourcedepth.config import (ATTN_PROFILE, ATTN_PROFILE_SWAPPED,
                                COCO_IMG_DIR, PAIRS_CSV, PROMPT_MULTI_SECOND,
                                SANITY_FLAG, SEED, TEMPLATE_CHOICE)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase, questions_for
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
    ap.add_argument("--swap", action="store_true",
                    help="탐색적 대조 실행: [distractor, 원본] 순서 + 'second image' 질문 — "
                         "③의 position bias 분리용. 출력은 attn_profile_swapped 파일")
    args = ap.parse_args()

    dump_env("04_profile")
    if not SANITY_FLAG.exists():
        blocked("04_profile", "SANITY_PASSED 부재", {})
    if not torch.cuda.is_available():
        blocked("04_profile", "GPU 없음", {})
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)

    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    out_path = ATTN_PROFILE_SWAPPED if args.swap else ATTN_PROFILE
    pairs = pd.read_csv(PAIRS_CSV)
    rows = [r for i, r in enumerate(pairs.to_dict("records"))
            if i % args.num_shards == args.shard]
    done = {r["question_id"] for r in read_jsonl(out_path)
            if r.get("template") == template}
    todo = [r for r in rows if r["question_id"] not in done]
    print(f"shard {args.shard}: {len(todo)}/{len(rows)} to profile "
          f"(template={template}, swap={args.swap})")

    with stage(f"04_profile_shard{args.shard}"):
        model, processor = load_model_and_processor()
        n = num_layers(model)
        resolve_decoder_layers(model)   # layer 검증만 (mask hook 불필요 — M 조건)
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        for k, row in enumerate(todo):
            t0 = time.time()
            im1 = image_path(int(row["image1_id"]), COCO_IMG_DIR)
            im2 = image_path(int(row["image2_id"]), COCO_IMG_DIR)
            if args.swap:
                # [distractor, 원본] + "In the second image, ..." — 관련 이미지가 두 번째 위치
                q = PROMPT_MULTI_SECOND.format(obj=obj_phrase(row["article"], row["object"]))
                inp = build_inputs(processor, [im2, im1], q, DEV, template)
                spans = find_vision_spans(inp["input_ids"], vs, ve, pad)
                sp_rel, sp_dis = spans[1], spans[0]     # 관련=두 번째 span
            else:
                q, _ = questions_for(row)
                inp = build_inputs(processor, [im1, im2], q, DEV, template)
                spans = find_vision_spans(inp["input_ids"], vs, ve, pad)
                sp_rel, sp_dis = spans[0], spans[1]
            with torch.no_grad():
                out = model(**inp, use_cache=False, output_attentions=True)
            # masses는 항상 [관련, distractor, 텍스트] 의미 순서로 저장
            masses = masses_from_attentions(out.attentions, sp_rel, sp_dis)
            p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
            append_jsonl(out_path, {
                "question_id": row["question_id"], "cell": int(row["cell"]),
                "gt": row["gt"], "template": template, "n_layers": n,
                "swapped": bool(args.swap),
                "masses": masses, "pred_reprofile": p["pred"],
                "seq_len": int(inp["input_ids"].shape[1]),
                "rel_span": list(sp_rel), "dis_span": list(sp_dis),
                "elapsed_ms": int(1000 * (time.time() - t0)), "ts": iso_now()})
            if (k + 1) % 50 == 0:
                print(f"  {k + 1}/{len(todo)} done")
    print("profiling complete")


if __name__ == "__main__":
    main()
