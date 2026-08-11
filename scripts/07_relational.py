#!/usr/bin/env python
"""Gate 1 핵심: relational 질문에서 depth 차단의 반대 효과 측정 (탐색적 신규 실험).

질문: "Is there {obj} in both images?" — 답이 두 이미지 모두의 정보를 요구.
예측: distractor 세팅과 반대로, img2 차단 깊이 L이 얕을수록(=혼합 기회가 적을수록)
RB(양쪽 존재, gt=yes) 셀이 붕괴 → 단일 depth 정책 불가의 직접 증거.

서브셀 (각 N_REL):
  RB: obj ∈ img1 ∧ obj ∈ img2 → gt yes   (차단 시 img2 확인 불가 → no 오답 예상)
  R1: obj ∈ img1 만            → gt no
  R2: obj ∈ img2 만            → gt no    (차단 시 '우연히 정답' — bias 대조)
기존 다운로드 이미지(1,002장)와 annotation만 재사용 — 신규 다운로드 없음.
"""
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import torch

from sourcedepth.config import (COCO_IMG_DIR, COCO_INSTANCES, LOGS_DIR,
                                RESULTS_DIR, SEED)
from sourcedepth.data.coco_index import build_indices
from sourcedepth.data.download import image_path
from sourcedepth.eval.yesno import load_yes_no_ids, predict
from sourcedepth.model.inputs import build_inputs, find_vision_spans
from sourcedepth.model.load import (load_model_and_processor,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController, condition_to_block
from sourcedepth.runlog import append_jsonl, blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"
N_REL = 100
CONDS = ["M", "T4", "T8", "T12", "T16", "T20", "T24", "T0"]
OUT = RESULTS_DIR / "rel_results.jsonl"
PAIRS_OUT = RESULTS_DIR / "rel_pairs.json"
PROMPT_BOTH = "Is there {obj} in both images? Answer with Yes or No."
VOWELS = "aeiou"


def build_rel_pairs():
    idx = build_indices(COCO_INSTANCES)
    avail = {i for i in idx.img2cats if image_path(i, COCO_IMG_DIR).exists()}
    # annotation이 전혀 없는 이미지도 후보에 필요 (R1/R2의 '미포함' 쪽) — avail은 다운로드된 것만
    rng = random.Random(SEED)
    cats = sorted(idx.name2cat.items())
    rng.shuffle(cats)
    cells = {"RB": [], "R1": [], "R2": []}
    used = set()

    def article(o):
        return "an" if o[0] in VOWELS else "a"

    for name, cid in cats * 3:          # 여러 바퀴 돌며 채움
        if all(len(v) >= N_REL for v in cells.values()):
            break
        has = [i for i in avail if cid in idx.img2cats.get(i, set())]
        not_has = [i for i in avail if cid not in idx.img2cats.get(i, set())]
        rng.shuffle(has)
        rng.shuffle(not_has)
        for cell, pool_a, pool_b, gt in (("RB", has, has, "yes"),
                                         ("R1", has, not_has, "no"),
                                         ("R2", not_has, has, "no")):
            if len(cells[cell]) >= N_REL or not pool_a or not pool_b:
                continue
            a = pool_a[0]
            b = next((x for x in pool_b if x != a), None)
            if b is None or (a, b, cid) in used:
                continue
            used.add((a, b, cid))
            cells[cell].append({"cell": cell, "gt": gt, "object": name,
                                "article": article(name), "category_id": cid,
                                "image1_id": a, "image2_id": b})
    rows = [r for v in cells.values() for r in v]
    for i, r in enumerate(rows):
        r["question_id"] = f"rel{i}"
    counts = {k: len(v) for k, v in cells.items()}
    if any(c < N_REL for c in counts.values()):
        print(f"WARN: 서브셀 미달 {counts} — 가용 풀 한계, 그대로 진행")
    PAIRS_OUT.write_text(json.dumps(rows, ensure_ascii=False))
    return rows


def main():
    dump_env("07_relational")
    if not torch.cuda.is_available():
        blocked("07_rel", "GPU 없음", {})
    torch.manual_seed(SEED)

    rows = (json.loads(PAIRS_OUT.read_text()) if PAIRS_OUT.exists() else build_rel_pairs())
    print("relational pairs:", {c: sum(r['cell'] == c for r in rows) for c in ("RB", "R1", "R2")})

    with stage("07_relational"):
        model, processor = load_model_and_processor()
        layers = resolve_decoder_layers(model)
        ctrl = KVBlockController(model, layers)
        vs, ve, pad = vision_token_ids(processor)
        yes_ids, no_ids = load_yes_no_ids()
        tok = processor.tokenizer

        # grounding mini-check: 12문항 생성 육안 로그 (게이트 아님 — 정직 보고용)
        glog = [f"# relational grounding check {iso_now()}"]
        for r in rows[:6] + rows[N_REL:N_REL + 3] + rows[2 * N_REL:2 * N_REL + 3]:
            q = PROMPT_BOTH.format(obj=f"{r['article']} {r['object']}")
            inp = build_inputs(processor, [image_path(r["image1_id"], COCO_IMG_DIR),
                                           image_path(r["image2_id"], COCO_IMG_DIR)], q, DEV)
            gen = model.generate(**inp, max_new_tokens=8, do_sample=False)
            txt = tok.decode(gen[0, inp["input_ids"].shape[1]:], skip_special_tokens=True)
            glog.append(f"- [{r['cell']}] {r['object']} gt={r['gt']} gen={txt!r}")
        (LOGS_DIR / "rel_grounding.md").write_text("\n".join(glog))
        print("\n".join(glog))

        done = {(x["question_id"], x["condition"]) for x in read_jsonl(OUT)}
        executed = 0
        for r in rows:
            todo = [c for c in CONDS if (r["question_id"], c) not in done]
            if not todo:
                continue
            q = PROMPT_BOTH.format(obj=f"{r['article']} {r['object']}")
            inp = build_inputs(processor, [image_path(r["image1_id"], COCO_IMG_DIR),
                                           image_path(r["image2_id"], COCO_IMG_DIR)], q, DEV)
            sp = find_vision_spans(inp["input_ids"], vs, ve, pad)
            for cond in todo:
                t0 = time.time()
                bf, cols = condition_to_block(cond, sp[0], sp[1])
                if bf is None:
                    ctrl.disable()
                else:
                    ctrl.configure(bf, cols)
                try:
                    out = model(**inp, use_cache=False)
                finally:
                    ctrl.disable()
                p = predict(out.logits[0, -1].float(), yes_ids, no_ids)
                append_jsonl(OUT, {"question_id": r["question_id"], "cell": r["cell"],
                                   "gt": r["gt"], "condition": cond, **p,
                                   "correct": p["pred"] == r["gt"],
                                   "object": r["object"],
                                   "image1_id": r["image1_id"], "image2_id": r["image2_id"],
                                   "elapsed_ms": int(1000 * (time.time() - t0)),
                                   "ts": iso_now()})
                executed += 1
        print(f"executed {executed} forwards")

    # 요약
    res = read_jsonl(OUT)
    print(f"\n{'cond':>5} | " + " | ".join(f"{c:>6}" for c in ("RB", "R1", "R2")) + " | overall")
    for cond in CONDS:
        line = [cond]
        sub = [x for x in res if x["condition"] == cond]
        for cell in ("RB", "R1", "R2"):
            cc = [x for x in sub if x["cell"] == cell]
            line.append(f"{sum(x['correct'] for x in cc) / max(1, len(cc)):.3f}")
        line.append(f"{sum(x['correct'] for x in sub) / max(1, len(sub)):.3f}")
        print(f"{line[0]:>5} | " + " | ".join(f"{v:>6}" for v in line[1:]))


if __name__ == "__main__":
    main()
