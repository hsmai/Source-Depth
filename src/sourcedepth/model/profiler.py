"""M 조건 attention 프로파일링 (브리프 B-5).

표준 경로: model(..., output_attentions=True)의 outputs.attentions에서
마지막 프롬프트 토큰 행만 즉시 축약 (head 평균, [이미지1/이미지2/텍스트] 질량).
메모리 실측: seq~900, 36 layers, bf16 ≈ 1GB 미만 — 24GB 내 수용 (04 문서 §6 fallback 경로를 주 경로로 채택).
"""
from ..runlog import blocked


def masses_from_attentions(attentions, span1, span2) -> list[list[float]]:
    """반환: [[m1, m2, m_text] × n_layers]. 각 layer에서 합 ≈ 1.0 검증."""
    if attentions is None or attentions[0] is None:
        blocked("profiler", "attentions=None — eager 미적용 의심", {})
    out = []
    (s1, e1), (s2, e2) = span1, span2
    for li, attn in enumerate(attentions):
        w = attn[0, :, -1, :].float()          # (heads, kv_len) — 마지막 프롬프트 토큰 행
        m1 = w[:, s1:e1 + 1].sum(-1).mean().item()
        m2 = w[:, s2:e2 + 1].sum(-1).mean().item()
        total = w.sum(-1).mean().item()
        mt = total - m1 - m2
        if abs(total - 1.0) > 1e-3:
            blocked("profiler", "attention 행 질량 합 ≠ 1 (pre-softmax 오포착 또는 span 오류)",
                    {"layer": li, "total": total})
        out.append([round(m1, 6), round(m2, 6), round(mt, 6)])
    return out
