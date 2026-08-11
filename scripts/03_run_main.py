#!/usr/bin/env python
"""C-5 단계 3: 본 실험 — 10조건 × 600문항 logit 평가 (resume 내장)."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch

from sourcedepth.config import (CONDITIONS, PAIRS_CSV, RAW_RESULTS,
                                SANITY_FLAG, SEED, TEMPLATE_CHOICE)
from sourcedepth.eval.loop import run_eval
from sourcedepth.eval.yesno import load_yes_no_ids
from sourcedepth.model.load import (load_model_and_processor,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import blocked, dump_env, read_jsonl, stage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--num-shards", type=int, default=1)
    ap.add_argument("--extra-l", type=int, nargs="*", default=[],
                    help="PART D ② 실패 대응 전용 추가 T(L) 조건 (예: 2 6 10)")
    args = ap.parse_args()

    dump_env("03_main")
    if not SANITY_FLAG.exists():
        blocked("03_main", "SANITY_PASSED 부재 — 본 실험 진입 금지 (C-4)", {})
    if not torch.cuda.is_available():
        blocked("03_main", "GPU 없음", {})
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)

    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    conds = list(CONDITIONS) + [f"T{l}" for l in args.extra_l if f"T{l}" not in CONDITIONS]

    pairs = pd.read_csv(PAIRS_CSV)
    rows = [r for i, r in enumerate(pairs.to_dict("records"))
            if i % args.num_shards == args.shard]
    print(f"shard {args.shard}/{args.num_shards}: {len(rows)} items × {len(conds)} conds, "
          f"template={template}")

    with stage(f"03_main_shard{args.shard}"):
        model, processor = load_model_and_processor()
        layers = resolve_decoder_layers(model)
        ctrl = KVBlockController(model, layers)
        vs_ve_pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        executed = run_eval(rows, conds, model, processor, ctrl, vs_ve_pad,
                            RAW_RESULTS, template, yes_ids, no_ids)
        print(f"executed {executed} forwards this run")

    done = [r for r in read_jsonl(RAW_RESULTS) if r.get("template") == template]
    got = {(r["question_id"], r["condition"]) for r in done}
    need = {(r["question_id"], c) for r in rows for c in conds}
    missing = need - got
    if missing:
        blocked("03_main", f"본 실험 미완료 {len(missing)}건", {"sample": list(missing)[:5]})
    print(f"shard {args.shard} complete: {len(need)} (question, condition) pairs present")


if __name__ == "__main__":
    main()
