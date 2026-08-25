// SourceDepth v8 — 밤샘 실험 결과 반영 (2026-08-25). 모든 수치 results/ 실측.
const pptxgen = require("pptxgenjs");
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE";
const C = { navy:"1F3B57", darkbg:"142638", blue:"1F77B4", red:"D62728", dred:"8B1A1A",
  green:"2E8B57", orange:"B06A00", gray:"6B7280", white:"FFFFFF", light:"EFF4F9",
  lightred:"FBEAEA", lightgray:"F3F4F6", lightgreen:"E9F4EE", lightblue:"E8F1FA",
  lightorange:"FFF8E8", line:"D5DEE8" };
const F = "Arial";
const kick=(s,t,d)=>s.addText(t,{x:0.55,y:0.24,w:11.5,h:0.3,fontFace:F,fontSize:11,bold:true,color:d?"9FB8CE":C.blue,margin:0});
const head=(s,t,d)=>s.addText(t,{x:0.55,y:0.52,w:12.2,h:0.72,fontFace:F,fontSize:21,bold:true,color:d?C.white:C.navy,margin:0});
const take=(s,t,c)=>{s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.55,y:6.62,w:12.25,h:0.6,rectRadius:0.08,fill:{color:c||C.navy}});
  s.addText(t,{x:0.85,y:6.62,w:11.75,h:0.6,fontFace:F,fontSize:12.5,bold:true,color:C.white,margin:0,valign:"middle"});};
const foot=(s,t)=>s.addText(t,{x:0.55,y:6.2,w:12.2,h:0.34,fontFace:F,fontSize:10,italic:true,color:C.gray,margin:0});
const box=(s,x,y,w,h,f,l,lw)=>s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.06,fill:{color:f},line:l?{color:l,width:lw||1}:null});
const txt=(s,t,x,y,w,h,o)=>s.addText(t,Object.assign({x,y,w,h,fontFace:F,margin:0},o));
const hd={bold:true,color:C.white,fill:{color:C.navy},fontSize:11};
const cc={fontSize:11,color:C.navy,fill:{color:C.white}};
const m=(t,o)=>({text:t,options:Object.assign({},cc,o||{})});
const TBL={fontFace:F,align:"center",valign:"middle",border:{pt:0.75,color:"E2E8F0"}};

// ═══ 1 표지 ═══
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  txt(s,"SOURCEDEPTH · 실험 결과 보고 · 한상민 · 2026-08-26",0.6,0.5,12.2,0.3,{fontSize:11.5,bold:true,color:"7EC8F5"});
  txt(s,"오라클 없이 작동하고, FOCUS를 이깁니다.\n다만 두 가지 주장은 접었습니다",0.6,1.0,12.2,1.5,{fontSize:29,bold:true,color:C.white,lineSpacingMultiple:1.15});
  txt(s,"어젯밤 사전등록 5건 실행 · 3건 통과 · 2건 실패 · 전부 그대로 보고드립니다",0.6,2.66,12.2,0.35,{fontSize:13.5,color:"AFC6DA"});
  const cards=[
    ["실현 성능 확보","무관 사진 3장에서\n판별력 0.521 → 0.764\n정확도 0.477 → 0.697","오라클 없는 첫 수치","8CE0B0"],
    ["기여가 분명해짐","같은 선택으로 비교 시\n읽기차단 0.764 > 통째삭제 0.647\n6조건 중 5조건 유의","'무엇을 자르는가'가 기여","7EC8F5"],
    ["FOCUS 대비 우위","FOCUS식 0.599 vs 우리 0.764\nCI [+0.117, +0.210]\n판별도 0.730 vs 0.637","같은 문항·같은 레시피","FFC94D"],
  ];
  cards.forEach((c,i)=>{const x=0.6+i*4.15,y=3.3;
    box(s,x,y,3.95,3.2,"1D3850","2E4E6B",1);
    txt(s,c[0],x+0.25,y+0.2,3.45,0.34,{fontSize:15,bold:true,color:c[3]});
    txt(s,c[1],x+0.25,y+0.66,3.45,1.8,{fontSize:12,color:C.white,lineSpacingMultiple:1.3});
    txt(s,c[2],x+0.25,y+2.62,3.45,0.4,{fontSize:10.5,color:"9FB8CE"});});
  s.addNotes("어젯밤 사전등록 다섯 건을 실행했고 세 건 통과, 두 건 실패입니다. 통과한 것부터 말씀드리면, 오라클 없이 작동하는 수치가 처음 나왔고, 기여가 판별이 아니라 개입이라는 게 분명해졌고, FOCUS와 직접 비교해서 이겼습니다.");
}

// ═══ 2 문제 — anchor 벤치 ═══
{ const s=pres.addSlide();
  kick(s,"문제 재확인 — 위치를 알려주지 않는 새 벤치");
  head(s,"질문에서 위치 단서를 없앴더니 문제가 더 심각해졌습니다");
  box(s,0.55,1.32,12.25,0.86,C.light,C.line,1);
  txt(s,"기존 벤치의 약점: 질문이 \"첫 번째 사진\"이라고 위치를 알려줌 → 글자만 읽는 모듈도 만점",0.8,1.42,11.7,0.28,{fontSize:11.5,color:C.gray});
  txt(s,"새 벤치: \"microwave가 있는 사진에 boat가 있나?\"  — 관련 사진을 내용으로만 특정, 위치 무작위, 600문항",0.8,1.72,11.7,0.32,{fontSize:13,bold:true,color:C.navy});
  s.addTable([
    [m("",hd),m("무개입",hd),m("실현(우리)",hd),m("오라클",hd),m("오라클−무개입 95%CI",hd)],
    [m("3B · 사진 2장",{bold:true}),m("0.4927",{color:C.red,bold:true}),m("0.8141"),m("0.9730"),m("[+0.413, +0.545] ★")],
    [m("3B · 사진 3장",{bold:true}),m("0.4527",{color:C.red,bold:true}),m("0.8592"),m("0.9636"),m("[+0.449, +0.576] ★")],
    [m("7B · 사진 2장",{bold:true}),m("0.7977"),m("0.8551"),m("0.9425"),m("[+0.108, +0.187] ★")],
    [m("7B · 사진 3장",{bold:true}),m("0.7294"),m("0.8386"),m("0.9476"),m("[+0.172, +0.269] ★")],
  ],{x:0.55,y:2.34,w:12.25,rowH:[0.36,0.34,0.34,0.34,0.34],...TBL});
  box(s,0.55,4.36,6.05,1.7,C.lightred,C.red,1.3);
  txt(s,"3B는 무개입이 우연(0.5)보다 낮습니다",0.78,4.48,5.6,0.28,{fontSize:12.5,bold:true,color:C.red});
  txt(s,"정답이 \"없다\"인 문항만 보면 —\n\n무개입 정확도  0.267\n오라클 개입 후  0.973\n\n무관한 사진의 물건을 그대로 답합니다",0.78,4.8,5.6,1.16,{fontSize:11,color:C.navy,lineSpacingMultiple:1.2});
  box(s,6.78,4.36,6.02,1.7,C.lightgreen,C.green,1.3);
  txt(s,"기존 결과가 프롬프트 산물이 아니었습니다",7.01,4.48,5.6,0.28,{fontSize:12.5,bold:true,color:C.green});
  txt(s,"위치를 알려주지 않으면 문제가 사라질까 봐\n만든 벤치인데, 오히려 더 커졌습니다.\n\n→ 이 방향으로 계속할 근거가 확보됐습니다",7.01,4.8,5.6,1.16,{fontSize:11,color:C.navy,lineSpacingMultiple:1.25});
  take(s,"→ 판별력 점수 = 맞다/아니다를 가려내는 능력. 0.5는 찍기. n=600, COCO 기반, 사전 등록 후 측정");
  s.addNotes("가장 크게 지적받을 약점이 벤치마크가 위치를 알려준다는 점이었습니다. 그래서 위치를 없앤 벤치를 만들었는데, 문제가 사라지기는커녕 더 커졌습니다. 3B는 무개입이 찍기보다 못합니다. 정답이 없다인 문항에서 정확도가 0.267입니다.");
}

// ═══ 3 헤드라인 — 오라클 없는 종단 ═══
{ const s=pres.addSlide();
  kick(s,"핵심 결과 1 — 오라클 없이 작동하는가");
  head(s,"어느 사진이 방해인지 알려주지 않아도 작동합니다");
  txt(s,"지금까지 모든 수치는 \"방해 사진이 어느 것인지 알려준\" 조건이었습니다. 이번에 처음으로 컨트롤러를 포함한 실현 수치를 쟀습니다.",0.55,1.26,12.25,0.3,{fontSize:11.5,color:C.gray});
  s.addTable([
    [m("",hd),m("무개입",hd),m("실현 (컨트롤러 포함)",hd),m("오라클 (상한)",hd),m("실현−무개입 95%CI",hd),m("판정",hd)],
    [m("3B · 방해 1장",{bold:true}),m("0.6970"),m("0.7556",{bold:true,color:C.green}),m("0.9057",{color:C.gray}),m("[+0.031, +0.089]"),m("★ 통과",{bold:true,color:C.green})],
    [m("3B · 방해 2장",{bold:true}),m("0.6080"),m("0.7761",{bold:true,color:C.green}),m("0.9039",{color:C.gray}),m("[+0.126, +0.212]"),m("★ 통과",{bold:true,color:C.green})],
    [m("3B · 방해 3장",{bold:true}),m("0.5212",{color:C.red}),m("0.7643",{bold:true,color:C.green}),m("0.9033",{color:C.gray}),m("[+0.196, +0.294]"),m("★ 통과",{bold:true,color:C.green})],
    [m("7B · 방해 1장",{bold:true}),m("0.8690"),m("0.8971",{bold:true,color:C.green}),m("0.8993",{color:C.gray}),m("[+0.012, +0.046]"),m("★ 통과",{bold:true,color:C.green})],
    [m("7B · 방해 2장",{bold:true}),m("0.8723"),m("0.8826"),m("0.8970",{color:C.gray}),m("[−0.007, +0.030]"),m("부분",{color:C.orange})],
    [m("7B · 방해 3장",{bold:true}),m("0.8740"),m("0.8925",{bold:true,color:C.green}),m("0.8957",{color:C.gray}),m("[+0.003, +0.036]"),m("★ 통과",{bold:true,color:C.green})],
  ],{x:0.55,y:1.66,w:12.25,rowH:[0.36,0.33,0.33,0.33,0.33,0.33,0.33],...TBL});
  box(s,0.55,4.2,6.05,1.86,C.lightgreen,C.green,1.3);
  txt(s,"고정 임계값 정확도로 봐도 (3B, 방해 3장)",0.78,4.32,5.6,0.28,{fontSize:12.5,bold:true,color:C.green});
  [["무개입","0.4767",C.red],["실현 (우리)","0.6967",C.green],["오라클 (상한)","0.8200",C.gray]].forEach((r,i)=>{
    const y=4.66+i*0.34;
    txt(s,r[0],0.95,y,2.6,0.3,{fontSize:11.5,color:C.navy});
    txt(s,r[1],3.7,y,1.1,0.3,{fontSize:13,bold:true,color:r[2],align:"right"});});
  txt(s,"\"예\" 응답 비율도 0.610 → 0.517로 함께 교정됐습니다",0.95,5.72,5.3,0.26,{fontSize:10,italic:true,color:C.gray});
  box(s,6.78,4.2,6.02,1.86,C.light,C.line,1);
  txt(s,"남은 격차는 판별 오류입니다",7.01,4.32,5.6,0.28,{fontSize:12.5,bold:true,color:C.navy});
  txt(s,"실현 0.764 vs 오라클 0.903 — 이 차이는 컨트롤러가\n방해 사진을 잘못 고른 문항에서 나옵니다\n(3B 판별 정확도 0.730).\n\n확신도가 낮으면 개입하지 않는 방식(기권)을 시도했으나\n어떤 기권율도 항상 개입보다 못했습니다. 폐기했습니다.",7.01,4.64,5.6,1.3,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.2});
  take(s,"→ 방해 사진이 많을수록 이득이 커집니다: +0.059 → +0.168 → +0.243","2E8B57");
  s.addNotes("이 표가 헤드라인입니다. 지금까지 모든 숫자는 오라클이었는데, 이번에 컨트롤러를 포함한 실현 수치를 처음 쟀습니다. 6조건 중 5조건이 통과했고, 방해 사진이 많을수록 이득이 커집니다. 정확도로 봐도 0.477에서 0.697입니다.");
}

// ═══ 4 핵심 기여 — READ vs KEEP ═══
{ const s=pres.addSlide();
  kick(s,"핵심 결과 2 — 이 연구의 기여가 무엇인가");
  head(s,"기여는 '어느 사진을 고르는가'가 아니라 '무엇을 자르는가'입니다");
  txt(s,"같은 컨트롤러가 고른 같은 사진으로, 자르는 방식만 바꿔 비교했습니다.",0.55,1.26,12.25,0.3,{fontSize:11.5,color:C.gray});
  const cmp=[["흔한 방식 — 통째로 뺀다","무관 사진을 입력에서 제거",C.gray,C.lightgray,"0.6472"],
             ["우리 — 읽는 칸만 지운다","사진은 두고 질문의 읽기만 차단",C.green,C.lightgreen,"0.7643"]];
  cmp.forEach((c,i)=>{const x=0.55+i*6.23;
    box(s,x,1.62,6.02,1.5,c[3],c[2],1.4);
    txt(s,c[0],x+0.24,1.74,5.5,0.3,{fontSize:13,bold:true,color:c[2]});
    txt(s,c[1],x+0.24,2.06,3.4,0.3,{fontSize:11,color:C.navy});
    txt(s,c[4],x+3.9,1.94,1.9,0.7,{fontSize:30,bold:true,color:c[2],align:"right"});
    txt(s,"3B · 방해 3장",x+3.9,2.66,1.9,0.26,{fontSize:9.5,color:C.gray,align:"right"});});
  s.addTable([
    [m("",hd),m("읽기만 차단",hd),m("통째로 삭제",hd),m("차이 95%CI",hd),m("",hd)],
    [m("3B · 방해 1장",{bold:true}),m("0.7556",{bold:true}),m("0.6664"),m("[+0.061, +0.117]"),m("★",{color:C.green,bold:true})],
    [m("3B · 방해 2장",{bold:true}),m("0.7761",{bold:true}),m("0.6586"),m("[+0.086, +0.150]"),m("★",{color:C.green,bold:true})],
    [m("3B · 방해 3장",{bold:true}),m("0.7643",{bold:true}),m("0.6472"),m("[+0.088, +0.147]"),m("★",{color:C.green,bold:true})],
    [m("7B · 방해 1장",{bold:true}),m("0.8971"),m("0.8884"),m("[−0.005, +0.026]"),m("–",{color:C.gray})],
    [m("7B · 방해 2장",{bold:true}),m("0.8826",{bold:true}),m("0.8544"),m("[+0.008, +0.052]"),m("★",{color:C.green,bold:true})],
    [m("7B · 방해 3장",{bold:true}),m("0.8925",{bold:true}),m("0.8608"),m("[+0.010, +0.056]"),m("★",{color:C.green,bold:true})],
  ],{x:0.55,y:3.28,w:8.3,rowH:[0.34,0.31,0.31,0.31,0.31,0.31,0.31],...TBL});
  box(s,9.05,3.28,3.75,2.5,C.lightblue,C.blue,1.4);
  txt(s,"왜 중요한가",9.28,3.42,3.3,0.28,{fontSize:12.5,bold:true,color:C.blue});
  txt(s,"6조건 중 5조건 유의.\n\n컨트롤러가 틀린 문항에서도\n\"지우지 않고 읽기만 끊는\" 쪽이\n회복력이 큽니다.\n\n→ 판별은 남이 해줘도 됩니다.\n우리 기여는 개입 방식입니다.",9.28,3.76,3.3,1.9,{fontSize:11,color:C.navy,lineSpacingMultiple:1.25});
  foot(s,"판별력 점수(AUC) · n=300 · paired bootstrap 2000회 · 두 조건 모두 같은 컨트롤러 선택 사용");
  take(s,"→ 연구의 포지션이 분명해졌습니다: selector 논문이 아니라 '개입 방식' 논문입니다","1F77B4");
  s.addNotes("이게 이번에 새로 나온 가장 중요한 결과입니다. 같은 컨트롤러가 고른 같은 사진인데, 통째로 지우느냐 읽기만 끊느냐로 0.11 차이가 납니다. 6조건 중 5조건 유의합니다. 컨트롤러가 틀려도 읽기만 끊는 쪽이 덜 망가집니다. 그래서 우리 기여는 판별이 아니라 개입 방식입니다.");
}

// ═══ 5 FOCUS 비교 ═══
{ const s=pres.addSlide();
  kick(s,"핵심 결과 3 — 기존 연구와 직접 비교");
  head(s,"같은 레시피에서 개입 수단만 바꿔 비교했습니다");
  txt(s,"지금까지 비교 대상이 '오라클 전면 차단'뿐이라 FOCUS와 한 번도 비교하지 못했습니다. 같은 문항·같은 N+1 논리에서 개입 수단만 교체했습니다.",0.55,1.26,12.25,0.3,{fontSize:11.5,color:C.gray});
  s.addTable([
    [m("",hd),m("무개입",hd),m("FOCUS식\n(픽셀 노이즈)",hd),m("VCD식",hd),m("우리\n(attention 마스크)",hd),m("우리−FOCUS 95%CI",hd)],
    [m("3B · 방해 1장",{bold:true}),m("0.6970"),m("0.6940"),m("0.7005"),m("0.7556",{bold:true,color:C.green}),m("[+0.036, +0.094] ★",{bold:true,color:C.green})],
    [m("3B · 방해 3장",{bold:true}),m("0.5212"),m("0.5988"),m("0.5235"),m("0.7643",{bold:true,color:C.green}),m("[+0.117, +0.210] ★",{bold:true,color:C.green})],
    [m("7B · 방해 1장",{bold:true}),m("0.8690"),m("0.8858"),m("0.8724"),m("0.8971"),m("[−0.005, +0.030]",{color:C.orange})],
    [m("7B · 방해 3장",{bold:true}),m("0.8740"),m("0.8767"),m("0.8796"),m("0.8925"),m("[−0.001, +0.033]",{color:C.orange})],
  ],{x:0.55,y:1.66,w:12.25,rowH:[0.52,0.34,0.34,0.34,0.34],...TBL});
  box(s,0.55,3.94,6.05,1.5,C.lightgreen,C.green,1.3);
  txt(s,"판별 정확도도 마스킹이 더 높습니다",0.78,4.06,5.6,0.28,{fontSize:12.5,bold:true,color:C.green});
  s.addTable([
    [m("",{...cc,fontSize:10.5}),m("우리(마스킹)",{...cc,fontSize:10.5,bold:true}),m("FOCUS식(노이즈)",{...cc,fontSize:10.5})],
    [m("3B",{...cc,fontSize:10.5}),m("0.730",{...cc,fontSize:10.5,bold:true,color:C.green}),m("0.637",{...cc,fontSize:10.5})],
    [m("7B",{...cc,fontSize:10.5}),m("0.937",{...cc,fontSize:10.5,bold:true,color:C.green}),m("0.817",{...cc,fontSize:10.5})],
  ],{x:0.85,y:4.42,w:5.4,rowH:[0.28,0.26,0.26],...TBL});
  box(s,6.78,3.94,6.02,1.5,C.lightorange,C.orange,1.3);
  txt(s,"정직하게 붙이는 조건",7.01,4.06,5.6,0.28,{fontSize:12.5,bold:true,color:C.orange});
  txt(s,"· 7B는 동급입니다 (CI가 0에 접함). 정확도 축에서\n  7B 우위는 주장하지 않습니다.\n· 원 논문의 하이퍼파라미터를 그대로 옮긴 재현이 아니라,\n  \"N+1 반사실 + 개입 수단\"만 통제한 비교입니다.",7.01,4.38,5.6,1.0,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.2});
  box(s,0.55,5.56,12.25,0.56,C.light,C.line,1);
  txt(s,"구조적 차이: 우리는 attention만 바꾸므로 이미지 인코딩(비용의 66%)을 N+1회 전부 재사용할 수 있고, 픽셀을 바꾸는 방식은 매번 다시 인코딩해야 합니다 — 단 재사용 구현은 아직 없습니다.",0.85,5.56,11.7,0.56,{fontSize:11,color:C.navy,valign:"middle"});
  take(s,"→ 3B에서 유의하게 우위, 7B에서 동급. 판별 정확도는 두 스케일 모두 우위");
  s.addNotes("FOCUS와 처음으로 직접 비교했습니다. 3B에서는 유의하게 이겼고 7B에서는 동급입니다. 판별 정확도는 두 스케일 모두 마스킹이 높습니다. 다만 원 논문 재현이 아니라 개입 수단만 통제한 비교라는 점은 논문에도 그대로 씁니다.");
}

// ═══ 6 실패한 것 ═══
{ const s=pres.addSlide();
  kick(s,"실패한 것 — 사전등록대로 그대로 보고드립니다");
  head(s,"두 가지 주장을 접고, 두 가지 시도를 폐기했습니다");
  const fails=[
    ["접음","경로 대비 (0.974)","방해가 정답과 같은 방향으로 미는 문항에서 0.988 → 0.862 로 크게 해로움 (CI [−0.179, −0.078]). 어느 경우인지 미리 알 수 없으므로 자동 적용 불가.","→ '방법'이 아니라 '진단 도구'로 격하. 사전등록에 적어둔 실패 경로 그대로."],
    ["접음","통합 주장 (막기 vs 열기)","MIMIC식 균일 차단이 무개입보다 나쁨 (3B 0.412 vs 0.697, 7B 0.852 vs 0.869, 둘 다 유의). '우리 분해가 양 진영을 설명한다'는 성립하지 않음.","→ 철회. 남는 것은 '이미지끼리 차단은 층 구간을 어떻게 잡든 해롭다'."],
    ["폐기","기권(abstention) 게이트","확신도가 낮으면 개입하지 않는 방식. 기권율 10~70% 전 구간에서 항상 개입보다 못함 (3B 0.764 → 0.718 → 0.544).","→ 이 확신도 신호는 오판을 식별하지 못함."],
    ["폐기","top-k 일반화 가설","모든 사진이 필요한 질문에서 top-2 유지가 top-1보다 낫지 않음 (3B 0.644 vs 0.623, CI 0 포함).","→ 단 top-1만 남겨도 유의한 손해는 없었음 (do-no-harm은 통과)."],
  ];
  fails.forEach((f,i)=>{const y=1.34+i*1.28;
    box(s,0.55,y,12.25,1.16,i<2?C.lightred:C.lightgray,i<2?C.red:C.gray,1.2);
    box(s,0.75,y+0.16,0.72,0.32,i<2?C.red:C.gray,null,0);
    txt(s,f[0],0.75,y+0.16,0.72,0.32,{fontSize:11,bold:true,color:C.white,align:"center",valign:"middle"});
    txt(s,f[1],1.6,y+0.14,3.3,0.34,{fontSize:13,bold:true,color:i<2?C.red:C.navy});
    txt(s,f[2],1.6,y+0.5,7.4,0.58,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.15});
    txt(s,f[3],9.15,y+0.3,3.45,0.62,{fontSize:10.5,bold:true,color:i<2?C.red:C.gray,lineSpacingMultiple:1.2});});
  take(s,"→ 실험 전에 판정 기준을 문서로 고정하고 실행한 것이 누적 10건, 그중 6건이 기준 미달이거나 예측과 반대였습니다");
  s.addNotes("실패한 것을 먼저 말씀드립니다. 경로 대비는 방해가 정답 방향으로 미는 문항에서 크게 해로워서 방법이 아니라 진단 도구로 격하합니다. 통합 주장은 MIMIC식이 무개입보다 나빠서 철회합니다. 기권 게이트와 top-k 일반화는 폐기합니다. 전부 사전등록에 적어둔 실패 경로 그대로입니다.");
}

// ═══ 7 남은 약점 + 진행 중 ═══
{ const s=pres.addSlide();
  kick(s,"남은 약점 하나와, 지금 돌고 있는 검증");
  head(s,"판별에서는 CLIP에 밀립니다 — 그래서 무엇을 검증 중인가");
  box(s,0.55,1.3,12.25,1.62,C.lightorange,C.orange,1.3);
  txt(s,"새 벤치(anchor)에서 CLIP이 우리 컨트롤러보다 방해 사진을 잘 골랐습니다",0.85,1.42,11.7,0.3,{fontSize:13,bold:true,color:C.orange});
  s.addTable([
    [m("",{...cc,fontSize:10.5}),m("우리 (하나씩 빼보기)",{...cc,fontSize:10.5}),m("CLIP",{...cc,fontSize:10.5}),m("둘 중 하나라도 맞음",{...cc,fontSize:10.5})],
    [m("3B · 사진 2장",{...cc,fontSize:10.5}),m("0.557",{...cc,fontSize:10.5,color:C.red}),m("0.817",{...cc,fontSize:10.5,bold:true}),m("0.907",{...cc,fontSize:10.5,bold:true,color:C.green})],
    [m("3B · 사진 3장",{...cc,fontSize:10.5}),m("0.763",{...cc,fontSize:10.5,bold:true}),m("0.733",{...cc,fontSize:10.5}),m("0.927",{...cc,fontSize:10.5,bold:true,color:C.green})],
  ],{x:0.85,y:1.78,w:7.2,rowH:[0.3,0.28,0.28],...TBL});
  txt(s,"이 벤치는 anchor 객체를 문장에 명시하므로\nCLIP에 유리한 설계입니다. 그대로 보고합니다.\n\n다만 둘은 서로 다른 문항을 맞힙니다 —\n우리만 맞은 문항이 27~58건.",8.35,1.78,4.2,1.0,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.2});
  box(s,0.55,3.1,12.25,1.5,C.lightblue,C.blue,1.4);
  txt(s,"지금 GPU에서 돌고 있는 검증 — \"판별을 남이 해줘도 우리 개입이 이득인가?\"",0.85,3.22,11.7,0.3,{fontSize:13,bold:true,color:C.blue});
  txt(s,"CLIP이 고른 사진으로 개입 방식만 바꿔 비교합니다:   CLIP + 읽기차단   vs   CLIP + 통째삭제\n\n앞의 결과(핵심 결과 2)가 CLIP 선택에서도 재현되면 — 판별자는 무엇이든 좋고, 우리 기여는 개입이라는 게 확정됩니다.\n합집합 상한 0.91~0.93도 함께 검증합니다 (CLIP ∪ 우리 선택 유지).",0.85,3.58,11.7,0.9,{fontSize:11,color:C.navy,lineSpacingMultiple:1.25});
  box(s,0.55,4.78,12.25,1.32,C.light,C.line,1);
  txt(s,"그 밖에 아직 못 한 것 — 순서대로 진행 예정",0.85,4.9,11.7,0.28,{fontSize:12.5,bold:true,color:C.navy});
  txt(s,"① 공개 벤치마크 (MuirBench · BLINK)  ← 2주차 중단 조건: 여기서 재현 안 되면 접습니다     ② 다른 모델군 (LLaVA-OneVision 등)\n③ 인코더 재사용 구현 후 실측 속도 (지금은 계산상 절감만 있음)     ④ 생성(자유 서술) 평가 — 현재 마스크는 prefill 전용이라 적용 가능성부터 확인 필요\n⑤ 방해 사진 5~8장 확장 (지금 최대 3장)     ⑥ 프롬프트 문구 강건성",0.85,5.22,11.7,0.8,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.3});
  take(s,"→ 7B는 8층까지만 판별 절단 가능(0.930), 16층에서 0.790으로 떨어짐 — 비용 절감 주장은 3B보다 약합니다");
  s.addNotes("남은 약점은 판별입니다. 새 벤치에서 CLIP이 우리보다 잘 골랐습니다. 이 벤치가 CLIP에 유리한 설계라는 점은 있지만 그대로 보고합니다. 중요한 건 둘이 서로 다른 문항을 맞힌다는 것이고, 그래서 지금 CLIP이 고른 사진으로 개입 방식만 바꾸는 실험을 돌리고 있습니다. 이게 재현되면 우리 기여가 개입이라는 게 확정됩니다.");
}

// ═══ 8 논문 포지션 ═══
{ const s=pres.addSlide();
  kick(s,"그래서 논문을 어떻게 쓸 것인가");
  head(s,"selector 논문이 아니라 '개입 방식' 논문으로 갑니다");
  box(s,0.55,1.3,12.25,1.0,C.navy,null,0);
  txt(s,[{text:"한 문장   ",options:{bold:true,fontSize:11,color:"9FB8CE"}},
         {text:"멀티이미지 환각의 해악은 「질문 → 무관 이미지」 읽기 경로로만 흐르므로,",options:{bold:true,fontSize:14.5,color:C.white,breakLine:true}},
         {text:"무관 이미지를 지우지 말고 그 칸만 끊어야 한다 — 지우는 것보다, 픽셀을 바꾸는 것보다 낫다.",options:{bold:true,fontSize:14.5,color:C.white}}],
      0.9,1.4,11.6,0.84,{margin:0,paraSpaceAfter:2});
  const con=[["C1","기전 규명","해악은 읽기 경로에만. 이미지끼리 혼합은 오히려 보호적","XIMG 차단이 이득인 설정 0/8건 · 두 배치 × 두 모델 일관"],
             ["C2","개입 방식","같은 선택으로도 읽기차단 > 통째삭제","실현 조건 6개 중 5개 유의 · 3B +0.088~+0.147"],
             ["C3","기존 대비","같은 레시피에서 픽셀 노이즈보다 우위","3B [+0.117,+0.210] · 판별도 0.730 vs 0.637"],
             ["C4","실현 성능","오라클 없이 작동. 방해가 많을수록 이득 증가","3B 0.521 → 0.764 · 정확도 0.477 → 0.697"],
             ["C5","새 벤치","위치 단서 없는 멀티이미지 환각 벤치 600문항","무개입이 우연 이하(0.453)까지 떨어지는 난이도"]];
  txt(s,"기여 5가지 — 전부 실측, 사전 등록 후 실행",0.55,2.46,12.25,0.28,{fontSize:12.5,bold:true,color:C.navy});
  con.forEach((c,i)=>{const y=2.8+i*0.44;
    box(s,0.55,y,12.25,0.4,i%2?C.light:C.lightgray,null,0);
    txt(s,c[0],0.72,y,0.5,0.4,{fontSize:11,bold:true,color:C.blue,valign:"middle"});
    txt(s,c[1],1.28,y,1.9,0.4,{fontSize:11,bold:true,color:C.navy,valign:"middle"});
    txt(s,c[2],3.3,y,4.9,0.4,{fontSize:10.5,color:C.navy,valign:"middle"});
    txt(s,c[3],8.3,y,4.4,0.4,{fontSize:10,color:C.gray,valign:"middle"});});
  box(s,0.55,5.1,12.25,1.0,C.lightgreen,C.green,1.3);
  txt(s,"쓰지 않을 주장 (검증했으나 성립하지 않음)",0.85,5.22,11.7,0.28,{fontSize:12,bold:true,color:C.green});
  txt(s,"\"training-free 최초\" · \"층 단위 개입 최초\" · \"개입으로 원인 검증 최초\" (전부 선행연구 있음)  ·  \"양 진영을 통합한다\" (반증됨)  ·  \"selector보다 잘 고른다\" (CLIP에 밀림)  ·  \"더 빠르다\" (구현 없음)",0.85,5.54,11.7,0.48,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.2});
  take(s,"→ 남은 차별점: 여러 사진 중 특정 한 장으로 가는 '읽기 경로'만 끊은 연구는 문헌에 없습니다","1F77B4");
  s.addNotes("논문 포지션입니다. selector 경쟁이 아니라 개입 방식 논문으로 갑니다. 기여 다섯 가지는 전부 실측이고 사전등록 후 실행했습니다. 쓰지 않을 주장도 명시했습니다. 검증해봤더니 성립하지 않는 것들입니다.");
}

// ═══ 9 일정 ═══
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  kick(s,"남은 일정",true);
  head(s,"CVPR 2027 마감까지 11주 — 중단 조건을 먼저 둡니다",true);
  const plan=[["1주","공개 벤치마크 포팅 (MuirBench · BLINK yes/no 서브셋)","여기서 재현 안 되면 접습니다","FF9E80"],
              ["2–3주","다른 모델군 1개 (LLaVA-OneVision-7B) · 마스크 훅 포팅","기전이 Qwen 고유물이 아닌가","7EC8F5"],
              ["4–5주","인코더 재사용 구현 → 실측 속도 · 방해 5~8장 확장 · 실패 사례 분석","비용 주장 확정 / 실패 꼬리 특성화","7EC8F5"],
              ["6–7주","생성(자유 서술) 평가 · 프롬프트 강건성 · 통계 정비(seed 3개)","yes/no 논문이 아니게 만들기","7EC8F5"],
              ["8–10주","초고 → 내부 리뷰 2회 → 리뷰어 공격 대비 ablation","—","8CE0B0"],
              ["11주","버퍼 · 초록 11/06 · 제출 11/13","—","8CE0B0"]];
  plan.forEach((p,i)=>{const y=1.34+i*0.72;
    box(s,0.55,y,12.25,0.62,"1D3850","2E4E6B",1);
    txt(s,p[0],0.8,y,1.1,0.62,{fontSize:12.5,bold:true,color:p[3],valign:"middle"});
    txt(s,p[1],2.05,y,6.6,0.62,{fontSize:11.5,color:C.white,valign:"middle"});
    txt(s,"→ "+p[2],8.85,y,3.75,0.62,{fontSize:10.5,color:"9FB8CE",valign:"middle"});});
  box(s,0.55,5.78,12.25,0.72,"3A2430","6B3A4A",1.2);
  txt(s,"가장 큰 위험: 지금 모든 결과가 COCO 기반 자체 제작 벤치와 예/아니오 단답에 한정됩니다. 공개 벤치에서 재현되지 않으면 1주차에 접습니다.",0.85,5.78,11.7,0.72,{fontSize:11.5,bold:true,color:"FFB4A2",valign:"middle"});
  s.addNotes("11주 남았습니다. 1주차 공개 벤치마크가 중단 조건입니다. 지금 결과가 전부 자체 제작 벤치와 예아니오 단답에 한정되어 있어서, 공개 벤치에서 재현되지 않으면 접겠습니다.");
}

pres.writeFile({ fileName: "/Users/hansangmin/Source-Depth/meeting/_generated/deck_v8.pptx" })
  .then(()=>console.log("DECK v8 WRITTEN"));
