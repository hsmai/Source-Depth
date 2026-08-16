"""KV 차단의 등가 구현 — decoder layer forward_pre_hook로 4D additive mask에
distractor key 열 finfo.min 주입 (브리프 C-3, 03 §B-5·B-6).

T(L) = 0-based layer idx >= L에서 차단 (혼합 허용 layer = 앞 L개).
M-RoPE/position id 불변 — 개입 지점은 per-layer attention mask 하나뿐.
"""
from collections import Counter

import torch

from ..runlog import blocked


def _find_4d_mask(args, kwargs):
    """mask 위치 탐색: kwargs 우선, 구버전 positional 대비 args도 검사 (03 §B-5)."""
    m = kwargs.get("attention_mask")
    if torch.is_tensor(m) and m.dim() == 4:
        return m, ("kw", "attention_mask")
    for i, a in enumerate(args):
        if torch.is_tensor(a) and a.dim() == 4 and a.dtype.is_floating_point:
            return a, ("pos", i)
    return None, None


class KVBlockController:
    def __init__(self, model, layers):
        self.layers = layers
        self.block_from: int | None = None   # None = 비활성 (S·M 조건)
        self.cols: tuple[int, int] | None = None
        self.rules: list | None = None       # configure_multi/pathway 사용 시
        self.soft: list | None = None        # configure_soft 사용 시 (유한 음수 bias)
        self.fired = Counter()               # no-op 탐지용 발화 카운터 (03 §B-1)
        self.handles = [ly.register_forward_pre_hook(self._make(i), with_kwargs=True)
                        for i, ly in enumerate(layers)]

    def configure(self, block_from: int, cols: tuple[int, int]):
        self.block_from, self.cols = block_from, cols
        self.rules = None

    def configure_multi(self, rules):
        """rules = [(block_from, (s, e)), ...] — 이미지별로 서로 다른 exit depth 배분.
        per-image adaptive depth의 실제 구현체 (예: distractor L=4, relevant L=28)."""
        self.block_from, self.cols = None, None
        self.rules = [(bf, None, sp) for bf, sp in rules]

    def configure_pathway(self, rules):
        """rules = [(block_from, qspan | None, kspan), ...] — 경로 지정 차단.
        qspan=None 이면 모든 query에 대해 kspan 열 차단 (기존 동작과 동일).
        qspan=(qs, qe) 이면 해당 query 행에서만 kspan 열 차단 — 예:
          (0, img2_span, img1_span)  → 이미지2가 이미지1을 보는 경로만 차단
          (0, text_span, img2_span)  → 질문 토큰이 이미지2를 읽는 경로만 차단
        decode 단계(q_len=1)에서는 prefill 좌표가 어긋나므로 이 실험은 prefill 단발
        forward(use_cache=False)에서만 사용한다."""
        self.block_from, self.cols = None, None
        self.rules = list(rules)

    def configure_soft(self, rules):
        """rules = [(block_from, kspan, lam), ...] — 하드 차단(-inf) 대신 **유한한 음수 bias**.
        softmax 전에 λ를 빼므로 해당 열의 가중치가 e^-λ 배로 줄되 0은 아니다.
        λ=0 무개입, λ→∞ 하드 차단. 앞단 selector에는 없는 연속 축."""
        self.block_from, self.cols, self.rules = None, None, None
        self.soft = list(rules)

    def disable(self):
        self.block_from = None
        self.cols = None
        self.rules = None
        self.soft = None

    def remove(self):
        for h in self.handles:
            h.remove()
        self.handles = []

    def reset_counter(self):
        self.fired = Counter()

    def expected_fires(self, block_from: int, n_layers: int, n_forwards: int) -> int:
        return max(0, n_layers - block_from) * n_forwards

    def _make(self, idx: int):
        def hook(module, args, kwargs):
            if self.soft is not None:
                act = [(k, l) for bf, k, l in self.soft if idx >= bf]
                if not act:
                    return None
                mask, loc = _find_4d_mask(args, kwargs)
                if mask is None:
                    blocked("mask", "4D attention_mask 미발견", {"layer": idx})
                m = mask.clone()
                for (s_, e_), lam in act:
                    m[:, :, :, s_:e_ + 1] -= lam
                self.fired[idx] += 1
                if loc[0] == "kw":
                    kwargs[loc[1]] = m
                else:
                    args = tuple(m if i == loc[1] else a for i, a in enumerate(args))
                return (args, kwargs)
            if self.rules is not None:
                active = [(q, k) for bf, q, k in self.rules if idx >= bf]
                if not active:
                    return None
            elif self.block_from is None or idx < self.block_from:
                return None                  # 무개입
            else:
                active = [(None, self.cols)]
            mask, loc = _find_4d_mask(args, kwargs)
            if mask is None:
                blocked("mask", "4D attention_mask 미발견 (kwargs·args 모두)",
                        {"layer": idx, "kwargs_keys": sorted(kwargs.keys())})
            m = mask.clone()                 # 원본은 전 layer 공유 — in-place 금지
            for q, (s, e) in active:
                if q is None:
                    m[:, :, :, s:e + 1] = torch.finfo(m.dtype).min
                else:
                    m[:, :, q[0]:q[1] + 1, s:e + 1] = torch.finfo(m.dtype).min
            self.fired[idx] += 1
            if loc[0] == "kw":
                kwargs[loc[1]] = m
            else:
                args = tuple(m if i == loc[1] else a for i, a in enumerate(args))
            return (args, kwargs)
        return hook


def condition_to_block(cond: str, span1, span2):
    """조건명 → (block_from | None, cols | None). T(L)의 L은 0-based idx 기준 (§B-6)."""
    if cond in ("S", "M"):
        return None, None
    if cond == "T0":
        return 0, span2
    if cond == "Trel8":
        return 8, span1
    if cond.startswith("T"):
        return int(cond[1:]), span2
    blocked("mask", f"unknown condition: {cond}", {})
