from pathlib import Path
import json, math, re, base64, hashlib, html, copy, sys
from PIL import Image, ImageDraw, ImageFont
ROOT=Path('/Users/w/code/For-Use-AI')
OUT=Path(__file__).parent
FONT='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
E=[]; FILES={}; META=[]; group='cover'; n=0
INK='#263545'; GRAY='#637084'; BLUE='#d9eaff'; GREEN='#dbf2e5'; PURPLE='#e8dffc'; PEACH='#ffe6cc'; YELLOW='#fff1ba'; PINK='#f9deeb'
COLORS=[BLUE,PURPLE,GREEN,PEACH]
def el(t,x,y,w,h,**kw):
 global n
 n+=1
 d=dict(id=f'e{n:05}',type=t,x=x,y=y,width=w,height=h,angle=0,strokeColor=INK,backgroundColor='transparent',fillStyle='solid',strokeWidth=1.6,strokeStyle='solid',roughness=0.8,opacity=100,groupIds=[group],frameId=None,roundness=None,seed=n*71,version=1,versionNonce=n*13,isDeleted=False,boundElements=None,updated=1790208000000,link=None,locked=False)
 d.update(kw);E.append(d);return d

def rect(x,y,w,h,fill='white',stroke=INK,rounded=True,dash=False):
 return el('rectangle',x,y,w,h,backgroundColor=fill,strokeColor=stroke,roundness={'type':3} if rounded else None,strokeStyle='dotted' if dash else 'solid')
def line(points,color=INK,dash=False,arrow=False):
 x,y=points[0];p=[[a-x,b-y] for a,b in points]
 return el('arrow' if arrow else 'line',x,y,max(a for a,b in p)-min(a for a,b in p),max(b for a,b in p)-min(b for a,b in p),points=p,strokeColor=color,strokeStyle='dashed' if dash else 'solid',startBinding=None,endBinding=None,startArrowhead=None,endArrowhead='arrow' if arrow else None,lastCommittedPoint=None)
def txt(x,y,s,size=23,color=INK,width=None):
 f=ImageFont.truetype(FONT,size)
 if width:
  ls=[]
  for para in s.split('\n'):
   a=''
   for c in para:
    if a and f.getlength(a+c)>width: ls.append(a);a=c
    else:a+=c
   ls.append(a)
  s='\n'.join(ls)
 ls=s.split('\n');w=max(f.getlength(a) for a in ls)+3;h=len(ls)*size*1.3
 return el('text',x,y,w,h,text=s,originalText=s,fontSize=size,fontFamily=2,textAlign='left',verticalAlign='top',containerId=None,autoResize=True,lineHeight=1.3,baseline=size)
def card(x,y,w,h,title,fill=BLUE):
 rect(x+7,y+7,w,h,fill,fill);rect(x,y,w,h)
 txt(x+18,y+15,title,23);line([(x+18,y+49),(x+w-18,y+49)],fill)
def note(x,y,w,h,s,fill=YELLOW):
 rect(x+4,y+5,w,h,'#e8e8e8','#e8e8e8',False)
 rect(x,y,w,h,fill,INK,False);txt(x+12,y+12,s,20,width=w-24)
def pill(x,y,s,fill=BLUE,w=None):
 w=w or ImageFont.truetype(FONT,19).getlength(s)+26
 rect(x,y,w,36,fill,fill);txt(x+12,y+5,s,19);return w
def arrow(x,y,x2,y2,label=None):
 line([(x,y),(x2,y2)],arrow=True)
 if label:txt((x+x2)/2-45,(y+y2)/2-31,label,18,GRAY)
def doc(x,y,w,h,title,fill=BLUE,lines=4):
 rect(x+5,y+5,w,h,fill,fill,False);rect(x,y,w,h,'white',INK,False)
 txt(x+12,y+12,title,21,width=w-24)
 for k in range(lines):line([(x+14,y+55+k*21),(x+w-16-(k%2)*25,y+55+k*21)],'#b7c1ce')
def browser(x,y,w,h,title):
 rect(x,y,w,h);line([(x,y+36),(x+w,y+36)],'#b7c1ce');txt(x+14,y+7,title,18,GRAY)
 for i in range(3):el('ellipse',x+w-60+i*15,y+14,6,6,backgroundColor=COLORS[i],strokeColor=COLORS[i])
def render_svg(elements,box,path,files=True):
 x,y,w,h=box;ss=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white"/>']
 for e in elements:
  a,b,c,d=e['x'],e['y'],e['width'],e['height'];co=e['strokeColor'];fi=e['backgroundColor'];sty=f'fill="{fi if fi!="transparent" else "none"}" stroke="{co}" stroke-width="{e["strokeWidth"]}"';dash=' stroke-dasharray="4 7"' if e['strokeStyle']!='solid' else ''
  if e['type']=='rectangle':ss.append(f'<rect x="{a}" y="{b}" width="{c}" height="{d}" rx="{12 if e["roundness"] else 0}" {sty}{dash}/>')
  elif e['type']=='ellipse':ss.append(f'<ellipse cx="{a+c/2}" cy="{b+d/2}" rx="{c/2}" ry="{d/2}" {sty}/>')
  elif e['type']=='text':
   for i,s in enumerate(e['text'].split('\n')):ss.append(f'<text x="{a}" y="{b+e["fontSize"]+i*e["fontSize"]*1.3}" font-family="Arial Unicode MS, sans-serif" font-size="{e["fontSize"]}" fill="{co}">{html.escape(s)}</text>')
  elif e['type'] in ['line','arrow']:
   pts=[(a+u,b+v) for u,v in e['points']];ps=' '.join(f'{u},{v}' for u,v in pts);ss.append(f'<polyline points="{ps}" fill="none" stroke="{co}" stroke-width="1.6"{dash}/>')
   if e['type']=='arrow':
    u,v=pts[-1];q,r=pts[-2];ang=math.atan2(v-r,u-q);p=[(u-12*math.cos(ang-.45),v-12*math.sin(ang-.45)),(u,v),(u-12*math.cos(ang+.45),v-12*math.sin(ang+.45))];ss.append(f'<polyline points="{" ".join(f"{u},{v}" for u,v in p)}" fill="none" stroke="{co}" stroke-width="1.6"/>')
  elif e['type']=='image':ss.append(f'<image x="{a}" y="{b}" width="{c}" height="{d}" xlink:href="{FILES[e["fileId"]]["dataURL"]}"/>')
 ss.append('</svg>');path.write_text('\n'.join(ss))
def render_png(elements,box,path,scale=.8):
 bx,by,bw,bh=box;im=Image.new('RGB',(int(bw*scale),int(bh*scale)),'white');dr=ImageDraw.Draw(im)
 for e in elements:
  if e['x']>bx+bw or e['y']>by+bh or e['x']+e['width']<bx or e['y']+e['height']<by:continue
  x=(e['x']-bx)*scale;y=(e['y']-by)*scale;w=e['width']*scale;h=e['height']*scale;co=e['strokeColor'];fi=None if e['backgroundColor']=='transparent' else e['backgroundColor'];sw=max(1,round(e['strokeWidth']*scale))
  if e['type']=='rectangle':dr.rounded_rectangle((x,y,x+w,y+h),radius=10*scale if e['roundness'] else 0,fill=fi,outline=co,width=sw)
  elif e['type']=='ellipse':dr.ellipse((x,y,x+w,y+h),fill=fi,outline=co,width=sw)
  elif e['type']=='text':
   f=ImageFont.truetype(FONT,max(1,int(e['fontSize']*scale)))
   for j,s in enumerate(e['text'].split('\n')):dr.text((x,y+j*e['fontSize']*1.3*scale),s,font=f,fill=co)
  elif e['type'] in ['line','arrow']:
   p=[(x+a*scale,y+b*scale) for a,b in e['points']];dr.line(p,fill=co,width=sw)
   if e['type']=='arrow':
    a,b=p[-1];c,d=p[-2];ang=math.atan2(b-d,a-c);dr.line([(a-12*scale*math.cos(ang-.45),b-12*scale*math.sin(ang-.45)),(a,b),(a-12*scale*math.cos(ang+.45),b-12*scale*math.sin(ang+.45))],fill=co,width=sw)
  elif e['type']=='image':
   import io
   raw=base64.b64decode(FILES[e['fileId']]['dataURL'].split(',')[1]);pic=Image.open(io.BytesIO(raw)).convert('RGB').resize((int(w),int(h)),Image.Resampling.LANCZOS);im.paste(pic,(int(x),int(y)))
 im.save(path)

def start(num,name,question,structure,fields,usage,avoid):
 global group
 idx=num-1;x=80+(idx%2)*1220;y=540+(idx//2)*900
 group=f'meta{num:02}'
 rect(x,y,1120,830,'white','#ccd4de',True,True)
 pill(x+24,y+22,f'{num:02}',COLORS[(idx//4)%4],60)
 txt(x+102,y+22,name,32)
 txt(x+28,y+77,question,23,GRAY,width=1060)
 line([(x+28,y+122),(x+1092,y+122)],COLORS[(idx//4)%4])
 line([(x+28,y+632),(x+1092,y+632)],'#cbd2db',True)
 for i,(k,v) in enumerate([('构成',structure),('替换',fields),('用法',usage)]):
  txt(x+28,y+656+i*48,k,21,GRAY);txt(x+103,y+656+i*48,v,21,width=975)
 META.append(dict(id=f'C{num:02}',name=name,question=question,structure=structure,fields=fields,usage=usage,avoid=avoid,x=x,y=y))
 group=f'C{num:02}'
 return x+30,y+155

def mini(x,y,w,h,kind=0):
 rect(x,y,w,h)
 if kind==0:
  rect(x+15,y+17,w*.36,h-34,BLUE,BLUE)
  for i in range(3):line([(x+w*.47,y+24+i*24),(x+w-16-(i%2)*21,y+24+i*24)],'#7d8a9c')
 elif kind==1:
  rect(x+15,y+17,w-30,(h-34)*.48,BLUE,BLUE)
  for i in range(2):line([(x+17,y+h*.69+i*18),(x+w-25-i*30,y+h*.69+i*18)],'#7d8a9c')
 else:
  el('ellipse',x+18,y+23,65,65,backgroundColor=BLUE)
  for i in range(3):line([(x+100,y+27+i*24),(x+w-18,y+27+i*24)],'#7d8a9c')

def dot(x,y,c=PURPLE,r=22):el('ellipse',x,y,r,r,backgroundColor=c)

# Generic structures, not a retelling of the course.
txt(80,60,'可复用的视觉表达组件',54)
txt(83,143,'22 类组合结构＋4 个布局变体  /  中性示例  /  拖入画布后替换内容',28,GRAY)
for i,(a,b) in enumerate([('材料与动作','收集 · 协作 · 映射 · 标注'),('组织与变化','拆解 · 复用 · 对照 · 分镜'),('比较与关系','时间 · 选择 · 并列 · 汇合'),('判断与交付','确认 · 迭代 · 同步 · 打包')]):
 xx=80+i*605;rect(xx,218,570,124,COLORS[i],COLORS[i]);txt(xx+20,237,a,27);txt(xx+20,286,b,21)
txt(84,385,'先选要表达的关系，再挑组件；外观相近，不代表表达同一种意思。',26)
txt(84,432,'蓝色＝主体内容  ·  紫色＝补充或变化  ·  绿色＝采用或输出  ·  黄色便签＝判断依据',22,GRAY)

x,y=start(1,'材料集合','有哪些输入？怎么分组？下一步能拿到什么？','来源页＋图像缩略图＋分类容器＋交接标签','材料名称、媒体类型、分组依据、去向','多份材料尚无固定先后关系时使用。','不要给并列材料加顺序编号。')
doc(x+17,y+13,239,174,'文字材料',BLUE,4);mini(x+302,y+13,239,174);txt(x+318,y+203,'图像材料',22);doc(x+593,y+13,239,174,'要求与约束',PURPLE,4)
rect(x+21,y+290,1001,123,'#f7f9fc','#cbd4df',False);txt(x+42,y+304,'按用途归集',24)
for i,a in enumerate(['内容依据','视觉参考','执行条件']):pill(x+45+i*323,y+357,a,[BLUE,PURPLE,GREEN][i],280)
for xx in [137,421,718]:arrow(x+xx,y+230,x+xx,y+283)
note(x+866,y+19,157,150,'保留来源\n说明用途\n再交接',YELLOW)

x,y=start(2,'用户 / AI / 产出阶段卡','一次协作里，谁判断、谁执行、留下什么？','阶段标题＋产物预览＋三行分工＋判断便签','阶段名称、用户动作、AI动作、可见产物','解释一个阶段；多个阶段可横向连接。','只在涉及分工时使用，不强制套用所有组件。')
card(x+130,y+4,676,409,'阶段：从要求到一份可查看的样例',BLUE)
mini(x+153,y+78,240,147);txt(x+424,y+98,'产物预览',24);txt(x+424,y+146,'一张图 / 一段文字\n一个可操作样例',22)
for i,(k,v) in enumerate([('用户：','提供要求，查看并作出判断'),('AI：','依据要求生成样例'),('产出：','可确认、可交接的一份结果')]):
 yy=y+257+i*46;line([(x+152,yy-9),(x+782,yy-9)],'#cad4df',True);txt(x+156,yy,k,22);txt(x+250,yy,v,22)
note(x+839,y+240,189,124,'判断依据\n放在结果旁边',YELLOW)

x,y=start(3,'概念 → 图形映射','抽象含义，分别用什么视觉变量来表达？','含义列＋对应关系＋图形样本＋变量说明','概念、视觉符号、映射依据、参数','解释文字如何转成图形；每行对应一种关系。','不要凭图形好看就建立未经说明的对应。')
for i,(a,b) in enumerate([('数量','大小'),('类别','颜色'),('顺序','位置')]):
 yy=y+15+i*132;pill(x+18,yy+23,a,BLUE,232);arrow(x+270,yy+41,x+397,yy+41)
 if i==0:
  for j,r in enumerate([20,34,50]):dot(x+438+j*94,yy+45-r/2,PURPLE,r)
 elif i==1:
  for j,c in enumerate([BLUE,PURPLE,GREEN]):dot(x+439+j*94,yy+22,c,42)
 else:
  for j in range(3):pill(x+416+j*97,yy+25,str(j+1),GREEN,65)
 txt(x+795,yy+28,b,25)
note(x+19,y+416,1006,48,'一行讲清一种映射；复杂关系可以另接一个局部放大组件。',YELLOW)

x,y=start(4,'界面标注与局部放大','读者该看哪里？点哪里？哪一个细节需要放大解释？','界面壳＋焦点框＋引线＋放大区＋操作提示','截图或线框、标注位置、操作动作、放大细节','适合解释按钮、参数和界面变化。','标注具体位置，避免便签遮住被解释的对象。')
browser(x+20,y+15,652,376,'界面示例')
mini(x+47,y+82,328,228,1)
txt(x+415,y+99,'显示密度',23);line([(x+414,y+153),(x+624,y+153)],GRAY);dot(x+495,y+144,PURPLE,18);pill(x+415,y+233,'应用',GREEN,198)
rect(x+399,y+83,241,95,'transparent','#9375ba',False,True)
line([(x+647,y+132),(x+739,y+90)],'#9375ba')
rect(x+760,y+23,260,162,PURPLE,PURPLE);txt(x+779,y+42,'局部放大',23);line([(x+785,y+126),(x+990,y+126)],INK);dot(x+874,y+114,'white',24)
note(x+768,y+250,250,117,'① 调整滑杆\n② 查看变化\n③ 确认应用',YELLOW)

x,y=start(5,'整体拆解与分层','一个整体由哪些部分组成？每一层承担什么作用？','整体预览＋拆解引线＋分层模块＋职责说明','整体对象、层次、组成部分、各层职责','用于结构拆解；同层对象保持同级排布。','层次表示组成关系，不代表执行顺序。')
mini(x+20,y+65,341,256,0);pill(x+94,y+352,'整体对象',BLUE,198)
for i,(a,b,c) in enumerate([('内容层','信息与重点',BLUE),('表达层','图像与布局',PURPLE),('操作层','动作与反馈',GREEN)]):
 yy=y+12+i*142;rect(x+528,yy,486,108,c,c);txt(x+550,yy+14,a,25);txt(x+550,yy+60,b,22)
 line([(x+374,y+194),(x+451,y+194),(x+451,yy+52),(x+519,yy+52)],arrow=True)

x,y=start(6,'共用规则与一对多复用','同一份规则，如何支持多个独立的实例？','共用规范＋虚线调用关系＋多个实例＋差异便签','可复用规则、使用对象、共用部分、独立内容','统一样式、方法或模板时使用。','复用的是规则；每份实例的内容仍单独填写。')
card(x+265,y+6,532,115,'共用规则',PURPLE);txt(x+286,y+68,'结构 / 样式 / 检查要求',24)
for i,t in enumerate(['实例 A','实例 B','实例 C']):
 xx=x+10+i*352;line([(x+530,y+128),(xx+162,y+205)],'#9076ae',True,True);mini(xx,y+215,323,163,i);pill(xx+55,y+399,t,GREEN,207)
note(x+18,y+16,194,143,'固定：规则\n变化：内容',YELLOW)

x,y=start(7,'前后对照','同一对象，改动之前与之后有什么可见区别？','同尺寸双画面＋变化箭头＋差异标记＋保留说明','前态、后态、变化点、保留部分','解释一次修改、一次整理或一次转换。','必须对照同一对象；不同方案改用候选比较。')
for i,t in enumerate(['调整前','调整后']):
 xx=x+17+i*583;txt(xx+99,y+9,t,26);mini(xx,y+60,432,269,i)
arrow(x+469,y+187,x+578,y+187)
rect(x+610,y+107,399,64,'transparent','#9076ae',False,True)
note(x+28,y+375,447,77,'保留：同一份信息内容',BLUE);note(x+600,y+375,427,77,'变化：图文布局与层级',PURPLE)

x,y=start(8,'连续状态 / 分镜','同一个对象，怎样经过几个状态发生变化？','连续画框＋状态编号＋稳定对象＋变化说明','状态数量、出现顺序、变化对象、镜头说明','表达展开、运动、增加或转化；可增减格数。','与四格并列不同，相邻画面有明确前后关系。')
for i,(a,b) in enumerate([('起点','对象出现'),('增加','加入新元素'),('变化','对象移动'),('结果','形成新状态')]):
 xx=x+8+i*265;rect(xx,y+36,240,273,'white',INK,False);pill(xx+13,y+51,f'0{i+1}  {a}',COLORS[i],211)
 dot(xx+42+i*28,y+164,BLUE,49)
 if i>=1:rect(xx+134,y+198,56,56,PURPLE,PURPLE)
 if i==3:line([(xx+124,y+180),(xx+167,y+213)],arrow=True)
 txt(xx+20,y+343,b,22)
 if i<3:arrow(xx+242,y+176,xx+260,y+176)
note(x+18,y+407,1008,52,'重复出现的对象保持颜色与形状一致，用位置、数量或状态表现变化。',YELLOW)

x,y=start(9,'分层时间轨道','多件事何时开始、持续多久、哪里同时发生？','时间方向＋独立轨道＋持续区间＋同步标记','轨道名、时间刻度、开始结束、重叠关系','解释动画、制作安排或多项动作的配合。','轨道表达时间；不用于无时序的组成关系。')
arrow(x+167,y+40,x+1001,y+40);txt(x+783,y+2,'时间推进',21,GRAY)
for i,(t,off,w,c) in enumerate([('主体出现',0,330,BLUE),('补充说明',210,439,PURPLE),('动作反馈',475,325,GREEN)]):
 yy=y+109+i*103;txt(x+12,yy+10,t,23);line([(x+171,yy+35),(x+1010,yy+35)],'#cbd2dc');rect(x+181+off,yy,w,63,c,c)
line([(x+664,y+66),(x+664,y+404)],'#9076ae',True);note(x+446,y+419,427,47,'同一时刻：说明与反馈同时可见',YELLOW)

x,y=start(10,'候选方案比较与选择','同一个目标有几种表达？比较后采用哪一个？','等尺寸候选＋同一比较维度＋选择标记＋选择依据','候选数量、共同内容、比较维度、采用结果','视觉、布局或方案选择；选定后再接执行组件。','不能一边换内容、一边换形式，却只比较外观。')
for i,t in enumerate(['A  左右布局','B  上下布局','C  图标引导']):
 xx=x+10+i*352;txt(xx+51,y+9,t,23);mini(xx,y+61,323,204,i)
 txt(xx+31,y+284,['图文同时查看','先图后文阅读','重点快速定位'][i],21,GRAY)
 if i==1:rect(xx-5,y+55,333,217,'transparent','#639a78',False);pill(xx+84,y+331,'示例采用 B',GREEN,177)
note(x+15,y+397,1008,65,'同一份信息，只比较表达方式；采用理由：符合所需阅读顺序。',YELLOW)

x,y=start(11,'并列四格 / 案例墙','几个同级对象，各有什么特点、用途或观点？','同级小卡＋图文摘要＋独立便签；无顺序箭头','对象数量、标题、图像、特点、评价','分类、案例、能力或材料盘点；可扩成 3 / 6 格。','格子不自动代表象限坐标，也不代表时间先后。')
for i,(a,b) in enumerate([('案例 A','突出信息'),('案例 B','补充解释'),('案例 C','表达关系'),('案例 D','提供操作')]):
 xx=x+8+(i%2)*532;yy=y+6+(i//2)*235;rect(xx,yy,498,213,'white',INK,True,True);txt(xx+17,yy+15,a,23)
 mini(xx+18,yy+61,236,127,i%3);note(xx+282,yy+99,194,94,b,COLORS[i])

x,y=start(12,'多路汇合 / 分流','哪些工作并行推进？交接什么？在哪里形成共同结果？','平行输入＋交接线＋汇合节点＋后续分流','分支数量、分支结果、汇合要求、后续去向','并行内容、素材组合、跨环节交接。','连接点表示依赖，不自动表示现实发生时间。')
for i,(t,c) in enumerate([('文字结果',BLUE),('图像结果',PURPLE),('交互结果',GREEN)]):
 yy=y+23+i*137;pill(x+10,yy,t,c,277);line([(x+297,yy+18),(x+368,yy+18),(x+368,y+175),(x+441,y+175)],arrow=True)
card(x+459,y+92,260,193,'组合产物',PEACH);mini(x+480,y+162,215,101)
for i,t in enumerate(['使用场景 A','使用场景 B']):
 yy=y+80+i*208;line([(x+730,y+184),(x+771,y+184),(x+771,yy+18),(x+823,yy+18)],arrow=True);pill(x+837,yy,t,[BLUE,GREEN][i],204)
txt(x+72,y+425,'多个输入',24,GRAY);txt(x+491,y+425,'共同汇合',24,GRAY);txt(x+836,y+425,'分别使用',24,GRAY)

x,y=start(13,'样例 → 确认 → 扩展','先确认什么，才能继续批量应用或正式接入？','小样预览＋确认依据＋采用箭头＋扩展结果','小样、确认条件、采用状态、扩展对象','原型确认、样式确认、内容接入之前使用。','这是决策关口；不要把“已生成”等同“已确认”。')
mini(x+11,y+106,300,210,0);pill(x+76,y+341,'先做一份样例',BLUE,223)
arrow(x+325,y+209,x+385,y+209)
card(x+403,y+89,283,243,'确认依据',YELLOW);txt(x+426,y+158,'内容对得上\n效果看得清\n操作用得通',24)
arrow(x+700,y+209,x+758,y+209)
for i in range(3):mini(x+799+i*18,y+51+i*76,211,115,0)
pill(x+786,y+364,'确认后再扩展',GREEN,248)

x,y=start(14,'正常反馈与迭代','看过结果后，依据什么调整，再回到哪里检查？','产物预览＋具体观察＋调整项＋有目标的回返线','观察位置、预期变化、调整对象、回返位置','表达主路径中正常的试用和优化。','回返箭头必须落到被修改对象，不能只画一个圆。')
browser(x+12,y+30,460,287,'查看结果');mini(x+37,y+88,410,197,0)
note(x+583,y+41,432,105,'观察：补充说明不够醒目\n预期：更容易被看见',YELLOW)
arrow(x+489,y+143,x+569,y+99)
rect(x+594,y+233,414,83,PURPLE,PURPLE);txt(x+614,y+252,'调整：强化说明的视觉层级',23,width=376)
arrow(x+805,y+156,x+805,y+226)
line([(x+803,y+329),(x+803,y+412),(x+246,y+412),(x+246,y+325)],'#9076ae',True,True);txt(x+407,y+430,'回到同一位置再次查看',22,GRAY)

x,y=start(15,'多轨同步对照','同一步里，画面、解释和操作应该怎样对应？','共同列序＋多条内容轨＋垂直对齐＋衔接提示','阶段、画面、文字说明、动作、其他对应项','演示安排、图文同步、讲述提示或操作指引。','列表示同一时刻或阶段；行数可按需要增减。')
for i,t in enumerate(['画面','说明','操作']):txt(x+8,y+82+i*132,t,23,GRAY)
for i,(a,b,c) in enumerate([('状态 1','解释主体','打开'),('状态 2','说明变化','调整'),('状态 3','总结结果','确认')]):
 xx=x+112+i*316;txt(xx+89,y+8,a,23);mini(xx,y+51,290,104,i)
 for k,s in enumerate([b,c]):rect(xx,y+185+k*131,290,81,[PURPLE,GREEN][k],[PURPLE,GREEN][k]);txt(xx+26,y+211+k*131,s,24)
line([(x+430,y+33),(x+430,y+417)],'#cbd4df',True)
txt(x+155,y+435,'横着看推进过程；竖着看同一步的画面、说明与操作是否一致。',22,GRAY)

x,y=start(16,'交付包 / 组成与入口','最后交什么？哪些文件互相依赖？从哪里开始使用？','主入口＋附件组合＋对应关系＋使用顺序','主要产物、依赖文件、说明材料、使用入口','多文件交付、素材包、成套设计或演示。','不要只列文件名；要让接收者知道文件之间的关系。')
rect(x+323,y+46,390,302,'#f7f9fc','#8da0b5',False);txt(x+395,y+73,'主产物 / 入口',28);mini(x+352,y+139,333,165,0)
for i,(xx,yy,t,c) in enumerate([(x+13,y+6,'内容文件',BLUE),(x+13,y+249,'依赖素材',PURPLE),(x+793,y+6,'使用说明',GREEN),(x+793,y+249,'配套备注',PEACH)]):
 doc(xx,yy,233,166,t,c,4)
 if i<2:arrow(xx+240,yy+78,x+311,y+145+i*129)
 else:arrow(xx-9,yy+78,x+724,y+145+(i-2)*129)
txt(x+352,y+418,'打开主产物 → 配套材料 → 使用说明',22,GRAY)


x,y=start(17,'全局路线与当前位置','整体有几条路线？当前展开的是哪一段？','总览路径＋章节站点＋当前位置＋局部展开','路线名称、章节数量、当前位置、展开内容','长画布、跨章节或多线叙事时使用。','总览保持简洁，细节放到局部展开中。')
for i,a in enumerate(['准备','构建','组合','交付']):
 xx=x+22+i*271;dot(xx+27,y+42,GREEN if i==1 else BLUE,33);txt(xx,y+95,a,24)
 if i<3:arrow(xx+67,y+58,xx+281,y+58)
pill(x+294,y+146,'当前位置',GREEN,180)
line([(x+335,y+187),(x+335,y+240)],GRAY,True,True)
card(x+156,y+251,745,185,'展开这一段',GREEN)
for i,a in enumerate(['形成样例','查看效果','确认结果']):pill(x+180+i*240,y+335,a,[BLUE,PURPLE,GREEN][i],214)

x,y=start(18,'层级树 / 内容骨架','整体怎样分成章节，再分成更小的内容？','根主题＋分层枝干＋同级节点＋层级标记','主题、层数、章节、要点','组织内容大纲、信息架构与目录结构。','树枝表达包含关系，不表达动作先后。')
pill(x+391,y+12,'一个总主题',PEACH,272)
for i,a in enumerate(['部分 A','部分 B','部分 C']):
 xx=x+16+i*351;line([(x+526,y+56),(x+526,y+103),(xx+161,y+103),(xx+161,y+146)])
 pill(xx+15,y+157,a,COLORS[i],290)
 for j,b in enumerate(['要点 1','要点 2']):
  yy=y+255+j*104;line([(xx+45,y+198),(xx+45,yy+18),(xx+81,yy+18)]);pill(xx+91,yy,b,COLORS[i],215)
txt(x+324,y+443,'整体 → 部分 → 要点',24,GRAY)

x,y=start(19,'条件分支','不同条件成立时，分别进入哪条路径？','明确条件＋带标签分支＋分支结果＋可选汇合','判断问题、条件、路径动作、结果','有真实选择规则时使用；每条出口写清条件。','不要把并行工作误画成互斥选择。')
pill(x+22,y+182,'待判断对象',BLUE,260)
arrow(x+296,y+200,x+360,y+200)
line([(x+380,y+200),(x+533,y+96),(x+686,y+200),(x+533,y+304),(x+380,y+200)])
txt(x+442,y+177,'条件是否满足？',23)
for i,(a,b,c) in enumerate([('满足','直接进入下一步',GREEN),('尚不满足','先补充必要材料',YELLOW)]):
 yy=y+65+i*249;line([(x+695,y+200),(x+746,y+200),(x+746,yy+18),(x+803,yy+18)],arrow=True);txt(x+754,yy-28,a,20);pill(x+812,yy,b,c,222)

x,y=start(20,'二维矩阵 / 位置与依据','两个维度同时考虑时，各对象处于什么位置？','具名坐标轴＋四个区域＋对象点＋定位依据','两个维度、方向、对象、定位依据','比较取舍或分布；位置需有可解释的依据。','与并列四格不同，这里的位置承载含义。')
rect(x+147,y+36,603,367,'white','#cad4df',False)
line([(x+448,y+36),(x+448,y+403)],GRAY,True);line([(x+147,y+220),(x+750,y+220)],GRAY,True)
arrow(x+147,y+416,x+777,y+416);arrow(x+133,y+403,x+133,y+12)
txt(x+472,y+436,'投入：低 → 高',23);txt(x+10,y+67,'依据\n充分\n↑\n不足',22)
for dx,dy,t,c in [(255,118,'A',BLUE),(575,139,'B',PURPLE),(356,318,'C',GREEN)]:dot(x+dx,y+dy,c,32);txt(x+dx+43,y+dy,t,23)
note(x+795,y+73,241,189,'B 的位置依据\n投入较高\n可参考材料充分',YELLOW)
line([(x+795,y+222),(x+609,y+158)],GRAY)

x,y=start(21,'证据 → 观察 → 结论','一个判断，具体依据哪份材料的哪个细节？','原始片段＋局部标注＋观察描述＋结论','来源、片段、关注位置、观察与判断','解释选择理由、验收结果或设计判断。','把材料上能看到的事实与自己的推断分开。')
browser(x+13,y+20,488,325,'来源片段 / 中性示意');mini(x+38,y+78,437,235,0)
rect(x+230,y+93,226,105,'transparent','#9171ad',False,True)
line([(x+465,y+141),(x+580,y+105)],GRAY,True)
note(x+599,y+26,420,123,'观察\n主要信息集中在上半区。',BLUE)
arrow(x+808,y+159,x+808,y+214)
card(x+600,y+228,420,143,'判断',GREEN);txt(x+620,y+290,'适合优先阅读核心信息。',22)
pill(x+27,y+390,'来源：样例 01 / 关注区域 A',BLUE,473)

x,y=start(22,'版本演进与采用','经过多轮变化，什么被保留，最终采用哪版？','多版缩略图＋变化说明＋保留项＋采用标记','版本数、每次变化、保留部分、采用状态','连续修改超过两轮时使用；可保留中间关键版本。','最新版本不必然被采用，采用状态需单独标出。')
for i,(a,b) in enumerate([('V1','建立信息结构'),('V2','调整图文布局'),('V3','加强重点提示')]):
 xx=x+10+i*351;txt(xx+119,y+12,a,28);mini(xx,y+66,322,207,i);txt(xx+58,y+298,b,22)
 if i<2:arrow(xx+325,y+177,xx+346,y+177)
 if i==1:pill(xx+73,y+350,'此版采用',GREEN,192)
note(x+15,y+410,1008,51,'共同保留：内容主体。逐轮改变：表达方式。采用标记与版本新旧分开。',YELLOW)

x,y=start(23,'变体示例 / 候选比较','候选数量和主次关系变化时，怎样调整排法？','双图细看 / 主方案突出','候选图片、对比说明、采用理由','作为第 10 类组件的布局变体。','仍然围绕同一目标比较，不增加新的组件类型。')
for i,a in enumerate(['双图细看','主方案突出']):txt(x+35+i*551,y+3,a,25)
for i in range(2):mini(x+15+i*244,y+69,226,207,i);txt(x+59+i*244,y+292,['方案 A','方案 B'][i],22)
note(x+15,y+354,470,89,'适合：两个方案需要逐项对照。',YELLOW)
mini(x+564,y+69,302,249,0);mini(x+883,y+69,148,112,1);mini(x+883,y+205,148,112,2)
pill(x+593,y+337,'重点方案',GREEN,232);txt(x+571,y+402,'适合：一个主方案＋两个备选。',21)

x,y=start(24,'变体示例 / 并列案例','案例数量与重要程度变化时，怎样安排画面？','三列等权 / 一主两辅','案例数量、内容摘要、视觉主次','作为第 11 类组件的布局变体。','视觉面积意味着强调程度，不能无意制造主次。')
txt(x+25,y+4,'三列等权',25);txt(x+570,y+4,'一主两辅',25)
for i in range(3):
 xx=x+10+i*169;rect(xx,y+70,154,246,'white',INK,True,True);txt(xx+16,y+87,f'案例 {i+1}',21);mini(xx+12,y+141,130,146,i)
note(x+14,y+366,494,73,'适合：三个同级对象平等比较。',YELLOW)
rect(x+570,y+69,453,131,'white',INK,True,True);mini(x+583,y+82,165,103,0);txt(x+773,y+124,'主要案例',23)
for i in range(2):mini(x+570+i*237,y+221,215,111,i+1)
txt(x+585,y+395,'适合：一个重点案例＋两个补充。',21)

# Concrete drawings of primitives and assembly recipes on the same canvas.
group='primitives'
txt(80,11430,'12 个基础零件，用来组合上面的结构',40)
prims=['来源页','图片框','窗口壳','便签','角色分工','参数杆','采用标记','持续区间','关系线','交接标签','分组区','局部焦点']
for i,a in enumerate(prims):
 xx=80+(i%6)*405;yy=11520+(i//6)*244;txt(xx,yy,a,23)
 if i==0:doc(xx+5,yy+50,250,139,'材料',BLUE,3)
 elif i==1:mini(xx+5,yy+50,260,137,1)
 elif i==2:browser(xx+5,yy+50,300,137,'界面')
 elif i==3:note(xx+5,yy+50,276,128,'观察 / 判断 / 依据',YELLOW)
 elif i==4:
  for j,b in enumerate(['用户：作出判断','AI：执行动作','产出：留下结果']):txt(xx+5,yy+55+j*43,b,22)
 elif i==5:line([(xx+5,yy+114),(xx+292,yy+114)]);dot(xx+163,yy+103,PURPLE,22)
 elif i==6:pill(xx+5,yy+92,'采用',GREEN,224)
 elif i==7:line([(xx+5,yy+114),(xx+300,yy+114)]);rect(xx+50,yy+90,163,45,PURPLE,PURPLE,False)
 elif i==8:arrow(xx+5,yy+89,xx+292,yy+89);line([(xx+5,yy+150),(xx+292,yy+150)],GRAY,True,True)
 elif i==9:pill(xx+5,yy+92,'文件 / 结果 / 方法',BLUE,292)
 elif i==10:rect(xx+5,yy+53,288,128,'white',GRAY,True,True)
 else:rect(xx+5,yy+53,288,128,'transparent','#9375ba',False,True);line([(xx+219,yy+177),(xx+302,yy+207)],'#9375ba')
group='recipes'
txt(80,12080,'组合方法：结构可以套用，内容可以替换',40)
recipes=[('从材料到结果','01 材料集合 → 02 协作阶段 → 16 交付包'),('从样例到扩展','10 候选比较 → 13 确认关口 → 06 共用规则'),('从变化到表达','03 图形映射 → 08 连续状态 → 09 时间轨道'),('从并行到成套','11 并列盘点 → 12 多路汇合 → 14 整体迭代')]
for i,(a,b) in enumerate(recipes):
 yy=12180+i*118;pill(80,yy,a,COLORS[i],294);txt(414,yy+3,b,25)
txt(82,12700,'组件库只保留可拖用的图形实例；说明文字与外框留在这张展示画布中。',23,GRAY)

# Deliver one atlas and a library of individual vector groups.
data=dict(type='excalidraw',version=2,source='https://excalidraw.com',elements=E,appState={'viewBackgroundColor':'#ffffff','gridSize':None},files={})
(OUT/'通用表达组件-实例画布.excalidraw').write_text(json.dumps(data,ensure_ascii=False))
lib=[]
for m in META:
 es=copy.deepcopy([e for e in E if e['groupIds']==[m['id']]])
 for e in es:e['x']-=m['x']+30;e['y']-=m['y']+155
 lib.append(dict(id=m['id'],status='unpublished',elements=es,created=1790208000000,name=m['name']))
(OUT/'通用表达组件-扩展库.excalidrawlib').write_text(json.dumps(dict(type='excalidrawlib',version=2,source='https://excalidraw.com',libraryItems=lib),ensure_ascii=False))
(OUT/'组件索引.json').write_text(json.dumps(META,ensure_ascii=False,indent=2))
render_svg(E,(0,0,2500,12840),OUT/'通用表达组件-实例画布.svg')
render_png(E,(0,0,2500,12840),OUT/'组件总览.png',.3)
for i,name in enumerate(['01-材料与动作','02-组织与变化','03-比较与关系','04-判断与交付','05-导航层级与判断','06-证据版本与变体']):render_png(E,(50,520+i*1800,2390,1770),OUT/f'{name}.png',.75)
render_png(E,(50,11400,2390,1430),OUT/'基础零件与组合.png',.75)
for m in META:render_png(E,(m['x']-10,m['y']-10,1140,850),OUT/f'{m["id"]}.png',.9)
parts=['# 通用视觉表达组件库\n','本组件库从正常制作路径中的关系提炼结构，用中性内容演示，不复述课程制作经历。规划为 **22 类组合组件＋4 个布局变体＋12 个基础零件**。组件库文件包含 22 类组合实例和 2 张变体组合板（每板 2 个布局）；基础零件可从展示画布中复制。\n','## 使用方式\n','打开 `通用表达组件-实例画布.excalidraw` 查看全部示例。`通用表达组件-扩展库.excalidrawlib` 为独立组件库文件；每项只包含图形实例，不带展示外框与说明。也可以直接从画布复制一个分组。文字、图形、箭头均为原生元素。\n','先判断自己要表达什么关系，再选组件。复制实例后替换名称、图片、说明或数量，保留关系结构。移动子元素时需检查连线端点；当前连线使用固定坐标，未做对象绑定。\n','## 如何选型\n','| 想讲清楚什么 | 组件 |\n|---|---|']
for m in META:parts.append(f'| {m["question"]} | {m["id"]} {m["name"]} |')
parts.append('\n## 每类组件的详细实例\n')
for m in META:
 parts.extend([f'### {m["id"]} {m["name"]}\n',f'![{m["name"]}]({m["id"]}.png)\n',f'- 要回答：{m["question"]}\n- 结构：{m["structure"]}。\n- 可替换内容：{m["fields"]}。\n- 使用时机：{m["usage"]}\n- 边界：{m["avoid"]}\n'])
parts.extend(['## 容易混淆的结构\n','- **连续分镜与并列四格**：前者看前后变化，后者看同级对象。不能因为都是四格就互相替代。\n- **前后对照与候选比较**：前者解释同一对象的改变；后者比较同一目标的多种选择。\n- **结构拆解与时间轨道**：前者回答“由什么组成”；后者回答“何时发生”。\n- **一对多复用与多路汇合**：前者是一个规则支持多个实例；后者是多份产物汇成一个结果。\n- **协作阶段与确认关口**：前者讲分工，后者讲能否继续推进的条件。\n','## 从正常路径提炼出的选型依据\n','此表只说明组件为什么值得准备，展示画布本身不填入课程实质内容。来源：[已确认的正常主路径](../课程制作主路径.mmd)。\n','| 主路径中反复出现的关系 | 应准备的通用组件 |\n|---|---|\n| 收集多份输入 | 材料集合 |\n| 用户判断、AI执行、形成产物 | 协作阶段卡 |\n| 文字含义转成图形 | 概念到图形映射 |\n| 看原型、调参数、查看细节 | 界面标注与局部放大 |\n| 研究参考并拆解方法 | 整体拆解与分层 |\n| 沉淀方法，后续多处使用 | 共用规则与复用 |\n| 整理或调整前后的变化 | 前后对照 |\n| 内容逐步展开 | 连续状态与分镜 |\n| 多种动作配合发生 | 分层时间轨道 |\n| 查看样式并作出选择 | 候选比较 |\n| 多种材料或案例平级盘点 | 并列四格 |\n| 多条内容线交织与汇合 | 汇合与分流 |\n| 先确认小样，再正式接入 | 样例确认与扩展 |\n| 回顾效果并返回调整 | 正常反馈与迭代 |\n| 页面、说明和操作相互对应 | 多轨同步对照 |\n| 成套产物交接使用 | 交付包与入口 |\n','## 图形约定与核验\n','蓝色表示主体，紫色表示补充或变化，绿色表示采用或输出，黄色便签表示观察与依据。实线用于交付或推进；虚线用于引用规则或反馈回返。颜色不单独承担含义，旁边保留文字。\n','示例 UI 与文案均为中性示范，不表示任何真实产品、课程或工作已经完成。PNG / SVG 用同一组元素坐标生成，供快速审阅；手绘笔触和字体可能与 Excalidraw 原生显示略有不同。\n'])
(OUT/'组件库使用说明.md').write_text('\n'.join(parts))
assert len(lib)==24 and len({e['id'] for e in E})==len(E)
assert all(e['type']!='image' for e in E)
print(json.dumps({'components':len(lib),'elements':len(E),'libraryElements':sum(len(z['elements']) for z in lib)},ensure_ascii=False))
