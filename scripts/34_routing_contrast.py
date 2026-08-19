#!/usr/bin/env python
"""경로 대비 재현 — 새 문항으로 (docs/30_routing_contrast_prereg.md)

기존 pairs.csv 이미지를 전부 제외하고 새로 구성한 300문항에서,
'읽기 차단(양) − 이미지간 차단(음)' 조합이 읽기 차단 단독보다 나은지 확인한다.
FOCUS 방식(픽셀 노이즈) 대조군과 판별기 포함 성능도 같은 실행에서 잰다.
"""
import argparse, json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd, torch
from PIL import Image
from sourcedepth.config import (COCO_IMG_DIR, COCO_INSTANCES, PAIRS_CSV,
                                RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE)
from sourcedepth.data.coco_index import build_indices
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase, questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"routing{TAG}.jsonl"
ITEMS = RESULTS_DIR / "routing_items.json"
CONDS = ["M", "B0", "B1", "READ1", "READ2", "XIMG", "NOISE2"]
N_PER = 100   # 적대 2셀 + 대조 2셀 = 400문항


def build_items():
    """기존 pairs.csv 이미지를 전부 제외한 새 문항."""
    idx = build_indices(COCO_INSTANCES)
    have = {i for i in idx.img2cats if image_path(i, COCO_IMG_DIR).exists()}
    old = pd.read_csv(PAIRS_CSV)
    used = set(old["image1_id"].astype(int)) | set(old["image2_id"].astype(int))
    pool = sorted(have - used)
    print(f"가용 이미지 {len(have)} 중 기존 사용 {len(used)} 제외 → {len(pool)}")
    rng = random.Random(SEED + 7)
    name2cat = idx.name2cat
    rows, seen = [], set()
    # 카테고리별로 '있는 이미지'와 '없는 이미지' 풀 구성
    for name, cat in sorted(name2cat.items()):
        withc = [i for i in pool if cat in idx.img2cats.get(i, set())]
        without = [i for i in pool if cat not in idx.img2cats.get(i, set())]
        if len(withc) < 2 or len(without) < 2:
            continue
        art = "an" if name[0] in "aeiou" else "a"
        for kind in ("c1", "c2", "c3", "c4"):
            for _ in range(6):
                if kind == "c1":          # 적대적: 정답 없다 · 방해에 객체 있음
                    im1, im2, gt = rng.choice(without), rng.choice(withc), "no"
                elif kind == "c2":        # 적대적: 정답 있다 · 방해에 객체 없음
                    im1, im2, gt = rng.choice(withc), rng.choice(without), "yes"
                elif kind == "c3":        # 대조: 정답 없다 · 방해에도 없음 (방해가 정답 방향)
                    im1, im2, gt = rng.choice(without), rng.choice(without), "no"
                else:                      # 대조: 정답 있다 · 방해에도 있음 (방해가 정답 방향)
                    im1, im2, gt = rng.choice(withc), rng.choice(withc), "yes"
                if im1 == im2 or (im1, im2) in seen:
                    continue
                seen.add((im1, im2))
                rows.append({"question_id": f"rt{len(rows)}", "kind": kind, "gt": gt,
                             "article": art, "object": name, "category_id": cat,
                             "image1_id": int(im1), "image2_id": int(im2)})
    final = []
    for k in ("c1", "c2", "c3", "c4"):
        sub = [r for r in rows if r["kind"] == k]
        rng.shuffle(sub)
        final += sub[:N_PER]
    print("새 문항:", {k: sum(r["kind"] == k for r in final) for k in ("c1", "c2", "c3", "c4")})
    if len(final) < 280:
        blocked("34_routing", f"문항 부족 {len(final)}", {})
    ITEMS.write_text(json.dumps(final, ensure_ascii=False))
    return final


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("34_routing_contrast")
    if not torch.cuda.is_available(): blocked("34_routing", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = json.loads(ITEMS.read_text()) if ITEMS.exists() else build_items()
    if args.limit: rows = rows[: args.limit]
    print(f"{len(rows)} 문항 × {len(CONDS)} 조건 = {len(rows)*len(CONDS)}회")

    with stage("34_routing_contrast"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]
            todo = [c for c in CONDS if (qid, c) not in done]
            if not todo: continue
            q_multi, _ = questions_for(row)
            p1 = image_path(int(row["image1_id"]), COCO_IMG_DIR)
            p2 = image_path(int(row["image2_id"]), COCO_IMG_DIR)
            inputs = build_inputs(processor, [p1, p2], q_multi, DEV, template)
            sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
            if len(sp) != 2: blocked("34_routing", f"span != 2: {len(sp)}", {"qid": qid})
            seq = int(inputs["input_ids"].shape[1]); ts = (sp[-1][1] + 1, seq - 1)
            noisy_in = None
            for cond in todo:
                t0 = time.time(); use = inputs
                if cond == "M": ctrl.disable()
                elif cond == "B0": ctrl.configure_pathway([(0, None, sp[0])])
                elif cond == "B1": ctrl.configure_pathway([(0, None, sp[1])])
                elif cond == "READ1": ctrl.configure_pathway([(0, ts, sp[0])])
                elif cond == "READ2": ctrl.configure_pathway([(0, ts, sp[1])])
                elif cond == "XIMG": ctrl.configure_pathway([(0, sp[1], sp[0])])
                else:                                    # NOISE2 — FOCUS 방식 대조군
                    ctrl.disable()
                    if noisy_in is None:
                        im2 = Image.open(p2).convert("RGB")
                        nz = Image.effect_noise(im2.size, 64).convert("RGB")
                        enc = processor.image_processor(images=[Image.open(p1).convert("RGB"), nz],
                                                        return_tensors="pt")
                        noisy_in = dict(inputs)
                        noisy_in["pixel_values"] = enc["pixel_values"].to(
                            DEV, dtype=inputs["pixel_values"].dtype)
                        noisy_in["image_grid_thw"] = enc["image_grid_thw"].to(DEV)
                    use = noisy_in
                try:
                    try: out = model(**use, use_cache=False)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache(); out = model(**use, use_cache=False)
                finally: ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "kind": row["kind"], "gt": row["gt"],
                                   "condition": cond, **p, "correct": p["pred"] == row["gt"],
                                   "n_layers": nlay, "seq_len": seq,
                                   "elapsed_ms": int(1000*(time.time()-t0)), "ts": iso_now()})
                executed += 1; del out
            del inputs, noisy_in
            torch.cuda.empty_cache()
        print(f"executed {executed}")


if __name__ == "__main__": main()
