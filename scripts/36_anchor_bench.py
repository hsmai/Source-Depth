#!/usr/bin/env python
"""anchor 벤치 v0 — 질문이 위치를 알려주지 않는 벤치마크 (docs/32_anchor_prereg.md).

질문: "In the image that contains {anchor}, is there {obj}?"
관련 이미지는 위치가 아니라 **내용(anchor 객체 포함)** 으로 특정된다.
  - 관련 이미지: anchor 포함 / 방해 이미지: anchor 전부 미포함 (참조 유일성)
  - 셀1: 관련에 obj 없음, 방해에 obj 있음 → 정답 no  (적대)
  - 셀2: 관련에 obj 있음, 방해에 obj 없음 → 정답 yes
  - 관련 이미지 위치는 무작위 → 정규식·위치 전략으로 풀 수 없음

조건 (문항당, 이미지 K장):
  M / B0..B{K-1} (하나씩 전면 차단 → 컨트롤러) / ORD_READ (오라클) / REAL_READ (실현)
REAL_READ의 pick은 같은 실행의 B_i에서 즉석 계산 (규칙: argmax |margin(B_i) − margin(M)|).

3B 실행 시(TAG=="") CLIP selector도 같은 문항에서 측정: pred = argmax sim(img, "a photo containing {anchor}").
"""
import argparse, json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import torch
from sourcedepth.config import (COCO_IMG_DIR, COCO_INSTANCES, RESULTS_DIR, SEED, TAG,
                                TEMPLATE_CHOICE)
from sourcedepth.data.coco_index import build_indices
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import obj_phrase
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"anchor{TAG}.jsonl"
CLIP_OUT = RESULTS_DIR / "anchor_clip.jsonl"
ITEMS = RESULTS_DIR / "anchor_items.json"
KS = [2, 3]
N_PER = 150          # 셀당 · K당
PROMPT = "In the image that contains {anchor}, is there {obj}? Answer with Yes or No."
MAX_PER_PAIR = 4     # (anchor, obj) 쌍당 문항 상한 — 특정 쌍 집중 방지


def art(name): return "an" if name[0] in "aeiou" else "a"


def build_items():
    idx = build_indices(COCO_INSTANCES)
    have = sorted(i for i in idx.img2cats if image_path(i, COCO_IMG_DIR).exists())
    rng = random.Random(SEED + 13)
    cats = sorted(idx.name2cat.items())
    withc = {c: set(i for i in have if c in idx.img2cats[i]) for _, c in cats}
    rows, pair_n, seen = [], {}, set()
    quota = {(k, cell): N_PER for k in KS for cell in ("c1", "c2")}
    tries = 0
    while any(v > 0 for v in quota.values()) and tries < 600000:
        tries += 1
        (aname, acat), (qname, qcat) = rng.sample(cats, 2)
        if pair_n.get((acat, qcat), 0) >= MAX_PER_PAIR: continue
        k = rng.choice(KS); cell = rng.choice(("c1", "c2"))
        if quota[(k, cell)] <= 0: continue
        wa, wq = withc[acat], withc[qcat]
        # 관련: anchor 포함 + obj 상태 / 방해: anchor 미포함 + obj 반대 상태
        rel_pool = sorted(wa - wq) if cell == "c1" else sorted(wa & wq)
        dis_pool = sorted((wq - wa) if cell == "c1" else (set(have) - wa - wq))
        if len(rel_pool) < 1 or len(dis_pool) < k - 1: continue
        rel = rng.choice(rel_pool)
        ds = rng.sample(dis_pool, k - 1)
        if rel in ds: continue
        imgs = ds[:]; pos = rng.randrange(k); imgs.insert(pos, rel)
        key = (tuple(imgs), acat, qcat)
        if key in seen: continue
        seen.add(key)
        rows.append({"question_id": f"an{len(rows)}", "k": k, "cell": cell,
                     "gt": "no" if cell == "c1" else "yes",
                     "anchor": aname, "anchor_cat": acat, "object": qname,
                     "category_id": qcat, "rel_pos": pos,
                     "image_ids": [int(i) for i in imgs]})
        pair_n[(acat, qcat)] = pair_n.get((acat, qcat), 0) + 1
        quota[(k, cell)] -= 1
    built = {f"K{k}/{c}": sum(1 for r in rows if r["k"] == k and r["cell"] == c)
             for k in KS for c in ("c1", "c2")}
    print("anchor 문항:", built, f"(tries={tries})")
    if any(v < N_PER * 0.9 for v in built.values()):
        blocked("36_anchor", f"문항 미달: {built}", {})
    ITEMS.write_text(json.dumps(rows, ensure_ascii=False))
    return rows


def run_clip(rows):
    import glob, os
    from PIL import Image
    from transformers import CLIPModel, CLIPProcessor
    hf = os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
    cands = glob.glob(os.path.join(hf, "hub", "models--openai--clip-vit-base-patch32",
                                   "snapshots", "*"))
    if not cands:
        print("CLIP 스냅샷 없음 — selector 비교 생략"); return
    mdl = CLIPModel.from_pretrained(cands[0], use_safetensors=True,
                                    local_files_only=True).to(DEV).eval()
    proc = CLIPProcessor.from_pretrained(cands[0], local_files_only=True)
    done = {x["question_id"] for x in read_jsonl(CLIP_OUT)}
    for row in rows:
        if row["question_id"] in done: continue
        ims = [Image.open(image_path(i, COCO_IMG_DIR)).convert("RGB") for i in row["image_ids"]]
        text = f"a photo containing {obj_phrase(art(row['anchor']), row['anchor'])}"
        with torch.no_grad():
            inp = proc(text=[text], images=ims, return_tensors="pt", padding=True).to(DEV)
            sims = mdl(**inp).logits_per_image.float().cpu()[:, 0]
        pred = int(sims.argmax())
        append_jsonl(CLIP_OUT, {"question_id": row["question_id"], "k": row["k"],
                                "rel_pos": row["rel_pos"], "clip_pred": pred,
                                "clip_correct": pred == row["rel_pos"],
                                "sims": [round(float(s), 4) for s in sims], "ts": iso_now()})
    del mdl; torch.cuda.empty_cache()
    print("CLIP selector 완료")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("36_anchor_bench")
    if not torch.cuda.is_available(): blocked("36_anchor", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = json.loads(ITEMS.read_text()) if ITEMS.exists() else build_items()
    if args.limit: rows = rows[: args.limit]
    print(f"{len(rows)} 문항 (K∈{KS})")

    with stage("36_anchor_bench"):
        model, processor = load_model_and_processor(sdpa_vision=True)
        nlay = num_layers(model)
        ctrl = KVBlockController(model, resolve_decoder_layers(model))
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0
        for row in rows:
            qid = row["question_id"]; k = row["k"]
            conds = ["M"] + [f"B{i}" for i in range(k)] + ["ORD_READ", "REAL_READ"]
            if all((qid, c) in done for c in conds): continue
            q = PROMPT.format(anchor=obj_phrase(art(row["anchor"]), row["anchor"]),
                              obj=obj_phrase(art(row["object"]), row["object"]))
            paths = [image_path(i, COCO_IMG_DIR) for i in row["image_ids"]]
            inputs = build_inputs(processor, paths, q, DEV, template)
            sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
            if len(sp) != k:
                blocked("36_anchor", f"span != {k}: {len(sp)}", {"qid": qid})
            seq = int(inputs["input_ids"].shape[1]); ts = (sp[-1][1] + 1, seq - 1)
            margins = {}

            def fire(cond, rules):
                nonlocal executed
                t0 = time.time()
                if rules is None: ctrl.disable()
                else: ctrl.configure_pathway(rules)
                try:
                    try: out = model(**inputs, use_cache=False)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache(); out = model(**inputs, use_cache=False)
                finally: ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                margins[cond] = p["margin"]
                rec = {"question_id": qid, "k": k, "cell": row["cell"], "gt": row["gt"],
                       "rel_pos": row["rel_pos"], "condition": cond, **p,
                       "correct": p["pred"] == row["gt"], "n_layers": nlay, "seq_len": seq,
                       "elapsed_ms": int(1000*(time.time()-t0)), "ts": iso_now()}
                if cond == "REAL_READ": rec["pick"] = pick; rec["pick_correct"] = pick == row["rel_pos"]
                append_jsonl(OUT, rec); executed += 1
                del out

            # 재개 시 margin 복원
            for x in read_jsonl(OUT):
                if x["question_id"] == qid: margins[x["condition"]] = x["margin"]
            if (qid, "M") not in done: fire("M", None)
            for i in range(k):
                if (qid, f"B{i}") not in done: fire(f"B{i}", [(0, None, sp[i])])
            d = [abs(margins[f"B{i}"] - margins["M"]) for i in range(k)]
            pick = max(range(k), key=lambda i: d[i])
            rel = row["rel_pos"]
            if (qid, "ORD_READ") not in done:
                fire("ORD_READ", [(0, ts, sp[i]) for i in range(k) if i != rel])
            if (qid, "REAL_READ") not in done:
                fire("REAL_READ", [(0, ts, sp[i]) for i in range(k) if i != pick])
            del inputs
            torch.cuda.empty_cache()
        print(f"executed {executed}")
        del model
        torch.cuda.empty_cache()
    if TAG == "":
        with stage("36_anchor_clip"):
            run_clip(rows)


if __name__ == "__main__": main()
