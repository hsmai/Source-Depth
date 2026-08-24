#!/usr/bin/env python
"""기존 연구 직접 비교 — FOCUS식(픽셀 노이즈) · VCD식 vs 우리(attention 마스킹).

docs/34_baseline_prereg.md. 지금까지 비교 대상이 T0(오라클 전면 차단)뿐이어서
"FOCUS보다 나은가"를 한 번도 재지 않았다. 같은 문항·같은 N+1 반사실 논리에서
**개입 수단만** 바꿔 직접 비교한다.

조건 (scale_auc_items, N ∈ {1,3}):
  M       : 무개입
  FN{i}   : i번째 이미지를 픽셀 노이즈로 교체 (재인코딩)  ← FOCUS식 반사실
  FKEEP   : FOCUS식 컨트롤러가 고른 것만 남기고 나머지 노이즈  ← FOCUS식 최종 출력
  ALLN    : 전 이미지 노이즈  ← VCD식 음의 기준

우리 쪽 대응(REAL_READ / B{i})은 35_endtoend.py·24_loo_controller.py 결과와 짝지어 분석.
"""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import torch
from PIL import Image
from sourcedepth.config import COCO_IMG_DIR, RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import load_model_and_processor, num_layers, vision_token_ids
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"baselines{TAG}.jsonl"
ITEMS = RESULTS_DIR / "scale_auc_items.json"
NS = [1, 3]
NOISE_SIGMA = 64


def noisy_inputs(processor, base, paths, which, dtype):
    """which(set) 위치의 이미지를 같은 크기 노이즈로 교체 — 토큰 수 불변."""
    ims = []
    for j, p in enumerate(paths):
        im = Image.open(p).convert("RGB")
        ims.append(Image.effect_noise(im.size, NOISE_SIGMA).convert("RGB")
                   if j in which else im)
    enc = processor.image_processor(images=ims, return_tensors="pt")
    out = dict(base)
    out["pixel_values"] = enc["pixel_values"].to(DEV, dtype=dtype)
    out["image_grid_thw"] = enc["image_grid_thw"].to(DEV)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("38_baselines")
    if not torch.cuda.is_available(): blocked("38_base", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = json.loads(ITEMS.read_text())
    if args.limit: rows = rows[: args.limit]
    print(f"{len(rows)} 문항 × N∈{NS}")

    with stage("38_baselines"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"], x["n_dist"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]
            q_multi, _ = questions_for(row)
            paths_all = [image_path(row["image1_id"], COCO_IMG_DIR)] + \
                        [image_path(d, COCO_IMG_DIR) for d in row["distractors"]]
            for n in NS:
                conds = ["M"] + [f"FN{i}" for i in range(n + 1)] + ["ALLN", "FKEEP"]
                if all((qid, c, n) in done for c in conds): continue
                paths = paths_all[: n + 1]
                base = build_inputs(processor, paths, q_multi, DEV, template)
                sp = find_vision_spans(base["input_ids"], vs, ve, pad)
                if len(sp) != n + 1:
                    blocked("38_base", f"span != {n+1}: {len(sp)}", {"qid": qid})
                seq = int(base["input_ids"].shape[1]); dt = base["pixel_values"].dtype
                margins = {}
                for x in read_jsonl(OUT):
                    if x["question_id"] == qid and x["n_dist"] == n:
                        margins[x["condition"]] = x["margin"]

                def fire(cond, which):
                    nonlocal executed
                    t0 = time.time()
                    inp = base if which is None else noisy_inputs(processor, base, paths, which, dt)
                    try: out = model(**inp, use_cache=False)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache(); out = model(**inp, use_cache=False)
                    p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                    margins[cond] = p["margin"]
                    rec = {"question_id": qid, "cell": row["cell"], "gt": row["gt"],
                           "condition": cond, "n_dist": n, **p,
                           "correct": p["pred"] == row["gt"], "n_layers": nlay,
                           "seq_len": seq, "elapsed_ms": int(1000*(time.time()-t0)),
                           "ts": iso_now()}
                    if cond == "FKEEP":
                        rec["pick"] = pick; rec["pick_correct"] = pick == 0
                    append_jsonl(OUT, rec); executed += 1
                    del out, inp

                if (qid, "M", n) not in done: fire("M", None)
                for i in range(n + 1):
                    if (qid, f"FN{i}", n) not in done: fire(f"FN{i}", {i})
                if (qid, "ALLN", n) not in done: fire("ALLN", set(range(n + 1)))
                # FOCUS식 컨트롤러: 노이즈로 지웠을 때 답이 가장 크게 흔들리는 이미지 = 관련
                d = [abs(margins[f"FN{i}"] - margins["M"]) for i in range(n + 1)]
                pick = max(range(n + 1), key=lambda i: d[i])
                if (qid, "FKEEP", n) not in done:
                    fire("FKEEP", {i for i in range(n + 1) if i != pick})
                del base
                torch.cuda.empty_cache()
        print(f"executed {executed}")


if __name__ == "__main__": main()
