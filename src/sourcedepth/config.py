"""SourceDepth Phase 0 — 모든 상수의 단일 출처.

사전 등록 결정 (docs/03 §A, 권장값 채택 확정 2026-08-10):
  A-1 FLOPs 분모 = 실측 N (36 예상)
  A-2 Flip Rate = 분모 셀 전체 150, 셀별 지정 방향만, 판정 ① 3요건 전부
  A-3 MASK_SPAN_MODE = with_delimiters (vision_start~vision_end 전 구간 차단)
  A-4 distractor pool = 질의 객체 supercategory 소속 객체 ≥1 포함 이미지
  A-5 ② 분모 격차 < 0.05 → 판정 ② 전체 INDETERMINATE (PASS 격상 금지)
  A-6 ARTICLE_MODE = preserve_pope (POPE 원문 관사 보존)
"""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"
LOGS_DIR = REPO_ROOT / "logs"

SEED = 42
# 모델 스위칭 (7B 재현 실험용): SD_MODEL_ID + SD_TAG(결과 파일 suffix, 예: "_7b")
MODEL_ID = os.environ.get("SD_MODEL_ID", "Qwen/Qwen2.5-VL-3B-Instruct")
TAG = os.environ.get("SD_TAG", "")

L_GRID = [4, 8, 12, 16, 20, 24]
L_GRID_FALLBACK = [2, 4, 6, 8, 10, 12]  # PART D ② 실패 대응 전용 (각 1회)
CONDITIONS = ["S", "M", "T4", "T8", "T12", "T16", "T20", "T24", "T0", "Trel8"]

N_PER_CELL = 150
PAIRING_OVERGEN = 160  # 이미지 다운로드 실패 대비 여분 생성 후 상위 150 사용
# cell: (gt_label, distractor_contains_object)
CELL_SPEC = {1: ("no", True), 2: ("yes", False), 3: ("no", False), 4: ("yes", True)}

MASK_SPAN_MODE = "with_delimiters"   # A-3
ARTICLE_MODE = "preserve_pope"       # A-6
INDET_GAP = 0.05                     # A-5: |Acc(T0)-Acc(M)| < 5%p → 셀 판정 불가

# 프롬프트 (브리프 B-1/B-2 문구, {obj}에 관사 포함 객체구 삽입: "an orange")
PROMPT_MULTI = "In the first image, is there {obj}? Answer with Yes or No."
PROMPT_SINGLE = "In the image, is there {obj}? Answer with Yes or No."
# 순서 뒤집기 대조 실행 전용 (탐색적 — ③ position bias 분리): [distractor, 원본] + "second image"
PROMPT_MULTI_SECOND = "In the second image, is there {obj}? Answer with Yes or No."
# sanity 2 실패 시에만 사용 (C-4 fallback). build_inputs가 라벨 텍스트를 삽입한다.
TEMPLATE_PRIMARY = "primary"
TEMPLATE_FALLBACK = "picture_labels"

POPE_ADV = DATA_DIR / "pope" / "coco_pope_adversarial.json"
POPE_POP = DATA_DIR / "pope" / "coco_pope_popular.json"
COCO_INSTANCES = DATA_DIR / "coco" / "annotations" / "instances_val2014.json"
COCO_IMG_DIR = DATA_DIR / "coco" / "images"
COCO_IMG_URL = "http://images.cocodataset.org/val2014/COCO_val2014_{id:012d}.jpg"

PAIRS_CSV = RESULTS_DIR / "pairs.csv"        # 모델 간 공유 (동일 데이터)
RAW_RESULTS = RESULTS_DIR / f"raw_results{TAG}.jsonl"
SMOKE_RESULTS = RESULTS_DIR / f"smoke_results{TAG}.jsonl"
ATTN_PROFILE = RESULTS_DIR / f"attn_profile{TAG}.jsonl"
ATTN_PROFILE_SWAPPED = RESULTS_DIR / f"attn_profile_swapped{TAG}.jsonl"
TOKEN_IDS_JSON = RESULTS_DIR / f"token_ids{TAG}.json"
TEMPLATE_CHOICE = RESULTS_DIR / f"template_choice{TAG}.json"
SANITY_FLAG = RESULTS_DIR / f"SANITY_PASSED{TAG}"
SMOKE_FLAG = RESULTS_DIR / f"SMOKE_PASSED{TAG}"

# 판정 상수 (PART D 사전 등록 — 결과 보고 변경 금지)
FLIP_THRESH = 0.10
RECOVERY_FRAC = 0.5
MCNEMAR_ALPHA = 0.05
IDENT_THRESH = 0.80          # ③: layer 8 (1-indexed) 만 판정, layer 4는 측정만
PROFILE_LAYERS_1IDX = [4, 8]

SANITY1_PASS = 0.90
SANITY1_BUG = 0.70
SANITY2_ACC = 0.60           # 자동 게이트: 셀 3·4 표본만 사용 (03 §B-2)
SANITY3_ACC = 0.60
