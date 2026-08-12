// SourceDepth 미팅 덱 — 컴팩트판 (본편 6장 + 부록 4장)
// 결과가 좋지 않으므로 간결하게: 무엇을 쟀고, 무엇이 무너졌고, 1주일만 더.
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

const R = "/Users/hansangmin/Source-Depth/results/";
const C = {
  navy: "1F3B57", darkbg: "142638", blue: "1F77B4", red: "D62728",
  orange: "E8890C", green: "2E8B57", gray: "6B7280", light: "EFF4F9",
  lightred: "FBEAEA", lightgray: "F3F4F6", white: "FFFFFF", line: "D5DEE8",
  lightgreen: "E9F4EE", lightorange: "FDF3E3",
};
const F = "Arial";
const W = 13.33;

// ── POSBAL: 위치 균형화 결과 (실측되면 아래 값이 채워짐) ──────────
// null 이면 "실행 중" 으로 표기된다.
const POSBAL = require("./posbal_summary.json");

function kicker(s, t, dark) {
  s.addText(t, { x: 0.55, y: 0.28, w: 10.5, h: 0.32, fontFace: F, fontSize: 11.5,
    bold: true, color: dark ? "9FB8CE" : C.blue, margin: 0 });
}
function headline(s, t, dark, w) {
  s.addText(t, { x: 0.55, y: 0.58, w: w || 12.2, h: 0.8, fontFace: F, fontSize: 23,
    bold: true, color: dark ? C.white : C.navy, margin: 0 });
}
function takeaway(s, t) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.6, w: 12.25, h: 0.62,
    rectRadius: 0.08, fill: { color: C.navy } });
  s.addText(t, { x: 0.85, y: 6.6, w: 11.75, h: 0.62, fontFace: F, fontSize: 13,
    bold: true, color: C.white, margin: 0, valign: "middle" });
}
function foot(s, t, dark) {
  s.addText(t, { x: 0.55, y: 6.05, w: 12.2, h: 0.4, fontFace: F, fontSize: 10.5,
    color: dark ? "8AA5BC" : C.gray, margin: 0 });
}

// =====================================================================
// 1 — 표지 + 한 장 요약
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.darkbg };
  s.addText("SOURCEDEPTH · 검증 실험 결과 보고 · 2026-08-12 · 한상민", { x: 0.6, y: 0.5,
    w: 11, h: 0.32, fontFace: F, fontSize: 11.5, bold: true, color: "8AA5BC", margin: 0 });
  s.addText("가설의 앞부분은 확인됐고,\n뒷부분은 제 손으로 반증했습니다", { x: 0.6, y: 1.05,
    w: 12.2, h: 1.5, fontFace: F, fontSize: 30, bold: true, color: C.white,
    margin: 0, lineSpacingMultiple: 1.15 });
  s.addText("\"이미지마다 계산 깊이를 다르게 주면 환각이 줄고 계산도 준다\" — 3일간 6,000회 이상 측정한 결과", {
    x: 0.6, y: 2.65, w: 12.2, h: 0.4, fontFace: F, fontSize: 13.5, color: "AFC6DA", margin: 0 });
  const cards = [
    ["✓ 확인된 것", "무관한 이미지가 답의 21%를 뒤집고(대조군 0%),\n그 이미지를 차단하면 오답의 81%가 회복된다.\n반대로 정답 이미지를 자르면 0.79 → 0.50으로 붕괴", "부작용은 3.7%뿐 · p = 6×10⁻⁷ / 4×10⁻³⁸", "8CE0B0"],
    ["✗ 무너진 것", "관련 이미지를 스스로 판정하는 시점(22층)이\n개입해야 하는 시점(16층)보다 늦다.\n실제 컨트롤러를 끼우면 −1.5%p", "→ 자동화가 안 되면 쓸 수 없다", "FF8A80"],
    ["? 남은 것", "가장 가까운 연구를 원문 대조해 보니\ntraining-free 추론시 개입과 환각 평가는\n다루지 않았고, 열린 질문을 남겼다", "→ 1주일만 더 확인하고 싶습니다", "FFC94D"],
  ];
  cards.forEach((c, i) => {
    const x = 0.6 + i * 4.15, y = 3.35, w = 3.95, h = 3.3;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: "1D3850" }, line: { color: "2E4E6B", width: 1 } });
    s.addText(c[0], { x: x + 0.25, y: y + 0.22, w: w - 0.5, h: 0.4, fontFace: F,
      fontSize: 16, bold: true, color: c[3], margin: 0 });
    s.addText(c[1], { x: x + 0.25, y: y + 0.78, w: w - 0.5, h: 1.7, fontFace: F,
      fontSize: 12.5, color: C.white, margin: 0, lineSpacingMultiple: 1.25 });
    s.addText(c[2], { x: x + 0.25, y: y + 2.6, w: w - 0.5, h: 0.55, fontFace: F,
      fontSize: 11, color: "9FB8CE", margin: 0 });
  });
  s.addNotes("결론부터 말씀드리겠습니다. 가설의 앞부분은 확인했고, 뒷부분은 제 손으로 반증했습니다. 다만 어제 '이미 나온 연구가 있어서 접어야겠다'고 판단했던 걸 원문으로 확인해 보니 제가 수치를 잘못 읽었더군요. 그래서 1주일만 더 확인하고 진행/중단을 확정하고 싶습니다.");
}

// =====================================================================
// 2 — 무엇을 어떻게 쟀나
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "실험 설계");
  headline(s, "오염이 생길 수밖에 없는 문항과 안 생기는 문항을 나란히 놓고 비교했다");
  // 좌: 4셀
  const rows = [
    [{ text: "", options: {} },
     { text: "방해 이미지에 그 물건 있음", options: { bold: true, color: C.white, fill: { color: C.navy } } },
     { text: "없음", options: { bold: true, color: C.white, fill: { color: C.navy } } }],
    [{ text: "정답 '없다'", options: { bold: true, color: C.white, fill: { color: C.navy } } },
     { text: "주 측정\n(뒤집힘 예상)", options: { fill: { color: C.lightred }, bold: true, color: C.red } },
     { text: "대조군", options: { fill: { color: C.lightgray }, color: C.gray } }],
    [{ text: "정답 '있다'", options: { bold: true, color: C.white, fill: { color: C.navy } } },
     { text: "대조군", options: { fill: { color: C.lightgray }, color: C.gray } },
     { text: "역방향 측정", options: { fill: { color: C.lightred }, bold: true, color: C.red } }],
  ];
  s.addTable(rows, { x: 0.55, y: 1.75, w: 6.2, rowH: [0.5, 0.95, 0.95], fontFace: F,
    fontSize: 11.5, align: "center", valign: "middle", border: { pt: 1, color: "FFFFFF" } });
  s.addText("POPE(COCO) 600문항 · 셀당 150 · Qwen2.5-VL 3B와 7B · seed 고정 · 판정 기준 사전 동결", {
    x: 0.55, y: 4.4, w: 6.2, h: 0.55, fontFace: F, fontSize: 11, color: C.gray, margin: 0 });
  // 우: 개입
  s.addText("개입: 특정 층부터 그 이미지를 참조하지 못하게 차단", { x: 7.1, y: 1.75, w: 5.7, h: 0.4,
    fontFace: F, fontSize: 13.5, bold: true, color: C.navy, margin: 0 });
  const items = [
    ["차단 없음", "지금의 모델 (기준선)"],
    ["4·8·12·16·20·24층부터", "차단 시작 층을 바꿔가며"],
    ["완전 차단", "이미지를 안 준 것과 비교"],
    ["반대로 정답 이미지를 차단", "검증용 — 무너져야 정상"],
  ];
  items.forEach((it, i) => {
    const y = 2.25 + i * 0.72;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.1, y, w: 5.7, h: 0.6, rectRadius: 0.07,
      fill: { color: i === 3 ? C.lightorange : C.light }, line: { color: i === 3 ? C.orange : C.line, width: 1 } });
    s.addText([{ text: it[0] + "   ", options: { bold: true, fontSize: 12, color: C.navy } },
      { text: it[1], options: { fontSize: 10.5, color: C.gray } }],
      { x: 7.32, y, w: 5.3, h: 0.6, fontFace: F, margin: 0, valign: "middle" });
  });
  s.addText("정합성 점검 3종 통과 후 진행: 차단이 실제로 작동(98.3%) · 채점 정상(85.5%) · 마스킹≡실제삭제(100%)", {
    x: 0.55, y: 5.15, w: 12.2, h: 0.5, fontFace: F, fontSize: 11.5, italic: true, color: C.gray, margin: 0 });
  takeaway(s, "→ 대조군을 둔 이유: '답이 뒤집히는 것'이 우연인지 방해 이미지 때문인지 숫자로 구분하기 위해");
  s.addNotes("설계의 핵심은 대조군입니다. 방해 이미지에 물건이 있는 문항과 없는 문항을 똑같이 150개씩 두면, 뒤집힘이 물건 때문인지 아닌지 바로 구분됩니다.");
}

// =====================================================================
// 3 — 확인된 것
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "결과 ① — 확인된 것");
  headline(s, "문제는 실재하고, 차단하면 회복되며, 그 효과는 인과적이다");
  const stats = [
    ["21.3%", "답이 뒤집힌 비율", "같은 조건 대조군은 0.0%\n→ 우연이 아니라 그 물건이 넘어온 것", C.red],
    ["81%", "차단으로 회복된 오답", "새로 생긴 오답은 3.7% (22배)\nMcNemar p = 6×10⁻⁷", C.blue],
    ["0.79 → 0.50", "정답 이미지를 대신 차단하면", "우연일 확률 p = 4×10⁻³⁸\n→ 상관이 아니라 인과", C.green],
  ];
  stats.forEach((t, i) => {
    const x = 0.55 + i * 4.25, y = 1.8, w = 4.0, h = 2.55;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: C.light }, line: { color: t[3], width: 1.25 } });
    s.addText(t[0], { x: x + 0.25, y: y + 0.25, w: w - 0.5, h: 0.8, fontFace: F,
      fontSize: 34, bold: true, color: t[3], margin: 0 });
    s.addText(t[1], { x: x + 0.25, y: y + 1.1, w: w - 0.5, h: 0.4, fontFace: F,
      fontSize: 13, bold: true, color: C.navy, margin: 0 });
    s.addText(t[2], { x: x + 0.25, y: y + 1.55, w: w - 0.5, h: 0.9, fontFace: F,
      fontSize: 11, color: C.gray, margin: 0, lineSpacingMultiple: 1.2 });
  });
  s.addImage({ path: R + "fig1b_when_to_block.png", x: 2.3, y: 4.5, w: 8.7, h: 1.95 });
  foot(s, "");
  takeaway(s, "→ 여기까지가 좋은 소식입니다. 다만 이 숫자들은 전부 '어느 이미지가 방해인지 아는' 조건입니다");
  s.addNotes("세 숫자만 보시면 됩니다. 21%가 뒤집혔고, 81%가 회복됐고, 반대로 자르면 무너집니다. 그림은 몇 층에서 자르느냐에 따른 정답률인데, 16층 이전에 자르면 방해 이미지가 없었던 것과 같은 수준입니다.");
}

// =====================================================================
// 4 — 무너진 것
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "결과 ② — 무너진 것 (오늘의 핵심)");
  headline(s, "어느 이미지가 방해인지 스스로 알아내지 못했고, 속도 이득도 실현되지 않았다");
  const fails = [
    ["①", "스스로 판정하지 못한다",
     "8층에서 관련 이미지를 99.8% 맞히길래 됐다 싶었는데,\n이미지 순서를 뒤집으니 0.2%. 관련도가 아니라 '첫 번째'를 보던 것.\n순서를 뒤집어도 맞는 신호는 22층에서야 나오는데, 차단이 효과 있는 구간은 16층 이전.",
     "실제로 끼워보면 무개입 대비 −1.5%p"],
    ["②", "실제로는 별로 빨라지지 않았다",
     "계산량 기준으로는 42% 절약인데, 실제 응답 시작 시간은 510ms → 461ms.\n이론치의 23%밖에 실현되지 않았다.",
     "9.7% 단축으로는 쓸 이유가 없다"],
    ["③", "7B에서는 현상 자체가 옅다",
     "답 뒤집힘이 3B 21.3% → 7B 0.7%. 단일 이미지에서 이미 94.7%라 천장 효과.\n(문헌상 더 어려운 벤치에서는 7B도 −10.4%p로 남아 있음)",
     "벤치마크를 바꿔야 측정 가능"],
  ];
  fails.forEach((f, i) => {
    const y = 1.72 + i * 1.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 12.25, h: 1.45, rectRadius: 0.09,
      fill: { color: C.lightred }, line: { color: C.red, width: 1 } });
    s.addShape(pres.shapes.OVAL, { x: 0.8, y: y + 0.15, w: 0.48, h: 0.48, fill: { color: C.red } });
    s.addText(f[0], { x: 0.8, y: y + 0.15, w: 0.48, h: 0.48, align: "center", valign: "middle",
      fontFace: F, fontSize: 14, bold: true, color: C.white, margin: 0 });
    s.addText(f[1], { x: 1.45, y: y + 0.12, w: 4.0, h: 0.4, fontFace: F, fontSize: 13.5,
      bold: true, color: C.navy, margin: 0 });
    s.addText(f[2], { x: 1.45, y: y + 0.52, w: 8.0, h: 0.85, fontFace: F, fontSize: 10.8,
      color: C.gray, margin: 0, lineSpacingMultiple: 1.15 });
    s.addText("→ " + f[3], { x: 9.6, y: y + 0.3, w: 3.05, h: 0.85, fontFace: F, fontSize: 11,
      bold: true, color: C.red, margin: 0 });
  });
  takeaway(s, "→ 다만 좋은 소식 하나: 계산량이 같을 때 \u0027방해 이미지를 먼저 끊는\u0027 배분이 \u0027둘 다 똑같이 끊는\u0027 것보다 나았고, 이미지 순서를 뒤집어도 그 이득의 80%가 유지됐습니다");
  s.addNotes("이 세 개가 오늘 보고의 중심입니다. 특히 첫 번째 — 순서를 뒤집었더니 신호가 무너진 것 — 은 제 방법만의 문제가 아니라 얕은 층 attention을 쓰는 기존 방법들에도 해당됩니다. 두 번째는 더 단순합니다 — 계산량을 42% 줄여도 실제 응답 시간은 10%밖에 안 줄었습니다. 이론과 실측이 이만큼 벌어지면 효율성을 기여로 내세울 수 없습니다. 다만 아래 결론처럼, 같은 계산량 안에서 방해 이미지를 먼저 끊는 배분 자체는 순서를 뒤집어도 살아남았습니다.");
}

// =====================================================================
// 5 — 그런데 자리는 비어 있다
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "결과 ③ — 그러면 이미 누가 했나?");
  headline(s, "어제는 '이미 나왔다'고 판단했는데, 원문을 보니 제가 잘못 읽었습니다");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 12.5 };
  const cc = { fontSize: 13.5, color: C.navy, fill: { color: C.white } };
  const m = (t, o) => ({ text: t, options: Object.assign({}, cc, o || {}) });
  s.addTable([
    [m("", hd), m("MIMIC (CVPR 2026, arXiv 2601.07812)", hd), m("우리", hd)],
    [m("학습", { bold: true, fontSize: 14 }),
     m("필요  —  8×H100 · 합성데이터 198K", { bold: true, color: C.red }),
     m("불필요  —  추론 중 개입만", { bold: true, color: C.green })],
    [m("환각 평가", { bold: true, fontSize: 14 }),
     m("안 함  —  POPE 언급 0회", { bold: true, color: C.red }),
     m("주 평가 대상  —  POPE 4셀 통제 설계", { bold: true, color: C.green })],
  ], { x: 0.55, y: 1.95, w: 12.25, rowH: [0.5, 0.9, 0.9], fontFace: F,
       align: "center", valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 4.6, w: 12.25, h: 1.75, rectRadius: 0.09,
    fill: { color: C.lightgreen }, line: { color: C.green, width: 1.25 } });
  s.addText([
    { text: "그들이 설명하지 못한 것을, 우리는 이미 측정했습니다", options: { bold: true, fontSize: 15, color: C.green, breakLine: true } },
    { text: "그들의 마스킹은 자체 벤치에서는 오르고 다른 벤치에서는 내려가는데, 왜 그런지 설명이 없습니다.", options: { fontSize: 13, color: C.navy, breakLine: true } },
    { text: "우리 데이터에서는 질문 유형에 따라 부호가 뒤집힙니다 — 단일 이미지 질문 +21%p  ↔  두 이미지 비교 질문 −51%p (7B에서도 −41%p로 재현)", options: { fontSize: 13, bold: true, color: C.navy } },
  ], { x: 0.9, y: 4.75, w: 11.6, h: 1.5, fontFace: F, margin: 0, paraSpaceAfter: 7 });

  takeaway(s, "→ 학습 없이, 환각을 대상으로 하는 자리는 아직 비어 있습니다 — 다만 확인하려면 검증이 더 필요합니다");
  s.addNotes("어제 저는 이 논문 때문에 접어야겠다고 판단했었습니다. 그런데 원문 19페이지를 직접 대조해 보니 핵심 수치를 잘못 읽었더군요. 26.4에서 49.4로 올랐다고 보고된 부분은 마스킹이 아니라 198K 합성 학습데이터가 만든 것이고, 동일 조건에서 마스킹 단독 효과는 3.3점입니다. 그리고 파인튜닝이 전제입니다. 덧붙이면 그들의 마스킹은 자체 벤치 밖에서는 오히려 평균이 42.7에서 41.2로 내려갑니다. 다루는 이미지 장수도 중앙값 4~7장의 집계 태스크라 저희 2장 출처 귀속과는 다릅니다.");
}

// =====================================================================
// 6 — 1주일 계획
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.darkbg };
  kicker(s, "요청", true);
  headline(s, "1주일 뒤에 진행/중단을 확정하겠습니다", true);

  const gates = [
    ["A", "깊이를 조절할 이유가 있는가?",
     "방해 이미지를 0층에서 아예 지운 것과 직접 비교한다 (셀 2·3 대상)",
     "아예 지우는 쪽이 같거나 더 좋으면  →  이 주제는 폐기"],
    ["B", "어느 이미지가 방해인지 자동으로 알 수 있는가?",
     "attention 대신 vision feature · hidden state로 16층 이전에서 판정",
     "이미지 순서를 뒤집었을 때 유지되지 않으면  →  이 주제는 폐기"],
  ];
  gates.forEach((g, i) => {
    const y = 1.62 + i * 2.0;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 12.25, h: 1.82, rectRadius: 0.09,
      fill: { color: "1A3247" }, line: { color: "2E4E6B", width: 1.25 } });
    s.addShape(pres.shapes.OVAL, { x: 0.95, y: y + 0.55, w: 0.72, h: 0.72, fill: { color: "7EC8F5" } });
    s.addText(g[0], { x: 0.95, y: y + 0.55, w: 0.72, h: 0.72, align: "center", valign: "middle",
      fontFace: F, fontSize: 22, bold: true, color: C.darkbg, margin: 0 });
    s.addText("게이트 " + g[0], { x: 1.95, y: y + 0.24, w: 3.0, h: 0.3, fontFace: F, fontSize: 11,
      bold: true, color: "7EC8F5", margin: 0 });
    s.addText(g[1], { x: 1.95, y: y + 0.52, w: 10.0, h: 0.45, fontFace: F, fontSize: 18,
      bold: true, color: C.white, margin: 0 });
    s.addText(g[2], { x: 1.95, y: y + 1.02, w: 10.0, h: 0.32, fontFace: F, fontSize: 12.5,
      color: "9FB8CE", margin: 0 });
    s.addText([
      { text: "실패 조건   ", options: { bold: true, fontSize: 12, color: "FF9E80" } },
      { text: g[3], options: { bold: true, fontSize: 12.5, color: "FFC94D" } },
    ], { x: 1.95, y: y + 1.38, w: 10.0, h: 0.34, fontFace: F, margin: 0 });
  });

  s.addText("그 외 보조 3건 — 질문 유형 게이트 · random 배분 대조군 · 선행연구가 남긴 열린 질문 검증", {
    x: 0.55, y: 5.72, w: 12.25, h: 0.34, fontFace: F, fontSize: 12, color: "8AA5BC", margin: 0 });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.22, w: 12.25, h: 0.95, rectRadius: 0.08,
    fill: { color: "1D3850" }, line: { color: "2E4E6B", width: 1 } });
  s.addText([
    { text: "중단 규칙을 먼저 정해두겠습니다 — A와 B가 모두 실패하면 이 주제는 접고 다른 방향으로 넘어가겠습니다.", options: { bold: true, fontSize: 12.5, color: "FFC94D", breakLine: true } },
    { text: "GPU 1장 · 기존 코드·데이터 전부 재사용 · 새로 만들 인프라 없음", options: { fontSize: 11, color: "9FB8CE" } },
  ], { x: 0.85, y: 6.32, w: 11.7, h: 0.8, fontFace: F, margin: 0, paraSpaceAfter: 4 });
  s.addNotes("게이트 A가 더 무겁습니다. 방해 이미지를 0층에서 그냥 지워버린 쪽이 깊이를 조절한 것보다 좋다면, 애초에 '깊이'라는 축을 쓸 이유가 없어집니다. 연구의 전제 자체가 걸린 시험이라 이걸 먼저 하겠습니다. 게이트 B는 자동화 가능성입니다 — 오늘 보고드린 위치 편향 문제를 다른 신호로 넘을 수 있는지 봅니다. 두 게이트 다 통과 기준 숫자는 실험 전에 먼저 못 박고 들어가겠습니다. 1주일이면 충분합니다. 인프라와 데이터가 이미 다 있어서 새로 만들 게 없습니다.");
}

// ===================== 부록 =====================
function appendix(title, imgs, notes) {
  const s = pres.addSlide();
  kicker(s, "APPENDIX");
  headline(s, title);
  if (imgs.img) s.addImage({ path: R + imgs.img, x: imgs.x, y: imgs.y, w: imgs.w, h: imgs.h });
  if (notes) s.addText(notes, { x: 0.55, y: 6.4, w: 12.2, h: 0.6, fontFace: F, fontSize: 11,
    color: C.gray, margin: 0 });
  return s;
}
appendix("질문 유형에 따라 최적 깊이가 정반대 — 두 스케일 모두",
  { img: "fig6_xcross_both_scales.png", x: 0.6, y: 1.6, w: 12.1, h: 4.15 },
  "R1: '두 이미지 모두에 X가 있나?' 정답 '아니오' — 2번 이미지를 반드시 확인해야 함. 3B 0.760→0.250(−51%p), 7B 0.950→0.540(−41%p)");
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX");
  headline(s, "계산량은 똑같이 두고 배분만 바꿨을 때 (어느 쪽이 방해인지 아는 조건)");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 12 };
  const cc = { fontSize: 12, color: C.navy, fill: { color: C.white } };
  const m = (t, o) => ({ text: t, options: Object.assign({}, cc, o || {}) });
  s.addTable([
    [m("", hd), m("방해 이미지", hd), m("정답 이미지", hd), m("총 계산량", hd), m("정확도", hd)],
    [m("일괄 (기존 방식)", { bold: true }), m("16층까지"), m("16층까지"),
     m("16 + 16 = 32", { bold: true }), m("0.550", { bold: true, color: C.red })],
    [m("차등 (우리)", { bold: true }), m("4층까지만", { color: C.blue }), m("28층까지", { color: C.blue }),
     m("4 + 28 = 32", { bold: true }), m("0.837", { bold: true, color: C.green })],
  ], { x: 1.3, y: 1.95, w: 10.7, h: 1.8, rowH: 0.6, fontFace: F, align: "center",
       valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  s.addText([
    { text: "총 계산량이 정확히 같은데 정확도는 28.7%p 차이난다 — 예산을 똑같이 나누는 것보다 필요한 쪽에 몰아주는 편이 낫다", options: { bullet: true, breakLine: true } },
    { text: "이유는 단순하다: 일괄 방식은 정답 이미지까지 16층에서 잘라버려 정작 필요한 정보를 함께 날린다", options: { bullet: true, breakLine: true } },
    { text: "이미지 순서를 뒤집어 재측정해도 이득의 80%가 유지됐다 (원순서 +34.2%p → 뒤집기 +27.3%p, 양방향 평균 +30.7%p)", options: { bullet: true, breakLine: true } },
    { text: "7B에서도 같은 방향 — 38.9% 절감 구간에서 0.802 vs 0.715 (+8.7%p). 무개입 기준선은 0.790", options: { bullet: true, breakLine: true } },
    { text: "한계: 비교 대상인 일괄 차단(0.550)이 무개입(0.790)보다도 낮은 약한 baseline이다. random 배분 대조군으로 보강해야 한다 (게이트 4)", options: { bullet: true, bold: true, color: C.red } },
  ], { x: 0.9, y: 4.1, w: 11.6, h: 2.6, fontFace: F, fontSize: 12, color: C.navy,
       margin: 0, paraSpaceAfter: 9 });
  s.addText("※ 어느 쪽이 방해인지 미리 알려준 조건(oracle)에서의 상한값이다 — 이것을 자동 판정하는 부분이 무너진 지점(본편 4번 슬라이드)", {
    x: 0.9, y: 6.85, w: 11.6, h: 0.4, fontFace: F, fontSize: 10.5, italic: true,
    color: C.gray, margin: 0 });
}


{
  const s = pres.addSlide();
  kicker(s, "APPENDIX");
  headline(s, "\"적응적\"이라는 표현은 못 쓴다 — 문항마다 깊이를 바꿀 필요가 없었다");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11.5 };
  const cc = { fontSize: 11.5, color: C.navy, fill: { color: C.white } };
  const m = (t, o) => ({ text: t, options: Object.assign({}, cc, o || {}) });
  s.addTable([
    [m("문항군", hd), m("모든 문항에 같은 층 하나", hd), m("문항마다 최적 층을 안다면", hd), m("차이", hd)],
    [m("셀 1 (n=150)", { bold: true }), m("0.933"), m("0.960"), m("+2.7%p", { bold: true, color: C.red })],
    [m("셀 2 (n=150)", { bold: true }), m("0.720"), m("0.747"), m("+2.7%p", { bold: true, color: C.red })],
  ], { x: 1.6, y: 1.85, w: 10.1, h: 1.7, rowH: 0.55, fontFace: F, align: "center",
       valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  s.addText([
    { text: "문항의 66%는 어느 층에서 끊어도 정답이라, 문항별로 최적화할 여지 자체가 거의 없다", options: { bullet: true, breakLine: true } },
    { text: "즉 필요한 것은 '문항마다 조절하는 컨트롤러'가 아니라 '고정 스케줄 하나 + 어느 이미지가 방해인지'뿐이다", options: { bullet: true, breakLine: true } },
    { text: "선행연구도 같은 방향 — γ-MoD(ICLR'25)는 깊이 여유도를 오프라인 50샘플로 한 번 정하고 고정한다", options: { bullet: true, breakLine: true } },
    { text: "→ 나쁜 소식: 연구 이름의 \"적응적\"을 못 쓴다.  좋은 소식: 방법이 훨씬 단순해진다", options: { bullet: true, bold: true } },
  ], { x: 1.0, y: 3.9, w: 11.4, h: 2.3, fontFace: F, fontSize: 12.5, color: C.navy,
       margin: 0, paraSpaceAfter: 9 });
  s.addText("※ '이미지 간' 차등(방해는 얕게, 관련은 깊게)은 이것과 별개이며 유효하다 — 본편 참조", {
    x: 1.0, y: 6.3, w: 11.4, h: 0.4, fontFace: F, fontSize: 11, italic: true, color: C.gray, margin: 0 });
}

appendix("컨트롤러 신호를 층·head별로 전수 탐색한 결과",
  { img: "fig4_controller_feature_sweep.png", x: 0.8, y: 1.7, w: 11.7, h: 4.3 },
  "순서를 뒤집어도 맞는 head: 얕은 층 0.31~0.51(무작위), layer 22에서 0.882가 최고. 개입이 유효한 구간은 16층 이전");
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX");
  headline(s, "재현성 · 한계");
  s.addText([
    { text: "환경: RTX 3090/A6000 1장 · torch 2.5.1+cu121 · transformers 4.52.3 · Qwen2.5-VL-3B(36층)/7B(28층) · BF16", options: { bullet: true, breakLine: true } },
    { text: "규모: 본 실험 600문항×10조건 + 확장 실험 약 25,000회 forward · seed 42 · 판정 기준 사전 동결 · 오류 중단 0건", options: { bullet: true, breakLine: true } },
    { text: "코드·데이터·raw 결과 전부 버전 관리 (github.com/hsmai/Source-Depth)", options: { bullet: true, breakLine: true } },
    { text: "한계: 이미지 2장 세팅 · 단일 물체 yes/no 질문 중심 · POPE는 7B에게 천장(단일 94.7%) · 실측 속도는 프로토타입 · 컨트롤러 결론은 'training-free × 마지막 토큰 attention' 조건 한정", options: { bullet: true, bold: true } },
  ], { x: 0.7, y: 2.0, w: 12.0, h: 3.5, fontFace: F, fontSize: 13, color: C.navy,
    margin: 0, paraSpaceAfter: 14 });
}

pres.writeFile({ fileName: "/Users/hansangmin/Source-Depth/meeting/_generated/deck_compact.pptx" })
  .then(() => console.log("COMPACT DECK WRITTEN"));
