#!/usr/bin/env python
"""C-5 단계 2: sanity 3종 (C-4) — 미통과 시 본 실험 진입 금지.

실행 순서는 2(grounding/템플릿 확정) → 1(T0 vs S) → 3(S 정답률).
브리프의 번호 순서와 다르지만 요구 게이트는 전부 동일하게 적용 — fallback 채택 시
sanity 1·3과 토큰 probe를 확정 템플릿으로 실행하기 위한 순서 최적화일 뿐이다.
자동 게이트는 셀 3·4 표본만 사용 (03 §B-2: 셀 1·2 오답은 leakage일 수 있음).
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch

from sourcedepth.config import (COCO_IMG_DIR, LOGS_DIR, PAIRS_CSV, RAW_RESULTS,
                                SANITY1_BUG, SANITY1_PASS, SANITY2_ACC,
                                SANITY3_ACC, SANITY_FLAG, SEED, SMOKE_FLAG,
                                TEMPLATE_CHOICE, TEMPLATE_FALLBACK,
                                TEMPLATE_PRIMARY)
from sourcedepth.data.download import image_path
from sourcedepth.eval.loop import questions_for, run_eval
from sourcedepth.eval.yesno import load_yes_no_ids, resolve_yes_no_ids
from sourcedepth.model.inputs import build_inputs
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.runlog import blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"


def sample_cells(pairs, spec, rng):
    """spec: {cell: n}. 반환 dict rows 목록 (결정적 — 문항 id 정렬 후 rng 추출)."""
    out = []
    for cell, k in spec.items():
        sub = pairs[pairs["cell"] == cell].sort_values("question_id").reset_index(drop=True)
        picks = rng.sample(range(len(sub)), k)
        out.extend(sub.iloc[i].to_dict() for i in picks)
    return out


def grounding_check(items, model, processor, template):
    """20문항 생성 → 육안 로그 + 셀 3·4 자동 게이트 acc 반환."""
    tok = processor.tokenizer
    lines, gate_ok, gate_n = [], 0, 0
    for s in items:
        q_multi, _ = questions_for(s)
        im1 = image_path(int(s["image1_id"]), COCO_IMG_DIR)
        im2 = image_path(int(s["image2_id"]), COCO_IMG_DIR)
        inp = build_inputs(processor, [im1, im2], q_multi, DEV, template)
        gen = model.generate(**inp, max_new_tokens=10, do_sample=False)
        text = tok.decode(gen[0, inp["input_ids"].shape[1]:], skip_special_tokens=True)
        first = text.strip().split()[0].strip(".,!").lower() if text.strip() else ""
        pred = first if first in ("yes", "no") else "unparsed"
        cell = int(s["cell"])
        lines.append(f"- [cell {cell}] {s['question_id']} | q={q_multi!r} | "
                     f"img1_has_obj={s['gt']=='yes'} img2_has_obj={bool(s['cell'] in (1, 4))} | "
                     f"gen={text!r} → pred={pred} gt={s['gt']}")
        if cell in (3, 4):
            gate_n += 1
            gate_ok += int(pred == s["gt"])
    acc = gate_ok / gate_n if gate_n else 0.0
    header = (f"# sanity 2 grounding — template={template} acc(cell3·4)={acc:.2f} {iso_now()}\n"
              f"(주의: 셀 1·2의 오답은 본 연구가 측정하려는 leakage일 수 있음 — 게이트는 셀 3·4만 사용)\n")
    with open(LOGS_DIR / "sanity2_grounding.md", "a") as f:
        f.write(header + "\n".join(lines) + "\n")
    print(header)
    return acc


def main():
    dump_env("02_sanity")
    if not SMOKE_FLAG.exists():
        blocked("02_sanity", "SMOKE_PASSED 부재 — 스모크 미통과", {})
    if not torch.cuda.is_available():
        blocked("02_sanity", "GPU 없음", {})
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)

    pairs = pd.read_csv(PAIRS_CSV)
    model, processor = load_model_and_processor()
    layers = resolve_decoder_layers(model)
    ctrl = KVBlockController(model, layers)
    vs_ve_pad = vision_token_ids(processor)

    # ---- sanity 2: "first image" grounding → 템플릿 확정 ----
    with stage("02_sanity2_grounding"):
        rng2 = random.Random(SEED)
        items20 = sample_cells(pairs, {1: 5, 2: 5, 3: 5, 4: 5}, rng2)
        template = TEMPLATE_PRIMARY
        acc_primary = grounding_check(items20, model, processor, template)
        acc_fb = None
        fallback_adopted = False
        if acc_primary < SANITY2_ACC:
            print(f"primary 템플릿 게이트 실패 (acc={acc_primary:.2f}) → fallback 시도 (C-4)")
            template = TEMPLATE_FALLBACK
            acc_fb = grounding_check(items20, model, processor, template)
            if acc_fb < SANITY2_ACC:
                blocked("02_sanity", "first-image grounding 실패 (fallback 포함)",
                        {"acc_primary": acc_primary, "acc_fallback": acc_fb})
            fallback_adopted = True
        acc = acc_fb if fallback_adopted else acc_primary   # 채택 템플릿의 게이트 값 (리뷰 지적)
        TEMPLATE_CHOICE.write_text(json.dumps(
            {"template": template, "fallback_adopted": fallback_adopted,
             "acc_gate": acc, "acc_primary": acc_primary, "acc_fallback": acc_fb,
             "ts": iso_now()}))
        print(f"template 확정: {template} (gate acc={acc:.2f})")

    # fallback 채택 시 토큰 probe 재확인 (03 §B-2 후속 처리)
    if fallback_adopted:
        with stage("02_reprobe_tokens"):
            rngp = random.Random(SEED + 1)
            items4 = sample_cells(pairs, {1: 1, 2: 1, 3: 1, 4: 1}, rngp)
            probes = []
            for s in items4:
                q_multi, q_single = questions_for(s)
                im1 = image_path(int(s["image1_id"]), COCO_IMG_DIR)
                im2 = image_path(int(s["image2_id"]), COCO_IMG_DIR)
                probes.append(build_inputs(processor, [im1], q_single, DEV, template))
                probes.append(build_inputs(processor, [im1, im2], q_multi, DEV, template))
            resolve_yes_no_ids(model, processor, probes,
                               log_path=LOGS_DIR / "yesno_probe_fallback.json")
    yes_ids, no_ids = load_yes_no_ids()

    # ---- sanity 1: T(0) vs S 일치율 (셀 3·4 각 30) ----
    with stage("02_sanity1_t0_vs_s"):
        rng1 = random.Random(SEED + 2)
        items60 = sample_cells(pairs, {3: 30, 4: 30}, rng1)
        run_eval(items60, ["S", "T0"], model, processor, ctrl, vs_ve_pad,
                 RAW_RESULTS, template, yes_ids, no_ids)
        rows = [r for r in read_jsonl(RAW_RESULTS) if r.get("template") == template]
        by_q = {}
        for r in rows:
            by_q.setdefault(r["question_id"], {}).setdefault(r["condition"], r["pred"])
            # setdefault = first-wins — 05_analyze의 중복 채택 정책과 통일 (리뷰 지적)
        qids = [s["question_id"] for s in items60]
        agree_list = [(q, by_q[q]["S"] == by_q[q]["T0"]) for q in qids]
        agree = sum(a for _, a in agree_list) / len(agree_list)
        disagree = [q for q, a in agree_list if not a]
        print(f"sanity1 agree = {agree:.3f} ({len(disagree)} disagree: {disagree[:10]})")
        (LOGS_DIR / "sanity1_detail.json").write_text(json.dumps(
            {"agree": agree, "disagree_qids": disagree, "n": len(agree_list)}))
        if agree < SANITY1_BUG:
            blocked("02_sanity", f"sanity1 {agree:.2f} < 0.70 — mask 구현 버그 의심", {})
        if agree < SANITY1_PASS:
            blocked("02_sanity", f"sanity1 {agree:.2f} ∈ [0.70, 0.90) — layout 차이 초과, 원인 조사 필요", {})

    # ---- sanity 3: S 정답률 (셀당 50 = 200) ----
    with stage("02_sanity3_s_acc"):
        rng3 = random.Random(SEED + 3)
        items200 = sample_cells(pairs, {1: 50, 2: 50, 3: 50, 4: 50}, rng3)
        run_eval(items200, ["S"], model, processor, ctrl, vs_ve_pad,
                 RAW_RESULTS, template, yes_ids, no_ids)
        rows = [r for r in read_jsonl(RAW_RESULTS)
                if r.get("template") == template and r["condition"] == "S"]
        by_q = {r["question_id"]: r for r in rows}
        accs = [by_q[s["question_id"]]["correct"] for s in items200]
        acc_s = sum(accs) / len(accs)
        print(f"sanity3 S accuracy = {acc_s:.3f} (POPE 3B급 보고치 ~0.8x와 비교해 REPORT 기록)")
        if acc_s < SANITY3_ACC:
            blocked("02_sanity", f"sanity3 acc {acc_s:.2f} < 0.60 — 평가 파이프라인 버그 의심", {})

    summary = {"template": template, "fallback_adopted": fallback_adopted,
               "sanity1_agree": agree, "sanity3_s_acc": acc_s,
               "sanity2_gate_acc": acc, "ts": iso_now()}
    (LOGS_DIR / "sanity_summary.json").write_text(json.dumps(summary, indent=1))
    SANITY_FLAG.write_text(json.dumps(summary))
    print("SANITY PASSED:", summary)


if __name__ == "__main__":
    main()
