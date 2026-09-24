"""Build the approved visual vocabulary into one evidence-linked production story."""
from pathlib import Path
import sys, re, json, copy, html
# Reuse only the prototype explicitly accepted by the user in this task.
BASE=Path(__file__).resolve().parent.parent/'表达形式原型/生成原型.py'
prototype=BASE.read_text()
exec(prototype.split('# Cover:')[0])
exec(prototype[prototype.index('def render('):prototype.index("render(D/'课程制作路径图-表达形式总览.png'")])
CHAPTER=int(sys.argv[1]) if len(sys.argv)>1 else 4
SCENES=[];CHAPTERS=[];SOURCES=C/'PPT课程制作复盘';BOXES={};LINKS=[]

# All scene captions are paraphrases of production records, not fabricated chat transcripts.
def wraptext(s,w,size):
 f=ImageFont.truetype(FONT,size);ls=[]
 for ln in s.split('\n'):
  buf=''
  for ch in ln:
   if f.getlength(buf+ch)>w and buf:ls.append(buf);buf=''
   buf+=ch
  ls.append(buf)
 return '\n'.join(ls)
def tx(x,y,s,size=25,color=INK,w=900,**kw):return text(x,y,wraptext(s,w,size),size,color,**kw)
def refs(*pairs):
 out=[]
 for pre,ids in pairs:
  p=next((SOURCES/'对话数据/Codex').glob(pre+'*.md'))
  out.append({'file':str(p.relative_to(ROOT)),'messages':ids})
 return out

def chapter(n,y,name,sub,color):
 global G
 G=f'chapter-{n}';CHAPTERS.append({'n':n,'y':y,'name':name})
 line([(90,y),(4090,y)],'#cbd6da',dash=True)
 circ(93,y+51,35,color,color);text(111,y+67,f'{n:02}',29)
 text(194,y+47,name,47)
 tx(197,y+113,sub,27,MUTED,3600)

def scene(key,x,y,w,h,title_,user,ai,output,nodes,source,style='card',color=PALE[2],method='',boundary=''):
 global G
 G=key
 # Flat scenes are open compositions; cards retain the accepted color-offset paper.
 if style=='card':paper(x,y,w,h,color)
 else:line([(x,y+71),(x+w,y+71)],color,sw=4)
 badge(x+23,y+23,key,color,INK,20)
 tx(x+110,y+21,title_,32,INK,w-140)
 tx(x+26,y+h-171,'用户：'+user,24,INK,w-52)
 tx(x+26,y+h-128,'AI：'+ai,24,INK,w-52)
 tx(x+26,y+h-85,'产出：'+output,24,INK,w-52)
 if style=='card':line([(x,y+h-193),(x+w,y+h-193)],'#9eadb5',dash=True,sw=1)
 tx(x+26,y+h-34,'证据 '+key+'  ↗',17,MUTED,w-52,link=f'./完整制作历程-来源.md#{key.lower()}')
 SCENES.append(dict(id=key,title=title_,nodes=nodes.split(),user=user,ai=ai,output=output,sources=source,method=method,boundary=boundary,box=[x,y,w,h]))
 BOXES[key]=(x,y,w,h)
 return x,y,w,h

def bridge(a,b,route=None,color=INK,dash=False,label='',sides=('R','L')):
 global G
 G='connections'
 def pt(k,side):
  x,y,w,h=BOXES[k];return {'R':(x+w+13,y+h*.42),'L':(x-13,y+h*.42),'T':(x+w*.5,y-15),'B':(x+w*.5,y+h+18)}[side]
 ps=[pt(a,sides[0]),*(route or []),pt(b,sides[1])];line(ps,color,True,dash,2)
 LINKS.append(dict(a=a,b=b,label=label))
 if label:
  
  if route:
   xx,yy=ps[len(ps)//2];tx(xx+13,yy-43,label,21,color,700)
  else:
   xx=(ps[0][0]+ps[-1][0])/2;yy=(ps[0][1]+ps[-1][1])/2
   lw=ImageFont.truetype(FONT,21).getlength(label);tx(xx-lw/2,yy-41,label,21,color,700)

def port(x,y,letter,s,color=BLUE):
 badge(x,y,letter,'#edf4f7',color,21);tx(x+61,y+3,s,21,color,700)

def methodbar(y,items):
 global G
 G='methods-'+str(y)
 for i,(head,body) in enumerate(items):
  x=100+i*(3930/len(items));w=3930/len(items)-45
  box(x,y,w,122,'#f5f8f8','#f5f8f8')
  tx(x+18,y+13,head,25,GREEN,w-36);tx(x+18,y+57,body,22,INK,w-36)

def mini_slide(x,y,w=250,h=155,title_='讲述页',co=BLUE):
 window(x,y,w,h,None,co);tx(x+20,y+41,title_,19,co,w-40)
 for i in range(2):line([(x+22,y+92+i*22),(x+w-25,y+92+i*22)],'#9eafb9')

def ui_terrain(x,y,w=500,h=260):
 window(x,y,w,h,'操作示意')
 box(x+17,y+46,w*.34,h-100,'#f0f4f6','#f0f4f6')
 for i in range(4):line([(x+30,y+66+i*32),(x+w*.32,y+66+i*32)],'#9cabb4')
 terrain(x+w*.43,y+67,w*.50,h*.48,2)
 for i,s in enumerate(['运行','停止','重置']):badge(x+20+i*92,y+h-43,s,'#edf4f7',BLUE,16)

G='cover'
text(97,62,'一套 44 页 PPT，是怎样做出来的？',63)
line([(101,153),(1608,146)],'#f1d878',sw=12)
text(100,187,'2026.09.01—09.21 制作复盘  ·  从材料、试作、反馈到现场课件',29,MUTED)
text(100,245,'用户作选择，AI 把选择变成可检查的产物，再依据反馈修改。',31)
text(100,293,'四条线交错推进；下面按工作主题组织，不代表四条线严格依次发生。',25,MUTED)
# Compact dependency overview with visual artifacts.
for x,y,s,co in [(190,460,'地形与教学对话',PALE[2]),(190,620,'两段课程视频',PALE[0]),(1030,535,'课程阅读网页',PALE[3]),(1880,535,'现场 PPT',PALE[4])]:
 box(x,y,380,105,co,co);text(x+31,y+31,s,30)
line([(582,512),(780,512),(780,571),(1015,571)],BLUE,True,True)
line([(582,672),(850,672),(850,608),(1015,608)],PURPLE,True,True)
line([(1425,586),(1865,586)],GREEN,True,True);text(1495,538,'选定文章与素材',22,GREEN)
line([(575,470),(680,470),(680,402),(2150,402),(2150,523)],BLUE,True,True)
text(987,364,'校正后的地形对话页',22,BLUE)
line([(575,712),(700,712),(700,758),(2170,758),(2170,655)],PURPLE,True,True)
text(991,766,'视频与独立字幕',22,PURPLE)
# small sixth transfer: reader provides raw dialogue to terrain story
line([(1115,526),(1115,442),(581,442),(581,481)],GREEN,True,True)
text(1158,430,'完整教学对话回到地形接入',19,GREEN)
text(2730,386,'读图约定',31)
line([(2730,455),(2830,455)],INK,True);text(2862,435,'实线：采用后的推进',25)
line([(2730,513),(2830,513)],GREEN,True,True);text(2862,493,'虚线：跨线材料交接',25)
line([(2730,571),(2830,571)],RED,True,True);text(2862,551,'红色回路：修改、回退',25)
text(2730,620,'线稿 / UI：制作动作的示意\n原始图：分镜、对话素材、历史截图\n44 页：9 月 21 日阶段版本',24,MUTED)

# 01 Terrain: real actions before and during PPT integration.
chapter(1,885,'地形：从能动，到因果与对话都能讲清','9/2–9/8 前置素材；9/20 接入课件后，再次回到原文核对。',PALE[2])
scene('T1',100,1110,990,630,'接上原文，逐项调整','逐项调路径、停顿与文字。','沿原概念与案例调整动画。','可继续检查的地形网页。','TA TB',refs(('01a06001',[23,33,217])),method='先沿现有材料逐项修改，让每次反馈有明确对象。')
doc(153,1238,125,173,BLUE,'原文＋案例');line([(299,1330),(423,1330)],BLUE,True);ui_terrain(448,1224,578,282)
scene('T2',1460,1110,1100,710,'先纠正因果，再看动画效果','指出“小球走过才出沟壑”不对。','调整为语义先塑形、小球后移动。','先后关系明确的动画方案。','TC TD',refs(('01a06001',[33,34])),style='open',color=PALE[2],method='反馈先指出因果关系；“看起来更顺”不能替代解释正确。')
for i,s in enumerate(['① 语义进入','② 地形先变','③ 小球随后移动']):
 xx=1474+i*366;box(xx,1240,343,245,'#ffffff','#93aaba',False);text(xx+17,1259,s,22,BLUE);terrain(xx+26,1338,285,108,[0,1,2][i])
note(1735,1530,'当时的问题：地形和小球共用进度，\n画面让人误以为“小球挖出了沟”。',PALE[4],583)
scene('T3',2980,1110,1030,710,'尝试改造后，收回修改范围','发现大改破坏设计，允许不用 Three.js。','沿用 Canvas，回到局部微调。','保留原设计、补足对比的素材。','TE TF TG',refs(('01a06001',[217,218]),('01a07a7d',[21,22,28,29])),color=PALE[3],method='明确这轮改什么、保留什么；工具选择服从表达效果。')
mini_slide(3020,1252,307,188,'尝试改造',PURPLE)
line([(3340,1345),(3430,1345)],RED,True)
mini_slide(3449,1252,490,188,'回到已有页面微调',GREEN)
note(3455,1480,'保留整体画面\n核对案例、标签与变化顺序',PALE[3],458)
bridge('T1','T2');bridge('T2','T3')
line([(3988,1700),(4090,1700),(4090,1870),(3440,1870),(3440,1840)],RED,True,True)
text(3530,1840,'回到素材完善',21,RED)
scene('T4',100,2050,1690,795,'把可运行地形，接成 A / B / 对照三页','保留完整教学对话；能运行、停止、重置。','每组先 A，再 B，最后双图并列。','同一案例可逐页讲、并排比较。','TH TI',refs(('01a0bc49',[58,59,62,63])),style='open',color=PALE[2],method='先用一组案例定讲法，再扩展；教学对话不能用总结替代。')
for i,s in enumerate(['A 原表达','B 调整表达','A / B 并排比较']):
 xx=130+i*555;window(xx,2212,520,260,s);
 if i<2:terrain(xx+45,2300,420,98,1 if i==0 else 2)
 else:
  terrain(xx+30,2300,210,98,1);terrain(xx+283,2300,210,98,2)
 if i<2:line([(xx+526,2340),(xx+546,2340)],BLUE,True)
port(134,2527,'E','接收阅读材料中的完整教学对话',GREEN)
text(135,2582,'课程里的 A/B 是教学示例，不是制作 PPT 时的聊天截图。',22,MUTED)
scene('T5',2250,2050,1760,795,'错配之后，完整研究原网页与八组对话','发现动画与原文不符，要求完整查原网页。','确认独立 A/B 被套统一模板；分别重建事件。','原文、地形、小球共用对应时间线。','TJ TK TL',refs(('01a0bc49',[69,72,73,81,82,86])),style='open',color=PALE[1],method='复用结构前先检查原假设；两段独立对话不能画成一段中途补条件。',boundary='M086为助手历史实现和验证报告；此图不重新验收交互。')
image(C/'04-需求表达与反馈闭环/素材/04-dialogue-balance-a.png',2285,2190,690,265)
image(C/'04-需求表达与反馈闭环/素材/04-dialogue-balance-b.png',3095,2174,840,313)
text(2299,2488,'A 原始教学对话（素材原图）',22,BLUE);text(3120,2515,'B 的条件从一开始就存在',22,GREEN)
line([(2300,2580),(2800,2580)],BLUE,True);text(2310,2591,'A：独立事件顺序',21,BLUE)
line([(3110,2580),(3900,2580)],GREEN,True);text(3120,2591,'B：独立事件顺序',21,GREEN)
bridge('T3','T4',[(3495,1938),(945,1938)],sides=('B','T'),label='进入 PPT 时，带着原文一起接入')
bridge('T4','T5')
port(2780,2884,'F','校正后的对话页 → PPT 的八组案例',BLUE)
port(120,2884,'A','地形素材 → 课程网页整理',BLUE)
methodbar(2990,[('先看因果','是否真的解释了原文的关系？'),('明确改动边界','保留设计，只改需要调整的部分。'),('对照要忠于原文','A/B 独立编排，不套统一故事。')])

# CHAPTERS_CONTINUE
def save(end,final=False):
 D.mkdir(exist_ok=True)
 path=D/'完整制作历程.excalidraw'
 d={'type':'excalidraw','version':2,'source':'https://excalidraw.com','elements':E,'appState':{'viewBackgroundColor':'#ffffff','gridSize':None,'zoom':{'value':.28},'scrollX':0,'scrollY':0},'files':F}
 path.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
 raw=(SOURCES/'图解/课程制作路径图.md').read_text().split('```mermaid\n')[1].split('```')[0]
 nodes={m[1]:(m[2] or m[3]) for m in re.finditer(r'\b([TVWP][A-Z])(?:\[([^\]]+)\]|\{([^}]+)\})',raw)}
 edges=[]
 for l in raw.splitlines():
  a=re.match(r'\s*([TVWP][A-Z])(?:\[[^\]]+\]|\{[^}]+\})?\s*-->\s*(?:\|([^|]+)\|\s*)?([TVWP][A-Z])',l)
  b=re.match(r'\s*([TVWP][A-Z])\s+-\.\s*(.*?)\s+\.->\s*([TVWP][A-Z])',l)
  if a:edges.append({'from':a[1],'to':a[3],'label':a[2] or '', 'kind':'flow'})
  if b:edges.append({'from':b[1],'to':b[3],'label':b[2],'kind':'handoff'})
 lookup={n:s['id'] for s in SCENES for n in s['nodes']}
 for ed in edges:ed['fromScene']=lookup.get(ed['from']);ed['toScene']=lookup.get(ed['to'])
 if final:assert set(lookup)==set(nodes),(set(nodes)-set(lookup),set(lookup)-set(nodes))
 evidence={'scenes':SCENES,'sourceNodes':nodes,'originalEdges':edges,'drawnSceneConnections':LINKS,'coverage':{'originalNodes':len(nodes),'coveredNodes':len(lookup),'originalEdges':len(edges)},'embeddedImages':len(F)}
 (D/'完整制作历程-场景与证据索引.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
 md=['# 完整制作历程：来源与阅读边界','','这张图复盘 2026 年 9 月 1–21 日的课程与 PPT 制作，44 页是该阶段版本。图中的“用户／AI／产出”均为归纳，不是逐字聊天截图。线稿和 UI 是操作示意；原始图像按图注标明。没有在本次重新验收整套 PPT、视频或网页。','','总依据：[PPT 与视频构建指南](../../PPT与视频构建指南.md)、[页面与素材对应](../../页面与素材对应.md)、[来源与完整性](../../来源与完整性.md)。','']
 for s in SCENES:
  md += [f"<a id=\"{s['id'].lower()}\"></a>",f"## {s['id']} · {s['title']}",'',f"- 用户：{s['user']}",f"- AI：{s['ai']}",f"- 产出：{s['output']}",f"- 可复用做法：{s['method']}",f"- 原路径节点：{'、'.join(s['nodes'])}"]
  for src in s['sources']:
   p=ROOT/src['file'];assert p.exists();contents=p.read_text()
   for mid in src['messages']:assert re.search(r'^## M%03d\b'%mid,contents,re.M),(p,mid)
   rel='../../'+str(p.relative_to(SOURCES));mi='、'.join('M%03d'%i for i in src['messages'])
   md += [f"- 对话：[\u200b{p.stem} · {mi}]({rel})。"]
  if s['boundary']:md += ['- 验证边界：'+s['boundary']]
  md+=['']
 md+=['## 素材口径','','原图从当前课程素材直接内嵌。两张视频静帧来自现存 PPT 资产的抽帧，属于本次抽帧，不能当作历史故障画面；历史问题另以示意图标出。第 37 页对照为用户选定图和 9 月 21 日历史 HTML 渲染。底稿完整外部生成过程不齐，因此只叙述实际导入与选择，不推定其来自某次候选。','','## 完整性','','原 Mermaid 的 49 个节点映射到制作场景；59 条原始关系保留在 JSON 索引。图中同一场景内的动作以卡片、比较和分镜表达，跨场景用连线；6 条跨线材料交接用总览及 A–F 成对标识表达。']
 (D/'完整制作历程-来源.md').write_text('\n'.join(md))
 render(D/'完整制作历程-总览.png',(30,20,4185,end),.5)
 bounds=[(1,860,2390),(2,3240,3500),(3,6770,1500),(4,8300,end-8300)]
 for n,y,h in bounds:
  if n<=CHAPTER and y<end:render(D/f'{n:02}-制作历程.png',(40,y,4160,min(h,end-y)),.7)
 # SVG companion preserves full-resolution text and all embedded original images.
 z=[f'<svg xmlns="http://www.w3.org/2000/svg" width="4250" height="{end+20}" viewBox="0 0 4250 {end+20}">','<rect width="100%" height="100%" fill="white"/>','<defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="none" stroke="context-stroke"/></marker></defs>']
 for e in E:
  x,y,w,h=[e[k] for k in ('x','y','width','height')];tp=e['type'];fill='none' if e['backgroundColor']=='transparent' else e['backgroundColor'];col=e['strokeColor'];sw=e['strokeWidth'];style=f'fill="{fill}" stroke="{col}" stroke-width="{sw}"';dash=' stroke-dasharray="7 7"' if e['strokeStyle']!='solid' else ''
  if tp=='rectangle':z.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{12 if e["roundness"] else 0}" {style}{dash}/>')
  elif tp=='ellipse':z.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" {style}/>')
  elif tp=='diamond':z.append(f'<polygon points="{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}" {style}/>')
  elif tp=='text':
   size=e['fontSize']
   for j,ln in enumerate(e['text'].split('\n')):z.append(f'<text x="{x}" y="{y+size+j*size*e["lineHeight"]}" font-family="Arial Unicode MS, PingFang SC, sans-serif" font-size="{size}" fill="{col}">{html.escape(ln)}</text>')
  elif tp in ['line','arrow']:
   pts=' '.join(f'{x+a},{y+b}' for a,b in e['points']);mark=' marker-end="url(#arrow)"' if e.get('endArrowhead') else '';z.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{sw}"{dash}{mark}/>')
  elif tp=='image':z.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{F[e["fileId"]]["dataURL"]}"/>')
 z.append('</svg>');(D/'完整制作历程.svg').write_text('\n'.join(z))
 assert len(set(e['id'] for e in E))==len(E)
 assert all(e['fileId'] in F for e in E if e['type']=='image')
 print(json.dumps({'chapter':CHAPTER,'scenes':len(SCENES),'coveredNodes':len(lookup),'elements':len(E),'images':len(F),'file':str(path)},ensure_ascii=False))
if CHAPTER==1:
 save(3150);sys.exit()
# 02 Video: one reference branch and one original explanatory-video branch.
chapter(2,3260,'视频：先确定画面怎样变化，再进入制作','9/15–9/16 · 第一段研究 3Blue1Brown；第二段从自己的输入输出文章开始。',PALE[0])
scene('V1',100,3480,1750,740,'找到参考，研究源码，再收紧范围','研究 3Blue1Brown 源码素材；限定到 6:59。','核对场景与缺失素材，按要求先做 480p。','可先检查内容与顺序的低清版本。','VA VB VC VD',refs(('01a0a377',[1,4,38,120,126,134,138])),color=PALE[0],method='先说明借鉴范围和首轮交付规格，用低成本版本检查关键内容。',boundary='原私有素材不齐，历史实现包含替代素材；不能表述为原片一比一复刻。')
image(D/'素材/原理视频-现存文件28秒.png',137,3620,670,360)
text(145,4000,'现存选定视频 · 本次抽帧 00:28',20,MUTED)
doc(900,3650,135,175,PURPLE,'源码 / 素材');line([(1068,3747),(1204,3747)],PURPLE,True)
box(1230,3650,541,181,'#faf7fe',PURPLE);text(1260,3678,'先看可检查的一版',29,PURPLE)
text(1260,3733,'0:00—6:59   ·   480p\n字幕另存为 SRT',27)
note(1250,3890,'私有素材缺失 → 使用替代品\n明确改编范围，不声称原片复刻',PALE[4],493)
scene('V2',2260,3480,1750,740,'播放时发现：待预测的词已经泄漏','指出“夜空”不应提前出现在输入中。','暂停相关渲染，统一修正训练例子的输入。','更正后的片段与独立字幕。','VE',refs(('01a0a377',[143,144,145,153])),style='open',color=PALE[1],method='检查教学内容是否成立，不能只看画面流畅、文件能播放。',boundary='更正结果和完整解码检查为历史报告；示意图并非故障截图。')
text(2310,3615,'问题画法（示意）',25,RED);text(3190,3615,'应当表达的关系（示意）',25,GREEN)
box(2300,3666,730,130,'#fff4ee',RED);text(2330,3708,'输入：烟花映亮了夜空',33,RED)
line([(2658,3788),(2946,3668)],RED,sw=3)
box(3160,3666,790,130,'#edf7f0',GREEN);text(3195,3708,'输入：烟花映亮了',32,GREEN)
line([(3390,3813),(3390,3890)],GREEN,True)
box(3195,3910,398,96,'#ffffff',GREEN);text(3225,3937,'预测侧：夜空',30,GREEN)
note(3670,3860,'能播放\n≠\n解释正确',PALE[4],255)
bridge('V1','V2')
# Original-video branch.
scene('V3',100,4490,880,800,'先把内容讲对，再谈画面','先写 AI 输入输出；案例只负责串联。','纠正会议纪要喧宾夺主，回到输入与工具机制。','图形表达可依据的文章和镜头内容。','VF VG',refs(('01a0a41b',[1,4,11,65,81,92])),color=PALE[2],method='用案例解释机制，但持续检查案例有没有带偏主题。')
doc(150,4632,134,184,BLUE,'输入输出文章')
line([(310,4729),(380,4729)],BLUE,True)
for i,(s,co) in enumerate([('完整输入',PALE[2]),('模型请求 / 程序执行',PALE[0]),('工具结果进入下一轮',PALE[3])]):
 box(405,4635+i*70,506,54,co,co);text(424,4646+i*70,s,23)
note(425,4910,'录音案例只串起过程，\n不把课程改成会议纪要教程。',PALE[4],459)
scene('V4',1170,4490,1730,940,'候选比较 → 连续分镜 → 选定基准','比较不同方向，保留 C，逐格提出修改。','把镜头展开为连续画面，按反馈调整并存图。','修改后的 C 基准与后续镜头分镜。','VH VI',refs(('01a0a41b',[33]),('01a0a7f4',[20,21,33,35,37,60,62])),style='open',color=PALE[0],method='先让静态分镜暴露变化缺口，选定后保存明确参照。',boundary='左边为候选结构示意；右边为首次输入基准原图。第9、10格问题属于后续回流镜头，不是这张首次输入图。')
text(1205,4634,'比较表达方向（结构示意）',23,PURPLE)
for i,(s,co) in enumerate([('A 聚合',BLUE),('B 流动',PURPLE),('C 展开',GREEN)]):
 xx=1205+i*217;paper(xx,4690,193,178,PALE[i]);text(xx+17,4708,s,23,co)
 if i==0:
  for j in range(3):box(xx+24,4760+j*25,140,16,PALE[j],co)
 elif i==1:
  for j in range(3):circ(xx+31+j*48,4780,11,PALE[j],co)
  line([(xx+25,4820),(xx+161,4820)],co,True)
 else:box(xx+25,4760,143,80,'#edf6ef',co);box(xx+43,4775,65,31,PALE[4],GOLD)
line([(1870,4780),(1950,4780)],PURPLE,True)
image(C/'03-信息输入与工具执行/AI的输入与输出/素材/图片/视觉基准/镜头01_首次输入_十二格_清理版.png',1965,4627,865,451)
text(2030,5095,'原始素材 · 首次输入的十二格视觉基准',21,BLUE)
note(1210,4946,'选择 C 后仍继续改：\n背景、比例、局部内容、涂抹清理。',PALE[4],648)
text(1205,5110,'后续镜头：第 9 → 10 格必须看见新增信息',23,RED)
scene('V5',3180,4490,830,900,'把选择结果，交给下一步','保存选定图、每镜提示词和制作要求。','逐镜整理 JSON，交给代码制作阶段。','图片＋提示词＋镜头要求的材料包。','VJ',refs(('01a0a7f4',[7,60,80,85])),color=PALE[3],method='换任务时交接已采用材料、具体要求与待做部分，不只交目标。')
packet(3420,4660,282,190)
for i,(s,co) in enumerate([('选定图片',BLUE),('一镜一份提示词',PURPLE),('要出现的变化',GREEN)]):
 xx=3215+i*253;doc(xx+26,4920,124,152,co);text(xx+4,5095,s,20,co)
line([(3560,4867),(3560,4898)],GREEN,True)
bridge('V1','V3',[(975,4360),(540,4360)],sides=('B','T'),label='另一条支线：自己的输入输出视频')
bridge('V3','V4');bridge('V4','V5')
scene('V6',100,5730,2770,650,'从逐格检查，转为按时间点检查成片','指出 1:06 的缺失变化、0:28 / 1:28 的输入问题。','定位镜头，返修新增信息、对象消失和外框断裂。','多轮渲染后的选定视频版本。','VK VL',refs(('01a0a7f4',[80,85]),('01a0a87b',[22,28,44,53])),style='open',color=PALE[1],method='图用格子、视频用时间点；每次都说明哪里不对、应该看见什么。',boundary='本次抽帧来自现存选定视频，不是当时的故障画面。成片返修与验证为历史记录。')
image(D/'素材/输入输出视频-现存文件66秒.png',145,5850,555,309)
text(145,6168,'现存视频 01:06 · 非历史故障截图',19,MUTED)
window(805,5860,1140,292,'历史反馈位置 · 操作示意')
box(846,5910,394,104,'#eaf3fa',BLUE);text(878,5940,'原有输入',28,BLUE)
line([(1263,5960),(1386,5960)],BLUE,True)
box(1414,5910,466,104,'#fff8db',GOLD,strokeStyle='dashed');text(1445,5940,'新增的请求与工具结果',26,GOLD)
line([(844,6079),(1882,6079)],MUTED,sw=3)
for i,(xx,s) in enumerate([(940,'0:28'),(1270,'1:06'),(1700,'1:28')]):circ(xx,6072,7,RED,RED);text(xx-24,6093,s,20,RED)
note(2110,5875,'报出位置，也说清变化：\n哪些模块应保留？\n新增了什么信息？\n外框为什么不该消失？',PALE[4],643)
scene('V7',3180,5730,830,650,'两段视频，分别交给课程与 PPT','要求独立字幕；确认首个视频页后，再接第二页。','整理成片与 SRT，并接入两段视频对应页面。','原理视频＋独立 SRT；输入输出视频。','VM',refs(('01a0a377',[126,153]),('01a0bc49',[54,55,57])),color=PALE[0],method='交接时说明每段视频的用途，替换对应内容与时间点。',boundary='原理视频交付与两段视频接入均为历史报告，不是本次重新播放验收；独立SRT的直接证据来自原理视频要求。')
for i,s in enumerate(['原理视频','输入与输出']):
 xx=3220+i*377;window(xx,5863,337,174,s);line([(xx+139,5933),(xx+168,5953),(xx+139,5973),(xx+139,5933)],PURPLE)
 text(xx+52,6056,'MP4 + 独立 SRT' if i==0 else 'MP4 + 对应讲解',22,PURPLE)
bridge('V5','V6',[(3595,5540),(1485,5540)],sides=('B','T'),label='按选定基准进入代码制作与渲染')
bridge('V6','V7')
bridge('V2','V7',[(4160,3791),(4160,6003)],sides=('R','R'),color=PURPLE,dash=True)
text(3830,5612,'第一段视频交接 ↓',21,PURPLE)
# explicit correction loops inside video branches
line([(3300,4210),(3300,4320),(1480,4320),(1480,4235)],RED,True,True);text(1945,4270,'修正内容与镜头后再渲染',23,RED)
line([(1870,6396),(1870,6460),(1050,6460),(1050,6396)],RED,True,True);text(1215,6420,'发现缺失 → 回到代码渲染',22,RED)
port(3188,6415,'B','视频 → 课程材料',PURPLE);port(3188,6470,'D','视频＋字幕 → PPT 视频页',PURPLE)
methodbar(6550,[('首轮先压小范围','低清版本先检查内容、顺序和变化。'),('先选画面，再写代码','用连续分镜预先暴露遗漏。'),('交接与验收都要具体','图片、提示词、格号和时间点。')])
if CHAPTER==2:
 save(6740);sys.exit()
# 03 Reader: preserve selected content and distinguish reader from presentation.
chapter(3,6790,'课程网页：组织材料，也守住已经选好的版本','9/16–9/18 · 先组织七篇阅读材料；后续有删减、替换，不是七篇原封不动搬进课件。',PALE[3])
port(119,6990,'A','接收地形素材',BLUE);port(520,6990,'B','接收视频材料',PURPLE)
scene('W1',100,7140,850,790,'接上已有讨论，组织课程','保存讨论结论，围绕既有材料组织七篇。','整理正文、配图与统一阅读网页。','可供阅读和继续选材的课程材料。','WA WB WC',refs(('01a0a8a9',[19,27,31,81,95])),color=PALE[3],method='先让 AI 说明已有材料怎样沿用，再补缺失内容。')
for i in range(7):
 x=145+(i%4)*180;y=7285+(i//4)*130;doc(x,y,106,92,[BLUE,PURPLE,GREEN,GOLD][i%4]);text(x+35,y+102,str(i+1),18,MUTED)
text(150,7579,'正文、原案例、配图、视频与交互',22,GREEN)
scene('W2',1140,7140,850,790,'整理目录，意外丢掉正式网页','要求每篇一个目录，只保留采用的代码设计。','误把正式阅读器简化为零散页面。','需要纠正的整理结果。','WD WE',refs(('01a0b221',[16,53,54,55])),color=PALE[1],method='整理前列出必须保留的产物，整理后检查入口和功能。')
window(1180,7310,338,209,'正式阅读器',GREEN)
box(1192,7352,75,151,'#e5f1e9','#e5f1e9')
for i in range(4):line([(1285,7370+i*31),(1495,7370+i*31)],GREEN)
line([(1530,7410),(1590,7410)],RED,True)
window(1607,7310,340,209,'被简化的页面',RED)
for i in range(3):line([(1630,7370+i*31),(1919,7370+i*31)],RED)
note(1180,7570,'清理重复设计稿，不能拆掉正式网站。',PALE[4],761)
scene('W3',2180,7140,850,790,'两种找回：网站结构与第六篇稿件','指出网页丢失并质疑文章，指定回查改写任务。','恢复阅读器；查明第六篇选错稿，再由 Git 恢复。','历史恢复报告与待核对的正确入口。','WF WG WH',refs(('01a0b221',[53,55,57,58,60,63,65,68])),style='open',color=PALE[2],method='用原任务与版本记录定位已采用结果，不能凭文件名猜最新版。',boundary='网站与正文恢复是当时助手报告；并非本次重跑网站验收。')
for i,(heading,body,co) in enumerate([('正式网站','导航 / 搜索 / 目录',BLUE),('第六篇选定稿','原任务 / Git / 改写稿',GREEN)]):
 y=7300+i*179;paper(2222,y,759,145,PALE[2+i]);doc(2245,y+25,70,89,co);text(2350,y+22,heading,27,co);text(2350,y+82,body,23)
scene('W4',3220,7140,850,790,'核对材料后，再区分阅读与演示','盘点资产，改为单 HTML 加载正文，PPT 单独管理。','核对文章、图片与交互；拆分阅读网页和 PPT 材料。','阅读网页与现场 PPT 各司其职。','WI WJ WK',refs(('01a0b221',[65,68]),('01a0b362',[41,45,47,63,64])),color=PALE[3],method='先确认使用场景，再决定交付形态：阅读页与演示页标准不同。')
window(3260,7298,353,215,'单 HTML + Markdown',GREEN)
for i in range(5):line([(3280,7353+i*27),(3586,7353+i*27)],GREEN)
window(3670,7298,353,215,'现场 PPT',GOLD);circ(3798,7360,36,PALE[4],GOLD);text(3710,7470,'逐页讲述 / 播放',20,GOLD)
note(3260,7580,'恢复之后再调整形态：\n单 HTML 读 Markdown，PPT 独立组织讲述。',PALE[4],762)
bridge('W1','W2');bridge('W2','W3',color=RED,label='检查发现丢失');bridge('W3','W4')
port(3195,7980,'C','选定文章与素材 → PPT 制作',GREEN)
port(105,7980,'E','完整教学对话 → 地形接入',GREEN)
methodbar(8080,[('整理也要验收','入口、版本、图片、交互都要对得上。'),('恢复靠可定位的依据','回原任务、源码和 Git 找到采用稿。'),('材料相同，用途不同','阅读展开解释；PPT 组织现场讲述。')])
if CHAPTER==3:
 save(8290);sys.exit()
# 04 PPT: choose a base, establish reusable pages, assemble, then review the whole talk.
chapter(4,8330,'PPT：选对底稿，先确认一处，再逐块接入','9/18–9/21 · 文章、视频、地形与投入图表汇合；最终检查整场讲述，而不只看单页。',PALE[4])
port(120,8524,'C','选定文章与素材进入课件',GREEN)
scene('P1',100,8600,1100,790,'试作不合适，先纠正用途与选材','拒绝用错素材、堆文字和硬塞阅读网页。','经历课件与视觉候选试作，按反馈调整方向。','被放弃的试作与更明确的现场用途。','PA PB PC PD',refs(('01a0b362',[32,41,45,47]),('01a0b339',[10,15])),color=PALE[1],method='先确认这份内容给谁看、在哪用；用途不对，继续改字号也无济于事。')
for i,(head,lines_) in enumerate([('素材不对',2),('文字堆积',6),('网页外壳',4)]):
 xx=143+i*343;window(xx,8761,298,221,head,RED)
 for j in range(lines_):line([(xx+22,8820+j*22),(xx+273,8820+j*22)],'#b89b97')
 line([(xx+230,8748),(xx+276,8798)],RED,sw=3);line([(xx+276,8748),(xx+230,8798)],RED,sw=3)
note(143,9040,'判断标准：学员在现场能不能跟着讲述？',PALE[4],997)
scene('P2',1570,8600,1100,790,'重新选定十页，并把规范真正用上','只采用附件 1–10 页；要求全局参数落到页面。','导入底稿，提取通用参数，再应用到实际页面。','新的十页起点与共同设计依据。','PE PF',refs(('01a0bc49',[1,4,9,10,12,13,19])),color=PALE[2],method='讨论规则、保存规则、产物遵守规则，是三件分别检查的事。',boundary='外部底稿完整生成过程不齐；不把早期其他候选误认成这份附件。')
for j in range(3):box(1625+j*11,8760-j*10,357,232,'#ffffff',BLUE)
image(C/'PPT/assets/cover-clean.png',1652,8780,310,139)
text(1671,8936,'采用 1—10 页',27,BLUE)
text(2044,8768,'全局设计参数',27,BLUE)
for i,s in enumerate(['画布 · 标题位置','字号 · 颜色','间距 · 通用组件']):badge(2045,8825+i*49,s,'#eaf3fa',BLUE,21)
note(1630,9045,'“网页处理了吗？”\n当时只改了规范，追问后才应用到页面。',PALE[4],989)
scene('P3',3080,8600,990,790,'先确认一个视频页，再复用到第二段','第一个视频页可用后，要求同样布局和逻辑。','沿用机制图、视频、进度条；替换内容与时间点。','两段内容不同、播放方式一致的视频页。','PG',refs(('01a0bc49',[29,54,55,57])),color=PALE[0],method='先验证一页，再扩展；明确相同部分与需要替换的部分。')
for i,(s,im) in enumerate([('原理视频',D/'素材/原理视频-现存文件28秒.png'),('输入与输出',D/'素材/输入输出视频-现存文件66秒.png')]):
 xx=3122+i*473;window(xx,8760,431,256,s,PURPLE)
 image(im,xx+112,8809,299,164)
 for j in range(3):box(xx+19,8829+j*33,67,18,PALE[j],PALE[j])
 line([(xx+21,8990),(xx+409,8990)],PURPLE,sw=3)
text(3130,9064,'复用的是布局与控制；\n机制图、章节与时间点仍要分别对应。',24,PURPLE)
port(3110,8530,'D','接收选定视频与字幕',PURPLE)
bridge('P1','P2',label='选定新的底稿');bridge('P2','P3')
# Integrate all eight terrain examples; image structure mirrors the adopted three-page pattern.
port(123,9535,'F','接收校正后的 A/B 时间线',BLUE)
scene('P4',100,9630,1330,900,'八组案例，各用三页讲清差异','每组先 A，再 B，再双图对照；原文不能省。','按已确认结构扩展，并修切页闪烁与加载时序。','八组 × 三页 = 24 页地形案例。','PH',refs(('01a0bc49',[58,62,63,68,82,86,92,93])),style='open',color=PALE[2],method='样板可复用；每组原文、事件和演示含义仍需逐项核对。')
case_names=['语义漂移','特征纠缠','显式配平','隐式提纯','案例好于说明','引导采样与回滚','先推理后结论','语义退火']
for i,s in enumerate(case_names):
 xx=128+(i%4)*325;yy=9790+(i//4)*224
 text(xx+2,yy,s,22,BLUE)
 for j,l in enumerate(['A','B','A/B']):
  box(xx+j*99,yy+49,90,102,'#f1f7fa',BLUE);text(xx+22+j*99,yy+80,l,24,BLUE)
text(157,10257,'每组：先观察一种结果 → 看另一种 → 并排解释差异',23,GREEN)
scene('P5',1760,9630,2310,900,'投入章节：先比较三套分镜，再试交互','要三种十二格方向；原型使用已有真实任务。','比较数据地图、工作台、路径图，并制作可操作原型。','可试用的章节原型；首版仍被否定并重做。','PI',refs(('01a0bc49',[96,102,103,109,110])),style='open',color=PALE[0],method='图片比较表达方向；原型检验操作方式。两种检查不能互相代替。')
for i,(name,fn) in enumerate([('A 数据地图','投入控制-分镜-A-数据地图.png'),('B 任务工作台','投入控制-分镜-B-任务工作台.png'),('C 决策路径','投入控制-分镜-C-决策路径.png')]):
 xx=1800+i*427;paper(xx,9795,390,459,PALE[i]);image(C/'06-行动选择与投入控制/素材'/fn,xx+15,9810,360,379);text(xx+21,10205,name,25)
line([(3077,10010),(3197,10010)],PURPLE,True)
window(3230,9840,761,298,'可操作的原型 · 示意',PURPLE)
line([(3310,10074),(3900,10074)],MUTED,True);line([(3310,10074),(3310,9900)],MUTED,True)
for xx,yy in [(3350,9995),(3450,10020),(3550,9940),(3670,9965),(3820,9915)]:circ(xx,yy,7,PALE[0],PURPLE)
note(3290,10174,'首版不行 → 重做\n删标签栏和详情区，让位给讲述。',PALE[4],650)
bridge('P3','P4',[(3575,9490),(765,9490)],sides=('B','T'),label='继续接入已经确认的材料')
bridge('P4','P5')
# Four related adjustments: what changes, what must remain.
scene('P6',100,10820,1730,1070,'调整控制方式，同时保留满意的表现','手动翻页但保留过渡；标签可隐藏，缩放要保留。','改触发方式，处理标签、点位边界与新增页编辑。','逐页可讲的交互章节，以及需要逐项核对的修改。','PJ',refs(('01a0bc49',[112,116,117,125,126,156]),('01a0c158',[4,9,14,20,21])),style='open',color=PALE[3],method='一条修改要求同时说清“改什么”和“保留什么”，再按状态检查。',boundary='部分边界与格式项在历史盘点中仍是建议，不全部写成已修复；页面内编辑不等于自动保存文件。')
for i,(head,co) in enumerate([('改：由讲者手动翻页',BLUE),('留：翻页时的图形过渡',PURPLE),('改：标签密度与点位边界',GOLD),('留：缩放和页面内编辑',GREEN)]):
 xx=140+(i%2)*837;yy=10977+(i//2)*308;paper(xx,yy,785,256,PALE[i],True);text(xx+24,yy+18,head,28,co)
 if i==0:
  for j,l in enumerate(['←','第 n 页','→']):box(xx+47+j*224,yy+105,197,89,'#ffffff',co);text(xx+83+j*224,yy+132,l,26,co)
 elif i==1:
  circ(xx+96,yy+112,28,PALE[0],co);circ(xx+594,yy+147,28,PALE[1],co);line([(xx+154,yy+140),(xx+564,yy+171)],co,True);text(xx+253,yy+92,'同一对象延续',24,co)
 elif i==2:
  box(xx+34,yy+81,710,144,'#fffdf4',co)
  for j in range(4):circ(xx+104+j*157,yy+132,7,PALE[4],co)
  for j,l in enumerate(['短标签','按需隐藏','不压边界']):text(xx+54+j*213,yy+170,l,20,co)
 else:
  box(xx+44,yy+100,415,112,'#eff8f2',co);text(xx+68,yy+124,'可选中文字',28,co);line([(xx+57,yy+166),(xx+385,yy+166)],co,sw=2)
  badge(xx+511,yy+113,'−   缩放   +',PALE[3],co,26)
text(139,11643,'检查默认画面，也检查缩放后、翻页时、再次进入时。',24,GREEN)
# Overall review, multiple visual attempts, and selected reference implemented as HTML.
scene('P7',2210,10820,1860,1300,'检查整场讲述，补过渡，再按选定图重建','指出 36 / 37 页缺过渡，多轮比较后选回参考图。','补讲述衔接，按选定图重建第 37 页 HTML。','左右布局的知识过渡页与可编辑文字。','PK PL',refs(('01a0c158',[37,38,46,47,53,56,62,72,74])),style='open',color=PALE[4],method='局部能用之后，检查整场的铺垫、转折与收束；实现围绕最后的明确选择。',boundary='下面右图是9月21日历史渲染。图标与像素并非完全一致；可操作与持久化能力不能仅凭截图确认。')
for i,s in enumerate(['看整场讲述','定位缺少过渡','比较多轮生图','选回已有参考','重建 HTML']):
 xx=2247+i*358;box(xx,10980,319,80,'#fff9e5',GOLD);text(xx+20,11004,s,25,GOLD)
 if i<4:line([(xx+325,11020),(xx+348,11020)],GOLD,True)
for i,(cap,fn) in enumerate([('用户选定图 · 原始素材','37页-用户选定生图.png'),('HTML 历史渲染 · 9/21','37页-HTML历史渲染.png')]):
 xx=2247+i*921;text(xx+9,11129,cap,26,BLUE)
 paper(xx,11195,881,510,PALE[2+i]);image(C/'PPT课程制作复盘/证据/关键画面'/fn,xx+13,11210,855,482)
line([(3139,11442),(3160,11442)],BLUE,True)
note(2270,11760,'新生成的版本不一定更好。\n用户最后指定的参考，才是这一步的实现依据。',PALE[4],1730)
bridge('P5','P6',[(2915,10665),(965,10665)],sides=('B','T'),label='从“看图”进入“实际操作”')
bridge('P6','P7')
line([(4082,11688),(4160,11688),(4160,10949),(3920,10949),(3920,10969)],RED,True,True)
text(3410,10886,'发现缺口 → 回到对应页修改',22,RED)
# Adopted-version timeline and exact 44-page content map.
scene('P8',100,12540,3970,1110,'形成 44 页阶段版本：材料真正汇合成一场讲述','逐页检查格式、播放与可编辑性，再检查章节交接。','把选定材料合并到同一套网页 PPT，持续修正。','9 月 21 日的 44 页阶段课件；不等同最终全量验收。','PM',refs(('01a0bc49',[1,54,68,125,126,131]),('01a0c158',[9,14,37,46,74])),style='open',color=PALE[3],method='页数增长只统计同一条已采用版本；最后分别检查内容、操作和整场讲述。',boundary='页数以9月22日采集核对记录为依据；此图只复盘历史，不宣称所有建议均已修复。')
line([(226,12807),(3897,12807)],MUTED,True,sw=2)
for i,(num,cap,delta) in enumerate([('10','选定底稿','起点'),('11','加入第二段视频','+1'),('35','八组各三页','+24'),('42','合并投入章节','净增 7'),('43','补投入开场','+1'),('44','补知识过渡','+1')]):
 xx=150+i*650
 for k in range(3):box(xx+14-k*5,12687+k*7,415,85,'#ffffff',BLUE)
 text(xx+34,12710,num+' 页',35,BLUE);circ(xx+207,12800,8,PALE[i%5],BLUE)
 text(xx+4,12838,cap,26);badge(xx+459,12725,delta,PALE[i%5],MUTED,22)
text(149,12909,'8 组 × 3 页 = 24 页；投入章节用 8 页替换 1 页引入，因此净增 7 页。',24,MUTED)
# Native, individually editable page tiles.
for n in range(1,45):
 xx=151+((n-1)%11)*149;yy=13005+((n-1)//11)*82
 co=PALE[0] if n in (5,7) else PALE[2] if 10<=n<=33 else PALE[4] if 34<=n<=43 else PALE[3] if n==44 else '#eef1f4'
 box(xx,yy,128,58,co,co);text(xx+42,yy+14,str(n),23)
text(2020,13012,'1—9 页',29,INK);text(2290,13016,'建立问题与机制 · 含两段视频',27)
text(2020,13082,'10—33 页',29,BLUE);text(2290,13086,'八组 A / B / 双图案例',27)
text(2020,13152,'34—43 页',29,GOLD);text(2290,13156,'投入章节 · 含知识状态过渡',27)
text(2020,13222,'44 页',29,GREEN);text(2290,13226,'收束：人类负责什么判断',27)
text(2020,13303,'讲述链：理解机制 → 观察偏差 → 练习反馈 → 判断投入',27,GREEN)
bridge('P7','P8',[(3140,12360),(2085,12360)],sides=('B','T'),label='组合以后，再检查整场是否讲得通')
# Reusable methods, not generic decorating components.
G='takeaways'
text(100,13805,'把这段经历，变成下一次可以照做的 8 个动作',44)
methods=[('01  先接上已有材料','给出原文、案例和已选结果，\n让 AI 说明哪些沿用、还缺什么。'),('02  先交能判断的小产物','选一页、一段低清视频或一组分镜，\n明确这一轮准备判断什么。'),('03  同一内容比较表达','候选图使用同一段内容，\n分清表达差异与内容差异。'),('04  反馈落在具体位置','用格子、时间点、页码定位，\n同时说明应该看见什么变化。'),('05  改什么，也说留什么','更换触发方式时保留过渡，\n调整细节时保留已确认设计。'),('06  把选定结果交接齐','图片、提示词、镜头要求与待办\n一起保存，让下一步能直接接续。'),('07  先有样板，再扩展','复用已确认的布局与控制，\n逐项替换和核对内容、事件、时间点。'),('08  分层检查真实产物','分别看内容是否正确、操作是否可用、\n以及整场是否有铺垫、转折与收束。')]
for i,(h,b) in enumerate(methods):
 xx=110+(i%4)*1010;yy=13908+(i//4)*237
 paper(xx,yy,936,197,PALE[i%5],True);text(xx+25,yy+22,h,29,GREEN);text(xx+25,yy+86,b,25)
text(102,14434,'范围：9/1–9/21 制作历史。原图与示意分开标注；AI 历史完成报告不替代本次实际验收。',24,MUTED)
text(102,14482,'点击各场景的证据编号，或查看同目录《完整制作历程-来源.md》；四条线共覆盖原路径的 49 个节点。',23,MUTED)
save(14560,final=True)
render(D/'PPT-选底稿与复用.png',(50,8300,4100,1220),.8)
render(D/'PPT-扩展与交互.png',(50,9500,4100,2700),.7)
render(D/'PPT-定稿与成果.png',(50,12430,4100,2130),.7)
render(D/'关键转折-选定图到HTML.png',(2160,10780,1970,1370),.9)
render(D/'总览入口.png',(50,30,4120,790),.7)
