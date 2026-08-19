#!/usr/bin/env python3
"""층 차원 설명도 — 모든 층에 거는가, 특정 층인가. 수치는 results/readdepth*.jsonl 실측."""
from pathlib import Path
W,H=1600,900
NAVY="#1F3B57"; BLUE="#1F77B4"; RED="#D62728"; DRED="#8B1A1A"; GREEN="#2E8B57"
GRAY="#6B7280"; DARKBG="#142638"; MUTE="#9AA6B2"; ORANGE="#B06A00"
CBLUE="#CBE0F5"; CGREEN="#CFE9DC"; LGREEN="#E9F4EE"; LRED="#FBEAEA"; LGRAY="#F1F3F5"
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
ST={"ghost":(GHOST,GHOSTLINE,0.8,"✕",FAINT),"diag":(LGRAY,LINE,0.8,None,None),
    "kept":(CBLUE,BLUE,1.1,None,None),"need":(CGREEN,GREEN,1.1,None,None),
    "block":(DRED,DRED,1.0,"✕","#FFFFFF"),"open":("#F6DADA",RED,1.1,None,None)}
G_ON =[["diag","ghost","ghost"],["kept","diag","ghost"],["need","block","diag"]]
G_OFF=[["diag","ghost","ghost"],["kept","diag","ghost"],["need","open","diag"]]
def mat(x,y,cell,g):
    ms=cell*0.46
    for r in range(3):
        for c in range(3):
            f,s,sw,mk,mc=ST[g[r][c]]
            rect(x+c*cell,y+r*cell,cell,cell,f,s,sw)
            if mk: txt(mk,x+c*cell+cell/2,y+r*cell+cell/2+ms*0.36,ms,mc,"middle",True)

o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">')
o.append(f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
         f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{GRAY}"/></marker></defs>')
rect(0,0,W,H,"#FFFFFF")
txt("층 차원에서는? — 같은 사각형을 모든 층에 겁니다",40,52,25,NAVY,bold=True)
txt("attention 행렬은 층마다 새로 계산됩니다. 그래서 개입도 층마다 새로 걸어야 합니다.",40,80,13.5,GRAY)
line(40,102,1560,102,LINE,1.2)

# ── 좌: 모든 층에 동일 개입 ──
txt("모든 층에 같은 사각형",40,138,16,NAVY,bold=True)
labels=[("0층",172),("1층",290),("⋯",408),("35층",452)]
for i,(lb,y) in enumerate(labels):
    if lb=="⋯":
        for dy in (0,14,28): rect(126,y-6+dy,5,5,MUTE,None,0,2.5)
        continue
    mat(70,y,38,G_ON)
    txt(lb,196,y+62,13,NAVY,bold=True)
    txt("질문 → 방해 차단",196,y+80,10.5,DRED)
o.append(f'<line x1="52" y1="168" x2="52" y2="574" stroke="{MUTE}" stroke-width="1.8" marker-end="url(#ah)"/>')
txt("정보는 0층에서 35층 방향으로 흐릅니다",70,596,11,GRAY)
rect(40,614,460,92,LGRAY,LINE,1,6)
txt("가중치는 전혀 바꾸지 않습니다.",56,638,12,NAVY,bold=True)
txt("층마다 만들어지는 attention mask에 같은 위치의 사각형을",56,660,11,NAVY)
txt("−∞ 로 더할 뿐입니다. 층 수만큼 반복되지만 비용은 사실상 0.",56,680,11,NAVY)

# ── 우: 언제부터 걸어야 하나 ──
X=540
txt("그럼 몇 층부터 걸어야 하나 — 실측으로 확인",X,138,16,NAVY,bold=True)
txt("Qwen2.5-VL-3B · 36개 층 · 문항 300",X,158,10.5,GRAY)
BX,BW=X+128,600
txt("0층",BX,190,10.5,GRAY,"middle"); txt("35층",BX+BW,190,10.5,GRAY,"middle")
txt("← 앞쪽",BX+60,190,10,MUTE,"middle"); txt("뒤쪽 →",BX+BW-60,190,10,MUTE,"middle")
rows=[("0층부터  (우리)",0,0.9057,100.0,True),
      ("8층부터",8,0.8992,96.9,False),
      ("16층부터",16,0.8394,68.2,False),
      ("24층부터",24,0.7153,8.8,False),
      ("아예 안 걸면",36,0.6970,0.0,False)]
for k,(lab,L,a,rec,ours) in enumerate(rows):
    y=212+k*74
    if ours: rect(X-8,y-8,1020,60,"#F2FAF5",GREEN,1.6,7)
    txt(lab,X+4,y+30,13 if ours else 12,GREEN if ours else NAVY,bold=ours)
    w0=BW*L/36
    if w0>0:
        rect(BX,y+8,w0,34,"#F6DADA",RED,1.2,3)
        if w0>70: txt("그대로 읽힘",BX+w0/2,y+30,11,RED,"middle",bold=True)
    if BW-w0>0:
        rect(BX+w0,y+8,BW-w0,34,CGREEN,GREEN,1.2,3)
        if BW-w0>70: txt("읽기 차단",BX+w0+(BW-w0)/2,y+30,11,GREEN,"middle",bold=True)
    txt(f"{a:.3f}",BX+BW+56,y+30,15,GREEN if ours else NAVY,"middle",bold=True)
    col = GREEN if rec>90 else (ORANGE if rec>50 else RED)
    txt(f"{rec:.0f}%",BX+BW+150,y+30,17 if ours else 15,col,"middle",bold=True)
txt("판별력",BX+BW+56,200,10.5,GRAY,"middle")
txt("회복률",BX+BW+150,200,10.5,GRAY,"middle")

rect(X,596,1020,58,LRED,RED,1.4,6)
txt("앞쪽 8층을 놓치면 아직 97%가 남지만, 16층까지 놓치면 68%, 24층까지 놓치면 사실상 0입니다.",X+16,622,12.5,NAVY,bold=True)
txt("오염은 앞쪽 층에서 일어납니다. 이미 섞인 뒤에 끊는 것은 늦습니다 — 되돌릴 수 없습니다.",X+16,643,11.5,RED,bold=True)
rect(X,666,1020,40,"#FFF8E8",ORANGE,1.2,6)
txt("7B(28층)도 같은 방향입니다. 다만 16층부터 걸면 무개입(0.869)보다 낮은 0.854 — 늦은 개입은 도움이 아니라 해가 됩니다.",X+16,691,11,NAVY)

rect(40,734,1520,58,DARKBG,None,0,8)
txt("특정 층만 고르는 게 아닙니다. 0층부터 끝까지 전부 겁니다 — 앞쪽을 놓치면 뒤에서 아무리 막아도 소용없기 때문입니다.",70,770,16,"#FFFFFF",bold=True)
txt("판별력 점수(AUC) · 문항 300 · 회복률 = (해당 조건 − 무개입) / (0층부터 − 무개입). 사전 등록 후 측정.",40,834,10.5,GRAY,italic=True)
o.append("</svg>")
p=Path(__file__).parent/"fig6_layers.svg"; p.write_text("\n".join(o),encoding="utf-8")
print("wrote",p)
