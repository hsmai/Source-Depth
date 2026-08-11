#!/usr/bin/env python
"""C-5 단계 1: 데이터 준비 → pairs.csv (로그인 노드 CPU 작업, GPU 불필요)."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sourcedepth.config import (CELL_SPEC, COCO_IMG_DIR, COCO_INSTANCES,
                                LOGS_DIR, N_PER_CELL, PAIRS_CSV, POPE_ADV,
                                POPE_POP, RESULTS_DIR, SEED)
from sourcedepth.data.coco_index import build_indices
from sourcedepth.data.download import download_images, image_path
from sourcedepth.data.pairing import build_pairs, verify_pairs
from sourcedepth.data.pope import load_pope
from sourcedepth.runlog import blocked, dump_env, stage


def main():
    dump_env("01_prepare")
    for p in (POPE_ADV, POPE_POP, COCO_INSTANCES):
        if not p.exists() or p.stat().st_size == 0:
            blocked("01_prepare", f"소스 파일 부재: {p}", {})

    with stage("01_load_sources"):
        adv, adv_fail = load_pope(POPE_ADV)
        pop, pop_fail = load_pope(POPE_POP, id_prefix="p")
        idx = build_indices(COCO_INSTANCES)
        print(f"POPE adversarial: {len(adv)} (parse fail {len(adv_fail)}), "
              f"popular: {len(pop)} (parse fail {len(pop_fail)})")
        if adv_fail or pop_fail:
            print("PARSE FAILURES:", adv_fail[:5], pop_fail[:5])

    with stage("01_pairing"):
        df, stats = build_pairs(adv, pop, idx, seed=SEED)
        print("pairing stats:", json.dumps(stats, ensure_ascii=False))
        if any(v > 10 for v in stats["shortfall"].values()):
            blocked("01_prepare", "페어링 셀 미달 (여분 포함 실패)", stats)

    with stage("01_download_images"):
        ids = set(df["image1_id"]) | set(df["image2_id"])
        print(f"downloading {len(ids)} unique images ...")
        ok, failed = download_images(ids, COCO_IMG_DIR)
        print(f"images ok={len(ok)} failed={len(failed)}")
        if failed:
            df = df[~(df["image1_id"].isin(failed) | df["image2_id"].isin(failed))]

    with stage("01_finalize"):
        parts = []
        for c in CELL_SPEC:
            sub = df[df["cell"] == c]
            if len(sub) < N_PER_CELL:
                blocked("01_prepare", f"셀 {c} 문항 부족: {len(sub)} < {N_PER_CELL}", {})
            parts.append(sub.head(N_PER_CELL))
        final = __import__("pandas").concat(parts).reset_index(drop=True)
        errors = verify_pairs(final, idx)
        if errors:
            blocked("01_prepare", "검증 pass 실패", {"errors": errors[:10]})
        for r in final.itertuples():   # 이미지 실재 재확인
            for iid in (r.image1_id, r.image2_id):
                if not image_path(int(iid), COCO_IMG_DIR).exists():
                    blocked("01_prepare", f"이미지 파일 부재: {iid}", {})
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        final.to_csv(PAIRS_CSV, index=False)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOGS_DIR / "pairing_stats.json", "w") as f:
            json.dump({"stats": stats, "final_per_cell":
                       {c: int((final["cell"] == c).sum()) for c in CELL_SPEC},
                       "n_unique_images": len(set(final["image1_id"]) | set(final["image2_id"])),
                       "supercategory_dist": final["supercategory"].value_counts().to_dict()},
                      f, ensure_ascii=False, indent=1)
        print(f"pairs.csv written: {len(final)} rows -> {PAIRS_CSV}")


if __name__ == "__main__":
    random.seed(SEED)
    main()
