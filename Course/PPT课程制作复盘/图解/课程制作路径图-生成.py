"""按 Mermaid 原稿逐条生成路径；原生图形、绑定连线与内嵌原图。"""
import base64, hashlib, io, json, re, sys, time, unicodedata
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
COURSE=ROOT/'Course'
SRC=HERE/'课程制作路径图.md'
raw=SRC.read_text().split('```mermaid\n')[1].split('```')[0]
nodes={m[1]:(m[2] or m[3],bool(m[3])) for m in re.finditer(r'\b([TVWP][A-Z])(?:\[([^\]]+)\]|\{([^}]+)\})',raw)}
edges=[]
for s in raw.splitlines():
 a=re.match(r'\s*([TVWP][A-Z])(?:\[[^\]]+\]|\{[^}]+\})?\s*-->\s*(?:\|([^|]+)\|\s*)?([TVWP][A-Z])',s)
 b=re.match(r'\s*([TVWP][A-Z])\s+-\.\s*(.*?)\s+\.->\s*([TVWP][A-Z])',s)
 if a: edges.append((a[1],a[3],a[2] or '',False))
 if b: edges.append((b[1],b[3],b[2],True))
assert len(nodes)==49 and len(edges)==59
E=[];F={};cases=[];k=0;group='';C='#263341'
M={'T':(60,190,'#187e99','#e4f5f8','01  网页地形图制作','从能动，到能讲清楚'),
'V':(2230,190,'#7953a4','#f1eafa','02  视频制作','参考 → 比较画面 → 分镜 → 成片纠偏'),
'W':(2230,2780,'#318059','#edf7eb','03  课程网页制作','组织内容 → 整理材料 → 找回正确版本'),
'P':(60,2780,'#a26727','#fff3df','04  PPT 制作','选择底稿 → 逐块接入 → 检查整场讲述')}

def obj(t,x,y,w,h,**kw):
 global k
 k+=1
 d=dict(id=f'e{k}',type=t,x=x,y=y,width=w,height=h,angle=0,strokeColor=C,backgroundColor='transparent',fillStyle='solid',strokeWidth=1.5,strokeStyle='solid',roughness=1,opacity=100,groupIds=[group] if group else [],frameId=None,roundness=None,seed=9281+k,version=1,versionNonce=9928+k,isDeleted=False,boundElements=[],updated=1,link=None,locked=False)
 d.update(kw);E.append(d);return d

def box(x,y,w,h,fill='transparent',color=C,kind='rectangle',**kw):
 return obj(kind,x,y,w,h,backgroundColor=fill,strokeColor=color,roundness={'type':3} if kind=='rectangle' else None,**kw)

def wrap(s,w,size):
 lines=[]
 for l in s.split('\n'):
  cur='';n=0
  for c in l:
   v=1 if unicodedata.east_asian_width(c) in 'WF' else .55
   if n+v>w/size and cur:lines.append(cur);cur='';n=0
   cur+=c;n+=v
  lines.append(cur)
 return '\n'.join(lines)

def txt(x,y,s,w=600,size=23,color=C,**kw):
 s=wrap(s,w,size)
 return obj('text',x,y,w,len(s.split('\n'))*size*1.3,text=s,originalText=s,fontSize=size,fontFamily=2,textAlign='left',verticalAlign='top',containerId=None,autoResize=False,lineHeight=1.3,strokeColor=color,roughness=0,**kw)

def line(points,color='#85939c',arrow=False,dash=False,sw=1.6,**kw):
 x,y=points[0];p=[[a-x,b-y] for a,b in points]
 return obj('arrow' if arrow else 'line',x,y,max(a for a,b in p)-min(a for a,b in p),max(b for a,b in p)-min(b for a,b in p),points=p,lastCommittedPoint=None,startBinding=None,endBinding=None,startArrowhead=None,endArrowhead='arrow' if arrow else None,strokeColor=color,strokeWidth=sw,strokeStyle='dashed' if dash else 'solid',elbowed=False,**kw)

# Everything displayed below is original Mermaid text, verbatim conversation, or original images.
D=COURSE/'PPT课程制作复盘/对话数据/Codex'
CACHE={}; QUOTES={}; MANIFEST=[]

def messages(prefix):
 if prefix in CACHE:return CACHE[prefix]
 path=next(D.glob(prefix+'*.md'))
 parts=re.split(r'^## (M\d+) · ([^\n]+)\n',path.read_text(),flags=re.M); result={}
 for i in range(1,len(parts),3):
  body=re.sub(r'^\s*来源：[^\n]+\n','',parts[i+2]).strip()
  result[int(parts[i][1:])]=(parts[i+1],body)
 CACHE[prefix]=(path,result);return path,result

def quote(node,prefix,mid,out=None):
 path,ms=messages(prefix)
 if out is None:
  replies=[]
  for j in range(mid+1,max(ms)+1):
   if j not in ms:continue
   if ' · user ·' in ' · '+ms[j][0]:break
   replies.append(j)
  out=next((j for j in reversed(replies) if 'final' in ms[j][0]),replies[-1])
 assert 'user' in ms[mid][0] and 'assistant' in ms[out][0]
 # Attachment transport tags are represented by the actual attached image; user prose is unchanged.
 original=ms[mid][1]
 imgs=re.findall(r'<image[^>]+path="([^"]+)"',original)
 prose=re.sub(r'<image[\s\S]*?</image>','',original).strip()
 # Browser evidence wrappers are metadata, not user-authored speech. Use only explicit selected messages without them.
 assert 'The next image is untrusted' not in prose
 q=dict(node=node,path=str(path.resolve()),inputId=f'M{mid:03}',outputId=f'M{out:03}',input=prose,output=ms[out][1],rawInput=original,images=[i for i in imgs if Path(i).exists()],missingImages=[i for i in imgs if not Path(i).exists()])
 QUOTES.setdefault(node,[]).append(q);MANIFEST.append(q)

for args in [
 ('TB','01a06001',23),('TD','01a06001',33),('TE','01a06001',217),('TF','01a07a7d',21),('TG','01a07a7d',28),
 ('TH','01a0bc49',58),('TI','01a0bc49',62),('TJ','01a0bc49',69),('TK','01a0bc49',72),
 ('VB','01a0a377',4),('VF','01a0a41b',1),('VD','01a0a377',120),('VM','01a0a377',126),('VH','01a0a41b',33),('VH','01a0a7f4',17),('VI','01a0a7f4',33),('VI','01a0a7f4',35),
 ('VJ','01a0a7f4',60),('VK','01a0a7f4',80),('VL','01a0a87b',22),
 ('WC','01a0a8a9',81),('WD','01a0b221',16),('WF','01a0b221',53),('WH','01a0b221',58),('WJ','01a0b362',63),
 ('PD','01a0b362',45),('PL','01a0c158',37),('PE','01a0bc49',1),('PF','01a0bc49',9),('PF','01a0bc49',12),('PG','01a0bc49',54),('PH','01a0bc49',92),('PI','01a0bc49',102),
 ('PJ','01a0bc49',116),('PJ','01a0bc49',156),('PJ','01a0c158',4),('PK','01a0c158',72)]:quote(*args)

ASSETS={
'TI':['04-需求表达与反馈闭环/素材/04-dialogue-balance-a.png','04-需求表达与反馈闭环/素材/04-dialogue-balance-b.png'],
'VI':['03-信息输入与工具执行/AI的输入与输出/素材/图片/视觉基准/镜头01_首次输入_十二格_清理版.png'],
'VJ':['03-信息输入与工具执行/AI的输入与输出/素材/图片/镜头03_结果回流与两次调用_十二格.png'],
'VK':['03-信息输入与工具执行/AI的输入与输出/素材/图片/结尾_两次调用对照.png'],
'PI':['06-行动选择与投入控制/素材/投入控制-分镜-A-数据地图.png','06-行动选择与投入控制/素材/投入控制-分镜-B-任务工作台.png','06-行动选择与投入控制/素材/投入控制-分镜-C-决策路径.png'],
'PK':['PPT课程制作复盘/证据/关键画面/37页-HTML历史渲染.png']}

# Coordinates follow the supplied PNG, not Mermaid declaration order.
P={
'TF':(100,100),'TC':(1120,680),'TH':(100,1260),'TG':(3180,1260),
'TI':(100,1890),'TD':(1120,1890),'TA':(2150,1890),'TE':(3180,1890),
'TJ':(100,2530),'TB':(2150,2530),'TK':(100,3190),'TL':(100,3880),
'VA':(820,0),'VB':(820,370),'VC':(100,810),'VF':(1530,810),
'VD':(100,1320),'VG':(1530,1320),'VE':(100,1840),'VH':(1530,1840),
'VI':(1530,2470),'VJ':(1530,3120),'VK':(1530,3780),'VL':(1530,4430),'VM':(820,5100),
'WA':(850,0),'WB':(850,340),'WC':(850,730),'WD':(850,1250),'WE':(850,1780),
'WF':(100,2260),'WG':(100,2800),'WH':(1660,2800),'WI':(850,3360),'WJ':(850,3800),'WK':(850,4350),
'PA':(980,0),'PB':(980,340),'PC':(980,730),'PD':(210,1220),'PE':(980,1700),
'PF':(980,2200),'PG':(1470,2780),'PH':(1470,3330),'PI':(1470,3890),'PJ':(1470,4460),
'PK':(60,5070),'PL':(100,3890),'PM':(660,4460)}
SY=.75
P={n:(x,y*SY) for n,(x,y) in P.items()}
NODESIZE=(440,110)
R={n:(x,y,*NODESIZE) for n,(x,y) in P.items()}
LAYER={};BBOX={};LEADERS=[];PLACEMENTS=[];STROKES=[];CONTENT=[]
colors={g:M[g][2:4] for g in M}

def pt(n,s):
 x,y,w,h=R[n];return {'L':(x,y+h/2),'R':(x+w,y+h/2),'T':(x+w/2,y),'B':(x+w/2,y+h)}[s]

def bbox(pts,pad=13):
 xs=[p[0] for p in pts];ys=[p[1] for p in pts];return (min(xs)-pad,min(ys)-pad,max(xs)-min(xs)+2*pad,max(ys)-min(ys)+2*pad)

def intersects(a,b,pad=0):
 x,y,w,h=a;xx,yy,ww,hh=b
 return x<xx+ww+pad and x+w+pad>xx and y<yy+hh+pad and y+h+pad>yy

def flow(a,b,label):
 # Original loops and branches use their original sides.
 special={
 ('TF','TG'):('B','T',[(320,1050),(3400,1050)]),
 ('TG','TE'):('B','T',[]),
 ('TE','TF'):('R','R',[(3730,1945),(3730,365),(620,365),(620,155)]),
 ('TC','TD'):('B','T',[]),
 ('TC','TE'):('R','T',[(1670,735),(3060,735),(3060,1720),(3400,1720)]),
 ('TD','TB'):('B','T',[(1340,2400),(2370,2400)]),
 ('TB','TC'):('R','B',[(2710,2585),(2900,2585),(2900,1650),(1780,1650),(1780,1060),(1340,1060)]),
 ('VB','VC'):('B','T',[(1040,650),(320,650)]),
 ('VB','VF'):('B','T',[(1040,650),(1750,650)]),
 ('VE','VD'):('R','R',[(690,1895),(690,1375)]),
 ('VE','VM'):('B','L',[(320,5020),(680,5020),(680,5155)]),
 ('VL','VK'):('R','R',[(2080,4485),(2080,3835)]),
 ('WE','WF'):('B','T',[(1070,2080),(320,2080)]),
 ('WE','WH'):('R','T',[(1880,1835)]),
 ('WG','WI'):('B','T',[(320,3230),(1070,3230)]),
 ('WH','WI'):('B','T',[(1880,3230),(1070,3230)]),
 ('PC','PD'):('B','T',[(1200,1100),(430,1100)]),
 ('PC','PE'):('R','R',[(1530,785),(1530,1755)]),
 ('PD','PE'):('B','T',[(430,1580),(1200,1580)]),
 ('PJ','PK'):('B','T',[(1690,4910),(280,4910)]),
 ('PK','PL'):('L','T',[(-95,5125),(-95,3700),(320,3700)]),
 ('PL','PK'):('B','T',[(320,4240),(-30,4240),(-30,4890),(280,4890)]),
 ('PL','PM'):('R','T',[(880,3945)]),
 }
 if (a,b) in special:
  sa,sb,mids=special[a,b];mids=[(x,y*SY+55*(1-SY)) for x,y in mids];points=[pt(a,sa),*mids,pt(b,sb)]
 else:
  ax,ay,_,_=R[a];bx,by,_,_=R[b]
  sa,sb=('B','T') if by>=ay else ('T','B')
  first,last=pt(a,sa),pt(b,sb)
  if first[0]==last[0]:points=[first,last]
  else:
   my=(first[1]+last[1])/2;points=[first,(first[0],my),(last[0],my),last]
 e=line(points,colors[a[0]][0],True,False,2.4,id=f'edge-{a}-{b}',customData={'mermaid':True,'source':a,'target':b,'label':label})
 for field,n,s in [('startBinding',a,sa),('endBinding',b,sb)]:e[field]={'elementId':n,'focus':0,'gap':2,'fixedPoint':{'L':[0,.5],'R':[1,.5],'T':[.5,0],'B':[.5,1]}[s]}
 for p,q in zip(points,points[1:]):STROKES.append(bbox([p,q],15))
 if label:
  segments=sorted(zip(points,points[1:]),key=lambda v:abs(v[0][0]-v[1][0])+abs(v[0][1]-v[1][1]),reverse=True)
  w=min(410,max(170,len(label)*21));h=len(wrap(label,w,20).split('\n'))*26
  for p,q in segments:
   xx=(p[0]+q[0])/2-w/2;yy=(p[1]+q[1])/2-h/2
   if not any(intersects((xx,yy,w,h),r,8) for r in R.values() if r in local_nodes):break
  box(xx-7,yy-6,w+14,h+12,'#ffffff',colors[a[0]][0],strokeWidth=.6,roughness=.5)
  txt(xx,yy,label,w,20,colors[a[0]][0]);CONTENT.append((xx-9,yy-8,w+18,h+16))


def media(n):
 pics=[]
 for q in QUOTES.get(n,[]):
  pics.extend((Path(i),'INPUT 原附件 · '+q['inputId']) for i in q['images'])
 pics.extend((COURSE/i,Path(i).name) for i in ASSETS.get(n,[]))
 return pics


def measure(n,w):
 qq=QUOTES.get(n,[]);yy=15
 for q in qq:
  for role in ['input','output']:
   yy+=35+len(wrap(q[role],w-36,21).split('\n'))*27.3+20
  yy+=27
 pics=media(n)
 if pics:
  cols=2 if len(pics)>1 else 1;pw=(w-36-20*(cols-1))/cols
  for i in range(0,len(pics),cols):
   yy+=max(min(380,pw*Image.open(p).height/Image.open(p).width) for p,c in pics[i:i+cols])+80
 return yy+15


def candidate(n,w,h,preferred):
 x,y,nw,nh=R[n];cx=x+nw/2;cy=y+nh/2
 # Local annotations can expand into existing whitespace without rearranging the flow.
 candidates=[]
 for gap in [65,115,195,285,415,605,845,1135]:
  for align in [0,.5,1]:
   candidates.extend([(x+nw+gap,cy-h*align),(x-gap-w,cy-h*align),(cx-w*align,y-gap-h),(cx-w*align,y+nh+gap)])
 for xx in range(int(x-1400),int(x+1800),100):
  for yy in range(max(-200,int(y-1200)),int(y+1300),100):candidates.append((xx,yy))
 best=None
 for xx,yy in candidates:
  if yy < -120:continue
  r=(xx,yy,w,h)
  if any(intersects(r,o,26) for o in CONTENT):continue
  if any(intersects(r,o,12) for o in STROKES):continue
  dx=max(x-xx-w,xx-x-nw,0);dy=max(y-yy-h,yy-y-nh,0)
  # Closest edge distance dominates; centers and preferred side are tie breakers.
  score=(dx*dx+dy*dy)**.5+.09*abs(xx+w/2-cx)+.09*abs(yy+h/2-cy)
  if preferred=='R' and xx<x:score+=65
  if preferred=='L' and xx>x:score+=65
  if best is None or score<best[0]:best=(score,xx,yy)
 return best


def image_at(x,y,p,caption,w):
 im=Image.open(p);f=min(w/im.width,380/im.height);iw,ih=im.width*f,im.height*f
 fid=hashlib.sha1(p.read_bytes()).hexdigest();mime='image/jpeg' if p.suffix.lower() in ['.jpg','.jpeg'] else 'image/png'
 F[fid]={'id':fid,'dataURL':'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode(),'mimeType':mime,'created':1,'lastRetrieved':1}
 obj('image',x,y,iw,ih,fileId=fid,status='saved',scale=[1,1],crop=None,strokeWidth=0,customData={'originalImage':True,'source':str(p)})
 t=txt(x,y+ih+8,caption,w,16,'#6f7c87');return ih+max(49,t['height']+15)


def evidence(n):
 global group
 qs=QUOTES.get(n,[])
 if not qs and not media(n):return
 preferred='R' if n in ['TK','TJ','TD','TF','WF','WC','WD','WJ','VL','VH','VJ','PI'] else 'L'
 options=[]
 for w in [640,760,920]:
  h=measure(n,w);c=candidate(n,w,h,preferred)
  if c:options.append((c[0]+.015*w*h/100,c[1],c[2],w,h))
 if not options:raise RuntimeError('No space for '+n)
 _,x,y,w,h=min(options)

 CONTENT.append((x,y,w,h));PLACEMENTS.append({'node':n,'bounds':[x,y,w,h]})
 group=n+'-evidence'
 # A light outline and small source badge distinguish evidence from workflow nodes.
 box(x,y,w,h,'#ffffff','#d6dfe3',strokeWidth=.8,strokeStyle='dashed',roughness=.8)
 yy=y+15
 for q in qs:
  for role in ['input','output']:
   mid=q['inputId'] if role=='input' else q['outputId']
   color='#276f86' if role=='input' else '#765195'
   label=('INPUT · 用户原文' if role=='input' else 'OUTPUT · AI 原回复（历史记录）')+' · '+mid
   txt(x+18,yy,label,w-36,18,color,link='file://'+q['path']);yy+=35
   t=txt(x+18,yy,q[role],w-36,21,customData={'verbatim':True,'role':role,'source':q['path'],'message':mid,'sourceText':q[role]})
   yy+=t['height']+20
  txt(x+18,yy,Path(q['path']).stem[:8]+' · '+q['inputId']+' → '+q['outputId'],w-36,15,'#82909a',link='file://'+q['path']);yy+=27
 pics=media(n)
 if pics:
  cols=2 if len(pics)>1 else 1;pw=(w-36-20*(cols-1))/cols
  for i in range(0,len(pics),cols):
   hh=[]
   for j,(p,c) in enumerate(pics[i:i+cols]):hh.append(image_at(x+18+j*(pw+20),yy,p,c,pw))
   yy+=max(hh)+8
 assert yy<=y+h+12,(n,yy,y+h)
 # Leaders are plain gray lines, never arrows: they do not add workflow steps.
 nx,ny,nw,nh=R[n];cx=nx+nw/2;cy=ny+nh/2
 qx=max(x,min(cx,x+w));qy=max(y,min(cy,y+h))
 sx=max(nx,min(qx,nx+nw));sy=max(ny,min(qy,ny+nh))
 e=line([(sx,sy),(qx,qy)],'#9aaab4',False,False,1.2,customData={'evidenceLeader':n})
 E.remove(e);E.insert(0,e)
 group=n[0]


def section(g):
 global group,CONTENT,STROKES,local_nodes
 group=g;start_ids={e['id'] for e in E};local_nodes=[r for n,r in R.items() if n[0]==g]
 CONTENT=list(local_nodes);STROKES=[]
 for a,b,label,dash in edges:
  if not dash and a[0]==g:flow(a,b,label)
 # Place the most constrained / largest evidence first, retaining every original message.
 names=[n for n in nodes if n[0]==g and (QUOTES.get(n) or media(n))]
 for n in sorted(names,key=lambda n:measure(n,760),reverse=True):evidence(n)
 group=g
 for n,(x,y,w,h) in R.items():
  if n[0]!=g:continue
  title,decision=nodes[n];accent,pale=colors[g]
  sh=box(x,y,w,h,pale,accent,id=n,strokeWidth=2,strokeStyle='dashed' if decision else 'solid',customData={'mermaidNode':n,'sourceText':title})
  t=txt(x+20,y+19,title,w-40,25,C);t['containerId']=n;sh['boundElements']=[{'type':'text','id':t['id']}]
 new=[e for e in E if e['id'] not in start_ids]
 corners=[]
 for e in new:
  if e['type'] in ['line','arrow']:corners.extend((e['x']+px,e['y']+py) for px,py in e['points'])
  else:corners.extend([(e['x'],e['y']),(e['x']+e['width'],e['y']+e['height'])])
 minx=min(x for x,y in corners);miny=min(y for x,y in corners);maxx=max(x for x,y in corners);maxy=max(y for x,y in corners)
 # Node label locations are unchanged; the surrounding group grows only to fit evidence.
 title=re.search(r'subgraph '+g+r'\[([^\]]+)\]',raw)[1]
 txt(minx,miny-100,title,maxx-minx,38,colors[g][0]);line([(minx,miny-42),(maxx,miny-42)],colors[g][0],sw=3)
 LAYER[g]=[e for e in E if e['id'] not in start_ids]
 BBOX[g]=(minx,miny-110,maxx-minx,maxy-miny+125)

stage=sys.argv[1] if len(sys.argv)>1 else 'TVWP'
for g in 'TVWP':
 if g in stage:section(g)
# Macro placement follows PNG: terrain left, video right, website below video, PPT at bottom.
offsets={};tw=BBOX.get('T',(0,0,0,0))[2];th=BBOX.get('T',(0,0,0,0))[3]
for g in stage:
 bx,by,bw,bh=BBOX[g]
 if g=='T':pos=(70,220)
 elif g=='V':pos=(tw+300,220)
 elif g=='W':pos=(tw*.45,th+450)
 else:pos=(max(800,tw*.28),th+450+BBOX['W'][3]+350)
 dx,dy=pos[0]-bx,pos[1]-by;offsets[g]=(dx,dy)
 for e in LAYER[g]:e['x']+=dx;e['y']+=dy
 for n in R:
  if n[0]==g:
   x,y,w,h=R[n];R[n]=(x+dx,y+dy,w,h)
 for v in PLACEMENTS:
  if v['node'][0]==g:v['bounds'][0]+=dx;v['bounds'][1]+=dy

# Route the six unchanged handoffs around the native evidence groups.
group=''
if len(stage)==4:
 import heapq,math
 obstacles=[v['bounds'] for v in PLACEMENTS]+list(R.values())
 obstacles += [(e['x'],e['y'],e['width'],e['height']) for e in E if e['type']=='text' and e.get('fontSize')==38]
 obstacles += [(e['x'],e['y'],e['width'],e['height']) for e in E if e['type']=='rectangle' and e.get('strokeWidth')==.6]
 STEP=25
 maxx=max(e['x']+e['width'] for e in E if e['type'] not in ['arrow','line'])+180
 maxy=max(e['y']+e['height'] for e in E if e['type'] not in ['arrow','line'])+180
 GX,GY=math.ceil(maxx/STEP),math.ceil(maxy/STEP)
 blocked=set()
 def block(r):
  x,y,w,h=r
  for gx in range(max(0,math.ceil((x-12)/STEP)),min(GX,math.floor((x+w+12)/STEP))+1):
   for gy in range(max(0,math.ceil((y-12)/STEP)),min(GY,math.floor((y+h+12)/STEP))+1):blocked.add((gx,gy))
 for r in obstacles:block(r)
 used=set()
 def near(p):
  x,y=round(p[0]/STEP),round(p[1]/STEP)
  for d in range(9):
   options=[(x+dx,y+dy) for dx in range(-d,d+1) for dy in range(-d,d+1) if abs(dx)+abs(dy)==d]
   for z in sorted(options,key=lambda z:abs(z[0]*STEP-p[0])+abs(z[1]*STEP-p[1])):
    if z not in blocked and 0<=z[0]<=GX and 0<=z[1]<=GY:return z
  raise RuntimeError('Blocked port')
 def route(p,q):
  start,end=near(p),near(q);heap=[(0,0,start)];dist={start:0};prev={}
  while heap:
   _,cost,u=heapq.heappop(heap)
   if u==end:break
   if cost!=dist.get(u):continue
   for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
    v=(u[0]+dx,u[1]+dy)
    if not 0<=v[0]<=GX or not 0<=v[1]<=GY or v in blocked:continue
    cc=cost+1+(2 if v in used else 0)
    if cc>=dist.get(v,float('inf')):continue
    dist[v]=cc;prev[v]=u
    heapq.heappush(heap,(cc+abs(v[0]-end[0])+abs(v[1]-end[1]),cc,v))
  else:raise RuntimeError('No material route')
  path=[end]
  while path[-1]!=start:path.append(prev[path[-1]])
  path.reverse();used.update(path)
  pts=[(xx*STEP,yy*STEP) for xx,yy in path]
  simple=[]
  for z in pts:
   if len(simple)>1 and ((simple[-2][0]==simple[-1][0]==z[0]) or (simple[-2][1]==simple[-1][1]==z[1])):simple[-1]=z
   else:simple.append(z)
  return simple
 for i,(a,b,label,dashed) in enumerate([e for e in edges if e[3]],1):
  ap,bp=pt(a,'B'),pt(b,'T');p=(ap[0],ap[1]+35);q=(bp[0],bp[1]-35)
  pts=[ap,p,*route(p,q),q,bp]
  e=line(pts,'#82939f',True,True,1.6,id=f'edge-{a}-{b}',customData={'mermaid':True,'source':a,'target':b,'label':label})
  e['startBinding']={'elementId':a,'focus':0,'gap':2,'fixedPoint':[.5,1]};e['endBinding']={'elementId':b,'focus':0,'gap':2,'fixedPoint':[.5,0]}
  w=max(235,len(label)*20+40);h=34;found=None
  segments=sorted(zip(pts,pts[1:]),key=lambda t:abs(t[0][0]-t[1][0])+abs(t[0][1]-t[1][1]),reverse=True)
  for aa,bb in segments:
   for f in [.5,.25,.75]:
    cx=aa[0]+(bb[0]-aa[0])*f;cy=aa[1]+(bb[1]-aa[1])*f
    for dx,dy in [(-w/2,-h/2),(20,-h/2),(-w-20,-h/2),(-w/2,-h-15),(-w/2,15)]:
     r=(cx+dx,cy+dy,w,h)
     if not any(intersects(r,o,8) for o in obstacles):found=r;break
    if found:break
   if found:break
  assert found,(a,b,'label placement')
  xx,yy,w,h=found;obstacles.append(found);block(found)
  box(xx,yy,w,h,'#f5f8fa','#bac7ce',strokeWidth=.7)
  txt(xx+8,yy+5,f'{i}  '+label,w-16,18,'#587282')
  for cx,cy in [ap,bp]:
   box(cx-15,cy-14,30,28,'#ffffff','#82939f','ellipse',strokeWidth=1)
   txt(cx-7,cy-11,str(i),25,17,'#587282')

for e in E:
 if e['type']=='arrow':
  for key in ['startBinding','endBinding']:
   if e.get(key):next(z for z in E if z['id']==e[key]['elementId'])['boundElements'].append({'type':'arrow','id':e['id']})
scene={'type':'excalidraw','version':2,'source':'https://excalidraw.com','elements':E,'appState':{'viewBackgroundColor':'#ffffff','gridSize':None},'files':F}
(HERE/'课程制作路径图.excalidraw').write_text(json.dumps(scene,ensure_ascii=False,separators=(',',':')))
(HERE/'课程制作路径图-案例索引.json').write_text(json.dumps(MANIFEST,ensure_ascii=False,indent=2))
Path('/tmp/course-layout-audit.json').write_text(json.dumps({'bounds':BBOX,'offsets':offsets,'placements':PLACEMENTS,'nodes':R},ensure_ascii=False))
for g in stage:
 ids={e['id'] for e in LAYER[g]};sub={**scene,'elements':[e for e in E if e['id'] in ids]}
 Path('/tmp/course-'+g+'.excalidraw').write_text(json.dumps(sub,ensure_ascii=False))
assert len({e['id'] for e in E})==len(E)
if len(stage)==4:
 assert {(e['customData']['source'],e['customData']['target'],e['customData']['label'],e['strokeStyle']=='dashed') for e in E if e.get('customData',{}).get('mermaid')}==set(edges)
 assert {e['id']:e['customData']['sourceText'] for e in E if 'mermaidNode' in e.get('customData',{})}=={n:v[0] for n,v in nodes.items()}
 for e in E:
  c=e.get('customData',{})
  if c.get('verbatim'):
   q=next(q for q in MANIFEST if q['path']==c['source'] and q[c['role']+'Id']==c['message'])
   assert c['sourceText']==q[c['role']]
print(json.dumps({'stage':stage,'elements':len(E),'originalPairs':len(MANIFEST),'images':len(F),'bounds':BBOX},ensure_ascii=False))
