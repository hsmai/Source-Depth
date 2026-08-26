// SourceDepth v11 — 사용자 초안 7장 뼈대 + 원인규명·차별성·신뢰도 3장 추가
const pptxgen = require("pptxgenjs");
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE";
const C = { navy:"1F3B57", darkbg:"142638", blue:"1F77B4", red:"D62728", green:"2E8B57",
  orange:"B06A00", gray:"6B7280", white:"FFFFFF", light:"EFF4F9", lightred:"FBEAEA",
  lightgray:"F3F5F7", lightgreen:"E9F4EE", lightblue:"E8F1FA", lightorange:"FFF8E8",
  line:"D5DEE8", mute:"9AA6B2" };
const F="Arial", FIG="/Users/hansangmin/Source-Depth/meeting/figs/";
const kick=(s,t,d)=>s.addText(t,{x:0.55,y:0.26,w:11.5,h:0.3,fontFace:F,fontSize:11,bold:true,color:d?"9FB8CE":C.blue,margin:0});
const head=(s,t,d)=>s.addText(t,{x:0.55,y:0.54,w:12.2,h:0.66,fontFace:F,fontSize:21,bold:true,color:d?C.white:C.navy,margin:0});
const take=(s,t,c)=>{s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.55,y:6.68,w:12.25,h:0.54,rectRadius:0.08,fill:{color:c||C.navy}});
  s.addText(t,{x:0.85,y:6.68,w:11.75,h:0.54,fontFace:F,fontSize:11.5,bold:true,color:C.white,margin:0,valign:"middle"});};
const box=(s,x,y,w,h,f,l,lw)=>s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.06,fill:{color:f},line:l?{color:l,width:lw||1}:null});
const txt=(s,t,x,y,w,h,o)=>s.addText(t,Object.assign({x,y,w,h,fontFace:F,margin:0},o));
const img=(s,n,ar)=>{const h=5.32,w=h/ar; s.addImage({path:FIG+n,x:(13.33-w)/2,y:1.16,w,h});};

// 1 표지
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  txt(s,"2026-08-26 · 주간 진행 보고 · 한상민",0.7,0.6,12.0,0.3,{fontSize:12,bold:true,color:"7EC8F5"});
  txt(s,"Source Depth",0.7,1.06,12.0,0.86,{fontSize:44,bold:true,color:C.white});
  txt(s,"벤치마크 수정  |  문제 실재 파악  |  비교  |  원인 규명",0.7,2.06,12.0,0.4,{fontSize:17,color:"AFC6DA"});
  const cards=[["문제가 더 심각했다","위치 힌트를 없앤 새 벤치","0.453","아무 처리도 안 했을 때\n(동전 던지기 0.50 이하)","8CE0B0"],
               ["스스로 찾아서 고친다","방해 사진을 알려주지 않아도","0.521 → 0.764","사진 4장 · 상한 0.903","7EC8F5"],
               ["원인을 특정했다","통념과 반대 방향의 측정","0.697 → 0.403","이미지끼리 섞임을 끊으면\n오히려 무너진다","FFC94D"]];
  cards.forEach((c,i)=>{const x=0.7+i*4.1,y=2.66;
    box(s,x,y,3.9,2.86,"1D3850","2E4E6B",1);
    txt(s,c[0],x+0.25,y+0.2,3.4,0.32,{fontSize:14.5,bold:true,color:c[4]});
    txt(s,c[1],x+0.25,y+0.56,3.4,0.3,{fontSize:10.5,color:"9FB8CE"});
    txt(s,c[2],x+0.25,y+0.94,3.4,0.62,{fontSize:c[2].length>9?23:29,bold:true,color:c[4],align:"center"});
    txt(s,c[3],x+0.25,y+1.7,3.4,0.62,{fontSize:11,color:C.white,align:"center",lineSpacingMultiple:1.25});});
  box(s,0.7,5.7,12.1,0.94,"1D3850","3E6E8E",1.4);
  txt(s,"어떤 수치가 벤치마크와 무관하게 성립하고, 어떤 수치가 외부 검증을 기다리는지 9페이지에서 구분해 말씀드립니다",1.0,5.8,11.5,0.3,{fontSize:12.5,bold:true,color:"FFC94D"});
  txt(s,"과하게 주장했던 2건은 스스로 분해해 범위를 좁혔습니다 · 접은 주장 2건은 되살릴 경로와 함께 보관 중입니다",1.0,6.14,11.5,0.3,{fontSize:11,color:"9FB8CE"});
  s.addNotes("이번 주는 벤치마크를 고치고, 문제가 실재하는지 다시 확인하고, 기존 연구와 비교하고, 원인을 특정했습니다. 그리고 어떤 수치를 어디까지 믿을 수 있는지도 정리했습니다.");
}
// 2 문제 실재
{ const s=pres.addSlide();
  kick(s,"문제 실재 여부  ·  유/무관 이미지 위치 무작위");
  head(s,"위치 힌트를 없앤 새 벤치에서 문제가 더 커졌습니다");
  img(s,"wk_a_problem.png",780/1400);
  take(s,"→ 가장 큰 약점을 스스로 공격했는데, 결과는 문제가 더 크다는 쪽이었습니다");
  s.addNotes("지금까지 가장 큰 약점이 질문에서 '첫 번째 사진'이라고 위치를 알려준다는 점이었습니다. 관련 사진을 내용으로만 특정하고 위치를 무작위로 섞은 벤치를 새로 만들었더니, 문제가 사라지기는커녕 더 커져서 아무 처리도 안 하면 동전 던지기보다 못했습니다.");
}
// 3 실현 성능
{ const s=pres.addSlide();
  kick(s,"실현 성능");
  head(s,"어느 사진이 유/무관인지 알려주지 않아도 Ours 성능이 보장되는가?");
  const bars=[["아무것도 안 함",0.521,C.mute,false],["Ours (스스로 찾아서 처리)",0.764,C.green,true],["상한 (정답을 알려준 경우)",0.903,C.gray,false]];
  const X0=4.5,BW=6.1;
  bars.forEach((b,i)=>{const y=1.5+i*0.86;
    txt(s,b[0],0.8,y+0.14,3.5,0.44,{fontSize:14,bold:b[3],color:b[3]?C.navy:C.gray,align:"right"});
    box(s,X0,y,BW,0.62,"F1F4F7",C.line,1);
    box(s,X0,y,BW*((b[1]-0.45)/0.5),0.62,b[2],null,0);
    txt(s,b[1].toFixed(3),X0+BW+0.2,y+0.14,1.2,0.44,{fontSize:21,bold:true,color:b[2]});});
  txt(s,"판별력 점수 · 사진 4장 · 문항 300개 · 3B  (이 벤치는 관련 사진이 항상 첫 번째 — 위치를 섞은 결과는 2페이지)",X0,4.2,7.6,0.3,{fontSize:10,italic:true,color:C.gray});
  const kv=[["방해 사진이 많을수록 이득이 커짐","1장 +0.06   2장 +0.17   3장 +0.24",C.green,C.lightgreen],
            ["고정 임계값 정확도로 봐도","0.477  →  0.697",C.blue,C.lightblue],
            ["남은 격차는 전부 판별 오류","0.764  vs  상한 0.903",C.orange,C.lightorange]];
  kv.forEach((k,i)=>{const x=0.55+i*4.12;
    box(s,x,4.6,3.95,1.5,k[3],k[2],1.3);
    txt(s,k[0],x+0.22,4.74,3.5,0.32,{fontSize:11.5,bold:true,color:k[2],lineSpacingMultiple:1.1});
    txt(s,k[1],x+0.22,5.24,3.5,0.6,{fontSize:15,bold:true,color:k[2],align:"center"});});
  take(s,"→ 6개 조건 중 5개에서 통계적으로 유의. 컨트롤러를 포함한 실현 수치를 처음 쟀습니다","2E8B57");
  s.addNotes("지금까지 모든 수치는 어느 사진이 방해인지 알려준 조건이었는데, 이번에 모델이 스스로 찾게 한 실현 성능을 처음 쟀습니다. 방해 사진이 많을수록 이득이 커져서 3장일 때 +0.24였고, 6개 조건 중 5개가 통계적으로 유의했습니다.");
}
// 4 기존 대비 — 방식
{ const s=pres.addSlide();
  kick(s,"기존 대비  ·  방식");
  head(s,"FOCUS는 무관한 사진을 고르지 않습니다 — 방식이 다릅니다");
  img(s,"wk_e_mechanism.png",890/1400);
  take(s,"→ FOCUS는 사진을 망가뜨려 한 장씩 물어보고 합칩니다. 우리는 사진을 그대로 두고 읽기 통로만 막습니다");
  s.addNotes("FOCUS는 사진을 하나씩만 남기고 나머지를 노이즈로 덮은 결과를 전부 합치는 방식이라, 무관한 사진을 고르는 단계 자체가 없습니다. 저희는 하나씩 빼보며 무관한 사진을 특정한 뒤, 사진은 그대로 두고 질문이 그것을 읽는 경로만 막습니다.");
}
// 5 기존 대비 — 결과
{ const s=pres.addSlide();
  kick(s,"기존 대비  ·  결과");
  head(s,"논문 수식을 재구성해 같은 문항에서 측정했습니다 (사진 2장)");
  img(s,"wk_b_focus.png",800/1400);
  take(s,"→ 두 모델 모두 우위. 다만 공식 코드 재현이 아니므로 다음 2주에 정식으로 다시 잽니다","B06A00");
  s.addNotes("같은 문항에서 FOCUS 논문 수식을 그대로 재구성해 비교했더니 두 모델 모두 저희가 높았고, 3B에서는 FOCUS가 아무 처리도 안 한 것보다 낮았습니다. 다만 공식 코드가 아니라 수식을 재구성한 것이고 사진 2장 조건에서만 가능했던 비교라, 공식 코드 재현은 다음 2주 안에 하겠습니다.");
}
// 6 원인 규명 (NEW)
{ const s=pres.addSlide();
  kick(s,"원인 규명");
  head(s,"왜 하필 '읽기' 경로인가 — 통념과 반대였습니다");
  img(s,"wk_f_mechanism_why.png",820/1400);
  take(s,"→ 처방을 먼저 정한 게 아니라, 두 경로를 각각 끊어보고 원인을 특정했습니다","2E8B57");
  s.addNotes("기존 통념은 여러 이미지가 섞여서 환각이 생긴다는 것이고, 그래서 MIMIC은 섞임을 막고 CAPL은 오히려 더 엽니다. 그런데 저희가 섞임을 끊어보니 0.697에서 0.403으로 오히려 무너졌습니다. 배치와 모델과 질문 유형을 바꿔 열 개 설정에서 재봤는데 이미지끼리 차단이 이득인 설정이 하나도 없었습니다.");
}
// 7 핵심 주장
{ const s=pres.addSlide();
  kick(s,"핵심 주장");
  head(s,"기여는 '어느 사진을 고르는가'가 아니라 '무엇을 자르는가'입니다");
  img(s,"wk_d_selector.png",660/1400);
  take(s,"→ 연구 범위를 좁혔습니다: selector 경쟁이 아니라, 찾은 뒤 attention 어디를 끊는가에 대한 연구","1F77B4");
  s.addNotes("판별을 CLIP이 대신 해줘도 읽기 경로만 차단하는 쪽이 사진을 통째로 지우는 것보다 유의하게 낫습니다. 두 모델 모두 그렇습니다. 그래서 우리 기여는 판별이 아니라 개입 방식이라고 범위를 좁혔습니다.");
}
// 8 차별성 (NEW)
{ const s=pres.addSlide();
  kick(s,"차별성");
  head(s,"기존 연구와 우리는 서로 다른 곳에 손을 댑니다");
  img(s,"fig5_novelty.png",900/1600);
  take(s,"→ 여러 사진 중 특정 한 장으로 가는 '읽기 경로'만 끊은 연구는 문헌에 없습니다");
  s.addNotes("기존 연구를 개입 지점으로 정리하면 네 줄이 나옵니다. 입력 픽셀을 바꾸거나, 연결을 통째로 바꾸거나, 출력을 보정하거나입니다. 맨 아래 줄, 연결 중 한 칸만 바꾸는 자리는 비어 있습니다.");
}
// 9 신뢰도 (NEW)
{ const s=pres.addSlide();
  kick(s,"수치의 신뢰도");
  head(s,"이 수치들을 어디까지 믿을 수 있나");
  img(s,"wk_g_trust.png",830/1400);
  take(s,"→ 기전은 지금 단단합니다. 성능 수치는 아직 우리 벤치 안의 값입니다","B06A00");
  s.addNotes("벤치마크가 자체 제작이라는 점 때문에 증거를 둘로 나눠서 봐야 합니다. 기전 발견은 같은 문항 같은 모델에서 마스크 한 칸만 바꾼 인과 개입이라 벤치마크에 흔들리지 않고, 열 개 설정에서 재현됐으며, 마스킹이 실제 삭제와 98.3% 같은 답을 낸다는 것도 확인했습니다. 반면 성능 수치는 우리 문항의 난이도가 그대로 반영되므로 외부 검증이 필요하고, 그게 다음 2주 계획입니다.");
}
// 10 다음 계획
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  kick(s,"다음 계획",true);
  head(s,"경쟁 방법과 같은 벤치·같은 모델에서 직접 붙는 것이 최우선입니다",true);
  box(s,0.55,1.26,12.25,1.32,"1D3850","3E6E8E",1.6);
  txt(s,"FOCUS는 우리와 같은 모델(Qwen2.5-VL 3B / 7B)로 공개 벤치마크를 평가했고, 코드도 공개되어 있습니다",0.85,1.38,11.7,0.3,{fontSize:12.5,bold:true,color:"FFC94D"});
  txt(s,"MuirBench +3.2%p · Mantis-Eval +5.5%p · MIRB +1.7%p · Winoground · VisMin",0.85,1.72,11.7,0.28,{fontSize:11.5,color:C.white});
  txt(s,"→ 같은 벤치에 우리 방법을 올리면 '공개 벤치 검증'과 'FOCUS 정식 비교'가 한 번에 끝납니다",0.85,2.06,11.7,0.3,{fontSize:12,bold:true,color:"8CE0B0"});
  const plan=[["1–2주","MuirBench · Mantis-Eval 에 우리 방법 + FOCUS 공식 코드를 같은 조건으로","★ 여기서 밀리면 방향을 바꿉니다","FF9E80"],
              ["3주","관련도를 이산이 아니라 연속으로 — 개입 강도 라우팅","실현 0.76 → 상한 0.90 격차 줄이기","FFC94D"],
              ["4–5주","다른 모델군 (InternVL3 · LLaVA-OneVision — FOCUS가 쓴 것과 동일)","기전이 Qwen 고유물이 아닌가","7EC8F5"],
              ["6–8주","생성 평가 (Winoground · VisMin) · 인코더 재사용 후 실측 속도","예-아니오 논문 탈피 / 비용 주장 확정","7EC8F5"],
              ["9–11주","초고 → 내부 리뷰 2회 → 초록 11/06 → 제출 11/13","—","8CE0B0"]];
  plan.forEach((p,i)=>{const y=2.74+i*0.68;
    box(s,0.55,y,12.25,0.58,"1D3850","2E4E6B",1);
    txt(s,p[0],0.8,y,1.25,0.58,{fontSize:12,bold:true,color:p[3],valign:"middle"});
    txt(s,p[1],2.2,y,6.6,0.58,{fontSize:11,color:C.white,valign:"middle"});
    txt(s,"→ "+p[2],8.95,y,3.7,0.58,{fontSize:10,color:"9FB8CE",valign:"middle"});});
  box(s,0.55,6.24,12.25,0.78,"3A2430","6B3A4A",1.2);
  txt(s,"중단 조건: 같은 벤치·같은 모델에서 FOCUS를 넘지 못하면, 방법 논문이 아니라 기전 분석 논문으로 방향을 바꿉니다.",0.85,6.34,11.7,0.28,{fontSize:11.5,bold:true,color:"FFB4A2"});
  txt(s,"지금 모든 성능 수치가 저희가 만든 벤치와 예/아니오 단답에 한정되어 있다는 점이 가장 큰 위험입니다.",0.85,6.64,11.7,0.28,{fontSize:10.5,color:"D0BCC4"});
  s.addNotes("가장 중요한 다음 단계는 경쟁 방법과 같은 벤치, 같은 모델에서 직접 붙는 것입니다. FOCUS가 저희와 같은 Qwen2.5-VL로 공개 벤치마크를 평가했고 코드도 공개돼 있어서, 같은 벤치에 저희 방법을 올리면 공개 벤치 검증과 FOCUS 정식 비교가 한 번에 끝납니다. 여기서 밀리면 방법 논문이 아니라 기전 분석 논문으로 방향을 바꾸겠습니다.");
}
pres.writeFile({fileName:"/Users/hansangmin/Source-Depth/meeting/_generated/deck_v11.pptx"}).then(()=>console.log("DECK v11 WRITTEN"));
