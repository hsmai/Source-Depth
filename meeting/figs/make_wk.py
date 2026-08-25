#!/usr/bin/env python3
"""주간 보고용 그림 3장. 수치는 results/ 실측."""
from pathlib import Path
NAVY="#1F3B57"; BLUE="#1F77B4"; RED="#D62728"; DRED="#8B1A1A"; GREEN="#2E8B57"
GRAY="#6B7280"; MUTE="#9AA6B2"; ORANGE="#B06A00"
LB="#E8F1FA"; LR="#FBEAEA"; LG="#E9F4EE"; LGY="#F3F5F7"; LO="#FFF8E8"
LINE="#D5DEE8"; FAINT="#C9D2DB"
FF="Helvetica Neue, Helvetica, Arial, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif"

def new(w,h):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{GRAY}"/></marker></defs>',
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#FFFFFF"/>']
def R(o,x,y,w,h,f,s=None,sw=1,rx=0):
    st=f' stroke="{s}" stroke-width="{sw}"' if s else ''
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}"{st}/>')
def T(o,t,x,y,sz=12,f=NAVY,an="start",b=False,i=False):
    bb=' font-weight="bold"' if b else ''; ii=' font-style="italic"' if i else ''
    o.append(f'<text x="{x}" y="{y}" font-family="{FF}" font-size="{sz}" fill="{f}" text-anchor="{an}"{bb}{ii}>{t}</text>')
def L(o,x1,y1,x2,y2,c=LINE,w=1,d=None):
    dd=f' stroke-dasharray="{d}"' if d else ''
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{dd}/>')
def save(o,n):
    o.append("</svg>"); p=Path(__file__).parent/n; p.write_text("\n".join(o),encoding="utf-8"); print("wrote",n)

# ───────── 그림 A : 문제 (슬라이드 2) ─────────
o=new(1400,780)
T(o,"위치 힌트를 없앤 새 벤치에서 문제가 더 커졌습니다",50,58,29,NAVY,b=True)
T(o,"관련 사진을 '내용'으로만 특정하고, 위치는 무작위로 섞었습니다 · 새로 만든 600문항",50,88,14,GRAY)
L(o,50,110,1350,110,LINE,1.2)
R(o,50,136,1300,150,LGY,LINE,1,10)
T(o,"문항 예시",76,166,15,GRAY,b=True)
T(o,"사진 3장  —  ① 주방(microwave 있음, 개 없음)   ② 공원(개 있음)   ③ 거리",76,198,15.5,NAVY,b=True)
T(o,'"microwave가 있는 사진에 개가 있나요?"',76,230,15.5,NAVY,i=True)
T(o,"정답: 아니오",76,262,14,GREEN,b=True)
T(o,"모델의 답:  \"있습니다\"  ✗",300,262,14,RED,b=True)
T(o,"— 무관한 사진에 있는 개를 그대로 답합니다",470,262,13,GRAY)
T(o,"같은 문항 · 같은 모델 · 개입만 다르게",50,330,17,NAVY,b=True)
X0,BW=460,660
bars=[("아무것도 안 함",0.453,RED),("방해 사진을 알려주고 처리",0.964,GREEN)]
for i,(lab,v,c) in enumerate(bars):
    y=356+i*96
    T(o,lab,X0-24,y+42,16,NAVY,"end",b=True)
    R(o,X0,y,BW,62,"#EDF1F5",LINE,1,6)
    R(o,X0,y,BW*v,62,c,None,0,6)
    T(o,f"{v:.3f}",X0+BW+20,y+42,28,c,b=True)
L(o,X0+BW*0.5,340,X0+BW*0.5,y+80,MUTE,1.8,"5 4")
T(o,"0.50 = 동전 던지기",X0+BW*0.5+12,336,13,MUTE,b=True)
T(o,"판별력 점수 — 맞다/아니다를 얼마나 잘 가려내는가 · 작은 모델(3B) · 사진 3장 · 문항 300개",X0,566,12.5,GRAY,i=True)
T(o,"참고: 기존 벤치(위치를 알려주는 질문)에서 사진 1장만 줬을 때는 0.908 이었습니다",X0,590,12.5,GRAY,i=True)
R(o,50,624,1300,60,LR,RED,1.6,8)
T(o,"아무 처리도 안 하면 동전 던지기보다 못합니다. 정답이 '아니오'인 문항만 보면 정확도 0.267.",76,662,17,RED,b=True)
R(o,50,700,1300,60,NAVY,None,0,8)
T(o,"기존 벤치는 질문이 \"첫 번째 사진\"이라고 위치를 알려줬습니다. 그것을 없앴더니 문제가 사라지기는커녕 더 커졌습니다.",76,738,17,"#FFFFFF",b=True)
save(o,"wk_a_problem.svg")

# ───────── 그림 B : FOCUS 비교 (슬라이드 4) ─────────
o=new(1400,800)
T(o,"기존 최신 연구(FOCUS)와의 비교",50,58,29,NAVY,b=True)
T(o,"같은 문항·같은 모델에서, 원 논문 수식 그대로 재구성했습니다 (이미지 2장 조건)",50,88,14,GRAY)
L(o,50,110,1350,110,LINE,1.2)
T(o,"두 방법이 무엇을 하는가",50,150,19,NAVY,b=True)
rows=[("FOCUS",["사진을 하나씩만 남기고 나머지는 노이즈로 덮음","그 결과를 전부 합산 + 노이즈만 넣은 결과를 뺌"],
       "무관한 사진을 고르지 않음 — 전부 합침",MUTE,LGY),
      ("우리",["사진을 하나씩 빼보고 답이 흔들리는 정도로 무관한 사진을 찾음","그 사진을 '질문이 읽는 경로'만 차단 (사진은 그대로 둠)"],
       "무관한 사진을 특정해서 그 경로만 끊음",GREEN,LG)]
for i,(nm,ls,note,col,lf) in enumerate(rows):
    y=175+i*128
    R(o,50,y,1300,112,lf,col,1.6,10)
    T(o,nm,76,y+40,21,col,b=True)
    for j,l in enumerate(ls): T(o,"· "+l,230,y+34+j*26,14,NAVY)
    T(o,note,230,y+94,13,col,b=True)
T(o,"결과 — 판별력 점수",50,470,19,NAVY,b=True)
T(o,"FOCUS에게는 하이퍼파라미터를 가장 유리한 값으로 맞춰줬습니다",250,470,13,GRAY)
groups=[("작은 모델 (3B)",[("아무것도 안 함",0.697,MUTE),("FOCUS",0.583,RED),("우리",0.756,GREEN)]),
        ("큰 모델 (7B)",[("아무것도 안 함",0.869,MUTE),("FOCUS",0.854,RED),("우리",0.897,GREEN)])]
for gi,(gn,bs) in enumerate(groups):
    gx=50+gi*680
    T(o,gn,gx+24,506,16,NAVY,b=True)
    for i,(lab,v,c) in enumerate(bs):
        y=522+i*62
        T(o,lab,gx+170,y+32,14,NAVY if c!=MUTE else GRAY,"end",b=(c==GREEN))
        R(o,gx+184,y,420,42,"#EDF1F5",None,0,5)
        R(o,gx+184,y,420*((v-0.5)/0.45),42,c,None,0,5)
        T(o,f"{v:.3f}",gx+614,y+30,20,c,b=True)
    L(o,gx+184,516,gx+184,522+3*62-14,MUTE,1.5,"4 4")
    T(o,"0.5",gx+184,512,11,MUTE,"middle")
R(o,50,720,1300,60,LG,GREEN,1.8,8)
T(o,"두 모델 모두 우리가 유의하게 높습니다.  3B는 FOCUS가 아무것도 안 한 것보다도 낮습니다.",76,748,17,GREEN,b=True)
T(o,"※ 공식 코드가 아니라 원 논문 수식을 우리 로그로 재구성한 것이고, 노이즈 강도는 FOCUS에 불리한 설정입니다. 논문 주장으로 쓰려면 공식 코드로 다시 재야 합니다.",76,770,12.5,GRAY,i=True)
save(o,"wk_b_focus.svg")

# ───────── 그림 C : 관련도 연속성 (슬라이드 5) ─────────
o=new(1400,820)
T(o,"한계 — 관련도는 '있다/없다'로 나뉘지 않습니다",50,58,29,NAVY,b=True)
T(o,"지금 우리 방법은 가장 영향이 큰 사진 1장만 남기고 나머지를 무관으로 처리합니다",50,88,14,GRAY)
L(o,50,110,1350,110,LINE,1.2)
T(o,"사진 4장을 넣고, 각 사진을 빼봤을 때 답이 흔들린 정도 (가장 큰 것을 1.0으로) — 실측 중앙값",50,150,17,NAVY,b=True)
ex=[("한 장이 압도적인 문항 (n=111)",[1.00,0.08,0.04,0.01],GREEN,"판별 정확도 0.937"),
    ("영향이 비슷하게 퍼진 문항 (n=71)",[1.00,0.83,0.50,0.20],RED,"판별 정확도 0.493")]
for i,(ti,vs,col,acc) in enumerate(ex):
    x=50+i*680
    R(o,x,172,650,268,LGY if i==0 else LR,LINE if i==0 else RED,1.4 if i else 1,10)
    T(o,ti,x+24,204,15.5,NAVY if i==0 else RED,b=True)
    for j,v in enumerate(vs):
        y=224+j*48
        T(o,f"사진 {j+1}",x+24,y+30,13,NAVY)
        R(o,x+100,y+10,420,28,"#FFFFFF",LINE,1,4)
        R(o,x+100,y+10,420*v,28,col if j==0 else (MUTE if v<0.4 else ORANGE),None,0,4)
        T(o,f"{v:.2f}",x+534,y+31,14,NAVY,b=(j==0))
    T(o,acc,x+430,204,14,col,b=True)
T(o,"두 번째로 영향이 큰 사진이 첫 번째와 비슷할수록, 판별이 정확히 그만큼 무너집니다",50,486,17,NAVY,b=True)
cells=[("1·2위 차이가 큼\n상위 25%",0.960,GREEN),("중간 50%",0.733,ORANGE),("1·2위 차이가 작음\n하위 25%",0.493,RED)]
for i,(lab,v,c) in enumerate(cells):
    x=50+i*436
    R(o,x,506,406,150,"#FFFFFF",c,2,10)
    for j,ln in enumerate(lab.split("\n")):
        T(o,ln,x+203,536+j*20,14,NAVY,"middle",b=(j==0))
    T(o,f"{v:.2f}",x+203,624,38,c,"middle",b=True)
    if i<2: T(o,"▶",x+416,596,20,MUTE,"middle")
T(o,"작은 모델(3B) · 사진 4장 · 문항 300개 · '판별 정확도' = 관련 있는 사진을 맞게 고른 비율",50,684,12.5,GRAY,i=True)
R(o,50,706,1300,96,LB,BLUE,1.8,10)
T(o,"그래서 다음 단계는",76,738,17,BLUE,b=True)
T(o,"① 두 사진이 비슷하게 중요하면 둘 다 남긴다 (문항마다 몇 장 남길지 다르게)",76,768,15,NAVY)
T(o,"② 아예 끊거나 안 끊거나가 아니라, 관련도에 비례해 차단 강도를 조절한다",76,792,15,NAVY)
save(o,"wk_c_continuity.svg")

# ───────── 그림 D : 판별자를 바꿔도 개입이 이득 (슬라이드 5) ─────────
o=new(1400,660)
T(o,"판별을 누가 하든, '읽기만 차단'이 '통째 삭제'보다 낫습니다",50,58,29,NAVY,b=True)
T(o,"관련 사진 위치가 무작위인 새 벤치 · 사진 3장 · 문항 300개 · 작은 모델(3B)",50,88,14,GRAY)
L(o,50,110,1350,110,LINE,1.2)
X0,BW=380,520
bars=[("아무것도 안 함",0.453,MUTE,False),
      ("CLIP이 찾고  →  통째 삭제",0.742,"#A9B4BF",False),
      ("CLIP이 찾고  →  읽기만 차단",0.763,BLUE,True),
      ("우리가 찾고  →  읽기만 차단",0.859,GREEN,True)]
for i2,(lab,v,c,b) in enumerate(bars):
    y=160+i2*76
    T(o,lab,X0-24,y+36,15.5,NAVY if b else GRAY,"end",b=b)
    R(o,X0,y,BW,52,"#F1F4F7",LINE,1,6)
    R(o,X0,y,BW*((v-0.40)/0.52),52,c,None,0,6)
    T(o,f"{v:.3f}",X0+BW+20,y+36,24,c,b=True)
# 브래킷 — CLIP 두 조건 차이
bx=X0+BW+120
L(o,bx,236,bx+18,236,GREEN,2.2); L(o,bx+18,236,bx+18,312,GREEN,2.2); L(o,bx,312,bx+18,312,GREEN,2.2)
R(o,bx+30,240,290,68,LG,GREEN,1.6,8)
T(o,"차이 [+0.007, +0.036]  ★ 유의",bx+46,266,14.5,GREEN,b=True)
T(o,"7B도 동일:  [+0.003, +0.046] ★",bx+46,292,12.5,GRAY)
T(o,"판별자를 CLIP으로 바꿔도 결과가 유지됩니다  →  기여는 '판별'이 아니라 '개입 방식'입니다",X0-24,486,15.5,NAVY,"start",b=True)
T(o,"※ 사진 2장 조건에서는 차이가 없습니다 — 차단할 사진이 한 장뿐이라 여지가 없기 때문입니다",X0-24,510,12.5,GRAY,i=True)
R(o,50,548,1300,84,NAVY,None,0,10)
T(o,"사진을 지우면 나머지 사진들이 서로 참고하던 맥락까지 함께 사라집니다.",76,582,18,"#FFFFFF",b=True)
T(o,"읽기 경로만 끊으면 그 맥락은 남고, 방해가 되는 통로만 막힙니다.",76,610,15,"#AFC6DA")
save(o,"wk_d_selector.svg")
