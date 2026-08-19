#!/usr/bin/env python3
"""기존 연구와의 차별성 — 어디에 손대는가 한눈에. 텍스트 최소화."""
from pathlib import Path
W,H=1600,900
NAVY="#1F3B57"; BLUE="#1F77B4"; RED="#D62728"; DRED="#8B1A1A"; GREEN="#2E8B57"
GRAY="#6B7280"; DARKBG="#142638"; MUTE="#9AA6B2"
LGREEN="#E9F4EE"; LGRAY="#F4F6F8"; LINE="#D8E0E8"; FAINT="#DDE3E9"
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
def circ(x,y,r,f,s=None,sw=2):
    st=f' stroke="{s}" stroke-width="{sw}"' if s else ''
    o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{f}"{st}/>')

def ic_pixel(x,y,s):                       # 사진에 노이즈
    rect(x,y+s*0.12,s,s*0.76,"#EDF1F5",MUTE,1.6,4)
    o.append(f'<clipPath id="cp1"><rect x="{x}" y="{y+s*0.12}" width="{s}" height="{s*0.76}" rx="4"/></clipPath>')
    o.append(f'<g clip-path="url(#cp1)">')
    for i in range(-4,14):
        line(x+i*7,y+s*0.12,x+i*7-24,y+s*0.88,RED,2.2)
    o.append('</g>')
    rect(x,y+s*0.12,s,s*0.76,"none",RED,2,4)
def grid(x,y,s,dark,n=4):                  # n×n 격자, dark=[(r,c),..]
    c=s/n
    for r in range(n):
        for k in range(n):
            f = DRED if (r,k) in dark else "#EDF1F5"
            rect(x+k*c,y+r*c,c-1.5,c-1.5,f,"#FFFFFF",1)
def ic_whole(x,y,s):  grid(x,y,s,[(r,1) for r in range(4)]+[(r,2) for r in range(4)])
def ic_one(x,y,s):    grid(x,y,s,[(3,1)])
def ic_logit(x,y,s):                       # 두 막대 빼기
    rect(x+s*0.04,y+s*0.18,s*0.26,s*0.64,"#EDF1F5",MUTE,1.6,3)
    rect(x+s*0.04,y+s*0.42,s*0.26,s*0.40,BLUE,None,0,3)
    txt("−",x+s*0.50,y+s*0.62,26,RED,"middle",bold=True)
    rect(x+s*0.70,y+s*0.18,s*0.26,s*0.64,"#EDF1F5",MUTE,1.6,3)
    rect(x+s*0.70,y+s*0.58,s*0.26,s*0.24,RED,None,0,3)

o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">')
rect(0,0,W,H,"#FFFFFF")
txt("기존 연구와 우리는 서로 다른 곳에 손을 댑니다",40,54,26,NAVY,bold=True)
txt("● = 그 연구가 개입하는 지점",40,82,13,GRAY)
line(40,104,1560,104,LINE,1.2)

COLS=[("VCD · FOCUS",False),("MIMIC",False),("CAPL · SoFA",False),("RSCD",False),("우리",True)]
CW=196; CX0=580
ROWS=[("입력 사진을 바꾼다",ic_pixel,[0]),
      ("연결을 통째로 바꾼다",ic_whole,[1,2,3]),
      ("출력을 보정한다",ic_logit,[0,3]),
      ("연결 중 한 칸만 바꾼다",ic_one,[4])]
RY0=214; RH=128
# 1) 행 띠 + 아이콘 + 라벨
for r,(lab,icon,hits) in enumerate(ROWS):
    y=RY0+r*RH; last=(r==3)
    rect(40,y,1520,RH-14,LGREEN if last else ("#FFFFFF" if r%2 else LGRAY),
         GREEN if last else None,1.6 if last else 0,8)
    icon(72,y+18,78)
    txt(lab,178,y+62,17 if last else 15.5,GREEN if last else NAVY,bold=True)
# 2) 열 구분선
for i in range(1,5):
    line(CX0+i*CW,196,CX0+i*CW,RY0+4*RH-14,FAINT,1)
# 3) 우리 열 테두리 (행 위에 얹어 하나의 틀로)
rect(CX0+4*CW-8,152,CW+16,RY0+4*RH-14-152+2,"none",GREEN,2.4,10)
# 4) 점
for r,(lab,icon,hits) in enumerate(ROWS):
    y=RY0+r*RH
    for i,(nm,ours) in enumerate(COLS):
        cx=CX0+i*CW+CW/2; cy=y+(RH-14)/2
        if i in hits:
            if ours: circ(cx,cy,23,GREEN); circ(cx,cy,9.5,"#FFFFFF")
            else:    circ(cx,cy,16,MUTE)
        else:
            circ(cx,cy,5,"none",FAINT,2)
# 5) 열 이름
for i,(nm,ours) in enumerate(COLS):
    cx=CX0+i*CW+CW/2
    txt(nm,cx,188,16 if ours else 13.5,GREEN if ours else NAVY,"middle",bold=True)

rect(40,742,1520,64,DARKBG,None,0,8)
txt("맨 아래 줄은 비어 있었습니다.",70,782,20,"#FFFFFF",bold=True)
txt("여러 사진 중 한 장으로 가는 경로만 끊은 연구는 아직 없습니다.",370,782,17,"#9FC7E8")
txt("VCD(2023) · FOCUS(2025) · MIMIC(2026) · CAPL(2026) · SoFA(CVPR 2025) · RSCD(2026) — 원문 대조 결과. "
    "빈 원 = 그 지점에 개입하지 않음.",40,848,11,GRAY,italic=True)
o.append("</svg>")
p=Path(__file__).parent/"fig5_novelty.svg"; p.write_text("\n".join(o),encoding="utf-8")
print("wrote",p)
