#!/usr/bin/env python
"""S2 방어: "CLIP으로 관련 이미지 고르면 되지 않나?" 에 대한 정면 비교 (탐색적).

CLIP(ViT-B/32)으로 질문 텍스트 vs 두 이미지의 유사도를 재어 관련 이미지를 고르게 하고,
(a) 식별 정확도, (b) 추가 비용(별도 모델 forward)을 우리 in-forward 컨트롤러와 비교한다.
CLIP은 이미지를 독립적으로 인코딩하므로 position bias가 원천적으로 없다 — 강한 baseline.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch
from PIL import Image

from sourcedepth.config import COCO_IMG_DIR, PAIRS_CSV, RESULTS_DIR, SEED
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase
from sourcedepth.runlog import blocked, dump_env, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / "clip_baseline.json"
CLIP_ID = "openai/clip-vit-base-patch32"


def main():
    dump_env("12_clip")
    if not torch.cuda.is_available():
        blocked("12_clip", "GPU 없음", {})
    torch.manual_seed(SEED)
    from transformers import CLIPModel, CLIPProcessor

    rows = pd.read_csv(PAIRS_CSV).to_dict("records")
    with stage("12_clip_baseline"):
        model = CLIPModel.from_pretrained(CLIP_ID).to(DEV).eval()
        proc = CLIPProcessor.from_pretrained(CLIP_ID)

        hit = 0
        margins = []
        t_total = 0.0
        with torch.no_grad():
            for row in rows:
                # 질문 텍스트: 객체구 중심 (CLIP은 문장형 질의보다 명사구에 강함 — baseline에 유리하게)
                text = f"a photo of {obj_phrase(row['article'], row['object'])}"
                ims = [Image.open(image_path(int(row[f"image{i}_id"]), COCO_IMG_DIR)).convert("RGB")
                       for i in (1, 2)]
                inputs = proc(text=[text], images=ims, return_tensors="pt", padding=True).to(DEV)
                torch.cuda.synchronize()
                t0 = time.perf_counter()
                out = model(**inputs)
                torch.cuda.synchronize()
                t_total += (time.perf_counter() - t0) * 1000
                sims = out.logits_per_image[:, 0]          # (2,) 이미지별 텍스트 유사도
                s1, s2 = sims[0].item(), sims[1].item()
                # oracle: 관련 이미지는 항상 image1. 단 cell 1·4는 distractor에도 객체가 있어
                # '객체 유무' 기준으론 원리적으로 구분 불가 → 셀별로 분리 보고한다.
                hit += int(s1 > s2)
                margins.append({"cell": int(row["cell"]), "s1": s1, "s2": s2,
                                "correct": bool(s1 > s2)})

        df = pd.DataFrame(margins)
        by_cell = df.groupby("cell")["correct"].mean().to_dict()
        # 셀 2·3 = distractor에 질의 객체 없음 → CLIP이 원리적으로 풀 수 있는 부분집합
        solvable = df[df["cell"].isin([2, 3])]["correct"].mean()
        summary = {
            "clip_model": CLIP_ID,
            "overall_identification": round(hit / len(rows), 4),
            "by_cell": {int(k): round(v, 4) for k, v in by_cell.items()},
            "on_solvable_cells_2_3": round(float(solvable), 4),
            "extra_cost_ms_per_item_median": round(float(pd.Series(
                [t_total / len(rows)]).median()), 2),
            "note": ("셀 1·4는 distractor에도 질의 객체가 존재해 CLIP의 객체 유사도로는 "
                     "원리적으로 구분 불가 — 이것이 '외부 relevance 모델'의 구조적 한계다. "
                     "우리 컨트롤러는 질문의 지시어(first image)까지 조건화된 내부 신호를 쓴다."),
        }
        OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=1))
        print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
