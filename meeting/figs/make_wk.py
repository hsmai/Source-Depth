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

# ───────── 그림 E : FOCUS vs 우리, 방식 자체 비교 ─────────
o=new(1400,890)
T(o,"두 방법이 실제로 무엇을 하는가  —  사진 3장 예시",50,56,28,NAVY,b=True)
L(o,50,86,1350,86,LINE,1.2)
CW,CH,GP=76,52,8
def imgrow(x,y,states,ans=None,ansc=NAVY):
    """states: 'ok' 원본 / 'noise' 픽셀 노이즈 / 'cut' attention 차단"""
    for i,st in enumerate(states):
        bx=x+i*(CW+GP)
        if st=="ok":
            R(o,bx,y,CW,CH,"#DCE9F7",BLUE,1.4,5)
            T(o,f"사진{i+1}",bx+CW/2,y+CH/2+5,13,NAVY,"middle",b=True)
        elif st=="noise":
            R(o,bx,y,CW,CH,"#F6DADA",RED,1.4,5)
            o.append(f'<clipPath id="cp{x}{y}{i}"><rect x="{bx}" y="{y}" width="{CW}" height="{CH}" rx="5"/></clipPath>')
            o.append(f'<g clip-path="url(#cp{x}{y}{i})">')
            for k in range(-2,9): L(o,bx+k*11,y,bx+k*11-18,y+CH,RED,1.6)
            o.append('</g>')
            R(o,bx,y,CW,CH,"none",RED,1.4,5)
        else:
            R(o,bx,y,CW,CH,"#DCE9F7",BLUE,1.4,5)
            T(o,f"사진{i+1}",bx+CW/2,y+CH/2+5,13,"#9BB6D4","middle",b=True)
            R(o,bx,y,CW,CH,"#5A6570",None,0,5)
            o.append(f'<rect x="{bx}" y="{y}" width="{CW}" height="{CH}" rx="5" fill="#5A6570" opacity="0.72"/>')
            T(o,"✕",bx+CW/2,y+CH/2+8,22,"#FFFFFF","middle",b=True)
    qx=x+3*(CW+GP)+6
    R(o,qx,y,64,CH,NAVY,None,0,5)
    T(o,"질문",qx+32,y+CH/2+5,13,"#FFFFFF","middle",b=True)
    if ans:
        T(o,"→",qx+76,y+CH/2+7,18,MUTE,"middle")
        T(o,ans,qx+100,y+CH/2+7,15,ansc,b=True)

# ── 왼쪽: FOCUS ──
PX=50
R(o,PX,106,640,652,"#FFFFFF",RED,1.8,12)
T(o,"FOCUS",PX+24,146,23,RED,b=True)
T(o,"한 장만 남기고 나머지를 노이즈로 덮음  →  전부 합산",PX+24,172,14,GRAY)
rows=[(["ok","noise","noise"],"답 A"),(["noise","ok","noise"],"답 B"),
      (["noise","noise","ok"],"답 C"),(["noise","noise","noise"],"답 D")]
for i,(st,ans) in enumerate(rows):
    y=196+i*72
    T(o,f"{i+1}회차",PX+24,y+CH/2+5,12,GRAY)
    imgrow(PX+84,y,st,ans,NAVY if i<3 else MUTE)
T(o,"↑ 아무것도 안 보고 하는 말 (모델의 원래 편향)",PX+84,494,11.5,MUTE,i=True)
R(o,PX+24,512,592,74,LR,RED,1.5,8)
T(o,"최종 답  =  A + B + C  −  α × D",PX+320,548,17,RED,"middle",b=True)
T(o,"모든 사진에 똑같이 한 번씩 기회를 주고 전부 더합니다",PX+320,572,12,NAVY,"middle")
R(o,PX+24,600,592,86,"#FFF4F4",RED,1.5,8)
T(o,"무관한 사진을 고르는 단계가 없습니다.",PX+44,628,15,RED,b=True)
T(o,"\"이 사진은 관계없으니 버리자\"는 판단을 하지 않고,",PX+44,652,13,NAVY)
T(o,"모든 사진의 의견을 그대로 합칩니다.",PX+44,674,13,NAVY)
T(o,"픽셀을 망가뜨리므로 매번 이미지 인코딩을 다시 해야 합니다",PX+24,712,12,GRAY,i=True)

# ── 오른쪽: 우리 ──
QX=710
R(o,QX,106,640,652,"#FFFFFF",GREEN,1.8,12)
T(o,"우리",QX+24,146,23,GREEN,b=True)
T(o,"하나씩 가려보고 무관한 사진을 특정  →  그 읽기 경로만 차단",QX+24,172,14,GRAY)
rows2=[(["ok","ok","ok"],"기준 답",MUTE),(["cut","ok","ok"],"조금 흔들림",MUTE),
       (["ok","cut","ok"],"크게 흔들림",GREEN),(["ok","ok","cut"],"조금 흔들림",MUTE)]
for i,(st,ans,c) in enumerate(rows2):
    y=196+i*72
    T(o,"기준" if i==0 else f"{i}회차",QX+24,y+CH/2+5,12,GRAY)
    imgrow(QX+84,y,st,ans,c)
T(o,"↑ 가장 크게 흔들린 사진 2 = 실제로 답에 쓰이는 사진",QX+84,494,11.5,GREEN,i=True,b=True)
R(o,QX+24,512,592,74,LG,GREEN,1.5,8)
T(o,"최종 답  =  사진 3장 전부 그대로 넣고 한 번만 계산",QX+320,544,15.5,GREEN,"middle",b=True)
T(o,"질문이 사진 1·3을 읽는 칸만 −∞ 로 막음",QX+320,570,13,NAVY,"middle")
R(o,QX+24,600,592,86,LG,GREEN,1.5,8)
T(o,"사진을 지우지 않습니다.",QX+44,628,15,GREEN,b=True)
T(o,"픽셀은 그대로 두고 attention 행렬에서",QX+44,652,13,NAVY)
T(o,"'질문 → 무관 사진' 칸만 막습니다.",QX+44,674,13,NAVY)
T(o,"픽셀을 안 바꾸므로 이미지 인코딩을 한 번만 하면 됩니다",QX+24,712,12,GRAY,i=True)

# ── 범례 (두 패널 아래, 가운데 정렬) ──
lg=[("#DCE9F7",BLUE,"원본 사진"),("#F6DADA",RED,"픽셀을 노이즈로 덮음"),("#5A6570","#5A6570","attention만 차단 — 사진은 그대로")]
tot=sum(len(l)*13+92 for _,_,l in lg)
lx=(1400-tot)//2
for f,st,lab in lg:
    R(o,lx,776,24,24,f,st,1.5,4)
    T(o,lab,lx+34,794,13.5,NAVY)
    lx+=len(lab)*13+92
R(o,50,822,1300,58,NAVY,None,0,10)
T(o,"FOCUS는 사진을 망가뜨려 한 장씩 따로 물어보고 합칩니다.  우리는 사진을 그대로 두고, 무관한 사진으로 가는 '읽기 통로'만 막습니다.",76,858,16.5,"#FFFFFF",b=True)
save(o,"wk_e_mechanism.svg")

# ───────── 그림 F : 기전 — 왜 하필 '읽기' 경로인가 ─────────
o=new(1400,820)
T(o,"왜 하필 '읽기' 경로인가  —  통념과 반대였습니다",50,58,29,NAVY,b=True)
T(o,"처방을 먼저 정한 게 아니라, 두 경로를 각각 끊어보고 원인을 특정했습니다",50,88,14,GRAY)
L(o,50,110,1350,110,LINE,1.2)
# 통념 vs 측정
R(o,50,136,630,148,LGY,MUTE,1.4,10)
T(o,"기존 통념",76,168,15.5,GRAY,b=True)
T(o,"\"여러 이미지가 서로 섞여서 환각이 생긴다\"",76,202,17,NAVY,b=True)
T(o,"→ 처방: 이미지끼리 보는 연결을 막아라  (MIMIC 등)",76,232,13.5,GRAY)
T(o,"→ 반대 진영은 오히려 더 열어라  (CAPL · SoFA)",76,258,13.5,GRAY)
R(o,720,136,630,148,LR,RED,1.6,10)
T(o,"우리 측정",746,168,15.5,RED,b=True)
T(o,"이미지끼리 보는 연결을 끊었더니",746,202,17,NAVY,b=True)
T(o,"오히려 0.697 → 0.403 으로 무너졌습니다",746,232,17,RED,b=True)
T(o,"섞임은 오염원이 아니라 오히려 버팀목이었습니다",746,258,13.5,NAVY,b=True)
# 막대
T(o,"같은 문항 · 같은 모델 · 끊는 경로만 다르게",50,326,17,NAVY,b=True)
X0,BW=430,660
bars=[("아무것도 안 함",0.697,MUTE,""),
      ("이미지 ↔ 이미지 를 끊음",0.403,RED,"▼ 통념대로 했더니 무너짐"),
      ("질문 → 무관 이미지 를 끊음",0.906,GREEN,"▲ 사진 1장만 준 수준으로 회복")]
for i,(lab,v,c,note) in enumerate(bars):
    y=352+i*84
    T(o,lab,X0-24,y+38,15.5,NAVY,"end",b=(i>0))
    R(o,X0,y,BW,56,"#EDF1F5",LINE,1,6)
    R(o,X0,y,BW*((v-0.35)/0.60),56,c,None,0,6)
    T(o,f"{v:.3f}",X0+BW+20,y+38,24,c,b=True)
    if note: T(o,note,X0+BW+126,y+38,13.5,c,b=True)
T(o,"판별력 점수 · 작은 모델(3B) · 사진 2장 · 문항 300개 · 7B도 같은 방향 (0.869 → 0.447 / 0.899)",X0,624,12.5,GRAY,i=True)
R(o,50,652,1300,64,LG,GREEN,1.6,8)
T(o,"배치·모델·질문 유형을 바꿔 10개 설정에서 재봤고, 이미지끼리 차단이 이득인 설정은 하나도 없었습니다.",76,682,16.5,GREEN,b=True)
T(o,"층 구간을 12~23층으로 한정한 MIMIC 방식도 마찬가지였습니다 (3B 0.412 · 7B 0.852, 둘 다 아무것도 안 한 것보다 낮음).",76,706,12.5,NAVY)
R(o,50,732,1300,68,NAVY,None,0,10)
T(o,"그래서 우리 처방은 휴리스틱이 아니라 원인 규명에서 나온 것입니다.",76,762,18,"#FFFFFF",b=True)
T(o,"무관한 사진을 지우면 버팀목까지 사라집니다. 그래서 지우지 않고, 해악이 흐르는 '읽기' 통로만 막습니다.",76,788,14,"#AFC6DA")
save(o,"wk_f_mechanism_why.svg")
