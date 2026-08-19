#!/usr/bin/env python3
"""3단계(경로 대비) 상세 설명도. 수치는 results/pathway.jsonl 실측."""
from pathlib import Path
W,H=1600,1050
NAVY="#1F3B57"; BLUE="#1F77B4"; RED="#D62728"; DRED="#8B1A1A"; GREEN="#2E8B57"
GRAY="#6B7280"; DARKBG="#142638"; ORANGE="#B06A00"
CBLUE="#CBE0F5"; CGREEN="#CFE9DC"; CRED="#F6CFCF"
LBLUE="#E8F1FA"; LRED="#FBEAEA"; LGREEN="#E9F4EE"; LGRAY="#F1F3F5"
LINE="#D5DEE8"; GHOST="#FAFBFC"; GHOSTLINE="#EDF0F3"; FAINT="#C3C9D0"
FF="Helvetica Neue, Helvetica, Arial, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"
o=[]
def rect(x,y,w,h,fill,stroke=None,sw=1,rx=0):
    s=f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}/>')
def txt(t,x,y,size=12,fill=NAVY,anchor="start",bold=False,italic=False):
    b=' font-weight="bold"' if bold else ''; i=' font-style="italic"' if italic else ''
    o.append(f'<text x="{x}" y="{y}" font-family="{FF}" font-size="{size}" fill="{fill}"'
             f' text-anchor="{anchor}"{b}{i}>{t}</text>')
def line(x1,y1,x2,y2,c=LINE,w=1,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{d}/>')
def circ(x,y,r,f,s=None,sw=1.5):
    st=f' stroke="{s}" stroke-width="{sw}"' if s else ''
    o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{f}"{st}/>')
ST={"ghost":(GHOST,GHOSTLINE,0.8,"✕",FAINT),"diag":(LGRAY,LINE,0.8,None,None),
    "kept":(CBLUE,BLUE,1.2,None,None),"need":(CGREEN,GREEN,1.2,None,None),
    "block":(DRED,DRED,1.0,"✕","#FFFFFF"),"open":(CRED,RED,1.2,None,None)}
def matrix(x,y,cell,g):
    ms=cell*0.44
    for r in range(3):
        for c in range(3):
            f,s,sw,mk,mc=ST[g[r][c]]
            rect(x+c*cell,y+r*cell,cell,cell,f,s,sw)
            if mk: txt(mk,x+c*cell+cell/2,y+r*cell+cell/2+ms*0.36,ms,mc,"middle",True)
# 3x3: 행/열 = [사진1(대상), 방해, 질문]
G_POS=[["diag","ghost","ghost"],["kept","diag","ghost"],["need","block","diag"]]
G_NEG=[["diag","ghost","ghost"],["block","diag","ghost"],["need","open","diag"]]

o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">')
o.append(f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
         f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{GRAY}"/></marker>'
         f'<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker></defs>')
rect(0,0,W,H,"#FFFFFF")
txt("3단계 자세히 — 왜 '빼면' 좋아지는가",40,52,25,NAVY,bold=True)
txt("음의 갈래는 무작위로 틀리는 게 아니라 <tspan font-weight=\"bold\">체계적으로 거꾸로</tspan> 답합니다. 거꾸로인 신호를 빼면 정보가 더해집니다.",40,80,13.5,GRAY)
line(40,102,1560,102,LINE,1.2)

# ── ① 두 상태 만들기 ──
txt("①",40,140,17,BLUE,bold=True)
txt("같은 입력으로 두 상태를 만듭니다",72,140,16,NAVY,bold=True)
inp=[("질문 대상 사진","개 없음",LBLUE,BLUE),("방해 사진","개 있음",LRED,RED),("질문","\"1번에 개가 있나?\"",NAVY,NAVY)]
for i,(t,sub,f,s) in enumerate(inp):
    x=40+i*208
    rect(x,158,196,50,f,s,1.4,5)
    txt(t,x+98,180,12.5,"#FFFFFF" if t=="질문" else NAVY,"middle",bold=True)
    txt(sub,x+98,198,10.5,"#C7D6E4" if t=="질문" else s,"middle")
br=[("양의 갈래","질문이 방해 사진을 못 읽음",G_POS,GREEN,"\"없다\"","정답과 일치",True,40),
    ("음의 갈래","사진끼리 못 봄",G_NEG,RED,"\"있다\"","정답과 반대",False,352)]
for title,sub,g,col,ans,note,ok,bx in br:
    rect(bx,226,272,214,"#FFFFFF",col,1.8,7)
    txt(title,bx+16,250,13.5,col,bold=True)
    txt(sub,bx+16,268,10.5,GRAY)
    matrix(bx+18,282,44,g)
    txt("답",bx+180,318,11,GRAY)
    txt(ans,bx+180,346,23,col,bold=True)
    txt(("✓ " if ok else "✗ ")+note,bx+180,368,10.5,col,bold=True)
    txt("판별력 0.906" if ok else "판별력 0.403",bx+16,428,11.5,col,bold=True)
txt("두 갈래가 보는 사진은 완전히 동일합니다 — 열린 경로만 다릅니다",40,464,11.5,NAVY,bold=True)

# ── ② 음의 갈래가 하는 일 ──
X=680
txt("②",X,140,17,RED,bold=True)
txt("음의 갈래는 방해 사진을 읽고 답합니다",X+32,140,16,NAVY,bold=True)
cols=[("",X+14,168),("질문 대상",X+186,88),("방해 사진",X+296,88),("정답",X+396,72),
      ("양의 갈래",X+506,96),("음의 갈래",X+626,96)]
rect(X,158,860,30,NAVY,None,0,4)
for t,cx,cw in cols:
    if t: txt(t,cx+cw/2,178,11.5,"#FFFFFF","middle",bold=True)
rows=[("경우 A","개 없음","개 있음","없다","\"없다\"","\"있다\""),
      ("경우 B","개 있음","개 없음","있다","\"있다\"","\"없다\"")]
for k,r in enumerate(rows):
    y=188+k*54
    rect(X,y,860,54,"#FFFFFF" if k%2==0 else "#FAFBFC",LINE,0.8)
    txt(r[0],X+14+84,y+32,12,NAVY,"middle",bold=True)
    txt(r[1],X+186+44,y+32,12,NAVY,"middle")
    rect(X+296+10,y+12,68,30,LRED,RED,1.2,4)
    txt(r[2],X+296+44,y+32,12,RED,"middle",bold=True)
    txt(r[3],X+396+36,y+32,12,NAVY,"middle",bold=True)
    txt(r[4]+"  ✓",X+506+48,y+32,12,GREEN,"middle",bold=True)
    rect(X+626+10,y+12,76,30,"#F6DADA",RED,1.4,4)
    txt(r[5]+"  ✗",X+626+48,y+32,12,RED,"middle",bold=True)
rect(X,306,860,64,LRED,RED,1.4,6)
txt("두 경우 모두 음의 갈래의 답 = 방해 사진의 내용 그대로입니다.",X+16,330,13,RED,bold=True)
txt("사진끼리 못 보게 하면 방해 사진이 '다른 사진'으로 구분되지 않아, 그 내용이 질문 대상인 것처럼 새어 들어옵니다.",X+16,354,11,NAVY)
rect(X,384,860,56,"#FFF8E8",ORANGE,1.4,6)
txt("판별력 0.403 — 우연(0.500)보다 낮습니다.",X+16,408,13,ORANGE,bold=True)
txt("무작위로 틀리는 게 아니라 체계적으로 거꾸로입니다. 그래서 '빼는' 것이 의미를 갖습니다.",X+16,430,11,NAVY)
txt("두 갈래의 상관 r = +0.33 — 서로 다른 정보를 담고 있어 합칠 이득이 큽니다",X,464,11.5,NAVY,bold=True)
line(40,492,1560,492,LINE,1)

# ── ③ 빼면 어떻게 되는가 ──
txt("③",40,540,17,BLUE,bold=True)
txt("거꾸로인 신호를 빼면, 맞는 방향으로 더 밀립니다",72,540,16,NAVY,bold=True)
txt("가로축 = 모델의 판단. 아래 값은 각 경우의 평균 margin (logit(있다) − logit(없다))",72,560,10.5,GRAY)
AX0,AXW=150,860; CX=AX0+AXW/2; SC=76
txt("← 더 확실한 \"없다\"",AX0,600,11.5,GRAY,bold=True)
txt("0",CX,600,11.5,GRAY,"middle",bold=True)
txt("더 확실한 \"있다\" →",AX0+AXW,600,11.5,GRAY,"end",bold=True)
cases=[("경우 A","정답 \"없다\"",-2.243,+0.388,-4.874,652),
       ("경우 B","정답 \"있다\"",+0.909,-0.217,+2.035,762)]
for title,gtl,vp,vn,vc,ay in cases:
    txt(title,40,ay-4,12.5,NAVY,bold=True)
    txt(gtl,40,ay+14,11,GRAY)
    line(AX0,ay,AX0+AXW,ay,"#C9D2DB",1.6)
    for tick in range(-5,6):
        x=CX+tick*SC
        if AX0<=x<=AX0+AXW: line(x,ay-4,x,ay+4,"#C9D2DB",1.1)
    line(CX,ay-26,CX,ay+26,"#9AA6B2",1,"3 3")
    xn,xp,xc=CX+vn*SC,CX+vp*SC,CX+vc*SC
    o.append(f'<line x1="{xp}" y1="{ay-11}" x2="{xc+(9 if vc<vp else -9)}" y2="{ay-11}" '
             f'stroke="{BLUE}" stroke-width="2" marker-end="url(#ahb)"/>')
    circ(xn,ay,9,"#FFFFFF",RED,2.4)
    txt(f"{vn:+.2f}",xn,ay-46,11.5,RED,"middle",bold=True)
    txt("음의 갈래",xn,ay-32,10,RED,"middle")
    circ(xp,ay,9,"#FFFFFF",GREEN,2.4)
    txt(f"{vp:+.2f}",xp,ay+26,11.5,GREEN,"middle",bold=True)
    txt("양의 갈래",xp,ay+40,10,GREEN,"middle")
    circ(xc,ay,12,BLUE,BLUE,2.4); circ(xc,ay,4.5,"#FFFFFF")
    txt(f"{vc:+.2f}",xc,ay+26,12.5,BLUE,"middle",bold=True)
    txt("조합 = 2×양 − 음",xc,ay+40,10,BLUE,"middle")

rect(1060,536,500,64,"#F5F8FB",LINE,1.2,7)
txt("점수  =  ( 1 + β ) · 양의 갈래  −  β · 음의 갈래",1310,565,15,NAVY,"middle",bold=True)
txt("β = 1 로 사전 고정 (결과를 보고 고르지 않음)",1310,586,10.5,GRAY,"middle")
rect(1060,618,500,96,LGREEN,GREEN,2,7)
txt("0.906",1132,666,26,GRAY,"middle",bold=True)
txt("양의 갈래 단독",1132,690,10,GRAY,"middle")
txt("→",1204,664,20,GRAY,"middle")
txt("0.974",1300,670,36,GREEN,"middle",bold=True)
txt("사진 한 장만 줬을 때의",1382,654,10.5,NAVY)
txt("상한 0.908 도 넘습니다",1382,672,10.5,NAVY,bold=True)
txt("2모델 × 2배치 전부 유의",1382,690,10,GRAY)

# ── 한계 ──
rect(40,822,1520,112,"#FFF4F4",RED,1.8,8)
txt("반드시 함께 말해야 하는 한계 — 이 빼기가 통하는 이유가 곧 약점입니다",64,850,15,RED,bold=True)
txt("음의 갈래가 '거꾸로'인 것은 우리 문항이 방해 사진을 항상 정답과 반대 방향으로 밀도록 설계했기 때문입니다.",64,876,12,NAVY)
txt("방해가 정답과 같은 방향으로 미는 문항에서는 음의 갈래가 오히려 맞히고, 빼기가 손해로 뒤집힐 수 있습니다 — 아직 한 번도 측정하지 않았습니다.",64,898,12,NAVY)
txt("→ 재현 실험에 대조 문항 200개를 추가했습니다. 여기서 손해가 나면 3단계는 '방법'이 아니라 '진단 도구'로 격하해 보고합니다.",64,920,12,RED,bold=True)
rect(40,950,1520,50,DARKBG,None,0,8)
txt("음의 갈래는 \"방해 사진이 답을 어느 쪽으로 밀고 있는가\"를 재는 측정기입니다. 그만큼 반대로 되밀어 줍니다.",70,981,16,"#FFFFFF",bold=True)
txt("판별력 점수(AUC) · Qwen2.5-VL-3B · 문항 300 · 셀별 평균 margin · 사후 분석에 근거한 예비 결과이며 새 문항 재현이 사전 등록되어 있습니다.",40,1024,10.5,GRAY,italic=True)
o.append("</svg>")
p=Path(__file__).parent/"fig4_contrast.svg"; p.write_text("\n".join(o),encoding="utf-8")
print("wrote",p)
