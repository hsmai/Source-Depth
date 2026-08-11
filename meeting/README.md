# 미팅 자료 작업 규칙 (2026-08-11 사고 후 수립)

## 사고 기록
2026-08-11 22:45, 사용자가 PowerPoint로 직접 편집 중이던
`SourceDepth_Phase0_meeting.pptx`를 생성 스크립트가 **같은 경로에 덮어써서 편집 내용이 소실**됨.
git·스냅샷·자동복구 어디에도 편집본이 없었고, PowerPoint 메모리(열린 창)가 유일한 복구 경로였음.

## 재발 방지 규칙 (반드시 준수)

1. **`meeting/SourceDepth_Phase0_meeting.pptx` = 사용자 소유 파일.**
   자동 생성 스크립트는 절대 이 경로에 쓰지 않는다.
2. 생성 스크립트(`make_deck.js`)의 출력은 **`meeting/_generated/deck_generated.pptx`** 로 고정.
3. 사용자 파일에 반영해야 할 변경이 생기면 **전체 재생성이 아니라 python-pptx 기반 표적 수정**으로
   해당 텍스트/도형만 교체한다 (레이아웃 편집 보존).
4. 사용자 파일을 건드리기 전에는 **항상 타임스탬프 사본을 먼저 만든다**:
   `cp SourceDepth_Phase0_meeting.pptx _generated/backup_$(date +%H%M).pptx`
5. **PowerPoint가 그 파일을 열고 있는지 먼저 확인**한다 (`~$` 잠금 파일 존재 여부 / `pgrep PowerPoint`).
   열려 있으면 파일을 수정하지 말고 사용자에게 먼저 알린다.

## 파일 구성
- `SourceDepth_Phase0_meeting.pptx` — **사용자 편집본 (건드리지 말 것)**
- `make_deck.js` — 생성 스크립트 (출력: `_generated/`)
- `_generated/` — 스크립트 산출물·백업 보관소
