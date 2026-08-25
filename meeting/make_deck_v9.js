// SourceDepth v9 — 주간 진행 보고 (2026-08-26). 정정 반영. 모든 수치 results/ 실측.
const pptxgen = require("pptxgenjs");
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE";
const C = { navy:"1F3B57", darkbg:"142638", blue:"1F77B4", red:"D62728", green:"2E8B57",
  orange:"B06A00", gray:"6B7280", white:"FFFFFF", light:"EFF4F9", lightred:"FBEAEA",
  lightgray:"F3F4F6", lightgreen:"E9F4EE", lightblue:"E8F1FA", lightorange:"FFF8E8", line:"D5DEE8" };
const F = "Arial";
const kick=(s,t,d)=>s.addText(t,{x:0.55,y:0.24,w:11.5,h:0.3,fontFace:F,fontSize:11,bold:true,color:d?"9FB8CE":C.blue,margin:0});
const head=(s,t,d)=>s.addText(t,{x:0.55,y:0.52,w:12.2,h:0.72,fontFace:F,fontSize:21,bold:true,color:d?C.white:C.navy,margin:0});
const take=(s,t,c)=>{s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.55,y:6.62,w:12.25,h:0.6,rectRadius:0.08,fill:{color:c||C.navy}});
  s.addText(t,{x:0.85,y:6.62,w:11.75,h:0.6,fontFace:F,fontSize:12.5,bold:true,color:C.white,margin:0,valign:"middle"});};
const foot=(s,t)=>s.addText(t,{x:0.55,y:6.18,w:12.2,h:0.34,fontFace:F,fontSize:10,italic:true,color:C.gray,margin:0});
const box=(s,x,y,w,h,f,l,lw)=>s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.06,fill:{color:f},line:l?{color:l,width:lw||1}:null});
const txt=(s,t,x,y,w,h,o)=>s.addText(t,Object.assign({x,y,w,h,fontFace:F,margin:0},o));
const hd={bold:true,color:C.white,fill:{color:C.navy},fontSize:11};
const cc={fontSize:11,color:C.navy,fill:{color:C.white}};
const m=(t,o)=>({text:t,options:Object.assign({},cc,o||{})});
const TBL={fontFace:F,align:"center",valign:"middle",border:{pt:0.75,color:"E2E8F0"}};

// ═══ 1 표지 — 이번 주 결론 ═══
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  txt(s,"SOURCEDEPTH · 주간 진행 보고 · 한상민 · 2026-08-26",0.6,0.5,12.2,0.3,{fontSize:11.5,bold:true,color:"7EC8F5"});
  txt(s,"이번 주 결론: 연구 가치가 강해졌습니다",0.6,1.0,12.2,0.7,{fontSize:31,bold:true,color:C.white});
  txt(s,"사전등록 5건 실행 · 문제 실재와 실현 성능이 확보됐고, 과했던 주장 2건은 스스로 찾아 정정했습니다",0.6,1.86,12.2,0.35,{fontSize:13.5,color:"AFC6DA"});
  const cards=[
    ["문제가 더 심각해졌다","위치 단서를 없앤 새 벤치에서\n무개입 판별력 0.453\n— 동전 던지기(0.5)보다 낮음","기존 결과가 프롬프트 산물이 아님","8CE0B0"],
    ["오라클 없이 작동한다","방해 3장에서 0.521 → 0.764\n정확도 0.477 → 0.697\n방해가 많을수록 이득이 커짐","실현 수치를 처음 확보","7EC8F5"],
    ["기존 연구 대비 우위 지점","마스킹 기반 반사실이\n픽셀 노이즈보다 판별을 잘함\n0.730 vs 0.637 · 0.937 vs 0.817","두 스케일 모두 일관","FFC94D"],
  ];
  cards.forEach((c,i)=>{const x=0.6+i*4.15,y=2.52;
    box(s,x,y,3.95,2.5,"1D3850","2E4E6B",1);
    txt(s,c[0],x+0.25,y+0.2,3.45,0.34,{fontSize:14.5,bold:true,color:c[3]});
    txt(s,c[1],x+0.25,y+0.64,3.45,1.3,{fontSize:11.5,color:C.white,lineSpacingMultiple:1.3});
    txt(s,c[2],x+0.25,y+2.02,3.45,0.34,{fontSize:10.5,color:"9FB8CE"});});
  box(s,0.6,5.28,12.25,1.36,"1D3850","2E4E6B",1);
  txt(s,"동시에 — 과했던 주장 2건을 스스로 분해해서 정정했습니다",0.9,5.4,11.7,0.3,{fontSize:13,bold:true,color:"FFB4A2"});
  txt(s,"· \"읽기 차단이 통째 삭제보다 낫다\" → 판별이 맞으면 현 벤치에서는 구조적으로 동일. 차이는 판별이 틀렸을 때만 (검증 중)\n· \"우리 개입이 FOCUS보다 낫다\" → 판별이 같으면 차이 없음. 우위는 개입이 아니라 판별 단계에서 옴",0.9,5.74,11.7,0.66,{fontSize:11,color:"D0DCE6",lineSpacingMultiple:1.25});
  s.addNotes("이번 주 결론부터 말씀드리면 연구 가치가 강해졌습니다. 문제가 실재한다는 근거가 더 강해졌고, 오라클 없이 작동하는 수치를 처음 확보했고, 기존 연구 대비 우위 지점을 찾았습니다. 동시에 제가 과하게 주장했던 두 가지를 스스로 분해해서 정정했습니다.");
}

// ═══ 2 ① 문제 실재 ═══
{ const s=pres.addSlide();
  kick(s,"근거 ① — 문제가 실재하는가");
  head(s,"질문에서 위치 단서를 없앴더니 문제가 더 심각해졌습니다");
  box(s,0.55,1.3,12.25,0.94,C.light,C.line,1);
  txt(s,"기존 벤치의 최대 약점: 질문이 \"첫 번째 사진\"이라고 위치를 알려줌 → 글자만 읽는 모듈도 만점을 받음",0.85,1.4,11.7,0.28,{fontSize:11,color:C.gray});
  txt(s,"새 벤치 (600문항 신규 제작):  \"microwave가 있는 사진에 boat가 있나?\"  — 내용으로만 특정, 위치 무작위",0.85,1.72,11.7,0.32,{fontSize:13,bold:true,color:C.navy});
  s.addTable([
    [m("",hd),m("무개입",hd),m("우리 방법 (실현)",hd),m("상한 (오라클)",hd),m("문제 크기 95%CI",hd)],
    [m("3B · 사진 2장",{bold:true}),m("0.4927",{color:C.red,bold:true}),m("0.8141",{color:C.green}),m("0.9730"),m("[+0.413, +0.545] ★")],
    [m("3B · 사진 3장",{bold:true}),m("0.4527",{color:C.red,bold:true}),m("0.8592",{color:C.green}),m("0.9636"),m("[+0.449, +0.576] ★")],
    [m("7B · 사진 2장",{bold:true}),m("0.7977"),m("0.8551",{color:C.green}),m("0.9425"),m("[+0.108, +0.187] ★")],
    [m("7B · 사진 3장",{bold:true}),m("0.7294"),m("0.8386",{color:C.green}),m("0.9476"),m("[+0.172, +0.269] ★")],
  ],{x:0.55,y:2.4,w:12.25,rowH:[0.36,0.34,0.34,0.34,0.34],...TBL});
  box(s,0.55,4.42,6.05,1.62,C.lightred,C.red,1.3);
  txt(s,"3B는 무개입이 찍기보다 못합니다",0.78,4.54,5.6,0.28,{fontSize:12.5,bold:true,color:C.red});
  txt(s,"정답이 \"없다\"인 문항만 보면 —\n\n     무개입 정확도        0.267\n     개입 후 (오라클)      0.973\n\n무관한 사진에 있는 물건을 그대로 답합니다",0.78,4.86,5.6,1.08,{fontSize:11,color:C.navy,lineSpacingMultiple:1.2});
  box(s,6.78,4.42,6.02,1.62,C.lightgreen,C.green,1.3);
  txt(s,"이게 왜 중요한가",7.01,4.54,5.6,0.28,{fontSize:12.5,bold:true,color:C.green});
  txt(s,"\"위치를 알려주니까 나온 결과 아니냐\"가\n지금까지 가장 큰 약점이었습니다.\n\n위치를 없앤 벤치를 만들었더니 문제가\n사라지기는커녕 더 커졌습니다.\n→ 이 방향으로 계속할 근거가 생겼습니다",7.01,4.86,5.6,1.08,{fontSize:11,color:C.navy,lineSpacingMultiple:1.2});
  foot(s,"판별력 점수(AUC): 맞다/아니다를 가려내는 능력. 0.5 = 찍기 · n=600 · COCO 기반 자체 제작 · 사전 등록 후 측정");
  take(s,"→ 가장 큰 약점을 스스로 공격했고, 결과는 문제가 더 크다는 쪽이었습니다");
  s.addNotes("첫 번째 근거입니다. 지금까지 가장 큰 약점이 벤치마크가 위치를 알려준다는 것이었습니다. 그래서 위치를 없앤 벤치를 새로 만들었는데, 문제가 사라지기는커녕 더 커졌습니다. 3B는 무개입이 찍기보다 못합니다.");
}

// ═══ 3 ② 실현 성능 ═══
{ const s=pres.addSlide();
  kick(s,"근거 ② — 실제로 쓸 수 있는가");
  head(s,"어느 사진이 방해인지 알려주지 않아도 작동합니다");
  txt(s,"지금까지 모든 수치는 방해 사진을 알려준 조건이었습니다. 이번에 컨트롤러를 포함한 실현 수치를 처음 쟀습니다.",0.55,1.26,12.25,0.3,{fontSize:11.5,color:C.gray});
  s.addTable([
    [m("",hd),m("무개입",hd),m("실현 (컨트롤러 포함)",hd),m("상한 (오라클)",hd),m("실현−무개입 95%CI",hd),m("판정",hd)],
    [m("3B · 방해 1장",{bold:true}),m("0.6970"),m("0.7556",{bold:true,color:C.green}),m("0.9057",{color:C.gray}),m("[+0.031, +0.089]"),m("★",{bold:true,color:C.green})],
    [m("3B · 방해 2장",{bold:true}),m("0.6080"),m("0.7761",{bold:true,color:C.green}),m("0.9039",{color:C.gray}),m("[+0.126, +0.212]"),m("★",{bold:true,color:C.green})],
    [m("3B · 방해 3장",{bold:true}),m("0.5212",{color:C.red}),m("0.7643",{bold:true,color:C.green}),m("0.9033",{color:C.gray}),m("[+0.196, +0.294]"),m("★",{bold:true,color:C.green})],
    [m("7B · 방해 1장",{bold:true}),m("0.8690"),m("0.8971",{bold:true,color:C.green}),m("0.8993",{color:C.gray}),m("[+0.012, +0.046]"),m("★",{bold:true,color:C.green})],
    [m("7B · 방해 2장",{bold:true}),m("0.8723"),m("0.8826"),m("0.8970",{color:C.gray}),m("[−0.007, +0.030]"),m("부분",{color:C.orange})],
    [m("7B · 방해 3장",{bold:true}),m("0.8740"),m("0.8925",{bold:true,color:C.green}),m("0.8957",{color:C.gray}),m("[+0.003, +0.036]"),m("★",{bold:true,color:C.green})],
  ],{x:0.55,y:1.66,w:12.25,rowH:[0.36,0.33,0.33,0.33,0.33,0.33,0.33],...TBL});
  const kv=[["방해가 많을수록 이득이 커진다","+0.059  →  +0.168  →  +0.243","방해 1장 → 2장 → 3장 (3B)",C.green,C.lightgreen],
            ["고정 임계값 정확도로 봐도","0.477  →  0.697","무개입 → 실현 (3B, 방해 3장)",C.blue,C.lightblue],
            ["남은 격차는 전부 판별 오류","실현 0.764  vs  상한 0.903","컨트롤러 판별 정확도 0.730",C.orange,C.lightorange]];
  kv.forEach((k,i)=>{const x=0.55+i*4.12;
    box(s,x,4.2,3.95,1.86,k[4],k[3],1.3);
    txt(s,k[0],x+0.22,4.34,3.5,0.3,{fontSize:12,bold:true,color:k[3]});
    txt(s,k[1],x+0.22,4.76,3.5,0.6,{fontSize:17,bold:true,color:k[3],align:"center"});
    txt(s,k[2],x+0.22,5.46,3.5,0.3,{fontSize:10,color:C.gray,align:"center"});});
  txt(s,"\"예\" 응답 편향도 0.610 → 0.517로 함께 교정됩니다",0.77,5.76,3.5,0.24,{fontSize:9.5,italic:true,color:C.gray,align:"center"});
  txt(s,"여기를 줄이는 것이 남은 최대 이득",8.89,5.76,3.5,0.24,{fontSize:9.5,italic:true,color:C.gray,align:"center"});
  take(s,"→ 6조건 중 5조건 유의. 이 표가 논문의 헤드라인이 됩니다","2E8B57");
  s.addNotes("두 번째 근거입니다. 지금까지 모든 숫자가 오라클이었는데 이번에 실현 수치를 처음 쟀습니다. 6조건 중 5조건 통과했고, 방해가 많을수록 이득이 커집니다. 남은 격차는 전부 판별 오류이고 그게 다음 개선 지점입니다.");
}

// ═══ 4 ③ 기존 연구 대비 ═══
{ const s=pres.addSlide();
  kick(s,"근거 ③ — 기존 연구보다 나은 점이 있는가");
  head(s,"같은 레시피에서 개입 수단만 바꿔 비교했습니다");
  txt(s,"FOCUS와 한 번도 비교하지 못했습니다. 같은 문항·같은 N+1 반사실 논리에서 개입 수단만 교체했습니다.",0.55,1.26,12.25,0.3,{fontSize:11.5,color:C.gray});
  box(s,0.55,1.64,6.05,2.1,C.lightgreen,C.green,1.4);
  txt(s,"우위가 확인된 지점 — 판별 단계",0.78,1.78,5.6,0.3,{fontSize:13,bold:true,color:C.green});
  txt(s,"\"어느 사진이 방해인가\"를 맞히는 정확도",0.78,2.1,5.6,0.26,{fontSize:10.5,color:C.gray});
  s.addTable([
    [m("",{...cc,fontSize:11}),m("우리 (마스킹)",{...cc,fontSize:11,bold:true}),m("FOCUS식 (픽셀 노이즈)",{...cc,fontSize:11})],
    [m("3B",{...cc,fontSize:11}),m("0.730",{...cc,fontSize:12,bold:true,color:C.green}),m("0.637",{...cc,fontSize:11})],
    [m("7B",{...cc,fontSize:11}),m("0.937",{...cc,fontSize:12,bold:true,color:C.green}),m("0.817",{...cc,fontSize:11})],
  ],{x:0.85,y:2.42,w:5.45,rowH:[0.3,0.3,0.3],...TBL});
  txt(s,"노이즈는 입력 분포 밖으로 나가는 거친 교란이고,\n마스킹은 깨끗한 인과 절제입니다. 두 스케일 모두 일관.",0.85,3.36,5.45,0.32,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.15});
  box(s,6.78,1.64,6.02,2.1,C.lightorange,C.orange,1.4);
  txt(s,"정정 — 개입 단계에서는 차이가 없습니다",7.01,1.78,5.6,0.3,{fontSize:13,bold:true,color:C.orange});
  txt(s,"두 방법이 모두 방해 사진을 맞게 고른 문항만 비교하면:",7.01,2.1,5.6,0.26,{fontSize:10.5,color:C.gray});
  s.addTable([
    [m("",{...cc,fontSize:10.5}),m("우리",{...cc,fontSize:10.5}),m("FOCUS식",{...cc,fontSize:10.5}),m("차이 95%CI",{...cc,fontSize:10.5})],
    [m("3B N=3",{...cc,fontSize:10.5}),m("0.9423",{...cc,fontSize:10.5}),m("0.9398",{...cc,fontSize:10.5}),m("[−0.008,+0.014]",{...cc,fontSize:10.5,color:C.orange})],
    [m("7B N=3",{...cc,fontSize:10.5}),m("0.9153",{...cc,fontSize:10.5}),m("0.9083",{...cc,fontSize:10.5}),m("[−0.005,+0.020]",{...cc,fontSize:10.5,color:C.orange})],
  ],{x:7.01,y:2.42,w:5.55,rowH:[0.3,0.3,0.3],...TBL});
  txt(s,"→ 전체 우위(3B +0.117~+0.210)는 판별 정확도 차이에서\n   나온 것이고, 고치는 방식 자체는 동급입니다.",7.01,3.36,5.55,0.32,{fontSize:10.5,bold:true,color:C.orange,lineSpacingMultiple:1.15});
  box(s,0.55,3.92,12.25,1.16,C.lightblue,C.blue,1.4);
  txt(s,"그래서 주장을 이렇게 좁힙니다",0.85,4.04,11.7,0.3,{fontSize:13,bold:true,color:C.blue});
  txt(s,"\"우리 개입이 더 낫다\"  (X)   →   \"마스킹 기반 반사실이 픽셀 노이즈보다 정확한 판별자다\"  (O)",0.85,4.38,11.7,0.32,{fontSize:13,bold:true,color:C.navy});
  txt(s,"판별과 개입에 같은 수단(attention 마스크)을 쓰므로 이미지 인코딩(비용의 66%)을 N+1회 재사용할 수 있습니다. 픽셀을 바꾸면 매번 재인코딩해야 합니다.",0.85,4.72,11.7,0.32,{fontSize:10,color:C.navy});
  box(s,0.55,5.24,12.25,0.8,C.light,C.line,1);
  txt(s,"정직하게 붙이는 조건:  원 논문 하이퍼파라미터를 그대로 옮긴 재현이 아니라 \"N+1 반사실 + 개입 수단\"만 통제한 비교입니다.\n인코딩 재사용은 아직 구현하지 않았으므로 \"더 빠르다\"는 주장하지 않습니다.",0.85,5.24,11.7,0.8,{fontSize:10.5,color:C.navy,valign:"middle",lineSpacingMultiple:1.2});
  take(s,"→ 우위 지점이 어디인지 정확히 특정했습니다. 이게 논문의 주장 범위가 됩니다","1F77B4");
  s.addNotes("세 번째 근거입니다. FOCUS와 처음 비교했는데, 전체적으로는 이겼지만 분해해보니 우위가 판별 단계에서 나온 것이었습니다. 고치는 방식 자체는 동급입니다. 그래서 주장을 마스킹 기반 반사실이 더 정확한 판별자라는 쪽으로 좁힙니다.");
}

// ═══ 5 스스로 정정 ═══
{ const s=pres.addSlide();
  kick(s,"검증 태도 — 유리한 결과를 스스로 분해했습니다");
  head(s,"처음엔 더 좋아 보였는데, 쪼개보니 조건부였습니다");
  box(s,0.55,1.3,12.25,2.3,C.lightorange,C.orange,1.4);
  txt(s,"정정 — \"읽기만 차단\"이 \"통째 삭제\"보다 낫다는 주장",0.85,1.44,11.7,0.3,{fontSize:14,bold:true,color:C.orange});
  txt(s,"전체로 보면 0.7643 vs 0.6472 로 유의하게 좋았습니다. 그런데 판별 성공/실패로 나눠보니:",0.85,1.78,11.7,0.28,{fontSize:11.5,color:C.navy});
  s.addTable([
    [m("3B · 방해 3장",hd),m("읽기만 차단",hd),m("통째 삭제",hd),m("차이",hd)],
    [m("판별 성공 (219건)",{bold:true}),m("0.9397"),m("0.9397"),m("margin이 219/219 완전 동일",{bold:true,color:C.orange})],
    [m("판별 실패 (81건)",{bold:true}),m("0.0753"),m("0.0338"),m("CI [−0.012, +0.117] · 단독으론 비유의")],
  ],{x:0.85,y:2.14,w:11.7,rowH:[0.32,0.32,0.32],...TBL});
  txt(s,"이유: 현 벤치는 관련 사진이 항상 첫 번째입니다. 맞게 고르면 차단 대상이 전부 뒤쪽 사진인데, 첫 번째 사진은 causal attention 때문에 애초에 뒤쪽을 볼 수 없습니다 → 두 방식이 수학적으로 같아집니다.",0.85,3.14,11.7,0.36,{fontSize:11,color:C.navy,lineSpacingMultiple:1.15});
  box(s,0.55,3.74,6.05,1.28,C.lightblue,C.blue,1.3);
  txt(s,"지금 GPU에서 검정 중",0.78,3.86,5.6,0.28,{fontSize:12.5,bold:true,color:C.blue});
  txt(s,"새 벤치(anchor)는 관련 사진 위치가 무작위라\n이 동치가 깨집니다. 거기서 차이가 나면\n\"개입 방식 자체가 낫다\"가 성립합니다.",0.78,4.18,5.6,0.72,{fontSize:11,color:C.navy,lineSpacingMultiple:1.2});
  box(s,6.78,3.74,6.02,1.28,C.lightgreen,C.green,1.3);
  txt(s,"지금 말할 수 있는 것",7.01,3.86,5.6,0.28,{fontSize:12.5,bold:true,color:C.green});
  txt(s,"\"판별이 틀렸을 때 읽기 차단이 덜 망가진다\"\n— 선택 오류에 강건하다는 성질입니다.\n검정 전까지는 여기까지만 주장합니다.",7.01,4.18,5.6,0.72,{fontSize:11,color:C.navy,lineSpacingMultiple:1.2});
  box(s,0.55,5.18,12.25,0.86,C.navy,null,0);
  txt(s,"이런 분해를 하지 않았다면 리뷰어가 찾아냈을 것입니다. 미리 찾아서 주장 범위를 좁히는 편이 논문에 유리합니다.",0.85,5.18,11.7,0.86,{fontSize:12.5,bold:true,color:C.white,valign:"middle"});
  take(s,"→ 사전 등록 누적 10건 중 6건이 기준 미달·예측 반대였고, 전부 기록했습니다");
  s.addNotes("이번 주에 제가 처음 보고드리려던 것보다 주장을 좁혔습니다. 전체로 보면 읽기 차단이 훨씬 좋았는데, 판별 성공과 실패로 나눠보니 성공한 문항에서는 완전히 동일했습니다. 현 벤치가 관련 사진을 항상 첫 번째에 두기 때문에 구조적으로 같아지는 것이었습니다. 새 벤치에서 다시 검정하고 있습니다.");
}

// ═══ 6 접은 것 / 보류 ═══
{ const s=pres.addSlide();
  kick(s,"접은 것 — 다만 폐기가 아니라 보류입니다");
  head(s,"두 주장을 접었습니다. 되살릴 경로는 남겨뒀습니다");
  const f=[
    ["경로 대비","같은 사진으로 '가장 깨끗한 경로'와 '가장 오염된 경로'를 만들어 빼는 추가 기능",
     "방해가 정답과 같은 방향으로 미는 문항에서 크게 해로움 (0.988 → 0.862)",
     "게이트 추가 / 문항별 적응 β / '방해가 얼마나 미는가'를 재는 진단 지표로 전환"],
    ["통합 주장","'막아라(MIMIC) vs 열어라(CAPL)'로 갈린 기존 연구를 우리 분해가 설명한다",
     "MIMIC식 균일 차단이 무개입보다 나쁨 (3B 0.412 vs 0.697)",
     "층 구간을 상대 위치로 맞춰 스윕 (3B 36층 / 7B 28층이라 절대값 12~23은 위치가 다름)"],
  ];
  f.forEach((x,i)=>{const y=1.3+i*1.5;
    box(s,0.55,y,12.25,1.36,C.lightred,C.red,1.3);
    txt(s,x[0],0.8,y+0.14,2.3,0.32,{fontSize:14,bold:true,color:C.red});
    txt(s,x[1],0.8,y+0.5,5.5,0.5,{fontSize:10.5,color:C.gray,lineSpacingMultiple:1.15});
    txt(s,"왜 접었나",6.5,y+0.14,2.6,0.28,{fontSize:11,bold:true,color:C.navy});
    txt(s,x[2],6.5,y+0.44,3.0,0.6,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.15});
    txt(s,"되살릴 경로",9.7,y+0.14,2.9,0.28,{fontSize:11,bold:true,color:C.green});
    txt(s,x[3],9.7,y+0.44,3.0,0.8,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.15});});
  box(s,0.55,4.36,6.05,1.66,C.lightgreen,C.green,1.3);
  txt(s,"중요 — 핵심 방법 자체는 안전합니다",0.78,4.48,5.6,0.28,{fontSize:12.5,bold:true,color:C.green});
  txt(s,"해로운 것은 '빼기'였고, '읽기 차단'은 아닙니다.\n방해가 정답 방향으로 미는 문항에서도:",0.78,4.8,5.6,0.36,{fontSize:11,color:C.navy,lineSpacingMultiple:1.15});
  s.addTable([
    [m("",{...cc,fontSize:10.5}),m("무개입 → 읽기차단",{...cc,fontSize:10.5}),m("95%CI",{...cc,fontSize:10.5})],
    [m("3B",{...cc,fontSize:10.5}),m("0.9937 → 0.9883",{...cc,fontSize:10.5}),m("[−0.013,+0.001]",{...cc,fontSize:10.5,color:C.green})],
    [m("7B",{...cc,fontSize:10.5}),m("0.9847 → 0.9897",{...cc,fontSize:10.5}),m("[−0.002,+0.013]",{...cc,fontSize:10.5,color:C.green})],
  ],{x:0.78,y:5.22,w:5.6,rowH:[0.26,0.26,0.26],...TBL});
  box(s,6.78,4.36,6.02,1.66,C.lightgray,C.gray,1.2);
  txt(s,"그 밖에 폐기가 아니라 보류한 것 2건",7.01,4.48,5.6,0.28,{fontSize:12.5,bold:true,color:C.navy});
  txt(s,"· 기권(abstention) 게이트 — 확신도 신호 하나로는 실패.\n  CLIP과 우리 판별의 '불일치'를 신호로 쓰는 방안이 남음\n\n· top-k 일반화 — 관련 사진 개수를 추정하지 않고\n  무조건 k개를 남긴 것이 원인일 수 있음",7.01,4.8,5.6,1.08,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.2});
  take(s,"→ 실패 4건 전부 원인과 되살릴 경로를 문서에 남겼습니다 (docs/38)");
  s.addNotes("접은 것 두 가지입니다. 다만 폐기가 아니라 보류입니다. 원인을 규명했고 되살릴 경로를 문서에 남겼습니다. 중요한 건 해로웠던 게 빼기였지 읽기 차단이 아니라는 점입니다. 핵심 방법은 방해가 정답 방향으로 미는 경우에도 안전합니다.");
}

// ═══ 7 다음 단계 ═══
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  kick(s,"다음 단계",true);
  head(s,"CVPR 2027 마감까지 11주 — 중단 조건을 먼저 둡니다",true);
  const plan=[["이번 주","진행 중인 검정 마무리 (개입 방식 자체가 나은가) · 판별 개선 (CLIP과의 불일치를 신호로)","실현 0.764 → 오라클 0.903 격차 줄이기","FFC94D"],
              ["1–2주","공개 벤치마크 포팅 (MuirBench · BLINK)","★ 여기서 재현 안 되면 접습니다","FF9E80"],
              ["3–4주","다른 모델군 1개 (LLaVA-OneVision-7B) 마스크 훅 포팅","기전이 Qwen 고유물이 아닌가","7EC8F5"],
              ["5–7주","인코더 재사용 구현 → 실측 속도 · 방해 5~8장 · 생성(자유 서술) 평가","비용 주장 확정 / 예-아니오 논문 탈피","7EC8F5"],
              ["8–11주","초고 → 내부 리뷰 2회 → 초록 11/06 → 제출 11/13","—","8CE0B0"]];
  plan.forEach((p,i)=>{const y=1.34+i*0.84;
    box(s,0.55,y,12.25,0.72,"1D3850","2E4E6B",1);
    txt(s,p[0],0.8,y,1.25,0.72,{fontSize:12.5,bold:true,color:p[3],valign:"middle"});
    txt(s,p[1],2.2,y,6.5,0.72,{fontSize:11.5,color:C.white,valign:"middle"});
    txt(s,"→ "+p[2],8.9,y,3.7,0.72,{fontSize:10.5,color:"9FB8CE",valign:"middle"});});
  box(s,0.55,5.62,12.25,0.9,"3A2430","6B3A4A",1.2);
  txt(s,"가장 큰 위험: 지금 모든 결과가 우리가 만든 COCO 기반 벤치와 예/아니오 단답에 한정됩니다.",0.85,5.72,11.7,0.28,{fontSize:12,bold:true,color:"FFB4A2"});
  txt(s,"공개 벤치마크에서 재현되지 않으면 2주차에 접습니다. 그 판정 기준을 지금 문서로 고정해두겠습니다.",0.85,6.04,11.7,0.28,{fontSize:11,color:"D0BCC4"});
  s.addNotes("11주 남았습니다. 이번 주에는 진행 중인 검정을 마무리하고 판별 개선을 시도합니다. 1, 2주차 공개 벤치마크가 중단 조건입니다. 지금 결과가 전부 자체 제작 벤치와 예아니오 단답에 한정되어 있어서, 공개 벤치에서 재현되지 않으면 접겠습니다.");
}

pres.writeFile({ fileName: "/Users/hansangmin/Source-Depth/meeting/_generated/deck_v9.pptx" })
  .then(()=>console.log("DECK v9 WRITTEN"));
