// SourceDepth v7 — 최종 7장. attention 행렬 그림을 네이티브 도형으로 내장.
// 감사 반영: 7B READ>T0 비유의 명시 / 대비 0.974는 '예비' / 부분관련 실패 제외 / '보호막'은 해석 표기
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const C = { navy:"1F3B57", darkbg:"142638", blue:"1F77B4", red:"D62728", dred:"8B1A1A",
  green:"2E8B57", orange:"E8890C", gray:"6B7280", white:"FFFFFF", light:"EFF4F9",
  lightred:"FBEAEA", lightgray:"F3F4F6", lightgreen:"E9F4EE", lightblue:"E8F1FA",
  line:"D5DEE8", ghost:"FBFBFB", ghostline:"EDEEF0", faint:"B9BFC7" };
const F = "Arial";
const kick = (s,t,d) => s.addText(t,{x:0.55,y:0.24,w:11.5,h:0.3,fontFace:F,fontSize:11,bold:true,color:d?"9FB8CE":C.blue,margin:0});
const head = (s,t,d) => s.addText(t,{x:0.55,y:0.52,w:12.2,h:0.7,fontFace:F,fontSize:22,bold:true,color:d?C.white:C.navy,margin:0});
const take = (s,t,col) => { s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.55,y:6.62,w:12.25,h:0.6,rectRadius:0.08,fill:{color:col||C.navy}});
  s.addText(t,{x:0.85,y:6.62,w:11.75,h:0.6,fontFace:F,fontSize:12.5,bold:true,color:C.white,margin:0,valign:"middle"}); };
const box = (s,x,y,w,h,fill,line,lw) => s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.05,fill:{color:fill},line:{color:line,width:lw||1}});
const txt = (s,t,x,y,w,h,o) => s.addText(t,Object.assign({x,y,w,h,fontFace:F,margin:0},o));

// ═══ 1. 표지 ═══
{
  const s = pres.addSlide(); s.background = { color: C.darkbg };
  txt(s,"SOURCEDEPTH · 연구 방향 보고 · 한상민",0.6,0.55,12.2,0.3,{fontSize:11.5,bold:true,color:"7EC8F5"});
  txt(s,"여러 장의 사진을 주면 모델은\n엉뚱한 사진을 보고 답합니다",0.6,1.1,12.2,1.4,{fontSize:30,bold:true,color:C.white,lineSpacingMultiple:1.15});
  txt(s,"이 현상이 실제로 있는지 · 왜 생기는지 · 어떻게 고치는지 — 세 가지를 측정으로 보고드립니다",0.6,2.68,12.2,0.35,{fontSize:13.5,color:"AFC6DA"});
  const cards = [
    ["확인한 것","무관한 사진 3장이면 작은 모델의\n판별력이 0.91 → 0.52\n(동전 던지기 수준)","사전 등록 · 2개 모델 · 문항 300","8CE0B0"],
    ["알아낸 것","범인은 '사진끼리 섞임'이 아니라\n'질문이 무관한 사진을 읽는 것'.\n섞임을 끊으면 오히려 0.40으로 붕괴","우리 가설을 우리 실험으로 반증","7EC8F5"],
    ["만든 것","사진은 두고 읽기만 끊으면 0.91 복구.\n두 경로 상태를 빼면 0.97 (예비)","지우는 것보다 낫다는 것까지 측정","FFC94D"],
  ];
  cards.forEach((c,i)=>{ const x=0.6+i*4.15,y=3.35;
    box(s,x,y,3.95,3.1,"1D3850","2E4E6B",1);
    txt(s,c[0],x+0.25,y+0.2,3.45,0.34,{fontSize:15,bold:true,color:c[3]});
    txt(s,c[1],x+0.25,y+0.66,3.45,1.7,{fontSize:12,color:C.white,lineSpacingMultiple:1.28});
    txt(s,c[2],x+0.25,y+2.55,3.45,0.4,{fontSize:10.5,color:"9FB8CE"});
  });
  s.addNotes("결론부터 세 가지입니다. 문제가 실재하고, 원인이 예상과 반대였고, 그 원인에 정확히 개입하는 방법을 만들었습니다.");
}

// ═══ 2. 문제 ═══
{
  const s = pres.addSlide();
  kick(s,"문제 — 실재 확인");
  head(s,"사진을 한 장 더 넣었을 뿐인데 답이 바뀝니다");
  const ex = [
    ["사진 1장만 줬을 때",["개 없는 거실 사진"],"\"이 사진에 개가 있나요?\"","\"아니오\"  (정답)",C.green,C.lightgreen],
    ["무관한 사진을 한 장 추가",["개 없는 거실 사진","+ 개 있는 공원 사진 (질문과 무관)"],"\"첫 번째 사진에 개가 있나요?\"","\"있습니다\"  (오답)",C.red,C.lightred],
  ];
  ex.forEach((c,i)=>{ const x=0.55+i*6.23,w=6.02;
    box(s,x,1.4,w,2.6,c[5],c[4],1.25);
    txt(s,c[0],x+0.25,1.54,w-0.5,0.3,{fontSize:13,bold:true,color:c[4]});
    c[1].forEach((im,j)=>{ box(s,x+0.25,1.92+j*0.5,w-0.5,0.42,C.white,C.line,0.75);
      txt(s,im,x+0.4,1.92+j*0.5,w-0.8,0.42,{fontSize:11,color:C.navy,valign:"middle"}); });
    txt(s,c[2],x+0.25,2.98,w-0.5,0.3,{fontSize:11.5,italic:true,color:C.gray});
    txt(s,"모델:  "+c[3],x+0.25,3.36,w-0.5,0.4,{fontSize:14,bold:true,color:c[4]});
  });
  txt(s,"무관한 사진을 늘려가며 재본 결과 (판별력 점수 · 3B · 문항 300)",0.55,4.22,9,0.3,{fontSize:12.5,bold:true,color:C.navy});
  const bars=[["사진 1장만",0.9078,C.green],["+ 무관 1장",0.6978,C.orange],["+ 무관 2장",0.6063,C.orange],["+ 무관 3장",0.5213,C.red]];
  bars.forEach((b,i)=>{ const y=4.58+i*0.45, full=8.6, w=Math.max(0.05,(b[1]-0.5)/0.5)*full;
    txt(s,b[0],0.55,y,1.7,0.36,{fontSize:11,bold:true,color:C.navy,valign:"middle"});
    s.addShape(pres.shapes.RECTANGLE,{x:2.35,y:y+0.06,w:full,h:0.24,fill:{color:"EDF1F5"}});
    s.addShape(pres.shapes.RECTANGLE,{x:2.35,y:y+0.06,w,h:0.24,fill:{color:b[2]}});
    txt(s,b[1].toFixed(2),2.35+full+0.15,y,1.1,0.36,{fontSize:11.5,bold:true,color:b[2],valign:"middle"});
  });
  txt(s,"막대 시작점 = 0.5 (찍기)  ·  판별력 점수: 맞다/아니다를 가려내는 능력. \"예\"를 자주 답해 오르는 착시가 없는 지표",2.35,6.35,10,0.3,{fontSize:10,italic:true,color:C.gray});
  take(s,"→ 3장이면 사실상 찍기가 됩니다. 문서 여러 장·영상 프레임·검색 이미지 등 실제 입력은 대부분 이런 상황입니다");
  s.addNotes("왼쪽이 정상, 오른쪽이 문제 상황입니다. 무관한 사진 속 개가 첫 번째 사진으로 옮겨붙습니다. 아래 막대처럼 무관한 사진이 늘수록 판별력이 떨어져 3장이면 찍기 수준입니다.");
}

// ═══ 3. attention 행렬 (그림1 네이티브) ═══
{
  const s = pres.addSlide();
  kick(s,"원인 — 모델 내부에서 실제로 일어나는 일");
  head(s,"누가 무엇을 읽을 수 있는가 — 길은 두 개뿐입니다");
  txt(s,"행 = 읽는 쪽 · 열 = 읽히는 쪽 · 순서상 앞에 있는 것만 읽을 수 있음(causal). 사진·질문 블록 단위로 그리면:",0.55,1.24,12.2,0.28,{fontSize:11,color:C.gray});
  const cx=[3.05,4.82,6.59], cw=1.67, ry=[2.06,3.18,4.30], rh=1.0;
  // 입력 순서 스트립
  const strip=[["1번 사진 · 거실","개 없음 (질문 대상)",C.lightblue,C.blue],["2번 사진 · 공원","개 있음 (무관)",C.lightgray,C.gray],["질문","\"1번 사진에 개가 있나?\"",C.light,C.navy]];
  txt(s,"입력 순서 →",3.05,1.52,1.6,0.22,{fontSize:10,bold:true,color:C.gray});
  strip.forEach((b,i)=>{ box(s,cx[i],1.72,cw,0.3,b[2],b[3],1);
    txt(s,b[0]+"  ·  "+b[1],cx[i]+0.05,1.72,cw-0.1,0.3,{fontSize:8.5,bold:true,color:C.navy,align:"center",valign:"middle"}); });
  // 행 라벨
  const rl=[["1번 사진이 읽을 때",C.navy],["2번 사진이 읽을 때",C.navy],["질문이 읽을 때  (답이 만들어짐)",C.red]];
  rl.forEach((r,i)=>txt(s,r[0],0.55,ry[i]+rh/2-0.18,2.42,0.36,{fontSize:11.5,bold:true,color:r[1],align:"right"}));
  // 셀
  const cell=(ci,ri,fill,line,lw,t1,c1,t2)=>{ box(s,cx[ci],ry[ri],cw,rh,fill,line,lw);
    if(t1) txt(s,t1,cx[ci],ry[ri]+(t2?0.2:0.36),cw,0.3,{fontSize:11.5,bold:true,color:c1,align:"center"});
    if(t2) txt(s,t2,cx[ci],ry[ri]+0.52,cw,0.3,{fontSize:9.5,color:C.navy,align:"center"}); };
  cell(0,0,C.lightgray,C.line,0.75,"자기 자신",C.gray);
  cell(1,0,C.ghost,C.ghostline,0.75,"✕ 읽을 수 없음",C.faint,"(2번은 뒤에 있음)");
  cell(2,0,C.ghost,C.ghostline,0.75,"✕",C.faint);
  cell(0,1,C.lightblue,C.blue,2,"경로 A",C.blue,"2번이 1번을 읽음 (섞임)");
  cell(1,1,C.lightgray,C.line,0.75,"자기 자신",C.gray);
  cell(2,1,C.ghost,C.ghostline,0.75,"✕",C.faint);
  cell(0,2,C.lightgreen,C.green,1.25,"질문이 1번을 읽음",C.green,"정상 — 꼭 필요");
  cell(1,2,C.lightred,C.red,2.5,"경로 B",C.red,"질문이 2번(무관)을 읽음");
  cell(2,2,C.lightgray,C.line,0.75,"자기 자신",C.gray);
  txt(s,"← 사고 지점",cx[1],ry[2]+1.02,cw,0.24,{fontSize:10.5,bold:true,color:C.red,align:"center"});
  // 우측 주석
  box(s,8.62,ry[1],4.16,rh,C.lightblue,C.blue,1.25);
  txt(s,"경로 A는 '배달로'가 아닙니다",8.82,ry[1]+0.1,3.8,0.26,{fontSize:11.5,bold:true,color:C.blue});
  txt(s,"1번은 2번을 못 보므로(✕) 2번의 내용이 답으로 가는 길은 경로 B뿐. A는 2번이 맥락을 얻는 통로.",8.82,ry[1]+0.38,3.8,0.56,{fontSize:9.5,color:C.navy,lineSpacingMultiple:1.15});
  box(s,8.62,ry[2],4.16,rh,C.lightred,C.red,1.25);
  txt(s,"무슨 일이 벌어지나",8.82,ry[2]+0.1,3.8,0.26,{fontSize:11.5,bold:true,color:C.red});
  txt(s,"답은 이 행에서 만들어지는데, 빨간 칸으로 2번의 '개'가 흘러들어와 \"있다\"(오답).",8.82,ry[2]+0.38,3.8,0.56,{fontSize:9.5,color:C.navy,lineSpacingMultiple:1.15});
  txt(s,"실제로는 사진 한 장 = 토큰 수백 개 → 각 칸은 사각형 블록.  '지우기' = 블록에 −∞를 더해 attention 0으로 (실제 토큰 삭제와 예측 100% 일치 검증)",0.55,5.5,12.25,0.3,{fontSize:10,italic:true,color:C.gray});
  box(s,0.55,5.88,12.25,0.6,C.light,C.line,1);
  txt(s,"실험 = 칸을 하나씩 지우고 비교.  사진·질문·모델이 전부 같고 지운 칸 하나만 다르므로, 결과 차이는 그 칸 때문입니다 (인과 개입)",0.85,5.88,11.7,0.6,{fontSize:12,bold:true,color:C.navy,valign:"middle"});
  take(s,"→ 무관한 사진의 내용이 답에 닿는 길은 이 행렬의 칸입니다. 다음 장: 칸을 하나씩 지워본 결과");
  s.addNotes("모델 내부를 행렬로 그리면 이렇습니다. 무관한 2번 사진과 관련된 칸이 두 개 있습니다. 경로 A는 사진끼리 섞이는 칸, 경로 B는 질문이 무관한 사진을 읽는 칸입니다. 중요한 점은 1번이 2번을 못 보기 때문에, 2번의 내용이 답으로 배달되는 길은 경로 B 하나라는 것입니다. 사고는 마지막 행에서 납니다.");
}

// ═══ 4. 결과 (그림2 네이티브) ═══
{
  const s = pres.addSlide();
  kick(s,"실험 결과");
  head(s,"범인은 '읽기'였습니다 — 섞임을 끊으면 오히려 무너집니다");
  const minis=[["① 아무것도 안 지움",null,"0.70",C.gray,"무관한 사진이 답을 흔든다"],
               ["② 경로 A(섞임)를 지움","A","0.40 ▼",C.red,"훨씬 나빠짐 — 섞임은 지지대였다*"],
               ["③ 경로 B(읽기)를 지움","B","0.91 ▲",C.green,"1장만 준 수준(0.91)으로 회복"]];
  minis.forEach((mn,k)=>{ const X=0.75+k*4.3, cs=0.62, gp=0.05;
    txt(s,mn[0],X,1.4,3.6,0.3,{fontSize:13.5,bold:true,color:mn[3],align:"center"});
    const gx=[X+0.7,X+0.7+cs+gp,X+0.7+2*(cs+gp)], gy=[1.78,1.78+cs+gp,1.78+2*(cs+gp)];
    ["1을","2를","Q를"].forEach((t,i)=>txt(s,t,gx[i],1.56,cs,0.2,{fontSize:8.5,color:C.gray,align:"center"}));
    ["1이","2가","Q가"].forEach((t,i)=>txt(s,t,X+0.2,gy[i]+cs/2-0.1,0.45,0.2,{fontSize:8.5,color:C.gray,align:"right"}));
    const paint=(ci,ri,f,l,lw,mark,mc)=>{ s.addShape(pres.shapes.RECTANGLE,{x:gx[ci],y:gy[ri],w:cs,h:cs,fill:{color:f},line:{color:l,width:lw}});
      if(mark) txt(s,mark,gx[ci],gy[ri]+cs/2-0.16,cs,0.32,{fontSize:mark==="✕"?15:10,bold:true,color:mc,align:"center"}); };
    paint(0,0,C.lightgray,C.line,0.5); paint(1,0,C.ghost,C.ghostline,0.5); paint(2,0,C.ghost,C.ghostline,0.5);
    if(mn[1]==="A") paint(0,1,C.dred,C.dred,0.5,"✕",C.white); else paint(0,1,C.lightblue,C.blue,1.25,"A",C.blue);
    paint(1,1,C.lightgray,C.line,0.5); paint(2,1,C.ghost,C.ghostline,0.5);
    paint(0,2,C.lightgray,C.line,0.5);
    if(mn[1]==="B") paint(1,2,C.dred,C.dred,0.5,"✕",C.white); else paint(1,2,C.lightred,C.red,1.25,"B",C.red);
    paint(2,2,C.lightgray,C.line,0.5);
    txt(s,mn[2],X,3.95,3.6,0.55,{fontSize:26,bold:true,color:mn[3],align:"center"});
    txt(s,mn[4],X,4.52,3.6,0.3,{fontSize:11,bold:true,color:mn[3],align:"center"});
  });
  txt(s,"판별력 점수 · 3B · 문항 300 · 7B도 같은 방향(0.87 / 0.45 / 0.90)   *'지지대'는 해석 — 측정 사실은 \"섞임 차단이 이득인 설정이 8개 중 0개\"",0.55,4.95,12.25,0.3,{fontSize:10,italic:true,color:C.gray});
  box(s,0.55,5.32,12.25,1.14,C.light,C.line,1);
  txt(s,"\"그냥 2번 사진을 통째로 지우면 되지 않나?\"",0.8,5.44,11.7,0.28,{fontSize:12.5,bold:true,color:C.navy});
  txt(s,"2번 '열' 전체를 지우는 것 = 이 배치에선 ③과 완전히 동일 (배달로가 경로 B뿐이라서 — 600문항 전부 소수점까지 일치).\n무관 사진이 앞에 오는 배치에선 통째 삭제 0.889 < 칸만 삭제 0.908 (3B 유의 · 7B는 같은 방향, 유의하지 않음) — 통째로 지우면 경로 A(맥락)까지 죽이기 때문.",0.8,5.76,11.7,0.66,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.2});
  take(s,"→ 해악은 「질문 → 무관 사진」 칸 하나. 우리 방법 = 사진은 두고 그 칸만 지운다","2E8B57");
  s.addNotes("칸을 하나씩 지워봤습니다. 섞임을 지우면 0.40으로 무너지고, 읽기를 지우면 0.91로 회복됩니다. 저희 처음 가설이 반증된 지점이 가운데입니다. 아래 박스가 중요합니다. 통째로 지우는 것과의 차이는 무관 사진이 앞에 올 때 드러나는데, 3B에서 유의하게 칸만 지우는 쪽이 낫습니다. 7B는 같은 방향이지만 유의하지는 않습니다.");
}

// ═══ 5. 방법 완성 ═══
{
  const s = pres.addSlide();
  kick(s,"방법 완성 — 남은 두 조각");
  head(s,"어느 사진이 무관한지 아는 법, 그리고 두 상태를 빼서 더 올리는 법");
  // 좌: 판별
  box(s,0.55,1.4,6.05,2.9,C.light,C.line,1);
  txt(s,"조각 1 — 무관한 사진 판별: '하나씩 빼보기'",0.8,1.54,5.6,0.3,{fontSize:13,bold:true,color:C.navy});
  txt(s,"사진을 하나씩 빼고 다시 돌려서, 답이 가장 크게 흔들리는 사진 = 진짜 필요한 사진. 위치를 안 보므로 위치 편향이 원천 불가능.",0.8,1.88,5.6,0.55,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.2});
  const th={bold:true,color:C.white,fill:{color:C.navy},fontSize:10.5};
  const tc={fontSize:10.5,color:C.navy,fill:{color:C.white}};
  const mm=(t,o)=>({text:t,options:Object.assign({},tc,o||{})});
  s.addTable([
    [mm("사진 수",th),mm("의미 유사도 (CLIP)",th),mm("하나씩 빼보기 (우리)",th),mm("찍으면",th)],
    [mm("2장",{bold:true}),mm("51%",{color:C.red}),mm("69%",{bold:true,color:C.green}),mm("50%",{color:C.gray})],
    [mm("3장",{bold:true}),mm("39%",{color:C.red}),mm("71%",{bold:true,color:C.green}),mm("33%",{color:C.gray})],
    [mm("4장",{bold:true}),mm("33%",{color:C.red}),mm("73%",{bold:true,color:C.green}),mm("25%",{color:C.gray})],
  ],{x:0.8,y:2.52,w:5.55,rowH:[0.32,0.3,0.3,0.3],fontFace:F,align:"center",valign:"middle",border:{pt:0.75,color:"E2E8F0"}});
  txt(s,"CLIP은 무관한 사진에 질문 속 물건이 있으면 오히려 그쪽을 고름 — 관련도는 '의미'가 아니라 '이 모델의 답을 바꾸는가'",0.8,3.86,5.6,0.42,{fontSize:9.5,italic:true,color:C.gray,lineSpacingMultiple:1.15});
  // 우: 대비
  box(s,6.78,1.4,6.02,2.9,C.lightblue,C.blue,1.25);
  txt(s,"조각 2 — 두 경로 상태를 빼기  (예비 결과)",7.03,1.54,5.5,0.3,{fontSize:13,bold:true,color:C.blue});
  txt(s,"같은 사진으로 두 상태를 만든다:",7.03,1.9,5.5,0.26,{fontSize:11,color:C.navy});
  txt(s,"깨끗한 상태 = 경로 B만 지움  →  0.91\n오염된 상태 = 경로 A만 지움  →  0.40",7.28,2.18,5.2,0.55,{fontSize:11.5,bold:true,color:C.navy,lineSpacingMultiple:1.3});
  txt(s,"둘을 빼면 '오염의 크기' 자체가 단서가 되어",7.03,2.82,5.5,0.26,{fontSize:11,color:C.navy});
  txt(s,"0.97",7.03,3.1,2.2,0.6,{fontSize:34,bold:true,color:C.blue});
  txt(s,"사진 1장만 준 0.91보다 높음\n2모델 × 2배치 = 4조건 전부 유의",9.0,3.16,3.6,0.55,{fontSize:10.5,bold:true,color:C.blue,lineSpacingMultiple:1.2});
  txt(s,"※ 기존 방법(VCD·FOCUS)은 사진에 노이즈를 씌워 '오염 상태'를 만듦 — 우리는 같은 사진에서 내부 경로만 바꿈. 입력을 건드리는 방식으론 이 두 상태를 만들 수 없음",7.03,3.8,5.5,0.5,{fontSize:9.5,italic:true,color:C.gray,lineSpacingMultiple:1.15});
  // 하단 정직 박스
  box(s,0.55,4.5,12.25,1.44,C.lightred,C.red,1.25);
  txt(s,"정직하게 붙이는 조건",0.8,4.62,11.7,0.28,{fontSize:12.5,bold:true,color:C.red});
  txt(s,"· 0.97은 기존 로그를 재조합한 사후 분석 — 같은 300문항을 공유하므로 독립 재현 아님. 새 문항 재현이 사전 등록되어 있음 (β=1.0 고정, GPU 2시간)\n· 두 상태 모두 '어느 사진이 무관한지 아는' 조건에서의 값. 판별기까지 포함한 종단 성능은 별도 측정 필요\n· 판별에 사진 수만큼 forward 필요 — 정확도를 얻는 대신 비용을 씀 (속도 이득은 아직 미증명)",0.8,4.94,11.7,0.94,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.25});
  take(s,"→ 파이프라인: 하나씩 빼보기로 무관 사진 특정 → 그 사진의 '읽기 칸'만 지움 → (선택) 두 상태 대비로 증폭");
  s.addNotes("방법의 나머지 두 조각입니다. 첫째, 어느 사진이 무관한지는 하나씩 빼보고 답이 흔들리는 정도로 판정합니다. CLIP 같은 의미 유사도는 찍기 수준입니다. 둘째, 두 경로 상태를 빼면 0.97까지 오르는데, 이건 사후 분석이라 예비 결과로 말씀드립니다. 재현 실험은 사전 등록해 뒀습니다.");
}

// ═══ 6. 기존 연구와의 관계 ═══
{
  const s = pres.addSlide();
  kick(s,"왜 가치가 있는가");
  head(s,"기존 연구는 정반대 처방을 냈고 — 우리 분해가 둘 다 설명합니다");
  const camp=[["\"연결을 늘려라\"",["CAPL (2026)","SoFA (CVPR 2025)"],"사진 간 정보가 부족하다고 진단",C.blue,C.lightblue],
              ["\"연결을 끊어라\"",["MIMIC (2026)","FOCUS (2025)"],"사진 간 정보가 오염시킨다고 진단",C.red,C.lightred]];
  camp.forEach((c,i)=>{ const x=0.55+i*3.28,w=3.12;
    box(s,x,1.42,w,1.8,c[4],c[3],1.25);
    txt(s,c[0],x+0.15,1.54,w-0.3,0.3,{fontSize:13,bold:true,color:c[3],align:"center"});
    c[1].forEach((p,j)=>txt(s,"· "+p,x+0.25,1.9+j*0.27,w-0.5,0.25,{fontSize:10.5,color:C.navy}));
    txt(s,c[2],x+0.25,2.52,w-0.5,0.6,{fontSize:10,color:C.gray,lineSpacingMultiple:1.2});
  });
  box(s,7.25,1.42,5.55,1.8,C.lightgreen,C.green,1.5);
  txt(s,"우리 답 — 둘 다 맞았습니다",7.48,1.54,5.1,0.3,{fontSize:13,bold:true,color:C.green});
  txt(s,"서로 다른 칸을 건드리고 있었습니다.\n· 경로 A(섞임) → 도움  ⇒ '늘려라'가 맞음\n· 경로 B(읽기) → 해악  ⇒ '끊어라'가 맞음\n칸을 나눠 재기 전에는 구분할 수 없었습니다.",7.48,1.88,5.1,1.25,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.25});
  txt(s,"둘 다 성능이 올랐다고 보고 — 아무도 이유를 설명 못 함",0.55,3.28,6.6,0.28,{fontSize:10.5,italic:true,color:C.gray});
  // 좌우: 못쓰는 주장 / 빈 자리
  box(s,0.55,3.72,6.05,2.2,C.lightred,C.red,1);
  txt(s,"우리가 쓸 수 없는 주장 (선행연구 조사로 확인)",0.8,3.84,5.6,0.28,{fontSize:12,bold:true,color:C.red});
  txt(s,"· \"학습 없이 추론 때 개입\" — 이미 3편이 함\n· \"층 단위 개입\" — 4편 모두 이미 함\n· \"개입으로 원인 검증\" — 1편이 이미 함\n\n→ 이 셋은 novelty로 쓰지 않습니다",0.8,4.16,5.6,1.6,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.3});
  box(s,6.78,3.72,6.02,2.2,C.lightgreen,C.green,1);
  txt(s,"아직 비어 있는 자리 (우리 기여)",7.03,3.84,5.5,0.28,{fontSize:12,bold:true,color:C.green});
  txt(s,"· 사진↔사진 칸만 따로 끊어 원인을 가른 연구 — 0편\n  (기존 개입은 전부 모달리티 사이 연결만)\n· 여러 사진 중 특정 한 장만 골라 끊은 연구 — 0편\n· '무관한 사진이 섞인 상황' 자체를 늘려라 진영은\n  실험한 적이 없음",7.03,4.16,5.5,1.6,{fontSize:10.5,color:C.navy,lineSpacingMultiple:1.3});
  take(s,"→ 새 방법 하나를 더하는 게 아니라, 분야가 갈려 있던 지점을 측정으로 정리하는 결과입니다");
  s.addNotes("기존 연구는 늘려라와 끊어라로 갈려 있고 양쪽 다 개선을 보고합니다. 저희 분해로 보면 서로 다른 칸을 건드린 것이라 둘 다 맞습니다. 조사 과정에서 저희가 처음에 novelty로 생각한 세 가지는 선점돼 있다는 것도 확인했고, 그대로 적었습니다. 비어 있는 자리는 오른쪽 세 가지입니다.");
}

// ═══ 7. 한계와 계획 ═══
{
  const s = pres.addSlide(); s.background={color:C.darkbg};
  kick(s,"한계와 계획",true);
  head(s,"이 연구를 무너뜨릴 수 있는 것 세 가지 — 4주 안에 각각 확인합니다",true);
  const risk=[["지금 벤치마크는 질문이 위치(\"1번 사진\")를 알려줌","텍스트만 파싱하는 앞단 모듈도 100%가 됨 — 내부 개입의 필요성을 이 벤치로는 증명 불가"],
              ["0.97(대비)은 사후 분석","같은 문항 재조합 + β 사후 선택. 새 문항 재현(사전 등록 완료)이 통과해야 확정"],
              ["속도 이득 미증명","이미지 인코딩이 비용의 66%라 재사용 여지는 크지만, 그 구현은 아직 없음. \"더 싸다\"는 아직 주장 안 함"]];
  risk.forEach((r,i)=>{ const y=1.4+i*0.86;
    box(s,0.55,y,12.25,0.76,"3A2430","6B3A4A",1);
    txt(s,String(i+1),0.82,y+0.18,0.35,0.4,{fontSize:13,bold:true,color:"FF9E80",align:"center"});
    txt(s,r[0],1.3,y+0.08,11.2,0.3,{fontSize:12.5,bold:true,color:C.white});
    txt(s,r[1],1.3,y+0.4,11.2,0.3,{fontSize:10.5,color:"D0BCC4"});
  });
  const plan=[["1주","위치를 알려주지 않는 질문으로 벤치마크 교체","앞단 모듈이 원리적으로 못 푸는가"],
              ["2주","공개 벤치마크(BLINK·MUIRBench)에서 재현","여기서 안 되면 접습니다"],
              ["3주","대비 재현(β=1.0 고정) + FOCUS와 같은 비용에서 직접 비교","예비 결과가 확정되는가"],
              ["4주","모델 3계열 확장 · 논문 초안","—"]];
  plan.forEach((p,i)=>{ const y=4.14+i*0.5;
    txt(s,p[0],0.75,y,0.8,0.42,{fontSize:12,bold:true,color:"7EC8F5",valign:"middle"});
    txt(s,p[1],1.75,y,6.5,0.42,{fontSize:11.5,color:C.white,valign:"middle"});
    txt(s,"→ "+p[2],8.45,y,4.3,0.42,{fontSize:10.5,color:"8CE0B0",valign:"middle"});
  });
  box(s,0.55,6.32,12.25,0.86,"1D3850","2E4E6B",1);
  txt(s,[{text:"중단 조건: 2주차 공개 벤치마크 재현이 실패하면 이 방향은 접습니다.",options:{bold:true,fontSize:12,color:"FFC94D",breakLine:true}},
         {text:"지금까지 판정 기준을 먼저 문서로 고정하고 실행한 실험 7건 — 그중 5건이 기준 미달 또는 예측 반대였고 전부 그대로 기록했습니다. GPU 1장, 기존 코드·데이터 재사용.",options:{fontSize:10.5,color:"9FB8CE"}}],
      0.85,6.4,11.7,0.72,{paraSpaceAfter:3});
  s.addNotes("마지막으로 불리한 것부터 말씀드립니다. 벤치마크가 위치를 알려주는 문제가 가장 크고 1주차에 바꿉니다. 2주차 공개 벤치마크에서 재현되지 않으면 접겠습니다. 지금까지 사전 등록 7건 중 5건이 기준 미달이거나 예측 반대였고 전부 기록했습니다.");
}

pres.writeFile({ fileName: "/Users/hansangmin/Source-Depth/meeting/_generated/deck_v7.pptx" })
  .then(() => console.log("DECK v7 WRITTEN"));
