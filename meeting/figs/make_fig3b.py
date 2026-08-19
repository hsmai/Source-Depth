#!/usr/bin/env python3
"""제안 방법 개요도 — 2단계 버전(경로 대비 제외). 모든 수치는 실측값."""
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

# ══════════ 3 — 실제로 지우는 양 ══════════
X3=1136
txt("3",X3,140,19,BLUE,bold=True)
txt("실제로 지우는 양",X3+20,140,16,NAVY,bold=True)
txt("실측 — 사진 2장, 시퀀스 776토큰 (방해 사진 347 · 질문 21)",X3,158,10.5,GRAY)
SQ=236; SX,SY=X3+6,176
rect(SX,SY,SQ,SQ,"#F4F6F8",LINE,1.2)
txt("전체 attention 행렬  776 × 776",SX,SY-6,10,GRAY)
c0=SX+SQ*(360/776); cw=SQ*(347/776); rh=SQ*(21/776)
rect(c0,SY,cw,SQ,"#F3C9C9","#D62728",1.2)
rect(c0,SY+SQ-rh,cw,max(rh,2.5),DRED,DRED,0.8)
line(c0+cw,SY+SQ-rh/2,X3+300,SY+SQ+44,GRAY,1.2)
line(c0,SY+SQ-rh/2,X3+180,SY+SQ+44,GRAY,1.2)
rect(X3+180,SY+SQ+44,120,26,DRED,DRED,1,3)
txt("우리가 지우는 칸",X3+240,SY+SQ+61,10.5,"#FFFFFF","middle",bold=True)
rows=[("전체 행렬","776 × 776","602,176칸","100%",GRAY,"#F4F6F8"),
      ("사진을 통째로 뺀다","776 × 347","269,272칸","44.7%",RED,LRED),
      ("읽는 칸만 지운다  (우리)","21 × 347","7,287칸","1.21%",GREEN,LGREEN)]
for k,(lab,dim,cells,pct,col,bg) in enumerate(rows):
    y=SY+SQ+92+k*54
    rect(X3,y,424,46,bg,col if k else LINE,1.4 if k else 1,5)
    txt(lab,X3+12,y+18,11.5,col,bold=(k==2))
    txt(dim,X3+12,y+36,10,GRAY)
    txt(cells,X3+300,y+20,11.5,col,"end",bold=True)
    txt(pct,X3+412,y+20,15 if k==2 else 12.5,col,"end",bold=True)
txt("질문 토큰이 21개뿐이라, 지우는 것은 정사각형이 아니라",X3,SY+SQ+274,11.5,NAVY,bold=True)
txt("21줄짜리 얇고 긴 띠입니다. 사진을 통째로 빼는 것보다 37배 작습니다.",X3,SY+SQ+292,11.5,NAVY,bold=True)

# ── 배너 ──
rect(40,796,1520,58,DARKBG,None,0,8)
txt("무관한 사진은 입력에서 절대 제거되지 않습니다.  개입은 attention 행렬 안의 사각형 하나입니다.",70,832,17,"#FFFFFF",bold=True)
txt("판별력 점수(AUC) · Qwen2.5-VL-3B · 문항 300 · 사진 2장 기준 · 사전 등록 후 측정. "
    "토큰 수는 같은 조건 24문항의 중앙값(전체 776 · 방해 사진 347 · 질문 21).",
    40,876,10.5,GRAY,italic=True)
o.append("</svg>")
p=Path(__file__).parent/"fig3_method_2stage.svg"; p.write_text("\n".join(o),encoding="utf-8")
print("wrote", p)
