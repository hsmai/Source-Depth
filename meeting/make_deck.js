const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5

const R = "/Users/hansangmin/Source-Depth/results/";
const C = {
  navy: "1F3B57", darkbg: "142638", blue: "1F77B4", red: "D62728",
  orange: "E8890C", green: "2E8B57", gray: "6B7280", light: "EFF4F9",
  lightred: "FBEAEA", lightgray: "F3F4F6", white: "FFFFFF", line: "D5DEE8",
  lightgreen: "E9F4EE", lightorange: "FDF3E3",
};
const F = "Arial";
const W = 13.33;

// ---------- helpers ----------
function kicker(s, txt, dark) {
  s.addText(txt, { x: 0.55, y: 0.26, w: 10.5, h: 0.32, fontFace: F, fontSize: 11.5,
    bold: true, color: dark ? "9FB8CE" : C.blue, charSpacing: 1, margin: 0 });
}
function headline(s, txt, dark, wOverride) {
  s.addText(txt, { x: 0.55, y: 0.56, w: wOverride || 12.2, h: 0.8, fontFace: F,
    fontSize: 22, bold: true, color: dark ? C.white : C.navy, margin: 0 });
}
function takeaway(s, txt) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.62, w: 12.25, h: 0.62,
    rectRadius: 0.08, fill: { color: C.navy } });
  s.addText(txt, { x: 0.85, y: 6.62, w: 11.75, h: 0.62, fontFace: F, fontSize: 13,
    bold: true, color: C.white, margin: 0, valign: "middle" });
}
function tag(s, txt, fill) {
  const w = 0.28 + txt.length * 0.105;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: W - 0.55 - w, y: 0.28, w: w, h: 0.34,
    fill: { color: fill }, rectRadius: 0.17 });
  s.addText(txt, { x: W - 0.55 - w, y: 0.28, w: w, h: 0.34, align: "center",
    fontFace: F, fontSize: 10.5, bold: true, color: C.white, margin: 0 });
}
function pendTag(s) { tag(s, "미확정 · 내일 오전 업데이트", C.orange); }
function readNote(s, x, y, w, txt) {   // 그림 "읽는 법" 캡션
  s.addText([{ text: "읽는 법  ", options: { bold: true, color: C.blue } },
    { text: txt, options: { color: C.gray } }],
    { x, y, w, h: 0.55, fontFace: F, fontSize: 10.5, margin: 0 });
}
function bar(s, x, yBase, w, hMax, frac, color, valTxt, label) {
  const bh = Math.max(0.04, hMax * frac);
  s.addShape(pres.shapes.RECTANGLE, { x, y: yBase - bh, w, h: bh, fill: { color } });
  s.addText(valTxt, { x: x - 0.35, y: yBase - bh - 0.38, w: w + 0.7, h: 0.34, align: "center",
    fontFace: F, fontSize: 15, bold: true, color, margin: 0 });
  s.addText(label, { x: x - 0.55, y: yBase + 0.08, w: w + 1.1, h: 0.75, align: "center",
    fontFace: F, fontSize: 10.5, color: C.navy, margin: 0 });
}

// =====================================================================
// S1 — 표지 (dark): 문장으로 말하는 3개의 결과
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.darkbg };
  s.addText("SOURCEDEPTH · 검증 실험(PHASE 0) 결과 보고 · 2026-08-12 · IMML Lab 한상민", { x: 0.6, y: 0.5,
    w: 11, h: 0.32, fontFace: F, fontSize: 11.5, bold: true, color: "8AA5BC", charSpacing: 1, margin: 0 });
  s.addText("이미지마다 계산 깊이를 다르게 주면,\n멀티이미지 환각이 줄고 계산도 준다", { x: 0.6, y: 1.15,
    w: 12.2, h: 1.9, fontFace: F, fontSize: 32, bold: true, color: C.white, margin: 0, lineSpacingMultiple: 1.15 });
  s.addText("이 가설이 성립하는지 — 24시간 검증 실험에서 얻은 숫자로 보고드립니다.", {
    x: 0.6, y: 3.1, w: 12, h: 0.45, fontFace: F, fontSize: 15, color: "AFC6DA", margin: 0 });
  const cards = [
    ["문제는 실재했습니다", "질문과 무관한 이미지 1장이\n멀쩡하던 답의 21%를 뒤집었습니다", "(같은 조건의 대조군에서는 0%)"],
    ["해법도 작동했습니다", "4층 이후 그 이미지를 차단하는 것만으로\n뒤집힌 답의 81%가 되살아났습니다", "(부작용은 3.7% — 회복이 22배)"],
    ["그리고 핵심 발견 —", "질문 종류에 따라 최적의 깊이가\n정반대라는 것을 확인했습니다", "(고정 깊이로는 불가능 → 적응 배분 필요)"],
  ];
  cards.forEach((c, i) => {
    const x = 0.6 + i * 4.15, y = 3.85, w = 3.95, h = 2.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: "1D3850" }, line: { color: "2E4E6B", width: 1 } });
    s.addText(c[0], { x: x + 0.25, y: y + 0.22, w: w - 0.5, h: 0.45, fontFace: F, fontSize: 15.5,
      bold: true, color: "7EC8F5", margin: 0 });
    s.addText(c[1], { x: x + 0.25, y: y + 0.8, w: w - 0.5, h: 1.3, fontFace: F, fontSize: 13.5,
      color: C.white, margin: 0, lineSpacingMultiple: 1.25 });
    s.addText(c[2], { x: x + 0.25, y: y + 2.2, w: w - 0.5, h: 0.5, fontFace: F, fontSize: 11,
      color: "9FB8CE", margin: 0 });
  });
  s.addNotes("오늘 보고는 한 문장입니다 — '이미지마다 계산 깊이를 다르게 주면 환각이 줄고 계산도 준다', 이 가설이 실험에서 성립했습니다. 세 개의 숫자(21% 오염, 81% 회복, 정반대 최적 깊이)로 차례로 보여드리겠습니다.");
}

// =====================================================================
// S2 — 오늘의 구조: 질문 3개
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "오늘 보고의 구조");
  headline(s, "\"이 연구가 성립하는가\"를 세 가지 질문으로 나눠 검증했습니다");
  const qs = [
    ["Q1", "문제가 진짜 있는가?", "이미지를 하나 더 넣으면\n정말 답이 오염되는가", "✓ 그렇다", C.green, "슬라이드 5"],
    ["Q2", "해법이 작동하는가?", "'중간부터 차단'이 오염을 고치는가,\n그 효과는 인과적인가", "✓ 그렇다", C.green, "슬라이드 6–8"],
    ["Q3", "실제로 만들 수 있는가?", "무엇을 차단할지 스스로 알 수 있는가,\n실제로 빨라지는가", "◐ 절반 확인\n(나머지 검증 중)", C.orange, "슬라이드 9"],
  ];
  qs.forEach((q, i) => {
    const x = 0.55 + i * 4.25, y = 1.75, w = 4.0, h = 4.4;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: C.light }, line: { color: C.line, width: 1 } });
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.25, w: 0.62, h: 0.62, fill: { color: C.navy } });
    s.addText(q[0], { x: x + 0.25, y: y + 0.25, w: 0.62, h: 0.62, align: "center", valign: "middle",
      fontFace: F, fontSize: 16, bold: true, color: C.white, margin: 0 });
    s.addText(q[1], { x: x + 1.05, y: y + 0.33, w: w - 1.25, h: 0.5, fontFace: F, fontSize: 15.5,
      bold: true, color: C.navy, margin: 0 });
    s.addText(q[2], { x: x + 0.28, y: y + 1.15, w: w - 0.56, h: 1.0, fontFace: F, fontSize: 12.5,
      color: C.gray, margin: 0, lineSpacingMultiple: 1.2 });
    s.addText(q[3], { x: x + 0.28, y: y + 2.35, w: w - 0.56, h: 1.15, fontFace: F, fontSize: 21,
      bold: true, color: q[4], margin: 0, lineSpacingMultiple: 1.1 });
    s.addText("답은 " + q[5] + "에서", { x: x + 0.28, y: y + 3.75, w: w - 0.56, h: 0.4, fontFace: F,
      fontSize: 11, italic: true, color: C.gray, margin: 0 });
  });
  takeaway(s, "→ 세 질문 전부 실측 숫자로 답합니다 — \"그래서 이 연구를 계속할 가치가 있는가\"가 오늘의 결론입니다 (마지막 슬라이드)");
  s.addNotes("발표 구조를 먼저 드립니다. 성립 여부를 세 질문으로 쪼갰고, 각 질문에 실험 숫자로 답한 뒤 마지막에 종합 결론과 다음 계획을 말씀드립니다.");
}

// =====================================================================
// S3 — 문제 설명
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "배경 — 무엇이 문제인가");
  headline(s, "이미지를 한 장 더 넣었을 뿐인데, 모델은 답의 '출처'를 섞기 시작한다");
  // 좌: 도식
  const dx = 0.55, dy = 1.62;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: dx, y: dy, w: 2.5, h: 1.4, rectRadius: 0.08,
    fill: { color: C.light }, line: { color: C.blue, width: 2 } });
  s.addText([{ text: "이미지 1 (질문 대상)", options: { bold: true, color: C.navy, fontSize: 12, breakLine: true } },
    { text: "파란 모자", options: { color: C.blue, fontSize: 15, bold: true } }],
    { x: dx, y: dy + 0.28, w: 2.5, h: 0.85, align: "center", fontFace: F, margin: 0 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: dx + 2.8, y: dy, w: 2.5, h: 1.4, rectRadius: 0.08,
    fill: { color: C.light }, line: { color: C.red, width: 2 } });
  s.addText([{ text: "이미지 2 — \"방해 이미지\"", options: { bold: true, color: C.red, fontSize: 12, breakLine: true } },
    { text: "빨간 모자", options: { color: C.red, fontSize: 15, bold: true } }],
    { x: dx + 2.8, y: dy + 0.28, w: 2.5, h: 0.85, align: "center", fontFace: F, margin: 0 });
  s.addText("질문: \"1번 이미지 사람의 모자는 무슨 색?\"", { x: dx, y: dy + 1.6, w: 5.3, h: 0.38,
    align: "center", fontFace: F, fontSize: 13, bold: true, color: C.navy, margin: 0 });
  s.addShape(pres.shapes.DOWN_ARROW, { x: dx + 2.45, y: dy + 2.02, w: 0.4, h: 0.42, fill: { color: C.gray } });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: dx + 1.0, y: dy + 2.55, w: 3.3, h: 0.95, rectRadius: 0.1,
    fill: { color: C.lightred }, line: { color: C.red, width: 1.5 } });
  s.addText([{ text: "모델의 답: \"빨간색\"  ✗", options: { bold: true, fontSize: 15, color: C.red, breakLine: true } },
    { text: "→ 옆 이미지의 정보를 가져다 답함", options: { fontSize: 10.5, color: C.gray } }],
    { x: dx + 1.0, y: dy + 2.63, w: 3.3, h: 0.85, align: "center", fontFace: F, margin: 0 });
  // 용어 정의
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: dx, y: 5.45, w: 5.85, h: 0.95, rectRadius: 0.08,
    fill: { color: C.lightgray } });
  s.addText([{ text: "이 발표의 용어 두 개", options: { bold: true, fontSize: 11, color: C.navy, breakLine: true } },
    { text: "방해 이미지 = 질문과 무관한 이미지  ·  차단 = 특정 층부터 모델이 그 이미지를 참조하지 못하게 막는 것", options: { fontSize: 10.5, color: C.gray } }],
    { x: dx + 0.22, y: 5.53, w: 5.5, h: 0.8, fontFace: F, margin: 0, paraSpaceAfter: 3 });
  // 우: 실측
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.75, y: 1.62, w: 6.05, h: 4.78, rectRadius: 0.1,
    fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("이 현상을 저희 실험으로 재보면 —", { x: 7.05, y: 1.85, w: 5.5, h: 0.35,
    fontFace: F, fontSize: 13, bold: true, color: C.gray, margin: 0 });
  s.addText("같은 질문 · 같은 정답. 방해 이미지 1장만 추가", { x: 7.05, y: 2.25, w: 5.5, h: 0.35,
    fontFace: F, fontSize: 12.5, color: C.navy, margin: 0 });
  s.addText([
    { text: "89.3%", options: { fontSize: 44, bold: true, color: C.blue } },
    { text: "  →  ", options: { fontSize: 30, color: C.gray } },
    { text: "72.0%", options: { fontSize: 44, bold: true, color: C.red } },
  ], { x: 7.05, y: 2.75, w: 5.5, h: 1.0, fontFace: F, margin: 0 });
  s.addText("정답률 17.3%p 하락 — 이미지 600문항 실측", { x: 7.05, y: 3.85, w: 5.5, h: 0.4,
    fontFace: F, fontSize: 14, bold: true, color: C.red, margin: 0 });
  s.addText([
    { text: "이미 학계가 이름 붙인 문제입니다 (cross-image leakage, FOCUS 2025 등)", options: { bullet: true, breakLine: true } },
    { text: "기존 해법들은 계산을 '더' 써서 고칩니다 — 예: 이미지 N장이면 forward를 N+1번", options: { bullet: true } },
  ], { x: 7.05, y: 4.4, w: 5.55, h: 1.8, fontFace: F, fontSize: 12, color: C.navy,
    margin: 0, paraSpaceAfter: 8 });
  takeaway(s, "→ 문제 상황: 이미지가 늘면 출처가 섞여 정답률이 크게 떨어진다 — 그리고 기존 해법은 전부 '계산을 더 쓰는' 방향이다");
  s.addNotes("문제 자체는 알려져 있습니다. 저희의 차별점은 '어느 깊이에서 섞이는가'를 재고, '계산을 줄이면서' 고치는 것입니다.");
}

// =====================================================================
// S4 — 아이디어
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "아이디어");
  headline(s, "이미지들이 섞이는 통로는 층마다 한 번의 attention뿐 — 그 통로를 중간부터 닫아보자");
  const panels = [
    { x: 1.0, title: "지금의 모델: 끝까지 계속 섞임", blockFrom: 99,
      cap: "층이 깊어질수록 출처 오염이 누적된다", col: C.red },
    { x: 7.2, title: "제안: L층부터 방해 이미지 차단", blockFrom: 2,
      cap: "오염 통로를 닫고, 그 이미지의 남은 계산도 아낀다", col: C.green },
  ];
  panels.forEach(p => {
    s.addText(p.title, { x: p.x, y: 1.58, w: 5.1, h: 0.35, fontFace: F, fontSize: 13.5,
      bold: true, color: C.navy, margin: 0, align: "center" });
    for (let i = 0; i < 5; i++) {
      const y = 1.98 + i * 0.58;
      const blocked = i >= p.blockFrom;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: p.x, y, w: 5.1, h: 0.48, rectRadius: 0.06,
        fill: { color: blocked ? C.lightgray : C.light }, line: { color: C.line, width: 0.75 } });
      s.addText(`${i + 1}층`, { x: p.x + 0.12, y, w: 0.75, h: 0.48, fontFace: F, fontSize: 11,
        bold: true, color: C.gray, margin: 0, valign: "middle" });
      s.addText("질문 대상 ●", { x: p.x + 0.95, y, w: 1.7, h: 0.48, fontFace: F, fontSize: 11.5,
        bold: true, color: C.blue, margin: 0, valign: "middle" });
      s.addText(blocked ? "차단" : "⇄ 섞임", { x: p.x + 2.6, y, w: 1.0, h: 0.48, align: "center",
        fontFace: F, fontSize: 11.5, bold: true, color: blocked ? C.green : C.red, margin: 0, valign: "middle" });
      s.addText(blocked ? "방해 ✕ (계산 생략)" : "방해 ●", { x: p.x + 3.6, y, w: 1.5, h: 0.48, fontFace: F,
        fontSize: 10.5, bold: true, color: blocked ? C.gray : C.red, margin: 0, valign: "middle" });
    }
    s.addText(p.cap, { x: p.x, y: 4.95, w: 5.1, h: 0.62, align: "center", fontFace: F,
      fontSize: 11.5, bold: true, color: p.col, margin: 0 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.65, w: 12.25, h: 0.85, rectRadius: 0.08,
    fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText([
    { text: "이 차단은 '어림 억제'가 아닙니다 — 수학적으로 그 이미지가 없는 것과 동일합니다.  ", options: { bold: true, color: C.navy } },
    { text: "한계도 있습니다: L층 이전에 이미 새어나간 정보는 못 막습니다 (실측해 보니 그 잔여분은 오답의 19% 이하였습니다).", options: { color: C.gray } },
  ], { x: 0.85, y: 5.65, w: 11.7, h: 0.85, fontFace: F, fontSize: 12, margin: 0, valign: "middle" });
  takeaway(s, "→ 가설: 무관한 이미지는 얕게, 필요한 이미지는 깊게 — \"이미지별로 다른 깊이\"가 정확도와 효율을 동시에 잡는다");
  s.addNotes("차단은 attention 계산에서 그 이미지 토큰을 제외하는 것이라, 수학적으로 '없는 것'과 동일합니다. 다만 차단 이전 층에서 이미 새어나간 정보는 못 막는데, 그 잔여분도 실측했고 오답의 19% 이하였습니다.");
}

// =====================================================================
// S5 — 실험 설계
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "검증 방법 — 실험을 어떻게 짰는가");
  headline(s, "오염이 '생길 수밖에 없는' 문항과 '안 생기는' 문항을 나란히 놓고 비교했다");
  const design = [
    ["①", "이렇게 묻습니다", "\"첫 번째 이미지에 ○○이 있나요?\" (예/아니오)\nCOCO 사진 + 공인 검증 문제(POPE) 600문항"],
    ["②", "오염을 '유발'하는 조건", "방해 이미지에 바로 그 ○○이 들어있는 문항\n— 모델이 헷갈릴 재료를 일부러 제공"],
    ["③", "대조군", "방해 이미지에 ○○이 없는 문항\n— 여기서도 답이 뒤집히면 오염이 아닌 다른 원인"],
  ];
  design.forEach((d, i) => {
    const y = 1.72 + i * 1.36;
    s.addShape(pres.shapes.OVAL, { x: 0.55, y, w: 0.55, h: 0.55, fill: { color: C.navy } });
    s.addText(d[0], { x: 0.55, y, w: 0.55, h: 0.55, align: "center", valign: "middle",
      fontFace: F, fontSize: 15, bold: true, color: C.white, margin: 0 });
    s.addText(d[1], { x: 1.3, y: y - 0.02, w: 5.3, h: 0.38, fontFace: F, fontSize: 13.5,
      bold: true, color: C.navy, margin: 0 });
    s.addText(d[2], { x: 1.3, y: y + 0.38, w: 5.3, h: 0.9, fontFace: F, fontSize: 11.5,
      color: C.gray, margin: 0, lineSpacingMultiple: 1.15 });
  });
  // 우: 차단 조건
  s.addText("그리고 문항마다 '차단 깊이'를 바꿔가며 10번씩 측정", { x: 7.0, y: 1.72, w: 5.8, h: 0.38,
    fontFace: F, fontSize: 13.5, bold: true, color: C.navy, margin: 0 });
  const conds = [
    ["차단 없음", "기준선 — 지금의 모델 그대로", C.gray],
    ["4층부터 ~ 24층부터", "차단 시작 층을 6단계로 변화", C.blue],
    ["처음부터 완전 차단", "이미지를 아예 안 준 것과 비교하는 상한", C.blue],
    ["반대로 '질문 대상'을 차단", "검증용 — 이게 무너지지 않으면 가짜", C.orange],
  ];
  conds.forEach((c, i) => {
    const y = 2.2 + i * 0.92;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.0, y, w: 5.8, h: 0.8, rectRadius: 0.08,
      fill: { color: i === 3 ? C.lightorange : C.light }, line: { color: c[2], width: 1 } });
    s.addText([{ text: c[0] + "   ", options: { bold: true, fontSize: 12.5, color: C.navy } },
      { text: c[1], options: { fontSize: 11, color: C.gray } }],
      { x: 7.25, y, w: 5.35, h: 0.8, fontFace: F, margin: 0, valign: "middle" });
  });
  s.addText("+ 판정 기준(무엇이 나오면 성공/실패인지)은 실험 전에 문서로 못 박아 두었습니다 — 결과를 보고 바꾸지 않음", {
    x: 0.55, y: 6.0, w: 12.2, h: 0.4, fontFace: F, fontSize: 11.5, italic: true, color: C.gray, margin: 0 });
  takeaway(s, "→ 이렇게 짜면 \"답이 뒤집히는 것\"이 우연인지, 방해 이미지 때문인지가 숫자로 구분된다");
  s.addNotes("설계의 핵심은 대조군입니다. 방해 이미지에 물건이 있는 문항과 없는 문항을 똑같이 150개씩 두면, 뒤집힘이 물건 때문인지 아닌지 바로 구분됩니다. 그리고 판정 기준을 실험 전에 동결했습니다.");
}

// =====================================================================
// S6 — 신뢰성
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "검증 방법 — 측정을 믿을 수 있는가");
  headline(s, "본 실험 전에, 측정 장치가 멀쩡한지부터 3가지로 점검했다");
  const checks = [
    ["차단 장치가 진짜 작동하나?", "98.3%", "방해 이미지를 '완전 차단'한 결과가\n아예 안 준 결과와 예측 98.3% 일치\n(+ 차단된 층의 참조량이 정확히 0임을 관측)"],
    ["채점이 멀쩡한가?", "85.5%", "이미지 1장만 줬을 때 정답률 85.5%\n— 같은 모델의 공개 보고치(~80%대)와 일치"],
    ["마스킹이 흉내는 아닌가?", "100%", "토큰을 실제로 삭제한 별도 구현과\n예측이 100% 일치 — 등가성 검증"],
  ];
  checks.forEach((c, i) => {
    const x = 0.55 + i * 4.25, y = 1.8, w = 4.0, h = 3.55;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: C.lightgreen }, line: { color: C.green, width: 1 } });
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.25, w: 0.5, h: 0.5, fill: { color: C.green } });
    s.addText("✓", { x: x + 0.25, y: y + 0.25, w: 0.5, h: 0.5, align: "center", valign: "middle",
      fontFace: F, fontSize: 18, bold: true, color: C.white, margin: 0 });
    s.addText(c[0], { x: x + 0.9, y: y + 0.28, w: w - 1.1, h: 0.75, fontFace: F, fontSize: 13.5,
      bold: true, color: C.navy, margin: 0 });
    s.addText(c[1], { x: x + 0.28, y: y + 1.15, w: w - 0.56, h: 0.9, fontFace: F, fontSize: 40,
      bold: true, color: C.green, margin: 0 });
    s.addText(c[2], { x: x + 0.28, y: y + 2.1, w: w - 0.56, h: 1.4, fontFace: F, fontSize: 11,
      color: C.navy, margin: 0, lineSpacingMultiple: 1.2 });
  });
  s.addText("규모: 600문항 × 10조건 = 6,000회 측정 · GPU 1장 · 29분 · 난수 고정(seed 42) · 오류 중단 0건", {
    x: 0.55, y: 5.65, w: 12.2, h: 0.4, fontFace: F, fontSize: 12, bold: true, color: C.gray, margin: 0 });
  takeaway(s, "→ 이후의 모든 숫자는 이 3가지 점검을 통과한 측정에서 나온 실측값이다");
  s.addNotes("측정 장치 자체를 먼저 검증했습니다. 특히 세 번째 — 마스킹이 흉내가 아니라 토큰을 실제로 삭제한 구현과 100% 같은 예측을 낸다는 것까지 확인했습니다.");
}

// =====================================================================
// S7 — Q1 결과
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "질문 ① — 문제가 진짜 있는가?");
  headline(s, "방해 이미지에 '그 물건'이 있을 때만, 멀쩡하던 답이 뒤집혔다");
  // 좌: 큰 막대 2개
  s.addText("답이 뒤집힌 문항의 비율 (150문항 중)", { x: 0.7, y: 1.72, w: 5.2, h: 0.32,
    fontFace: F, fontSize: 12.5, bold: true, color: C.navy, margin: 0 });
  const yB = 4.9, hM = 2.5;
  bar(s, 1.45, yB, 1.3, hM, 0.213 / 0.25, C.red, "21.3%", "방해 이미지에\n물건 있음 (오염 유발)");
  bar(s, 3.75, yB, 1.3, hM, 0.003, C.gray, "0.0%", "물건 없음\n(대조군)");
  s.addShape(pres.shapes.LINE, { x: 0.9, y: yB, w: 5.0, h: 0, line: { color: C.navy, width: 1.25 } });
  // 우: '뒤집힘'이 무슨 뜻인지
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.6, y: 1.75, w: 6.2, h: 2.6, rectRadius: 0.1,
    fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("\"답이 뒤집힌다\"는 것의 의미", { x: 6.9, y: 1.95, w: 5.6, h: 0.35,
    fontFace: F, fontSize: 13, bold: true, color: C.navy, margin: 0 });
  s.addText([
    { text: "이미지 1장일 때:   \"○○ 있나요?\" → \"없다\"  ", options: { fontSize: 13, color: C.navy } },
    { text: "정답 ○", options: { fontSize: 13, bold: true, color: C.green, breakLine: true } },
    { text: "방해 이미지 추가:  같은 질문 → \"있다\"  ", options: { fontSize: 13, color: C.navy } },
    { text: "오답 ✗", options: { fontSize: 13, bold: true, color: C.red, breakLine: true } },
    { text: "— 방해 이미지 속 물건을 '첫 번째 이미지에 있다'고 착각", options: { fontSize: 11.5, color: C.gray } },
  ], { x: 6.9, y: 2.4, w: 5.7, h: 1.8, fontFace: F, margin: 0, paraSpaceAfter: 10 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.6, y: 4.6, w: 6.2, h: 1.55, rectRadius: 0.1,
    fill: { color: C.lightgray } });
  s.addText([
    { text: "대조군이 0%라는 것이 핵심입니다", options: { bold: true, fontSize: 13, color: C.navy, breakLine: true } },
    { text: "방해 이미지에 물건이 없으면 답은 전혀 뒤집히지 않았습니다. 즉 뒤집힘은 우연도, 단순히 '이미지가 늘어서'도 아니고 — 정확히 그 물건이 넘어와서 생긴 오염입니다.", options: { fontSize: 11.5, color: C.gray } },
  ], { x: 6.9, y: 4.72, w: 5.7, h: 1.35, fontFace: F, margin: 0, paraSpaceAfter: 5 });
  takeaway(s, "→ 질문 ①의 답: 그렇다 — 오염은 실재한다 (뒤집힘 21.3% vs 대조군 0.0%, 우연으로 설명 불가)");
  s.addNotes("대조군 0%가 이 슬라이드의 핵심입니다. 물건이 없으면 전혀 뒤집히지 않으니, 뒤집힘은 정확히 방해 이미지의 물건이 넘어와 생긴 오염입니다. 반대 방향 오염(있는 걸 없다고)도 쟀는데 약했고, 그 상세는 부록에 있습니다.");
}

// =====================================================================
// S8 — Q2 회복
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "질문 ② — 해법이 작동하는가?  (1/3: 고쳐지는가)");
  headline(s, "4층 이후 차단만으로, 오염된 오답의 81%가 되살아났다");
  s.addImage({ path: R + "fig1_accuracy_vs_L.png", x: 0.55, y: 1.72, w: 7.6, h: 3.11 });
  readNote(s, 0.55, 4.9, 7.6, "가로축 = 차단을 시작하는 층(왼쪽일수록 일찍 차단) · 빨간 점선 = 차단 없음(72%) · 왼쪽 패널이 위 질문 ①의 문항들");
  const cards = [
    ["고쳐진 오답 81%  vs  새로 생긴 오답 3.7%", "부작용의 22배 — '지우기만 한 것'이 아니라 회복"],
    ["우연일 확률 p = 6×10⁻⁷", "같은 문항을 짝지어 비교하는 통계 검정(McNemar)"],
    ["차단 = 계산 절약이기도", "방해 이미지 계산의 89%를 건너뜀 (이론상 전체의 42%)"],
  ];
  cards.forEach((c, i) => {
    const y = 1.8 + i * 1.32;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.45, y, w: 4.35, h: 1.16, rectRadius: 0.08,
      fill: { color: C.light }, line: { color: C.line, width: 1 } });
    s.addText([{ text: c[0], options: { bold: true, fontSize: 12.5, color: C.navy, breakLine: true } },
      { text: c[1], options: { fontSize: 10.5, color: C.gray } }],
      { x: 8.68, y: y + 0.1, w: 3.95, h: 1.0, fontFace: F, margin: 0, paraSpaceAfter: 4 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.32, w: 12.25, h: 1.12, rectRadius: 0.08,
    fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText([
    { text: "\"답을 '없다' 쪽으로 민 것 아닌가?\" — 아닙니다. 오염이 있던 문항군만 오르고, 없던 대조군은 오르지 않았습니다.", options: { bold: true, fontSize: 12.5, color: C.navy, breakLine: true } },
    { text: "오염 유발 문항군 72.0% → 92.0% (+20.0%p)   vs   같은 정답('없다')이지만 오염 없는 대조군 98.0% → 96.0% (−2.0%p)", options: { fontSize: 12, color: C.gray } },
  ], { x: 0.85, y: 5.44, w: 11.7, h: 0.95, fontFace: F, margin: 0, paraSpaceAfter: 5 });
  takeaway(s, "→ 차단은 오염을 부작용 없이 고친다 — 그리고 고치는 동시에 계산을 아낀다 (이 연구의 핵심 약속이 실측됨)");
  s.addNotes("회복 81% 대 부작용 3.7%, 22배입니다. 그리고 차단 결과가 이미지 1장만 준 것보다 높다는 것 — '얕게 차단하는 것이 더 싸면서 더 정확하다'는 제안서의 문장이 그대로 실측됐습니다.");
}

// =====================================================================
// S9 — Q2 인과
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "질문 ② — 해법이 작동하는가?  (2/3: 효과가 진짜인가)");
  headline(s, "확인 사살 — 반대로 '질문 대상'을 차단하면 무너져야 한다. 실제로 무너졌다");
  s.addImage({ path: R + "aux_chartC_negative_control.png", x: 0.55, y: 1.75, w: 7.0, h: 4.0 });
  readNote(s, 0.55, 5.8, 7.0, "보라 막대 = 질문 대상 이미지를 차단한 경우. 모델에게는 방해 이미지만 보이는 상태");
  const cards = [
    ["정답률 0.79 → 0.50 으로 붕괴", "우연일 확률 10⁻³⁸ — 사실상 0", C.red],
    ["답이 '보이는 이미지'를 그대로 따라감", "질문 대상을 가리면 방해 이미지 기준으로 답함 — 차단이 구조적으로 완전하다는 뜻", C.navy],
    ["방향을 뒤집으면 효과도 뒤집힘", "= 회복 효과는 상관이 아니라 인과", C.green],
  ];
  cards.forEach((c, i) => {
    const y = 1.85 + i * 1.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.85, y, w: 4.95, h: 1.3, rectRadius: 0.08,
      fill: { color: C.light }, line: { color: c[2], width: 1.25 } });
    s.addText([{ text: c[0], options: { bold: true, fontSize: 13.5, color: c[2], breakLine: true } },
      { text: c[1], options: { fontSize: 10.5, color: C.gray } }],
      { x: 8.08, y: y + 0.1, w: 4.5, h: 1.12, fontFace: F, margin: 0, paraSpaceAfter: 4 });
  });
  takeaway(s, "→ 질문 ②의 답 (2/3): 회복은 진짜다 — 차단 방향을 뒤집자 효과도 뒤집혔다 (인과 확인)");
  s.addNotes("'그 회복이 우연 아니냐'에 대한 답입니다. 질문 대상을 반대로 차단하면 정답률이 무너져야 진짜인데, 실제로 0.79에서 0.50으로 무너졌고 답이 정확히 '보이는 이미지'를 따라갔습니다.");
}

// =====================================================================
// S10 — Q2 X자 ★
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "질문 ② — 해법이 작동하는가?  (3/3: 오늘의 핵심 그림)");
  headline(s, "같은 차단인데 — 한 장에 대한 질문은 좋아지고, 두 장을 비교하는 질문은 무너진다");
  s.addImage({ path: R + "fig3_opposite_depth_policies.png", x: 1.55, y: 1.62, w: 7.5, h: 4.41 });
  const notes = [
    ["파란 곡선 ▲ +21%p", "\"1번 이미지에 ○○ 있나?\"\n— 일찍 차단할수록 정확", C.blue],
    ["빨간 곡선 ▼ −51%p", "\"두 이미지 '모두'에 ○○ 있나?\"\n— 두 장을 봐야 하므로 차단하면 붕괴", C.red],
    ["같은 구간(20~24층)에서 전환", "두 장을 잇는 계산과 오염이\n같은 층에서 일어난다는 뜻", C.orange],
  ];
  notes.forEach((n, i) => {
    const y = 1.75 + i * 1.5;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.25, y, w: 3.55, h: 1.35, rectRadius: 0.1,
      fill: { color: C.white }, line: { color: n[2], width: 1.5 } });
    s.addText([{ text: n[0], options: { bold: true, fontSize: 13.5, color: n[2], breakLine: true } },
      { text: n[1], options: { fontSize: 10.5, color: C.gray } }],
      { x: 9.45, y: y + 0.1, w: 3.2, h: 1.18, fontFace: F, margin: 0, paraSpaceAfter: 4 });
  });
  readNote(s, 1.55, 6.05, 8.5, "신규 300문항 실험 · 가로축 = 차단 시작 층 — 왼쪽(일찍 차단)에서 두 곡선의 격차가 72%p까지 벌어짐");
  takeaway(s, "→ 하나의 고정 깊이로는 두 질문을 동시에 만족할 수 없다 — \"이미지·질문마다 다른 깊이\"가 유일한 해법 = 이 연구가 필요한 이유");
  s.addNotes("오늘 가장 중요한 그림입니다. 같은 개입인데 질문 유형에 따라 +21과 -51로 완전히 반대입니다. 즉 어떤 고정 깊이를 골라도 한쪽을 망칩니다. 이미지와 질문마다 깊이를 다르게 주는 것 외에 해법이 없고, 그게 바로 이 연구입니다. 덤으로 — 두 전환이 같은 층에서 일어난다는 것도 발견했는데, 관계 추론과 출처 오염이 같은 계산의 양면이라는 뜻입니다.");
}

// =====================================================================
// S11 — Q3 실용화
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "질문 ③ — 실제로 만들 수 있는가?");
  pendTag(s);
  headline(s, "\"무엇을 차단할지\"는 8층에서 이미 알 수 있고, 속도 이득도 실측으로 확인했다", false, 10.2);
  // 좌: 컨트롤러
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 1.72, w: 6.05, h: 3.4, rectRadius: 0.1,
    fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("재료 1 — 판단 신호가 모델 안에 이미 있다", { x: 0.85, y: 1.9, w: 5.5, h: 0.4,
    fontFace: F, fontSize: 14, bold: true, color: C.navy, margin: 0 });
  s.addText([
    { text: "질문과 관련된 이미지가 어느 쪽인지, 모델 내부의 attention 신호 하나로 ", options: { fontSize: 12.5, color: C.navy } },
    { text: "8층에서 99.8% 식별", options: { fontSize: 12.5, bold: true, color: C.green } },
    { text: " (600문항, 교차검증)", options: { fontSize: 11, color: C.gray, breakLine: true } },
    { text: "· 별도 모델 불필요 — 어차피 하는 계산에서 공짜로 얻는 신호", options: { fontSize: 11.5, color: C.gray, breakLine: true } },
    { text: "· 당초 '실패(72.5%)'로 보였던 건 신호 16개를 평균해 흐려진 탓 — 좋은 신호 1개만 고르면 충분했음", options: { fontSize: 11.5, color: C.gray } },
  ], { x: 0.85, y: 2.35, w: 5.5, h: 1.6, fontFace: F, margin: 0, paraSpaceAfter: 6 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.85, y: 4.05, w: 5.45, h: 0.92, rectRadius: 0.08,
    fill: { color: C.lightorange }, line: { color: C.orange, width: 1.25 } });
  s.addText([
    { text: "⚠ 미확정 — 지금 실험은 정답 이미지가 항상 '1번 자리'", options: { bold: true, fontSize: 11.5, color: C.orange, breakLine: true } },
    { text: "이 신호가 '자리 선호'일 가능성을 밤새 검증 중 (자리를 뒤집은 대조 실험)", options: { fontSize: 10.5, color: C.navy } },
  ], { x: 1.05, y: 4.14, w: 5.1, h: 0.8, fontFace: F, margin: 0, paraSpaceAfter: 3 });
  // 우: 속도
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.8, y: 1.72, w: 6.0, h: 3.4, rectRadius: 0.1,
    fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("재료 2 — 실제로 빨라진다 (흉내 아님)", { x: 7.1, y: 1.9, w: 5.5, h: 0.4,
    fontFace: F, fontSize: 14, bold: true, color: C.navy, margin: 0 });
  s.addText([
    { text: "방해 이미지 토큰을 실제로 삭제하는 구현을 만들어 실측 → 응답 시작 시간 ", options: { fontSize: 12.5, color: C.navy } },
    { text: "9.7% 단축", options: { fontSize: 12.5, bold: true, color: C.green } },
    { text: " (510→461ms)", options: { fontSize: 11, color: C.gray, breakLine: true } },
    { text: "· 이론 상한은 42.4% — 격차의 원인 3가지를 규명했고 모두 해소 가능 (부록)", options: { fontSize: 11.5, color: C.gray, breakLine: true } },
    { text: "· 정확도는 그대로: 마스킹 방식과 예측 100% 일치 확인", options: { fontSize: 11.5, color: C.gray } },
  ], { x: 7.1, y: 2.35, w: 5.5, h: 1.6, fontFace: F, margin: 0, paraSpaceAfter: 6 });
  s.addText("이론치만 보고하지 않고 실측을 먼저 했습니다 — 격차를 아는 것이 부풀리는 것보다 낫기 때문", {
    x: 7.1, y: 4.2, w: 5.5, h: 0.7, fontFace: F, fontSize: 11, italic: true, color: C.gray, margin: 0 });
  s.addText("두 재료가 합쳐지면: \"8층에서 판단 → 그 지점부터 방해 이미지 삭제\" — 추가 모델 없이 한 번의 forward 안에서 완결", {
    x: 0.55, y: 5.35, w: 12.2, h: 0.75, fontFace: F, fontSize: 13.5, bold: true, color: C.navy, margin: 0 });
  takeaway(s, "→ 질문 ③의 답: 실용화의 두 재료(판단 신호 · 속도 이득)는 확인 — '자리 편향' 검증 결과가 내일 아침 나온다");
  s.addNotes("[내일 결과에 따라] 자리를 뒤집어도 유지되면: '관련도를 따라가는 신호'로 확정, 컨트롤러 실현 가능. 무너지면: 자리 선호였다는 것을 확정한 것이고, 깊은 층(21층, 99%)의 신호를 쓰는 설계로 전환 — 어느 쪽이든 다음 설계가 명확해집니다.");
}

// =====================================================================
// S12 — 선행연구
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "예상 질문 — \"이미 있는 연구 아닌가요?\"");
  headline(s, "인접 논문 12편의 원문을 전부 확인했다 — \"이미지별로 깊이를 다르게\"는 빈칸이다");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11.5 };
  const cell = { fontSize: 11, color: C.navy, fill: { color: C.lightgray } };
  const rows = [
    [{ text: "무엇을 위해 ＼ 어떤 단위로", options: hd }, { text: "모든 이미지에 똑같이", options: hd }, { text: "토큰(조각) 단위", options: hd }, { text: "이미지 단위", options: hd }],
    [{ text: "계산 절약만", options: hd },
     { text: "VTW (AAAI'25)\nShortV (ICCV'25)", options: cell },
     { text: "FastV 계열", options: cell },
     { text: "MVPruner (ECCV'26)\n— 단, '토큰 개수'만 조절", options: cell }],
    [{ text: "환각(출처) 개선", options: hd },
     { text: "RSCD · FOCUS\nDelimiter (ICLR'26)", options: cell },
     { text: "PruneHal (철회)", options: cell },
     { text: "★ 이 연구\n'계산 깊이'를 조절", options: { fontSize: 12.5, bold: true, color: C.white, fill: { color: C.red } } }],
  ];
  s.addTable(rows, { x: 0.55, y: 1.75, w: 12.25, rowH: [0.5, 0.95, 0.95], fontFace: F,
    align: "center", valign: "middle", border: { pt: 1.5, color: "FFFFFF" } });
  s.addText([
    { text: "가장 가까운 MVPruner(ECCV'26)도 이미지별로 '토큰 개수'를 조절할 뿐 — 모든 이미지가 끝까지 계산되고, 환각 문제는 다루지 않음", options: { bullet: true, breakLine: true } },
    { text: "'깊이 절감'과 '환각 완화'는 각각 존재하지만, 둘을 이미지 단위로 결합한 연구는 확인되지 않음 — 넓은 주장은 버리고 이 칸만 주장", options: { bullet: true } },
  ], { x: 0.55, y: 5.0, w: 12.25, h: 1.3, fontFace: F, fontSize: 12.5, color: C.navy,
    margin: 0, paraSpaceAfter: 8 });
  takeaway(s, "→ 단, '기존 연구의 조합'으로 보이지 않으려면 남은 관문(이미지별 차등 배분의 이득)을 실증해야 한다 — 그것이 다음 단계다");
  s.addNotes("novelty 우려는 저희가 먼저 조사했습니다. 12편 전부 원문 확인했고, 과한 주장은 버렸습니다. 남는 칸이 이 연구의 자리이고, 이 칸은 비어 있습니다. 단 결합 novelty라는 지적을 피하려면 차등 배분의 이득을 실증해야 하고, 그게 지금 밤새 돌고 있는 실험입니다.");
}

// =====================================================================
// S13 — 종합 + 계획
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "결론과 다음 계획");
  pendTag(s);
  headline(s, "성립 조건은 통과했다 — 6개월을 걸기 전에, 남은 관문 3개를 2~4주 안에 검증한다", false, 10.2);
  // 좌: 3질문 답
  s.addText("오늘의 세 질문, 세 답", { x: 0.55, y: 1.7, w: 6.0, h: 0.4, fontFace: F, fontSize: 14,
    bold: true, color: C.navy, margin: 0 });
  const ans = [
    ["Q1", "문제가 진짜 있는가", "✓ 있다 — 오염 21.3% vs 대조군 0%", C.green],
    ["Q2", "해법이 작동하는가", "✓ 한다 — 81% 회복 + 인과 확인 + X자 곡선", C.green],
    ["Q3", "실제로 만들 수 있는가", "◐ 두 재료 확인 — 자리 편향 검증만 남음 (내일)", C.orange],
  ];
  ans.forEach((a, i) => {
    const y = 2.2 + i * 1.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 6.0, h: 1.0, rectRadius: 0.08,
      fill: { color: i === 2 ? C.lightorange : C.lightgreen }, line: { color: a[3], width: 1.25 } });
    s.addText([{ text: `${a[0]} · ${a[1]}`, options: { bold: true, fontSize: 12.5, color: C.navy, breakLine: true } },
      { text: a[2], options: { fontSize: 12.5, bold: true, color: a[3] } }],
      { x: 0.8, y: y + 0.1, w: 5.5, h: 0.85, fontFace: F, margin: 0, paraSpaceAfter: 4 });
  });
  // 우: 계획
  s.addText("다음 계획 — 11월 CVPR 제출 역산", { x: 6.9, y: 1.7, w: 5.9, h: 0.4, fontFace: F,
    fontSize: 14, bold: true, color: C.navy, margin: 0 });
  const plan = [
    ["지금~4주", "관문 3개 검증", "① 이미지별 '차등' 깊이의 이득 (밤새 1차 실측 중) ② 컨트롤러 완결(자리 뒤집기·외부 방법과 비교) ③ 속도 우위(커널 구현)"],
    ["9~10월", "방법 확정·확장", "7B·타 모델 재현 → 표준 벤치마크 → 기존 방법들과 비교·ablation"],
    ["11월", "제출", "CVPR — 실패 시 출구도 준비: '깊이와 환각의 인과' 분석 논문 (자산 전부 재사용)"],
  ];
  plan.forEach((p, i) => {
    const y = 2.2 + i * 1.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.9, y, w: 5.9, h: 1.0, rectRadius: 0.08,
      fill: { color: C.light }, line: { color: C.line, width: 1 } });
    s.addText([{ text: `${p[0]} · ${p[1]}   `, options: { bold: true, fontSize: 12, color: C.blue } },
      { text: p[2], options: { fontSize: 10.5, color: C.gray } }],
      { x: 7.12, y: y + 0.08, w: 5.5, h: 0.88, fontFace: F, margin: 0 });
  });
  s.addText("판정 기준을 미리 동결하는 방식은 다음 단계에서도 유지합니다 — 실패하면 실패했다고 보고드리는 구조", {
    x: 0.55, y: 5.85, w: 12.2, h: 0.4, fontFace: F, fontSize: 11.5, italic: true, color: C.gray, margin: 0 });
  takeaway(s, "→ 오늘의 결론: 이 연구는 성립 근거를 '정량 수치'로 확보했다 — 관문 3개를 통과하면 CVPR, 못 하면 분석 논문으로 전환");
  s.addNotes("정리합니다. 문제는 실재하고(21% vs 0%), 해법은 인과적으로 작동하며(81% 회복), 질문 유형에 따라 최적 깊이가 정반대라 적응 배분 외엔 답이 없습니다. 실용화 재료 둘 중 하나만 검증이 남았고 내일 아침 나옵니다. 6개월을 먼저 걸지 않고 관문 3개를 2~4주에 먼저 깨보겠습니다.");
}

// =====================================================================
// S14 — Appendix divider
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addText("Appendix", { x: 0.8, y: 2.5, w: 8, h: 1.0, fontFace: F, fontSize: 44, bold: true,
    color: C.white, margin: 0 });
  s.addText("질문 대응 상세 자료", { x: 0.8, y: 3.5, w: 8, h: 0.5, fontFace: F, fontSize: 16,
    color: "AFC6DA", margin: 0 });
  s.addText([
    { text: "A0  실험 설계 상세 (4셀 매트릭스·조건 정의)", options: { breakLine: true } },
    { text: "A1  전체 결과표 (조건 × 문항군)", options: { breakLine: true } },
    { text: "A2  '두 장 비교' 질문 3종 상세", options: { breakLine: true } },
    { text: "A3  반대 방향 오염과 margin 민감도", options: { breakLine: true } },
    { text: "A3b 자체 반증 점검 (단일 이미지 비교)", options: { breakLine: true } },
    { text: "A4  층별 식별률 전체 곡선", options: { breakLine: true } },
    { text: "A5  층별 attention 분포", options: { breakLine: true } },
    { text: "A6  재현성·환경·한계", options: { breakLine: true } },
    { text: "A7  [미확정] 오늘 밤 산출분", options: {} },
  ], { x: 7.3, y: 1.55, w: 5.5, h: 4.6, fontFace: F, fontSize: 13.5, color: "D7E4EF",
    margin: 0, paraSpaceAfter: 9 });
}

// =====================================================================
// A0 — 실험 설계 상세
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A0");
  headline(s, "실험 설계 상세 — 4개 문항군(셀)과 10개 조건");
  const rows = [
    [{ text: "", options: {} }, { text: "방해 이미지에 질의 객체 있음", options: { bold: true, color: C.white, fill: { color: C.navy } } }, { text: "없음", options: { bold: true, color: C.white, fill: { color: C.navy } } }],
    [{ text: "정답 '없다'", options: { bold: true, color: C.white, fill: { color: C.navy } } },
     { text: "셀1 · 주 오염 측정\n(없다→있다 뒤집힘 예상)", options: { fill: { color: C.lightred }, bold: true, color: C.red } },
     { text: "셀3 · 대조군", options: { fill: { color: C.lightgray }, color: C.gray } }],
    [{ text: "정답 '있다'", options: { bold: true, color: C.white, fill: { color: C.navy } } },
     { text: "셀4 · 대조군", options: { fill: { color: C.lightgray }, color: C.gray } },
     { text: "셀2 · 반대 방향 오염\n(있다→없다)", options: { fill: { color: C.lightred }, bold: true, color: C.red } }],
  ];
  s.addTable(rows, { x: 0.55, y: 1.8, w: 6.6, rowH: [0.5, 1.0, 1.0], fontFace: F, fontSize: 11,
    align: "center", valign: "middle", border: { pt: 1, color: "FFFFFF" } });
  s.addText([
    { text: "프롬프트: \"In the first image, is there a ○○? Answer with Yes or No.\"", options: { bullet: true, breakLine: true } },
    { text: "조건 10개: 차단 없음(M) / 4·8·12·16·20·24층부터 차단 / 완전 차단(T0) / 이미지 1장(S) / 역방향 차단(T-rel)", options: { bullet: true, breakLine: true } },
    { text: "평가: 생성 없이 다음 토큰의 Yes/No 확률 비교 · 통계: 동일 문항 짝지은 McNemar 검정", options: { bullet: true, breakLine: true } },
    { text: "방해 이미지: 같은 상위 범주의 다른 COCO 사진 — 객체 유무는 annotation으로 검증, 4셀 균형 배정", options: { bullet: true } },
  ], { x: 7.4, y: 1.85, w: 5.4, h: 3.6, fontFace: F, fontSize: 11.5, color: C.navy,
    margin: 0, paraSpaceAfter: 8 });
  s.addText("양방향(셀1·셀2)을 두는 이유: '예'라고만 답하는 편향(yes-bias) 같은 단일 편향으로는 두 방향을 동시에 설명할 수 없기 때문", {
    x: 0.55, y: 5.35, w: 12.2, h: 0.6, fontFace: F, fontSize: 11.5, color: C.gray, margin: 0 });
}

// =====================================================================
// A1 — 전체 결과표
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A1");
  headline(s, "전체 결과표 — 조건 × 문항군 정답률, 회복/부작용, p값");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 10.5 };
  const c0 = { fontSize: 10.5, color: C.navy, fill: { color: C.white } };
  const c1 = { fontSize: 10.5, color: C.navy, fill: { color: C.lightgray } };
  const mk = (t, alt, opts) => ({ text: t, options: Object.assign({}, alt ? c1 : c0, opts || {}) });
  const data = [
    ["이미지 1장 (S)", "0.893", "0.740", "0.947", "0.780", "0.840", "—", "—", "—"],
    ["차단 없음 (M)", "0.720", "0.633", "0.980", "0.827", "0.790", "—", "—", "—"],
    ["4층부터 차단", "0.920", "0.720", "0.960", "0.767", "0.842", "81.0%", "3.7%", "6.0e-7"],
    ["8층부터", "0.933", "0.667", "0.960", "0.760", "0.830", "83.3%", "2.8%", "6.7e-8"],
    ["16층부터", "0.933", "0.627", "0.967", "0.740", "0.817", "85.7%", "3.7%", "1.9e-7"],
    ["24층부터", "0.733", "0.633", "0.987", "0.820", "0.793", "7.1%", "0.9%", "0.63"],
    ["완전 차단 (T0)", "0.933", "0.720", "0.953", "0.773", "0.845", "83.3%", "2.8%", "6.7e-8"],
    ["역방향 차단", "0.240", "0.027", "0.980", "0.760", "0.502", "—", "—", "3.6e-38*"],
  ];
  const rows = [[mk("조건", 0, hd), mk("셀1", 0, hd), mk("셀2", 0, hd), mk("셀3", 0, hd), mk("셀4", 0, hd),
    mk("전체", 0, hd), mk("회복(셀1)", 0, hd), mk("부작용(셀1)", 0, hd), mk("p(셀1)", 0, hd)]];
  data.forEach((r, i) => rows.push(r.map((v, j) => mk(v, i % 2, j === 0 ? { bold: true } : {}))));
  s.addTable(rows, { x: 0.55, y: 1.75, w: 12.25, rowH: 0.42, fontFace: F, align: "center",
    valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  s.addText("* 역방향 차단은 600문항 전체 검정 · 12/20층 포함 전체 그리드는 results/table1.csv · 내일 세분화 그리드(12점) 추가 예정", {
    x: 0.55, y: 6.35, w: 12.2, h: 0.35, fontFace: F, fontSize: 10, color: C.gray, margin: 0 });
}

// =====================================================================
// A2 — relational 상세
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A2");
  headline(s, "'두 장 비교' 질문 상세 — \"두 이미지 모두에 ○○ 있나요?\" (3종 × 100문항)");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 10.5 };
  const cc = { fontSize: 10.5, color: C.navy, fill: { color: C.white } };
  const mk2 = (t, o) => ({ text: t, options: Object.assign({}, cc, o || {}) });
  const rows = [
    [mk2("문항 유형 (정답)", hd), mk2("차단 없음", hd), mk2("24층", hd), mk2("20층", hd), mk2("16층", hd), mk2("12층", hd), mk2("8층", hd), mk2("4층", hd), mk2("완전 차단", hd)],
    [mk2("1번에만 있음 ('아니오')", { bold: true }), mk2("0.76"), mk2("0.72"), mk2("0.38", { color: C.red, bold: true }), mk2("0.34", { color: C.red, bold: true }), mk2("0.27", { color: C.red, bold: true }), mk2("0.24", { color: C.red, bold: true }), mk2("0.25", { color: C.red, bold: true }), mk2("0.26", { color: C.red, bold: true })],
    [mk2("2번에만 있음 ('아니오')", { bold: true }), mk2("0.49"), mk2("0.48"), mk2("0.83"), mk2("0.99"), mk2("1.00"), mk2("1.00"), mk2("1.00"), mk2("1.00")],
    [mk2("둘 다 있음 ('예')", { bold: true }), mk2("0.73"), mk2("0.73"), mk2("0.80"), mk2("0.73"), mk2("0.76"), mk2("0.77"), mk2("0.74"), mk2("0.72")],
  ];
  s.addTable(rows, { x: 0.55, y: 1.8, w: 12.25, rowH: 0.5, fontFace: F, align: "center",
    valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  s.addText([
    { text: "본편(핵심 그림)의 빨간 곡선은 1행입니다 — '아니오'가 정답이려면 2번 이미지를 반드시 확인해야 하므로, 차단하면 무너지는 것이 정상", options: { bullet: true, breakLine: true } },
    { text: "2행이 차단 시 1.00이 되는 이유: 2번이 안 보이면 모델이 '한 장짜리 문제'로 축소해 '아니오'를 답함(우연히 정답) — 차단의 완전성을 보여주는 부수 증거", options: { bullet: true, breakLine: true } },
    { text: "3행이 평평한 이유: 1번만 보고도 '예'로 기울 수 있어 판별력이 낮음 — 그래서 본편 판정은 1행 기준", options: { bullet: true } },
  ], { x: 0.55, y: 4.15, w: 12.25, h: 2.1, fontFace: F, fontSize: 11.5, color: C.navy,
    margin: 0, paraSpaceAfter: 8 });
}

// =====================================================================
// A3 — 반대 방향 + margin
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A3");
  headline(s, "반대 방향 오염('있다→없다')과 확신도(margin) 민감도");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11 };
  const cc = { fontSize: 11, color: C.navy, fill: { color: C.white } };
  const mk3 = (t, o) => ({ text: t, options: Object.assign({}, cc, o || {}) });
  const rows = [
    [mk3("확신도 낮은 문항 제외 기준", hd), mk3("주 오염: 없다→있다 (셀1)", hd), mk3("반대: 있다→없다 (셀2)", hd), mk3("회복률 (셀1, 4층 차단)", hd)],
    [mk3("제외 없음 (전체)"), mk3("21.3%  (150문항)", { bold: true }), mk3("12.7%  (150문항)"), mk3("81.0%", { bold: true })],
    [mk3("확신도 ≥ 0.25만"), mk3("21.4%  (131)", { bold: true }), mk3("8.6%  (128)"), mk3("82.9%", { bold: true })],
    [mk3("확신도 ≥ 0.5만"), mk3("18.9%  (111)", { bold: true }), mk3("1.0%  (103)", { color: C.red, bold: true }), mk3("77.8%", { bold: true })],
    [mk3("확신도 ≥ 1.0만"), mk3("16.2%  (74)", { bold: true }), mk3("0.0%  (78)", { color: C.red, bold: true }), mk3("85.7%", { bold: true })],
  ];
  s.addTable(rows, { x: 0.9, y: 1.85, w: 11.5, rowH: 0.52, fontFace: F, align: "center",
    valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  s.addText([
    { text: "주 오염(셀1)은 확신도 높은 문항만 남겨도 16~21%로 유지 → 경계선 문항의 착시가 아님", options: { bullet: true, breakLine: true } },
    { text: "반대 방향(셀2)은 확신도 0.5 이상에서 사실상 소멸 → 결정 경계 근처의 흔들림으로 해석, 본편 주장에서 제외", options: { bullet: true, breakLine: true } },
    { text: "따라서 본편은 셀1 + 인과 실험(역방향 차단)만으로 구성 — 약한 증거는 약하다고 표기하는 원칙", options: { bullet: true, bold: true } },
  ], { x: 0.9, y: 4.85, w: 11.5, h: 1.7, fontFace: F, fontSize: 12, color: C.navy,
    margin: 0, paraSpaceAfter: 8 });
}

// =====================================================================
// A3b — 자체 반증: '단일 이미지보다 좋다'는 성립하지 않음
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A3b");
  headline(s, "자체 반증 점검 — \"차단이 이미지 1장보다 낫다\"는 주장은 성립하지 않는다");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11 };
  const cc = { fontSize: 11, color: C.navy, fill: { color: C.white } };
  const m = (t, o) => ({ text: t, options: Object.assign({}, cc, o || {}) });
  const rows = [
    [m("조건", hd), m("정답 '없다'\n셀1", hd), m("정답 '없다'\n셀3", hd), m("정답 '있다'\n셀2", hd), m("정답 '있다'\n셀4", hd), m("전체", hd), m("'있다' 응답률", hd)],
    [m("이미지 1장 (S)", { bold: true }), m("0.893"), m("0.947"), m("0.740"), m("0.780"), m("0.840", { bold: true }), m("0.420")],
    [m("4층부터 차단 (T4)", { bold: true }), m("0.920", { color: C.green }), m("0.960", { color: C.green }), m("0.720", { color: C.red }), m("0.767", { color: C.red }), m("0.842", { bold: true }), m("0.402")],
    [m("완전 차단 (T0)", { bold: true }), m("0.933", { color: C.green }), m("0.953", { color: C.green }), m("0.720", { color: C.red }), m("0.773", { color: C.red }), m("0.845", { bold: true }), m("0.402")],
    [m("16층부터 차단", { bold: true }), m("0.933", { color: C.green }), m("0.967", { color: C.green }), m("0.627", { color: C.red }), m("0.740", { color: C.red }), m("0.817", { bold: true }), m("0.367")],
  ];
  s.addTable(rows, { x: 0.55, y: 1.75, w: 12.25, rowH: [0.62, 0.44, 0.44, 0.44, 0.44], fontFace: F,
    align: "center", valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  s.addText([
    { text: "관찰: 차단하면 정답이 '없다'인 문항군은 전부 오르고(초록), '있다'인 문항군은 전부 내린다(빨강) — 그리고 '있다' 응답률 자체가 감소", options: { bullet: true, breakLine: true } },
    { text: "→ 이는 정확도 향상이 아니라 판정 기준이 '없다' 쪽으로 이동한 것. 전체 정답률은 84.0% vs 84.2%로 사실상 동일", options: { bullet: true, breakLine: true, bold: true } },
    { text: "→ 따라서 \"단일 이미지보다 정확하다\"는 주장은 폐기. 올바른 서술은 \"차단이 멀티이미지 손실을 단일 이미지 수준으로 회복시킨다\"", options: { bullet: true, breakLine: true, bold: true } },
    { text: "단, 본편의 핵심 주장(M → T4)은 무관하게 유효: 같은 layout·같은 프롬프트에서 오염 문항군만 +20%p, 오염 없는 대조군은 −2%p — 기준 이동이면 둘 다 올랐어야 함 (응답률 이동폭 3.8%p로는 20%p 설명 불가)", options: { bullet: true } },
  ], { x: 0.55, y: 4.35, w: 12.25, h: 2.3, fontFace: F, fontSize: 11.5, color: C.navy,
    margin: 0, paraSpaceAfter: 7 });
}

// =====================================================================
// A4 — layer별 식별률
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A4");
  headline(s, "층별 '관련 이미지' 식별률 — 16개 신호 평균 기준 (n=600)");
  s.addImage({ path: R + "aux_chartA_ident_by_layer.png", x: 0.75, y: 1.9, w: 11.8, h: 4.29 });
  s.addText("16개 신호(head)를 평균하면 8층 72.5%(당초 판정 기준 미달 지점) — 단일 신호 선택 시 8층 99.8% (본편 질문③)", {
    x: 0.75, y: 6.3, w: 11.8, h: 0.35, fontFace: F, fontSize: 10.5, color: C.gray, margin: 0 });
}

// =====================================================================
// A5 — attention 프로파일
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A5");
  headline(s, "층별 attention 분포 — 정답 문항 vs 뒤집힌 문항");
  s.addImage({ path: R + "fig2_attention_profile.png", x: 1.9, y: 1.85, w: 9.5, h: 5.28 });
  s.addText("20층 이후 두 이미지의 참조량이 갈라짐 — 본편 '같은 층 전환' 관찰과 정합", {
    x: 1.9, y: 7.05, w: 9.5, h: 0.3, align: "center", fontFace: F, fontSize: 10.5, color: C.gray, margin: 0 });
}

// =====================================================================
// A6 — 재현성
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A6");
  headline(s, "재현성 · 환경 · 한계");
  s.addText([
    { text: "환경: RTX 3090 24GB × 1 · torch 2.5.1+cu121 · transformers 4.52.3 · Qwen2.5-VL-3B-Instruct (BF16, eager) · 실측 36 layers", options: { bullet: true, breakLine: true } },
    { text: "재현성: 난수 고정(seed 42) · 판정 기준 사전 등록(문서 동결) · 전 결과 raw 보존 · 실행 로그·버전 기록", options: { bullet: true, breakLine: true } },
    { text: "규모·비용: 본 실험 29분 + 야간 확장 실험 · GPU 1장 · 오류 중단 0건", options: { bullet: true, breakLine: true } },
    { text: "동점 처리: Yes/No 확률이 같은 104건(1.7%)은 사전 규정('없다'로 판정)대로 처리", options: { bullet: true, breakLine: true } },
    { text: "저장소: github.com/hsmai/Source-Depth (private) — 코드·데이터 명세·문서·판정 기준·raw 결과 전부 버전 관리", options: { bullet: true, breakLine: true } },
    { text: "한계(정직 고지): 정답 이미지 위치 고정(oracle) · 단일 물체 질문 중심 · 3B 단일 모델(7B 재현 진행 중) · 속도는 프로토타입 실측 · COCO 주석 노이즈 36건(6%)", options: { bullet: true, bold: true } },
  ], { x: 0.7, y: 2.0, w: 12.0, h: 4.6, fontFace: F, fontSize: 13, color: C.navy,
    margin: 0, paraSpaceAfter: 14 });
}

// =====================================================================
// A7 — [미확정]
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A7");
  pendTag(s);
  headline(s, "오늘 밤 산출 중 — 내일 오전 이 칸들을 채웁니다", false, 10.2);
  const items = [
    ["자리 뒤집기 대조", "질문③ 신호가 '자리 선호'인지 '관련도'인지 확정", "→ 본편 질문③ 해석 확정"],
    ["이미지별 '차등' 깊이 실측", "방해 4층 + 대상 28층을 동시에 적용 — 방법의 첫 실제 구동", "→ 결론·계획 슬라이드 갱신"],
    ["'모두 똑같이 자르기'와 비교", "기존 방식(모든 이미지 같은 층 차단)과 동일 예산 비교", "→ 선행연구 슬라이드 보강"],
    ["외부 선택기(CLIP)와 비교", "\"CLIP으로 고르면 되지 않나\"에 대한 정면 비교", "→ 질문 대응"],
    ["안전 손잡이(α) 곡선", "'오류율 상한을 정하고 계산 최소화' — 정확도·절감 곡선", "→ 계획 슬라이드 보강"],
    ["7B 모델 재현", "같은 실험을 2배 큰 모델에서 — 스케일 일반화", "→ 한계 항목 해소"],
  ];
  items.forEach((it, i) => {
    const x = 0.55 + (i % 3) * 4.25, y = 1.9 + Math.floor(i / 3) * 2.3, w = 4.0, h = 2.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: C.lightorange }, line: { color: C.orange, width: 1.25, dashType: "dash" } });
    s.addText([{ text: it[0], options: { bold: true, fontSize: 14, color: C.orange, breakLine: true } },
      { text: it[1], options: { fontSize: 11, color: C.navy, breakLine: true } },
      { text: it[2], options: { fontSize: 10.5, bold: true, color: C.gray } }],
      { x: x + 0.22, y: y + 0.18, w: w - 0.44, h: h - 0.36, fontFace: F, margin: 0, paraSpaceAfter: 6 });
  });
  s.addText("야간 자동 체인 실행 중 · 실패 시 자동 재제출(watchdog) · 전 단계 이어하기(resume) 지원", {
    x: 0.55, y: 6.55, w: 12.2, h: 0.35, fontFace: F, fontSize: 10.5, color: C.gray, margin: 0 });
}

pres.writeFile({ fileName: "/Users/hansangmin/Source-Depth/meeting/SourceDepth_Phase0_meeting.pptx" })
  .then(() => console.log("DECK v2 WRITTEN"));
