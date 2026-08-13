"""모델·processor 로딩 + decoder layer resolver (03 §B-4: 버전 의존 경로 fallback)."""
import operator

import torch

from ..config import MODEL_ID
from ..runlog import blocked

_LAYER_PATHS = (
    "model.language_model.layers",       # transformers >= ~4.52 (VLM refactor)
    "model.layers",                      # 구버전 (ForConditionalGeneration.model = text model)
    "language_model.layers",
    "model.model.language_model.layers",
    "model.model.layers",
)


def load_model_and_processor(max_pixels: int | None = None, sdpa_vision: bool = False):
    """sdpa_vision=True: LM은 eager(4D mask 주입에 필수) 유지, **vision tower만 SDPA**.

    eager ViT는 이미지 patch 전체에 대한 attention 행렬을 통째로 materialize한다.
    이미지 4장(~6,800 patch)이면 단일 할당이 ~3GB라 24GB 카드에서 7B와 함께 못 버틴다.
    ViT는 마스크 주입 대상이 아니므로 SDPA로 바꿔도 실험 설계에 영향이 없다.
    구버전 transformers는 dict 형태를 받지 않으므로 실패 시 조용히 eager로 되돌린다.
    """
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
    common = dict(torch_dtype=torch.bfloat16, device_map="cuda:0")
    model = None
    if sdpa_vision:
        try:
            model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                MODEL_ID, attn_implementation={"text_config": "eager",
                                               "vision_config": "sdpa"}, **common)
            print("[load] vision tower=SDPA, LM=eager")
        except Exception as e:                      # 버전 미지원 → eager 전체로 fallback
            print(f"[load] per-subconfig attn 미지원 ({type(e).__name__}) — eager 전체로 진행")
            model = None
    if model is None:
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            MODEL_ID, attn_implementation="eager",   # C-1 필수: 4D mask 주입 + attention 추출
            **common)
    model.eval()
    torch.set_grad_enabled(False)
    proc_kwargs = {"max_pixels": max_pixels} if max_pixels else {}
    processor = AutoProcessor.from_pretrained(MODEL_ID, **proc_kwargs)
    return model, processor


def text_config(model):
    return getattr(model.config, "text_config", model.config)


def num_layers(model) -> int:
    return text_config(model).num_hidden_layers


def resolve_decoder_layers(model):
    layers = None
    for path in _LAYER_PATHS:
        try:
            cand = operator.attrgetter(path)(model)
        except AttributeError:
            continue
        if hasattr(cand, "__len__") and len(cand) > 0 and hasattr(cand[0], "self_attn"):
            layers = cand
            break
    if layers is None:
        blocked("mask", "decoder layers 경로 미발견",
                {"model_cls": type(model).__name__, "tried": list(_LAYER_PATHS)})
    n = num_layers(model)
    if len(layers) != n:
        blocked("mask", "layer 수 불일치 (vision block 혼입 의심)",
                {"len_layers": len(layers), "num_hidden_layers": n})
    for i, ly in enumerate(layers):
        li = getattr(ly.self_attn, "layer_idx", i)
        if li is not None and li != i:
            blocked("mask", "layer_idx 불일치", {"enumerate": i, "hf_layer_idx": li})
    return list(layers)


def vision_token_ids(processor):
    """special token id 실측 조회 (하드코딩 금지 — 03 §B 지침)."""
    tok = processor.tokenizer
    ids = {}
    for name in ("<|vision_start|>", "<|vision_end|>", "<|image_pad|>"):
        t = tok.convert_tokens_to_ids(name)
        if t is None or t == tok.unk_token_id:
            blocked("model", f"special token 미발견: {name}", {})
        ids[name] = t
    return ids["<|vision_start|>"], ids["<|vision_end|>"], ids["<|image_pad|>"]
