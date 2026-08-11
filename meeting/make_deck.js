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
const W = 13.33, H = 7.5;

// ---------- helpers ----------
function kicker(s, txt, dark) {
  s.addText(txt, { x: 0.55, y: 0.28, w: 9.5, h: 0.32, fontFace: F, fontSize: 11,
    bold: true, color: dark ? "9FB8CE" : C.gray, charSpacing: 2, margin: 0 });
}
function headline(s, txt, dark, wOverride) {
  s.addText(txt, { x: 0.55, y: 0.58, w: wOverride || 12.2, h: 0.75, fontFace: F,
    fontSize: 23, bold: true, color: dark ? C.white : C.navy, margin: 0 });
}
function tag(s, txt, fill) {
  const w = 0.28 + txt.length * 0.105;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: W - 0.55 - w, y: 0.30, w: w, h: 0.34,
    fill: { color: fill }, rectRadius: 0.17 });
  s.addText(txt, { x: W - 0.55 - w, y: 0.30, w: w, h: 0.34, align: "center",
    fontFace: F, fontSize: 10.5, bold: true, color: C.white, margin: 0 });
}
function pendTag(s) { tag(s, "미확정 · 내일 오전 업데이트", C.orange); }
function footer(s, txt, dark) {
  s.addText(txt, { x: 0.55, y: 7.02, w: 12.2, h: 0.34, fontFace: F, fontSize: 10,
    color: dark ? "8AA5BC" : C.gray, margin: 0 });
}
function statCard(s, x, y, w, h, title, num, sub, color, darkCard) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08,
    fill: { color: darkCard ? "1D3850" : C.light }, line: { color: darkCard ? "2E4E6B" : C.line, width: 0.75 } });
  s.addText(title, { x: x + 0.18, y: y + 0.12, w: w - 0.36, h: 0.3, fontFace: F,
    fontSize: 11.5, bold: true, color: darkCard ? "AFC6DA" : C.gray, margin: 0 });
  s.addText(num, { x: x + 0.18, y: y + 0.38, w: w - 0.36, h: 0.62, fontFace: F,
    fontSize: 27, bold: true, color, margin: 0 });
  s.addText(sub, { x: x + 0.18, y: y + 1.0, w: w - 0.36, h: h - 1.1, fontFace: F,
    fontSize: 10.5, color: darkCard ? "9FB8CE" : C.gray, margin: 0 });
}
function bar(s, x, yBase, w, hMax, frac, color, valTxt, label, outline) {
  const bh = Math.max(0.03, hMax * frac);
  s.addShape(pres.shapes.RECTANGLE, { x, y: yBase - bh, w, h: bh,
    fill: outline ? { color: C.white } : { color }, line: { color, width: outline ? 1.5 : 0 } });
  s.addText(valTxt, { x: x - 0.25, y: yBase - bh - 0.34, w: w + 0.5, h: 0.3, align: "center",
    fontFace: F, fontSize: 13, bold: true, color, margin: 0 });
  s.addText(label, { x: x - 0.35, y: yBase + 0.06, w: w + 0.7, h: 0.52, align: "center",
    fontFace: F, fontSize: 10.5, color: C.navy, margin: 0 });
}

// =====================================================================
// S1 — 표지 + 한 장 요약 (dark)
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.darkbg };
  s.addText("SOURCEDEPTH · PHASE 0 FEASIBILITY · 2026-08-12 미팅", { x: 0.6, y: 0.45,
    w: 7, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: "8AA5BC", charSpacing: 2, margin: 0 });
  s.addText("멀티이미지 환각의 원인을 depth에서 찾고,\n같은 지점에서 계산도 줄인다", { x: 0.6, y: 0.95,
    w: 6.3, h: 1.9, fontFace: F, fontSize: 28, bold: true, color: C.white, margin: 0, lineSpacingMultiple: 1.15 });
  s.addText("이미지별 적응적 깊이 배분 (per-image adaptive depth) — 24시간 검증 실험 결과", {
    x: 0.6, y: 2.9, w: 6.2, h: 0.4, fontFace: F, fontSize: 13, color: "AFC6DA", margin: 0 });
  s.addText("IMML Lab · 한상민", { x: 0.6, y: 3.35, w: 6, h: 0.35, fontFace: F, fontSize: 12,
    color: "8AA5BC", margin: 0 });
  s.addImage({ path: R + "fig3_opposite_depth_policies.png", x: 7.05, y: 0.85, w: 5.7, h: 3.35 });
  s.addText("같은 개입, 정반대 결과 — 오늘의 핵심 그림", { x: 7.05, y: 4.22, w: 5.7, h: 0.3,
    align: "center", fontFace: F, fontSize: 10.5, italic: true, color: "9FB8CE", margin: 0 });
  const bw = 2.95, bx0 = 0.6, gap = 0.13, by = 4.85, bh = 1.95;
  statCard(s, bx0, by, bw, bh, "① 문제 실재", "flip 21.3%", "distractor가 답을 뒤집음\n(대조군 0.0%) · 사전 등록 PASS", "FF8A80", true);
  statCard(s, bx0 + (bw + gap), by, bw, bh, "② 메커니즘", "회복 81%", "layer-4 이후 차단만으로\n(McNemar p = 6×10⁻⁷)", "7EC8F5", true);
  statCard(s, bx0 + 2 * (bw + gap), by, bw, bh, "②″ 인과 확인", "0.79 → 0.50", "관련 이미지를 차단하면 붕괴\n(p = 4×10⁻³⁸)", "FFC94D", true);
  statCard(s, bx0 + 3 * (bw + gap), by, bw, bh, "③ 컨트롤러 신호", "99.8%", "layer-8 단일 head 식별률\n(위치 편향 검증은 진행 중)", "8CE0B0", true);
  s.addNotes("결론부터: 같은 개입인데 질문 유형에 따라 +21%p와 -51%p로 갈립니다. 고정 depth로는 둘 다 만족할 수 없고, 그게 이 연구의 존재 이유입니다. 지금부터 이 그림이 나오기까지를 보여드리겠습니다.");
}

// =====================================================================
// S2 — 문제
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "문제");
  headline(s, "이미지가 여러 장 들어가면, 모델은 정보의 '출처'를 혼동한다");
  // 좌: 도식
  const dx = 0.55, dy = 1.7;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: dx, y: dy, w: 2.5, h: 1.5, rectRadius: 0.08,
    fill: { color: C.light }, line: { color: C.blue, width: 2 } });
  s.addText([{ text: "이미지 1", options: { bold: true, color: C.navy, fontSize: 13, breakLine: true } },
    { text: "파란 모자", options: { color: C.blue, fontSize: 15, bold: true } }],
    { x: dx, y: dy + 0.3, w: 2.5, h: 0.9, align: "center", fontFace: F, margin: 0 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: dx + 2.8, y: dy, w: 2.5, h: 1.5, rectRadius: 0.08,
    fill: { color: C.light }, line: { color: C.red, width: 2 } });
  s.addText([{ text: "이미지 2 (distractor)", options: { bold: true, color: C.navy, fontSize: 13, breakLine: true } },
    { text: "빨간 모자", options: { color: C.red, fontSize: 15, bold: true } }],
    { x: dx + 2.8, y: dy + 0.3, w: 2.5, h: 0.9, align: "center", fontFace: F, margin: 0 });
  s.addText("Q. \"1번 이미지 사람의 모자 색은?\"", { x: dx, y: dy + 1.75, w: 5.3, h: 0.4,
    align: "center", fontFace: F, fontSize: 13.5, bold: true, color: C.navy, margin: 0 });
  s.addShape(pres.shapes.DOWN_ARROW, { x: dx + 2.45, y: dy + 2.2, w: 0.4, h: 0.5, fill: { color: C.gray } });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: dx + 1.15, y: dy + 2.85, w: 3.0, h: 0.85, rectRadius: 0.1,
    fill: { color: C.lightred }, line: { color: C.red, width: 1.5 } });
  s.addText([{ text: "\"빨간색\"  ✗", options: { bold: true, fontSize: 17, color: C.red, breakLine: true } },
    { text: "2번 이미지에서 온 정보", options: { fontSize: 10.5, color: C.gray } }],
    { x: dx + 1.15, y: dy + 2.9, w: 3.0, h: 0.8, align: "center", fontFace: F, margin: 0 });
  // 우: 실측 카드
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.7, y: 1.75, w: 6.05, h: 3.9, rectRadius: 0.1,
    fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText("실측 — 같은 문항에 distractor 1장만 추가하면 (셀 1)", { x: 7.0, y: 2.0, w: 5.5, h: 0.35,
    fontFace: F, fontSize: 12.5, bold: true, color: C.gray, margin: 0 });
  s.addText([
    { text: "89.3%", options: { fontSize: 40, bold: true, color: C.blue } },
    { text: "   →   ", options: { fontSize: 28, color: C.gray } },
    { text: "72.0%", options: { fontSize: 40, bold: true, color: C.red } },
  ], { x: 7.0, y: 2.45, w: 5.5, h: 0.9, fontFace: F, margin: 0 });
  s.addText("−17.3%p  (단일 이미지 → 2장, 동일 질문·동일 정답)", { x: 7.0, y: 3.45, w: 5.5, h: 0.35,
    fontFace: F, fontSize: 13, bold: true, color: C.red, margin: 0 });
  s.addText([
    { text: "선행 연구가 명명한 실패 모드: cross-image leakage (FOCUS '25), multi-view hallucination (MVH-Bench '26)", options: { breakLine: true, bullet: true } },
    { text: "기존 해법은 전부 full-depth 전제 + 계산을 더 씀 (FOCUS: 이미지 N장에 N+1회 forward)", options: { bullet: true } },
  ], { x: 7.0, y: 3.95, w: 5.55, h: 1.55, fontFace: F, fontSize: 12, color: C.navy,
    margin: 0, paraSpaceAfter: 8 });
  s.addNotes("문제 자체는 알려져 있습니다. 저희 기여는 '이 오염이 어느 깊이에서 생기는가'를 측정하고, '계산을 줄이면서' 고치는 데 있습니다.");
}

// =====================================================================
// S3 — 가설과 개입
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "가설과 개입");
  headline(s, "이미지 간 정보가 섞이는 유일한 통로 = layer마다 한 번의 self-attention");
  const panels = [
    { x: 1.0, title: "기존: full depth 실행", blockFrom: 99, cap: "모든 layer에서 혼합\n= 출처 오염 누적", col: C.red },
    { x: 7.2, title: "개입: layer L 이후 distractor KV 차단", blockFrom: 2, cap: "L 이후 직접 참조 불가\n= 구조적 차단 + 연산 절감", col: C.green },
  ];
  panels.forEach(p => {
    s.addText(p.title, { x: p.x, y: 1.62, w: 5.1, h: 0.35, fontFace: F, fontSize: 13.5,
      bold: true, color: C.navy, margin: 0, align: "center" });
    for (let i = 0; i < 5; i++) {
      const y = 2.05 + i * 0.62;
      const blocked = i >= p.blockFrom;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: p.x, y, w: 5.1, h: 0.5, rectRadius: 0.06,
        fill: { color: blocked ? C.lightgray : C.light }, line: { color: C.line, width: 0.75 } });
      s.addText(`L${i + 1}`, { x: p.x + 0.12, y, w: 0.7, h: 0.5, fontFace: F, fontSize: 11,
        bold: true, color: C.gray, margin: 0, valign: "middle" });
      s.addText("img1 ●", { x: p.x + 0.9, y, w: 1.35, h: 0.5, fontFace: F, fontSize: 12,
        bold: true, color: C.blue, margin: 0, valign: "middle" });
      s.addText(blocked ? "⇥" : "⇄", { x: p.x + 2.25, y, w: 0.7, h: 0.5, align: "center",
        fontFace: F, fontSize: 16, bold: true, color: blocked ? C.green : C.red, margin: 0, valign: "middle" });
      s.addText(blocked ? "img2 ✕" : "img2 ●", { x: p.x + 3.0, y, w: 1.5, h: 0.5, fontFace: F,
        fontSize: 12, bold: true, color: blocked ? C.gray : C.red, margin: 0, valign: "middle" });
    }
    s.addText(p.cap, { x: p.x, y: 5.25, w: 5.1, h: 0.7, align: "center", fontFace: F,
      fontSize: 11.5, bold: true, color: p.col, margin: 0 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.15, w: 12.25, h: 0.95, rectRadius: 0.08,
    fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText([
    { text: "차단 = softmax 분모에서 제외 = 그 토큰이 \"없는 것\"과 수학적으로 동일 (근사 억제가 아님)", options: { bold: true, color: C.navy, breakLine: true } },
    { text: "단, L 이전에 이미 전파된 정보는 남음 — 실측 잔여 효과: 오답의 19% 이하", options: { color: C.gray } },
  ], { x: 0.85, y: 6.25, w: 11.8, h: 0.8, fontFace: F, fontSize: 12, margin: 0, paraSpaceAfter: 4 });
  s.addNotes("실행 layer 수 = 이미지 간 정보가 섞일 수 있었던 횟수입니다. 무관 이미지를 후반에서 차단하면 오답 회복과 계산 절감이 동시에 일어난다는 게 가설입니다. 단서 하나 — L 이전 전파는 못 막습니다. 그 잔여 효과가 얼마인지도 수치로 쟀고, 19% 이하였습니다.");
}

// =====================================================================
// S4 — 실험 설계
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "실험 설계 — 왜 이렇게 짰는가");
  headline(s, "반증 가능하도록 설계했다 — 대조군 · 양방향 · 역방향 컨트롤");
  // 좌: 4셀 표
  const rows = [
    [{ text: "", options: {} }, { text: "distractor에 질의 객체 있음", options: { bold: true, color: C.white, fill: { color: C.navy } } }, { text: "없음", options: { bold: true, color: C.white, fill: { color: C.navy } } }],
    [{ text: "정답 No", options: { bold: true, color: C.white, fill: { color: C.navy } } },
     { text: "셀1 · 주 leak 측정\n(No→Yes 뒤집힘 예상)", options: { fill: { color: C.lightred }, bold: true, color: C.red } },
     { text: "셀3 · 대조군", options: { fill: { color: C.lightgray }, color: C.gray } }],
    [{ text: "정답 Yes", options: { bold: true, color: C.white, fill: { color: C.navy } } },
     { text: "셀4 · 대조군", options: { fill: { color: C.lightgray }, color: C.gray } },
     { text: "셀2 · 역방향 leak\n(Yes→No)", options: { fill: { color: C.lightred }, bold: true, color: C.red } }],
  ];
  s.addTable(rows, { x: 0.55, y: 1.75, w: 6.1, rowH: [0.5, 1.05, 1.05], fontFace: F, fontSize: 11.5,
    align: "center", valign: "middle", border: { pt: 1, color: "FFFFFF" } });
  s.addText("셀당 150문항 × 4 = 600 · POPE(COCO) adversarial · distractor 조건은 COCO annotation으로 검증", {
    x: 0.55, y: 4.55, w: 6.1, h: 0.55, fontFace: F, fontSize: 10.5, color: C.gray, margin: 0 });
  // 조건 축
  s.addText("문항당 10개 조건 (총 6,000 forward)", { x: 0.55, y: 5.2, w: 6.1, h: 0.3,
    fontFace: F, fontSize: 11.5, bold: true, color: C.navy, margin: 0 });
  const conds = [["S", "단독"], ["M", "2장 기준선"], ["T(L)", "L=4…24 차단"], ["T(0)", "완전 차단"], ["T-rel(8)", "역방향 컨트롤"]];
  conds.forEach((c, i) => {
    const cx = 0.55 + i * 1.24;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: 5.55, w: 1.14, h: 0.78, rectRadius: 0.08,
      fill: { color: i === 4 ? C.lightorange : C.light }, line: { color: i === 4 ? C.orange : C.line, width: 1 } });
    s.addText([{ text: c[0], options: { bold: true, fontSize: 12, color: C.navy, breakLine: true } },
      { text: c[1], options: { fontSize: 8.5, color: C.gray } }],
      { x: cx, y: 5.62, w: 1.14, h: 0.66, align: "center", fontFace: F, margin: 0 });
  });
  // 우: 타당성 3
  const vx = 7.1, vw = 5.65;
  s.addText("이 세팅이 타당한 이유", { x: vx, y: 1.75, w: vw, h: 0.35, fontFace: F, fontSize: 13.5,
    bold: true, color: C.navy, margin: 0 });
  const valid = [
    ["⇄", "양방향 측정", "셀1(No→Yes)·셀2(Yes→No)는 반대 방향 — 단일 편향(yes-bias)으로는 설명 불가"],
    ["◎", "Oracle 세팅", "관련 이미지를 알고 시작 — 가설 검증과 컨트롤러 성능을 분리"],
    ["⚠", "역방향 컨트롤 내장", "관련 이미지를 대신 차단하면 무너져야 정상 — 인과 확인 장치"],
  ];
  valid.forEach((v, i) => {
    const vy = 2.2 + i * 1.35;
    s.addShape(pres.shapes.OVAL, { x: vx, y: vy, w: 0.55, h: 0.55, fill: { color: C.navy } });
    s.addText(v[0], { x: vx, y: vy, w: 0.55, h: 0.55, align: "center", valign: "middle",
      fontFace: F, fontSize: 16, bold: true, color: C.white, margin: 0 });
    s.addText(v[1], { x: vx + 0.75, y: vy - 0.03, w: vw - 0.75, h: 0.35, fontFace: F,
      fontSize: 13.5, bold: true, color: C.navy, margin: 0 });
    s.addText(v[2], { x: vx + 0.75, y: vy + 0.33, w: vw - 0.75, h: 0.75, fontFace: F,
      fontSize: 11.5, color: C.gray, margin: 0 });
  });
  footer(s, "판정 기준은 실험 전에 문서로 동결(사전 등록)하고 결과를 보고 바꾸지 않음 — github.com/hsmai/Source-Depth");
  s.addNotes("'왜 이 세팅이 타당한가'의 답은 하나입니다 — 결과가 틀렸다면 틀렸다고 나오게 만들었습니다. 그리고 판정 기준을 결과를 보기 전에 문서로 박아두고 바꾸지 않았습니다.");
}

// =====================================================================
// S5 — 신뢰성
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "신뢰성");
  headline(s, "정합성 점검 3종을 통과한 뒤에야 본 실험에 들어갔다");
  const checks = [
    ["차단이 실제로 작동", "98.3%", "T(0) vs 단일이미지 예측 일치율\n차단 layer의 distractor attention 질량 = 정확히 0 (직접 관측)"],
    ["평가가 정상", "85.5%", "단일이미지 정답률\nPOPE 3B급 공개 보고치(~80%대)와 부합"],
    ["마스킹 ≡ 실제 제거", "100%", "토큰을 물리적으로 제거한 구현과\n예측 일치율 (n=40) — 등가성 검증"],
  ];
  checks.forEach((c, i) => {
    const x = 0.55 + i * 4.25, y = 1.9, w = 4.0, h = 3.4;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: C.lightgreen }, line: { color: C.green, width: 1 } });
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.25, w: 0.5, h: 0.5, fill: { color: C.green } });
    s.addText("✓", { x: x + 0.25, y: y + 0.25, w: 0.5, h: 0.5, align: "center", valign: "middle",
      fontFace: F, fontSize: 18, bold: true, color: C.white, margin: 0 });
    s.addText(c[0], { x: x + 0.9, y: y + 0.3, w: w - 1.1, h: 0.45, fontFace: F, fontSize: 14.5,
      bold: true, color: C.navy, margin: 0 });
    s.addText(c[1], { x: x + 0.28, y: y + 1.0, w: w - 0.56, h: 0.95, fontFace: F, fontSize: 42,
      bold: true, color: C.green, margin: 0 });
    s.addText(c[2], { x: x + 0.28, y: y + 2.05, w: w - 0.56, h: 1.25, fontFace: F, fontSize: 11.5,
      color: C.navy, margin: 0, lineSpacingMultiple: 1.15 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.75, w: 12.25, h: 0.75, rectRadius: 0.08,
    fill: { color: C.light } });
  s.addText("규모: 600문항 × 10조건 = 6,000 forward  ·  RTX 3090 1장 · 총 29분  ·  seed 42  ·  중단(BLOCKED) 0건  ·  실측 decoder 36 layers", {
    x: 0.85, y: 5.75, w: 11.8, h: 0.75, fontFace: F, fontSize: 12.5, bold: true, color: C.navy,
    margin: 0, valign: "middle" });
  s.addNotes("차단이 흉내가 아니라는 걸 두 방법으로 확인했습니다. attention 질량이 정확히 0인 것을 직접 관측했고, 토큰을 실제로 제거하는 구현과 예측이 100% 일치했습니다. 이 슬라이드가 있어야 뒤의 모든 숫자가 삽니다.");
}

// =====================================================================
// S6 — 결과 ①②
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "결과 ① ②  ·  사전 등록");
  headline(s, "distractor가 답의 21%를 뒤집고 — layer-4 차단이 그 81%를 회복시킨다");
  // 좌: flip 막대 (수동)
  s.addText("Flip Rate — 이미지 추가로 답이 뒤집힌 비율", { x: 0.55, y: 1.62, w: 4.6, h: 0.3,
    fontFace: F, fontSize: 12, bold: true, color: C.navy, margin: 0 });
  const yBase = 4.35, hMax = 2.1;
  bar(s, 0.85, yBase, 0.8, hMax, 0.213 / 0.25, C.red, "21.3%", "셀1\n주 leak");
  bar(s, 1.95, yBase, 0.8, hMax, 0.001, C.gray, "0.0%", "셀3\n대조군");
  bar(s, 3.05, yBase, 0.8, hMax, 0.127 / 0.25, C.red, "12.7%", "셀2\n역방향");
  bar(s, 4.15, yBase, 0.8, hMax, 0.047 / 0.25, C.gray, "4.7%", "셀4\n대조군");
  s.addShape(pres.shapes.LINE, { x: 0.7, y: yBase, w: 4.5, h: 0, line: { color: C.navy, width: 1.25 } });
  s.addText("객체가 distractor에 있을 때만 뒤집힘", { x: 0.55, y: 5.1, w: 4.6, h: 0.3,
    fontFace: F, fontSize: 10.5, italic: true, color: C.gray, margin: 0 });
  // 우: fig1
  s.addImage({ path: R + "fig1_accuracy_vs_L.png", x: 5.55, y: 1.7, w: 7.25, h: 2.97 });
  s.addText("T4 = 0.920 — 단일이미지(0.893)보다도 높음:  \"얕게 차단하는 것이 더 싸면서 더 정확하다\"", {
    x: 5.55, y: 4.72, w: 7.25, h: 0.34, align: "center", fontFace: F, fontSize: 11.5, bold: true,
    color: C.blue, margin: 0 });
  // 하단 3 스탯
  const stats = [["회복 81.0%  vs  피해 3.7%", "회복이 부수 피해의 22배 (셀1, T4)"],
    ["McNemar p = 6×10⁻⁷", "동일 문항 paired 검정 (셀1)"],
    ["이론 연산 절감 42.4%", "distractor 토큰이 36층 중 32층 생략"]];
  stats.forEach((t, i) => {
    const x = 0.55 + i * 4.25;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.5, w: 4.0, h: 0.95, rectRadius: 0.08,
      fill: { color: C.light } });
    s.addText([{ text: t[0], options: { bold: true, fontSize: 13.5, color: C.navy, breakLine: true } },
      { text: t[1], options: { fontSize: 10, color: C.gray } }],
      { x: x + 0.2, y: 5.56, w: 3.7, h: 0.85, fontFace: F, margin: 0 });
  });
  footer(s, "⚠ 역방향(셀2)은 확신도 높은 문항만 남기면 소멸(margin 민감도 분석, 부록 A3) — 주 증거는 셀1 + 인과 실험으로 구성");
  s.addNotes("margin 민감도 분석을 저희가 먼저 했고, 약한 축(셀2)은 약하다고 보고합니다. 그리고 T4가 단일 이미지보다 높다 — 제안서의 핵심 주장 '얕게 차단하는 것이 더 싸면서 더 정확하다'가 실측됐습니다.");
}

// =====================================================================
// S7 — 인과
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "결과 ②″ 인과  ·  사전 등록");
  headline(s, "관련 이미지를 '대신' 차단하자 0.79 → 0.50으로 붕괴 (p = 4×10⁻³⁸)");
  s.addImage({ path: R + "aux_chartC_negative_control.png", x: 0.55, y: 1.8, w: 7.35, h: 4.2 });
  const cards = [
    ["셀1 0.24 · 셀2 0.03", "모델이 distractor만 보고 답함 — 원본 정보가 정말로 사라짐", C.red],
    ["셀3 0.98 유지", "정답이 원래 '없음'인 셀은 그대로 — 답이 '보이는 이미지'를 정확히 따라감", C.gray],
    ["방향을 뒤집으면 효과도 뒤집힘", "상관이 아니라 인과 — 차단은 '약한 억제'가 아니라 구조적으로 완전함", C.navy],
  ];
  cards.forEach((c, i) => {
    const y = 1.9 + i * 1.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.15, y, w: 4.65, h: 1.28, rectRadius: 0.08,
      fill: { color: C.light }, line: { color: c[2], width: 1.25 } });
    s.addText([{ text: c[0], options: { bold: true, fontSize: 14, color: c[2], breakLine: true } },
      { text: c[1], options: { fontSize: 10.5, color: C.gray } }],
      { x: 8.38, y: y + 0.09, w: 4.2, h: 1.1, fontFace: F, margin: 0, paraSpaceAfter: 3 });
  });
  s.addNotes("'우연 아니냐'는 질문에 대한 답이 이 슬라이드입니다. p값이 10의 -38승입니다. 차단 방향을 뒤집으면 효과가 뒤집힙니다 — 인과입니다.");
}

// =====================================================================
// S8 — ★ 핵심: X자 교차
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "핵심 발견  ·  탐색적 (신규 relational 300문항)");
  headline(s, "질문 유형이 바뀌면 최적 depth가 정반대 — 고정 정책은 원리적으로 불가능");
  s.addImage({ path: R + "fig3_opposite_depth_policies.png", x: 1.95, y: 1.62, w: 8.15, h: 4.79 });
  const notes = [
    ["+21%p", "unary + distractor\n차단이 이득", C.blue, 0.5, 2.1],
    ["−51%p", "relational '둘 다에 있나?'\n차단이 손해", C.red, 10.35, 2.1],
    ["L≈20–24", "두 전환이 같은 층 밴드\n= 같은 계산의 양면", C.orange, 10.35, 4.4],
  ];
  notes.forEach(n => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: n[3], y: n[4], w: 2.45, h: 1.35, rectRadius: 0.1,
      fill: { color: C.white }, line: { color: n[2], width: 1.5 } });
    s.addText([{ text: n[0], options: { bold: true, fontSize: 21, color: n[2], breakLine: true } },
      { text: n[1], options: { fontSize: 10, color: C.gray } }],
      { x: n[3] + 0.16, y: n[4] + 0.12, w: 2.15, h: 1.15, fontFace: F, margin: 0 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.55, w: 12.25, h: 0.62, rectRadius: 0.08,
    fill: { color: C.navy } });
  s.addText("같은 모델·같은 개입에서 72%p 격차  →  이미지별·질문별 적응 배분(per-image adaptive depth)의 직접 근거", {
    x: 0.85, y: 6.55, w: 11.8, h: 0.62, fontFace: F, fontSize: 13.5, bold: true, color: C.white,
    margin: 0, valign: "middle" });
  s.addNotes("오늘 가장 중요한 결과입니다. 제안서에서 가설로 그렸던 Type A/Type B 분기가 실제 데이터에서 X자로 교차합니다. 특히 두 효과가 같은 층에서 켜집니다 — 관계 추론 능력과 출처 혼동이 동일한 attention 계산의 양면이라는 뜻이고, 'depth를 질문에 맞게 배분해야 한다'는 주장의 가장 직접적인 근거입니다.");
}

// =====================================================================
// S9 — 컨트롤러 (미확정)
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "컨트롤러  ·  탐색적");
  pendTag(s);
  headline(s, "'실패'로 보였던 신호가 feature 문제였다 — 단일 head, layer 8에서 99.8%", false, 10.3);
  s.addImage({ path: R + "fig4_controller_feature_sweep.png", x: 0.55, y: 1.75, w: 7.4, h: 3.4 });
  // before/after
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.25, y: 1.8, w: 4.55, h: 2.0, rectRadius: 0.1,
    fill: { color: C.light }, line: { color: C.line, width: 1 } });
  s.addText([
    { text: "Phase 0 (사전 등록) — 16개 head 평균", options: { fontSize: 11, color: C.gray, breakLine: true } },
    { text: "layer 8 → 72.5%  ✗ 기준(80%) 미달", options: { fontSize: 15, bold: true, color: C.red, breakLine: true } },
    { text: "오늘 (탐색적) — 단일 head · 2-fold 교차검증", options: { fontSize: 11, color: C.gray, breakLine: true } },
    { text: "layer 8 → 99.8%  ✓  (layer 5 → 98.3%)", options: { fontSize: 15, bold: true, color: C.green } },
  ], { x: 8.5, y: 1.95, w: 4.1, h: 1.75, fontFace: F, margin: 0, paraSpaceAfter: 6 });
  s.addText([
    { text: "선택된 head가 두 fold에서 완전히 동일 → 우연한 과적합 아님", options: { bullet: true, breakLine: true } },
    { text: "함의: 식별에 깊이가 필요 없다 = 차단 시점을 앞당길 수 있다", options: { bullet: true } },
  ], { x: 8.25, y: 4.0, w: 4.6, h: 1.1, fontFace: F, fontSize: 11.5, color: C.navy,
    margin: 0, paraSpaceAfter: 6 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 5.45, w: 12.25, h: 1.15, rectRadius: 0.08,
    fill: { color: C.lightorange }, line: { color: C.orange, width: 1.25 } });
  s.addText([
    { text: "⚠ 미확정 — 관련 이미지가 항상 1번 위치라 \"첫 이미지 선호 head\"와 아직 구분되지 않음", options: { bold: true, fontSize: 13, color: C.orange, breakLine: true } },
    { text: "순서 뒤집기 대조 실험이 진행 중 (내일 오전 결과) — 유지되면 '관련도 신호' 확정, 무너지면 '위치 편향'으로 확정하고 위치 불변 feature 설계가 Phase 1 과제", options: { fontSize: 11.5, color: C.navy } },
  ], { x: 0.85, y: 5.56, w: 11.7, h: 1.0, fontFace: F, margin: 0, paraSpaceAfter: 4 });
  s.addNotes("[내일 결과에 따라 택1]\n버전 A(유지 시): 순서를 뒤집어도 XX%로 유지됐습니다. 질문 관련도를 따라가는 head입니다. 컨트롤러는 실현 가능합니다.\n버전 B(붕괴 시): 뒤집으니 무너졌습니다. 이 신호는 위치 편향이고, 진짜 관련도 신호는 layer 21에 있습니다. 무엇이 신호가 아닌지를 확정한 것이며, 위치 불변 feature 설계가 Phase 1의 1순위 과제입니다. (실패 톤 금지 — 판별 완료 톤으로)");
}

// =====================================================================
// S10 — 실측 속도
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "실측 속도  ·  탐색적");
  headline(s, "이론 42.4% vs 실측 TTFT 9.7% — 격차의 원인까지 규명했다");
  // 좌: 막대 2개
  const yB = 5.0, hM = 2.9;
  bar(s, 1.3, yB, 1.15, hM, 0.424 / 0.45, C.navy, "42.4%", "이론 FLOPs 절감\n(토큰-레이어 계산)", true);
  bar(s, 3.15, yB, 1.15, hM, 0.097 / 0.45, C.blue, "9.7%", "실측 TTFT 절감\n(510.2 → 460.8ms)");
  s.addShape(pres.shapes.LINE, { x: 0.9, y: yB, w: 4.1, h: 0, line: { color: C.navy, width: 1.25 } });
  s.addText("실제 sequence compaction 구현 · n=40 · L=4", { x: 0.7, y: 5.75, w: 4.6, h: 0.3,
    fontFace: F, fontSize: 10.5, italic: true, color: C.gray, margin: 0 });
  // 우: 원인 3
  s.addText("격차의 3가지 원인 (해소 경로 포함)", { x: 5.9, y: 1.8, w: 6.5, h: 0.35,
    fontFace: F, fontSize: 13.5, bold: true, color: C.navy, margin: 0 });
  const causes = [
    ["①", "vision encoder는 여전히 두 이미지 모두 인코딩", "LLM 밖의 고정 비용 → Phase 1: ViT 단계에도 배분 확장"],
    ["②", "per-layer Python 슬라이싱 오버헤드", "프로토타입 한계 → 커널 수준 구현 시 해소"],
    ["③", "짧은 시퀀스에서 attention은 memory-bound", "이미지 수가 늘수록(3~6장) 절감 폭 확대 예상"],
  ];
  causes.forEach((c, i) => {
    const y = 2.3 + i * 1.15;
    s.addShape(pres.shapes.OVAL, { x: 5.9, y, w: 0.5, h: 0.5, fill: { color: C.blue } });
    s.addText(c[0], { x: 5.9, y, w: 0.5, h: 0.5, align: "center", valign: "middle",
      fontFace: F, fontSize: 14, bold: true, color: C.white, margin: 0 });
    s.addText([{ text: c[1], options: { bold: true, fontSize: 12.5, color: C.navy, breakLine: true } },
      { text: c[2], options: { fontSize: 10.5, color: C.gray } }],
      { x: 6.6, y: y - 0.05, w: 6.15, h: 1.05, fontFace: F, margin: 0, paraSpaceAfter: 3 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.35, w: 12.25, h: 0.72, rectRadius: 0.08,
    fill: { color: C.lightgreen }, line: { color: C.green, width: 1 } });
  s.addText("✓ 마스킹 대비 예측 일치율 100% — 지금까지의 정확도 수치는 실제 구현에 그대로 전이됨", {
    x: 0.85, y: 6.35, w: 11.8, h: 0.72, fontFace: F, fontSize: 13, bold: true, color: C.green,
    margin: 0, valign: "middle" });
  s.addNotes("이 숫자를 굳이 먼저 보여드리는 이유는, 이론치만 들고 가면 리뷰에서 반드시 깨지기 때문입니다. 먼저 재고, 먼저 인정하고, 원인과 해소 경로까지 확인했습니다.");
}

// =====================================================================
// S11 — 선행연구 지형
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "선행 연구 지형 — 12편 전수 검증 (원문 확인)");
  headline(s, "비어 있는 칸 — \"이미지 단위 실행 깊이 × 출처 정확도\"");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 12 };
  const cell = { fontSize: 11, color: C.navy, fill: { color: C.lightgray } };
  const rows = [
    [{ text: "목표 ＼ 배분 단위", options: hd }, { text: "전역 균일", options: hd }, { text: "토큰 단위", options: hd }, { text: "이미지 단위", options: hd }],
    [{ text: "효율만", options: hd },
     { text: "VTW (AAAI'25)\nShortV (ICCV'25)", options: cell },
     { text: "FastV 계열", options: cell },
     { text: "MVPruner (ECCV'26)\n— 토큰 수 예산", options: cell }],
    [{ text: "정확도(출처)", options: hd },
     { text: "RSCD · FOCUS\nDelimiter (ICLR'26)", options: cell },
     { text: "PruneHal (철회)", options: cell },
     { text: "★ Ours\n실행 depth 예산", options: { fontSize: 13, bold: true, color: C.white, fill: { color: C.red } } }],
  ];
  s.addTable(rows, { x: 0.55, y: 1.8, w: 12.25, rowH: [0.5, 1.0, 1.0], fontFace: F,
    align: "center", valign: "middle", border: { pt: 1.5, color: "FFFFFF" } });
  s.addText([
    { text: "최근접 MVPruner(ECCV'26): view별 '토큰 수' 예산 — 모든 view가 전 layer 통과(depth 요소 없음), 환각·출처 목표 없음", options: { bullet: true, breakLine: true } },
    { text: "RSCD: layer 범위 개입은 있으나 대상이 text-to-text attention이고 계산이 +10% 증가 (절감 아님)", options: { bullet: true, breakLine: true } },
    { text: "\"depth 절감 최초\" 같은 넓은 주장은 폐기 — 12편 원문 전수 검증 후 위 빈칸으로 좁힌 주장만 유지", options: { bullet: true, bold: true } },
  ], { x: 0.55, y: 5.0, w: 12.25, h: 1.7, fontFace: F, fontSize: 12.5, color: C.navy,
    margin: 0, paraSpaceAfter: 8 });
  s.addNotes("novelty 우려를 저희가 먼저 조사했습니다. 12편 전부 원문을 확인했고, 넓은 주장은 버렸습니다. 남는 자리는 이 한 칸이고, 이 칸은 비어 있습니다.");
}

// =====================================================================
// S12 — 종합 판정 (미확정)
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "종합 판정");
  pendTag(s);
  headline(s, "문제·메커니즘·인과·신호는 확보 — 남은 관문은 '적응의 이득'과 '속도 우위'", false, 10.3);
  // 좌 확보
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 1.75, w: 6.0, h: 4.35, rectRadius: 0.1,
    fill: { color: C.lightgreen }, line: { color: C.green, width: 1.25 } });
  s.addText("✅ 확보한 것 (전부 실측)", { x: 0.85, y: 1.92, w: 5.4, h: 0.4, fontFace: F,
    fontSize: 14.5, bold: true, color: C.green, margin: 0 });
  const got = [
    ["문제 실재", "flip 21.3% vs 대조군 0%"],
    ["메커니즘", "회복 81% · p = 6×10⁻⁷"],
    ["인과", "0.79 → 0.50 · p = 4×10⁻³⁸"],
    ["정책 비가역성", "+21%p vs −51%p (72%p 격차)"],
    ["컨트롤러 신호", "layer-8 단일 head 99.8%"],
  ];
  got.forEach((g, i) => {
    const y = 2.42 + i * 0.72;
    s.addText(g[0], { x: 0.9, y, w: 2.1, h: 0.6, fontFace: F, fontSize: 12.5, bold: true,
      color: C.navy, margin: 0 });
    s.addText(g[1], { x: 3.05, y, w: 3.35, h: 0.6, fontFace: F, fontSize: 12.5,
      color: C.navy, margin: 0 });
  });
  // 우 관문
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.8, y: 1.75, w: 6.0, h: 4.35, rectRadius: 0.1,
    fill: { color: C.lightorange }, line: { color: C.orange, width: 1.25 } });
  s.addText("⏳ 남은 관문 (2~4주 kill gate)", { x: 7.1, y: 1.92, w: 5.4, h: 0.4, fontFace: F,
    fontSize: 14.5, bold: true, color: C.orange, margin: 0 });
  const gates = [
    ["이미지별 '차등' 배분의 이득", "미확정 — J(4,28) 실험 오늘 밤 산출"],
    ["비-oracle 컨트롤러 완결", "counterbalance + CLIP·MVPruner 비교"],
    ["실측 속도 '우위'", "VTW / ShortV 대비 (커널 구현)"],
    ["모델·벤치 일반화", "미확정 — 7B 재현 오늘 밤 산출"],
  ];
  gates.forEach((g, i) => {
    const y = 2.42 + i * 0.9;
    s.addText([{ text: g[0], options: { bold: true, fontSize: 12.5, color: C.navy, breakLine: true } },
      { text: g[1], options: { fontSize: 11, color: g[1].startsWith("미확정") ? C.orange : C.gray } }],
      { x: 7.1, y, w: 5.5, h: 0.85, fontFace: F, margin: 0, paraSpaceAfter: 2 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.55, y: 6.4, w: 12.25, h: 0.68, rectRadius: 0.08,
    fill: { color: C.navy } });
  s.addText("제안서의 go/no-go 기준(\"Type-B 구간의 존재\")은 오늘의 X자 곡선으로 충족 → 진행 조건 성립 · 실패 시 축소 기준도 사전 등록", {
    x: 0.85, y: 6.4, w: 11.8, h: 0.68, fontFace: F, fontSize: 12.5, bold: true, color: C.white,
    margin: 0, valign: "middle" });
  s.addNotes("6개월을 먼저 걸지 않겠습니다. 성립 조건을 2~4주 안에 먼저 깨보고, 깨지면 깨졌다고 보고드리는 구조입니다.");
}

// =====================================================================
// S13 — 후보 방법론 + 일정 (dark)
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.darkbg };
  kicker(s, "제안 — 후보 방법론과 일정", true);
  pendTag(s);
  headline(s, "얕게 판정하고, 이미지마다 다른 깊이로 끊는다 — 11월 CVPR 제출 역산", true, 10.3);
  const cards = [
    ["A · Early-decide, per-image exit", "유력", "layer 5~8에서 head 신호로 관련 이미지 판정 → distractor만 그 지점부터 차단",
     "근거: 신호 99.8%@L8 · 회복 81% · 절감 42%(이론)\n[미확정] J(4,28) 동시 차등 배분 — 오늘 밤 실측", "7EC8F5"],
    ["B · Question-type routing", "", "unary / relational을 먼저 분류해 depth 정책을 분기",
     "근거: 같은 L에서 +21%p vs −51%p\n— 분기의 이득이 크고 방향이 명확", "FFC94D"],
    ["C · Risk-calibrated α-knob", "차별화", "\"출처 오류율 ≤ α 보증 + 계산 최소화\"의 제약 최적화 — 기존 pruning은 전부 휴리스틱",
     "[미확정] (오류율, 절감) Pareto 곡선\n— 오늘 밤 산출 (실측 정오 기반)", "8CE0B0"],
  ];
  cards.forEach((c, i) => {
    const x = 0.55 + i * 4.25, y = 1.75, w = 4.0, h = 3.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1,
      fill: { color: "1D3850" }, line: { color: "2E4E6B", width: 1 } });
    s.addText(c[0], { x: x + 0.22, y: y + 0.18, w: w - 0.44, h: 0.62, fontFace: F, fontSize: 14,
      bold: true, color: c[4], margin: 0 });
    if (c[1]) {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + w - 1.0, y: y + 0.16, w: 0.8, h: 0.32,
        rectRadius: 0.16, fill: { color: C.orange } });
      s.addText(c[1], { x: x + w - 1.0, y: y + 0.16, w: 0.8, h: 0.32, align: "center",
        fontFace: F, fontSize: 10, bold: true, color: C.white, margin: 0 });
    }
    s.addText(c[2], { x: x + 0.22, y: y + 0.85, w: w - 0.44, h: 1.05, fontFace: F, fontSize: 11.5,
      color: "D7E4EF", margin: 0, lineSpacingMultiple: 1.1 });
    s.addText(c[3], { x: x + 0.22, y: y + 1.95, w: w - 0.44, h: 1.1, fontFace: F, fontSize: 10.5,
      color: "9FB8CE", margin: 0, lineSpacingMultiple: 1.1 });
  });
  // 타임라인
  const tl = [["8월", "Kill gate 3종\n▲ go/no-go 판정"], ["9월", "방법 확정 (A/B/C)\n7B·LLaVA-OV / 벤치 확장"],
    ["10월", "baseline 비교 · ablation\n▲ 결과 동결"], ["11월", "작성 · 제출\n(CVPR)"]];
  s.addShape(pres.shapes.LINE, { x: 0.9, y: 5.62, w: 11.5, h: 0, line: { color: "2E4E6B", width: 2 } });
  tl.forEach((t, i) => {
    const x = 0.9 + i * 3.0;
    s.addShape(pres.shapes.OVAL, { x: x - 0.09, y: 5.53, w: 0.18, h: 0.18, fill: { color: "7EC8F5" } });
    s.addText([{ text: t[0], options: { bold: true, fontSize: 13, color: C.white, breakLine: true } },
      { text: t[1], options: { fontSize: 10, color: "9FB8CE" } }],
      { x: x - 0.2, y: 5.8, w: 2.9, h: 0.95, fontFace: F, margin: 0 });
  });
  footer(s, "학습 없음 · 총 400–1,000 GPU-hour (제안서 계획 유지)  ·  Gate 실패 시 출구: 분석 논문 — 데이터·코드 전부 재사용", true);
  s.addNotes("하나에 걸지 않고 셋을 병렬 검증합니다. A가 무너져도 B·C가 살아 있고, C는 MVPruner류와 기여의 '종류'가 달라지는 지점입니다. 마지막으로 — 실패 경로까지 준비되어 있습니다.");
}

// =====================================================================
// S14 — Appendix divider
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addText("Appendix", { x: 0.8, y: 2.6, w: 8, h: 1.0, fontFace: F, fontSize: 44, bold: true,
    color: C.white, margin: 0 });
  s.addText("질문 대응 자료", { x: 0.8, y: 3.6, w: 8, h: 0.5, fontFace: F, fontSize: 16,
    color: "AFC6DA", margin: 0 });
  s.addText([
    { text: "A1  전체 결과표 (조건 × 셀)", options: { breakLine: true } },
    { text: "A2  Relational 3셀 상세", options: { breakLine: true } },
    { text: "A3  Margin 민감도 분석", options: { breakLine: true } },
    { text: "A4  Layer별 식별률 전곡선", options: { breakLine: true } },
    { text: "A5  Attention 프로파일", options: { breakLine: true } },
    { text: "A6  재현성·환경", options: { breakLine: true } },
    { text: "A7  [미확정] 오늘 밤 산출분", options: {} },
  ], { x: 8.6, y: 1.7, w: 4.2, h: 4.3, fontFace: F, fontSize: 14, color: "D7E4EF",
    margin: 0, paraSpaceAfter: 10 });
}

// =====================================================================
// A1 — 전체 결과표
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A1");
  headline(s, "전체 결과표 — 조건 × 셀 정확도, 회복/피해, McNemar p");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 10.5 };
  const c0 = { fontSize: 10.5, color: C.navy, fill: { color: C.white } };
  const c1 = { fontSize: 10.5, color: C.navy, fill: { color: C.lightgray } };
  const mk = (t, alt, opts) => ({ text: t, options: Object.assign({}, alt ? c1 : c0, opts || {}) });
  const data = [
    ["S (단독)", "0.893", "0.740", "0.947", "0.780", "0.840", "—", "—", "—"],
    ["M (기준선)", "0.720", "0.633", "0.980", "0.827", "0.790", "—", "—", "—"],
    ["T4", "0.920", "0.720", "0.960", "0.767", "0.842", "81.0%", "3.7%", "6.0e-7"],
    ["T8", "0.933", "0.667", "0.960", "0.760", "0.830", "83.3%", "2.8%", "6.7e-8"],
    ["T16", "0.933", "0.627", "0.967", "0.740", "0.817", "85.7%", "3.7%", "1.9e-7"],
    ["T24", "0.733", "0.633", "0.987", "0.820", "0.793", "7.1%", "0.9%", "0.63"],
    ["T0 (완전)", "0.933", "0.720", "0.953", "0.773", "0.845", "83.3%", "2.8%", "6.7e-8"],
    ["T-rel(8)", "0.240", "0.027", "0.980", "0.760", "0.502", "—", "—", "3.6e-38*"],
  ];
  const rows = [[mk("조건", 0, hd), mk("셀1", 0, hd), mk("셀2", 0, hd), mk("셀3", 0, hd), mk("셀4", 0, hd),
    mk("전체", 0, hd), mk("회복(셀1)", 0, hd), mk("피해(셀1)", 0, hd), mk("p(셀1)", 0, hd)]];
  data.forEach((r, i) => rows.push(r.map((v, j) => mk(v, i % 2, j === 0 ? { bold: true } : {}))));
  s.addTable(rows, { x: 0.55, y: 1.75, w: 12.25, rowH: 0.42, fontFace: F, align: "center",
    valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  footer(s, "* T-rel(8)은 600문항 pooled McNemar · T12/T20 포함 전체 그리드는 results/table1.csv · 내일 세분화 그리드(12점) 추가 예정");
}

// =====================================================================
// A2 — relational 상세
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A2");
  headline(s, "Relational 3셀 상세 — \"둘 다에 있나?\" (각 100문항, img2 차단)");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11 };
  const cc = { fontSize: 11, color: C.navy, fill: { color: C.white } };
  const mk2 = (t, o) => ({ text: t, options: Object.assign({}, cc, o || {}) });
  const rows = [
    [mk2("셀 (정답)", hd), mk2("M", hd), mk2("T24", hd), mk2("T20", hd), mk2("T16", hd), mk2("T12", hd), mk2("T8", hd), mk2("T4", hd), mk2("T0", hd)],
    [mk2("R1 · img1에만 (no)", { bold: true }), mk2("0.76"), mk2("0.72"), mk2("0.38", { color: C.red, bold: true }), mk2("0.34", { color: C.red, bold: true }), mk2("0.27", { color: C.red, bold: true }), mk2("0.24", { color: C.red, bold: true }), mk2("0.25", { color: C.red, bold: true }), mk2("0.26", { color: C.red, bold: true })],
    [mk2("R2 · img2에만 (no)", { bold: true }), mk2("0.49"), mk2("0.48"), mk2("0.83"), mk2("0.99"), mk2("1.00"), mk2("1.00"), mk2("1.00"), mk2("1.00")],
    [mk2("RB · 둘 다 (yes)", { bold: true }), mk2("0.73"), mk2("0.73"), mk2("0.80"), mk2("0.73"), mk2("0.76"), mk2("0.77"), mk2("0.74"), mk2("0.72")],
  ];
  s.addTable(rows, { x: 0.55, y: 1.8, w: 12.25, rowH: 0.5, fontFace: F, align: "center",
    valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  s.addText([
    { text: "R1이 clean probe인 이유: 정답(no)을 맞히려면 img2를 반드시 확인해야 함 — 차단하면 \"img1에 있으니 both일 것\"으로 오답", options: { bullet: true, breakLine: true } },
    { text: "R2가 차단 시 1.00이 되는 이유: img2가 안 보이면 모델이 '단일 이미지 추론기'로 축소되어 no를 답함(우연히 정답) — 메커니즘 해석의 추가 근거", options: { bullet: true, breakLine: true } },
    { text: "RB가 평평한 이유: img1만 보고도 yes로 기울 수 있어 교란 — 그래서 본편(S8)의 relational 곡선은 R1로 판정", options: { bullet: true } },
  ], { x: 0.55, y: 4.1, w: 12.25, h: 2.2, fontFace: F, fontSize: 12, color: C.navy,
    margin: 0, paraSpaceAfter: 8 });
  footer(s, "질문: \"Is there {object} in both images?\" · 탐색적(사전 미등록) · 기존 이미지·annotation 재사용");
}

// =====================================================================
// A3 — margin 민감도
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A3");
  headline(s, "Margin 민감도 — 셀1 효과는 강건, 셀2 역방향은 근소-margin 산물");
  const hd = { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 11.5 };
  const cc = { fontSize: 11.5, color: C.navy, fill: { color: C.white } };
  const mk3 = (t, o) => ({ text: t, options: Object.assign({}, cc, o || {}) });
  const rows = [
    [mk3("min |logit margin| 필터", hd), mk3("Flip 셀1 (n)", hd), mk3("Flip 셀2 (n)", hd), mk3("회복 T4·셀1 (n)", hd)],
    [mk3("필터 없음"), mk3("21.3% (150)", { bold: true }), mk3("12.7% (150)"), mk3("81.0% (42)", { bold: true })],
    [mk3("≥ 0.25"), mk3("21.4% (131)", { bold: true }), mk3("8.6% (128)"), mk3("82.9% (35)", { bold: true })],
    [mk3("≥ 0.5"), mk3("18.9% (111)", { bold: true }), mk3("1.0% (103)", { color: C.red, bold: true }), mk3("77.8% (27)", { bold: true })],
    [mk3("≥ 1.0"), mk3("16.2% (74)", { bold: true }), mk3("0.0% (78)", { color: C.red, bold: true }), mk3("85.7% (14)", { bold: true })],
  ];
  s.addTable(rows, { x: 1.3, y: 1.9, w: 10.7, rowH: 0.52, fontFace: F, align: "center",
    valign: "middle", border: { pt: 0.75, color: "E2E8F0" } });
  s.addText([
    { text: "셀1 (주 효과): 확신도 높은 문항만 남겨도 flip 16~21% · 회복 78~86% 유지 → 근소 판정 아티팩트 아님", options: { bullet: true, breakLine: true } },
    { text: "셀2 (역방향): |margin| ≥ 0.5에서 사실상 소멸 → 결정 경계 근처 calibration 흔들림으로 해석", options: { bullet: true, breakLine: true } },
    { text: "따라서 본편의 주장은 셀1 + negative control로만 구성 (yes-bias 반박은 인과 실험이 담당)", options: { bullet: true, bold: true } },
  ], { x: 0.9, y: 4.9, w: 11.5, h: 1.8, fontFace: F, fontSize: 12.5, color: C.navy,
    margin: 0, paraSpaceAfter: 8 });
  footer(s, "logit 동률(tie) 104건(1.7%)은 사전 규정(동률→no)대로 처리 · 자체 수행한 민감도 분석 (외부 리뷰 §6 요구 대응)");
}

// =====================================================================
// A4 — layer별 식별률
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A4");
  headline(s, "Layer별 관련 이미지 식별률 (mean-head 기준, n=600)");
  s.addImage({ path: R + "aux_chartA_ident_by_layer.png", x: 0.75, y: 1.9, w: 11.8, h: 4.29 });
  footer(s, "mean-head(16개 평균): L4 15.5% · L8 72.5%(사전 등록 판정 ③ FAIL 지점) · L21 99.0% — 단일 head 선택 시 S9와 같이 L8 99.8%");
}

// =====================================================================
// A5 — attention 프로파일
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A5");
  headline(s, "Layer별 이미지 attention 질량 — 정답 vs 뒤집힌 케이스");
  s.addImage({ path: R + "fig2_attention_profile.png", x: 1.9, y: 1.85, w: 9.5, h: 5.28 });
  footer(s, "M 조건 600문항 · layer 20+에서 img1/img2 질량이 갈라짐 — S8의 '같은 층 밴드' 관찰과 정합");
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
    { text: "재현성: seed 42 고정 · 판정 기준 사전 등록(문서 동결) · 전 결과 raw 보존 · 실행 로그·환경 버전 기록", options: { bullet: true, breakLine: true } },
    { text: "규모·비용: 본 실험 29분 + 야간 확장 실험 · GPU 1장 · 중단(BLOCKED) 0건", options: { bullet: true, breakLine: true } },
    { text: "tie 처리: logit 동률 104건(1.7%)은 사전 규정(동률→no)대로 판정", options: { bullet: true, breakLine: true } },
    { text: "저장소: github.com/hsmai/Source-Depth (private) — 코드·데이터 명세·문서·판정 기준·raw 결과 전부 버전 관리", options: { bullet: true, breakLine: true } },
    { text: "한계(정직 고지): oracle 세팅(관련 이미지 위치 고정) · unary 중심 · 3B 단일 모델(7B 재현 진행 중) · TTFT는 프로토타입 실측 · COCO annotation 노이즈 36건(6%)", options: { bullet: true, bold: true } },
  ], { x: 0.7, y: 2.0, w: 12.0, h: 4.6, fontFace: F, fontSize: 13.5, color: C.navy,
    margin: 0, paraSpaceAfter: 14 });
}

// =====================================================================
// A7 — [미확정] 오늘 밤 산출분
// =====================================================================
{
  const s = pres.addSlide();
  kicker(s, "APPENDIX A7");
  pendTag(s);
  headline(s, "오늘 밤 산출 중 — 내일 오전 이 페이지들을 채움", false, 10.3);
  const items = [
    ["순서 뒤집기 대조", "S9 컨트롤러 신호의 위치 편향 여부 확정", "→ S9 해석 확정"],
    ["J(4,28) 차등 배분", "distractor 4층 + 관련 28층 동시 배분 — 방법의 첫 실제 구현", "→ S12·S13 갱신"],
    ["VTW식 동일 차단 비교", "두 이미지를 같은 K층에서 일괄 차단하는 baseline과 비교", "→ S11 보강"],
    ["CLIP 선택 baseline", "\"CLIP으로 고르면 되지 않나\"에 대한 정면 비교", "→ 질문 대응"],
    ["α-knob Pareto", "오류율 보증 하의 (정확도, 절감) 곡선 — 실측 정오 기반", "→ S13 카드 C"],
    ["7B 전체 재현", "Qwen2.5-VL-7B로 동일 파이프라인 — 스케일 일반화", "→ S12 갱신"],
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
  footer(s, "야간 자동 체인(gate2 → ext → 7B) 실행 중 · watchdog이 실패 시 자동 재제출 · 전 단계 checkpoint-resume");
}

pres.writeFile({ fileName: "/Users/hansangmin/Source-Depth/meeting/SourceDepth_Phase0_meeting.pptx" })
  .then(() => console.log("DECK WRITTEN"));
