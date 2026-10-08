from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
COURSE=ROOT/'Course'
raw=(ROOT/'Course/PPT课程制作复盘/图解/课程制作主路径.mmd').read_text()
titles={k:re.sub('<br\\s*/?>',' · ',v) for k,v in re.findall(r'^\s*([A-Z]+\d*)\["([^\"]+)"\]',raw,re.M)}
A={}
def asset(k,title,path,kind):
 p=(ROOT/path).resolve();assert p.is_file(),p
 # Paths are explicit material registrations; the server grants no directory browsing.
 A[k]={'title':title,'path':str(p),'kind':kind}
asset('terrainArticle','需求表达与反馈闭环','Course/04-需求表达与反馈闭环/需求表达与反馈闭环.md','text')
asset('terrain','操作地形演示','Course/04-需求表达与反馈闭环/交互/思维地形.html','interactive')
asset('terrainGif','地形运动','Course/04-需求表达与反馈闭环/素材/04-terrain-balance-b.gif','image')
asset('dialogue','教学对话','Course/04-需求表达与反馈闭环/素材/04-dialogue-balance-b.png','image')
asset('ioArticle','信息输入与工具执行','Course/03-信息输入与工具执行/信息输入与工具执行.md','text')
asset('videoLlm','本地原理视频','Course/PPT/assets/video_llm.mp4','video')
asset('videoIo','输入输出视频','Course/PPT/assets/video_io.mp4','video')
asset('story1','首次输入分镜','Course/03-信息输入与工具执行/AI的输入与输出/素材/图片/视觉基准/镜头01_首次输入_十二格_清理版.png','image')
asset('story2','模型输出与工具请求分镜','Course/03-信息输入与工具执行/AI的输入与输出/素材/图片/镜头02_模型输出请求_十二格.png','image')
asset('story3','结果回流分镜','Course/03-信息输入与工具执行/AI的输入与输出/素材/图片/镜头03_结果回流与两次调用_十二格.png','image')
asset('quadArticle','行动选择与投入控制','Course/06-行动选择与投入控制/行动选择与投入控制.md','text')
asset('quad','操作四象限原型','Course/06-行动选择与投入控制/交互/投入决策-交互原型.html','interactive')
asset('quadImage','四象限图形','Course/06-行动选择与投入控制/素材/06-slide-03-article.png','image')
asset('website','课程阅读网站','Course/网页/index.html','interactive')
asset('ppt','打开课件','Course/PPT/AI协作-动态幻灯片.html','interactive')
asset('selected','选定的页面图片','Course/PPT课程制作复盘/证据/关键画面/37页-用户选定生图.png','image')
asset('implemented','历史页面实现','Course/PPT课程制作复盘/证据/关键画面/37页-HTML历史渲染.png','image')
asset('design','页面设计参数','Course/PPT/design.md','text')
for key,title,folder in [('articleSkill','解释型文章 Skill','explanatory-article'),('animationSkill','动画制作 Skill','manim-animation'),('videoSkill','完整视频 Skill','manim-video')]:
 asset(key,title,f'.agents/skills/{folder}/SKILL.md','text')
asset('videoSources','原理视频资料来源','Course/02-AI的能力从哪里来/大语言模型简要说明/素材/大语言模型简要说明-资料来源.md','text')
asset('ioSources','输入输出视频资料来源','Course/03-信息输入与工具执行/AI的输入与输出/素材/AI的输入与输出-资料来源.md','text')
asset('reflection','制作方法与实际经历','Course/PPT课程制作复盘/PPT与视频构建指南.md','text')
# Explicit learner worksheet, not a purported historical finished speech.
(OUT/'演讲编排练习.md').write_text('''# 演讲编排练习

这是一份供学员使用的编排模板，不是历史讲稿。

## 选一页课件

记录页面标题，写下这一页希望观众理解的一件事。

## 讲述与演示对应

| 环节 | 讲什么 | 屏幕展示什么 | 何时操作 |
| --- | --- | --- | --- |
| 引入 | 提出本页的问题 | 页面标题或核心图形 | 进入页面 |
| 展开 | 解释一个变化 | 视频片段或交互演示 | 播放、暂停或调整 |
| 收束 | 点出观众可以复用的做法 | 结果或对照画面 | 停止或重置 |
| 衔接 | 说明下一页要回答的问题 | 下一页的相关内容 | 翻页 |

## 检查

- 每个动作是否服务于正在说的内容？
- 视频播放时需要说话，还是留给观众观看？
- 演示结束后是否要重置？
- 上一页的结果是否能自然引出下一页？
''')
asset('speech','演讲编排练习模板',str((OUT/'演讲编排练习.md').relative_to(ROOT)),'text')
asset('terrainOriginal','AI 时代的思维框架','资料库/AI时代的思维框架.md','text')
asset('quadOriginal','先获得判断，再扩大投入','.trash/20260918-结构重构/资料库-旧结构/02-知识与原文/AI协作框架/ai_collaboration_framework.md','text')
asset('animationCode','输入输出动画 · 场景代码','Course/03-信息输入与工具执行/AI的输入与输出/代码/scenes.py','text')
asset('pageMap','课件页面与素材对应','Course/PPT课程制作复盘/页面与素材对应.md','text')
N={}
def node(k,summary,takeaway,assets):
 N[k]={'title':titles[k],'summary':summary,'takeaway':takeaway,'materials':assets.split()}
node('START','把已有文章、图形、视频和交互组织成可以现场讲述的课件。','沿任一条制作线阅读；点开模块查看材料，再沿相邻步骤继续。','reflection ppt')
node('T1','从已有地形文章与教学对话开始，保留内容依据。','先列出已有材料与用途，再补缺少的内容。','terrainArticle dialogue')
node('T2','对照文章含义，确定地形、小球、轨迹分别表达什么。','为每个图形对象指出对应的原文含义，避免只有视觉效果。','terrainArticle terrainGif')
node('T3','把映射规则整理成原型设计要求，设计小球和运动轨迹等参数。','把对象、状态、变化与操作入口列出来，再交给 AI 实现。','terrain terrainArticle')
node('T4','先生成可运行的 HTML 样例，以具体画面作为讨论对象。','先检查一份能操作的样例，再扩大实现范围。','terrain')
node('T5','将文章中的关系构建为 3D 地形呈现。','判断画面是否表达内容，不把某个技术引擎当成目标。','terrain terrainGif')
node('T6','操作原型并对照文章，调整表达、画面和运动参数。','指出调整位置和希望看到的变化，再回到同一位置检查。','terrain terrainArticle')
node('T7','地形演示与教学内容一起交付，供课程网站和 PPT 使用。','交接运行入口和对应内容，让下一环节可以接着使用。','terrain dialogue ppt')
node('V1','找到 3Blue1Brown 参考视频，研究它怎样用图形解释机制。','选一个具体参考，把喜欢的表达落实到可观察的画面。','videoSources videoLlm')
node('V2','从参考的官方资料取得技术架构、源码与制作线索。','区分内容参考与实现资料，两者共同支持制作。','videoSources')
node('V3','在本地还原参考内容，理解制作过程。这里提供的是现存本地视频。','先做可检查的范围，核对内容顺序与图形变化。','videoLlm videoSources')
node('V4','从还原过程提炼图形表达、动画实现与整片组织的要求。','保存能用于下一次的原则，避免把一次任务的规格写死。','reflection videoSkill')
node('V5','将方法分成文章、动画、完整视频三个 skills，供后续环节调用。','按职责拆分工作说明，让方法可以在多个环节复用。','articleSkill animationSkill videoSkill')
node('S1','用 explanatory-article 整理解释型文章，支持多条课程内容线。','先讲清内容，再选择图片、动画或交互表达。','articleSkill ioArticle')
node('S2','用 manim-animation 实现单段动画的图形、运动和转换。','把一个镜头内的变化落实为能逐段检查的实现。','animationSkill story2')
node('S3','用 manim-video 组织分镜、镜头、字幕与成片。','将文章、画面与视频时间线对应起来。','videoSkill story1 videoIo')
node('V6','收集输入输出机制相关的素材与文章。','先固定要解释的机制，让案例服务于主题。','ioSources ioArticle')
node('V7','调用文章 skill，将资料整理为解释型文章。','检查文章是否回答主题，再进入镜头设计。','ioArticle articleSkill')
node('V8','根据文章内容与表达方式安排镜头，确定需要多少段变化。','镜头数量由内容决定，不固定套用某个格数。','ioArticle story1 story2 story3')
node('V9','逐步生成连续分镜，让相邻画面呈现对象和关系的变化。','比较相邻格：新增了什么，之前的关系是否保留。','story1 story2 story3')
node('V10','根据已确认的分镜，调用动画和视频 skills 完成开发。','逐段检查实现是否保留分镜中的内容、状态与先后关系。','story1 animationSkill videoSkill videoIo')
node('V11','形成可接入 PPT 的视频产物。','交付成片与对应内容，并实际播放检查。','videoIo videoLlm')
node('W1','归集已有课程原始文章，确认各自的主题与用途。','先接上已有材料，不重复从零生成。','terrainArticle ioArticle quadArticle')
node('W2','按解释型文章要求整理课程文章。','保留内容依据，让结构、例子与图形服务于理解。','articleSkill ioArticle')
node('Q1','四象限内容来自已有思考和现成文章。','先说明两个维度的含义，再考虑图形布局。','')
node('Q2','按文章要求改写四象限内容，形成可阅读的解释。','让读者能从例子理解判断维度，而不只看到坐标图。','quadArticle articleSkill')
node('Q3','形成四象限文章与图形表达，供网站和 PPT 使用。','每个位置都应有依据；图形与文字使用同一版本的维度。','quadImage quad quadArticle')
node('G1','将地形原始文章整理为网站可用的课程文章。','把原理、例子与演示入口组织在一起。','terrainArticle articleSkill')
node('G2','让地形文章与可运行的 HTML 演示配合。','阅读解释后能操作，操作结果能回到文章中理解。','terrainArticle terrain')
node('W3','以 ce101.ifuryst.com 作为网站呈现参考。','明确借鉴的是结构、阅读方式还是视觉表达。','website')
node('W4','结合文章、skills 要求与参考样例，开发统一课程网站。','先明确内容与结构，再检查实际页面。','website articleSkill')
node('W5','将各篇文章、四象限和地形演示接入同一网站。','检查每项材料的入口、正文和交互是否对应。','website terrain quad')
node('W6','打开实际网页检查内容、结构与呈现效果。','把问题定位到文章、图形或实现环节，返回对应位置调整。','website')
node('W7','形成课程网站，其文章成为 PPT 大纲的内容依据。','同一内容可以用于阅读与讲述，但两者需要不同组织方式。','website ppt')
node('P1','确认演讲要求与讲述细节。','先确定观众要理解什么，以及现场要演示什么。','reflection speech')
node('P2','根据网站文章确定演讲大纲与内容顺序。','用现场讲述的顺序组织内容，不把文章逐段搬进课件。','website ppt')
node('P3','根据大纲与文字生成页面样式图片。','先看整页表达，判断内容重点与图文关系。','selected design')
node('P4','查看图片，确认采用的 UI 表达。','明确采用哪张图、保留哪些关系，再进入实现。','selected implemented')
node('P5','按照确认路径，将选定图片接入 PPT。所附历史页面同时提供 HTML 重建结果作对照。','把选定对象与页面实现对应起来，检查采用的内容是否保留。','selected implemented ppt')
node('P6','先确认视频与地形在 PPT 中的嵌入原型效果。','在页面中检查播放与操作，而不只检查单独文件。','ppt videoIo terrain')
node('P7','将视频与地形内容接入课件。','统一讲述与操作入口，同时保留各自的内容和运行方式。','ppt videoLlm videoIo terrain')
node('P8','确认四象限在 PPT 中的呈现与操作效果。','用真实内容操作样例，检查图形、文字与页面推进。','quad ppt')
node('P9','将四象限内容接入课件，与另一条接入支线汇合。','合并后检查页面衔接与操作的一致性。','ppt quad')
node('P10','各部分汇合后，从整场讲述检查内容和演示。','检查相邻页面之间的铺垫、解释与衔接。','ppt design speech')
node('P11','按问题所在位置优化大纲、页面或嵌入内容，需要时返回地形和视频制作。','修改具体对象后，回到整套课件检查影响。','ppt terrain videoIo')
node('P12','组织演讲稿、页面衔接与演示安排。这里提供学员练习模板，历史讲稿完成状态尚未核验。','将页面、讲述和操作逐项对应。','speech ppt')
node('P13','交付包含 PPT、嵌入内容、讲稿与演示安排的课程材料。讲稿部分使用练习模板。','让接收者知道从哪里打开、用哪些内容、如何演示。','ppt videoIo terrain quad speech')
assert set(N)==set(titles)
edges=[]
for ln in raw.splitlines():
 if '-->' not in ln and '.->' not in ln:continue
 label=re.findall(r'-\.([^\n]+?)\.->',ln);chain=[v.strip() for v in re.sub(r'-\.[^\n]+?\.->','-->',ln).split('-->')]
 if all(v in N for v in chain):
  edges.extend({'from':a,'to':b,'label':label[0] if label else ''} for a,b in zip(chain,chain[1:]))
(OUT/'节点材料.json').write_text(json.dumps({'title':'课程制作路径','nodes':N,'assets':A,'edges':edges},ensure_ascii=False,indent=2))
print(f'{len(N)} nodes, {len(A)} materials, {len(edges)} edges')
