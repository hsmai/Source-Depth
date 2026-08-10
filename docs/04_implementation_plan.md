# SourceDepth Phase 0 — 24h Feasibility 구현 계획서

> 대상 브리프: `docs/01_feasibility_brief.md` (PART B·C **frozen** — 본 문서는 그 실행 방법만 구체화하며 설계를 변경하지 않는다)
> 실행 환경: 연구실 서버 `10.20.23.30` Node 3 (pleiades3, RTX 3090 24GB), PBS batch 전용 (`docs/06_gpu_policy.md`)
> **작성 경위**: 구현 설계 agent 초안을 독립 검증 agent가 브리프와 전수 대조한 뒤, 지적 사항(11건 위반·9건 정정)을 본문에 반영한 판이다. 미확정 결정 6건은 [03_risks_and_watchpoints.md](03_risks_and_watchpoints.md) §A 참조 — **A-3(마스킹 범위)·A-6(관사)은 코드 작성 전 확정 필요**.

---

## 0. 표기 규약 및 불변 조건 (구현 전 합의 사항)

구현 전반에서 아래 규약을 단일하게 사용하고, 전부 REPORT.md에 명기한다.

| 항목 | 규약 |
|---|---|
| layer indexing | decoder layer는 **0-indexed** `idx ∈ {0..N−1}`, `N = num_hidden_layers` — Qwen2.5-VL-3B는 **36** (검증 확인, 브리프의 32 전제와 불일치 → REPORT "이상 징후·비고"에 병기하고 모든 수식은 실측 N으로 계산). config 접근은 버전에 따라 text_config 하위일 수 있으므로 `getattr(cfg, "num_hidden_layers", cfg.text_config.num_hidden_layers)` fallback 사용 |
| T(L)의 의미 | **`idx ≥ L`인 layer에서 distractor key 열 차단**. 즉 mixing이 허용되는 layer는 `idx 0..L−1`의 L개. T(0) = 전 layer 차단, T(N) = M과 bitwise 동일(검증용) |
| T-rel(8) | `idx ≥ 8`에서 **이미지1(원본)** 열 차단 |
| 프로파일링 "layer ℓ" | 1-indexed 표기 ℓ = 0-indexed `idx ℓ−1`. 즉 "layer 4 식별률" = `idx 3`의 attention, "layer 8" = `idx 7` (근거: overview §7 "초기 layer 4개 실행" → 4개 실행 시 마지막으로 관측 가능한 attention이 idx 3) |
| 차단 열 범위 | **[03 §A-3 결정 대기]** 후보 (a) `<|image_pad|>` 구간만 / (b) `<|vision_start|>`~`<|vision_end|>` delimiter 포함 전 구간. **03 문서 권장은 (b)** — delimiter 잔존 시 leakage 통로가 남아 ② 회복률이 과소평가될 수 있음. 확정값을 config 상수로 고정, 선택 근거와 구간 인덱스를 로그·REPORT에 기록 |
| M-RoPE / position id | **절대 수정 금지.** 개입 지점은 4D additive attention mask 하나뿐 |
| 프롬프트 | M/T 계열: `"In the first image, is there {article} {object}? Answer with Yes or No."` / S: `"In the image, ..."` — 관사는 [03 §A-6 결정 대기] (권장: POPE 원문 관사 a/an 보존. 브리프 문구 그대로 "a" 고정 시 "a orange" 비문 발생) |
| batch size | **기본 1** (6,000 forward × 초 단위 prefill로 5h 상한 내 충분. padding·per-sample mask 복잡도 제거 우선. 시간 초과 조짐 시에만 batched fallback) — **브리프 C-1의 "배치 4~8" 지침에서 의도적 이탈이므로 사유와 함께 REPORT에 명기** |
| 허용된 fallback | 브리프가 명시한 것만: popular split 보충(C-2), OOM 시 `max_pixels` 제한(C-1), sanity 2 실패 시 "Picture 1:" 프롬프트(C-4), PART D의 ①·② 실패 대응(각 1회). 그 외 막히면 전부 BLOCKED |

## 1. 저장소 레이아웃

```
Source-Depth/
├── requirements.txt              # 서버 설치 시점에 exact pin 고정 (§7.5)
├── src/sourcedepth/
│   ├── __init__.py
│   ├── config.py                 # 모든 상수의 단일 출처 (03 §A 결정 6건 포함)
│   ├── runlog.py                 # 단계 시각 로깅 + BLOCKED 프로토콜
│   ├── data/
│   │   ├── pope.py               # POPE jsonl 로드·객체명 파싱
│   │   ├── coco_index.py         # instances_val2014.json → 인덱스 3종
│   │   ├── pairing.py            # 4셀 페어링 → pairs.csv
│   │   └── download.py           # 개별 이미지 다운로드·무결성 체크
│   ├── model/
│   │   ├── load.py               # 모델·processor 로딩, layer resolver
│   │   ├── inputs.py             # chat template 입력 구성, vision span 특정
│   │   ├── masking.py            # KV 차단 (hook 방식 주, monkey-patch 예비)
│   │   └── profiler.py           # per-layer 즉시 축약 attention profiler
│   └── eval/
│       ├── yesno.py              # Yes/No 토큰 id 확정 + logit 판정
│       ├── loop.py               # 체크포인트 가능한 평가 루프
│       ├── metrics.py            # Accuracy/Flip/Recovery/Damage/McNemar
│       └── flops.py              # 이론 FLOPs 절감 계산
├── scripts/                      # C-5 단계와 1:1 매핑
│   ├── 00_smoke_test.py          # (§9) 5문항 dry-run — 본 실험 전 필수
│   ├── 01_prepare_data.py        # C-5 단계 1: 환경·데이터 준비, pairs.csv
│   ├── 02_sanity_checks.py       # C-5 단계 2: mask 검증 + sanity 3종 (C-4)
│   ├── 03_run_main.py            # C-5 단계 3: 10조건 × 600문항 → results.csv
│   ├── 04_run_attention_profile.py  # C-5 단계 4: M 조건 attention 재실행
│   └── 05_analyze.py             # C-5 단계 5: 지표·그림·REPORT.md
├── pbs/                          # §7.1 및 05_pbs_execution_plan.md 참조
├── data/                         # gitignore. pope/, coco/annotations/, coco/images/
├── results/                      # pairs.csv, raw_results.jsonl, results.csv,
│                                 # token_ids.json, attn_profile.npz, fig1·fig2, REPORT.md
└── logs/                         # stage_times.jsonl, env_*.json, sanity_*, BLOCKED.md
```

### 모듈별 책임과 핵심 시그니처

**`config.py`** — 하드코딩 금지, 전 스크립트가 이것만 import.

```python
SEED = 42
MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
L_GRID = [4, 8, 12, 16, 20, 24]
L_GRID_FALLBACK = [2, 4, 6, 8, 10, 12]   # PART D ② 실패 대응 전용 (1회만, 실행 여부 REPORT 기록)
CONDITIONS = ["S", "M", "T4", "T8", "T12", "T16", "T20", "T24", "T0", "Trel8"]  # 10개
N_PER_CELL = 150
PAIRING_OVERGEN = 160                     # 다운로드 실패 대비 여분 — 셀당 160 생성 후 상위 150 사용
CELL_SPEC = {1: ("no", True), 2: ("yes", False), 3: ("no", False), 4: ("yes", True)}
#            cell: (gt_label, distractor_contains_object)
MASK_SPAN_MODE = ...   # [03 §A-3 확정값] "pad_only" | "with_delimiters" (권장)
ARTICLE_MODE = ...     # [03 §A-6 확정값] "fixed_a" | "preserve_pope" (권장)
PROMPT_MULTI  = "In the first image, is there {obj_phrase}? Answer with Yes or No."
PROMPT_SINGLE = "In the image, is there {obj_phrase}? Answer with Yes or No."
PROMPT_MULTI_FALLBACK = ...   # sanity 2 실패 시에만: "Picture 1: <image>\nPicture 2: <image>" 라벨형
COCO_IMG_URL = "http://images.cocodataset.org/val2014/COCO_val2014_{id:012d}.jpg"
POPE_URL = "https://raw.githubusercontent.com/RUCAIBox/POPE/main/output/coco/coco_pope_adversarial.json"
POPE_URL_POPULAR = ...        # 부족 시 보충용
COCO_ANN_ZIP = "http://images.cocodataset.org/annotations/annotations_trainval2014.zip"  # ~241MB, 허용
```

**`data/pope.py`**
```python
def load_pope(path: Path) -> list[PopeQ]          # jsonl 형식 (한 줄당 {"question_id","image","text","label"})
def parse_object(text: str) -> tuple[str, str]    # "Is there an orange in the image?" → ("an", "orange")
def image_id_from_filename(name: str) -> int      # "COCO_val2014_000000131089.jpg" → 131089
```

**`data/coco_index.py`**
```python
def build_indices(instances_path: Path) -> CocoIndex
# CocoIndex:
#   .name2cat: dict[str, int]              # category name → category_id (POPE 객체명과 exact match 검증)
#   .cat2super: dict[int, str]             # category_id → supercategory
#   .img2cats: dict[int, set[int]]         # image_id → 등장 category_id 집합 (iscrowd 처리 규칙은 상수로 고정·기록)
#   .super2imgs: dict[str, list[int]]      # supercategory → 해당 supercategory 카테고리를 1개 이상 포함한 image_id
```

**`data/pairing.py`** — §2.2 의사코드 구현. `def build_pairs(pope, idx, seed=42) -> pd.DataFrame`

**`model/load.py`**
```python
def load_model_and_processor(max_pixels: int | None = None): ...
def resolve_decoder_layers(model) -> list[nn.Module]   # §4.1 — text decoder만, vision block 제외
```

**`model/inputs.py`**
```python
def build_inputs(processor, images: list[Path], question: str, device) -> BatchFeature
def find_vision_spans(input_ids: Tensor, tok) -> list[tuple[int, int]]  # 경계 = MASK_SPAN_MODE 따름, inclusive
```

**`model/masking.py`** — §4의 `KVBlockController` / **`model/profiler.py`** — §6의 `AttentionProfiler`

**`eval/yesno.py`**
```python
def resolve_yes_no_ids(model, processor, sample_items) -> tuple[list[int], list[int]]  # §5
def predict(last_logits: Tensor, yes_ids, no_ids) -> dict  # {"pred","logit_yes","logit_no"}
```

**`eval/loop.py`** — §7.2 체크포인트 루프. **`eval/metrics.py`, `eval/flops.py`** — §7.6 지표.

**`runlog.py`**
```python
@contextmanager
def stage(name: str): ...                 # logs/stage_times.jsonl에 start/end ISO 시각 append
def blocked(stage: str, reason: str, detail: dict) -> NoReturn   # §7.4, exit code 86
def dump_env(stage: str): ...             # §7.5 버전·GPU·git rev 기록
```

## 2. 데이터 파이프라인 (`scripts/01_prepare_data.py`)

### 2.1 소스 파일과 스키마

- **`coco_pope_adversarial.json`**: POPE 공식 repo, **줄 단위 JSON**(jsonl — `json.load` 단일 배열 아님 주의). 필드:
  `{"question_id": int, "image": "COCO_val2014_%012d.jpg", "text": "Is there a {object} in the image?", "label": "yes"|"no"}` (label 소문자)
  로드 후 assert: label ∈ {yes,no}, `parse_object` 성공률 100% (실패 문항은 제외 후 로그), 객체명이 `name2cat`에 존재 (80 category exact-match 사전 사용, 다단어 객체 "dining table" 등 주의). 셀당 확보 부족 시 **popular split로 보충**하고 pairs.csv의 `pope_split` 컬럼에 출처 기록 (C-2 허용 사항).
- **`instances_val2014.json`**: `annotations_trainval2014.zip`(~241MB — 이미지 zip이 아니므로 다운로드 허용)에서 해당 파일만 추출. `build_indices`로 인덱스 3종 구성. category→supercategory 매핑은 `categories` 리스트의 `{"id","name","supercategory"}`에서 직접.

### 2.2 4셀 페어링 의사코드 (seed 42)

```
rng = random.Random(42)                        # 페어링 전용 RNG (다른 용도와 공유 금지)
questions = load_pope(adversarial); rng.shuffle(questions)
quota = {1:160, 2:160, 3:160, 4:160}           # PAIRING_OVERGEN — 다운로드 실패 대비 여분,
pairs = []                                     # 최종 사용은 셀당 상위 150 (§2.4)

for q in questions:
    if all(v == 0 for v in quota.values()): break
    c   = idx.name2cat[q.object]; sc = idx.cat2super[c]
    # gt에 따라 지원 가능한 셀: no → {1,3}, yes → {2,4}. quota 남은 쪽 우선(큰 쪽), 동률 시 셀 번호 낮은 쪽
    for cell in candidate_cells_sorted_by_quota(q.label):
        contains = CELL_SPEC[cell][1]
        pool = [i for i in idx.super2imgs[sc]              # [03 §A-4 확정 규칙 적용 지점]
                if i != q.image1_id                        # 동일 이미지 금지
                and ((c in idx.img2cats[i]) == contains)]  # 셀 조건을 annotation으로 검증
        if pool:
            pairs.append(row(q, cell, distractor=rng.choice(pool))); quota[cell] -= 1; break
        # pool 비면 다음 후보 셀 시도 — 예: supercategory "person"은 카테고리가 person뿐이라
        # '동일 supercategory + 객체 미포함' 셀(2·3) 충족 불가 → 해당 질문은 셀 1/4로만 배정 가능
if any(quota.values()): popular split로 동일 로직 보충; 그래도 부족하면 blocked("pairing", ...)
검증 pass: 각 row에 대해 (c in img2cats[image2_id]) == CELL_SPEC[cell][1] 재확인, image1≠image2 재확인
로그: 셀별 distractor 통계 (포함 객체 수, supercategory 분포) — 03 §A-4
```

### 2.3 `pairs.csv` 스키마

| 컬럼 | 내용 |
|---|---|
| `question_id` | POPE 원본 id (popular 보충분은 `p{id}`로 충돌 방지) |
| `cell` | 1–4 |
| `gt` | yes/no (이미지1 기준 POPE 정답) |
| `object`, `article`, `category_id`, `supercategory` | 판정 대상 객체 (관사는 A-6 확정값 기준) |
| `image1_id`, `image1_file`, `image2_id`, `image2_file` | 원본/distractor |
| `question_multi`, `question_single` | 실제 사용 프롬프트 문자열 (템플릿 적용 결과 그대로 저장 — 템플릿 fallback 채택 시 재생성, §8.2) |
| `pope_split` | adversarial / popular |

### 2.4 이미지 개별 다운로드

- 대상: pairs.csv의 image1·image2 유니크 집합 (≤ 1,300장, ~200–300MB). **val2014 전체 zip 금지** (C-2).
- URL: `http://images.cocodataset.org/val2014/COCO_val2014_{id:012d}.jpg` (zero-pad 12자리).
- `ThreadPoolExecutor(8)`, 파일별: 임시 `.part`로 stream 저장 → 완료 시 atomic rename. 재시도 3회, backoff 2/4/8s.
- 무결성: (a) 파일 크기 > 1KB, (b) `PIL.Image.open(f).verify()` 후 재-open하여 `convert("RGB")` 성공. 실패 시 삭제 후 재시도, 3회 소진 시 해당 문항을 제외 목록에 넣고 로그 — 셀당 160 여분에서 보충해 최종 150 확정.
- 재시작 가능: 이미 존재+무결성 통과 파일은 skip.
- 네트워크 경로: 로컬(맥)에서 01 실행 → 연구실 네트워크에서 `rsync -av data/ isangmin@10.20.23.30:...` (06 문서 §5). 서버에서 재실행해도 skip 로직으로 무해.

## 3. 모델 파이프라인

### 3.1 로딩 (`model/load.py`)

```python
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    MODEL_ID, torch_dtype=torch.bfloat16,   # 핀 버전에 따라 인자명 dtype일 수 있음 (torch_dtype는 deprecated 방향)
    attn_implementation="eager",            # C-1 필수: 4D mask 주입 + attn 추출
    device_map="cuda:0")
model.eval(); torch.set_grad_enabled(False)
processor = AutoProcessor.from_pretrained(MODEL_ID)   # 해상도 기본값 유지 (임의 축소 금지)
# eager 확인·N 확인 — config 경로는 버전 의존이므로 fallback 접근 (03 §B-4)
cfg = getattr(model.config, "text_config", model.config)
N = cfg.num_hidden_layers          # 36 예상 — 실측값 로그·REPORT 기록
```

- OOM 시에만 `AutoProcessor.from_pretrained(MODEL_ID, max_pixels=...)` 재로드 허용, 값과 사유를 `logs/env_*.json`과 REPORT에 기록 (C-1).
- special token id는 **예상값(151652/151653/151655) 하드코딩 금지, 반드시 `tok.convert_tokens_to_ids`로 조회** 후 로그.

### 3.2 입력 구성 (`model/inputs.py`)

```python
def build_inputs(processor, images, question, device):
    content = [{"type": "image", "image": str(p)} for p in images] + [{"type": "text", "text": question}]
    messages = [{"role": "user", "content": content}]      # system은 chat template 기본값 유지
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, _ = qwen_vl_utils.process_vision_info(messages)
    return processor(text=[text], images=image_inputs, return_tensors="pt").to(device)
```

- `add_generation_prompt=True` → 시퀀스가 `<|im_start|>assistant\n`으로 끝나며, **마지막 위치(-1)의 next-token logits가 답변 첫 토큰 예측**이 된다 (batch 1 + padding 없음이므로 인덱스 산술 불필요). 이 위치 결정 로직은 단일 함수로 두고 평가(§5)와 프로파일링(§6)이 공유한다 (03 §B-3).

### 3.3 이미지별 토큰 구간 특정

```python
def find_vision_spans(input_ids, tok):
    ids = input_ids[0].tolist()
    starts = [i for i, t in enumerate(ids) if t == VS_ID]   # <|vision_start|>
    ends   = [i for i, t in enumerate(ids) if t == VE_ID]   # <|vision_end|>
    assert len(starts) == len(ends) and all(s < e for s, e in zip(starts, ends))
    if MASK_SPAN_MODE == "with_delimiters":                 # 03 §A-3 권장
        spans = [(s, e) for s, e in zip(starts, ends)]      # delimiter 포함, inclusive
    else:                                                   # "pad_only"
        spans = [(s + 1, e - 1) for s, e in zip(starts, ends)]
        for (s, e) in spans:
            assert all(t == IMG_PAD_ID for t in ids[s:e + 1])   # 구간 전체가 image_pad인지 검증
    return spans
```

- M/T layout: `len(spans) == 2`, `spans[0]`=이미지1, `spans[1]`=이미지2. S layout: `len(spans) == 1`.
- **C-3 요구 로깅**: 매 문항 raw_results 행에 `img1_span`, `img2_span`, `seq_len` 기록. 최초 3개 샘플은 `logs/span_check.md`에 `tok.decode`로 [span 앞 5토큰 | 구간 요약 | span 뒤 5토큰]을 수동 확인 가능한 형태로 출력. fallback 라벨 텍스트("Picture 1:")가 마스킹 구간에 포함되지 않음도 여기서 확인.
- **S와의 layout 차이**: S는 이미지2 블록 자체가 없어 텍스트 토큰들의 절대 position이 다르다. T(0)는 이미지2를 참조 차단할 뿐 position은 남는다 → B-2가 명시한 "완전 일치하지 않는 허용 오차"의 원인. **고치지 않는다** (sanity 1의 ≥90% 기준으로만 확인).

## 4. KV 차단 구현 (`model/masking.py`)

**원리 (C-3)**: 실제 KV 계산 생략 없이, `idx ≥ L`인 decoder layer에서 4D additive attention mask의 distractor key 열에 `torch.finfo(dtype).min`을 더한다. softmax 분모에서 제외되므로 해당 KV는 수학적으로 부재와 동일하다. position id·M-RoPE는 불변 — **model.forward에 4D mask를 직접 넘기는 구현은 금지** (`get_rope_index()`가 2D mask를 기대해 M-RoPE가 깨진다, 03 §B-5).

### 4.1 공통 준비 — layer index를 정확히 세는 법

```python
def resolve_decoder_layers(model):
    for path in ("model.language_model.layers", "model.layers"):   # transformers 버전별 경로
        try:
            layers = operator.attrgetter(path)(model)
            break
        except AttributeError:
            continue
    else:
        blocked("mask", "decoder layers 경로 미발견", {"model_cls": type(model).__name__})
    assert len(layers) == N                                         # vision block 미포함 확인
    for i, ly in enumerate(layers):
        assert getattr(ly.self_attn, "layer_idx", i) == i           # HF 자체 layer_idx와 대조
    return list(layers)
```

추가 검증(스모크 시 1회): 각 layer에 순번 기록용 임시 hook을 걸고 1 forward → 호출 순서가 `0..N−1`과 일치하는지 assert. 이로써 "enumerate 순서 = 실행 순서 = HF layer_idx" 삼중 일치를 확인한다.

### 4.2 방식 A (주 구현): decoder layer `forward_pre_hook`

```python
class KVBlockController:
    def __init__(self, model):
        self.layers = resolve_decoder_layers(model)
        self.block_from: int | None = None      # None이면 비활성 (S·M 조건)
        self.cols: tuple[int, int] | None = None
        self.fired = Counter()                  # layer별 발화 카운터 (no-op 탐지, 03 §B-1)
        self.handles = [ly.register_forward_pre_hook(self._make(i), with_kwargs=True)
                        for i, ly in enumerate(self.layers)]

    def configure(self, block_from, cols): self.block_from, self.cols = block_from, cols
    def disable(self): self.block_from = None
    def remove(self): [h.remove() for h in self.handles]

    def _make(self, idx):
        def hook(module, args, kwargs):
            if self.block_from is None or idx < self.block_from:
                return None                      # 무개입
            mask = kwargs.get("attention_mask")
            if mask is None:
                # 버전에 따라 mask가 positional로 올 수 있음 — args에서 4D tensor 탐색 후에만 BLOCKED (검증자 지적)
                mask, pos = find_4d_mask_in_args(args)
                if mask is None:
                    blocked("mask", "4D attention_mask 미발견 (kwargs·args 모두)", {"layer": idx})
            assert mask.dim() == 4               # (B, 1, q_len, kv_len) additive
            m = mask.clone()                     # 주의: 원본 tensor는 전 layer가 공유 — in-place 금지
            s, e = self.cols
            m[:, :, :, s:e + 1] = torch.finfo(m.dtype).min
            self.fired[idx] += 1
            return replace_mask(args, kwargs, m) # kwargs 또는 발견된 positional 위치에 재주입
        return hook
```

조건 매핑: `M`→`disable()` / `T(L)`→`configure(L, img2_span)` / `T(0)`→`configure(0, img2_span)` / `Trel8`→`configure(8, img1_span)`.

- **장점**: transformers 내부 코드 무수정, install/remove가 명시적, 조건 전환이 상태 변수 하나, layer 단위 granularity가 자연스러움.
- **단점**: mask 전달 경로(kwarg명·positional)가 버전 의존 → 위 탐색·카운터로 즉시 탐지. hook 다중 등록 시(profiler와 공존) 순서 관리 필요. layer마다 clone 비용(수 MB, 무시 가능).
- 매 실행 종료 시 `fired` 카운터가 기대치(차단 대상 layer 수 × forward 수)와 일치하는지 assert — **무음 no-op 방지의 1차 방어선** (03 §B-1).

### 4.3 방식 B (예비): attention forward monkey-patch

`self.layer_idx`가 모듈 자체 속성이라 layer 세기 오류가 원천 불가능하다는 장점이 있으나, **attention forward의 signature가 버전에 따라 다르다** — 최신 리팩토링에서는 `(self, hidden_states, position_embeddings, attention_mask, ...)`로 position_embeddings가 mask보다 앞서고, 클래스명 자체도 버전 의존이다 (검증자 지적: 구식 signature 가정으로 positional 호출 시 오바인딩되어 조용히 오동작). **서버 핀 버전의 실제 소스 signature를 확인한 후에만 작성한다.**

- **선택**: A를 주 구현으로 확정. B는 A가 핀 버전에서 mask를 못 받을 때의 예비로만 유지. 스모크의 A·B 교차 검증(동일 3샘플, T(8) logits 일치)은 **advisory** — B가 동작하지 않으면 B를 폐기하고 A 단독 진행 + 로그 (검증자 지적: 예비 구현의 실패로 주 구현까지 BLOCKED시키지 않는다).

### 4.4 차단 검증 3종 (스모크·sanity 단계에서 자동 실행)

1. **동등성**: `T(N)` (block_from=N, 아무 layer도 차단 안 됨) logits == M logits, `torch.equal` 수준 일치. hook 자체의 부작용 부재 증명.
2. **직접 관측**: 1개 샘플을 `output_attentions=True`로 T(8) 실행 → `idx ≥ 8`의 attention에서 distractor 열 질량 합 == 0 (정확히 0, softmax 이후), `idx < 8`에서는 > 0. layer counting과 차단 방향의 결정적 증거.
3. **행동 검증**: sanity 1 (T(0) vs S 일치율, §8) + **셀 1에서 T(0) vs M 불일치 건수 > 0 확인** (전부 일치하면 no-op 의심 — 03 §B-1).

## 5. 평가: logit 기반 Yes/No (`eval/yesno.py`)

### 5.1 대표 토큰 id 집합 확정 절차 (본 실험 전, 스모크에서 1회)

1. seed-42로 셀당 2문항(총 8) 추출, S·M layout 각각 `model.generate(max_new_tokens=5, do_sample=False)` 실행.
2. 생성 첫 토큰 id와 `tok.decode` 문자열을 `logs/yesno_probe.jsonl`에 기록.
3. `YES_IDS` = {관측된 첫 토큰 중 `decode(t).strip().lower() == "yes"`인 id} ∪ {`tok.encode(s, add_special_tokens=False)`가 단일 토큰인 s ∈ {"Yes", " Yes", "yes", " yes", "YES"}}. `NO_IDS`도 동형으로.
4. assert: 두 집합 비어있지 않음, 교집합 없음. `results/token_ids.json`으로 동결하고 REPORT에 기록 (B-3). 이후 모든 단계는 이 파일만 읽는다. **템플릿 fallback 채택 시 재확인** (§8.2).

### 5.2 판정 규칙

```python
def predict(last_logits, yes_ids, no_ids):        # last_logits = logits[0, -1, :].float()
    ly = last_logits[yes_ids].max().item()
    ln = last_logits[no_ids].max().item()
    return {"pred": "yes" if ly > ln else "no",   # 동률은 "no" (사전 규정), 발생 시 카운트·REPORT 기록
            "logit_yes": ly, "logit_no": ln}
```

Generation loop 없음. forward는 `model(**inputs, use_cache=False)` — cache 미사용으로 메모리 절약.

## 6. Attention 프로파일링 (`model/profiler.py`, `scripts/04_run_attention_profile.py`)

M 조건을 **mask 비활성** 상태로 600문항 재실행 (`output_attentions=True`). 메모리를 위해 full attention tensor를 모으지 않고 **per-layer 즉시 축약 후 폐기**한다.

```python
class AttentionProfiler:
    def __init__(self, model):
        self.layers = resolve_decoder_layers(model)
        self.spans = None                       # 문항마다 set_spans((s1,e1),(s2,e2))
        self.buf = {}                           # idx -> (m1, m2, mtext)
        self.handles = [ly.self_attn.register_forward_hook(self._make(i)) for i, ly in enumerate(self.layers)]

    def _make(self, idx):
        def hook(module, inputs, output):
            attn_w = output[1]                  # (B, heads, q_len, kv_len); output_attentions=True 필요
            w = attn_w[0, :, -1, :].float()     # 마지막 프롬프트 토큰의 row만 (heads, kv_len)
            (s1, e1), (s2, e2) = self.spans
            m1 = w[:, s1:e1 + 1].sum(-1).mean().item()   # head 평균의 이미지1 질량
            m2 = w[:, s2:e2 + 1].sum(-1).mean().item()
            mt = w.sum(-1).mean().item() - m1 - m2       # 텍스트(비이미지) = 전체 − 두 이미지
            self.buf[idx] = (m1, m2, mt)
            return (output[0], None) + tuple(output[2:]) # attn_weights를 None으로 치환해 all_attentions 누적 차단
        return hook                                      # ※ 반환 tuple 구조(2/3원소)는 버전 의존 — 스모크에서 실측 확인
```

- 검증: 각 layer에서 `m1+m2+mt ≈ 1.0` (오차 1e-3; causal이므로 마지막 row는 전 구간 합 1) — 위반 시 span 오류 또는 pre-softmax 텐서 오포착으로 간주하고 중단.
- 저장: 문항당 `{"question_id", "mass": [[m1,m2,mt] × N layers]}`를 `results/attn_profile.jsonl`에 append(체크포인트 가능) → 완료 후 `attn_profile.npz`로 변환 (**jsonl append가 원본, npz는 최종 변환본** — np.savez는 append 불가).
- 산출 (05 스크립트):
  - `fig2_attention_profile.png`: x=layer(1..N), y=이미지1/이미지2 질량 평균 곡선. **그룹 분리**: (a) M 정답 케이스, (b) flip 케이스 — **그룹 라벨의 단일 소스는 stage 3의 results.csv** (03 §B-12). stage 4 재예측과의 일치율을 로그, 불일치 ≠ 0이면 REPORT 이상 징후에 기재.
  - **③ 식별률**: `mean(mass[:, idx, 0] > mass[:, idx, 1])`을 `idx ∈ {3, 7}`(= layer 4, 8)에서 계산. 분모는 M 600문항 전체. **판정 기준은 layer 8의 ≥ 80%만** (layer 4는 측정·보고만 — PART D 원문).
- fallback(메모리 이상 시): hook 치환 실패 버전이면 `output_attentions=True` 표준 경로로 받되 forward 직후 즉시 축약·`del`·`empty_cache()` (스모크에서 peak VRAM 실측 후 판단).

## 7. 실행 인프라

### 7.1 PBS job 설계 (요약 — 상세·제출 절차는 05_pbs_execution_plan.md)

- **1-GPU job으로만 제출** (본 파이프라인은 순차 루프 — 정책 7 "병렬화 불가 시 1 GPU"). 시간 단축은 pairs를 반으로 나눈 1-GPU job 2개(`--shard k/2`, 3090×2 = token 2.0 ≤ 2.5)로.
- **노드 고정(host/queue) 문법 확정 전 GPU job 제출 금지** — 미고정 제출 시 스케줄러가 Node 4에 2개를 배치하면 A6000×2 = 3.0 > 2.5 정책 위반이 실행 시점에 발생한다 (검증자 지적).
- 폴백: Node 4는 `ncpus≤6`(권장 4, job명 `1_4_...`), Node 1은 `ncpus≤4` (job명 `1_4_...`) — 노드별 CPU 제한 상이 주의.
- GPU 부재/미할당 시: `torch.cuda.is_available()` False → 즉시 `blocked("env", "GPU 없음")` (CPU 실행 시도 금지, C-1).

### 7.2 재시작 가능한 체크포인트 루프 (`eval/loop.py`)

```python
def run_eval(pairs, conds, model, ctrl, out_path):
    done = {(r["question_id"], r["condition"]) for r in read_jsonl(out_path)}   # 재시작 시 복원
    for item in pairs.itertuples():
        need_S = ("S" in conds) and ((item.question_id, "S") not in done)
        need_M = any((item.question_id, c) not in done for c in conds if c != "S")
        if need_S: in_S = build_inputs(processor, [item.image1], item.question_single, dev)
        if need_M:
            in_M = build_inputs(processor, [item.image1, item.image2], item.question_multi, dev)
            sp1, sp2 = find_vision_spans(in_M["input_ids"], tok)
        for cond in conds:
            if (item.question_id, cond) in done: continue
            t0 = time.time()
            if cond == "S":      ctrl.disable(); inputs = in_S
            elif cond == "M":    ctrl.disable(); inputs = in_M
            elif cond == "T0":   ctrl.configure(0, sp2); inputs = in_M
            elif cond == "Trel8": ctrl.configure(8, sp1); inputs = in_M
            else:                ctrl.configure(int(cond[1:]), sp2); inputs = in_M   # T4..T24
            out = model(**inputs, use_cache=False)
            p = predict(out.logits[0, -1].float(), YES_IDS, NO_IDS)
            row = {"question_id": item.question_id, "cell": item.cell, "gt": item.gt,
                   "condition": cond, **p, "correct": p["pred"] == item.gt,
                   "seq_len": inputs["input_ids"].shape[1],
                   "img1_span": list(sp1) if cond != "S" else None,
                   "img2_span": list(sp2) if cond != "S" else None,
                   "elapsed_ms": int(1000 * (time.time() - t0)), "ts": iso_now()}
            append_jsonl(out_path, row)          # 문항×조건 단위 즉시 append + flush + os.fsync
```

- 산출: `results/raw_results.jsonl` (진실의 원본) → 03 종료 시 `results.csv`(long format, `correct` 컬럼 포함)로 집계, `assert 행수 == 600 × 10`.
- 하나의 M layout 입력을 M/T×6/T(0)/Trel8 9조건이 공유 — processor 호출은 문항당 2회 (문항-major 루프).

### 7.3 단계 시각 로깅

모든 스크립트 본문을 `with stage("03_main"):`로 감싼다. `logs/stage_times.jsonl`에 `{"stage","event":"start|end|BLOCKED","ts","host","pbs_job_id"}` append. 05 스크립트가 이를 읽어 REPORT "소요 시간" 표를 생성. C-5 상한(1.5배) 초과 여부도 여기서 판정해 경고를 남긴다.

### 7.4 BLOCKED 프로토콜

- `blocked(stage, reason, detail)`: `logs/BLOCKED.md`에 [시각 / 단계 / 사유 / 상태 스냅샷(마지막 처리 문항, 진행률) / 재현 커맨드] append → `stage_times`에 BLOCKED 이벤트 → `sys.exit(86)`.
- 발동 지점 (대안 실행 금지): GPU 부재 / decoder layer 경로 미발견 / 4D mask 미발견(kwargs·args 모두) / span 검증 실패 / Yes·No 토큰 집합 확정 실패 / sanity 미통과(§8) / 페어링 셀 미달(보충 후에도) / 질량 합 ≠ 1.
- REPORT의 "BLOCKED 목록"은 이 파일을 그대로 옮긴다 (없으면 "없음").

### 7.5 Seed 42 고정 지점 / 버전 기록

| # | 지점 |
|---|---|
| 1 | `random.Random(42)` — 페어링 셔플·distractor 추출 (전용 인스턴스) |
| 2 | `random.Random(42)` — sanity 1·2·3 및 토큰 probe의 부분표본 추출 (각각 독립 인스턴스, 추출 문항 id를 로그로 저장) |
| 3 | 각 스크립트 시작부: `torch.manual_seed(42)`, `torch.cuda.manual_seed_all(42)`, `np.random.seed(42)` |
| 4 | PBS 스크립트: `export PYTHONHASHSEED=42` |
| 5 | 생성은 전부 `do_sample=False` (greedy — seed 무관함을 명시) |

버전 기록: 각 스크립트 시작 시 `dump_env()` → `logs/env_{stage}.json`에 {python, torch, transformers, qwen-vl-utils 등 버전, CUDA/driver, git rev, 실행 커맨드}. 최초 1회 `pip freeze > logs/pip_freeze.txt`. **requirements.txt는 서버 설치 시점의 실제 버전으로 exact pin 고정, 로컬 검증 환경도 동일 버전으로 맞춘다** (03 §B-4).

### 7.6 지표·통계 (05 스크립트, B-4·PART D 그대로 + 03 §A 확정 정의 적용)

- **Accuracy**: 조건 × 셀별 `mean(correct)`.
- **Flip Rate**(조건 M, 셀별): [03 §A-2 확정 정의] — 주 정의: 셀 1·3 `#(pred_S=no ∧ pred_M=yes)/150`, 셀 2·4 `#(pred_S=yes ∧ pred_M=no)/150`. `pred_S` 조건부 버전도 참고 병기, 양방향 raw 카운트 저장.
- **Recovery(L)** = `#(M오답 ∧ T(L)정답)/#(M오답)`, **Damage(L)** = `#(M정답 ∧ T(L)오답)/#(M정답)` (셀별).
- **McNemar**: `statsmodels ... mcnemar([[n_bb, n_bg], [n_gb, n_gg]], exact=True)` (정오 기준 2×2, exact binomial). T(L) vs M, T(0) vs M은 셀별 p값, **Trel8 vs M은 600문항 pooled p값도 별도 산출** (판정 ②″용 — 검증자 지적 반영). 전부 discordant pair (b,c)와 함께 표 1에 병기.
- **이론 FLOPs 절감**: `Σ_items n_img2_masked_tokens × (N − L) / Σ_items (seq_len × N)` — 브리프의 (32−L)/32를 실측 N(=36 예상)으로 일반화 [03 §A-1], 실측 latency는 측정하지 않으며 그 이유(mask 등가 구현)를 REPORT에 명시.
- **판정표 (PART D 5개, 사전 등록 그대로)**: ① [A-2 확정식 — 셀 2 동형 패턴 포함 3요건] / ② ∃L: 셀 1·2 모두 `Acc_T(L) − Acc_M ≥ 0.5 × (Acc_T(0) − Acc_M)` ∧ McNemar p < 0.05 [분모 경계는 A-5 규칙] / ②′ 그 L에서 Recovery > Damage / ②″ Trel8: 600문항 전체 Acc 하락 ∧ pooled p < 0.05 / ③ **layer 8** 식별률 ≥ 80%. 실패 시 대응은 PART D 순서로만 각 1회 (`L_GRID_FALLBACK`·distractor 교체/2장 확장 스크립트 인자로 사전 준비), 실행 여부를 REPORT에 기록.
- **REPORT.md 구조 (PART E 고정 — 누락 금지)**: 실행 환경(GPU·소요 시간·확정 토큰 id) / Sanity 3종 결과 / 판정표(5개 기준 PASS·FAIL·근거 수치) / 표 1 / 이론 FLOPs 절감률(최적 L 기준) / **한 줄 결론** / 이상 징후·한계·BLOCKED 목록 — **한계에 브리프 PART F의 3개 미검증 항목(관계 질문 보존, 실측 latency, 비-oracle 컨트롤러) + 03 §C 항목 명시** / **"제안" 섹션** (개선 아이디어 기록 전용, 실행 금지).

## 8. Sanity check 3종 (`scripts/02_sanity_checks.py`, C-4 — 미통과 시 본 실험 진입 금지)

실행 전 §4.4의 mask 검증 1·2를 먼저 통과해야 한다. 세 검사 결과는 `logs/sanity_summary.json`에 저장하고, 전부 통과 시 `results/SANITY_PASSED` flag 파일 생성 — `03_run_main.py`는 이 파일 없으면 즉시 종료.

### 8.1 Sanity 1 — T(0) vs S 일치율

```
sample = 셀3에서 30 + 셀4에서 30 (random.Random(42)로 추출, 문항 id 로그)
각 문항: pred_S (단독 layout), pred_T0 (2이미지 layout + block_from=0, cols=img2_span)
agree = mean(pred_S == pred_T0)
if agree >= 0.90: PASS
elif agree < 0.70: blocked("sanity1", "mask 구현 버그 의심", {"agree": agree})   # 디버그 후 재실행
else:              blocked("sanity1", "0.70~0.90 — layout 차이 초과, 원인 조사 필요", {...})
```
(0.70–0.90 구간도 진입 금지이므로 BLOCKED 처리하되 사유 메시지를 구분.) 불일치 문항 목록을 로그로 남겨 버그 vs layout 노이즈를 구분 (03 §B-1). 결과 행은 raw_results.jsonl에 append되어 본 실험에서 재사용.

### 8.2 Sanity 2 — "first image" grounding

```
육안 로그 표본 = 셀당 5문항 × 4셀 = 20 (random.Random(42))
각 문항: M layout으로 generate(max_new_tokens=10, do_sample=False)
로그: logs/sanity2_grounding.md — 문항별 [셀 / 질문 / img1·img2 객체 유무 / 생성문 전문] → 육안 확인 (브리프 요구)

자동 게이트 (브리프 외 보조 장치 — 판정은 셀 3·4 문항 10개만 사용):
  ※ 검증자 지적: 셀 1·2의 오답은 바로 이 연구가 측정하려는 leakage일 수 있어
    게이트에 포함하면 grounding이 정상인데도 fallback으로 오전환된다.
acc_34 = 셀 3·4 표본의 이미지1 기준 정답률
if acc_34 >= 0.60: PASS (사용 템플릿 = PROMPT_MULTI로 확정)
else: PROMPT_MULTI_FALLBACK으로 동일 20문항 재시도
      if acc_34_fb >= 0.60: PASS + fallback 채택
      else: blocked("sanity2", "first-image grounding 실패", {...})

fallback 채택 시 후속 처리 (검증자 지적 — 누락 시 결과 일관성 붕괴):
  1) pairs.csv의 question_multi 컬럼 재생성 (실제 사용 프롬프트 문자열 일치 유지)
  2) sanity 1 재실행 (기존 T(0)·S 행 무효 — raw_results에서 template 태그로 구분)
  3) Yes/No 토큰 probe 재확인 (token_ids.json 재생성)
  4) sanity 3 재실행. 최종 채택 템플릿의 렌더링 전문을 REPORT에 기록
```

### 8.3 Sanity 3 — S 정답률

```
sample = 셀당 50 × 4 = 200 (random.Random(42))
S 조건 logit 평가 → acc_S
if acc_S >= 0.60: PASS (원본 POPE 3B급 보고치 ~80%대와의 격차를 로그·REPORT에 수치로 기록)
else: blocked("sanity3", "평가 파이프라인 버그 의심 (acc_S < 0.60)", {"acc": acc_S})
```
결과는 raw_results.jsonl에 append — 본 실험 S 600문항 중 200문항이 완료된 상태로 시작.

## 9. 서버 스모크 테스트 (`scripts/00_smoke_test.py`, PBS `1_8_isangmin_sd_smoke`, walltime 00:30)

본 실험·sanity job 제출 전에 **5문항 (셀 1·2·3·4 각 1 + 셀 1 추가 1, seed 42 고정 추출)** 으로 전체 경로를 1회 관통한다. 전제: 모델·데이터는 로그인 노드에서 선다운로드 완료 (job은 offline — 05 문서 §6).

| 순서 | 검증 내용 | 통과 기준 |
|---|---|---|
| 1 | 환경: `nvidia-smi`, VRAM, 버전 dump | GPU 가시, `dump_env` 성공 |
| 2 | 데이터: pairs.csv 5행 + 이미지 10장 존재·무결성 | PIL open 성공 |
| 3 | 모델 로드 (offline 캐시) | eager 확인, `N` 실측 기록 (36 여부 확인) |
| 4 | span: 5문항 M layout | span 2개, MASK_SPAN_MODE 경계 검증, 첫 3개 수동 확인 출력 |
| 5 | mask 검증 (§4.4-1·2) | T(N)≡M bitwise, idx≥L에서 distractor 질량 0, fired 카운터 일치 |
| 6 | 방식 A vs B 교차 (advisory) | 3샘플 T(8) logits 일치 — B 실패 시 B 폐기·A 단독 진행 + 로그 (BLOCKED 아님) |
| 7 | Yes/No 토큰 probe | 집합 비공, disjoint → token_ids.json 생성 |
| 8 | 10조건 × 5문항 logit 평가 | raw jsonl 50행, NaN 없음, 문항당 elapsed 기록 (→ 본 실험 walltime 실측 보정) |
| 9 | 체크포인트 재시작 | 프로세스 재실행 시 50행 skip 확인 (0 forward) |
| 10 | attention profiler 5문항 | `mass (5, N, 3)`, 질량 합 ≈ 1, attn 반환 tuple 구조 확인, peak VRAM 기록 |
| 11 | 분석 dry-run | 5문항으로 metrics·fig 생성 함수가 예외 없이 동작 |

스모크 통과 후 제출 순서: `sd_sanity` → (SANITY_PASSED 확인 후) `sd_main` → `sd_attn` → 분석. 각 job 로그와 `stage_times.jsonl`로 C-5 시간 상한 준수를 추적한다.
