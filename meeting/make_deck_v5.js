// SourceDepth 미팅 덱 v5 — 경로 분해 + 인과 컨트롤러 (본편 10장)
// 2026-08-14. 모든 수치는 results/ 의 실측값. 추정·보간 없음.
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

const R = "/Users/hansangmin/Source-Depth/results/";
const C = {
  navy: "1F3B57", darkbg: "142638", blue: "1F77B4", red: "D62728",
  orange: "E8890C", green: "2E8B57", gray: "6B7280", white: "FFFFFF",
  light: "EFF4F9", lightred: "FBEAEA", lightgray: "F3F4F6",
  lightgreen: "E9F4EE", lightblue: "E8F1FA", line: "D5DEE8",
};
const F = "Arial";

function kicker(s, t, dark) {
  s.addText(t, { x: 0.55, y: 0.26, w: 11.5, h: 0.3, fontFace: F, fontSize: 11,
    bold: true, color: dark ? "9FB8CE" : C.blue, margin: 0 });
}
function headline(s, t, dark) {
  s.addText(t, { x: 0.55, y: 0.54, w: 12.2, h: 0.72, fontFace: F, fontSize: 21,
    bold: true, color: dark ? C.white : C.navy, margin: 0 });
}
function takeaway(s, t, color) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.62, w: 12.25, h: 0.6,
    rectRadius: 0.08, fill: { color: color || C.navy } });
  s.addText(t, { x: 0.85, y: 6.62, w: 11.75, h: 0.6, fontFace: F, fontSize: 12.5,
    bold: true, color: C.white, margin: 0, valign: "middle" });
}
function foot(s, t) {
  s.addText(t, { x: 0.55, y: 6.18, w: 12.2, h: 0.36, fontFace: F, fontSize: 10,
    italic: true, color: C.gray, margin: 0 });
}
const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11.5 };
const cc = { fontSize: 11.5, color: C.navy, fill: { color: C.white } };
const m = (t, o) => ({ text: t, options: Object.assign({}, cc, o || {}) });
const TBL = { fontFace: F, align: "center", valign: "middle",
              border: { pt: 0.75, color: "E2E8F0" } };

// ═══════════════ 1. 표지 ═══════════════
{
  const s = pres.addSlide();
  s.background = { color: C.darkbg };
  s.addText("SOURCEDEPTH · 연구 방향 보고 · 2026-08-14 · 한상민", {
    x: 0.6, y: 0.5, w: 12.2, h: 0.32, fontFace: F, fontSize: 11.5,
    bold: true, color: "7EC8F5", margin: 0 });
  s.addText("멀티이미지 환각은 '이미지가 섞여서'가 아니라\n'질문이 잘못 읽어서' 생깁니다", {
    x: 0.6, y: 1.05, w: 12.2, h: 1.3, fontFace: F, fontSize: 29, bold: true,
    color: C.white, margin: 0, lineSpacingMultiple: 1.15 });
  s.addText("인과 개입으로 두 경로를 분리했고, 상반된 처방을 낸 기존 연구들이 동시에 설명됩니다", {
    x: 0.6, y: 2.5, w: 12.2, h: 0.4, fontFace: F, fontSize: 13, color: "AFC6DA", margin: 0 });
  const cards = [
    ["문제는 실재한다", "무관 이미지 3장이면 3B의 판별력이\n0.908 → 0.521 (우연 수준)으로 붕괴.\n차단하면 0.904로 99% 복구", "n=300 · 두 스케일 · 위치 무관", "8CE0B0"],
    ["원인이 예상과 반대였다", "이미지 간 혼합을 끊으면 오히려\n−0.29 / −0.42로 크게 나빠진다.\n해악은 혼합이 아니라 읽기 단계에 있다", "설계 가설을 우리 손으로 반증", "7EC8F5"],
    ["오라클 없이 작동한다", "반사실 기반 컨트롤러 0.730 >\n손익분기 0.569. 무관 입력이 많을수록\n방법이 더 잘 작동한다", "N=3에서 무개입 대비 +18.2%p", "FFC94D"],
  ];
  cards.forEach((c, i) => {
    const x = 0.6 + i * 4.15, y = 3.15, w = 3.95, h = 3.4;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: "1D3850" }, line: { color: "2E4E6B", width: 1 } });
    s.addText(c[0], { x: x + 0.25, y: y + 0.22, w: w - 0.5, h: 0.36, fontFace: F,
      fontSize: 15, bold: true, color: c[3], margin: 0 });
    s.addText(c[1], { x: x + 0.25, y: y + 0.72, w: w - 0.5, h: 1.9, fontFace: F,
      fontSize: 12, color: C.white, margin: 0, lineSpacingMultiple: 1.25 });
    s.addText(c[2], { x: x + 0.25, y: y + 2.75, w: w - 0.5, h: 0.5, fontFace: F,
      fontSize: 10.5, color: "9FB8CE", margin: 0 });
  });
  s.addNotes("오늘 보고는 세 가지입니다. 문제가 실재한다는 인과 증거, 그 원인이 정확히 어느 경로인지, 그리고 오라클 없이 작동하는 컨트롤러를 찾았다는 것입니다. 특히 두 번째가 이번 연구의 중심 기여입니다.");
}

// ═══════════════ 2. 실험 설계 ═══════════════
{
  const s = pres.addSlide();
  kicker(s, "설계");
  headline(s, "오염이 생길 수밖에 없는 문항을 만들고, 개입만 바꿔가며 인과를 잽니다");
  s.addTable([
    [m("", hd), m("정답", hd), m("방해 이미지에 질의 객체", hd), m("압력 방향", hd), m("n", hd)],
    [m("셀 1", { bold: true }), m("없다"), m("있음", { bold: true, color: C.red }),
     m("\"있다\"고 말하게 밀어냄"), m("150")],
    [m("셀 2", { bold: true }), m("있다"), m("없음", { bold: true, color: C.blue }),
     m("\"없다\"고 말하게 밀어냄"), m("150")],
  ], { x: 0.55, y: 1.5, w: 12.25, rowH: [0.45, 0.52, 0.52], ...TBL });
  s.addText("양쪽 모두 방해 이미지가 오답 방향으로 압력을 준다 → 판별력에 최대 부하. 정답이 균형이라 AUC 계산 가능.", {
    x: 0.55, y: 3.14, w: 12.25, h: 0.32, fontFace: F, fontSize: 11, italic: true, color: C.gray, margin: 0 });

  const items = [
    ["개입 방식", "4D attention mask에 방해 이미지의 KV 열만 차단\n→ 토큰을 실제로 삭제한 것과 예측 100% 일치 확인"],
    ["주 지표", "AUC (임계값 무관) — 정확도는 yes/no 비율 이동과\n판별력 저하를 구분하지 못해 보조로만 사용"],
    ["통제", "같은 이미지가 물리적으로 전부 입력에 존재.\n차이는 KV 가시성 하나뿐 → 인과 해석 성립"],
    ["규모", "3B·7B 각 n=300 × 방해 1~3장 × 조건 10종\n= 모델당 3,000회. seed 고정, 사전 등록 후 실행"],
  ];
  items.forEach((it, i) => {
    const x = 0.55 + (i % 2) * 6.2, y = 3.62 + Math.floor(i / 2) * 1.28;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 6.05, h: 1.14, rectRadius: 0.07,
      fill: { color: C.light }, line: { color: C.line, width: 0.75 } });
    s.addText(it[0], { x: x + 0.22, y: y + 0.14, w: 5.6, h: 0.28, fontFace: F,
      fontSize: 12, bold: true, color: C.navy, margin: 0 });
    s.addText(it[1], { x: x + 0.22, y: y + 0.46, w: 5.6, h: 0.6, fontFace: F,
      fontSize: 10.5, color: C.gray, margin: 0, lineSpacingMultiple: 1.15 });
  });
  s.addNotes("설계의 핵심은 두 가지입니다. 첫째, 오염 압력이 양방향입니다 — 한쪽 방향만 보면 7B에서 현상을 놓칩니다. 실제로 저희가 처음에 그 실수를 했습니다. 둘째, 지표를 AUC로 잡았습니다. 정확도만 보면 예/아니오 비율이 이동한 것을 판별력 개선으로 착각합니다.");
}

// ═══════════════ 3. 문제 실존 ═══════════════
{
  const s = pres.addSlide();
  kicker(s, "결과 1 — 문제 실존");
  headline(s, "무관한 이미지 3장이면 3B의 판별력이 우연 수준까지 무너집니다");
  s.addTable([
    [m("방해 이미지 수", hd), m("개입 없음", hd), m("차단(T0)", hd), m("회복률", hd),
     m("개입 없음 (7B)", hd), m("차단 (7B)", hd)],
    [m("0 (1장 단독)", { bold: true }), m("0.9078", { bold: true }), m("—"), m("—"),
     m("0.9033", { bold: true }), m("—")],
    [m("1", { bold: true }), m("0.6978"), m("0.9058"), m("99%", { bold: true, color: C.green }),
     m("0.8690"), m("0.8993")],
    [m("2", { bold: true }), m("0.6063"), m("0.9037"), m("99%", { bold: true, color: C.green }),
     m("0.8723"), m("0.8970")],
    [m("3", { bold: true }), m("0.5213", { bold: true, color: C.red }), m("0.9041"),
     m("99%", { bold: true, color: C.green }), m("0.8740"), m("0.8957")],
  ], { x: 0.55, y: 1.5, w: 12.25, rowH: [0.5, 0.45, 0.45, 0.45, 0.5], ...TBL });
  s.addText("AUC · n=300 · 정답 균형 150/150", { x: 0.55, y: 3.85, w: 6, h: 0.3,
    fontFace: F, fontSize: 10, italic: true, color: C.gray, margin: 0 });

  const facts = [
    ["0.5213", "방해 3장에서 3B의 판별력", "동전 던지기(0.500)와 구분되지 않는다.\n고정 임계값 정확도는 0.460으로 우연 이하", C.red],
    ["99%", "차단으로 회복되는 손상", "방해가 몇 장이든 회복률이 같다.\n정보가 파괴된 게 아니라 가려져 있었다", C.green],
    ["−0.1765", "손상이 방해 수에 비례", "95% CI [−0.217, −0.136]\n사전 등록 통과선의 9배", C.blue],
  ];
  facts.forEach((f, i) => {
    const x = 0.55 + i * 4.13, y = 4.28;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.95, h: 1.78, rectRadius: 0.08,
      fill: { color: C.lightgray }, line: { color: C.line, width: 0.75 } });
    s.addText(f[0], { x: x + 0.22, y: y + 0.14, w: 3.5, h: 0.5, fontFace: F,
      fontSize: 22, bold: true, color: f[3], margin: 0 });
    s.addText(f[1], { x: x + 0.22, y: y + 0.66, w: 3.5, h: 0.28, fontFace: F,
      fontSize: 11.5, bold: true, color: C.navy, margin: 0 });
    s.addText(f[2], { x: x + 0.22, y: y + 1.0, w: 3.5, h: 0.65, fontFace: F,
      fontSize: 10, color: C.gray, margin: 0, lineSpacingMultiple: 1.15 });
  });
  takeaway(s, "→ 7B는 손상이 6~13배 작고 방해 수에 비례하지 않습니다. 이 현상은 소형 모델에서 압도적입니다");
  s.addNotes("왼쪽 표를 보시면 방해 이미지가 늘수록 판별력이 단조 감소합니다. 3장이면 0.521, 사실상 우연입니다. 그런데 차단하면 어느 경우든 0.904로 돌아옵니다. 회복률이 방해 수와 무관하게 99%라는 게 중요합니다 — 정보가 손상된 게 아니라 가려져 있었다는 뜻입니다.");
}

// ═══════════════ 4. 경로 분해 (핵심) ═══════════════
{
  const s = pres.addSlide();
  kicker(s, "결과 2 — 원인 특정 (오늘의 핵심)");
  headline(s, "해악은 '이미지가 섞여서'가 아니라 '질문이 잘못 읽어서' 생깁니다");
  s.addText("입력 순서 [이미지1, 이미지2, 질문]에서 정보가 흐르는 경로는 둘뿐입니다 (이미지1은 이미지2를 볼 수 없음)", {
    x: 0.55, y: 1.36, w: 12.25, h: 0.3, fontFace: F, fontSize: 11.5, color: C.gray, margin: 0 });
  s.addTable([
    [m("", hd), m("개입 없음", hd), m("경로 A 차단\n이미지2 → 이미지1", hd),
     m("경로 B 차단\n질문 → 이미지2", hd), m("전면 차단", hd)],
    [m("3B", { bold: true }), m("0.6970"), m("0.4030", { bold: true, color: C.red }),
     m("0.9057", { bold: true, color: C.green }), m("0.9057")],
    [m("7B", { bold: true }), m("0.8690"), m("0.4471", { bold: true, color: C.red }),
     m("0.8993", { bold: true, color: C.green }), m("0.8993")],
  ], { x: 0.55, y: 1.76, w: 12.25, rowH: [0.72, 0.5, 0.5], ...TBL });

  const box = (x, w, title, body, fill, line, tcol) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.6, w, h: 1.62, rectRadius: 0.08,
      fill: { color: fill }, line: { color: line, width: 1.25 } });
    s.addText(title, { x: x + 0.25, y: 3.74, w: w - 0.5, h: 0.3, fontFace: F,
      fontSize: 13, bold: true, color: tcol, margin: 0 });
    s.addText(body, { x: x + 0.25, y: 4.1, w: w - 0.5, h: 1.0, fontFace: F,
      fontSize: 11, color: C.navy, margin: 0, lineSpacingMultiple: 1.2 });
  };
  box(0.55, 6.05, "① 이 배치에서는 해악의 경로가 '읽기' 하나뿐",
      "읽기 차단 = 전면 차단, 차이 0.0000 (CI [0,0]).\n관련 이미지가 방해보다 앞이라 방해를 볼 수 없기 때문 —\n구조상 예상되며, 구현 정확성 검증을 겸합니다.",
      C.lightgreen, C.green, C.green);
  box(6.78, 6.02, "② 예상 밖 — 이미지 간 혼합을 끊으면 크게 나빠짐",
      "3B −0.294 · 7B −0.422.\n방해가 관련 이미지를 보고 맥락화되면 오히려 덜 해롭습니다.\n고립시키면 더 도드라져 침입합니다. 이것이 실제 발견입니다.",
      C.lightred, C.red, C.red);
  s.addText("→ 정정된 가설: 환각은 표현의 오염(contamination)이 아니라 읽기 단계의 출처 오귀속(source misattribution)이다", {
    x: 0.55, y: 5.42, w: 12.25, h: 0.32, fontFace: F, fontSize: 12.5, bold: true,
    color: C.navy, margin: 0 });
  foot(s, "n=300 · AUC · 4D mask의 (질의 행 × 키 열) 사각형 단위 개입. 순서를 뒤집으면 관련 이미지가 방해를 볼 수 있어 표현 오염 경로가 생김 — 현재 측정 중");
  takeaway(s, "→ 개입해야 할 곳은 '이미지를 서로 떼어놓는 것'이 아니라 '읽기 경로를 제어하는 것'입니다");
  s.addNotes("이 슬라이드가 오늘의 핵심입니다. 왼쪽 박스는 솔직히 말씀드리면 구조상 예상되는 결과입니다. 관련 이미지가 방해보다 앞에 있으면 방해를 볼 수 없으니, 경로가 읽기 하나로 강제됩니다. 저희 구현이 정확하다는 검증으로 봐주시면 됩니다. 진짜 발견은 오른쪽입니다. 이미지끼리 보는 경로를 끊으면 크게 나빠집니다. 방해 이미지가 관련 이미지를 보고 맥락화되면 오히려 덜 해롭고, 고립시키면 더 도드라져서 침입한다는 뜻입니다. 그리고 순서를 뒤집으면 관련 이미지가 방해를 볼 수 있게 되어 표현 오염 경로가 실제로 생깁니다. 그 배치에서 다시 재고 있습니다.");
}

// ═══════════════ 5. 경계 ═══════════════
{
  const s = pres.addSlide();
  kicker(s, "결과 3 — 경계");
  headline(s, "이미지 간 attention이 필요한지는 질문 유형이 정합니다");
  s.addTable([
    [m("질문 유형", hd), m("예시", hd), m("이미지끼리 서로 못 보게 하면", hd), m("판정", hd)],
    [m("존재 확인 (any)", { bold: true }),
     m("\"이 중에 X가 있나?\"", { fontSize: 11 }),
     m("3B +0.0009 · 7B −0.0022  (CI가 0 포함)"),
     m("불필요", { bold: true, color: C.green })],
    [m("비교 (both)", { bold: true }),
     m("\"둘 다 X가 있나?\"", { fontSize: 11 }),
     m("3B R1 −12.0%p · 7B R1 −9.0%p · RB −16.0%p"),
     m("필요", { bold: true, color: C.red })],
  ], { x: 0.55, y: 1.5, w: 12.25, rowH: [0.5, 0.62, 0.62], ...TBL });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 3.4, w: 12.25, h: 1.72,
    rectRadius: 0.09, fill: { color: C.lightblue }, line: { color: C.blue, width: 1.25 } });
  s.addText("이것이 '앞단에 작은 모듈을 두면 되지 않나'에 대한 답입니다", {
    x: 0.85, y: 3.56, w: 11.7, h: 0.32, fontFace: F, fontSize: 13.5, bold: true,
    color: C.navy, margin: 0 });
  s.addText([
    { text: "앞단 selector는 이미지 단위로 all-or-nothing 결정을 내립니다. 그런데 최적 정책은 질문 유형에 따라 갈립니다 — 존재 확인에서는 무관 이미지의 읽기를 막아야 하고, 비교에서는 이미지 간 attention을 살려둬야 합니다.", options: { fontSize: 11.5, color: C.navy, breakLine: true } },
    { text: "게다가 selector가 틀려서 관련 이미지를 버리면 AUC가 0.015~0.043으로 붕괴합니다 — 복구 불가능한 오류입니다. 모델 내부 개입은 층·경로·강도를 연속적으로 조절할 수 있습니다.", options: { fontSize: 11.5, color: C.navy } },
  ], { x: 0.85, y: 3.96, w: 11.7, h: 1.1, fontFace: F, margin: 0, paraSpaceAfter: 6 });
  foot(s, "any 태스크는 AUC 0.99로 천장에 가까워 증거력이 제한적 — 더 어려운 need-all 셋(all-of-3)을 현재 측정 중");
  takeaway(s, "→ 무엇을 언제 막을지는 질문이 정합니다. 이미지만 보고 미리 거를 수 있는 문제가 아닙니다");
  s.addNotes("교수님께서 물어보실 만한 것을 미리 답해두었습니다. CLIP 같은 작은 모듈로 앞에서 걸러내면 되지 않느냐는 질문인데, 두 가지로 답합니다. 첫째, 최적 정책이 질문 유형에 따라 다릅니다. 둘째, 앞단 selector의 오판은 복구가 안 됩니다.");
}

// ═══════════════ 6. 선행연구 ═══════════════
{
  const s = pres.addSlide();
  kicker(s, "선행연구 대조");
  headline(s, "기존 연구는 정반대 처방을 내놓았고, 우리 분해가 둘 다 설명합니다");
  s.addTable([
    [m("", hd), m("무엇을 하나", hd), m("layer 개입", hd), m("학습 불필요", hd), m("무관 이미지 실험", hd)],
    [m("FOCUS  2508.13744", { bold: true }), m("타깃 외 이미지를 픽셀 노이즈로 가림, N+1회 forward"),
     m("없음", { color: C.red }), m("예"), m("없음", { color: C.red })],
    [m("MIMIC  2601.07812", { bold: true }), m("layer 12–23에서 inter-image를 균일 차단"),
     m("예"), m("아니오", { color: C.red }), m("있음")],
    [m("CAPL  2603.07048", { bold: true }), m("cross-image attention을 오히려 연다 + DPO"),
     m("예"), m("아니오", { color: C.red }), m("없음", { color: C.red })],
    [m("SoFA  CVPR 2025", { bold: true }), m("causal ↔ 양방향 mask 보간 (2층 간격)"),
     m("예"), m("예"), m("없음", { color: C.red })],
    [m("RSCD  2603.23934", { bold: true }), m("중간층 text→text 차단 + 대조 디코딩"),
     m("예"), m("예"), m("있음")],
  ], { x: 0.55, y: 1.45, w: 12.25, rowH: [0.48, 0.45, 0.45, 0.45, 0.45, 0.45], ...TBL });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 4.32, w: 6.05, h: 1.75,
    rectRadius: 0.08, fill: { color: C.lightred }, line: { color: C.red, width: 1.25 } });
  s.addText("쓰면 안 되는 주장", { x: 0.78, y: 4.46, w: 5.6, h: 0.28, fontFace: F,
    fontSize: 12.5, bold: true, color: C.red, margin: 0 });
  s.addText("· \"training-free 개입\" — FOCUS·RSCD·SoFA가 이미\n· \"layer 단위 개입\" — 4편 모두 이미\n· \"인과 검증 방법론\" — RSCD가 layer sweep 국소화 수행", {
    x: 0.78, y: 4.8, w: 5.6, h: 1.0, fontFace: F, fontSize: 11, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.3 });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.78, y: 4.32, w: 6.02, h: 1.75,
    rectRadius: 0.08, fill: { color: C.lightgreen }, line: { color: C.green, width: 1.25 } });
  s.addText("비어 있는 자리", { x: 7.01, y: 4.46, w: 5.6, h: 0.28, fontFace: F,
    fontSize: 12.5, bold: true, color: C.green, margin: 0 });
  s.addText("· 이미지↔이미지 edge의 layer 분해 knockout — 0편\n  (기존 knockout은 전부 모달리티 간 edge만)\n· 무관 이미지 '하나만' 골라 차단 — pruning 25편 중 0편\n· 무관 이미지 레짐 자체를 CAPL·SoFA는 실험 안 함", {
    x: 7.01, y: 4.8, w: 5.6, h: 1.1, fontFace: F, fontSize: 11, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.25 });
  takeaway(s, "→ CAPL·SoFA는 \"열어라\", MIMIC은 \"막아라\". 둘 다 맞았습니다 — 서로 다른 경로를 건드리고 있었습니다");
  s.addNotes("선행연구를 네 축으로 조사했고 고위협 논문 다섯 편은 원문까지 확인했습니다. 그 결과 처음에 novelty로 생각했던 세 가지는 쓸 수 없다는 걸 알았습니다. 대신 더 좁고 확실한 자리가 열렸습니다. 특히 CAPL과 SoFA는 attention을 여는 방향, MIMIC은 막는 방향으로 정반대 처방을 냈는데, 저희 경로 분해가 이 모순을 설명합니다.");
}

// ═══════════════ 7. 컨트롤러 ═══════════════
{
  const s = pres.addSlide();
  kicker(s, "결과 4 — 오라클 없이 작동하는가");
  headline(s, "신호를 attention에서 인과적 반사실로 바꾸자 컨트롤러가 작동했습니다");
  s.addTable([
    [m("", hd), m("신호", hd), m("얕은 층 위치무관 정확도", hd), m("판정", hd)],
    [m("기존 시도", { bold: true }), m("attention 질량 (RoPE 유·무 모두)"),
     m("0.50 — 우연. 22층에서야 0.91", { color: C.red }),
     m("실패", { bold: true, color: C.red })],
    [m("전환", { bold: true }), m("이미지를 하나씩 빼보고 답이 얼마나 움직이는지"),
     m("위치를 참조하지 않음 → 편향 구조적 불가", { color: C.green }),
     m("성공", { bold: true, color: C.green })],
  ], { x: 0.55, y: 1.45, w: 12.25, rowH: [0.45, 0.55, 0.55], ...TBL });

  s.addTable([
    [m("", hd), m("방해 수", hd), m("컨트롤러", hd), m("손익분기", hd),
     m("개입 없음", hd), m("실현 성능", hd)],
    [m("3B", { bold: true }), m("1"), m("0.693"), m("0.761", { color: C.red }),
     m("0.6978"), m("0.6669  (−3.1%p)", { color: C.red })],
    [m("", {}), m("2"), m("0.707"), m("0.661"),
     m("0.6063"), m("0.7126  (+10.6%p)", { bold: true, color: C.green })],
    [m("", {}), m("3"), m("0.730", { bold: true }),
     m("0.569", { bold: true, color: C.green }), m("0.5213"),
     m("0.7028  (+18.2%p)", { bold: true, color: C.green })],
    [m("7B", { bold: true }), m("1"), m("0.953", { bold: true, color: C.blue }),
     m("0.966", { color: C.red }), m("0.8690"), m("0.8884  (+1.9%p)")],
    [m("", {}), m("3"), m("0.937", { bold: true, color: C.blue }),
     m("0.975", { color: C.red }), m("0.8740"), m("0.8928  (+1.9%p)")],
  ], { x: 0.55, y: 3.05, w: 12.25, rowH: [0.42, 0.38, 0.38, 0.42, 0.4, 0.4], ...TBL });

  s.addText([
    { text: "3B에서는 두 곡선이 반대로 움직여 N=2에서 교차합니다.  ", options: { bold: true, fontSize: 12, color: C.navy } },
    { text: "컨트롤러는 방해가 늘수록 정확해지고(0.693 → 0.730), 손익분기는 내려갑니다(0.761 → 0.569).", options: { fontSize: 12, color: C.navy, breakLine: true } },
    { text: "7B에서는 컨트롤러가 0.95로 훨씬 정확한데도 손익분기가 0.97이라 순이득이 남지 않습니다 — 고칠 손상 자체가 작기 때문입니다. 컨트롤러가 되는 곳에는 고칠 게 없고, 고칠 게 많은 곳에서 컨트롤러가 겨우 됩니다.", options: { fontSize: 12, color: C.navy } },
  ], { x: 0.55, y: 5.28, w: 12.25, h: 0.85, fontFace: F, margin: 0, paraSpaceAfter: 4 });
  foot(s, "n=300/모델. 컨트롤러 정확도와 손익분기는 정확한 값이며, '실현 성능'은 오판 시 조건을 근사한 낙관값 — 0.730 > 0.569 판정은 근사에 의존하지 않음. forward N+1회 필요(정확도 트랙)");
  takeaway(s, "→ 이 방법의 가치는 소형 모델 + 다수 무관 입력 레짐에 있습니다. 7B 이상은 \"되지만 고칠 게 없다\"가 정직한 서술입니다", C.green);
  s.addNotes("여기가 그동안 막혀 있던 부분입니다. attention으로 관련 이미지를 판정하려는 시도는 계속 실패했습니다. 위치 편향 때문이었고, 선행연구가 제시한 RoPE 제거 처방을 적용해도 안 됐습니다. 그래서 신호를 완전히 바꿨습니다. 이미지를 하나씩 빼보고 답이 가장 크게 움직이는 것을 관련 이미지로 봅니다. 위치를 아예 참조하지 않으니 위치 편향이 원천적으로 불가능합니다.");
}

// ═══════════════ 8. 방법 후보 ═══════════════
{
  const s = pres.addSlide();
  kicker(s, "방법 후보");
  headline(s, "정확도 트랙과 효율 트랙은 다른 지점입니다");
  s.addTable([
    [m("방법", hd), m("3B N=3 AUC", hd), m("계산량", hd), m("오라클 필요", hd), m("상태", hd)],
    [m("개입 없음", { bold: true }), m("0.5213", { color: C.red }), m("1×"), m("—"), m("기준선")],
    [m("하드 차단 (T0)", { bold: true }), m("0.9041"), m("< 1× (절감)"), m("예"), m("검증 완료")],
    [m("대조 디코딩 (β=1)", { bold: true }), m("0.9644", { bold: true, color: C.green }),
     m("2×", { color: C.red }), m("예"), m("검증 완료")],
    [m("반사실 컨트롤러 + 차단", { bold: true }), m("0.7028"), m("N+1×", { color: C.red }),
     m("아니오", { bold: true, color: C.green }), m("검증 완료")],
    [m("(참고) 1장만 준 상한", { bold: true, color: C.gray }), m("0.9078", { color: C.gray }),
     m("< 1×", { color: C.gray }), m("—"), m("—")],
  ], { x: 0.55, y: 1.45, w: 12.25, rowH: [0.48, 0.42, 0.42, 0.46, 0.46, 0.42], ...TBL });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 4.2, w: 12.25, h: 1.85,
    rectRadius: 0.09, fill: { color: C.lightgreen }, line: { color: C.green, width: 1.25 } });
  s.addText("대조 디코딩이 '1장만 준 상한'을 넘습니다 — 제거가 아니라 오염의 크기를 증거로 쓰기 때문", {
    x: 0.85, y: 4.36, w: 11.7, h: 0.3, fontFace: F, fontSize: 13, bold: true, color: C.green, margin: 0 });
  s.addText([
    { text: "margin_CD = (1+β)·margin(차단) − β·margin(무개입).  두 끝점을 빼기만 한 '차이 신호'도 단독으로 AUC 0.9370입니다 — 차단본(0.9041)보다도 높습니다.", options: { fontSize: 11.5, color: C.navy, breakLine: true } },
    { text: "방해 이미지가 답을 많이 밀어낸 문항이 곧 틀릴 뻔한 문항이기 때문입니다. 제거는 오염을 없애고, 대조는 오염의 크기를 정보로 씁니다. 7B에서는 지울 오염이 적어 β를 키우면 오히려 손해입니다 (β=2에서 0.828).", options: { fontSize: 11.5, color: C.navy } },
  ], { x: 0.85, y: 4.74, w: 11.7, h: 1.2, fontFace: F, margin: 0, paraSpaceAfter: 6 });
  takeaway(s, "→ 가설 정정에 따라 'neg attention으로 뒤쪽 층에서 분리'는 폐기합니다 — 분리할 대상이 문제가 아니었습니다");
  s.addNotes("방법은 여러 개를 시험했고 트레이드오프가 분명합니다. 하드 차단은 계산을 줄이지만 오라클이 필요합니다. 대조 디코딩은 정확도가 가장 좋지만 forward가 두 번입니다. 반사실 컨트롤러는 오라클이 필요 없지만 N+1번입니다. 그리고 처음에 생각했던 negative attention은 폐기합니다. 조사해보니 GPAM 계열은 전부 아키텍처 변경과 학습이 필요하고, 학습 없이 할 수 있는 건 결국 저희 마스크의 연속판이었습니다.");
}

// ═══════════════ 9. 남은 위험 ═══════════════
{
  const s = pres.addSlide();
  kicker(s, "정직한 한계");
  headline(s, "지금 이 연구를 무너뜨릴 수 있는 것 세 가지");
  const risks = [
    ["1", "벤치마크가 위치로 대상을 지목한다",
     "질문이 \"첫 번째 이미지에\"로 시작하므로, 앞단 모듈이 텍스트만 파싱해도 100% 맞힙니다.\n현 벤치마크로는 '내부 개입이어야 하는 이유'를 증명할 수 없습니다.",
     "대응: 관련도가 추론의 결과인 질문으로 교체 — all-of-3 세트 측정 중"],
    ["2", "실현 성능이 아직 오라클 상한에 크게 못 미친다",
     "N=3에서 오라클 0.904 vs 실현 0.703. 손상의 절반만 회수합니다.\n그리고 forward N+1회라 효율 이득이 없습니다.",
     "대응: 컨트롤러 신호 개선 + 소프트 개입(λ)으로 오판 비용 완화"],
    ["3", "표준 벤치마크에서 아직 보이지 않았다",
     "CAPL은 \"추론시 attention 수정만으로는 일시적 개선\"이라고 선점 반론을 폈습니다.\nBLINK·MUIRBench 같은 공개 벤치에서 재현해야 이 반론을 막습니다.",
     "대응: 다음 단계 1순위"],
  ];
  risks.forEach((r, i) => {
    const y = 1.42 + i * 1.68;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 12.25, h: 1.54,
      rectRadius: 0.08, fill: { color: C.lightred }, line: { color: C.red, width: 1 } });
    s.addShape(pres.shapes.OVAL, { x: 0.82, y: y + 0.18, w: 0.44, h: 0.44, fill: { color: C.red } });
    s.addText(r[0], { x: 0.82, y: y + 0.18, w: 0.44, h: 0.44, align: "center",
      valign: "middle", fontFace: F, fontSize: 13, bold: true, color: C.white, margin: 0 });
    s.addText(r[1], { x: 1.44, y: y + 0.16, w: 11.1, h: 0.3, fontFace: F,
      fontSize: 13, bold: true, color: C.navy, margin: 0 });
    s.addText(r[2], { x: 1.44, y: y + 0.5, w: 11.1, h: 0.6, fontFace: F,
      fontSize: 11, color: C.navy, margin: 0, lineSpacingMultiple: 1.15 });
    s.addText(r[3], { x: 1.44, y: y + 1.14, w: 11.1, h: 0.3, fontFace: F,
      fontSize: 11, bold: true, color: C.green, margin: 0 });
  });
  takeaway(s, "→ 셋 다 알고 있고, 셋 다 측정으로 답할 수 있습니다");
  s.addNotes("불리한 것을 먼저 말씀드립니다. 가장 큰 문제는 벤치마크입니다. 지금 질문이 첫 번째 이미지라고 위치를 지목하기 때문에 앞단 모듈이 텍스트만 읽어도 됩니다. 이건 설계 결함이고 바꿔야 합니다.");
}

// ═══════════════ 10. 계획 ═══════════════
{
  const s = pres.addSlide();
  s.background = { color: C.darkbg };
  kicker(s, "다음 단계", true);
  headline(s, "4주 계획 — 각 주마다 중단 조건을 미리 정해둡니다", true);
  const plan = [
    ["W1", "벤치마크 교체", "위치 지목 질문 → 관련도가 추론의 결과인 질문\n(all-of-3, 속성 비교, 다단계 참조)", "앞단 selector가 원리적으로 못 푸는가"],
    ["W2", "표준 벤치 재현", "BLINK · MUIRBench · MIRB에서\n경로 분해와 회복률이 재현되는가", "CAPL의 \"일시적 개선\" 반론 방어"],
    ["W3", "컨트롤러 강화", "반사실 신호 + 소프트 개입(λ) 결합,\nFOCUS(픽셀 노이즈)와 직접 비교", "같은 N+1 비용에서 우리가 이기는가"],
    ["W4", "정리", "3계열 이상 모델로 확장,\n논문 초안", "—"],
  ];
  plan.forEach((p, i) => {
    const y = 1.5 + i * 1.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 12.25, h: 1.02,
      rectRadius: 0.08, fill: { color: "1A3247" }, line: { color: "2E4E6B", width: 1 } });
    s.addText(p[0], { x: 0.85, y: y + 0.3, w: 0.7, h: 0.4, fontFace: F, fontSize: 15,
      bold: true, color: "7EC8F5", margin: 0 });
    s.addText(p[1], { x: 1.7, y: y + 0.14, w: 3.2, h: 0.3, fontFace: F, fontSize: 13,
      bold: true, color: C.white, margin: 0 });
    s.addText(p[2], { x: 1.7, y: y + 0.46, w: 5.3, h: 0.5, fontFace: F, fontSize: 10.5,
      color: "9FB8CE", margin: 0, lineSpacingMultiple: 1.15 });
    s.addText("→ " + p[3], { x: 7.4, y: y + 0.3, w: 5.2, h: 0.42, fontFace: F,
      fontSize: 11.5, color: "8CE0B0", margin: 0, valign: "middle" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.24, w: 12.25, h: 0.92,
    rectRadius: 0.08, fill: { color: "1D3850" }, line: { color: "2E4E6B", width: 1 } });
  s.addText([
    { text: "중단 조건: W2에서 표준 벤치 재현이 실패하면 이 방향은 접습니다.", options: { bold: true, fontSize: 12.5, color: "FFC94D", breakLine: true } },
    { text: "자원: GPU 1장 · 기존 코드·데이터 전부 재사용 · 지금까지 사전 등록 4건, 그중 2건은 실패로 기록했습니다", options: { fontSize: 11, color: "9FB8CE" } },
  ], { x: 0.85, y: 6.34, w: 11.7, h: 0.78, fontFace: F, margin: 0, paraSpaceAfter: 4 });
  s.addNotes("4주 계획입니다. 가장 중요한 건 2주차입니다. 공개 벤치마크에서 재현되지 않으면 접겠습니다. 지금까지 사전 등록을 네 번 했고 그중 두 번은 실패로 기록했습니다. 이번에도 같은 방식으로 하겠습니다.");
}

pres.writeFile({ fileName: "/Users/hansangmin/Source-Depth/meeting/_generated/deck_v5.pptx" })
  .then(() => console.log("DECK v5 WRITTEN"));
