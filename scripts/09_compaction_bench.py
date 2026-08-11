#!/usr/bin/env python
"""Gate 3 선행: 실측 TTFT — mask 등가가 아닌 실제 sequence compaction 구현·측정 (탐색적).

layer L부터 distractor 토큰을 hidden state·mask·position embedding에서 물리적으로 제거해
이후 층의 실제 연산량을 줄인다. 수학적으로 masked T(L)과 동일해야 하므로(마스킹 = softmax
분모 제외 = 부재) 예측 일치로 정합성을 검증하고, wall-clock TTFT를 비교한다.
주의: per-layer 슬라이싱 오버헤드가 포함된 보수적 측정 — 실제 구현은 1회 슬라이스로 더 빠름.
"""
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch

from sourcedepth.config import COCO_IMG_DIR, PAIRS_CSV, RESULTS_DIR, SEED
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import blocked, dump_env, stage

DEV = "cuda:0"
N_ITEMS = 40
L_LIST = [4, 8]
OUT = RESULTS_DIR / "compaction_bench.json"


class Compactor:
    """layer idx >= L에서 drop_span 토큰을 모든 seq 차원 텐서에서 물리 제거."""

    def __init__(self, layers):
        self.L = None
        self.keep = None
        self.full_s = None
        self.handles = [ly.register_forward_pre_hook(self._make(i), with_kwargs=True)
                        for i, ly in enumerate(layers)]

    def configure(self, L, drop_span, full_s, device):
        s, e = drop_span
        self.keep = torch.tensor([i for i in range(full_s) if not (s <= i <= e)],
                                 device=device)
        self.L, self.full_s = L, full_s

    def disable(self):
        self.L = None

    def _slice(self, t):
        for d in range(t.dim()):
            if t.shape[d] == self.full_s:
                t = t.index_select(d, self.keep)
        return t

    def _make(self, idx):
        def hook(module, args, kwargs):
            if self.L is None or idx < self.L:
                return None
            args = tuple(self._slice(a) if torch.is_tensor(a) else a for a in args)
            nk = {}
            for k, v in kwargs.items():
                if torch.is_tensor(v):
                    nk[k] = self._slice(v)
                elif isinstance(v, tuple) and all(torch.is_tensor(x) for x in v):
                    nk[k] = tuple(self._slice(x) for x in v)
                else:
                    nk[k] = v
            return (args, nk)
        return hook


def timed_forward(model, inp):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    with torch.no_grad():
        out = model(**inp, use_cache=False)
    torch.cuda.synchronize()
    return out, (time.perf_counter() - t0) * 1000


def main():
    dump_env("09_compaction")
    if not torch.cuda.is_available():
        blocked("09_compact", "GPU 없음", {})
    torch.manual_seed(SEED)

    pairs = pd.read_csv(PAIRS_CSV).to_dict("records")[:N_ITEMS]
    with stage("09_compaction_bench"):
        model, processor = load_model_and_processor()
        layers = resolve_decoder_layers(model)
        ctrl = KVBlockController(model, layers)     # masked reference
        comp = Compactor(layers)
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()

        # warmup
        for row in pairs[:3]:
            q, _ = questions_for(row)
            inp = build_inputs(processor, [image_path(int(row["image1_id"]), COCO_IMG_DIR),
                                           image_path(int(row["image2_id"]), COCO_IMG_DIR)], q, DEV)
            timed_forward(model, inp)

        res = {L: {"full_ms": [], "comp_ms": [], "agree": 0, "n": 0,
                   "max_logit_diff": 0.0} for L in L_LIST}
        for row in pairs:
            q, _ = questions_for(row)
            inp = build_inputs(processor, [image_path(int(row["image1_id"]), COCO_IMG_DIR),
                                           image_path(int(row["image2_id"]), COCO_IMG_DIR)], q, DEV)
            sp1, sp2 = find_vision_spans(inp["input_ids"], vs, ve, pad)
            full_s = inp["input_ids"].shape[1]
            for L in L_LIST:
                ctrl.disable(); comp.disable()
                _, t_full = timed_forward(model, inp)
                # masked reference (정합성 기준)
                ctrl.configure(L, sp2)
                out_mask, _ = timed_forward(model, inp)
                ctrl.disable()
                p_mask = predict(out_mask.logits[0, -1].float(), yes_ids, no_ids)
                # compacted
                comp.configure(L, sp2, full_s, DEV)
                out_comp, t_comp = timed_forward(model, inp)
                comp.disable()
                p_comp = predict(out_comp.logits[0, -1].float(), yes_ids, no_ids)
                r = res[L]
                r["full_ms"].append(t_full)
                r["comp_ms"].append(t_comp)
                r["n"] += 1
                r["agree"] += int(p_comp["pred"] == p_mask["pred"])
                r["max_logit_diff"] = max(
                    r["max_logit_diff"],
                    abs(p_comp["logit_yes"] - p_mask["logit_yes"]),
                    abs(p_comp["logit_no"] - p_mask["logit_no"]))

        summary = {}
        for L in L_LIST:
            r = res[L]
            fm, cm = statistics.median(r["full_ms"]), statistics.median(r["comp_ms"])
            summary[f"L{L}"] = {
                "n": r["n"],
                "ttft_full_ms_median": round(fm, 1),
                "ttft_compact_ms_median": round(cm, 1),
                "ttft_reduction_pct": round(100 * (1 - cm / fm), 1),
                "pred_agree_vs_masked": round(r["agree"] / r["n"], 4),
                "max_yes_no_logit_diff": round(r["max_logit_diff"], 4),
            }
        OUT.write_text(json.dumps(summary, indent=1))
        print("=== compaction TTFT bench (median, n=%d) ===" % N_ITEMS)
        print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
