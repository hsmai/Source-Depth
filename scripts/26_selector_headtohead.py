#!/usr/bin/env python
"""앞단 selector vs 모델 내부 반사실 — 같은 문항에서 직접 비교.

공격: "무관 이미지 판별을 CLIP 같은 앞단 모듈에서 하고, 유관 이미지만 VLM에 넣으면 되지 않나?"

이 실험이 그 공격을 정량으로 답한다. **핵심 논거**: 관련도는 의미론적(semantic)이 아니라
**모델 상대적(model-relative)**이다. 중요한 것은 "이 이미지가 질문과 의미상 가까운가"가 아니라
"이 이미지가 **이 모델의** 답을 바꾸는가"이고, 후자는 모델을 통과시키지 않으면 알 수 없다.

같은 scale_auc_items 문항·같은 N에서 세 가지 selector 정확도를 비교한다:
  (a) CLIP  — 텍스트-이미지 유사도 (질문 문장 기준)
  (b) CLIP-obj — 객체 이름만으로 유사도 (더 유리한 조건)
  (c) 반사실 — 이미 측정됨 (results/loo*.jsonl). 여기서는 (a)(b)만 계산해 붙인다.

출력: results/selector{TAG}.jsonl  — 문항별 각 selector의 예측 이미지 index
"""
import argparse
import glob
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import torch
from PIL import Image

from sourcedepth.config import COCO_IMG_DIR, RESULTS_DIR, SEED
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase
from sourcedepth.runlog import (append_jsonl, blocked, dump_env, iso_now,
                                read_jsonl, stage)

DEV = "cuda:0" if torch.cuda.is_available() else "cpu"
OUT = RESULTS_DIR / "selector.jsonl"
ITEMS = RESULTS_DIR / "scale_auc_items.json"
CLIP_ID = "openai/clip-vit-base-patch32"
NS = [1, 2, 3]
PROMPT = "a photo containing {obj}"


def load_clip():
    from transformers import CLIPModel, CLIPProcessor
    hf_home = os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
    cands = glob.glob(os.path.join(hf_home, "hub",
                                   "models--openai--clip-vit-base-patch32",
                                   "snapshots", "*"))
    if not cands:
        blocked("26_selector", "CLIP 로컬 스냅샷 없음", {"hf_home": hf_home})
    local = cands[0]
    model = CLIPModel.from_pretrained(local, use_safetensors=True,
                                      local_files_only=True).to(DEV).eval()
    proc = CLIPProcessor.from_pretrained(local, local_files_only=True)
    return model, proc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("26_selector_headtohead")
    torch.manual_seed(SEED)
    rows = json.loads(ITEMS.read_text())
    if args.limit:
        rows = rows[: args.limit]
    done = {(x["question_id"], x["n_dist"]) for x in read_jsonl(OUT)}

    with stage("26_selector_headtohead"):
        model, proc = load_clip()
        executed = 0
        for row in rows:
            qid = row["question_id"]
            paths = [image_path(row["image1_id"], COCO_IMG_DIR)] + \
                    [image_path(d, COCO_IMG_DIR) for d in row["distractors"]]
            obj = obj_phrase(row["article"], row["object"])
            texts = [PROMPT.format(obj=obj), row["object"]]
            for n in NS:
                if (qid, n) in done:
                    continue
                ims = [Image.open(p).convert("RGB") for p in paths[: n + 1]]
                with torch.no_grad():
                    inp = proc(text=texts, images=ims, return_tensors="pt",
                               padding=True).to(DEV)
                    out = model(**inp)
                    sims = out.logits_per_image.float().cpu()      # (n+1, 2)
                pred_q = int(sims[:, 0].argmax())      # 질문 문장 기준
                pred_o = int(sims[:, 1].argmax())      # 객체 이름만 기준
                append_jsonl(OUT, {"question_id": qid, "cell": row["cell"],
                                   "gt": row["gt"], "n_dist": n,
                                   "clip_q_pred": pred_q, "clip_obj_pred": pred_o,
                                   "clip_q_correct": pred_q == 0,
                                   "clip_obj_correct": pred_o == 0,
                                   "sims_q": [round(float(x), 4) for x in sims[:, 0]],
                                   "ts": iso_now()})
                executed += 1
        print(f"executed {executed}")

    res = read_jsonl(OUT)
    print(f"\n{'N':>2} {'CLIP(질문)':>11} {'CLIP(객체명)':>12} {'무작위':>8}  n")
    for n in NS:
        sub = [r for r in res if r["n_dist"] == n]
        if not sub:
            continue
        print(f"{n:>2} {sum(r['clip_q_correct'] for r in sub)/len(sub):11.4f}"
              f" {sum(r['clip_obj_correct'] for r in sub)/len(sub):12.4f}"
              f" {1/(n+1):8.3f}  {len(sub)}")


if __name__ == "__main__":
    main()
