#!/usr/bin/env python
"""비용 실측 — FOCUS 방식(픽셀 노이즈 재인코딩) vs 우리 방식(KV 마스킹).

FOCUS는 이미지를 픽셀에서 노이즈로 덮으므로 **매 pass마다 vision encoder를 다시 돌린다.**
우리는 같은 시각 인코딩을 재사용하고 attention mask만 바꾼다.

측정 (이미지 4장 = 방해 3장, 문항 40개, median):
  t_full     : 전체 forward (vision encoder + LLM)
  t_vision   : vision encoder 단독
  t_kvmask   : 이미지 인코딩 재사용 + KV 마스킹 forward  ← 우리 반사실 1회
  t_pixel    : 픽셀 노이즈로 덮고 재인코딩 + forward     ← FOCUS 반사실 1회

이로부터 파이프라인 비용:
  FOCUS : (N+1) × t_pixel
  우리  : t_full + N × (t_kvmask − t_vision) × (1 − L/n_layers) + t_vision
        (L층부터만 재계산 가정 — 30번 실험이 L을 정당화해야 유효)
"""
import argparse, json, statistics as st, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import torch
from PIL import Image
from sourcedepth.config import COCO_IMG_DIR, RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import blocked, dump_env, iso_now, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"cost_bench{TAG}.json"
ITEMS = RESULTS_DIR / "scale_auc_items.json"
N_ITEM, N_DIST, WARM = 40, 3, 5

def timeit(fn, n_warm=WARM):
    for _ in range(n_warm): fn()
    torch.cuda.synchronize(); t = time.time(); fn(); torch.cuda.synchronize()
    return 1000 * (time.time() - t)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=N_ITEM)
    args = ap.parse_args()
    dump_env("31_cost_bench")
    if not torch.cuda.is_available(): blocked("31_cost", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = json.loads(ITEMS.read_text())[: args.limit]
    with stage("31_cost_bench"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        rec = {"t_full": [], "t_vision": [], "t_kvmask": [], "t_pixel": []}
        for row in rows:
            paths = [image_path(row["image1_id"], COCO_IMG_DIR)] + \
                    [image_path(d, COCO_IMG_DIR) for d in row["distractors"][:N_DIST]]
            ims = [Image.open(p).convert("RGB") for p in paths]
            q_multi, _ = questions_for(row)
            inputs = build_inputs(processor, paths, q_multi, DEV, template)
            sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
            ctrl.disable()
            rec["t_full"].append(timeit(lambda: model(**inputs, use_cache=False)))
            pv, gt = inputs["pixel_values"], inputs["image_grid_thw"]
            rec["t_vision"].append(timeit(lambda: model.visual(pv, grid_thw=gt)))
            def kvmask():
                ctrl.configure_multi([(0, sp[1])])
                try: model(**inputs, use_cache=False)
                finally: ctrl.disable()
            rec["t_kvmask"].append(timeit(kvmask))
            # FOCUS 방식: 방해 이미지를 노이즈로 덮고 processor부터 다시
            noisy = [ims[0]] + [Image.effect_noise(im.size, 64).convert("RGB") for im in ims[1:]]
            def pixel():
                inp = processor(text=[q_multi], images=noisy, return_tensors="pt").to(DEV)
                model(**inp, use_cache=False)
            rec["t_pixel"].append(timeit(pixel))
            del inputs
            torch.cuda.empty_cache()
        med = {k: round(st.median(v), 2) for k, v in rec.items()}
        med["n_items"], med["n_images"], med["n_layers"] = len(rows), N_DIST + 1, nlay
        med["t_llm"] = round(med["t_full"] - med["t_vision"], 2)
        med["vision_share_pct"] = round(100 * med["t_vision"] / med["t_full"], 1)
        for L in (0, 8, 16, 24):
            focus = (N_DIST + 1) * med["t_pixel"]
            ours = med["t_full"] + N_DIST * med["t_llm"] * (1 - L / nlay)
            med[f"pipeline_L{L}"] = {"FOCUS_ms": round(focus, 1), "ours_ms": round(ours, 1),
                                     "saving_pct": round(100 * (1 - ours / focus), 1)}
        med["ts"] = iso_now()
        OUT.write_text(json.dumps(med, ensure_ascii=False, indent=1))
        print(json.dumps(med, ensure_ascii=False, indent=1))

if __name__ == "__main__": main()
