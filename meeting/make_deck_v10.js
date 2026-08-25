// SourceDepth v10 — 사용자 초안(7장) 구조 유지 + 정정·그림 반영. 2026-08-26 미팅.
const pptxgen = require("pptxgenjs");
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE";
const C = { navy:"1F3B57", darkbg:"142638", blue:"1F77B4", red:"D62728", green:"2E8B57",
  orange:"B06A00", gray:"6B7280", white:"FFFFFF", light:"EFF4F9", lightred:"FBEAEA",
  lightgray:"F3F5F7", lightgreen:"E9F4EE", lightblue:"E8F1FA", lightorange:"FFF8E8", line:"D5DEE8", mute:"9AA6B2" };
const F = "Arial";
const FIG = "/Users/hansangmin/Source-Depth/meeting/figs/";
const kick=(s,t,d)=>s.addText(t,{x:0.55,y:0.26,w:11.5,h:0.3,fontFace:F,fontSize:11,bold:true,color:d?"9FB8CE":C.blue,margin:0});
const head=(s,t,d)=>s.addText(t,{x:0.55,y:0.54,w:12.2,h:0.68,fontFace:F,fontSize:22,bold:true,color:d?C.white:C.navy,margin:0});
const take=(s,t,c)=>{s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.55,y:6.66,w:12.25,h:0.56,rectRadius:0.08,fill:{color:c||C.navy}});
  s.addText(t,{x:0.85,y:6.66,w:11.75,h:0.56,fontFace:F,fontSize:12,bold:true,color:C.white,margin:0,valign:"middle"});};
const box=(s,x,y,w,h,f,l,lw)=>s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.06,fill:{color:f},line:l?{color:l,width:lw||1}:null});
const txt=(s,t,x,y,w,h,o)=>s.addText(t,Object.assign({x,y,w,h,fontFace:F,margin:0},o));

// ═══ 1  표지 ═══
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  txt(s,"2026-08-26 · 주간 진행 보고 · 한상민",0.7,0.62,12.0,0.3,{fontSize:12,bold:true,color:"7EC8F5"});
  txt(s,"Source Depth",0.7,1.1,12.0,0.9,{fontSize:44,bold:true,color:C.white});
  txt(s,"이번 주 결론 — 연구 가치가 강해졌습니다",0.7,2.16,12.0,0.45,{fontSize:20,bold:true,color:"8CE0B0"});
  const cards=[["문제가 더 심각했다","위치 힌트를 없앤 새 벤치에서","0.453","아무 처리도 안 했을 때의 판별력\n(동전 던지기 0.50 이하)","8CE0B0"],
               ["스스로 찾아서 고친다","어느 사진이 방해인지 안 알려줘도","0.521 → 0.764","사진 4장 조건 · 상한은 0.903","7EC8F5"],
               ["기존 연구보다 낫다","FOCUS 논문 수식을 재구성 (사진 2장)","0.756 vs 0.583","같은 조건에서 두 모델 모두 우위\n※ 공식 코드 재현은 다음 단계","FFC94D"]];
  cards.forEach((c,i)=>{const x=0.7+i*4.1,y=2.86;
    box(s,x,y,3.9,2.9,"1D3850","2E4E6B",1);
    txt(s,c[0],x+0.25,y+0.2,3.4,0.32,{fontSize:14.5,bold:true,color:c[4]});
    txt(s,c[1],x+0.25,y+0.56,3.4,0.3,{fontSize:10.5,color:"9FB8CE"});
    txt(s,c[2],x+0.25,y+0.96,3.4,0.66,{fontSize:c[2].length>9?24:30,bold:true,color:c[4],align:"center"});
    txt(s,c[3],x+0.25,y+1.76,3.4,0.6,{fontSize:11,color:C.white,align:"center",lineSpacingMultiple:1.25});});
  box(s,0.7,5.94,12.1,0.72,"3A2430","6B3A4A",1);
  txt(s,"동시에 — 한계가 정확히 어디인지도 찾았고, 과하게 주장했던 2건은 스스로 정정했습니다",1.0,5.94,11.5,0.72,{fontSize:12.5,bold:true,color:"FFB4A2",valign:"middle"});
  s.addNotes("이번 주 결론부터 말씀드리면 연구 가치가 강해졌습니다. 근거 세 가지가 있고, 동시에 한계가 어디인지도 정확히 찾았습니다.");
}

// ═══ 2  문제 실재 여부 ═══
{ const s=pres.addSlide();
  kick(s,"문제 실재 여부");
  head(s,"위치 힌트를 없앤 새 벤치에서 문제가 더 커졌습니다");
  s.addImage({path:FIG+"wk_a_problem.png",x:1.82,y:1.14,w:9.69,h:5.40});
  take(s,"→ 가장 큰 약점을 스스로 공격했는데, 결과는 문제가 더 크다는 쪽이었습니다");
  s.addNotes("지금까지 가장 큰 약점이 질문에서 첫 번째 사진이라고 위치를 알려준다는 것이었습니다. 그래서 위치를 없앤 벤치를 새로 만들었는데, 문제가 사라지기는커녕 더 커졌습니다. 3B는 아무것도 안 했을 때 찍기보다 못합니다.");
}

// ═══ 3  실현 성능 ═══
{ const s=pres.addSlide();
  kick(s,"실현 성능");
  head(s,"어느 사진이 방해인지 알려주지 않아도 작동합니다");
  txt(s,"지금까지 모든 수치는 방해 사진을 알려준 조건이었습니다. 컨트롤러를 포함한 '실현' 수치를 처음 쟀습니다.  (이 벤치는 관련 사진이 항상 첫 번째 — 위치를 섞은 결과는 2·5페이지)",0.55,1.24,12.25,0.3,{fontSize:11,color:C.gray});
  // 파이프라인
  box(s,0.55,1.62,12.25,0.92,C.lightblue,C.blue,1.3);
  const pipe=[["사진들 입력","방해가 섞여 있음"],["attention 마스킹으로\n하나씩 제외해보기","답이 가장 크게 흔들리는\n사진 = 실제로 쓰이는 사진"],["그 사진의 '읽기'만 차단","사진은 입력에 그대로 둠"]];
  pipe.forEach((p,i)=>{const x=0.85+i*4.0;
    txt(s,p[0],x,1.74,3.3,0.34,{fontSize:12.5,bold:true,color:C.navy,align:"center",lineSpacingMultiple:1.1});
    txt(s,p[1],x,2.12,3.3,0.34,{fontSize:10,color:C.gray,align:"center",lineSpacingMultiple:1.1});
    if(i<2) txt(s,"▶",x+3.4,1.9,0.5,0.3,{fontSize:16,color:C.blue,align:"center",bold:true});});
  // 막대 3개
  const bars=[["아무것도 안 함",0.521,C.mute,false],["우리 방법",0.764,C.green,true],["상한 (정답을 알려준 경우)",0.903,C.gray,false]];
  const X0=4.3, BW=6.4;
  bars.forEach((b,i)=>{const y=2.94+i*0.72;
    txt(s,b[0],0.75,y+0.1,3.4,0.4,{fontSize:13.5,bold:b[3],color:b[3]?C.navy:C.gray,align:"right"});
    box(s,X0,y,BW,0.52,"F1F4F7",C.line,1);
    box(s,X0,y,BW*((b[1]-0.45)/0.5),0.52,b[2],null,0);
    txt(s,b[1].toFixed(3),X0+BW+0.18,y+0.1,1.2,0.4,{fontSize:19,bold:true,color:b[2]});});
  txt(s,"판별력 점수 · 사진 4장 · 문항 300개 · 작은 모델(3B)",X0,5.14,6.4,0.26,{fontSize:10,italic:true,color:C.gray});
  box(s,0.55,5.5,6.05,1.02,C.lightgreen,C.green,1.3);
  txt(s,"방해 사진이 많을수록 이득이 커집니다",0.8,5.62,5.6,0.28,{fontSize:12.5,bold:true,color:C.green});
  txt(s,"1장 +0.06   →   2장 +0.17   →   3장 +0.24",0.8,5.94,5.6,0.34,{fontSize:14,bold:true,color:C.navy});
  box(s,6.78,5.5,6.02,1.02,C.lightorange,C.orange,1.3);
  txt(s,"남은 격차(0.76 → 0.90)는 전부 판별 오류입니다",7.03,5.62,5.6,0.28,{fontSize:12.5,bold:true,color:C.orange});
  txt(s,"방해 사진을 잘못 고른 문항에서 발생 — 다음 장에서 그 원인을 봅니다",7.03,5.96,5.6,0.3,{fontSize:11,color:C.navy});
  take(s,"→ 6개 조건 중 5개에서 통계적으로 유의. 이 표가 논문의 대표 결과가 됩니다","2E8B57");
  s.addNotes("지금까지 모든 숫자는 방해 사진을 알려준 조건이었습니다. 이번에 모델이 스스로 찾게 했더니 0.52에서 0.76까지 왔습니다. 상한 0.90과의 차이는 전부 잘못 고른 경우입니다.");
}

// ═══ 4  기존 대비 ═══
{ const s=pres.addSlide();
  kick(s,"기존 대비");
  head(s,"FOCUS 논문 수식을 재구성해 직접 비교했습니다");
  s.addImage({path:FIG+"wk_b_focus.png",x:1.94,y:1.14,w:9.45,h:5.40});
  take(s,"→ FOCUS는 무관한 사진을 아예 고르지 않고 전부 합칩니다. 우리는 특정해서 그 경로만 끊습니다");
  s.addNotes("FOCUS와 처음 비교했습니다. FOCUS는 무관한 사진을 구분하지 않고 사진을 하나씩만 남긴 결과를 전부 합치는 방식입니다. 두 모델 모두 우리가 유의하게 높았고, 3B에서는 FOCUS가 아무것도 안 한 것보다도 낮았습니다. 다만 공식 코드가 아니라 논문 수식을 재구성한 것이라 논문에 쓰려면 다시 재야 합니다.");
}

// ═══ 5  핵심 주장 ═══
{ const s=pres.addSlide();
  kick(s,"핵심 주장");
  head(s,"기여는 '어느 사진을 고르는가'가 아니라 '무엇을 자르는가'입니다");
  s.addImage({path:FIG+"wk_d_selector.png",x:0.94,y:1.12,w:11.46,h:5.40});
  take(s,"→ 연구 범위를 좁혔습니다: selector 경쟁이 아니라, 찾은 뒤 attention 어디를 끊는가에 대한 연구","1F77B4");
  s.addNotes("이번에 확인한 가장 중요한 결과입니다. 판별을 CLIP이 해줘도 읽기만 차단하는 쪽이 통째 삭제보다 유의하게 낫습니다. 두 모델 모두 그렇습니다. 그래서 우리 기여는 판별이 아니라 개입 방식이라고 범위를 좁혔습니다.");
}

// ═══ 6  한계와 접은 것 ═══
{ const s=pres.addSlide();
  kick(s,"한계 · 접은 것");
  head(s,"관련도는 '있다/없다'로 나뉘지 않습니다 — 여기가 다음 방향입니다");
  s.addImage({path:FIG+"wk_c_continuity.png",x:0.55,y:1.10,w:8.40,h:4.92});
  box(s,9.15,1.08,3.65,2.42,C.lightred,C.red,1.3);
  txt(s,"접은 주장 2건",9.35,1.2,3.25,0.28,{fontSize:12.5,bold:true,color:C.red});
  txt(s,"① 통합 주장 (MIMIC vs CAPL)\n   MIMIC식 차단이 아무것도 안 한 것보다\n   나빴습니다. 우리 발견(사진끼리 보는 건\n   도움된다)과는 오히려 일관됩니다.\n\n② 경로 대비 (두 상태를 빼기)\n   방해가 정답 쪽으로 미는 문항에서\n   크게 해로웠습니다.",9.35,1.52,3.25,1.86,{fontSize:9.5,color:C.navy,lineSpacingMultiple:1.22});
  box(s,9.15,3.62,3.65,1.4,C.lightgreen,C.green,1.3);
  txt(s,"핵심 방법은 안전합니다",9.35,3.74,3.25,0.28,{fontSize:12.5,bold:true,color:C.green});
  txt(s,"해로웠던 것은 '빼기'였고\n'읽기 차단'이 아닙니다.\n\n방해가 정답 쪽으로 미는 문항에서도\n손해가 없었습니다.",9.35,4.06,3.25,0.9,{fontSize:9.5,color:C.navy,lineSpacingMultiple:1.22});
  box(s,9.15,5.14,3.65,1.36,C.lightgray,C.gray,1.2);
  txt(s,"폐기가 아니라 보류입니다",9.35,5.26,3.25,0.28,{fontSize:12,bold:true,color:C.navy});
  txt(s,"실패 4건 전부 원인을 규명하고\n되살릴 경로를 문서에 남겼습니다.\n예: MIMIC은 층 구간을 상대 위치로\n다시 맞춰 재시도 (GPU 2시간)",9.35,5.58,3.25,0.84,{fontSize:9.5,color:C.navy,lineSpacingMultiple:1.22});
  take(s,"→ 판정 기준을 먼저 문서로 고정하고 실행했고, 그중 절반 이상이 기준 미달·예측 반대였습니다. 전부 기록했습니다");
  s.addNotes("한계는 관련도가 있다없다로 안 나뉜다는 것입니다. 3B는 세 문항 중 한 문항에서 두 번째 사진도 절반 이상 영향을 줍니다. 판별 정확도가 정확히 그 지점에서 0.49로 무너집니다. 그리고 두 가지 주장을 접었는데 폐기가 아니라 보류입니다. 원인을 규명하고 되살릴 경로를 남겼습니다.");
}

// ═══ 7  다음 계획 ═══
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  kick(s,"다음 계획",true);
  head(s,"경쟁 방법과 같은 벤치·같은 모델에서 직접 붙이는 것이 최우선입니다",true);
  box(s,0.55,1.28,12.25,1.42,"1D3850","3E6E8E",1.6);
  txt(s,"FOCUS는 우리와 같은 모델(Qwen2.5-VL 3B / 7B)로 공개 벤치마크를 평가했습니다",0.85,1.4,11.7,0.3,{fontSize:13,bold:true,color:"FFC94D"});
  txt(s,"MuirBench +3.2%p  ·  Mantis-Eval +5.5%p  ·  MIRB +1.7%p  ·  Winoground · VisMin  (공식 코드 공개됨)",0.85,1.74,11.7,0.3,{fontSize:12,color:C.white});
  txt(s,"→ 같은 벤치에 우리 방법을 올리면 '공개 벤치 검증'과 'FOCUS 직접 비교'가 한 번에 끝납니다. 이게 1순위입니다.",0.85,2.1,11.7,0.32,{fontSize:12.5,bold:true,color:"8CE0B0"});
  const plan=[["1–2주","MuirBench · Mantis-Eval 에 우리 방법 + FOCUS 공식 코드를 같은 조건으로","★ 여기서 밀리면 방향을 바꿉니다","FF9E80"],
              ["3주","이번 주 발견에서 나온 개선 — 적응형 개수 / 관련도 비례 차단","실현 0.76 → 상한 0.90 격차 줄이기","FFC94D"],
              ["4–5주","다른 모델군 (InternVL3 · LLaVA-OneVision — FOCUS가 쓴 것과 동일)","기전이 Qwen 고유물이 아닌가","7EC8F5"],
              ["6–8주","생성 평가 (Winoground · VisMin) · 인코더 재사용 후 실측 속도","예-아니오 논문 탈피 / 비용 주장 확정","7EC8F5"],
              ["9–11주","초고 → 내부 리뷰 2회 → 초록 11/06 → 제출 11/13","—","8CE0B0"]];
  plan.forEach((p,i)=>{const y=2.86+i*0.66;
    box(s,0.55,y,12.25,0.56,"1D3850","2E4E6B",1);
    txt(s,p[0],0.8,y,1.25,0.56,{fontSize:12,bold:true,color:p[3],valign:"middle"});
    txt(s,p[1],2.2,y,6.6,0.56,{fontSize:11,color:C.white,valign:"middle"});
    txt(s,"→ "+p[2],8.95,y,3.7,0.56,{fontSize:10,color:"9FB8CE",valign:"middle"});});
  box(s,0.55,6.24,12.25,0.78,"3A2430","6B3A4A",1.2);
  txt(s,"중단 조건: 같은 벤치·같은 모델에서 FOCUS를 넘지 못하면, 방법 논문이 아니라 기전 분석 논문으로 방향을 바꿉니다.",0.85,6.34,11.7,0.28,{fontSize:11.5,bold:true,color:"FFB4A2"});
  txt(s,"지금 모든 결과가 저희가 만든 벤치와 예/아니오 단답에 한정되어 있다는 점이 가장 큰 위험입니다.",0.85,6.64,11.7,0.28,{fontSize:10.5,color:"D0BCC4"});
  s.addNotes("가장 중요한 다음 단계는 경쟁 방법과 같은 벤치, 같은 모델에서 직접 붙는 것입니다. 다행히 FOCUS가 저희와 같은 Qwen2.5-VL 3B, 7B로 공개 벤치마크를 평가했고 코드도 공개돼 있습니다. 같은 벤치에 저희 방법을 올리면 공개 벤치 검증과 FOCUS 직접 비교가 한 번에 끝납니다. 여기서 밀리면 방법 논문이 아니라 기전 분석 논문으로 방향을 바꾸겠습니다.");
}

pres.writeFile({ fileName: "/Users/hansangmin/Source-Depth/meeting/_generated/deck_v10.pptx" })
  .then(()=>console.log("DECK v10 WRITTEN"));
