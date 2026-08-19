// SourceDepth 미팅 덱 v6 — 서사 중심 재설계
// 원칙: 슬라이드 1장 = 질문 1개 / 용어는 그림으로 정의 / 숫자보다 "무엇을 했는지" 먼저
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

const C = {
  navy: "1F3B57", darkbg: "142638", blue: "1F77B4", red: "D62728",
  green: "2E8B57", orange: "E8890C", gray: "6B7280", white: "FFFFFF",
  light: "EFF4F9", lightred: "FBEAEA", lightgray: "F3F4F6",
  lightgreen: "E9F4EE", lightblue: "E8F1FA", line: "D5DEE8", mute: "AAB4BF",
};
const F = "Arial";

const kicker = (s, t, d) => s.addText(t, { x: 0.55, y: 0.26, w: 11.5, h: 0.3,
  fontFace: F, fontSize: 11, bold: true, color: d ? "9FB8CE" : C.blue, margin: 0 });
const headline = (s, t, d) => s.addText(t, { x: 0.55, y: 0.54, w: 12.2, h: 0.74,
  fontFace: F, fontSize: 22, bold: true, color: d ? C.white : C.navy, margin: 0 });
const takeaway = (s, t, col) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.6, w: 12.25, h: 0.62,
    rectRadius: 0.08, fill: { color: col || C.navy } });
  s.addText(t, { x: 0.85, y: 6.6, w: 11.75, h: 0.62, fontFace: F, fontSize: 12.5,
    bold: true, color: C.white, margin: 0, valign: "middle" });
};
const foot = (s, t) => s.addText(t, { x: 0.55, y: 6.16, w: 12.2, h: 0.36,
  fontFace: F, fontSize: 10, italic: true, color: C.gray, margin: 0 });

// ── 앵커 그림: [이미지1][이미지2][질문] + 두 경로 ────────────────
// mix / read : "on" | "cut" | "keep"
function anchor(s, x, y, mix, read, caption, k) {
  k = k || 1;
  const bw = 1.45 * k, bh = 0.8 * k, gap = 0.28 * k;
  const boxes = [
    ["이미지 1", "질문 대상", C.lightblue, C.blue],
    ["이미지 2", "무관", C.lightgray, C.gray],
    ["질문", "\"1번에 개가\n있나?\"", C.light, C.navy],
  ];
  boxes.forEach((b, i) => {
    const bx = x + i * (bw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx, y, w: bw, h: bh,
      rectRadius: 0.06, fill: { color: b[2] }, line: { color: b[3], width: 1 } });
    s.addText(b[0], { x: bx, y: y + 0.08 * k, w: bw, h: 0.26 * k, align: "center",
      fontFace: F, fontSize: 11 * k, bold: true, color: b[3], margin: 0 });
    s.addText(b[1], { x: bx, y: y + 0.34 * k, w: bw, h: 0.42 * k, align: "center",
      fontFace: F, fontSize: 8.5 * k, color: C.gray, margin: 0 });
  });
  const style = (st) => st === "cut" ? { col: C.red, dash: "dash" }
                      : st === "keep" ? { col: C.green, dash: "solid" }
                      : { col: C.mute, dash: "solid" };
  // 경로 A: 이미지2 → 이미지1  (혼합)
  const a = style(mix), ay = y + bh + 0.3 * k;
  s.addShape(pres.shapes.LINE, { x, y: ay, w: bw + gap, h: 0,
    line: { color: a.col, width: 2, dashType: a.dash, beginArrowType: "triangle" } });
  s.addText("경로 A · 이미지끼리 봄", { x: x - 0.05, y: ay + 0.06, w: bw + gap + 0.1,
    h: 0.24, align: "center", fontFace: F, fontSize: 8.5 * k, bold: true, color: a.col, margin: 0 });
  if (mix === "cut") s.addText("✕", { x: x + (bw + gap) / 2 - 0.12, y: ay - 0.24, w: 0.24,
    h: 0.24, align: "center", fontFace: F, fontSize: 14, bold: true, color: C.red, margin: 0 });
  // 경로 B: 질문 → 이미지2  (읽기)
  const b2 = style(read), by = y + bh + 0.78 * k;
  s.addShape(pres.shapes.LINE, { x: x + bw + gap, y: by, w: bw + gap, h: 0,
    line: { color: b2.col, width: 2, dashType: b2.dash, beginArrowType: "triangle" } });
  s.addText("경로 B · 질문이 이미지를 읽음", { x: x + bw + gap - 0.3, y: by + 0.06,
    w: bw + gap + 0.6, h: 0.24, align: "center", fontFace: F, fontSize: 8.5 * k,
    bold: true, color: b2.col, margin: 0 });
  if (read === "cut") s.addText("✕", { x: x + bw + gap + (bw + gap) / 2 - 0.12, y: by - 0.24,
    w: 0.24, h: 0.24, align: "center", fontFace: F, fontSize: 14, bold: true, color: C.red, margin: 0 });
  if (caption) s.addText(caption, { x: x - 0.1, y: y + bh + 1.24 * k, w: 3 * bw + 2 * gap + 0.2,
    h: 0.3, align: "center", fontFace: F, fontSize: 11, bold: true, color: C.navy, margin: 0 });
}

// ═════════ 1. 표지 ═════════
{
  const s = pres.addSlide();
  s.background = { color: C.darkbg };
  s.addText("SOURCEDEPTH · 연구 방향 보고 · 한상민 · 2026-08-14", { x: 0.6, y: 0.55,
    w: 12.2, h: 0.3, fontFace: F, fontSize: 11.5, bold: true, color: "7EC8F5", margin: 0 });
  s.addText("여러 장의 사진을 함께 주면\n모델이 엉뚱한 사진을 보고 답합니다", { x: 0.6, y: 1.15,
    w: 12.2, h: 1.35, fontFace: F, fontSize: 30, bold: true, color: C.white,
    margin: 0, lineSpacingMultiple: 1.15 });
  s.addText("이 보고는 세 가지를 다룹니다 — 그 현상이 실제로 있는지, 왜 생기는지, 어떻게 고치는지", {
    x: 0.6, y: 2.72, w: 12.2, h: 0.34, fontFace: F, fontSize: 13.5, color: "AFC6DA", margin: 0 });
  const q = [
    ["Q1", "정말 그런 일이 일어나는가?", "일어납니다. 무관한 사진 3장이면\n작은 모델은 사실상 찍는 수준이 됩니다"],
    ["Q2", "왜 그런가?", "사진끼리 섞여서가 아니라,\n질문이 엉뚱한 사진을 읽기 때문입니다"],
    ["Q3", "그럼 어떻게 고치는가?", "사진을 지우지 말고,\n질문만 못 읽게 하면 됩니다"],
  ];
  q.forEach((c, i) => {
    const x = 0.6 + i * 4.15, y = 3.4, w = 3.95, h = 2.9;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: "1D3850" }, line: { color: "2E4E6B", width: 1 } });
    s.addText(c[0], { x: x + 0.25, y: y + 0.22, w: 1, h: 0.3, fontFace: F,
      fontSize: 12, bold: true, color: "7EC8F5", margin: 0 });
    s.addText(c[1], { x: x + 0.25, y: y + 0.58, w: w - 0.5, h: 0.6, fontFace: F,
      fontSize: 15, bold: true, color: C.white, margin: 0, lineSpacingMultiple: 1.1 });
    s.addText(c[2], { x: x + 0.25, y: y + 1.5, w: w - 0.5, h: 1.1, fontFace: F,
      fontSize: 12, color: "AFC6DA", margin: 0, lineSpacingMultiple: 1.25 });
  });
  s.addNotes("오늘 보고는 세 질문으로 구성했습니다. 현상이 실제로 있는지, 왜 생기는지, 어떻게 고치는지입니다. 결론부터 말씀드리면 두 번째가 예상과 반대로 나왔고, 그게 이번 연구의 중심입니다.");
}

// ═════════ 2. 문제 정의 ═════════
{
  const s = pres.addSlide();
  kicker(s, "Q1 — 어떤 문제인가");
  headline(s, "사진을 한 장 더 넣었을 뿐인데 답이 바뀝니다");

  const cases = [
    ["사진 1장만 줬을 때", ["개가 없는 거실 사진"], "\"이 사진에 개가 있나요?\"", "아니오", true, C.green],
    ["무관한 사진을 한 장 더 넣었을 때", ["개가 없는 거실 사진", "+ 개가 있는 공원 사진 (질문과 무관)"],
      "\"첫 번째 사진에 개가 있나요?\"", "있습니다", false, C.red],
  ];
  cases.forEach((c, i) => {
    const x = 0.55 + i * 6.23, w = 6.02;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.42, w, h: 2.85, rectRadius: 0.09,
      fill: { color: i ? C.lightred : C.lightgreen }, line: { color: c[5], width: 1.25 } });
    s.addText(c[0], { x: x + 0.25, y: 1.56, w: w - 0.5, h: 0.3, fontFace: F,
      fontSize: 13, bold: true, color: c[5], margin: 0 });
    c[1].forEach((im, j) => {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.25, y: 1.94 + j * 0.5, w: w - 0.5,
        h: 0.42, rectRadius: 0.05, fill: { color: C.white }, line: { color: C.line, width: 0.75 } });
      s.addText(im, { x: x + 0.4, y: 1.94 + j * 0.5, w: w - 0.8, h: 0.42, fontFace: F,
        fontSize: 11, color: C.navy, margin: 0, valign: "middle" });
    });
    s.addText(c[2], { x: x + 0.25, y: 3.02, w: w - 0.5, h: 0.3, fontFace: F,
      fontSize: 11.5, italic: true, color: C.gray, margin: 0 });
    s.addText([{ text: "모델 답변:  ", options: { fontSize: 12, color: C.gray } },
               { text: c[3], options: { fontSize: 16, bold: true, color: c[5] } },
               { text: c[4] ? "   (정답)" : "   (오답)", options: { fontSize: 12, bold: true, color: c[5] } }],
      { x: x + 0.25, y: 3.44, w: w - 0.5, h: 0.4, fontFace: F, margin: 0, valign: "middle" });
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 4.5, w: 12.25, h: 1.5,
    rectRadius: 0.09, fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("두 번째 사진은 질문 대상이 아닙니다. 그런데 거기 있던 개가 첫 번째 사진으로 '옮겨붙습니다'.", {
    x: 0.85, y: 4.66, w: 11.7, h: 0.3, fontFace: F, fontSize: 13.5, bold: true, color: C.navy, margin: 0 });
  s.addText("실제 응용에서 이 상황은 예외가 아니라 기본값입니다 — 문서 여러 장을 함께 읽을 때, 영상에서 프레임을 여러 개 볼 때,\n검색으로 가져온 이미지들을 함께 넣을 때. 대부분의 입력은 질문과 무관하고, 그 무관한 것들이 답을 흔듭니다.", {
    x: 0.85, y: 5.04, w: 11.7, h: 0.8, fontFace: F, fontSize: 12, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.25 });
  takeaway(s, "→ 이 연구가 정의한 문제: 여러 입력이 함께 들어올 때, 무관한 입력이 답을 오염시키는 현상");
  s.addNotes("먼저 문제가 무엇인지부터 말씀드립니다. 개가 없는 사진 한 장만 주면 모델이 맞게 답합니다. 그런데 질문과 상관없는 사진을 한 장 더 넣으면, 거기 있던 개가 첫 번째 사진으로 옮겨붙습니다. 실제 응용에서는 이런 상황이 예외가 아니라 기본입니다.");
}

// ═════════ 3. 문제 실재 확인 ═════════
{
  const s = pres.addSlide();
  kicker(s, "Q1 — 정말 그런가");
  headline(s, "무관한 사진을 늘려가며 재봤습니다");

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 1.36, w: 5.9, h: 2.05,
    rectRadius: 0.08, fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("먼저 — '판별력 점수'가 무엇인가", { x: 0.78, y: 1.48, w: 5.4, h: 0.28,
    fontFace: F, fontSize: 12.5, bold: true, color: C.navy, margin: 0 });
  s.addText("맞다/아니다를 얼마나 잘 가려내는지를 0.5~1.0으로 나타낸 값.\n정답률과 달리 \"예\"라고 자주 답해서 점수가 오르는 착시가 없습니다.", {
    x: 0.78, y: 1.8, w: 5.4, h: 0.55, fontFace: F, fontSize: 10.5, color: C.gray,
    margin: 0, lineSpacingMultiple: 1.2 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.95, y: 2.62, w: 5.05, h: 0.16,
    fill: { color: "D9E2EC" }, line: { color: C.line, width: 0.5 } });
  [["0.5", 0.95, "찍기와 같음", C.red], ["1.0", 6.0, "완벽", C.green]].forEach(v => {
    s.addShape(pres.shapes.OVAL, { x: v[1] - 0.06, y: 2.56, w: 0.28, h: 0.28, fill: { color: v[3] } });
    s.addText(v[0], { x: v[1] - 0.35, y: 2.86, w: 0.9, h: 0.22, align: "center",
      fontFace: F, fontSize: 10, bold: true, color: v[3], margin: 0 });
    s.addText(v[2], { x: v[1] - 0.75, y: 3.06, w: 1.7, h: 0.22, align: "center",
      fontFace: F, fontSize: 9, color: C.gray, margin: 0 });
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.68, y: 1.36, w: 6.12, h: 2.05,
    rectRadius: 0.08, fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("어떻게 쟀나", { x: 6.91, y: 1.48, w: 5.6, h: 0.28, fontFace: F,
    fontSize: 12.5, bold: true, color: C.navy, margin: 0 });
  s.addText("· 같은 질문 300개를 두 종류로 준비 — 정답이 \"있다\"인 것 150개,\n  \"없다\"인 것 150개 (한쪽으로 찍어도 이득이 없게)\n· 무관한 사진을 0장 → 3장까지 늘려가며 같은 질문을 반복\n· 모델 두 개(3B·7B)에서 각각 3,000회 측정", {
    x: 6.91, y: 1.8, w: 5.66, h: 1.4, fontFace: F, fontSize: 10.5, color: C.gray,
    margin: 0, lineSpacingMultiple: 1.28 });

  const bars = [["사진 1장만", 0.9078, C.green], ["+ 무관 1장", 0.6978, C.orange],
                ["+ 무관 2장", 0.6063, C.orange], ["+ 무관 3장", 0.5213, C.red]];
  s.addText("작은 모델(3B)의 판별력 점수", { x: 0.55, y: 3.56, w: 6, h: 0.3, fontFace: F,
    fontSize: 12.5, bold: true, color: C.navy, margin: 0 });
  bars.forEach((b, i) => {
    const y = 3.94 + i * 0.56, full = 9.0;
    const wdt = Math.max(0.05, (b[1] - 0.5) / 0.5) * full;
    s.addText(b[0], { x: 0.55, y, w: 1.75, h: 0.42, fontFace: F, fontSize: 11.5,
      bold: true, color: C.navy, margin: 0, valign: "middle" });
    s.addShape(pres.shapes.RECTANGLE, { x: 2.4, y: y + 0.08, w: full, h: 0.26,
      fill: { color: "EDF1F5" } });
    s.addShape(pres.shapes.RECTANGLE, { x: 2.4, y: y + 0.08, w: wdt, h: 0.26, fill: { color: b[2] } });
    s.addText(b[1].toFixed(2), { x: 2.4 + full + 0.15, y, w: 1.2, h: 0.42, fontFace: F,
      fontSize: 12, bold: true, color: b[2], margin: 0, valign: "middle" });
  });
  s.addText("← 0.5 (찍기)", { x: 2.4, y: 6.2, w: 1.6, h: 0.24, fontFace: F, fontSize: 9,
    color: C.gray, margin: 0 });
  takeaway(s, "→ 무관한 사진 3장이면 작은 모델의 판별력이 찍는 것과 구분되지 않습니다. 큰 모델(7B)은 훨씬 덜합니다");
  s.addNotes("문제가 실제로 있는지 재봤습니다. 먼저 지표를 설명드리면, 판별력 점수는 맞다 아니다를 얼마나 잘 가려내는지를 0.5에서 1.0으로 나타낸 값입니다. 정답률만 보면 예라고 자주 답해서 점수가 오르는 착시가 있는데, 이 지표는 그게 없습니다. 결과는 오른쪽입니다. 무관한 사진이 늘수록 판별력이 떨어지고 3장이면 사실상 찍는 수준입니다.");
}

// ═════════ 4. 가설 두 개 ═════════
{
  const s = pres.addSlide();
  kicker(s, "Q2 — 왜 그런가");
  headline(s, "정보가 흐를 수 있는 길은 두 개뿐입니다");
  s.addText("모델은 [이미지1] [이미지2] [질문] 순서로 읽습니다. 앞쪽은 뒤쪽을 볼 수 없으므로, 무관한 이미지2가 답에 닿는 길은 다음 둘뿐입니다.", {
    x: 0.55, y: 1.3, w: 12.25, h: 0.3, fontFace: F, fontSize: 11.5, color: C.gray, margin: 0 });
  anchor(s, 1.0, 1.75, "on", "on");
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.9, y: 1.72, w: 5.9, h: 1.15,
    rectRadius: 0.08, fill: { color: C.lightgray }, line: { color: C.gray, width: 1 } });
  s.addText("가설 A — 사진끼리 섞여서", { x: 7.13, y: 1.84, w: 5.4, h: 0.28, fontFace: F,
    fontSize: 13, bold: true, color: C.navy, margin: 0 });
  s.addText("이미지2를 보면서 이미지1의 표현이 오염된다.\n→ 그렇다면 경로 A를 끊으면 좋아져야 한다.", {
    x: 7.13, y: 2.16, w: 5.4, h: 0.6, fontFace: F, fontSize: 11, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.2 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.9, y: 3.0, w: 5.9, h: 1.15,
    rectRadius: 0.08, fill: { color: C.lightgray }, line: { color: C.gray, width: 1 } });
  s.addText("가설 B — 질문이 잘못 읽어서", { x: 7.13, y: 3.12, w: 5.4, h: 0.28, fontFace: F,
    fontSize: 13, bold: true, color: C.navy, margin: 0 });
  s.addText("이미지1은 멀쩡한데, 질문이 답을 만들 때\n이미지2에서 본 것을 1번 것으로 착각한다.\n→ 그렇다면 경로 B를 끊으면 좋아져야 한다.", {
    x: 7.13, y: 3.44, w: 5.4, h: 0.66, fontFace: F, fontSize: 11, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.2 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 4.62, w: 12.25, h: 1.32,
    rectRadius: 0.09, fill: { color: C.lightblue }, line: { color: C.blue, width: 1.25 } });
  s.addText("이 구분이 왜 중요한가", { x: 0.85, y: 4.76, w: 11.7, h: 0.28, fontFace: F,
    fontSize: 13, bold: true, color: C.blue, margin: 0 });
  s.addText("처방이 정반대가 되기 때문입니다. A가 맞으면 사진들을 서로 떼어놓아야 하고, B가 맞으면 붙여두되 질문이 읽는 것만 막아야 합니다.\n그리고 실제로 기존 연구들이 이 지점에서 갈려 있습니다 — 어떤 팀은 사진 간 연결을 늘렸고, 어떤 팀은 끊었습니다. (9번 슬라이드)", {
    x: 0.85, y: 5.08, w: 11.7, h: 0.7, fontFace: F, fontSize: 11.5, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.25 });
  takeaway(s, "→ 지금까지 아무도 이 둘을 나눠서 재지 않았습니다. 그래서 우리가 하나씩 끊어봤습니다");
  s.addNotes("왜 그런지 알아보려면 정보가 흐를 수 있는 길을 먼저 봐야 합니다. 모델은 왼쪽부터 순서대로 읽고 앞쪽은 뒤쪽을 볼 수 없으므로, 무관한 이미지가 답에 닿는 길은 두 개뿐입니다. 사진끼리 보는 길과 질문이 사진을 읽는 길입니다. 이 둘 중 어느 쪽이 범인이냐에 따라 처방이 정반대가 됩니다.");
}

// ═════════ 5. 방법 ═════════
{
  const s = pres.addSlide();
  kicker(s, "Q2 — 어떻게 구분하는가");
  headline(s, "사진은 그대로 두고, 길만 하나씩 끊어봅니다");

  const steps = [
    ["1", "사진은 손대지 않는다", "입력에는 두 장이 그대로 들어있습니다.\n지우거나 흐리게 만들지 않습니다."],
    ["2", "'누가 무엇을 볼 수 있는지'만 바꾼다", "모델 내부에서 각 토큰이 서로를 보는 표를\n한 칸씩 막습니다 (attention mask)."],
    ["3", "한 번에 하나의 길만 끊는다", "경로 A만 끊은 조건, 경로 B만 끊은 조건을\n따로 만들어 비교합니다."],
  ];
  steps.forEach((st, i) => {
    const y = 1.4 + i * 1.02;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 6.05, h: 0.9,
      rectRadius: 0.07, fill: { color: C.light }, line: { color: C.line, width: 0.75 } });
    s.addShape(pres.shapes.OVAL, { x: 0.75, y: y + 0.25, w: 0.4, h: 0.4, fill: { color: C.blue } });
    s.addText(st[0], { x: 0.75, y: y + 0.25, w: 0.4, h: 0.4, align: "center", valign: "middle",
      fontFace: F, fontSize: 12, bold: true, color: C.white, margin: 0 });
    s.addText(st[1], { x: 1.3, y: y + 0.1, w: 5.1, h: 0.28, fontFace: F, fontSize: 12,
      bold: true, color: C.navy, margin: 0 });
    s.addText(st[2], { x: 1.3, y: y + 0.4, w: 5.1, h: 0.44, fontFace: F, fontSize: 10,
      color: C.gray, margin: 0, lineSpacingMultiple: 1.15 });
  });

  anchor(s, 7.15, 1.5, "cut", "on", "조건 ①  경로 A만 끊음");
  anchor(s, 7.15, 3.6, "on", "cut", "조건 ②  경로 B만 끊음");

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 4.62, w: 6.05, h: 1.32,
    rectRadius: 0.08, fill: { color: C.lightgreen }, line: { color: C.green, width: 1.25 } });
  s.addText("왜 이 방법이면 '원인'이라 말할 수 있나", { x: 0.78, y: 4.74, w: 5.6, h: 0.28,
    fontFace: F, fontSize: 12, bold: true, color: C.green, margin: 0 });
  s.addText("두 조건에서 사진·질문·모델이 전부 동일하고,\n바뀐 것은 '어느 길이 열려 있는가' 하나뿐입니다.\n따라서 결과 차이는 그 길 때문입니다.", {
    x: 0.78, y: 5.06, w: 5.6, h: 0.72, fontFace: F, fontSize: 10.5, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.2 });
  foot(s, "이 마스킹이 '토큰을 실제로 지운 것'과 예측이 100% 일치함을 별도로 확인했습니다 (부록)");
  takeaway(s, "→ 상관관계가 아니라 개입 실험입니다. 길을 끊었을 때 결과가 바뀌면, 그 길이 원인입니다");
  s.addNotes("구분하는 방법은 단순합니다. 사진은 그대로 두고 모델 내부에서 누가 누구를 볼 수 있는지만 바꿉니다. 두 조건에서 사진도 질문도 모델도 같고 열린 길만 다르므로, 결과 차이는 그 길 때문이라고 말할 수 있습니다. 상관관계가 아니라 개입 실험입니다.");
}

// ═════════ 6. 결과 ═════════
{
  const s = pres.addSlide();
  kicker(s, "Q2 — 결과");
  headline(s, "범인은 '읽기'였습니다. 그리고 '섞임'은 오히려 도움이었습니다");

  const res = [
    ["아무것도 안 함", "on", "on", 0.70, C.gray, "기준"],
    ["경로 A (섞임) 끊음", "cut", "on", 0.40, C.red, "훨씬 나빠짐"],
    ["경로 B (읽기) 끊음", "on", "cut", 0.91, C.green, "거의 완전 회복"],
  ];
  res.forEach((r, i) => {
    const x = 0.55 + i * 4.13, w = 3.95;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.36, w, h: 3.55, rectRadius: 0.09,
      fill: { color: i === 1 ? C.lightred : i === 2 ? C.lightgreen : C.lightgray },
      line: { color: r[4], width: 1.25 } });
    s.addText(r[0], { x: x + 0.2, y: 1.5, w: w - 0.4, h: 0.3, align: "center", fontFace: F,
      fontSize: 12.5, bold: true, color: r[4], margin: 0 });
    anchor(s, x + 0.28, 1.94, r[1], r[2], null, 0.72);
    s.addText(r[3].toFixed(2), { x: x + 0.2, y: 3.98, w: w - 0.4, h: 0.5, align: "center",
      fontFace: F, fontSize: 26, bold: true, color: r[4], margin: 0 });
    s.addText(r[5], { x: x + 0.2, y: 4.5, w: w - 0.4, h: 0.28, align: "center", fontFace: F,
      fontSize: 11, bold: true, color: r[4], margin: 0 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.04, w: 12.25, h: 1.0,
    rectRadius: 0.09, fill: { color: C.lightblue }, line: { color: C.blue, width: 1.25 } });
  s.addText("사진끼리 보는 것은 오염원이 아니라 보호막이었습니다", { x: 0.85, y: 5.16,
    w: 11.7, h: 0.28, fontFace: F, fontSize: 13, bold: true, color: C.blue, margin: 0 });
  s.addText("무관한 사진이 옆 사진을 함께 보면 '맥락 속의 한 장면'이 되지만, 혼자 떨어져 있으면 더 도드라져서 질문을 끌어당깁니다.\n같은 결과가 모델 두 개 × 사진 순서 두 가지 = 네 조건 모두에서 나왔습니다. 우연이 아닙니다.", {
    x: 0.85, y: 5.46, w: 11.7, h: 0.55, fontFace: F, fontSize: 11.5, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.2 });
  foot(s, "판별력 점수 · 문항 300개 · 3B 기준. 7B에서도 방향 동일 (0.87 / 0.45 / 0.90) — 상세는 부록");
  takeaway(s, "→ 처음 세운 가설(섞여서 생긴다)을 우리 손으로 반증했습니다. 원인은 읽기 단계의 출처 착각입니다");
  s.addNotes("결과입니다. 왼쪽이 기준, 가운데가 사진끼리 보는 길을 끊은 것, 오른쪽이 질문이 읽는 길을 끊은 것입니다. 가운데를 보시면 훨씬 나빠졌습니다. 즉 사진끼리 보는 건 오염원이 아니라 보호막이었습니다. 오른쪽처럼 읽기만 끊으면 거의 완전히 회복됩니다. 저희가 처음 세운 가설이 틀렸고, 그걸 저희 실험으로 확인했습니다.");
}

// ═════════ 7. 제안 방법 ═════════
{
  const s = pres.addSlide();
  kicker(s, "Q3 — 그래서 어떻게 푸는가");
  headline(s, "무관한 사진을 지우지 말고, 질문만 못 읽게 합니다");
  s.addText("가장 자연스러운 처방은 \"무관하면 빼버리자\"입니다. 그런데 그렇게 하면 보호막까지 같이 사라집니다.", {
    x: 0.55, y: 1.3, w: 12.25, h: 0.3, fontFace: F, fontSize: 11.5, color: C.gray, margin: 0 });
  const opt = [
    ["흔한 방법 — 통째로 뺀다", "cut", "cut", 0.889, C.orange,
     "사진 자체를 입력에서 제거.\n해로운 읽기는 막히지만\n이로운 맥락도 함께 사라집니다."],
    ["우리 방법 — 남기고 못 읽게 한다", "on", "cut", 0.908, C.green,
     "사진은 그대로 두어 옆 사진이 볼 수 있게 하고,\n질문이 그것을 읽는 길만 막습니다."],
  ];
  opt.forEach((o, i) => {
    const x = 0.55 + i * 6.23, w = 6.02;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.68, w, h: 3.5, rectRadius: 0.09,
      fill: { color: i ? C.lightgreen : C.lightgray }, line: { color: o[4], width: 1.25 } });
    s.addText(o[0], { x: x + 0.2, y: 1.82, w: w - 0.4, h: 0.3, align: "center", fontFace: F,
      fontSize: 13, bold: true, color: o[4], margin: 0 });
    anchor(s, x + 1.15, 2.24, o[1], o[2]);
    s.addText(o[5], { x: x + 0.3, y: 4.3, w: w - 0.6, h: 0.7, align: "center", fontFace: F,
      fontSize: 10.5, color: C.navy, margin: 0, lineSpacingMultiple: 1.2 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.3, w: 12.25, h: 0.74,
    rectRadius: 0.08, fill: { color: C.white }, line: { color: C.green, width: 1.5 } });
  s.addText([
    { text: "판별력 점수:   통째로 뺌 0.889   <   남기고 못 읽게 함 0.908", options: { fontSize: 14, bold: true, color: C.green } },
    { text: "     (차이 +0.018, 통계적으로 유의 · 문항 300개)", options: { fontSize: 11, color: C.gray } },
  ], { x: 0.85, y: 5.3, w: 11.7, h: 0.74, fontFace: F, margin: 0, valign: "middle" });
  takeaway(s, "→ 무관한 사진은 '증거로는 해롭고 맥락으로는 이롭다'는 두 얼굴을 갖습니다. 지우면 절반을 버립니다", C.green);
  s.addNotes("그래서 저희가 제안하는 방법은 지우지 않는 것입니다. 사진은 그대로 두어서 옆 사진이 볼 수 있게 하고, 질문이 그걸 읽는 길만 막습니다. 실제로 통째로 빼는 것보다 이 쪽이 더 낫습니다. 무관한 사진은 증거로는 해롭지만 맥락으로는 이롭다는 두 얼굴을 갖고 있어서, 지우면 절반을 버리는 셈입니다.");
}


// ═════════ 7b. 어느 층에서 개입하나 ═════════
{
  const s = pres.addSlide();
  kicker(s, "Q3 — 그럼 어느 시점에 막아야 하는가");
  headline(s, "중요한 일은 전부 앞쪽 절반에서 끝납니다");
  s.addText("모델은 여러 층을 거치며 답을 만듭니다. 막는 시점을 바꿔가며 재보니, 세 가지가 모두 앞쪽에서 결정됐습니다.", {
    x: 0.55, y: 1.28, w: 12.25, h: 0.3, fontFace: F, fontSize: 11.5, color: C.gray, margin: 0 });

  const X0 = 2.3, XW = 10.1, NL = 36;
  const LX = (l) => X0 + (l / NL) * XW;
  // 층 눈금
  s.addShape(pres.shapes.LINE, { x: X0, y: 1.78, w: XW, h: 0, line: { color: C.line, width: 1 } });
  [0, 8, 16, 24, 36].forEach(l => {
    s.addShape(pres.shapes.LINE, { x: LX(l), y: 1.72, w: 0, h: 0.12, line: { color: C.gray, width: 1 } });
    s.addText(String(l), { x: LX(l) - 0.3, y: 1.5, w: 0.6, h: 0.22, align: "center",
      fontFace: F, fontSize: 9.5, color: C.gray, margin: 0 });
  });
  s.addText("층 →", { x: X0 + XW + 0.1, y: 1.66, w: 0.7, h: 0.24, fontFace: F,
    fontSize: 9.5, color: C.gray, margin: 0 });

  const bands = [
    ["해로운 읽기가 쌓인다", 0, 16, C.red, C.lightred,
     "8층까지 막으면 효과의 97%.  16층부터면 68%,  24층부터면 9%밖에 못 건집니다.",
     "→ 개입은 늦어도 8층 전에"],
    ["이미지끼리 정보를 주고받는다", 0, 16, C.blue, C.lightblue,
     "0층부터 떼어놓으면 −0.055로 손해.  16층부터 떼어놓으면 −0.005로 사실상 무해합니다.",
     "→ 16층 이후엔 서로 안 봐도 됨"],
    ["무관한 사진을 가려낼 단서가 남아 있다", 0, 16, C.green, C.lightgreen,
     "16층부터만 다시 계산해도 판별 정확도가 0.730 → 0.720.  24층부터면 0.640으로 무너집니다.",
     "→ 판별은 16층부터 다시 계산해도 됨"],
  ];
  bands.forEach((b, i) => {
    const y = 2.12 + i * 1.28;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 12.25, h: 1.16,
      rectRadius: 0.07, fill: { color: b[4] }, line: { color: b[3], width: 1 } });
    s.addText(b[0], { x: 0.78, y: y + 0.1, w: 5.3, h: 0.28, fontFace: F, fontSize: 12,
      bold: true, color: b[3], margin: 0 });
    s.addText(b[5], { x: 0.78, y: y + 0.42, w: 8.6, h: 0.5, fontFace: F, fontSize: 10.5,
      color: C.navy, margin: 0, lineSpacingMultiple: 1.15 });
    s.addText(b[6], { x: 9.5, y: y + 0.42, w: 3.1, h: 0.5, fontFace: F, fontSize: 11,
      bold: true, color: b[3], margin: 0, valign: "middle" });
    // 구간 막대
    s.addShape(pres.shapes.RECTANGLE, { x: LX(b[1]) - 0.55 + 6.0, y: y + 0.1, w: 0.001, h: 0.001,
      fill: { color: b[3] } });
  });
  // 축 위 구간 표시
  bands.forEach((b, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: LX(b[1]), y: 1.84 + i * 0.075, w: LX(b[2]) - LX(b[1]),
      h: 0.06, fill: { color: b[3] } });
  });
  s.addShape(pres.shapes.LINE, { x: LX(8), y: 1.66, w: 0, h: 0.42,
    line: { color: C.red, width: 2, dashType: "dash" } });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.98, w: 12.25, h: 0.5,
    rectRadius: 0.07, fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("모델 두 개 모두에서 같은 그림입니다 — 3B는 8/36층(22% 지점), 7B는 8/28층(29% 지점)까지가 결정적이었습니다.", {
    x: 0.85, y: 5.98, w: 11.7, h: 0.5, fontFace: F, fontSize: 11, color: C.navy,
    margin: 0, valign: "middle" });
  takeaway(s, "→ '가려내는 일'은 늦게 해도 되고, '고치는 일'은 일찍 해야 합니다. 이 둘의 시점이 다르다는 게 방법 설계의 핵심입니다");
  s.addNotes("어느 층에서 막아야 하느냐는 질문에 답하는 슬라이드입니다. 세 가지를 각각 재봤는데 모두 앞쪽 절반에서 결정됐습니다. 중요한 건 마지막 줄입니다. 어느 사진이 무관한지 가려내는 일은 16층부터 계산해도 되는데, 실제로 고치는 일은 8층 전에 시작해야 합니다. 이 둘의 시점이 다르기 때문에, 가려내는 계산은 절반만 해도 되고 그만큼 비용이 절약됩니다.");
}


// ═════════ 7c. 경로 대비 — 읽기 차단 + 빼기 ═════════
{
  const s = pres.addSlide();
  kicker(s, "Q3 — 한 걸음 더");
  headline(s, "같은 사진으로 '가장 깨끗한 상태'와 '가장 오염된 상태'를 만들어 뺍니다");
  s.addText("앞에서 두 경로를 각각 끊어봤습니다. 그 두 결과를 버리지 않고 같이 쓰면, 사진 한 장만 줬을 때보다도 좋아집니다.", {
    x: 0.55, y: 1.28, w: 12.25, h: 0.3, fontFace: F, fontSize: 11.5, color: C.gray, margin: 0 });

  const br = [
    ["깨끗한 쪽", "질문이 무관한 사진을 못 읽게", "on", "cut", 0.906, C.green, C.lightgreen],
    ["오염된 쪽", "사진끼리 못 보게 (무관한 사진이 가장 도드라짐)", "cut", "on", 0.403, C.red, C.lightred],
  ];
  br.forEach((b, i) => {
    const x = 0.55 + i * 4.3, w = 4.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.66, w, h: 3.4, rectRadius: 0.09,
      fill: { color: b[6] }, line: { color: b[5], width: 1.25 } });
    s.addText(b[0], { x: x + 0.2, y: 1.78, w: w - 0.4, h: 0.28, align: "center", fontFace: F,
      fontSize: 13, bold: true, color: b[5], margin: 0 });
    s.addText(b[1], { x: x + 0.2, y: 2.08, w: w - 0.4, h: 0.4, align: "center", fontFace: F,
      fontSize: 10, color: C.navy, margin: 0, lineSpacingMultiple: 1.15 });
    anchor(s, x + 0.32, 2.54, b[2], b[3], null, 0.74);
    s.addText(b[4].toFixed(3), { x: x + 0.2, y: 4.42, w: w - 0.4, h: 0.44, align: "center",
      fontFace: F, fontSize: 20, bold: true, color: b[5], margin: 0 });
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.15, y: 1.66, w: 3.65, h: 3.4,
    rectRadius: 0.09, fill: { color: C.lightblue }, line: { color: C.blue, width: 1.5 } });
  s.addText("두 결과를 뺀다", { x: 9.35, y: 1.78, w: 3.25, h: 0.28, align: "center",
    fontFace: F, fontSize: 13, bold: true, color: C.blue, margin: 0 });
  s.addText("깨끗한 쪽을 밀고\n오염된 쪽을 빼면\n오염의 크기가\n오히려 단서가 됩니다", {
    x: 9.35, y: 2.16, w: 3.25, h: 1.0, align: "center", fontFace: F, fontSize: 11,
    color: C.navy, margin: 0, lineSpacingMultiple: 1.25 });
  s.addText("0.974", { x: 9.35, y: 3.3, w: 3.25, h: 0.6, align: "center", fontFace: F,
    fontSize: 30, bold: true, color: C.blue, margin: 0 });
  s.addText("사진 한 장만 줬을 때(0.908)\n보다도 높습니다", { x: 9.35, y: 3.96, w: 3.25, h: 0.5,
    align: "center", fontFace: F, fontSize: 10, bold: true, color: C.blue, margin: 0 });
  s.addText("2모델 × 2배치 = 4조건\n전부 통계적으로 유의", { x: 9.35, y: 4.5, w: 3.25, h: 0.44,
    align: "center", fontFace: F, fontSize: 9.5, color: C.gray, margin: 0 });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.2, w: 12.25, h: 0.84,
    rectRadius: 0.08, fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText([
    { text: "두 갈래의 사진은 완전히 똑같습니다. 다른 건 '어느 길이 열려 있는가'뿐입니다.", options: { fontSize: 12, bold: true, color: C.navy, breakLine: true } },
    { text: "기존 방법들은 음의 기준을 만들려고 사진에 노이즈를 씌웁니다(손상된 입력). 우리는 사진을 그대로 두고 내부 경로만 바꿉니다 — 입력을 건드리는 방식으로는 이 두 상태를 만들 수 없습니다.", options: { fontSize: 10.5, color: C.navy } },
  ], { x: 0.85, y: 5.28, w: 11.7, h: 0.7, fontFace: F, margin: 0, paraSpaceAfter: 3 });
  foot(s, "판별력 점수 · n=300 · 3B 원래 배치 기준. 두 갈래를 만들려면 무엇이 무관한지 알아야 하고, forward가 2회 필요합니다");
  takeaway(s, "→ '오염을 없애는 것'을 넘어 '오염의 크기를 증거로 쓰는' 단계입니다. 이건 경로를 나눠 봤기 때문에 가능해졌습니다", C.blue);
  s.addNotes("앞에서 두 경로를 각각 끊어본 결과를 버리지 않고 같이 씁니다. 질문이 못 읽게 한 쪽은 가장 깨끗한 상태이고, 사진끼리 못 보게 한 쪽은 무관한 사진이 가장 도드라진 상태입니다. 두 결과를 빼면 오염의 크기 자체가 단서가 되어서, 사진 한 장만 줬을 때보다도 높아집니다. 중요한 건 두 갈래의 사진이 완전히 같다는 점입니다. 기존 방법들은 노이즈를 씌워서 음의 기준을 만드는데, 그 방식으로는 이 두 상태를 만들 수 없습니다.");
}

// ═════════ 8. 무관한 사진 판별 ═════════
{
  const s = pres.addSlide();
  kicker(s, "Q3 — 어느 사진이 무관한지는 어떻게 아는가");
  headline(s, "하나씩 빼보고, 답이 가장 크게 흔들리는 쪽이 진짜 필요한 사진입니다");

  const st = [
    ["시도 1 — 실패", "모델이 각 사진에 얼마나 주목하는지 본다",
     "겉보기엔 99.8% 정확했지만, 사진 순서를 뒤집자 0.2%가 됐습니다.\n'관련 있는 사진'이 아니라 '첫 번째 사진'을 찾고 있었습니다.", C.red, C.lightred],
    ["시도 2 — 채택", "사진을 하나씩 빼보고 답이 얼마나 흔들리는지 본다",
     "위치를 아예 참조하지 않으므로 같은 함정에 빠질 수 없습니다.\n사진 3장일 때 73% 정확 — 무관한 사진이 많을수록 더 정확해집니다.", C.green, C.lightgreen],
  ];
  st.forEach((v, i) => {
    const y = 1.36 + i * 1.42;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 7.5, h: 1.28,
      rectRadius: 0.08, fill: { color: v[4] }, line: { color: v[3], width: 1.25 } });
    s.addText(v[0], { x: 0.78, y: y + 0.1, w: 2.0, h: 0.28, fontFace: F, fontSize: 12,
      bold: true, color: v[3], margin: 0 });
    s.addText(v[1], { x: 2.85, y: y + 0.1, w: 5.0, h: 0.28, fontFace: F, fontSize: 12,
      bold: true, color: C.navy, margin: 0 });
    s.addText(v[2], { x: 0.78, y: y + 0.44, w: 7.05, h: 0.7, fontFace: F, fontSize: 10.5,
      color: C.navy, margin: 0, lineSpacingMultiple: 1.2 });
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.28, y: 1.36, w: 4.52, h: 2.7,
    rectRadius: 0.08, fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("외부 모듈로는 안 되는 이유", { x: 8.5, y: 1.48, w: 4.1, h: 0.28, fontFace: F,
    fontSize: 12, bold: true, color: C.navy, margin: 0 });
  s.addText("\"CLIP 같은 걸 앞에 두면 되지 않나?\"\n\n실제로 재봤습니다 — 사실상 찍는 수준입니다.\n무관한 사진에도 질문 속 물건이 들어있으면,\n의미가 비슷하다는 이유로 오히려 그쪽을 고릅니다.\n\n중요한 건 \"의미가 가까운가\"가 아니라\n\"이 모델의 답을 바꾸는가\"이고,\n그건 모델을 통과시켜야만 알 수 있습니다.", {
    x: 8.5, y: 1.8, w: 4.1, h: 2.2, fontFace: F, fontSize: 10, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.22 });

  s.addTable([
    [{ text: "사진 수", options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11 } },
     { text: "외부 모듈 (CLIP)", options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11 } },
     { text: "우리 방법 (하나씩 빼보기)", options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11 } },
     { text: "무작위로 찍으면", options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11 } }],
    [{ text: "2장", options: { fontSize: 11, color: C.navy, bold: true } }, { text: "51%", options: { fontSize: 11, color: C.red } },
     { text: "69%", options: { fontSize: 11, bold: true, color: C.green } }, { text: "50%", options: { fontSize: 11, color: C.gray } }],
    [{ text: "3장", options: { fontSize: 11, color: C.navy, bold: true } }, { text: "39%", options: { fontSize: 11, color: C.red } },
     { text: "71%", options: { fontSize: 11, bold: true, color: C.green } }, { text: "33%", options: { fontSize: 11, color: C.gray } }],
    [{ text: "4장", options: { fontSize: 11, color: C.navy, bold: true } }, { text: "35%", options: { fontSize: 11, color: C.red } },
     { text: "73%", options: { fontSize: 11, bold: true, color: C.green } }, { text: "25%", options: { fontSize: 11, color: C.gray } }],
  ], { x: 0.55, y: 4.3, w: 7.5, rowH: [0.34, 0.3, 0.3, 0.3], fontFace: F, align: "center",
       valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  s.addText("사진이 많아질수록 우리 쪽은 좋아지고 외부 모듈은 나빠집니다 — 무관한 후보가 늘기 때문입니다.", {
    x: 0.55, y: 5.66, w: 7.5, h: 0.4, fontFace: F, fontSize: 10.5, color: C.gray,
    margin: 0, lineSpacingMultiple: 1.15 });
  foot(s, "판별 정확도 · 문항 300개 · 3B. 이 방식은 사진 수만큼 추가 계산이 필요합니다 (정확도를 얻는 대신 비용을 씁니다)");
  takeaway(s, "→ 관련도는 '의미'가 아니라 '이 모델의 답을 바꾸는가'로 정의됩니다");
  s.addNotes("어느 사진이 무관한지 아는 방법입니다. 처음에는 모델이 어디를 주목하는지 봤는데 실패했습니다. 사진 순서를 뒤집으니 정확도가 99.8에서 0.2로 떨어졌습니다. 관련도가 아니라 위치를 보고 있었던 겁니다. 그래서 방법을 바꿔서, 사진을 하나씩 빼보고 답이 가장 크게 흔들리는 쪽을 필요한 사진으로 봅니다. 위치를 아예 안 보니 같은 함정에 빠지지 않습니다.");
}

// ═════════ 9. 기존 연구 ═════════
{
  const s = pres.addSlide();
  kicker(s, "왜 가치 있는가 (1) — 기존 연구와의 관계");
  headline(s, "기존 연구는 정반대 처방을 내놓았고, 양쪽 다 개선을 보고했습니다");
  s.addText("한쪽은 '늘리라', 다른 쪽은 '끊으라' — 그런데 둘 다 성능이 올랐다고 보고합니다. 아무도 이유를 설명하지 못했습니다.", {
    x: 0.55, y: 1.3, w: 12.25, h: 0.32, fontFace: F, fontSize: 11.5, color: C.gray, margin: 0 });
  const camps = [
    ["\"연결을 늘려라\"", ["CAPL (2026.03)", "SoFA (CVPR 2025)"],
     "사진 간 정보가 부족해서 문제라고 진단.\n서로 더 잘 보게 만듭니다.", C.blue, C.lightblue],
    ["\"연결을 끊어라\"", ["MIMIC (2026.01)", "FOCUS (2025.08)"],
     "사진 간 정보가 오염시킨다고 진단.\n일괄로 막거나 아예 지웁니다.", C.red, C.lightred],
  ];
  camps.forEach((c, i) => {
    const x = 0.55 + i * 3.35, w = 3.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.68, w, h: 2.0, rectRadius: 0.08,
      fill: { color: c[4] }, line: { color: c[3], width: 1.25 } });
    s.addText(c[0], { x: x + 0.15, y: 1.8, w: w - 0.3, h: 0.3, align: "center", fontFace: F,
      fontSize: 13, bold: true, color: c[3], margin: 0 });
    c[1].forEach((p, j) => s.addText("· " + p, { x: x + 0.25, y: 2.14 + j * 0.28, w: w - 0.5,
      h: 0.26, fontFace: F, fontSize: 10.5, color: C.navy, margin: 0 }));
    s.addText(c[2], { x: x + 0.25, y: 2.78, w: w - 0.5, h: 0.7, fontFace: F, fontSize: 10,
      color: C.gray, margin: 0, lineSpacingMultiple: 1.2 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.3, y: 1.68, w: 5.5, h: 2.0, rectRadius: 0.08,
    fill: { color: C.lightgreen }, line: { color: C.green, width: 1.5 } });
  s.addText("우리 답 — 둘 다 맞았습니다", { x: 7.5, y: 1.8, w: 5.1, h: 0.3, fontFace: F,
    fontSize: 13, bold: true, color: C.green, margin: 0 });
  s.addText("서로 다른 길을 건드리고 있었습니다.\n\n· 사진끼리 보는 길 → 도움이 된다 (늘려라가 맞음)\n· 질문이 읽는 길 → 해롭다 (끊어라가 맞음)\n\n두 길을 나눠 재기 전에는 구분할 수 없었습니다.", {
    x: 7.5, y: 2.14, w: 5.1, h: 1.4, fontFace: F, fontSize: 11, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.25 });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 3.86, w: 6.05, h: 2.14,
    rectRadius: 0.08, fill: { color: C.lightred }, line: { color: C.red, width: 1 } });
  s.addText("우리가 쓸 수 없는 주장 (조사로 확인)", { x: 0.78, y: 3.98, w: 5.6, h: 0.28,
    fontFace: F, fontSize: 12, bold: true, color: C.red, margin: 0 });
  s.addText("· \"학습 없이 추론 때 개입한다\" — 이미 세 편이 함\n· \"층 단위로 개입한다\" — 네 편 모두 이미 함\n· \"개입으로 원인을 검증한다\" — 한 편이 이미 함\n\n→ 이 셋은 novelty로 쓰지 않습니다.", {
    x: 0.78, y: 4.3, w: 5.6, h: 1.5, fontFace: F, fontSize: 10.5, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.3 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.78, y: 3.86, w: 6.02, h: 2.14,
    rectRadius: 0.08, fill: { color: C.lightgreen }, line: { color: C.green, width: 1 } });
  s.addText("아직 비어 있는 자리", { x: 7.01, y: 3.98, w: 5.6, h: 0.28, fontFace: F,
    fontSize: 12, bold: true, color: C.green, margin: 0 });
  s.addText("· 사진끼리 보는 길만 따로 끊어본 연구 — 0편\n  (기존은 전부 모달리티 사이 연결만 끊음)\n· 여러 사진 중 특정 한 장만 골라 끊은 연구 — 0편\n· 무관한 사진이 섞인 상황 자체를 CAPL·SoFA는\n  실험한 적이 없음", {
    x: 7.01, y: 4.3, w: 5.6, h: 1.5, fontFace: F, fontSize: 10.5, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.3 });
  takeaway(s, "→ 새 방법 하나를 더하는 게 아니라, 분야가 갈려 있던 지점을 정리하는 결과입니다");
  s.addNotes("기존 연구를 조사했더니 두 진영으로 갈려 있었습니다. 한쪽은 사진 간 연결을 늘리라 하고 한쪽은 끊으라 하는데, 양쪽 다 개선을 보고합니다. 저희 경로 분해가 이 모순을 설명합니다. 그리고 조사 과정에서 저희가 처음에 novelty로 생각했던 세 가지는 쓸 수 없다는 것도 확인했습니다. 그건 슬라이드에 그대로 적어뒀습니다.");
}

// ═════════ 10. 기여 ═════════
{
  const s = pres.addSlide();
  kicker(s, "왜 가치 있는가 (2) — 기여");
  headline(s, "이 연구가 새로 밝힌 것 세 가지");
  const con = [
    ["1", "원인을 경로 수준에서 특정했다",
     "\"정보가 섞인다\"를 두 개의 구분 가능한 길로 나누고, 하나씩 끊어 어느 쪽이 해로운지 인과적으로 가렸습니다.",
     "사진끼리 보는 길을 끊으면 오히려 크게 나빠짐 · 모델 2개 × 사진 순서 2가지 전부 일관", C.blue],
    ["2", "그래서 처방이 달라지고, 한 걸음 더 갈 수 있다",
     "지우는 것보다 남겨두고 못 읽게 하는 편이 낫고, 나아가 '가장 깨끗한 경로'와 '가장 오염된 경로'를 만들어 빼면 사진 한 장만 줬을 때보다도 좋아집니다.",
     "통째로 뺌 0.889 < 못 읽게 함 0.908 < 경로 대비 0.974 · 2모델 × 2배치 전부 유의", C.green],
    ["3", "관련도는 '의미'가 아니라 '모델 상대적'이다",
     "무엇이 무관한지는 의미 유사도로 판별되지 않습니다. 이 모델의 답을 바꾸는지로 정의되고, 그건 모델을 통과시켜야 알 수 있습니다.",
     "외부 모듈(CLIP) 35~51% (찍기 수준) vs 우리 69~73%", C.orange],
  ];
  con.forEach((c, i) => {
    const y = 1.36 + i * 1.5;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 12.25, h: 1.36,
      rectRadius: 0.08, fill: { color: C.light }, line: { color: C.line, width: 0.75 } });
    s.addShape(pres.shapes.OVAL, { x: 0.85, y: y + 0.45, w: 0.46, h: 0.46, fill: { color: c[4] } });
    s.addText(c[0], { x: 0.85, y: y + 0.45, w: 0.46, h: 0.46, align: "center", valign: "middle",
      fontFace: F, fontSize: 14, bold: true, color: C.white, margin: 0 });
    s.addText(c[1], { x: 1.5, y: y + 0.14, w: 11.0, h: 0.3, fontFace: F, fontSize: 13.5,
      bold: true, color: C.navy, margin: 0 });
    s.addText(c[2], { x: 1.5, y: y + 0.46, w: 11.0, h: 0.46, fontFace: F, fontSize: 11,
      color: C.navy, margin: 0, lineSpacingMultiple: 1.15 });
    s.addText("근거   " + c[3], { x: 1.5, y: y + 0.98, w: 11.0, h: 0.3, fontFace: F,
      fontSize: 10, bold: true, color: c[4], margin: 0 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.9, w: 12.25, h: 0.6,
    rectRadius: 0.08, fill: { color: C.lightblue }, line: { color: C.blue, width: 1 } });
  s.addText("공통점: 셋 다 '사진을 넣을지 말지'라는 이진 선택으로는 표현할 수 없는 것입니다. 그래서 앞단에 모듈을 두는 방식으로는 도달할 수 없습니다.", {
    x: 0.85, y: 5.9, w: 11.7, h: 0.6, fontFace: F, fontSize: 11.5, bold: true,
    color: C.navy, margin: 0, valign: "middle" });
  takeaway(s, "→ selection은 관련도가 이진이고 미리 계산된다고 가정합니다. 우리 측정은 둘 다 아니라고 말합니다");
  s.addNotes("기여는 세 가지입니다. 첫째, 원인을 경로 수준에서 특정했습니다. 둘째, 그래서 처방이 달라집니다. 지우는 것보다 남기고 못 읽게 하는 게 낫습니다. 셋째, 관련도가 의미가 아니라 모델 상대적이라는 것입니다. 이 셋의 공통점은 사진을 넣을지 말지라는 이진 선택으로 표현할 수 없다는 겁니다. 그래서 앞단 모듈로는 도달할 수 없습니다.");
}

// ═════════ 11. 한계와 계획 ═════════
{
  const s = pres.addSlide();
  s.background = { color: C.darkbg };
  kicker(s, "남은 일", true);
  headline(s, "지금 이 연구를 무너뜨릴 수 있는 것과, 그것을 확인할 계획", true);
  const risk = [
    ["지금 벤치마크는 질문이 \"첫 번째 사진\"이라고 위치를 알려준다",
     "그러면 앞단 모듈이 글자만 읽어도 맞힙니다. 내부 개입이어야 하는 이유를 증명할 수 없습니다."],
    ["아직 공개 벤치마크에서 재현하지 않았다",
     "CAPL은 \"추론 때 손대는 건 일시적 개선일 뿐\"이라고 미리 반론을 걸어뒀습니다."],
    ["판별에 사진 수만큼 추가 계산이 든다",
     "16층부터만 다시 계산해도 판별이 유지되고(0.720), 이미지 인코딩은 전체 비용의 68%라 재사용 여지가 큽니다 — 다만 그 구현은 아직 안 했습니다."],
  ];
  risk.forEach((r, i) => {
    const y = 1.36 + i * 0.92;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 12.25, h: 0.8, rectRadius: 0.07,
      fill: { color: "3A2430" }, line: { color: "6B3A4A", width: 1 } });
    s.addText(String(i + 1), { x: 0.82, y: y + 0.2, w: 0.35, h: 0.4, align: "center",
      fontFace: F, fontSize: 13, bold: true, color: "FF9E80", margin: 0 });
    s.addText(r[0], { x: 1.3, y: y + 0.09, w: 11.2, h: 0.3, fontFace: F, fontSize: 12.5,
      bold: true, color: C.white, margin: 0 });
    s.addText(r[1], { x: 1.3, y: y + 0.42, w: 11.2, h: 0.3, fontFace: F, fontSize: 10.5,
      color: "D0BCC4", margin: 0 });
  });
  const plan = [["1주", "질문이 위치를 알려주지 않는 벤치마크로 교체", "앞단 모듈이 원리적으로 못 푸는가"],
                ["2주", "공개 벤치마크(BLINK·MUIRBench)에서 재현", "CAPL의 반론을 막을 수 있는가"],
                ["3주", "판별 비용 줄이기 + FOCUS와 직접 비교", "같은 비용에서 우리가 나은가"],
                ["4주", "모델 3계열로 확장 · 논문 초안", "—"]];
  plan.forEach((p, i) => {
    const y = 4.2 + i * 0.52;
    s.addText(p[0], { x: 0.75, y, w: 0.8, h: 0.44, fontFace: F, fontSize: 12, bold: true,
      color: "7EC8F5", margin: 0, valign: "middle" });
    s.addText(p[1], { x: 1.75, y, w: 6.0, h: 0.44, fontFace: F, fontSize: 11.5,
      color: C.white, margin: 0, valign: "middle" });
    s.addText("→ " + p[2], { x: 7.9, y, w: 4.9, h: 0.44, fontFace: F, fontSize: 10.5,
      color: "8CE0B0", margin: 0, valign: "middle" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.4, w: 12.25, h: 0.8,
    rectRadius: 0.08, fill: { color: "1D3850" }, line: { color: "2E4E6B", width: 1 } });
  s.addText([
    { text: "중단 조건을 미리 정해둡니다 — 2주차에 공개 벤치마크에서 재현되지 않으면 이 방향은 접겠습니다.", options: { bold: true, fontSize: 12, color: "FFC94D", breakLine: true } },
    { text: "지금까지 실험 전에 판정 기준을 먼저 적어두고 실행한 것이 6건이고, 그중 3건은 기준 미달로 실패 처리했습니다. GPU 1장, 기존 코드·데이터 재사용.", options: { fontSize: 10.5, color: "9FB8CE" } },
  ], { x: 0.85, y: 6.46, w: 11.7, h: 0.7, fontFace: F, margin: 0, paraSpaceAfter: 3 });
  s.addNotes("마지막으로 불리한 것을 말씀드립니다. 가장 큰 문제는 지금 벤치마크가 질문에서 첫 번째 사진이라고 위치를 알려준다는 겁니다. 그러면 앞단 모듈이 글자만 읽어도 맞힙니다. 이건 설계 결함이고 1주차에 바꿉니다. 그리고 2주차에 공개 벤치마크에서 재현되지 않으면 접겠습니다. 지금까지 판정 기준을 먼저 적어두고 실행한 게 여섯 번이고 그중 세 번은 실패로 기록했습니다.");
}


// ═════════════════ 부록 ═════════════════
const AH = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 10.5 };
const AC = { fontSize: 10.5, color: C.navy, fill: { color: C.white } };
const am = (t, o) => ({ text: t, options: Object.assign({}, AC, o || {}) });
const ATBL = { fontFace: F, align: "center", valign: "middle",
               border: { pt: 0.75, color: "E2E8F0" } };
function apx(title, sub) {
  const s = pres.addSlide();
  kicker(s, "APPENDIX");
  headline(s, title);
  if (sub) s.addText(sub, { x: 0.55, y: 1.28, w: 12.25, h: 0.3, fontFace: F,
    fontSize: 10.5, color: C.gray, margin: 0 });
  return s;
}

// A1 — 실험 설계
{
  const s = apx("실험 설계 — 오염이 생길 수밖에 없는 문항을 만든다",
    "질문: \"In the first image, is there {물건}?\"  ·  COCO val2014에서 구성  ·  seed 고정  ·  사전 등록 후 실행");
  s.addTable([
    [am("", AH), am("정답", AH), am("무관 사진에 질문 속 물건이", AH), am("어느 방향으로 미는가", AH), am("문항 수", AH)],
    [am("셀 1", { bold: true }), am("없다"), am("있음", { bold: true, color: C.red }), am("\"있다\"고 답하게"), am("150")],
    [am("셀 2", { bold: true }), am("있다"), am("없음", { bold: true, color: C.blue }), am("\"없다\"고 답하게"), am("150")],
  ], { x: 0.55, y: 1.7, w: 12.25, rowH: [0.44, 0.42, 0.42], ...ATBL });
  s.addText("양쪽 모두 무관한 사진이 '오답 방향'으로 밉니다. 한쪽만 보면 큰 모델에서 현상이 사라진 것처럼 보입니다 — 실제로 저희가 처음에 그 실수를 했습니다.", {
    x: 0.55, y: 3.1, w: 12.25, h: 0.34, fontFace: F, fontSize: 11, italic: true, color: C.gray, margin: 0 });
  const items = [["규모", "모델 2개(3B·7B) × 문항 300 × 무관 사진 0~3장 × 조건 10종 = 모델당 3,000회"],
                 ["통제", "모든 조건에서 사진이 물리적으로 전부 입력에 존재. 바뀌는 것은 '누가 무엇을 볼 수 있는가' 하나뿐"],
                 ["지표", "판별력 점수(AUC) 주 지표. 정답률은 보고하되 판정 근거로 쓰지 않음"],
                 ["재현", "체크포인트 재개, 코드·데이터 전부 git 기록, 사전 등록 문서 6건"]];
  items.forEach((it, i) => {
    const y = 3.6 + i * 0.68;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 12.25, h: 0.6, rectRadius: 0.06,
      fill: { color: i % 2 ? C.light : C.lightgray } });
    s.addText(it[0], { x: 0.8, y, w: 1.3, h: 0.6, fontFace: F, fontSize: 11, bold: true,
      color: C.navy, margin: 0, valign: "middle" });
    s.addText(it[1], { x: 2.2, y, w: 10.4, h: 0.6, fontFace: F, fontSize: 10.5,
      color: C.navy, margin: 0, valign: "middle" });
  });
}

// A2 — 마스킹 타당성
{
  const s = apx("이 마스킹이 '진짜로 지운 것'과 같은가",
    "개입이 흉내가 아니라 실제 삭제와 동일함을 별도로 검증했습니다");
  s.addTable([
    [am("확인 항목", AH), am("방법", AH), am("결과", AH)],
    [am("예측 일치", { bold: true }), am("마스킹한 경우 vs 토큰을 실제로 제거한 경우의 예측 비교"),
     am("100% 일치", { bold: true, color: C.green })],
    [am("차단 확인", { bold: true }), am("차단한 층에서 해당 이미지가 받는 주목량을 직접 관측"),
     am("정확히 0", { bold: true, color: C.green })],
    [am("채점 타당성", { bold: true }), am("사진 1장만 줬을 때의 정답률을 공개 보고치와 비교"),
     am("~80%대로 일치", { color: C.green })],
    [am("위치 영향", { bold: true }), am("사진 순서를 뒤집어 전체 재측정 (문항 600개)"),
     am("결론 방향 동일", { color: C.green })],
  ], { x: 0.55, y: 1.72, w: 12.25, rowH: [0.42, 0.44, 0.44, 0.44, 0.44], ...ATBL });
  s.addText("마스킹은 softmax 이전 단계에서 해당 열에 −∞를 더하는 방식입니다. 수학적으로 그 토큰이 없는 것과 동일하며, 위 첫 줄이 그것을 실측으로 확인한 것입니다.", {
    x: 0.55, y: 4.1, w: 12.25, h: 0.4, fontFace: F, fontSize: 11, color: C.navy, margin: 0 });
}

// A3 — 경로 분해 전체
{
  const s = apx("경로 분해 — 전체 수치",
    "판별력 점수 · 문항 300개 · 사진 순서를 바꿔 두 배치에서 각각 측정");
  s.addTable([
    [am("", AH), am("배치", AH), am("아무것도\n안 함", AH), am("경로 A 끊음\n(사진끼리)", AH),
     am("경로 B 끊음\n(질문의 읽기)", AH), am("통째로 뺌", AH)],
    [am("3B", { bold: true }), am("원래 순서"), am("0.6970"), am("0.4030", { bold: true, color: C.red }),
     am("0.9057", { bold: true, color: C.green }), am("0.9057")],
    [am(""), am("뒤집은 순서"), am("0.8000"), am("0.5679", { bold: true, color: C.red }),
     am("0.9078", { bold: true, color: C.green }), am("0.8894")],
    [am("7B", { bold: true }), am("원래 순서"), am("0.8690"), am("0.4471", { bold: true, color: C.red }),
     am("0.8993", { bold: true, color: C.green }), am("0.8993")],
    [am(""), am("뒤집은 순서"), am("0.8781"), am("0.4480", { bold: true, color: C.red }),
     am("0.8983", { bold: true, color: C.green }), am("0.8949")],
  ], { x: 0.55, y: 1.72, w: 12.25, rowH: [0.56, 0.4, 0.4, 0.4, 0.4], ...ATBL });
  s.addText([
    { text: "원래 순서에서 '경로 B 끊음 = 통째로 뺌'이 소수점까지 같은 것은 구조상 당연합니다", options: { fontSize: 11, bold: true, color: C.navy, breakLine: true } },
    { text: "질문 대상 사진이 앞에 있으면 무관한 사진을 볼 수 없으므로, 남는 길이 읽기 하나뿐입니다. 저희 구현이 정확하다는 검증으로 보시면 됩니다.", options: { fontSize: 10.5, color: C.gray, breakLine: true } },
    { text: "뒤집은 순서에서는 질문 대상 사진이 뒤에 있어 무관한 사진을 볼 수 있습니다 — 즉 '섞임' 경로가 실제로 존재합니다. 그런데도 그 경로를 끊으면 크게 나빠지고(−0.23), 읽기만 끊는 편이 통째로 빼는 것보다 낫습니다(+0.018, 유의).", options: { fontSize: 10.5, color: C.navy } },
  ], { x: 0.55, y: 4.06, w: 12.25, h: 1.3, fontFace: F, margin: 0, paraSpaceAfter: 5 });
  s.addText("사전에 적어둔 예측 두 개가 모두 틀렸고(읽기만으로는 부족할 것 / 섞임 차단이 도움될 것), 틀린 방향이 결론을 강화했습니다.", {
    x: 0.55, y: 5.5, w: 12.25, h: 0.34, fontFace: F, fontSize: 10.5, italic: true, color: C.gray, margin: 0 });
}

// A4 — 판별력 손상 전체
{
  const s = apx("무관한 사진이 늘어날 때 — 전체 수치",
    "판별력 점수 · 문항 300개 · 정답 균형 150/150 · '차단'은 어느 것이 무관한지 알려준 조건(상한값)");
  s.addTable([
    [am("무관한 사진 수", AH), am("3B 아무것도 안 함", AH), am("3B 차단", AH), am("회복률", AH),
     am("7B 아무것도 안 함", AH), am("7B 차단", AH)],
    [am("0 (한 장만)", { bold: true }), am("0.9078", { bold: true }), am("—"), am("—"),
     am("0.9033", { bold: true }), am("—")],
    [am("1", { bold: true }), am("0.6978"), am("0.9058"), am("99%", { bold: true, color: C.green }),
     am("0.8690"), am("0.8993")],
    [am("2", { bold: true }), am("0.6063"), am("0.9037"), am("99%", { bold: true, color: C.green }),
     am("0.8723"), am("0.8970")],
    [am("3", { bold: true }), am("0.5213", { bold: true, color: C.red }), am("0.9041"),
     am("99%", { bold: true, color: C.green }), am("0.8740"), am("0.8957")],
  ], { x: 0.55, y: 1.72, w: 12.25, rowH: [0.5, 0.4, 0.4, 0.4, 0.44], ...ATBL });
  const notes = [
    ["손상이 사진 수에 비례하는가", "3B는 예 (사진 3장에서 −0.386, 95%CI [−0.217, −0.136]로 유의). 7B는 아니오 — 손상이 −0.03로 고정되어 늘지 않음"],
    ["정답률로 보면", "3B는 사진 3장에서 0.460 — 찍기(0.50)보다도 낮습니다. 차단하면 0.820으로 복귀"],
    ["회복률이 일정한 이유", "정보가 파괴된 것이 아니라 가려져 있었기 때문입니다. 몇 장이 가리든 걷어내면 원래대로 돌아옵니다"],
  ];
  notes.forEach((n, i) => {
    const y = 4.1 + i * 0.72;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y, w: 12.25, h: 0.64, rectRadius: 0.06,
      fill: { color: i % 2 ? C.light : C.lightgray } });
    s.addText(n[0], { x: 0.8, y, w: 3.1, h: 0.64, fontFace: F, fontSize: 10.5, bold: true,
      color: C.navy, margin: 0, valign: "middle" });
    s.addText(n[1], { x: 4.0, y, w: 8.6, h: 0.64, fontFace: F, fontSize: 10,
      color: C.navy, margin: 0, valign: "middle" });
  });
}

// A5 — 하나씩 빼보기 상세
{
  const s = apx("'하나씩 빼보기' 판별 — 상세",
    "각 사진을 하나씩 빼보고 답이 가장 크게 흔들리는 것을 '필요한 사진'으로 판정. 위치를 참조하지 않음");
  s.addTable([
    [am("", AH), am("무관한\n사진 수", AH), am("판별 정확도", AH), am("무작위로\n찍으면", AH),
     am("이만큼은 맞혀야\n이득 (손익 기준선)", AH), am("아무것도\n안 했을 때", AH), am("판별기까지\n포함한 성능", AH)],
    [am("3B", { bold: true }), am("1"), am("0.693"), am("0.500"), am("0.761", { color: C.red }),
     am("0.6978"), am("0.6669  (−3.1%p)", { color: C.red })],
    [am(""), am("2"), am("0.707"), am("0.333"), am("0.661"), am("0.6063"),
     am("0.7126  (+10.6%p)", { bold: true, color: C.green })],
    [am(""), am("3"), am("0.730", { bold: true }), am("0.250"), am("0.569", { bold: true, color: C.green }),
     am("0.5213"), am("0.7028  (+18.2%p)", { bold: true, color: C.green })],
    [am("7B", { bold: true }), am("1"), am("0.953", { bold: true, color: C.blue }), am("0.500"),
     am("0.966", { color: C.red }), am("0.8690"), am("0.8884  (+1.9%p)")],
    [am(""), am("3"), am("0.937", { bold: true, color: C.blue }), am("0.250"),
     am("0.975", { color: C.red }), am("0.8740"), am("0.8928  (+1.9%p)")],
  ], { x: 0.55, y: 1.72, w: 12.25, rowH: [0.58, 0.38, 0.38, 0.42, 0.38, 0.38], ...ATBL });
  s.addText([
    { text: "두 곡선이 반대로 움직입니다 (3B)", options: { fontSize: 11.5, bold: true, color: C.navy, breakLine: true } },
    { text: "무관한 사진이 늘수록 판별은 정확해지고(0.693 → 0.730), 이득을 내기 위해 넘어야 할 기준선은 내려갑니다(0.761 → 0.569). 손상이 클수록 잘못 골랐을 때의 상대적 손해가 작아지고, 동시에 '빼봤을 때의 흔들림' 신호가 강해지기 때문입니다.", options: { fontSize: 10.5, color: C.navy, breakLine: true } },
    { text: "7B는 판별이 0.95로 훨씬 정확한데도 기준선이 0.97이라 순이득이 남지 않습니다 — 고칠 손상 자체가 작기 때문입니다. 이 방법의 가치는 작은 모델 + 무관 입력이 많은 상황에 있습니다.", options: { fontSize: 10.5, color: C.navy } },
  ], { x: 0.55, y: 4.42, w: 12.25, h: 1.5, fontFace: F, margin: 0, paraSpaceAfter: 5 });
  s.addText("'판별기까지 포함한 성능'의 2·3장 값은 잘못 골랐을 때의 조건을 근사한 낙관값입니다. 판별 정확도와 기준선은 정확한 값이며, 0.730 > 0.569 판정은 근사에 의존하지 않습니다.", {
    x: 0.55, y: 6.06, w: 12.25, h: 0.4, fontFace: F, fontSize: 9.5, italic: true, color: C.gray, margin: 0 });
}

// A6 — 선행연구
{
  const s = apx("선행연구 5편 — 원문 대조 결과",
    "고위협 논문은 초록이 아니라 본문까지 확인했습니다");
  s.addTable([
    [am("", AH), am("무엇을 하나", AH), am("층 단위\n개입", AH), am("학습\n불필요", AH),
     am("무관 사진\n실험", AH), am("우리와의 관계", AH)],
    [am("FOCUS\n2508.13744", { bold: true }), am("타깃 외 사진을 픽셀 노이즈로 덮고 N+1회 실행", { fontSize: 9.5 }),
     am("없음", { color: C.red }), am("예"), am("없음", { color: C.red }),
     am("사진을 통째로 지움 — 우리 처방을 표현 불가", { fontSize: 9.5 })],
    [am("MIMIC\n2601.07812", { bold: true }), am("12~23층에서 사진 간 연결을 일괄 차단", { fontSize: 9.5 }),
     am("예"), am("아니오", { color: C.red }), am("있음"),
     am("모든 사진 간 연결을 균일하게 막음", { fontSize: 9.5 })],
    [am("CAPL\n2603.07048", { bold: true }), am("사진 간 연결을 오히려 늘림 + 선호학습", { fontSize: 9.5 }),
     am("예"), am("아니오", { color: C.red }), am("없음", { color: C.red }),
     am("진단이 정반대 — 무관 사진 상황 미실험", { fontSize: 9.5 })],
    [am("SoFA\nCVPR 2025", { bold: true }), am("두 종류 마스크를 섞어 2개 층마다 삽입", { fontSize: 9.5 }),
     am("예"), am("예"), am("없음", { color: C.red }),
     am("역시 '늘리는' 방향", { fontSize: 9.5 })],
    [am("RSCD\n2603.23934", { bold: true }), am("중간 층에서 글자끼리의 연결을 차단", { fontSize: 9.5 }),
     am("예"), am("예"), am("있음"),
     am("대상이 사진이 아니라 글자 — 개입 대상이 다름", { fontSize: 9.5 })],
  ], { x: 0.55, y: 1.72, w: 12.25, rowH: [0.54, 0.5, 0.44, 0.44, 0.44, 0.44], ...ATBL });
  s.addText("조사 결과 저희가 처음에 새롭다고 생각했던 세 가지 — 학습 없는 개입, 층 단위 개입, 개입을 통한 원인 검증 — 는 모두 선점되어 있었습니다. 그래서 novelty의 무게중심을 '무엇을 끊는가'로 옮겼습니다.", {
    x: 0.55, y: 4.6, w: 12.25, h: 0.5, fontFace: F, fontSize: 10.5, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.2 });
}

// A7 — 사전등록 이력
{
  const s = apx("사전 등록 이력 — 실패도 그대로 기록했습니다",
    "실험 전에 판정 기준을 문서로 고정하고 커밋한 뒤 실행했습니다");
  s.addTable([
    [am("무엇을 물었나", AH), am("미리 정한 기준", AH), am("결과", AH), am("판정", AH)],
    [am("무관 사진이 늘면 오염도 늘어나는가 (7B)", { fontSize: 10 }), am("10%p 이상 & 유의", { fontSize: 10 }),
     am("+2.7%p, p=0.28", { fontSize: 10 }), am("실패", { bold: true, color: C.red })],
    [am("판별력 손상이 사진 수에 비례하는가 (7B)", { fontSize: 10 }), am("−0.020 이하 & 유의", { fontSize: 10 }),
     am("+0.005, 0 포함", { fontSize: 10 }), am("실패", { bold: true, color: C.red })],
    [am("같은 질문 (3B)", { fontSize: 10 }), am("동일", { fontSize: 10 }),
     am("−0.177, 유의", { fontSize: 10 }), am("통과", { bold: true, color: C.green })],
    [am("얕은 층에서 무관 사진을 판별할 수 있는가", { fontSize: 10 }), am("16층 이하에서 0.80 이상", { fontSize: 10 }),
     am("최고 0.517", { fontSize: 10 }), am("실패", { bold: true, color: C.red })],
    [am("섞임 경로가 해로운가 (뒤집은 배치)", { fontSize: 10 }), am("차단 시 개선될 것", { fontSize: 10 }),
     am("−0.232 악화", { fontSize: 10 }), am("예측 반대", { bold: true, color: C.orange })],
    [am("모두 필요한 질문에서 사진 고립이 무해한가", { fontSize: 10 }), am("−0.02 이내", { fontSize: 10 }),
     am("−0.055 (유의)", { fontSize: 10 }), am("불성립", { bold: true, color: C.orange })],
  ], { x: 0.55, y: 1.72, w: 12.25, rowH: [0.44, 0.42, 0.42, 0.42, 0.42, 0.42, 0.42], ...ATBL });
  s.addText([
    { text: "6건 중 3건이 기준 미달, 2건은 예측과 반대 방향이었습니다.", options: { fontSize: 11.5, bold: true, color: C.navy, breakLine: true } },
    { text: "특히 다섯 번째는 저희 가설을 정면으로 반박한 결과인데, 그 반박이 오히려 지금의 결론(섞임은 보호막)을 만들었습니다. 결과를 보고 기준을 바꾸지 않았고, 실패한 것은 실패로 두었습니다.", options: { fontSize: 10.5, color: C.navy } },
  ], { x: 0.55, y: 4.86, w: 12.25, h: 0.9, fontFace: F, margin: 0, paraSpaceAfter: 5 });
}

// A8 — 층별 상세 수치
{
  const s = apx("층별 개입 시점 — 상세 수치",
    "판별력 점수 · 문항 300개 · '몇 층부터 막기 시작하는가'를 바꿔가며 측정");
  s.addTable([
    [am("", AH), am("아무것도\n안 함", AH), am("0층부터", AH), am("8층부터", AH),
     am("16층부터", AH), am("24층부터", AH), am("전면 차단", AH)],
    [am("3B (36층)", { bold: true }), am("0.6970"), am("0.9057", { bold: true }),
     am("0.8992"), am("0.8394"), am("0.7153", { color: C.red }), am("0.9057")],
    [am("효과 잔존", { fontSize: 9.5, color: C.gray }), am("0%", { fontSize: 9.5, color: C.gray }),
     am("100%", { fontSize: 9.5, color: C.gray }), am("97%", { fontSize: 10, bold: true, color: C.green }),
     am("68%", { fontSize: 9.5, color: C.orange }), am("9%", { fontSize: 9.5, color: C.red }),
     am("100%", { fontSize: 9.5, color: C.gray })],
    [am("7B (28층)", { bold: true }), am("0.8690"), am("0.8993", { bold: true }),
     am("0.8925"), am("0.8542"), am("0.8693", { color: C.red }), am("0.8993")],
    [am("효과 잔존", { fontSize: 9.5, color: C.gray }), am("0%", { fontSize: 9.5, color: C.gray }),
     am("100%", { fontSize: 9.5, color: C.gray }), am("78%", { fontSize: 10, bold: true, color: C.green }),
     am("−48%", { fontSize: 9.5, color: C.red }), am("1%", { fontSize: 9.5, color: C.red }),
     am("100%", { fontSize: 9.5, color: C.gray })],
  ], { x: 0.55, y: 1.7, w: 12.25, rowH: [0.5, 0.36, 0.28, 0.36, 0.28], ...ATBL });

  s.addText("판별용 반사실은 몇 층부터 다시 계산해도 되는가 (3B, 무관 사진 3장)", { x: 0.55, y: 3.6,
    w: 12.25, h: 0.28, fontFace: F, fontSize: 12, bold: true, color: C.navy, margin: 0 });
  s.addTable([
    [am("다시 계산 시작 층", AH), am("0층 (전체)", AH), am("8층", AH), am("16층", AH), am("24층", AH)],
    [am("판별 정확도", { bold: true }), am("0.7300"), am("0.7200"),
     am("0.7200", { bold: true, color: C.green }), am("0.6400", { color: C.red })],
    [am("반사실 1회 비용", { bold: true }), am("100%"), am("78%"),
     am("56%", { bold: true, color: C.green }), am("33%")],
  ], { x: 0.55, y: 3.94, w: 12.25, rowH: [0.36, 0.34, 0.34], ...ATBL });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.1, w: 12.25, h: 1.0,
    rectRadius: 0.08, fill: { color: C.lightblue }, line: { color: C.blue, width: 1.25 } });
  s.addText([
    { text: "두 표가 서로 다른 것을 말합니다", options: { fontSize: 12, bold: true, color: C.blue, breakLine: true } },
    { text: "위 표(고치는 일): 손상은 앞쪽부터 쌓이므로 8층 전에 막아야 합니다.   아래 표(가려내는 일): 판별 단서는 16층까지 남아 있어 절반만 다시 계산해도 됩니다.\n같은 '층'이지만 목적이 다르면 필요한 시점이 다릅니다 — 이것이 파이프라인을 싸게 만드는 근거입니다.", options: { fontSize: 10.5, color: C.navy } },
  ], { x: 0.85, y: 5.18, w: 11.7, h: 0.86, fontFace: F, margin: 0, paraSpaceAfter: 4 });
}

// A9 — 비용 구조
{
  const s = apx("비용 구조 — 왜 픽셀을 건드리면 비싼가",
    "3B · 이미지 4장 · 같은 하드웨어에서 각 부분을 따로 측정");
  s.addTable([
    [am("측정 항목", AH), am("시간", AH), am("설명", AH)],
    [am("전체 forward 1회", { bold: true }), am("867.8 ms"), am("이미지 인코딩 + 언어모델 전체")],
    [am("이미지 인코딩만", { bold: true }), am("591.1 ms", { bold: true, color: C.red }),
     am("전체의 68.1% — 여기가 대부분입니다", { bold: true })],
    [am("언어모델 부분만", { bold: true }), am("276.6 ms"), am("나머지 31.9%")],
  ], { x: 0.55, y: 1.72, w: 12.25, rowH: [0.4, 0.38, 0.42, 0.38], ...ATBL });

  const cmp = [
    ["기존 방식 (픽셀을 노이즈로 덮음)", "이미지를 바꾸므로 매번 인코딩을 다시 해야 합니다.\n판별에 4번 실행하면 인코딩 비용 68%를 네 번 지불합니다.", C.red, C.lightred],
    ["우리 방식 (attention만 막음)", "픽셀이 그대로이므로 인코딩을 재사용할 수 있고,\n판별용 계산은 16층부터만 하면 됩니다.", C.green, C.lightgreen],
  ];
  cmp.forEach((c, i) => {
    const x = 0.55 + i * 6.23;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.5, w: 6.02, h: 1.3, rectRadius: 0.08,
      fill: { color: c[3] }, line: { color: c[2], width: 1.25 } });
    s.addText(c[0], { x: x + 0.22, y: 3.62, w: 5.6, h: 0.28, fontFace: F, fontSize: 12,
      bold: true, color: c[2], margin: 0 });
    s.addText(c[1], { x: x + 0.22, y: 3.94, w: 5.6, h: 0.72, fontFace: F, fontSize: 10.5,
      color: C.navy, margin: 0, lineSpacingMultiple: 1.2 });
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 4.96, w: 12.25, h: 1.4,
    rectRadius: 0.08, fill: { color: C.lightred }, line: { color: C.red, width: 1.5 } });
  s.addText("여기서 멈춰야 합니다 — 아직 \"더 싸다\"고 말할 수 없습니다", { x: 0.85, y: 5.08,
    w: 11.7, h: 0.28, fontFace: F, fontSize: 12.5, bold: true, color: C.red, margin: 0 });
  s.addText("측정한 것은 '이미지 인코딩이 전체의 68%를 차지한다'까지입니다. 그것을 건너뛰는 구현(인코딩 캐시 재사용 + 층 절단)은 아직 만들지 않았고,\n따라서 절감률은 부품 값에서 계산한 추정치일 뿐 종단 측정이 아닙니다. 이전에 이론 42% 절감이 실측 9.7%로 줄어든 경험이 있어, 구현 전에는 수치를 주장하지 않습니다.", {
    x: 0.85, y: 5.42, w: 11.7, h: 0.86, fontFace: F, fontSize: 10.5, color: C.navy,
    margin: 0, lineSpacingMultiple: 1.25 });
}

pres.writeFile({ fileName: "/Users/hansangmin/Source-Depth/meeting/_generated/deck_v6.pptx" })
  .then(() => console.log("DECK v6 WRITTEN"));
