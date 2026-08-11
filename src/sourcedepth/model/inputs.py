"""chat template 입력 구성 + vision token 구간 특정 (브리프 C-3, 결정 A-3)."""
from ..config import MASK_SPAN_MODE, TEMPLATE_FALLBACK, TEMPLATE_PRIMARY
from ..runlog import blocked


def build_messages(images: list, question: str, template: str = TEMPLATE_PRIMARY):
    if template == TEMPLATE_PRIMARY or len(images) == 1:
        content = [{"type": "image", "image": str(p)} for p in images]
        content.append({"type": "text", "text": question})
    elif template == TEMPLATE_FALLBACK:
        # C-4 fallback: "Picture 1: <image>\nPicture 2: <image>\n..." 라벨 명시
        content = []
        for i, p in enumerate(images, 1):
            content.append({"type": "text", "text": f"Picture {i}: "})
            content.append({"type": "image", "image": str(p)})
            content.append({"type": "text", "text": "\n"})
        content.append({"type": "text", "text": question})
    else:
        blocked("inputs", f"unknown template: {template}", {})
    return [{"role": "user", "content": content}]


def build_inputs(processor, images: list, question: str, device,
                 template: str = TEMPLATE_PRIMARY):
    from qwen_vl_utils import process_vision_info
    messages = build_messages(images, question, template)
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, _ = process_vision_info(messages)
    inputs = processor(text=[text], images=image_inputs, return_tensors="pt")
    return inputs.to(device)


def find_vision_spans(input_ids, vs_id: int, ve_id: int, pad_id: int,
                      mode: str = MASK_SPAN_MODE) -> list[tuple[int, int]]:
    """이미지별 차단 열 구간 (inclusive). A-3 확정: with_delimiters = start~end 전 구간."""
    ids = input_ids[0].tolist()
    starts = [i for i, t in enumerate(ids) if t == vs_id]
    ends = [i for i, t in enumerate(ids) if t == ve_id]
    if len(starts) != len(ends) or any(s >= e for s, e in zip(starts, ends)):
        blocked("inputs", "vision start/end 쌍 불일치", {"starts": starts, "ends": ends})
    if mode == "with_delimiters":
        spans = [(s, e) for s, e in zip(starts, ends)]
    else:  # "pad_only"
        spans = [(s + 1, e - 1) for s, e in zip(starts, ends)]
        for s, e in spans:
            if not all(t == pad_id for t in ids[s:e + 1]):
                blocked("inputs", "pad_only 구간에 비-pad 토큰", {"span": (s, e)})
    return spans


def span_decode_window(input_ids, tok, span: tuple[int, int], ctx: int = 5) -> str:
    """수동 확인용 로그 (C-3): [앞 ctx 토큰 | 구간 요약 | 뒤 ctx 토큰]."""
    ids = input_ids[0].tolist()
    s, e = span
    before = tok.decode(ids[max(0, s - ctx):s])
    inside = ids[s:e + 1]
    after = tok.decode(ids[e + 1:e + 1 + ctx])
    return (f"...{before!r} | [{len(inside)} tokens: first={tok.decode([inside[0]])!r} "
            f"last={tok.decode([inside[-1]])!r}] | {after!r}...")
