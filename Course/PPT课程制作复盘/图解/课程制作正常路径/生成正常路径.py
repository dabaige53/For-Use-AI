from pathlib import Path
LIB=Path(__file__).parent.parent/'正常路径组件库/生成组件库.py'
exec(LIB.read_text().split('def start(')[0])
OUT=Path(__file__).parent
import io
_base_txt=txt
def txt(x,y,s,size=23,color=INK,width=None):
 s=re.sub(r' (?:(?:T|V|W|P|Q|G)\d+)(?= /|$|；)', '', s)
 s=re.sub(r'\s*/\s*$', '', s)
 e=_base_txt(x,y,s,size,color,width);e['strokeColor']=color;return e
SCENES=[]; SOURCES=[]
NODEFILE=OUT.parent/'课程制作主路径.mmd'
TERRAIN='Course/04-需求表达与反馈闭环/素材/04-terrain-balance-b.gif'
DIALOGUE='Course/04-需求表达与反馈闭环/素材/04-dialogue-balance-b.png'
STORY='Course/03-信息输入与工具执行/AI的输入与输出/素材/图片/视觉基准/镜头01_首次输入_十二格_清理版.png'
QUAD='Course/06-行动选择与投入控制/素材/06-slide-03-article.png'
LLM='Course/PPT课程制作复盘/图解/课程制作正常路径/素材/原理视频-现存文件抽帧.png'
IOVIDEO='Course/PPT课程制作复盘/图解/课程制作正常路径/素材/输入输出视频-现存文件抽帧.png'
CHOSEN='Course/PPT课程制作复盘/证据/关键画面/37页-用户选定生图.png'

def pic(path,x,y,w,h,caption=None):
 p=ROOT/path;im=Image.open(p)
 if im.format=='GIF':im.seek(im.n_frames//2)
 im=im.convert('RGB');buf=io.BytesIO();im.save(buf,format='PNG');raw=buf.getvalue();fid=hashlib.sha256(raw).hexdigest()[:24]
 FILES[fid]={'id':fid,'mimeType':'image/png','dataURL':'data:image/png;base64,'+base64.b64encode(raw).decode(),'created':1790208000000}
 scale=min(w/im.width,h/im.height);ww,hh=im.width*scale,im.height*scale
 el('image',x+(w-ww)/2,y+(h-hh)/2,ww,hh,fileId=fid,status='saved',scale=[1,1],crop=None)
 if path not in SOURCES:SOURCES.append(path)
def dot(x,y,c=BLUE,r=25):el('ellipse',x,y,r,r,backgroundColor=c)
def terrain(x,y,w,h):
 for j in range(8):
  line([(x+i*w/24,y+j*16+h*.25+math.sin(i/4)*h*.13+((i/24-.6)**2)*h*.3) for i in range(25)],'#9bb7cb')
 for i in range(0,25,4):
  z=y+h*.25+math.sin(i/4)*h*.13+((i/24-.6)**2)*h*.3;line([(x+i*w/24,z),(x+i*w/24,z+112)],'#c2ceda')
 line([(x+w*.1,y+h*.43),(x+w*.35,y+h*.33),(x+w*.57,y+h*.38),(x+w*.8,y+h*.51)],'#8c71b5',arrow=True)
 dot(x+w*.56,y+h*.36,PURPLE,25)
def scene(id,title,nodes,components,x,y,w=1460,h=770,sub=''):
 global group
 group=id
 txt(x,y,title,34)
 line([(x,y+54),(x+w,y+54)],COLORS['TVWP'.index(id[0])])
 SCENES.append(dict(id=id,title=title,nodes=nodes.split(),components=components,x=x,y=y,width=w,height=h))
 return x,y+103

def chapter(id,y,title,subtitle):
 global group
 group='chapter'+id;rect(80,y,3240,85,COLORS['TVWP'.index(id)],COLORS['TVWP'.index(id)]);txt(111,y+17,title,42)
def roles(x,y,w,u,a,o):
 for i,(label,s) in enumerate([('用户：',u),('AI：',a),('产出：',o)]):
  txt(x,y+i*45,label,23);txt(x+93,y+i*45,s,23,width=w-105)
def tag(x,y,label,text,c=GREEN,w=460):
 pill(x,y,text,c,w)
def bridge(points,label=None,lx=None,ly=None,dash=False):
 global group
 prev=group;group='links';line(points,GRAY,dash,True)
 if label:txt(lx if lx!=None else points[0][0]+18,ly if ly!=None else points[0][1]+10,label,21,GRAY)
 group=prev

def save(stage):
 heights={1:3200,2:5400,3:7650,4:10700};height=heights[stage]
 data=dict(type='excalidraw',version=2,source='https://excalidraw.com',elements=E,appState={'viewBackgroundColor':'#ffffff','gridSize':None},files=FILES)
 (OUT/'课程制作正常路径.excalidraw').write_text(json.dumps(data,ensure_ascii=False))
 render_svg(E,(0,0,3400,height),OUT/'课程制作正常路径.svg')
 render_png(E,(0,0,3400,height),OUT/'正常路径-全图.png',.25)
 boxes=[('00-全局关系',(50,30,3300,950)),('01-地形制作',(50,1000,3300,2150)),('02-视频制作',(50,3200,3300,2120)),('03-课程网页',(50,5400,3300,2180)),('04-PPT设计',(50,7650,3300,1060)),('05-PPT接入',(50,8750,3300,920)),('06-整体检查与讲述',(50,9730,3300,950))]
 for name,box in boxes:
  if box[1]+box[3]<=height:render_png(E,box,OUT/(name+'.png'),.6)
 (OUT/'场景与来源索引.json').write_text(json.dumps({'basis':str(NODEFILE),'scenes':SCENES,'assets':SOURCES},ensure_ascii=False,indent=2))
 print(json.dumps({'stage':stage,'scenes':len(SCENES),'nodes':len({n for s in SCENES for n in s['nodes']}),'elements':len(E),'images':len(FILES)},ensure_ascii=False))

# Overall relationship map, not a chronological chain.
group='overview'
txt(100,58,'与 AI 合作制作课件',55)
SCENES.append(dict(id='START',title='制作目标',nodes=['START'],components=[17],x=100,y=50,width=3200,height=900))
for xx,yy,w,title,c,body in [(120,280,710,'地形与教学对话',BLUE,'文章 → HTML 原型 → 可运行演示'),(120,583,710,'视频制作',PURPLE,'参考还原 → skills → 自己的视频'),(1260,280,760,'课程网页',GREEN,'多条文章线＋图形＋HTML 演示'),(2490,280,690,'现场 PPT',PEACH,'大纲与选图 → 嵌入 → 演讲安排')]:
 card(xx,yy,w,165,title,c);txt(xx+21,yy+87,body,24,width=w-42)
bridge([(840,362),(1242,362)],'HTML 演示＋地形文章',864,315)
bridge([(480,578),(480,490),(1470,490),(1470,459)],'skills 指导文章；输入输出文章进入网站',741,498,True)
bridge([(2033,363),(2470,363)],'网站文章支持大纲',2090,314)
bridge([(830,663),(2700,663),(2700,459)],'视频 → PPT',1990,685)
bridge([(812,291),(812,232),(2850,232),(2850,267)],'HTML 地形演示 → PPT',1520,195)
pill(1260,576,'四象限：原有思考 → 文章 → 图形',GREEN,740)
bridge([(2011,594),(2280,594),(2280,440),(2480,440)],'四象限接入',2050,555)

chapter('T',1030,'01  地形与教学对话','核心手法：通过 HTML 原型样例驱动，把文章表达与图形、运动参数逐步对齐。')
x,y=scene('T-A','收集文章 · 建立图形映射','T1 T2',[1,3],130,1210,sub='原始文章是内容依据；映射规则决定画面中的对象承担什么含义。')
doc(x+14,y+10,353,254,'地形相关文章',BLUE,7)
arrow(x+385,y+134,x+474,y+134)
for i,(a,b) in enumerate([('文章中的概念','图形对象'),('概念之间的关系','地形与空间关系'),('过程中的变化','小球与运动轨迹')]):
 yy=y+9+i*135;pill(x+493,yy+25,a,BLUE,342);arrow(x+849,yy+43,x+904,yy+43);pill(x+925,yy+25,b,PURPLE,491)

x,y=scene('T-B','构建 HTML 地形原型','T3 T4 T5',[2,4,6],1790,1210,sub='整理原型设计 skills，设计小球、轨迹等参数，构建 3D 地形呈现。')
browser(x+10,y+4,925,327,'HTML 地形原型');terrain(x+41,y+57,520,202)
for i,t in enumerate(['小球','轨迹','地形']):
 yy=y+73+i*67;txt(x+671,yy,t,22);line([(x+730,yy+18),(x+881,yy+18)],GRAY);dot(x+769+i*20,yy+10,PURPLE,17)
pill(x+39,y+274,'运行',BLUE,145);pill(x+204,y+274,'重置',GREEN,145)
roles(x+19,y+381,1420,'提供文章并确认原型表达。','整理原型设计 skills，实现图形与运动参数。','HTML 原型样例与 3D 地形呈现。')
bridge([(1620,1600),(1772,1600)])
bridge([(2520,1990),(2520,2050),(850,2050),(850,2100)],'调整原型',1450,2065)

x,y=scene('T-C','对照原文 · 调整原型','T6',[14,21],130,2150,sub='分别看表达是否对应、画面是否清楚、运动是否能说明过程。')
pic(TERRAIN,x+9,y+4,823,340,'现存教学素材 GIF 的中间静帧；用于展示地形产物。')
for i,(a,b) in enumerate([('表达','与文章含义对应'),('画面','图形和说明相互配合'),('运动','小球与轨迹呈现过程')]):
 yy=y+5+i*122;card(x+911,yy,506,103,a,[BLUE,PURPLE,GREEN][i]);txt(x+929,yy+62,b,23)
line([(x+1164,y+381),(x+1164,y+457),(x+236,y+457),(x+236,y+383)],'#9375ba',True,True)
txt(x+335,y+474,'查看 → 对照文章 → 调整 → 再操作',24,GRAY)
bridge([(115,2390),(76,2390),(76,2019),(1750,2019),(1750,1480),(1780,1480)],dash=True)

x,y=scene('T-D','交付地形演示与教学内容','T7',[11,16],1790,2150,sub='地形与教学内容一起交付，供网站阅读和 PPT 现场演示使用。')
pic(DIALOGUE,x+9,y+5,505,335,'现存教学对话素材；不是制作过程聊天。')
pic(TERRAIN,x+575,y+5,853,335,'现存地形素材静帧；完整交互保存在 HTML。')
tag(x+29,y+418,'A','HTML 地形演示 → 网站 G2 / PPT P6',BLUE,1340)
tag(x+29,y+473,'B','地形原文 → 文章整理 G1',GREEN,1340)
bridge([(1625,2517),(1772,2517)])
if '--stage=1' in sys.argv:save(1);sys.exit()

chapter('V',3230,'02  视频制作','先研究好的表达方式，把制作要求整理成 skills，再用自己的材料完成视频。')
x,y=scene('V-A','研究 3Blue1Brown · 提炼方法','V1 V2 V3 V4',[5,21],130,3410,sub='找最佳实践 → 获取官网技术架构与源码 → 本地还原 → 提炼制作要求与细节。')
card(x+15,y+11,461,287,'3Blue1Brown → 本地还原',PURPLE)
pic(LLM,x+39,y+73,410,172)
for i,(a,b) in enumerate([('官网资料','技术架构与相关源码'),('本地还原','沿着内容与时间线实现'),('方法提炼','制作要求与实现细节')]):
 yy=y+12+i*116;rect(x+631,yy,780,98,COLORS[i],COLORS[i]);txt(x+654,yy+20,a,24);txt(x+833,yy+20,b,24)
 line([(x+485,y+152),(x+562,y+152),(x+562,yy+42),(x+620,yy+42)],arrow=True)

x,y=scene('V-B','整理三个 skills','V5 S1 S2 S3',[6,12],1790,3410,sub='同一批制作经验，分别支持文章整理、单段动画和完整视频。')
tag(x+232,y+5,'F','制作要求与实现细节',YELLOW,949)
for i,(a,b,c) in enumerate([('explanatory-article','解释型文章','自己的输入输出文章\n网页中其他课程文章'),('manim-animation','动画制作','各个镜头的图形\n运动与转换'),('manim-video','完整视频','镜头安排、分镜\n整片组织与制作')]):
 xx=x+13+i*483;line([(x+709,y+44),(xx+219,y+115)],GRAY,True,True)
 card(xx,y+130,441,249,a,COLORS[i]);txt(xx+20,y+203,b,28);txt(xx+20,y+265,c,23)
arrow(x+711,y+391,x+711,y+450)
tag(x+40,y+468,'F','调用：文章整理 / 动画实现 / 视频制作',PURPLE,1340)
bridge([(1625,3764),(1772,3764)])

x,y=scene('V-C','整理输入输出文章 · 编排镜头','V6 V7 V8',[1,7,18],130,4350,sub='收集输入输出素材 → 用 skills 整理解释型文章 → 按内容和表达确定镜头安排。')
doc(x+12,y+8,358,263,'输入输出素材与原文',BLUE,7)
arrow(x+385,y+139,x+464,y+139)
doc(x+483,y+8,384,263,'解释型文章',GREEN,7)
tag(x+479,y+301,'F','explanatory-article',PURPLE,388)
arrow(x+882,y+139,x+967,y+139)
for i,t in enumerate(['首次输入','模型输出与工具执行','结果回流与后续输入']):pill(x+987,y+26+i*101,t,BLUE,433)

x,y=scene('V-D','生成分镜 · 开发视频','V9 V10 V11',[8,9,16],1790,4350,sub='逐步生成分镜图片，再调用动画与视频 skills 完成开发。')
pic(STORY,x+5,y+1,745,483,'首次输入现存十二格分镜；图中文字属于教学示例。')
for i,(a,b) in enumerate([('画面','对象、文字与关系'),('动画','出现、运动与转换'),('整片','镜头连接与完整视频')]):
 yy=y+13+i*124;txt(x+823,yy,a,25);rect(x+940,yy-2,473,66,COLORS[i],COLORS[i]);txt(x+959,yy+12,b,24)
arrow(x+1103,y+368,x+1103,y+414)
tag(x+817,y+432,'C','视频 → PPT P6',PURPLE,587)
tag(x+818,y+487,'D','文章 → 课程网站 W5',GREEN,586)
bridge([(1625,4704),(1772,4704)])
bridge([(2233,4180),(2233,4260),(794,4260),(794,4334)],'skills 支持内容与视频制作',1180,4272,True)
if '--stage=2' in sys.argv:save(2);sys.exit()

chapter('W',5430,'03  课程网页','文章整理与网站开发交织推进；四象限、地形、输入输出内容在统一网站汇合。')
x,y=scene('W-A','整理文章 · 汇入网站','W1 W2 Q1 Q2 Q3 G1 G2',[7,11,12],130,5610,w=3120,h=745,sub='已有文章与思考保持各自来源，按 explanatory-article 要求整理成供网站使用的文章。')
for i,(a,b,c) in enumerate([('其他课程原始文章','按文章要求整理','课程文章'),('四象限思考与现成文章','改写四象限文章','四象限内容与图形'),('地形原始文章','整理地形相关文章','地形文章＋HTML 演示'),('输入输出解释型文章','来自视频内容准备','直接作为网站内容')]):
 yy=y+9+i*116;pill(x+14,yy,a,COLORS[i],652);arrow(x+683,yy+18,x+781,yy+18);pill(x+802,yy,b,COLORS[i],679);arrow(x+1498,yy+18,x+1597,yy+18);pill(x+1612,yy,c,COLORS[i],742)
 line([(x+2375,yy+18),(x+2445,yy+18),(x+2445,y+217),(x+2510,y+217)],arrow=True)
browser(x+2532,y+49,551,363,'统一课程网站');doc(x+2552,y+118,218,243,'文章',BLUE,6);rect(x+2792,y+116,266,244,GREEN,GREEN);txt(x+2813,y+163,'图形\n交互\n演示',30)
tag(x+18,y+482,'F','explanatory-article 提供文章整理要求',PURPLE,2334)
tag(x+2533,y+482,'E','四象限 → PPT P8',GREEN,550)

x,y=scene('W-B','结合文章与参考 · 开发网站','W3 W4 W5',[5,12],130,6490,sub='网站样例提供呈现参照；原始文章和 skills 要求提供内容与写作依据。')
for i,(a,b,c) in enumerate([('内容依据','各条文章线与图形',BLUE),('文章要求','explanatory-article',PURPLE),('网站参考','ce101.ifuryst.com',GREEN)]):
 xx=x+9+i*486;card(xx,y+5,450,130,a,c);txt(xx+20,y+76,b,25)
 line([(xx+225,y+148),(xx+225,y+201),(x+715,y+201),(x+715,y+245)],arrow=True)
browser(x+224,y+267,1006,210,'课程网站')
for i,t in enumerate(['文章目录','正文与图形','交互演示']):rect(x+244+i*330,y+325,308,127,COLORS[i],COLORS[i]);txt(x+269+i*330,y+363,t,27)

x,y=scene('W-C','检查网页 · 调整内容','W6 W7',[14,16],1790,6490,sub='回顾内容、结构与呈现效果；修改后再次查看，形成整套课程网站。')
for i,(a,b) in enumerate([('文章表达','返回文章整理 W2'),('四象限图形','返回内容与图形 Q3'),('地形配合','返回文章＋演示 G2'),('网站呈现','返回实现 W4')]):
 yy=y+2+i*100;card(x+11,yy,465,82,a,COLORS[i]);arrow(x+491,yy+37,x+581,yy+37);pill(x+600,yy+17,b,COLORS[i],805)
line([(x+1328,y+411),(x+1328,y+458),(x+256,y+458),(x+256,y+409)],'#739782',True,True)
tag(x+17,y+508,'G','课程网站文章 → PPT 大纲 P2',GREEN,1390)
bridge([(880,6370),(880,6470)],'内容进入网站开发',906,6400)
bridge([(1625,6840),(1772,6840)])
if '--stage=3' in sys.argv:save(3);sys.exit()

chapter('P',7680,'04  现场 PPT','确认设计 → 两条内容接入支线 → 整体优化 → 演讲稿与演示安排。')
x,y=scene('P-A','① 确认演讲要求 · 制定大纲','P1 P2',[2,18],130,7860,sub='网站文章提供内容依据，现场讲述需要自己的顺序和重点。')
card(x+10,y+8,482,243,'用户确认',PEACH);txt(x+33,y+88,'演讲要求\n讲述细节\n现场演示安排',29)
tag(x+17,y+301,'G','课程文章',GREEN,471)
arrow(x+506,y+138,x+593,y+138)
pill(x+669,y+13,'演讲大纲',PEACH,642)
for i,t in enumerate(['建立理解','展开机制与案例','行动与判断']):
 xx=x+590+i*291;line([(x+986,y+60),(x+986,y+101),(xx+128,y+101),(xx+128,y+148)])
 card(xx,y+162,267,176,t,COLORS[i]);txt(xx+20,y+229,'确定内容重点\n形成页面顺序',23)

x,y=scene('P-B','生成样式图 · 确认 UI · 嵌入 PPT','P3 P4 P5',[10,13,21],1790,7860,sub='页面图片先提供可判断的视觉结果，选定对象明确后再进入 PPT。')
pic(CHOSEN,x+9,y+5,738,357,'历史选定图片实物：展示“明确采用哪张图”。')
arrow(x+763,y+175,x+856,y+175)
browser(x+881,y+34,540,297,'PPT 页面');pic(CHOSEN,x+903,y+88,496,218)
roles(x+890,y+370,550,'确认 UI。','生成并嵌入图片。','定稿页面。')
line([(x+670,y+412),(x+670,y+459),(x+249,y+459),(x+249,y+396)],'#9e80b5',True,True)
txt(x+22,y+476,'调整样式图片',23,GRAY)
bridge([(1624,8217),(1772,8217)])

x,y=scene('P-C','②③ 确认嵌入效果 · 接入内容','P6 P7 P8 P9',[11,13,12],130,8860,w=3120,h=770,sub='两条支线都从已确定的 PPT 页面设计出发，接入后汇合；并非先做完视频，才能开始四象限。')
for i,(title,path,label,action) in enumerate([('② 视频与地形',TERRAIN,'A / C  地形 HTML＋视频','确认播放、操作与页面配合'),('③ 四象限',QUAD,'E  四象限内容与图形','确认图形与操作在 PPT 中的效果')]):
 yy=y+5+i*260
 if i==0:
  pic(path,x+13,yy,190,192);pic(IOVIDEO,x+218,yy,195,192)
 else:pic(path,x+13,yy,401,192)
 tag(x+9,yy+212,label.split('  ')[0],label.split('  ')[1],COLORS[i],438)
 arrow(x+464,yy+107,x+574,yy+107)
 browser(x+590,yy+8,630,220,title+' / PPT 内嵌入原型')
 txt(x+611,yy+71,action,24,width=587);pill(x+613,yy+148,'查看嵌入效果',YELLOW,578)
 arrow(x+1240,yy+107,x+1348,yy+107)
 card(x+1373,yy+24,644,189,'确认后嵌入内容',GREEN);txt(x+1396,yy+94,'内容与操作方式\n对应 PPT 讲述顺序',25)
 line([(x+2039,yy+111),(x+2124,yy+111),(x+2124,y+249),(x+2267,y+249)],arrow=True)
card(x+2290,y+107,787,313,'汇合为整套课件',PEACH)
for j,t in enumerate(['图文讲述页','视频与地形演示','四象限交互内容']):pill(x+2314,y+194+j*65,t,COLORS[j],735)
bridge([(2520,8641),(2520,8770),(1690,8770),(1690,8840)],'确认接入',1860,8790)

x,y=scene('P-D','④ 回顾课件 · 优化内容与演示','P10 P11',[14,21],130,9850,sub='各部分汇合后，检查整体是否讲得通、看得清、用得顺。')
for i,(a,b,c) in enumerate([('内容与逻辑','大纲与内容 P2',BLUE),('页面与样式','样式图片 P3',PURPLE),('嵌入与演示','接入原型 P6 / P8',GREEN)]):
 yy=y+9+i*119;card(x+13,yy,483,94,a,c);arrow(x+516,yy+40,x+619,yy+40);pill(x+642,yy+22,'返回优化：'+b,c,775)
line([(x+1337,y+369),(x+1337,y+419),(x+238,y+419),(x+238,y+372)],'#8a749e',True,True)
tag(x+19,y+454,'','源内容调整 → 地形演示 / 视频制作 → 接入课件',GREEN,1398)

x,y=scene('P-E','⑤ 编写讲稿 · 安排演示 · 交付','P12 P13',[15,16],1790,9850,sub='把每段讲述、页面衔接和演示操作对应起来，便于现场使用。')
for j,t in enumerate(['对应页面','讲述与衔接','演示安排']):txt(x+17,y+42+j*94,t,23,GRAY)
for i,(a,b,c) in enumerate([('内容引入','说明本段要点','准备演示'),('机制展开','连接前后内容','播放或操作'),('内容收束','衔接下一部分','结束或重置')]):
 xx=x+226+i*402
 for j,s in enumerate([a,b,c]):pill(xx,y+34+j*94,s,COLORS[j],374)
for i,t in enumerate(['PPT','嵌入内容','演讲稿与细节']):
 xx=x+13+i*487;pill(xx,y+391,t,COLORS[i],450)
bridge([(2880,9640),(2880,9720),(850,9720),(850,9830)],'整体回顾',1470,9742)
bridge([(1620,10222),(1770,10222)])

# Preserve exact source nodes and relations for traceability.
raw=NODEFILE.read_text()
nodes=dict(re.findall(r'^\s*([A-Z]+\d*)\["([^\"]+)"\]',raw,re.M))
covered=[n for sc in SCENES for n in sc['nodes']]
assert set(nodes)==set(covered),(set(nodes)-set(covered),set(covered)-set(nodes))
assert len(covered)==len(set(covered))
edges=[]
for ln in raw.splitlines():
 if '-->' not in ln and '.->' not in ln:continue
 label=re.findall(r'-\.([^\n]+?)\.->',ln)
 clean=re.sub(r'-\.[^\n]+?\.->','-->',ln)
 chain=[a.strip() for a in clean.split('-->')]
 if all(a in nodes for a in chain):
  for a,b in zip(chain,chain[1:]):edges.append(dict(source=a,target=b,label=label[0] if label else '',kind='guidance_or_feedback' if label else 'flow'))
assert len({e['id'] for e in E})==len(E)
save(4)
index=json.loads((OUT/'场景与来源索引.json').read_text());index.update(nodes=nodes,edges=edges)
(OUT/'场景与来源索引.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
for sid in ['T-B','V-D','P-B','P-E']:
 sc=next(s for s in SCENES if s['id']==sid)
 render_png(E,(sc['x']-20,sc['y']-20,sc['width']+40,sc['height']+40),OUT/(sid+'-细节.png'),.85)
parts=['# 课程制作正常路径：来源与阅读说明\n','本图以用户确认的 [课程制作主路径](../课程制作主路径.mmd) 为内容主线，应用本轮确认的通用组件库。地形、视频、网站、PPT 四条线按主题展开；不是全程严格串行的时间线。\n',f'覆盖 {len(nodes)} 个源节点、保留 {len(edges)} 条源关系。画布将相邻步骤合并成 {len(SCENES)-1} 个制作场景，另含全局入口。跨区依赖以总览连线和产物名称表达；全部源关系及节点位置见 [场景索引](场景与来源索引.json)。\n','## 画布与组件\n','| 场景 | 原路径节点 | 采用组件编号 |\n|---|---|---|']
for sc in SCENES:parts.append(f'| {sc["id"]} {sc["title"]} | {", ".join(sc["nodes"])} | {", ".join(map(str,sc["components"]))} |')
parts+=['\n组件编号对应 [通用组件库](../正常路径组件库/组件库使用说明.md)。本图按内容选择组件，并未要求用满所有类型。\n','## 跨线交接索引（画布不显示字母编号）\n','| 标签 | 内容 | 去向 |\n|---|---|---|\n| A | 可运行的 HTML 地形演示 | 网站 G2；PPT P6 |\n| B | 地形原始文章 | 文章整理 G1 |\n| C | 视频 | PPT P6 |\n| D | 输入输出解释型文章 | 网站 W5 |\n| E | 四象限内容和图形 | PPT P8 |\n| F | 三个 skills | 文章 V7 / W2 / Q2 / G1；动画与整片 V8 / V10 |\n| G | 网站文章 | PPT 大纲 P2 |\n','## 图片与证据\n']
for src in SOURCES:parts.append(f'- [{Path(src).name}]({ROOT/src})')
parts+=['\n地形 GIF 使用现存文件中间静帧，静帧本身不代替 HTML 交互；教学对话与分镜中的文字是课程教学内容，不是制作聊天。视频图片由现存 MP4 抽取（原理 0:28、输入输出 1:06），不是历史故障截图。原型窗口、大纲层级和讲稿表格是关系与组织方式示意。第 37 页配图是历史选定图片；旁边的嵌入窗口是按新确认主路径绘制的示意，不据此断言历史该页最终用图片直接嵌入（历史实现另有 HTML 重建）。\n','## 内容与状态边界\n','- 以最新确认主路径为准，不混入第二张失败与返修图，也不沿用早期被否决的完整路径图。正常反馈回路保留。\n- 本地还原参考视频是路径中的实际动作，不宣称与原片完全一致。\n- PPT 样式图片的生成与采用按 P3—P5 表达；外部底稿的完整生成历史不作补写。\n- P12 / P13 是已确认的讲稿与完整交付环节；本图没有生成讲稿，也没有把这些节点标成已核验完成。\n- 图形、文字与连线是可编辑的原生元素；真实配图内嵌。连线端点未绑定，移动局部图形后需检查连线。\n- PNG / SVG 根据同一组坐标生成，用于预览；手绘笔触可能与 Excalidraw 原生渲染略有不同。\n','## 支持材料\n','- [PPT 与视频构建指南](../../PPT与视频构建指南.md)\n- [生图与分镜证据](../../生图与分镜证据.md)\n- [页面与素材对应](../../页面与素材对应.md)\n- [来源与完整性](../../来源与完整性.md)\n']
(OUT/'课程制作正常路径-来源.md').write_text('\n'.join(parts))
print(json.dumps({'covered':len(nodes),'sourceEdges':len(edges),'nativeImages':len(FILES)},ensure_ascii=False))
