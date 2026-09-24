from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, base64, io, math, unicodedata, hashlib
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
C=ROOT/'Course'
E=[];F={};K=0;G='';MODULES=[]
INK='#26343d';MUTED='#697780';BLUE='#3b86ad';PURPLE='#9270b8';GREEN='#438b70';RED='#be655e';GOLD='#bd923c'
PALE=['#e6def7','#f9dae6','#dceef8','#def0df','#fff0b8']
FONT='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'

def el(t,x,y,w,h,**kw):
 global K
 K+=1
 d=dict(id='v'+str(K),type=t,x=x,y=y,width=w,height=h,angle=0,strokeColor=INK,backgroundColor='transparent',fillStyle='solid',strokeWidth=1.5,strokeStyle='solid',roughness=1.2,opacity=100,groupIds=[G] if G else [],frameId=None,roundness=None,seed=21000+K,version=1,versionNonce=99000+K,isDeleted=False,boundElements=[],updated=1,link=None,locked=False)
 d.update(kw);E.append(d);return d

def box(x,y,w,h,fill='transparent',stroke=INK,round=True,**kw):
 return el('rectangle',x,y,w,h,backgroundColor=fill,strokeColor=stroke,roundness={'type':3} if round else None,**kw)
def text(x,y,s,size=24,color=INK,w=None,**kw):
 lines=s.split('\n'); ft=ImageFont.truetype(FONT,size)
 wid=max(ft.getlength(l) for l in lines)+5 if w is None else w
 return el('text',x,y,wid,size*1.35*len(lines),text=s,originalText=s,fontSize=size,fontFamily=1,textAlign='left',verticalAlign='top',containerId=None,autoResize=True,lineHeight=1.35,strokeColor=color,roughness=0,**kw)
def line(ps,color=INK,arrow=False,dash=False,sw=1.5):
 x,y=ps[0];pts=[[a-x,b-y] for a,b in ps]
 return el('arrow' if arrow else 'line',x,y,max(a for a,b in ps)-min(a for a,b in ps),max(b for a,b in ps)-min(b for a,b in ps),points=pts,lastCommittedPoint=None,startBinding=None,endBinding=None,startArrowhead=None,endArrowhead='arrow' if arrow else None,strokeColor=color,strokeStyle='dashed' if dash else 'solid',strokeWidth=sw,elbowed=False)
def circ(x,y,r,fill='transparent',stroke=INK):return el('ellipse',x,y,r*2,r*2,backgroundColor=fill,strokeColor=stroke)
def badge(x,y,s,fill='#edf5ef',color=GREEN,size=18):
 w=ImageFont.truetype(FONT,size).getlength(s)+24
 box(x,y,w,34,fill,fill);text(x+12,y+3,s,size,color)
def paper(x,y,w,h,color=PALE[0],dotted=False):
 box(x+8,y+9,w,h,color,color)
 return box(x,y,w,h,'#ffffff',strokeStyle='dotted' if dotted else 'solid')
def note(x,y,s,fill='#fff8d7',w=190,angle=-.025):
 h=len(s.split('\n'))*27+34
 box(x+4,y+5,w,h,'#ecede8','#ecede8',False,angle=angle)
 box(x,y,w,h,fill,round=False,angle=angle)
 text(x+15,y+13,s,20,angle=angle)
 # tape
 box(x+w/2-24,y-9,48,18,'#f1e5bd','#f1e5bd',False,opacity=65,angle=-angle)
 return h

def title(n,x,y,name,why,ref):
 global G
 G=f'module-{n:02}'
 MODULES.append(dict(n=n,x=x,y=y,name=name,ref=ref))
 circ(x,y+3,22,PALE[(n-1)%5],PALE[(n-1)%5]);text(x+9,y+9,f'{n:02}',20)
 text(x+61,y,name,34)
 line([(x+62,y+47),(x+64+len(name)*33,y+43)],PALE[(n-1)%5],sw=5)
 text(x+61,y+61,why,22,MUTED)
 text(x+61,y+96,ref,17,MUTED)

def doc(x,y,w=90,h=110,color=BLUE,label=None):
 box(x,y,w,h,'#ffffff',color,False)
 line([(x+w-25,y),(x+w-25,y+25),(x+w,y+25)],color)
 for i in range(3):line([(x+14,y+40+i*17),(x+w-18,y+40+i*17)],color)
 if label:text(x,y+h+9,label,18,color)

def window(x,y,w,h,label=None,color=BLUE):
 box(x,y,w,h,'#fbfdfe',color)
 line([(x,y+29),(x+w,y+29)],color)
 for i in range(3):circ(x+12+i*15,y+11,3,[RED,GOLD,GREEN][i],[RED,GOLD,GREEN][i])
 if label:text(x+66,y+4,label,15,MUTED)

def terrain(x,y,w=300,h=150,stage=1):
 # Editable sketch: stable basin, semantic cue, then moving ball.
 pts=[]
 for i in range(41):
  u=i/40; yy=y+h*.36+(math.sin(u*math.pi)**2)*h*.53
  if stage==0: yy=y+h*.7
  pts.append((x+u*w,yy))
 for off in [-18,0,18]:line([(a,b+off) for a,b in pts], '#9dbea7',sw=1)
 line(pts,GREEN,sw=2.3)
 bx=x+w*(.18 if stage<2 else .55)
 by=y+h*.36+math.sin((.18 if stage<2 else .55)*math.pi)**2*h*.53 if stage else y+h*.7
 circ(bx-8,by-12,9,'#edb75d',GOLD)
 if stage>=2:line([(x+w*.2,y+27),(x+w*.46,y+47)],GOLD,True)
 if stage>=1:
  badge(x+w*.35,y-11,'语义条件', '#e8f4ed',GREEN,16)
  line([(x+w*.56,y+24),(x+w*.56,y+63)],GREEN,True,dash=True)

def packet(x,y,w=205,h=150):
 box(x+10,y-9,w-4,h,'#e9edf1','#8d9ca9')
 box(x,y,w,h,'#edf3f7','#6d8a9c')
 box(x+5,y-19,w*.5,27,'#edf3f7','#6d8a9c')
 doc(x+21,y+24,45,64,BLUE);doc(x+80,y+16,45,64,PURPLE);doc(x+139,y+24,45,64,GREEN)
 text(x+27,y+106,'图片 · 提示词 · 要求',16)

def film(x,y,w=300,h=155):
 box(x,y,w,h,'#24343c','#24343c',False)
 for xx in range(int(x+8),int(x+w-10),24):
  box(xx,y+6,12,7,'#ffffff','#ffffff',False);box(xx,y+h-13,12,7,'#ffffff','#ffffff',False)
 for i in range(3):
  box(x+13+i*(w-26)/3,y+26,(w-35)/3,h-52,'#f4fafb','#f4fafb',False)
  circ(x+32+i*(w-26)/3,y+52,11,PALE[i],BLUE)
  line([(x+25+i*(w-26)/3,y+92),(x+60+i*(w-26)/3,y+92)],BLUE)

def image(p,x,y,w,h):
 p=Path(p);im=Image.open(p).convert('RGB');r=min(w/im.width,h/im.height);ww=im.width*r;hh=im.height*r
 # Keep original bytes embedded: the document is portable.
 raw=p.read_bytes();fid=hashlib.sha1(raw).hexdigest();F[fid]=dict(id=fid,mimeType='image/png',dataURL='data:image/png;base64,'+base64.b64encode(raw).decode(),created=1,lastRetrieved=1)
 return el('image',x+(w-ww)/2,y+(h-hh)/2,ww,hh,fileId=fid,status='saved',scale=[1,1],crop=None,customData={'sourcePath':str(p.relative_to(ROOT))})

# Cover: an editorial whiteboard, no enclosing dashboard shell.
text(90,48,'把制作过程，画成能看懂的故事',54)
line([(92,128),(1180,121)],'#f3d876',sw=12)
text(92,161,'12 种表达形式  /  20 类可复用组件  /  一张可继续生长的画布',26,MUTED)
text(92,205,'用顺序讲推进，用画面讲变化，用对照讲选择，用批注讲判断。',25)
badge(2015,75,'表达形式原型',PALE[0],PURPLE,23)
text(1990,131,'内容取自课程制作经历\n线稿为示意；原始图片单独标记',20,MUTED)

# 01 Detailed journey.
title(1,90,300,'图文阶段路径','沿着做事顺序读，每一站都写清用户要求、AI 操作与具体产出。','适用：视频 VH → VI → VJ → VK → VL；同样适合 PPT 逐块接入')
xs=[95,600,1105,1610,2115];ys=[490,510,484,516,494]
labels=['先看几个方向','把变化摊开来看','留下明确基准','交接后进入制作','播放后定位返修']
for i,(x,y) in enumerate(zip(xs,ys)):
 paper(x,y,390,465,PALE[i]);text(x+24,y+20,f'{i+1}  {labels[i]}',27)
 line([(x+23,y+64),(x+351,y+62)],[PURPLE,RED,BLUE,GREEN,GOLD][i],sw=2.5)
 line([(x,y+279),(x+390,y+279)],MUTED,dash=True,sw=1)
 if i<4:line([(x+401,y+225),(xs[i+1]-15,ys[i+1]+225)],INK,True)
 if i==0:
  for j in range(3):
   xx=x+22+j*113;box(xx,y+100,99,138,'#f9fcff','#8ba0ae')
   text(xx+9,y+107,chr(65+j),19,[PURPLE,BLUE,GREEN][j])
   if j==0:
    for k in range(3):box(xx+17,y+144+k*23,62,14,PALE[k],PALE[k])
   if j==1:
    for k in range(3):circ(xx+16+k*22,y+166,8,PALE[k],BLUE)
    line([(xx+15,y+196),(xx+81,y+196)],BLUE,True)
   if j==2:
    box(xx+19,y+150,62,63,'#eef8f0',GREEN);box(xx+29,y+160,26,17,PALE[4],GOLD)
  text(x+23,y+301,'用户：同一内容，给几个方向',22)
  text(x+23,y+342,'AI：生成可并排比较的画面',22)
  text(x+23,y+383,'产出：候选方向图',22)
 elif i==1:
  film(x+27,y+107,336,145)
  text(x+23,y+301,'用户：展开镜头的连续变化',22)
  text(x+23,y+342,'AI：将变化组织为连续分镜',22)
  text(x+23,y+383,'产出：可逐格检查的分镜图',22)
 elif i==2:
  image(C/'03-信息输入与工具执行/AI的输入与输出/素材/图片/视觉基准/镜头01_首次输入_十二格_清理版.png',x+30,y+86,330,179)
  text(x+23,y+301,'用户：保留 C，修改后作基准',22)
  text(x+23,y+342,'AI：按反馈改图并保存',22)
  text(x+23,y+383,'产出：视觉基准（上方为原图）',22)
 elif i==3:
  packet(x+93,y+111,205,142)
  text(x+23,y+301,'用户：按选定材料继续制作',22)
  text(x+23,y+342,'AI：依据图片与镜头要求实现',22)
  text(x+23,y+383,'产出：代码与渲染视频',22)
 else:
  window(x+31,y+101,326,160,'播放检查')
  line([(x+59,y+218),(x+325,y+218)],MUTED,sw=3)
  circ(x+195,y+210,7,RED,RED);text(x+166,y+164,'1:06',27,RED)
  line([(x+169,y+140),(x+180,y+147),(x+169,y+154),(x+169,y+140)],BLUE)
  text(x+23,y+301,'用户：报时间点与缺失变化',22)
  text(x+23,y+342,'AI：定位对应片段并返修',22)
  text(x+23,y+383,'产出：返修版本，待播放核对',22)
note(319,925,'把抽象偏好\n变成可比较的画面',PALE[0],205)
note(1327,914,'采用的是\n修改后的 C',PALE[4],180)
line([(2305,985),(2305,1060),(1778,1060),(1778,1001)],RED,True,dash=True)
text(1873,1074,'返修回到制作环节',21,RED)

# 02 Parallel four-case discussion.
title(2,90,1210,'四格案例＋判断便签','并列看四种制作难点；没有先后顺序，就不强加箭头。','适用：四条主线复盘；类似参考图中的候选人讨论区')
case_data=[('地形｜因果错位','小球走过后才出现沟壑','先塑形，再移动',PALE[0]),('视频｜变化缺失','相邻画面没有新增信息','指出哪一格\n应增加什么',PALE[1]),('网页｜版本丢失','整理后正式网站被简化','回查源码和构建产物',PALE[2]),('PPT｜复用失真','套用结构后，对话与动画错配','分别编排 A / B\n再逐项核对',PALE[3])]
for i,(head,body,nt,co) in enumerate(case_data):
 x=100+(i%2)*598;y=1390+(i//2)*335
 paper(x,y,518,267,co,True);text(x+23,y+17,head,28)
 if i==0:terrain(x+26,y+88,229,105,2)
 elif i==1:film(x+30,y+87,240,119)
 elif i==2:
  window(x+30,y+81,230,123,'阅读网页')
  box(x+40,y+121,45,70,'#dceef8','#dceef8')
  for yy in range(3):line([(x+98,y+128+yy*24),(x+237,y+128+yy*24)],BLUE)
 else:
  for j in range(3):
   box(x+30+j*82,y+92,68,86,'#f6f1fc',PURPLE);text(x+48+j*82,y+118,['A','B','A/B'][j],23,PURPLE)
 text(x+23,y+223,body,20)
 note(x+294,y+96,nt,co,207,angle=.025 if i%2 else -.018)
text(111,2078,'读法：先看发生了什么，再看旁边的判断。便签是提炼，不冒充原话。',20,MUTED)

# 03 four panels with actual evolving objects.
title(3,1400,1210,'连续分镜','同一个对象跨格保留，让读者看见改变发生在哪一步。','适用：地形 TC → TD → TB；视频 VH 的相邻帧检查｜线稿示意')
for i in range(4):
 x=1420+(i%2)*550;y=1390+(i//2)*335
 box(x,y,500,248,'#ffffff','#7c949f',False)
 text(x+18,y+14,f'0{i+1}',25,BLUE)
 text(x+81,y+17,['原来的错误顺序','先输入语义条件','条件先改变地形','小球再沿地形移动'][i],24)
 terrain(x+53,y+99,380,107,[0,0,1,2][i])
 if i==1:badge(x+190,y+71,'先给条件',PALE[0],PURPLE,18)
 text(x+18,y+263,['误读：走过才留下沟壑','原因出现，等待地形响应','小球仍留在原位置','比较对象位置与地形状态'][i],19,RED if i==0 else MUTED)
line([(1935,1514),(1955,1514)],INK,True)
line([(2450,1695),(2450,1709),(1460,1709),(1460,1720)],MUTED,True)
line([(1935,1849),(1955,1849)],INK,True)
text(1420,2078,'四格是有方向的连续事件；左侧四格是无方向的并列案例。',20,GREEN)

# Remaining nine: deliberately different internal structures.
# 04 candidate gallery
title(4,90,2210,'候选画廊','同一任务、不同表达，先看差异再选择。','适用：PPT PI｜投入章节的 A / B / C 候选；未标为最终采用')
for i,(nm,fn) in enumerate([('A 数据地图','投入控制-分镜-A-数据地图.png'),('B 任务工作台','投入控制-分镜-B-任务工作台.png'),('C 决策路径','投入控制-分镜-C-决策路径.png')]):
 x=100+i*273;y=2400+(18 if i==1 else 0)
 paper(x,y,245,238,PALE[i]);image(C/'06-行动选择与投入控制/素材'/fn,x+10,y+10,225,169)
 text(x+12,y+194,nm,20)
line([(115,2690),(115,2705),(884,2705),(884,2690)],PURPLE)
text(205,2728,'比较：结构、变化、重点分别怎样呈现？',22,PURPLE)
#05 before after
title(5,980,2210,'选定图 ↔ 实现图','把依据和产物放在同一尺度下检查。','适用：PPT PK｜第 37 页；两张均为原始历史图')
for j,fn in enumerate(['37页-用户选定生图.png','37页-HTML历史渲染.png']):
 x=997+j*420;y=2425
 text(x,y-36,['选定画面','HTML 历史渲染'][j],23,BLUE)
 paper(x,y,388,230,PALE[j+2]);image(C/'PPT课程制作复盘/证据/关键画面'/fn,x+6,y+6,376,216)
line([(1389,2540),(1410,2540)],BLUE,True)
note(1195,2675,'看布局与文案是否保留；\n功能仍需实际操作验证。',PALE[4],325)
#06 decision loop
title(6,1870,2210,'判断分支＋返修回路','只有会改变下一步的条件，才画成分叉。','适用：地形 TF → TG → TE｜页面改造后的判断')
box(1890,2438,160,79,'#edf5fa',BLUE);text(1910,2463,'尝试改造',26)
el('diamond',2105,2389,206,182,backgroundColor='#fff7da',strokeColor=GOLD)
text(2154,2449,'保住\n原设计？',23)
line([(2056,2477),(2100,2477)],INK,True)
box(2392,2375,190,78,'#eaf5ed',GREEN);text(2414,2397,'接入 PPT',26)
line([(2295,2435),(2344,2414),(2381,2414)],GREEN,True);text(2325,2371,'是',20,GREEN)
box(2389,2578,194,98,'#fff0e9',RED);text(2412,2600,'回退并限定\n修改范围',23)
line([(2286,2538),(2340,2628),(2378,2628)],RED,True);text(2314,2570,'否',20,RED)
box(1890,2628,234,77,'#eaf5ed',GREEN);text(1906,2651,'继续完善素材',24,GREEN)
line([(2486,2689),(2486,2787),(2007,2787),(2007,2717)],RED,True,dash=True)
line([(1972,2617),(1972,2529)],GREEN,True)
text(2130,2742,'回到素材完善',22,RED)
#07 annotated screen
title(7,90,2935,'操作界面＋局部批注','把反馈钉在位置上，观众才知道改什么。','适用：视频 VL｜时间点反馈；下面是界面示意')
window(111,3110,551,301,'视频检查 · 示意')
box(129,3154,514,178,'#eff5f8','#eff5f8')
box(162,3189,142,90,'#dceef8',BLUE);text(178,3215,'已有输入',24,BLUE)
box(422,3189,177,90,'#fff3d1',GOLD,strokeStyle='dashed');text(437,3215,'新增内容？',24,GOLD)
line([(316,3234),(407,3234)],BLUE,True)
line([(148,3363),(625,3363)],MUTED,sw=4);circ(423,3355,8,RED,RED)
text(400,3381,'1:06',18,RED)
circ(451,3157,75,'transparent',RED)
line([(593,3198),(684,3170),(715,3170)],RED,True)
note(706,3118,'变化缺失\n报时间点\n说预期画面',PALE[4],167)
text(111,3452,'定位 → 问题 → 预期变化',24,RED)
#08 lanes
title(8,980,2935,'泳道与素材交接','看四条工作线怎样汇合，避免误读成串行。','适用：T / V / W / P 间的虚线交接；主流程仍在各自泳道')
for i,(name,co) in enumerate(zip(['地形','视频','网页','PPT'],[PALE[2],PALE[0],PALE[3],PALE[4]])):
 y=3124+i*83;box(996,y,817,71,co,co);text(1009,y+19,name,22)
for x,y,s in [(1100,3134,'校正 A/B'),(1230,3217,'视频＋字幕'),(1420,3300,'选定文章'),(1560,3383,'课件整合')]:
 box(x,y,180,50,'#ffffff',MUTED);text(x+14,y+10,s,20)
line([(1290,3160),(1697,3160),(1697,3375)],BLUE,True,dash=True)
line([(1423,3242),(1645,3242),(1645,3375)],PURPLE,True,dash=True)
line([(1510,3356),(1510,3410),(1550,3410)],GREEN,True,dash=True)
text(998,3470,'虚线只表示材料流向；不代表四条线依次发生。',21,MUTED)
#09 handoff exploded package
title(9,1870,2935,'材料包拆解','交给下一步的东西，展开到能逐项核对。','适用：视频 VJ → VK｜材料名称取自制作记录')
packet(1910,3220,230,165)
for x,y,s,col in [(2247,3124,'选定图片',BLUE),(2390,3282,'镜头要求',PURPLE),(2231,3430,'对应提示词',GREEN)]:
 doc(x,y,76,92,col)
 text(x+89,y+27,s,23,col)
 line([(2152,3300),(x-12,y+48)],col,True)
note(1920,3466,'换任务时，交接选择结果。',PALE[4],291)
#10 temporal version
title(10,90,3655,'版本演进带','只展示已采用版本的变化，解释成品怎样长大。','适用：PPT PE → PM｜来自指南的页数记录')
line([(143,3950),(834,3950)],MUTED,True,sw=2)
for i,(v,s) in enumerate([('10','选定底稿'),('11','第二段视频'),('35','八组案例'),('42','投入章节'),('44','补开场过渡')]):
 x=118+i*165
 for j in range(3):box(x+8-j*4,3871+j*5,113,67,'#ffffff','#c2cbd1')
 text(x+28,3890,v,32,BLUE);circ(x+43,3944,7,PALE[i],BLUE)
 text(x-7,3983,s,20)
 if i:badge(x+5,4040,['','+1','+24','净增 7','+2'][i],PALE[i],MUTED,17)
text(113,4139,'42 页阶段：8 页原型替换 1 页引入，净增 7 页。',21,MUTED)
#11 zoom mechanism
title(11,980,3655,'局部放大与结构拆解','总图保持简洁，复杂细节放在旁边展开。','适用：视频 VH / VJ｜借用首次输入的工具定义讲解；示意')
box(1008,3857,317,269,'#f5fafc',BLUE)
for i,(s,co) in enumerate([('用户请求',PALE[2]),('系统指令',PALE[3]),('环境',PALE[0]),('工具定义',PALE[4])]):
 box(1030,3876+i*58,273,42,co,co);text(1048,3884+i*58,s,22)
circ(1156,4022,47,'transparent',GOLD)
line([(1260,4066),(1414,3959)],GOLD,True)
box(1434,3859,369,275,'#fffdf4',GOLD)
text(1460,3878,'工具定义里有什么？',25,GOLD)
for i,s in enumerate(['名称：能调用哪个工具','说明：工具用来做什么','参数：需要哪些输入']):
 circ(1461,3940+i*55,5,PALE[4],GOLD);text(1484,3928+i*55,s,21)
text(1008,4170,'放大框要与原位置相连，保留整体与局部的对应。',21,MUTED)
#12 2D decision matrix
title(12,1870,3655,'二维决策矩阵','解释两种独立条件怎样影响投入，而非只有四个盒子。','适用：PPT PI / PJ｜以下为策略示意，不是历史评分')
line([(1971,4162),(1971,3851)],MUTED,True)
line([(1971,4162),(2548,4162)],MUTED,True)
text(1890,3814,'下一轮投入 ↑',19,MUTED);text(2270,4191,'判断依据更充分 →',19,MUTED)
line([(2230,3880),(2230,4161)],'#b5c0c5',dash=True)
line([(1970,4030),(2535,4030)],'#b5c0c5',dash=True)
for x,y,w,h,co in [(1984,3878,232,141,PALE[1]),(2244,3878,274,141,PALE[3]),(1984,4043,232,103,PALE[4]),(2244,4043,274,103,PALE[2])]:box(x,y,w,h,co,co)
text(2001,3900,'先缩小范围',25,RED);text(2001,3945,'依据不足，整段做完\n会放大返工',19)
text(2261,3900,'分段推进',25,GREEN);text(2261,3945,'已有参照与验收点\n再扩大下一步投入',19)
text(2001,4055,'先比较样稿',24,GOLD);text(2001,4095,'用小产物补依据',19)
text(2261,4055,'先验证一处',24,BLUE);text(2261,4095,'检查具体修改是否成立',19)

# Component inventory: actual reusable samples, 20 types / 4 families.
G='inventory'
line([(90,4330),(2590,4330)],'#becbd1',dash=True)
text(90,4390,'20 类组件，组合成上面的 12 种表达',38)
text(91,4450,'组件按用途复用；颜色、阴影、胶带和线型是样式变体，不另算类型。',23,MUTED)
component_names=['章节锚点','阶段卡','输入文档','动作标签','原始图像','分镜画格','候选缩略卡','对照括号','界面窗口','定位热点','判断便签','决策菱形','状态徽标','材料包','工作泳道','时间刻度','版本叠页','结构层','关系连线','证据入口']
for i,name in enumerate(component_names):
 G=f'component-{i+1:02}';col=i%10;row=i//10;x=95+col*251;y=4540+row*245
 text(x,y+172,f'{i+1:02}  {name}',21)
 if i==0:circ(x+50,y+50,32,PALE[0],PALE[0]);text(x+64,y+66,'01',24);line([(x+20,y+131),(x+177,y+126)],PURPLE,sw=5)
 elif i==1:paper(x+22,y+19,161,137,PALE[2]);text(x+35,y+35,'一个阶段',21);line([(x+22,y+80),(x+183,y+80)],MUTED,dash=True);text(x+31,y+99,'用户 / AI / 产出',16)
 elif i==2:doc(x+56,y+20,87,122,BLUE)
 elif i==3:badge(x+20,y+64,'先比较画面',PALE[0],PURPLE,22)
 elif i==4:image(C/'PPT课程制作复盘/证据/关键画面/37页-用户选定生图.png',x+8,y+33,190,111)
 elif i==5:film(x+4,y+30,209,115)
 elif i==6:
  for j in range(3):box(x+5+j*70,y+40,61,96,'#ffffff',[PURPLE,BLUE,GREEN][j]);text(x+20+j*70,y+69,chr(65+j),23)
 elif i==7:line([(x+14,y+72),(x+14,y+105),(x+198,y+105),(x+198,y+72)],BLUE);text(x+43,y+39,'同尺度比较',20)
 elif i==8:window(x+8,y+29,203,116,'界面')
 elif i==9:circ(x+61,y+39,44,'transparent',RED);line([(x+126,y+107),(x+184,y+139)],RED,True)
 elif i==10:note(x+9,y+29,'判断与理由',PALE[4],184)
 elif i==11:el('diamond',x+18,y+22,176,131,backgroundColor=PALE[4],strokeColor=GOLD);text(x+76,y+69,'是否？',21)
 elif i==12:badge(x+42,y+53,'已采用',PALE[3],GREEN,23);badge(x+43,y+103,'待核对',PALE[4],GOLD,19)
 elif i==13:packet(x+10,y+27,200,126)
 elif i==14:
  for j in range(3):box(x+3,y+25+j*40,210,31,PALE[j],PALE[j]);text(x+16,y+30+j*40,['地形','视频','PPT'][j],17)
 elif i==15:
  line([(x+8,y+95),(x+208,y+95)],BLUE,True)
  for j in range(3):line([(x+26+j*75,y+83),(x+26+j*75,y+107)],BLUE);text(x+10+j*75,y+115,['0:28','1:06','1:28'][j],17)
 elif i==16:
  for j in range(3):box(x+39-j*9,y+31+j*10,132,83,'#ffffff',BLUE)
  text(x+62,y+79,'44 页',24,BLUE)
 elif i==17:
  for j in range(3):box(x+27+j*10,y+30+j*38,147,30,PALE[j],MUTED)
 elif i==18:
  line([(x+6,y+53),(x+201,y+53)],BLUE,True);line([(x+6,y+102),(x+201,y+102)],GREEN,True,True);line([(x+184,y+127),(x+184,y+148),(x+9,y+148)],RED,True)
 else:
  badge(x+4,y+45,'原始素材',PALE[2],BLUE,21);text(x+7,y+106,'VJ · 材料交接 ↗',20,BLUE,link='../课程制作路径图.md')

G='sources'
text(92,5090,'怎样放回课程路径图？',33)
for i,(s,ss,co) in enumerate([('地形线','路径＋分镜＋局部放大＋返修回路',BLUE),('视频线','图文阶段＋候选画廊＋材料包＋时间批注',PURPLE),('网页线','判断分支＋产物对照＋版本演进',GREEN),('PPT 线','四格案例＋候选比较＋泳道汇合＋决策矩阵',GOLD)]):
 y=5160+i*55;badge(95,y,s,'#f0f4f6',co,20);text(260,y+3,ss,23)
text(1450,5100,'统一读法',29)
line([(1457,5170),(1560,5170)],INK,True);text(1582,5154,'实线：采用路径 / 顺序',23)
line([(1457,5220),(1560,5220)],GREEN,True,True);text(1582,5204,'虚线：素材交接',23)
line([(1457,5270),(1560,5270)],RED,True,True);text(1582,5254,'红色回路：修改 / 回退',23)
text(1450,5320,'无连接线：并列比较；便签：判断及理由。',22,MUTED)
text(94,5420,'来源：课程制作路径图.md、PPT与视频构建指南.md、生图与分镜证据.md。',20,MUTED)
text(94,5459,'本画布是表达形式原型：示意界面与线稿不是历史截图；原始素材内嵌，文字和图形可单独编辑。',20,MUTED)

D.mkdir(exist_ok=True)
scene={'type':'excalidraw','version':2,'source':'https://excalidraw.com','elements':E,'appState':{'viewBackgroundColor':'#ffffff','gridSize':None,'zoom':{'value':.43},'scrollX':15,'scrollY':-240},'files':F}
(D/'课程制作路径图-表达形式原型.excalidraw').write_text(json.dumps(scene,ensure_ascii=False,separators=(',',':')))
(D/'组件与表达形式索引.json').write_text(json.dumps({'expressions':MODULES,'components':[{'id':i+1,'name':v} for i,v in enumerate(component_names)],'notes':'原型示意，不是完整历史路径；原始素材内嵌。'},ensure_ascii=False,indent=2))

# Deterministic visual proof of the stored scene; same coordinates, fonts and embedded images.
def render(path,region,scale=1):
 ox,oy,ww,hh=region;out=Image.new('RGB',(round(ww*scale),round(hh*scale)),'white');draw=ImageDraw.Draw(out)
 def xy(x,y):return ((x-ox)*scale,(y-oy)*scale)
 def stroke(ps,fill,width,dashed=False):
  pp=[xy(*p) for p in ps]
  if not dashed:draw.line(pp,fill=fill,width=max(1,round(width*scale)),joint='curve');return
  for a,b in zip(pp,pp[1:]):
   ln=math.dist(a,b);n=max(1,int(ln/6))
   for j in range(0,n,2):draw.line([(a[0]+(b[0]-a[0])*j/n,a[1]+(b[1]-a[1])*j/n),(a[0]+(b[0]-a[0])*min(j+1,n)/n,a[1]+(b[1]-a[1])*min(j+1,n)/n)],fill=fill,width=max(1,round(width*scale)))
 for e in E:
  x,y,w,h=[e[k] for k in ('x','y','width','height')];tp=e['type'];sc=e['strokeColor'];bg=e['backgroundColor'];fill=None if bg=='transparent' else bg;sw=max(1,round(e['strokeWidth']*scale));bounds=[xy(x,y),xy(x+w,y+h)]
  if tp not in ['line','arrow'] and (x+w<ox or y+h<oy or x>ox+ww or y>oy+hh):continue
  if tp=='rectangle':
   if e['roundness']:draw.rounded_rectangle(bounds,radius=min(13*scale,w*scale/5,h*scale/5),fill=fill,outline=sc,width=sw)
   else:draw.rectangle(bounds,fill=fill,outline=sc,width=sw)
  elif tp=='ellipse':draw.ellipse(bounds,fill=fill,outline=sc,width=sw)
  elif tp=='diamond':draw.polygon([xy(x+w/2,y),xy(x+w,y+h/2),xy(x+w/2,y+h),xy(x,y+h/2)],fill=fill,outline=sc,width=sw)
  elif tp=='text':
   f=ImageFont.truetype(FONT,round(e['fontSize']*scale))
   for i,l in enumerate(e['text'].split('\n')):draw.text(xy(x,y+i*e['fontSize']*e['lineHeight']),l,font=f,fill=sc)
  elif tp in ['line','arrow']:
   ps=[(x+a,y+b) for a,b in e['points']];stroke(ps,sc,e['strokeWidth'],e['strokeStyle']!='solid')
   if e.get('endArrowhead')=='arrow':
    a,b=ps[-2:];an=math.atan2(b[1]-a[1],b[0]-a[0]);stroke([(b[0]-12*math.cos(an-.42),b[1]-12*math.sin(an-.42)),b,(b[0]-12*math.cos(an+.42),b[1]-12*math.sin(an+.42))],sc,e['strokeWidth'])
  elif tp=='image':
   raw=base64.b64decode(F[e['fileId']]['dataURL'].split(',',1)[1]);im=Image.open(io.BytesIO(raw)).convert('RGB');im=im.resize((max(1,round(w*scale)),max(1,round(h*scale))),Image.Resampling.LANCZOS);out.paste(im,tuple(round(z) for z in xy(x,y)))
 out.save(path)
render(D/'课程制作路径图-表达形式总览.png',(45,10,2620,5510),.75)
render(D/'01-图文阶段路径.png',(50,270,2570,890),1)
render(D/'02-四格案例与连续分镜.png',(50,1170,2560,1000),1)
for j,yy in enumerate([2170,2895,3615,4350]):render(Path('/tmp')/f'表达形式检查-{j+1}.png',(45,yy,2600,730),.85)

# Six component close-ups, reusing editable scene elements rather than rebuilding their pictures.
original_elements=E
E=[]
showcase=[(4,(70,2200,870,625)),(5,(960,2200,875,625)),(6,(1850,2200,780,625)),(7,(70,2920,870,650)),(9,(1850,2920,780,675)),(11,(960,3640,875,650))]
for j,(n,(sx,sy,sw,sh)) in enumerate(showcase):
 dx=25+(j%2)*930;dy=25+(j//2)*725
 for original in original_elements:
  if original['groupIds']!=[f'module-{n:02}']:continue
  shifted=dict(original);shifted['x']=original['x']-sx+dx;shifted['y']=original['y']-sy+dy;E.append(shifted)
render(D/'其他六种组件-放大展示.png',(0,0,1860,2200),1)
E=[e for e in original_elements if e['groupIds']==['module-01'] and e['type']!='arrow' and 90<=e['x']<535 and 480<=e['y']<1040]
render(D/'用户-AI-产出阶段卡.png',(72,463,463,594),1.4)
E=original_elements

assert len({e['id'] for e in E})==len(E)
assert all(e['fileId'] in F for e in E if e['type']=='image')
print(json.dumps({'elements':len(E),'embeddedImages':len(F),'expressions':len(MODULES),'components':len(component_names),'file':str(D/'课程制作路径图-表达形式原型.excalidraw')},ensure_ascii=False))
