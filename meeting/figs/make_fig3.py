#!/usr/bin/env python3
"""제안 방법 개요도 (Figure 1). 모든 수치는 results/ 실측값."""
from pathlib import Path

W, H = 1600, 900
NAVY="#1F3B57"; BLUE="#1F77B4"; RED="#D62728"; DRED="#8B1A1A"
GREEN="#2E8B57"; GRAY="#6B7280"; DARKBG="#142638"
LBLUE="#E8F1FA"; LRED="#FBEAEA"; LGREEN="#E9F4EE"; LGRAY="#F1F3F5"
CBLUE="#CBE0F5"; CGREEN="#CFE9DC"; CRED="#F6CFCF"
LINE="#D5DEE8"; GHOST="#FAFBFC"; GHOSTLINE="#EDF0F3"; FAINT="#C3C9D0"
FF="Helvetica Neue, Helvetica, Arial, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"
o=[]
def rect(x,y,w,h,fill,stroke=None,sw=1,rx=0):
    s=f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}/>')
def txt(t,x,y,size=12,fill=NAVY,anchor="start",bold=False,italic=False,rot=None):
    b=' font-weight="bold"' if bold else ''; i=' font-style="italic"' if italic else ''
    r=f' transform="rotate({rot} {x} {y})"' if rot is not None else ''
    o.append(f'<text x="{x}" y="{y}" font-family="{FF}" font-size="{size}" fill="{fill}"'
             f' text-anchor="{anchor}"{b}{i}{r}>{t}</text>')
def line(x1,y1,x2,y2,c=LINE,w=1,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{d}/>')
def arrow(x1,y1,x2,y2,c=GRAY,w=2.2):
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" marker-end="url(#ah)"/>')

ST={"ghost":(GHOST,GHOSTLINE,0.8,"✕",FAINT),"diag":(LGRAY,LINE,0.8,None,None),
    "kept":(CBLUE,BLUE,1.3,None,None),"need":(CGREEN,GREEN,1.3,None,None),
    "block":(DRED,DRED,1.0,"✕","#FFFFFF"),"open":(CRED,RED,1.3,None,None)}
def matrix(x,y,cell,grid,marksize=None):
    ms = marksize or cell*0.42
    for r in range(4):
        for c in range(4):
            f,s,sw,mk,mc = ST[grid[r][c]]
            rect(x+c*cell, y+r*cell, cell, cell, f, s, sw)
            if mk: txt(mk, x+c*cell+cell/2, y+r*cell+cell/2+ms*0.36, ms, mc, "middle", True)

G_MAIN=[["diag","ghost","ghost","ghost"],["kept","diag","ghost","ghost"],
        ["kept","kept","diag","ghost"],["need","block","block","diag"]]
G_DROP=[["diag","ghost","ghost","ghost"],["kept","block","ghost","ghost"],
        ["kept","block","block","ghost"],["need","block","block","diag"]]
G_POS =G_MAIN
G_NEG =[["diag","ghost","ghost","ghost"],["block","diag","ghost","ghost"],
        ["block","block","diag","ghost"],["need","open","open","diag"]]

o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">')
o.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
         f'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{GRAY}"/></marker>'
         '<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
         f'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker></defs>')
rect(0,0,W,H,"#FFFFFF")

# ── 헤더 ──
txt("제안 방법 — 무관한 사진을 지우지 않고, 질문이 그것을 읽는 경로만 끊습니다",40,50,25,NAVY,bold=True)
txt("입력·모델·가중치를 전혀 바꾸지 않고, attention 행렬 안의 사각형 하나에만 개입합니다",40,78,13.5,GRAY)
line(40,100,1560,100,LINE,1.2)

# ══════════ 1단계 ══════════
X1=40
txt("1",X1,140,19,BLUE,bold=True)
txt("무관한 사진 찾기 — 하나씩 빼보기",X1+20,140,16,NAVY,bold=True)
strip=[("사진 1","관련",LBLUE,BLUE),("사진 2","무관",LGRAY,GRAY),
       ("사진 3","무관",LGRAY,GRAY),("질문","",NAVY,NAVY)]
bw,bg=94,8
for i,(t,sub,f,s) in enumerate(strip):
    x=X1+11+i*(bw+bg)
    rect(x,166,bw,42,f,s,1.4,4)
    txt(t,x+bw/2,192,13,"#FFFFFF" if t=="질문" else NAVY,"middle",bold=True)
    if sub: txt(sub,x+bw/2,224,10.5,s,"middle")
txt("입력 순서 →",X1+11,158,10,GRAY)
txt("각 사진을 하나씩 빼고 다시 계산해, 답이 얼마나 흔들리는지 잽니다",X1+11,254,11.5,NAVY)
rows=[("사진 1을 빼면",0.92,BLUE,0,"★ 가장 큼"),
      ("사진 2를 빼면",0.16,"#B6BDC6",1,None),("사진 3를 빼면",0.09,"#B6BDC6",2,None)]
for k,(lab,frac,col,xo,note) in enumerate(rows):
    y=274+k*40
    tw,tg=17,3
    for i in range(4):
        xx=X1+11+i*(tw+tg)
        gone=(i==xo)
        rect(xx,y,tw,tw,"#F5F6F7" if gone else (LGRAY if i<3 else NAVY),
             GHOSTLINE if gone else LINE,0.8,2)
        if gone:
            line(xx+3,y+3,xx+tw-3,y+tw-3,RED,1.6); line(xx+tw-3,y+3,xx+3,y+tw-3,RED,1.6)
    txt("→",X1+96,y+13,12,GRAY)
    rect(X1+116,y+3,210,12,"#EDF1F5",None,0,2)
    rect(X1+116,y+3,round(210*frac),12,col,None,0,2)
    txt(lab,X1+116,y-2,10,GRAY)
    if note: txt(note,X1+334,y+13,10.5,BLUE,bold=True)
txt("답이 가장 크게 흔들리는 사진 = 모델이 실제로 쓰는 사진.",X1+11,412,11.5,NAVY,bold=True)
txt("나머지는 무관한 사진으로 판정합니다. 사진의 위치를 전혀 보지 않으므로",X1+11,430,11,GRAY)
txt("위치 편향이 원천적으로 불가능합니다.  비용: forward N+1회.",X1+11,447,11,GRAY)
rect(X1+11,468,415,104,"#FAFBFC",LINE,1,6)
txt("무관한 사진을 맞히는 정확도",X1+26,490,11.5,NAVY,bold=True)
cols=[("사진 2장",180),("3장",258),("4장",330)]
for t,cx in cols: txt(t,X1+cx,509,10,GRAY,"middle")
for k,(lab,vals,col,bold) in enumerate([
        ("이 방법 (하나씩 빼보기)",["0.69","0.71","0.73"],GREEN,True),
        ("의미 유사도 (CLIP)",["0.51","0.39","0.33"],RED,False),
        ("찍으면",["0.50","0.33","0.25"],GRAY,False)]):
    y=531+k*15
    txt(lab,X1+26,y,10.5,NAVY if bold else GRAY,bold=bold)
    for (t,cx),v in zip(cols,vals): txt(v,X1+cx,y,10.5,col,"middle",bold=bold)
arrow(474,360,504,360)

# ══════════ 2단계 ══════════
X2=512
txt("2",X2,140,19,RED,bold=True)
txt("칸 하나만 지우기 — 사진은 입력에 그대로 둡니다",X2+20,140,16,NAVY,bold=True)
CELL=58; MX,MY=X2+102,196
txt("읽히는 쪽  (key)",MX+CELL*2,166,10.5,GRAY,"middle")
txt("읽는 쪽  (query)",MX-72,MY+CELL*2,10.5,GRAY,"middle",rot=-90)
names=["사진1","사진2","사진3","질문"]
for i,n in enumerate(names):
    txt(n,MX+i*CELL+CELL/2,MY-8,11,NAVY,"middle",bold=True)
    txt(n,MX-10,MY+i*CELL+CELL/2+4,11,NAVY,"end",bold=True)
matrix(MX,MY,CELL,G_MAIN)
for (rr,cc,lb,lc) in [(1,0,"유지",BLUE),(2,0,"유지",BLUE),(2,1,"유지",BLUE),(3,0,"필요",GREEN)]:
    txt(lb,MX+cc*CELL+CELL/2,MY+rr*CELL+CELL/2+4,10,lc,"middle",bold=True)
rect(MX+CELL,MY+3*CELL,CELL*2,CELL,"none",RED,2.6)
txt("이 두 칸만 지웁니다",MX+CELL*2,MY+4*CELL+20,12,RED,"middle",bold=True)
leg=[(DRED,DRED,"차단 — 질문이 무관한 사진을 읽는 칸"),
     (CGREEN,GREEN,"필요 — 질문이 관련 사진을 읽는 칸"),
     (CBLUE,BLUE,"유지 — 사진끼리 보는 칸"),
     (GHOST,GHOSTLINE,"순서상 읽을 수 없음 (causal)")]
for k,(f,s,t) in enumerate(leg):
    x=X2+8+(k%2)*292; y=470+(k//2)*24
    rect(x,y-10,13,13,f,s,1); txt(t,x+20,y,10.5,NAVY)
txt("사진끼리 보는 칸은 끊으면 오히려 나빠집니다 (0.70 → 0.40). 그래서 유지합니다.",X2+8,516,10.5,BLUE,bold=True)
thumbs=[("사진을 통째로 뺀다",G_DROP,"0.889",GRAY,"흔한 방식"),
        ("읽는 칸만 지운다",G_MAIN,"0.908",GREEN,"이 방법")]
for k,(title,g,score,col,tag) in enumerate(thumbs):
    bx=X2+22+k*280
    rect(bx,530,258,146,"#FFFFFF",col if k else LINE,1.6 if k else 1,6)
    txt(title,bx+14,552,12,col,bold=True); txt(tag,bx+244,552,10,GRAY,"end")
    matrix(bx+16,562,24,g)
    txt(score,bx+140,614,27,col,bold=True)
    if k: txt("유의하게 더 높음",bx+140,634,10,GREEN)
    else: txt("맥락까지 함께 사라짐",bx+140,634,10,GRAY)
txt("무관한 사진은 입력에서 빠지지 않습니다. 그 사진의 열 전체가 아니라,",X2+8,700,11.5,NAVY,bold=True)
txt("(질문 행 × 무관한 사진 열) 사각형에만 −∞를 더해 attention을 0으로 만듭니다.",X2+8,718,11.5,NAVY,bold=True)
txt("0층부터 걸어야 합니다 — 8층부터 걸면 효과의 97%가 남지만, 16층부터면 68%로 떨어집니다.",X2+8,738,11,GRAY)
arrow(1098,360,1128,360)

# ══════════ 3단계 ══════════
X3=1136
txt("3",X3,140,19,BLUE,bold=True)
txt("두 경로 상태를 빼기",X3+20,140,16,NAVY,bold=True)
rect(X3+178,126,58,18,"#FFF4E0","#E8890C",1,4)
txt("예비 결과",X3+207,139,10,"#B06A00","middle",bold=True)
br=[("양의 갈래 — 가장 깨끗한 상태",G_POS,"0.906",GREEN,LGREEN,"질문이 무관한 사진을 못 읽음",168),
    ("음의 갈래 — 가장 오염된 상태",G_NEG,"0.403",RED,LRED,"사진끼리 못 봄 → 무관한 사진이 가장 도드라짐",352)]
for title,g,score,col,lf,sub,by in br:
    rect(X3,by,424,170,"#FFFFFF",col,1.8,7)
    txt(title,X3+16,by+24,12.5,col,bold=True)
    txt(sub,X3+16,by+42,10,GRAY)
    matrix(X3+18,by+54,28,g)
    txt(score,X3+300,by+104,30,col,"middle",bold=True)
o.append(f'<line x1="{X3+212}" y1="522" x2="{X3+212}" y2="546" stroke="{GRAY}" stroke-width="2.2" marker-end="url(#ah)"/>')
rect(X3,552,424,56,"#F5F8FB",LINE,1.2,7)
txt("점수  =  ( 1 + β ) · 양의 갈래  −  β · 음의 갈래",X3+212,578,14,NAVY,"middle",bold=True)
txt("β = 1  (사전 고정)",X3+212,596,10.5,GRAY,"middle")
rect(X3,622,424,84,LGREEN,GREEN,2,7)
txt("0.974",X3+108,672,38,GREEN,"middle",bold=True)
txt("사진을 한 장만 줬을 때의",X3+200,655,11,NAVY)
txt("상한 0.908 보다도 높습니다",X3+200,672,11,NAVY,bold=True)
txt("2모델 × 2배치 = 4조건 전부 유의",X3+200,690,10,GRAY)
txt("두 갈래가 보는 사진은 완전히 동일합니다. 다른 것은 어느 경로가",X3,730,11.5,NAVY,bold=True)
txt("열려 있는가뿐입니다. 사진에 노이즈를 씌워 음의 기준을 만드는",X3,748,11,GRAY)
txt("기존 방식으로는 이 두 상태를 어느 쪽도 만들 수 없습니다.",X3,766,11,GRAY)

# ── 배너 ──
rect(40,796,1520,58,DARKBG,None,0,8)
txt("무관한 사진은 입력에서 절대 제거되지 않습니다.  개입은 attention 행렬 안의 사각형 하나입니다.",70,832,17,"#FFFFFF",bold=True)
txt("판별력 점수(AUC) · Qwen2.5-VL-3B · 문항 300 · 사진 2장 기준 · 1·2단계는 사전 등록 후 측정. "
    "3단계는 저장된 로그의 사후 분석에 근거한 예비 결과이며, 새 문항 재현이 사전 등록되어 있습니다.",
    40,876,10.5,GRAY,italic=True)
o.append("</svg>")
p=Path(__file__).parent/"fig3_method.svg"; p.write_text("\n".join(o),encoding="utf-8")
print("wrote", p)
