#!/usr/bin/env python
"""부분 관련(partial relevance) — selection이 잘못된 추상임을 보이는 실험.

## 왜

지금까지 설계는 이미지가 **100% 관련 or 0% 관련**이었다. 그러면 앞단 selector가
원리적으로 가능하다(넣거나 빼면 됨). 실제 응용(인터리브 문서·롱비디오·멀티모달 RAG)에서는
**부분 관련**이 기본값이다.

부분 관련 이미지 B가 있을 때 selector의 선택지는 둘뿐이다:
  포함 → 오염을 감수   /   제외 → 필요한 정보를 잃음
우리는 제3의 선택지가 있다: **맥락으로 남기고 증거로만 차단.**

## 설계 (3장: 원본 + 부분관련 + 무관)

질문: "In the first image, is there {obj}?"  (gt 균형)
  PART-hit  : 2번 이미지에 질의 객체가 **작게** 존재 (COCO bbox 면적 하위 20%)
              → 관련도가 애매. 포함하면 오염 압력, 제외하면 정보 손실
  PART-miss : 2번 이미지에 질의 객체 없음 (대조군)
  3번은 항상 무관 이미지

조건:
  M      : 무개입 (전부 보임)                    ← selector "포함"
  DROP2  : 2번(부분관련) 통째 차단                ← selector "제외"
  READ2  : 2번을 질문만 못 읽게 (맥락은 유지)      ← 우리 제3의 선택지
  DROP3 / READ3 : 3번(무관)에 대한 동일 조건 (참조)

## 판정 (사전 고정)

**핵심**: PART-hit 문항에서  READ2 > max(M, DROP2)  이면 selection이 표현할 수 없는
우월 지점이 존재한다 → "selection은 잘못된 추상" 주장 성립.
CI가 0을 배제해야 한다. 아니면 성립하지 않는 것으로 보고한다.
"""
import argparse, json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd, torch
from sourcedepth.config import (COCO_IMG_DIR, COCO_INSTANCES, PAIRS_CSV,
                                RESULTS_DIR, SEED, TAG, TEMPLATE_CHOICE)
from sourcedepth.data.coco_index import build_indices
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
OUT = RESULTS_DIR / f"partial{TAG}.jsonl"
ITEMS = RESULTS_DIR / "partial_items.json"
CONDS = ["M", "DROP2", "READ2", "DROP3", "READ3"]
N_PER = 150

def build_items():
    """2번 이미지: 질의 객체가 작게 존재(PART-hit) / 없음(PART-miss). 3번: 항상 무관."""
    idx = build_indices(COCO_INSTANCES)
    have = {i for i in idx.img2cats if image_path(i, COCO_IMG_DIR).exists()}
    # 부분 관련 = 질의 객체가 존재하되 화면에서 아주 작게 차지 (면적비 < 2%)
    small = {}
    for (img, cat), frac in idx.maxfrac.items():
        if frac < 0.02 and img in have:
            small.setdefault(cat, set()).add(img)
    if not small:
        blocked("32_partial", "maxfrac 인덱스 비어 있음", {})
    rng = random.Random(SEED); out = []
    for r in pd.read_csv(PAIRS_CSV).to_dict("records"):
        cat = int(r["category_id"]); used = {int(r["image1_id"]), int(r["image2_id"])}
        pool_small = [i for i in sorted(small.get(cat, set())) if i in have and i not in used]
        pool_none  = [i for i in sorted(have) if i not in used and cat not in idx.img2cats.get(i, set())]
        if not pool_small or len(pool_none) < 2: continue
        grp = "PART-hit" if len(out) % 2 == 0 else "PART-miss"
        img2 = rng.choice(pool_small) if grp == "PART-hit" else rng.choice(pool_none)
        img3 = rng.choice([x for x in pool_none if x != img2])
        out.append({"question_id": f"pr{r['question_id']}", "group": grp, "gt": r["gt"],
                    "article": r["article"], "object": r["object"], "category_id": cat,
                    "image1_id": int(r["image1_id"]), "image2_id": int(img2),
                    "image3_id": int(img3)})
    final = []
    for g in ("PART-hit", "PART-miss"):
        final += [x for x in out if x["group"] == g][:N_PER]
    print("문항:", {g: sum(x["group"] == g for x in final) for g in ("PART-hit", "PART-miss")})
    if len(final) < 100: blocked("32_partial", f"문항 부족: {len(final)}", {})
    ITEMS.write_text(json.dumps(final, ensure_ascii=False)); return final

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    dump_env("32_partial_relevance")
    if not torch.cuda.is_available(): blocked("32_partial", "GPU 없음", {})
    torch.manual_seed(SEED)
    template = json.loads(TEMPLATE_CHOICE.read_text())["template"]
    rows = json.loads(ITEMS.read_text()) if ITEMS.exists() else build_items()
    if args.limit: rows = rows[: args.limit]
    print(f"{len(rows)} 문항 × {len(CONDS)} 조건")
    with stage("32_partial_relevance"):
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
            ims = [image_path(row[f"image{i}_id"], COCO_IMG_DIR) for i in (1, 2, 3)]
            inputs = build_inputs(processor, ims, q_multi, DEV, template)
            sp = find_vision_spans(inputs["input_ids"], vs, ve, pad)
            if len(sp) != 3: blocked("32_partial", f"span != 3: {len(sp)}", {"qid": qid})
            seq = int(inputs["input_ids"].shape[1]); ts = (sp[-1][1] + 1, seq - 1)
            for cond in todo:
                t0 = time.time()
                if cond == "M": ctrl.disable()
                elif cond.startswith("DROP"): ctrl.configure_pathway([(0, None, sp[int(cond[4:]) - 1])])
                else: ctrl.configure_pathway([(0, ts, sp[int(cond[4:]) - 1])])
                try:
                    try: out = model(**inputs, use_cache=False)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache(); out = model(**inputs, use_cache=False)
                finally: ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": qid, "group": row["group"], "gt": row["gt"],
                                   "condition": cond, **p, "correct": p["pred"] == row["gt"],
                                   "n_layers": nlay, "seq_len": seq,
                                   "elapsed_ms": int(1000*(time.time()-t0)), "ts": iso_now()})
                executed += 1; del out
            del inputs; torch.cuda.empty_cache()
        print(f"executed {executed}")

if __name__ == "__main__": main()
