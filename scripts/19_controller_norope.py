#!/usr/bin/env python
"""컨트롤러 재측정 — RoPE를 제거한 attention을 기준으로.

배경: 우리는 층별 '관련 이미지 판정'을 `out.attentions`(= RoPE 적용된 attention)의
이미지별 질량으로 쟀고, 8층 원순서 99.8% / 뒤집기 0.2% → "위치 편향"이라 결론냈다.
그런데 선행연구는 정확히 그 기준이 RoPE의 long-term decay 때문에 망가진다고 보고하고,
**RoPE를 빼고 마지막 텍스트 토큰의 attention을 계산하면 해결된다**고 한다
(Feather the Throttle, ICCV'25 / PosPrune, AAAI / Attention Debiasing 2508.17807).

즉 우리 사망 진단이 '고장난 기준' 위에서 내려졌을 수 있다. 이 스크립트가 그것을 가른다.

방법: 각 decoder layer의 self_attn 입력(hidden_states, post-layernorm)을 hook으로 받아
q_proj/k_proj를 직접 적용하고 **RoPE를 적용하지 않은 채** 마지막 토큰의 attention을 계산한다.
GQA면 k를 head 수만큼 repeat한다. 인과 마스크는 마지막 토큰이 전체를 보므로 불필요.

출력: 층×head별 (이미지1 질량, 이미지2 질량). 원순서/뒤집기 각각.
판정은 20_norope_analyze.py 에서.
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch

from sourcedepth.config import (COCO_IMG_DIR, PAIRS_CSV, PROMPT_MULTI_SECOND,
                                RESULTS_DIR, SEED, TAG)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase, questions_for
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, text_config,
                                    vision_token_ids)
from sourcedepth.runlog import append_jsonl, blocked, dump_env, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"norope_profile{TAG}.jsonl"
OUT_SWAP = RESULTS_DIR / f"norope_profile_swapped{TAG}.jsonl"
MAX_LAYER = 24


class NoRoPEProbe:
    """self_attn 입력을 받아 RoPE 없이 마지막 토큰의 head별 attention을 계산."""

    def __init__(self, model, layers, max_layer):
        self.cfg = text_config(model)
        self.n_head = self.cfg.num_attention_heads
        self.n_kv = getattr(self.cfg, "num_key_value_heads", self.n_head)
        self.hd = self.cfg.hidden_size // self.n_head
        self.rep = self.n_head // self.n_kv
        self.store = {}
        self.handles = []
        for i, ly in enumerate(layers[:max_layer]):
            self.handles.append(
                ly.self_attn.register_forward_pre_hook(self._make(i, ly.self_attn),
                                                       with_kwargs=True))

    def _make(self, idx, attn):
        def hook(module, args, kwargs):
            hs = kwargs.get("hidden_states")
            if hs is None and args:
                hs = args[0]
            if hs is None:
                return None
            with torch.no_grad():
                x = hs.float()
                T = x.shape[1]
                q = attn.q_proj(hs)[:, -1:, :].float().view(1, 1, self.n_head, self.hd)
                q = q.transpose(1, 2)                                    # (1,H,1,hd)
                k = attn.k_proj(hs).float().view(1, T, self.n_kv, self.hd).transpose(1, 2)
                if self.rep > 1:
                    k = k.repeat_interleave(self.rep, dim=1)             # (1,H,T,hd)
                s = (q @ k.transpose(-1, -2)) / math.sqrt(self.hd)       # (1,H,1,T)
                self.store[idx] = torch.softmax(s, dim=-1)[0, :, 0, :].cpu()
            return None
        return hook

    def remove(self):
        for h in self.handles:
            h.remove()


def run(model, processor, probe, rows, vs, ve, pad, swap):
    out_path = OUT_SWAP if swap else OUT
    done = {r["question_id"] for r in read_jsonl(out_path)}
    todo = [r for r in rows if r["question_id"] not in done]
    print(f"no-RoPE profiling (swap={swap}): {len(todo)}/{len(rows)}")
    for k, row in enumerate(todo):
        im1 = image_path(int(row["image1_id"]), COCO_IMG_DIR)
        im2 = image_path(int(row["image2_id"]), COCO_IMG_DIR)
        if swap:
            q = PROMPT_MULTI_SECOND.format(obj=obj_phrase(row["article"], row["object"]))
            inp = build_inputs(processor, [im2, im1], q, DEV)
            sp = find_vision_spans(inp["input_ids"], vs, ve, pad)
            (s1, e1), (s2, e2) = sp[1], sp[0]        # 저장은 항상 [관련, 방해]
        else:
            q_multi, _ = questions_for(row)
            inp = build_inputs(processor, [im1, im2], q_multi, DEV)
            (s1, e1), (s2, e2) = find_vision_spans(inp["input_ids"], vs, ve, pad)
        probe.store.clear()
        with torch.no_grad():
            model(**inp, use_cache=False)
        per_layer = []
        for li in range(MAX_LAYER):
            w = probe.store.get(li)
            if w is None:
                blocked("19_norope", f"layer {li} hook 미발화", {"qid": row["question_id"]})
            per_layer.append([w[:, s1:e1 + 1].sum(-1).tolist(),
                              w[:, s2:e2 + 1].sum(-1).tolist()])
        append_jsonl(out_path, {"question_id": row["question_id"], "cell": int(row["cell"]),
                                "swapped": swap, "heads": per_layer})
        if (k + 1) % 100 == 0:
            print(f"  {k + 1}/{len(todo)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("19_controller_norope")
    if not torch.cuda.is_available():
        blocked("19_norope", "GPU 없음", {})
    torch.manual_seed(SEED)
    rows = pd.read_csv(PAIRS_CSV).to_dict("records")
    if args.limit:
        rows = rows[: args.limit]
    with stage("19_controller_norope"):
        model, processor = load_model_and_processor()
        layers = resolve_decoder_layers(model)
        probe = NoRoPEProbe(model, layers, min(MAX_LAYER, num_layers(model)))
        vs, ve, pad = vision_token_ids(processor)
        try:
            run(model, processor, probe, rows, vs, ve, pad, swap=False)
            run(model, processor, probe, rows, vs, ve, pad, swap=True)
        finally:
            probe.remove()
    print("done")


if __name__ == "__main__":
    main()
