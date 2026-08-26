// SourceDepth v12 — 슬라이드는 제목 + 큰 그림 하나. 설명은 전부 스피커 노트로.
const pptxgen = require("pptxgenjs");
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE";
const C = { navy:"1F3B57", darkbg:"142638", white:"FFFFFF" };
const F="Arial", FIG="/Users/hansangmin/Source-Depth/meeting/figs/";
const SW=13.33, SH=7.5, TOP=1.16, BOT=0.30, MAXW=12.5;

function slide(title, sub, fig, ar, notes){
  const s = pres.addSlide();
  s.addText(title,{x:0.55,y:0.34,w:12.25,h:0.5,fontFace:F,fontSize:25,bold:true,color:C.navy,margin:0});
  if(sub) s.addText(sub,{x:0.55,y:0.86,w:12.25,h:0.28,fontFace:F,fontSize:13,color:"6B7280",margin:0});
  const availH = SH - (sub?1.24:1.02) - BOT, y0 = sub?1.24:1.02;
  let h = availH, w = h/ar;
  if(w > MAXW){ w = MAXW; h = w*ar; }
  s.addImage({path:FIG+fig, x:(SW-w)/2, y:y0+(availH-h)/2, w, h});
  s.addNotes(notes);
  return s;
}

// 1 표지
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  s.addText("2026-08-26 · 주간 진행 보고 · 한상민",{x:0.8,y:0.7,w:11.7,h:0.3,fontFace:F,fontSize:12,bold:true,color:"7EC8F5",margin:0});
  s.addText("Source Depth",{x:0.8,y:1.3,w:11.7,h:1.0,fontFace:F,fontSize:52,bold:true,color:C.white,margin:0});
  s.addText("벤치마크 수정   |   문제 실재 파악   |   비교   |   원인 규명",{x:0.8,y:2.42,w:11.7,h:0.4,fontFace:F,fontSize:17,color:"AFC6DA",margin:0});
  const n=[["0.453","아무 처리도 안 했을 때","8CE0B0"],["0.521 → 0.764","스스로 찾아서 처리","7EC8F5"],["0.697 → 0.403","통념대로 했더니","FFC94D"]];
  n.forEach((c,i)=>{const x=0.8+i*3.95;
    s.addText(c[0],{x,y:3.6,w:3.7,h:0.9,fontFace:F,fontSize:c[0].length>7?30:40,bold:true,color:c[2],align:"center",margin:0});
    s.addText(c[1],{x,y:4.62,w:3.7,h:0.34,fontFace:F,fontSize:13,color:"9FB8CE",align:"center",margin:0});});
  s.addNotes("이번 주는 벤치마크를 고치고, 문제가 실재하는지 다시 확인하고, 기존 연구와 비교하고, 원인을 특정했습니다. 세 숫자가 오늘의 요약입니다. 위치 힌트를 없앤 새 벤치에서 아무 처리도 안 하면 0.453으로 동전 던지기보다 못하고, 모델이 스스로 방해 사진을 찾아 처리하면 0.521에서 0.764로 올라가며, 통념대로 이미지끼리 섞임을 끊었더니 오히려 0.697에서 0.403으로 무너졌습니다.");
}

slide("문제 실재 여부", "유/무관 이미지 위치 무작위", "wk_a_problem.png", 780/1400,
"지금까지 가장 큰 약점이 질문에서 '첫 번째 사진'이라고 위치를 알려준다는 점이었습니다. 관련 사진을 내용으로만 특정하고 위치를 무작위로 섞은 벤치를 600문항 새로 만들었더니, 문제가 사라지기는커녕 더 커졌습니다.\n\n아무 처리도 안 하면 0.453으로 동전 던지기보다 못하고, 정답이 '아니오'인 문항만 보면 정확도가 0.267입니다. 같은 문항에서 방해 사진만 알려주고 처리하면 0.964까지 올라갑니다. 벤치마크가 바뀐 게 아니라 개입만 다르게 한 비교입니다.");

slide("실현 성능", "어느 사진이 유/무관인지 알려주지 않아도 Ours 성능이 보장되는가?", "wk_h_realized.png", 760/1400,
"지금까지 모든 수치는 어느 사진이 방해인지 알려준 조건이었습니다. 이번에 모델이 스스로 찾게 한 실현 성능을 처음 쟀습니다.\n\n방해 사진이 많을수록 이득이 커져서 3장일 때 +0.24였고, 6개 조건 중 5개가 통계적으로 유의했습니다. 남은 격차 0.764 대 0.903은 전부 방해 사진을 잘못 고른 경우에서 나옵니다. 참고로 이 벤치는 관련 사진이 항상 첫 번째이고, 위치를 섞은 결과는 앞 페이지입니다.");

slide("기존 대비 · 방식", null, "wk_e_mechanism.png", 890/1400,
"FOCUS는 사진을 하나씩만 남기고 나머지를 노이즈로 덮은 결과를 전부 합치는 방식입니다. 무관한 사진을 고르는 단계 자체가 없습니다. 마지막에 전부 노이즈인 경우를 빼주는데, 그건 모델이 원래 갖고 있던 편향을 제거하기 위한 것입니다.\n\n저희는 하나씩 빼보며 답이 가장 크게 흔들리는 사진을 찾아 무관한 사진을 특정한 뒤, 사진은 입력에 그대로 두고 질문이 그것을 읽는 attention 경로만 막습니다. 픽셀을 안 바꾸므로 이미지 인코딩을 한 번만 하면 된다는 차이도 있습니다.");

slide("기존 대비 · 결과", "논문 수식을 재구성해 같은 문항에서 측정 (사진 2장)", "wk_b_focus.png", 800/1400,
"같은 문항에서 FOCUS 논문 수식을 그대로 재구성해 비교했습니다. 두 모델 모두 저희가 높았고, 3B에서는 FOCUS가 아무 처리도 안 한 것보다 낮았습니다. FOCUS에게는 하이퍼파라미터를 가장 유리한 값으로 맞춰준 상태입니다.\n\n다만 공식 코드가 아니라 수식을 재구성한 것이고, 노이즈 강도가 FOCUS에 불리한 설정이며, 사진 2장 조건에서만 재구성이 가능했습니다. 공식 코드 재현은 다음 2주 안에 하겠습니다.");

slide("원인 규명", "왜 하필 '읽기' 경로인가", "wk_f_mechanism_why.png", 820/1400,
"기존 통념은 여러 이미지가 서로 섞여서 환각이 생긴다는 것입니다. 그래서 MIMIC은 섞임을 막고, CAPL과 SoFA는 오히려 더 엽니다.\n\n그런데 저희가 섞임을 끊어보니 0.697에서 0.403으로 오히려 무너졌습니다. 섞임은 오염원이 아니라 버팀목이었습니다. 배치와 모델과 질문 유형을 바꿔 10개 설정에서 재봤는데 이미지끼리 차단이 이득인 설정이 하나도 없었습니다. 그래서 저희 처방은 휴리스틱이 아니라 원인 규명에서 나온 것입니다.");

slide("핵심 주장", "기여는 '어느 사진을 고르는가'가 아니라 '무엇을 자르는가'", "wk_d_selector.png", 660/1400,
"판별을 CLIP이 대신 해줘도 읽기 경로만 차단하는 쪽이 사진을 통째로 지우는 것보다 유의하게 낫습니다. 두 모델 모두 그렇습니다.\n\n사진을 지우면 나머지 사진들이 서로 참고하던 맥락까지 함께 사라지는데, 읽기 경로만 끊으면 그 맥락은 남고 방해가 되는 통로만 막힙니다. 그래서 연구 범위를 좁혔습니다. selector 경쟁이 아니라, 찾은 다음 attention의 어디를 자르느냐에 대한 연구입니다.");

slide("차별성", null, "fig5_novelty.png", 900/1600,
"기존 연구를 개입 지점으로 정리하면 네 줄이 나옵니다. 입력 픽셀을 바꾸거나, 연결을 통째로 바꾸거나, 출력을 보정하거나입니다.\n\n맨 아래 줄, 연결 중 한 칸만 바꾸는 자리는 비어 있습니다. 여러 사진 중 특정 한 장으로 가는 읽기 경로만 끊은 연구는 문헌에 없습니다. 참고로 training-free나 층 단위 개입 같은 것은 이미 선행연구가 있어서 novelty로 쓰지 않습니다.");

slide("수치의 신뢰도", "이 수치들을 어디까지 믿을 수 있나", "wk_g_trust.png", 830/1400,
"벤치마크가 자체 제작이라는 점 때문에 증거를 둘로 나눠서 봐야 합니다.\n\n기전 발견은 같은 문항 같은 모델 같은 가중치에서 attention 마스크의 사각형 하나만 바꾼 인과 개입이라 벤치마크 품질에 흔들리지 않습니다. 10개 설정에서 재현했고, 마스킹이 실제로 이미지를 지운 것과 98.3% 같은 답을 낸다는 것도 확인했습니다. 다만 이 태스크에서라는 조건은 붙습니다.\n\n반면 성능 수치는 저희 문항의 난이도가 그대로 반영되므로 외부 검증이 필요합니다. 그게 다음 2주 계획이고, FOCUS가 저희와 같은 모델로 공개 벤치를 평가했기 때문에 한 번에 끝낼 수 있습니다.");

// 10 다음 계획
{ const s=pres.addSlide(); s.background={color:C.darkbg};
  s.addText("다음 계획",{x:0.55,y:0.34,w:12.25,h:0.5,fontFace:F,fontSize:25,bold:true,color:C.white,margin:0});
  s.addText("경쟁 방법과 같은 벤치 · 같은 모델에서 직접 붙는 것이 최우선",{x:0.55,y:0.86,w:12.25,h:0.28,fontFace:F,fontSize:13,color:"9FB8CE",margin:0});
  const plan=[["1–2주","MuirBench · Mantis-Eval  +  FOCUS 공식 코드","FF9E80"],
              ["3주","관련도를 이산이 아니라 연속으로 — 개입 강도 라우팅","FFC94D"],
              ["4–5주","다른 모델군  (InternVL3 · LLaVA-OneVision)","7EC8F5"],
              ["6–8주","생성 평가  ·  인코더 재사용 후 실측 속도","7EC8F5"],
              ["9–11주","초고 → 리뷰 → 초록 11/06 → 제출 11/13","8CE0B0"]];
  plan.forEach((p,i)=>{const y=1.62+i*0.94;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.55,y,w:12.25,h:0.78,rectRadius:0.08,fill:{color:"1D3850"},line:{color:"2E4E6B",width:1}});
    s.addText(p[0],{x:0.9,y,w:1.5,h:0.78,fontFace:F,fontSize:16,bold:true,color:p[2],valign:"middle",margin:0});
    s.addText(p[1],{x:2.6,y,w:9.9,h:0.78,fontFace:F,fontSize:16,color:C.white,valign:"middle",margin:0});});
  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.55,y:6.44,w:12.25,h:0.66,rectRadius:0.08,fill:{color:"3A2430"},line:{color:"6B3A4A",width:1.2}});
  s.addText("중단 조건 — 같은 벤치·같은 모델에서 FOCUS를 넘지 못하면, 방법 논문이 아니라 기전 분석 논문으로 방향을 바꿉니다",{x:0.9,y:6.44,w:11.6,h:0.66,fontFace:F,fontSize:13,bold:true,color:"FFB4A2",valign:"middle",margin:0});
  s.addNotes("가장 중요한 다음 단계는 경쟁 방법과 같은 벤치, 같은 모델에서 직접 붙는 것입니다. FOCUS가 저희와 같은 Qwen2.5-VL 3B와 7B로 MuirBench, Mantis-Eval, MIRB를 평가했고 코드도 공개돼 있습니다. 같은 벤치에 저희 방법을 올리면 공개 벤치 검증과 FOCUS 정식 비교가 한 번에 끝납니다.\n\n3주차는 오늘 말씀드린 한계에서 바로 나온 것으로, 관련도를 있다 없다로 나누지 않고 연속적으로 다루는 것입니다. 그리고 지금 모든 성능 수치가 저희가 만든 벤치와 예 아니오 단답에 한정되어 있다는 점이 가장 큰 위험이라, 공개 벤치에서 밀리면 방향을 바꾸겠습니다.");
}
pres.writeFile({fileName:"/Users/hansangmin/Source-Depth/meeting/_generated/deck_v12.pptx"}).then(()=>console.log("DECK v12 WRITTEN"));
