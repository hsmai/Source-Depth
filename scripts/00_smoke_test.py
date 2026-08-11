#!/usr/bin/env python
"""서버 스모크 테스트 (04 문서 §9) — 5문항으로 전체 경로 관통. 통과 시 SMOKE_PASSED."""
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import torch

from sourcedepth.config import (CONDITIONS, LOGS_DIR, PAIRS_CSV, SEED,
                                SMOKE_FLAG, SMOKE_RESULTS, TEMPLATE_PRIMARY)
from sourcedepth.eval.loop import questions_for, run_eval
from sourcedepth.eval.metrics import accuracy, to_wide
from sourcedepth.eval.yesno import load_yes_no_ids, resolve_yes_no_ids
from sourcedepth.model.inputs import (build_inputs, find_vision_spans,
                                      span_decode_window)
from sourcedepth.model.load import (load_model_and_processor, num_layers,
                                    resolve_decoder_layers, vision_token_ids)
from sourcedepth.model.masking import KVBlockController
from sourcedepth.model.profiler import masses_from_attentions
from sourcedepth.runlog import blocked, dump_env, iso_now, read_jsonl, stage

DEV = "cuda:0"


def main():
    dump_env("00_smoke")
    if not torch.cuda.is_available():
        blocked("00_smoke", "GPU 없음 (C-1: CPU 실행 금지)", {})
    if not PAIRS_CSV.exists():
        blocked("00_smoke", "pairs.csv 부재 — 01_prepare_data 미실행", {})

    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    rng = random.Random(SEED)

    pairs = pd.read_csv(PAIRS_CSV)
    sample = []
    for cell in (1, 2, 3, 4, 1):
        sub = pairs[pairs["cell"] == cell]
        pick = sub.iloc[rng.randrange(len(sub))]
        while pick["question_id"] in [s["question_id"] for s in sample]:
            pick = sub.iloc[rng.randrange(len(sub))]
        sample.append(pick.to_dict())
    print("smoke sample:", [s["question_id"] for s in sample])

    with stage("00_load_model"):
        model, processor = load_model_and_processor()
        tok = processor.tokenizer
        n = num_layers(model)
        layers = resolve_decoder_layers(model)
        vs, ve, pad = vision_token_ids(processor)
        print(f"num_hidden_layers = {n} (브리프 전제 32와 비교 — REPORT 기록)")
        print(f"vision token ids: start={vs} end={ve} pad={pad}")
        attn_impl = getattr(model.config, "_attn_implementation", "?")
        print(f"attn_implementation = {attn_impl}")
        if attn_impl != "eager":
            blocked("00_smoke", "attn_implementation != eager (C-1 위반 — mask 주입·attn 추출 불가)",
                    {"attn_impl": attn_impl})

    ctrl = KVBlockController(model, layers)

    with stage("00_span_check"):
        from sourcedepth.config import COCO_IMG_DIR
        from sourcedepth.data.download import image_path
        lines = [f"# span check {iso_now()} (첫 3개 샘플 수동 확인용 — 브리프 C-3)\n"]
        for s in sample[:3]:
            q_multi, _ = questions_for(s)
            im1 = image_path(int(s["image1_id"]), COCO_IMG_DIR)
            im2 = image_path(int(s["image2_id"]), COCO_IMG_DIR)
            inp = build_inputs(processor, [im1, im2], q_multi, DEV)
            spans = find_vision_spans(inp["input_ids"], vs, ve, pad)
            assert len(spans) == 2
            lines.append(f"\n## {s['question_id']} seq_len={inp['input_ids'].shape[1]}")
            for i, sp in enumerate(spans, 1):
                lines.append(f"- img{i} span={sp} ({sp[1]-sp[0]+1} tokens): "
                             f"{span_decode_window(inp['input_ids'], tok, sp)}")
        (LOGS_DIR / "span_check.md").write_text("\n".join(lines))
        print("\n".join(lines))

    with stage("00_mask_verify"):
        s0 = sample[0]
        q_multi, _ = questions_for(s0)
        im1 = image_path(int(s0["image1_id"]), COCO_IMG_DIR)
        im2 = image_path(int(s0["image2_id"]), COCO_IMG_DIR)
        inp = build_inputs(processor, [im1, im2], q_multi, DEV)
        sp1, sp2 = find_vision_spans(inp["input_ids"], vs, ve, pad)
        # (1) T(N) ≡ M — hook 무발화 동등성
        ctrl.disable()
        lm = model(**inp, use_cache=False).logits[0, -1].float()
        ctrl.configure(n, sp2)
        ltn = model(**inp, use_cache=False).logits[0, -1].float()
        if not torch.equal(lm, ltn):
            # bf16 logit ulp가 ~0.06-0.125이므로 완충 임계는 그보다 커야 실행 가능 (리뷰 지적).
            # hook이 실제 발화하면 이미지 하나가 통째로 차단되어 logit이 O(1) 이상 변한다.
            if not torch.allclose(lm, ltn, atol=0.05, rtol=0):
                blocked("00_smoke", "T(N) != M — hook 부작용 존재", {})
            print("WARN: T(N) vs M bitwise 불일치, allclose(0.05) 통과 (커널 비결정성 허용)")
        # (2) 직접 관측: T(8)에서 idx>=8 layer의 img2 질량 == 0 (구조적 차단의 결정적 증거)
        ctrl.reset_counter()
        ctrl.configure(8, sp2)
        out = model(**inp, use_cache=False, output_attentions=True)
        ctrl.disable()
        if out.attentions is None or out.attentions[0] is None:
            blocked("00_smoke", "output_attentions=None — eager 미적용", {"attn_impl": attn_impl})
        for li, attn in enumerate(out.attentions):
            w = attn[0, :, -1, :].float()
            m2 = w[:, sp2[0]:sp2[1] + 1].sum().item()
            if li >= 8 and m2 > 1e-6:
                blocked("00_smoke", "차단 layer에서 distractor 질량 > 0", {"layer": li, "mass": m2})
            if li < 8 and m2 <= 0:
                blocked("00_smoke", "비차단 layer에서 distractor 질량 = 0 (차단 방향 오류)",
                        {"layer": li})
        exp = ctrl.expected_fires(8, n, 1)
        if sum(ctrl.fired.values()) != exp:
            blocked("00_smoke", "hook 발화 카운터 불일치",
                    {"fired": dict(ctrl.fired), "expected": exp})
        print(f"mask verify OK: T(N)≡M, T(8) 구조 차단 확인, fired={sum(ctrl.fired.values())}/{exp}")

    with stage("00_token_probe"):
        ctrl.disable()
        probes = []
        for s in sample[:4]:
            q_multi, q_single = questions_for(s)
            im1 = image_path(int(s["image1_id"]), COCO_IMG_DIR)
            im2 = image_path(int(s["image2_id"]), COCO_IMG_DIR)
            probes.append(build_inputs(processor, [im1], q_single, DEV))
            probes.append(build_inputs(processor, [im1, im2], q_multi, DEV))
        yes_ids, no_ids = resolve_yes_no_ids(model, processor, probes,
                                             log_path=LOGS_DIR / "yesno_probe.json")
        print(f"YES_IDS={yes_ids} NO_IDS={no_ids}")

    with stage("00_eval_50"):
        SMOKE_RESULTS.unlink(missing_ok=True)
        executed = run_eval(sample, CONDITIONS, model, processor, ctrl,
                            (vs, ve, pad), SMOKE_RESULTS, TEMPLATE_PRIMARY,
                            yes_ids, no_ids)
        rows = read_jsonl(SMOKE_RESULTS)
        assert executed == 50 and len(rows) == 50, f"executed={executed} rows={len(rows)}"
        assert all(r["pred"] in ("yes", "no") for r in rows)
        times = [r["elapsed_ms"] for r in rows]
        med = statistics.median(times)
        est_main_h = 6000 * med / 1000 / 3600
        print(f"forward median {med:.0f}ms → 본실험 6,000 forwards ≈ {est_main_h:.1f}h (추정)")
        if est_main_h > 10:
            print(f"WARN: 추정 {est_main_h:.1f}h가 main walltime 12h에 근접/초과 — "
                  f"resume 재제출 필요 가능성 (진행은 계속)")
        # resume 검증: 재실행 시 0 forward
        executed2 = run_eval(sample, CONDITIONS, model, processor, ctrl,
                             (vs, ve, pad), SMOKE_RESULTS, TEMPLATE_PRIMARY,
                             yes_ids, no_ids)
        assert executed2 == 0, f"resume 실패: {executed2}"
        print("resume check OK (0 forward on rerun)")

    with stage("00_profiler_check"):
        for s in sample[:2]:
            q_multi, _ = questions_for(s)
            im1 = image_path(int(s["image1_id"]), COCO_IMG_DIR)
            im2 = image_path(int(s["image2_id"]), COCO_IMG_DIR)
            inp = build_inputs(processor, [im1, im2], q_multi, DEV)
            sp1, sp2 = find_vision_spans(inp["input_ids"], vs, ve, pad)
            ctrl.disable()
            out = model(**inp, use_cache=False, output_attentions=True)
            masses = masses_from_attentions(out.attentions, sp1, sp2)
            assert len(masses) == n
        peak = torch.cuda.max_memory_allocated() / 2**30
        print(f"profiler OK, peak VRAM {peak:.1f} GiB")

    with stage("00_analyze_dryrun"):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        df = pd.DataFrame(read_jsonl(SMOKE_RESULTS))
        pred, corr = to_wide(df)
        _ = accuracy(corr, "M")
        fig, ax = plt.subplots()
        ax.plot([4, 8], [0.5, 0.5])
        fig.savefig(LOGS_DIR / "smoke_fig_test.png")
        plt.close(fig)
        print("analyze dry-run OK")

    SMOKE_FLAG.write_text(json.dumps({
        "ts": iso_now(), "num_hidden_layers": n, "attn_impl": attn_impl,
        "yes_ids": yes_ids, "no_ids": no_ids,
        "forward_median_ms": med, "est_main_hours": round(est_main_h, 2),
        "peak_vram_gib": round(peak, 2)}))
    print("SMOKE PASSED")


if __name__ == "__main__":
    main()
