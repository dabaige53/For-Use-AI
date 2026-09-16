from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parent.parent
C = dict(ink="#18324A", blue="#1769AA", deep="#163A5F", pale="#EAF4FB", soft="#7A9AB8", rule="#C9D8E5", muted="#536B80", white="#FFFFFF", warn="#DCECF7")
FONT = "'PingFang SC','Noto Sans CJK SC','Microsoft YaHei',sans-serif"
ACTIVE_NAME = 'diagram'

def q(v):
    return int(round(float(v) / 4) * 4)

def txt(x,y,s,size=18,weight=500,anchor="middle",fill=None):
    x,y,size=q(x),q(y),max(16,q(size))
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill or C["ink"]}">{escape(s)}</text>'

def lines(x,y,items,size=18,weight=500,anchor="middle",gap=25,fill=None):
    return "".join(txt(x,y+i*gap,s,size,weight,anchor,fill) for i,s in enumerate(items))

def box(x,y,w,h,label,sub=None,focal=False,fill=None,stroke=None,rx=8):
    x,y,w,h,rx=map(q,(x,y,w,h,rx))
    fc=fill or (C['pale'] if focal else C['white']); sc=stroke or (C['blue'] if focal else C['soft'])
    def wrap(value):
        limit=max(4,int((w-24)/16)); result=[]; line=''; width=0
        for ch in value:
            advance=1 if ord(ch)>255 else .55
            if width+advance>limit: result.append(line); line=''; width=0
            line+=ch; width+=advance
        if line: result.append(line)
        return result
    items=[(line,600,C['ink']) for line in wrap(label)]
    if sub: items += [(line,400,C['muted']) for line in wrap(sub)]
    first=y+h/2-(len(items)-1)*10+4
    t=''.join(txt(x+w/2,first+i*20,line,16,weight,fill=color) for i,(line,weight,color) in enumerate(items))
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fc}" stroke="{sc}" stroke-width="{2 if focal else 1.5}"/>'+t

def arrow(points, accent=False, dashed=False, label=None, lx=None, ly=None):
    color=C['blue'] if accent else C['soft']; marker=f'{ACTIVE_NAME}-arrow-blue' if accent else f'{ACTIVE_NAME}-arrow'
    points=[(q(x),q(y)) for x,y in points]
    if len(points) < 3:
        d='M '+' L '.join(f'{x} {y}' for x,y in points)
    else:
        d=f'M {points[0][0]} {points[0][1]}'
        for i in range(1,len(points)-1):
            ax,ay=points[i-1]; bx,by=points[i]; cx,cy=points[i+1]; r=8
            p1=(bx-r*(1 if bx>ax else -1),by) if ax!=bx else (bx,by-r*(1 if by>ay else -1))
            p2=(bx+r*(1 if cx>bx else -1),by) if cx!=bx else (bx,by+r*(1 if cy>by else -1))
            d+=f' L {p1[0]} {p1[1]} Q {bx} {by} {p2[0]} {p2[1]}'
        d+=f' L {points[-1][0]} {points[-1][1]}'
    s=f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" marker-end="url(#{marker})"'+(' stroke-dasharray="6 5"' if dashed else '')+'/>'
    if label:
        lx,ly=q(lx),q(ly); w=q(max(64,len(label)*16)); s+=f'<rect x="{q(lx-w/2)}" y="{q(ly-20)}" width="{w}" height="24" fill="#FFFFFF"/>'+txt(lx,ly,label,16,500,fill=color)
    return s

def base(title,desc,body,w=960,h=600):
    prefix=ACTIVE_NAME
    defs=f'''<defs><marker id="{prefix}-arrow" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><polygon points="0 0,8 4,0 8" fill="{C['soft']}"/></marker><marker id="{prefix}-arrow-blue" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><polygon points="0 0,8 4,0 8" fill="{C['blue']}"/></marker><marker id="{prefix}-arrow-link" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><polygon points="0 0,8 4,0 8" fill="{C['deep']}"/></marker></defs>'''
    elements=re.findall(r'<(?:path|line|rect|text)\b[^>]*(?:/>|>.*?</text>)',body)
    connectors=''.join(e for e in elements if e.startswith(('<path','<line')))
    shapes=''.join(e for e in elements if e.startswith('<rect'))
    labels=''.join(e for e in elements if e.startswith('<text'))
    layered=connectors+shapes+labels
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{prefix}-title {prefix}-desc"><title id="{prefix}-title">{escape(title)}</title><desc id="{prefix}-desc">{escape(desc)}</desc>{defs}<rect width="{w}" height="{h}" fill="#FFFFFF"/>{txt(40,56,title,28,650,'start',C['deep'])}{layered}</svg>'''
    html=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>html,body{{margin:0;background:#fff}}body{{font-family:{FONT}}}svg{{display:block;width:100%;height:auto}}</style></head><body>{svg}</body></html>'''
    return html, '<?xml version="1.0" encoding="UTF-8"?>\n'+svg

def pipeline(title,desc,labels,subs=None,foot=None,w=960):
    body=''; n=len(labels); gap=24; bw=(w-80-gap*(n-1))/n; y=210
    for i,l in enumerate(labels):
        x=40+i*(bw+gap); body+=box(x,y,bw,92,l,subs[i] if subs else None,focal=i==n-1)
        if i<n-1: body+=arrow([(x+bw,y+46),(x+bw+gap,y+46)])
    if foot: body+=f'<rect x="40" y="392" width="{w-80}" height="92" rx="8" fill="{C["pale"]}" stroke="{C["rule"]}"/>'+lines(w/2,424,foot,16,500,gap=24)
    return base(title,desc,body,w,600)

def problem_map():
    labs=['资料','本轮输入','模型输出','程序执行','核对成果']; errs=['遗漏','误解','编造','执行失败','不适用']; body=''
    for i,(l,e) in enumerate(zip(labs,errs)):
        x=40+i*184; body+=box(x,175,144,74,l,focal=i==4)
        if i<4: body+=arrow([(x+144,212),(x+184,212)])
        body+=arrow([(x+72,249),(x+72,330)],dashed=True)
        body+=box(x+12,330,120,54,e,fill='#F7FAFC',stroke=C['rule'])
    body+=f'<rect x="152" y="440" width="656" height="64" rx="8" fill="{C["pale"]}" stroke="{C["blue"]}"/>'+txt(480,480,'这些环节是排查入口；同一偏差可能有多个原因',16,600)
    return base('从偏差反查工作链','五个工作环节及常见偏差类型；提示它们只是排查入口，不是唯一原因。',body)

def evidence():
    body=''; layers=[(250,360,460,82,'对照原始材料','可复核具体对应关系',True),(190,245,580,82,'提供成果','文件、链接、运行结果',False),(130,130,700,82,'声称完成','最抽象，仍需进一步查看',False)]
    for x,y,w,h,a,b,f in layers: body+=box(x,y,w,h,a,b,focal=f)
    body+=arrow([(480,212),(480,245)],accent=True); body+=arrow([(480,327),(480,360)],accent=True)
    body+=txt(480,500,'证据逐层具体，但“更具体”不等于严格证明',16,500,fill=C['muted'])
    return base('证据如何变得更具体','从声称完成到提供成果，再到对照原始材料；这是核对层次，不是形式证明。',body)

def context():
    items=['规则','用户任务','选取历史','工具定义','取得资料']; body=''
    for i,l in enumerate(items):
        x=50+i*170; body+=box(x,145,140,62,l,focal=l=='选取历史'); body+=arrow([(x+70,207),(x+70,330)])
    body+=box(80,330,800,92,'本轮输入','应用组织后交给模型',True)
    body+=box(70,430,220,62,'已保存的记录','保存不等于选入',False,fill='#F7FAFC')
    body+=arrow([(290,461),(310,461),(310,422)],dashed=True,label=None)
    body+=txt(700,452,'保存 ≠ 选入',20,650,fill=C['blue'])
    body+=txt(700,482,'路径 ≠ 文件内容',17,500,fill=C['muted'])
    return base('本轮输入由多种来源组成','规则、任务、相关历史、工具定义与取得资料被程序组织成本轮输入；保存不等于选入。',body)

def tool_loop():
    actors=['用户','程序','模型','工具']; xs=[112,352,608,848]; body=''
    for x,a in zip(xs,actors): body+=box(x-60,96,120,48,a,focal=a=='程序')+f'<line x1="{x}" y1="144" x2="{x}" y2="520" stroke="{C["rule"]}" stroke-width="1.5" stroke-dasharray="4 4"/>'
    msgs=[(112,352,180,'提交任务'),(352,608,224,'组织输入并调用模型'),(608,352,276,'工具请求'),(352,848,324,'执行工具'),(848,352,376,'结果回程序'),(352,608,436,'更新输入，再次调用'),(608,352,484,'最终回答'),(352,112,516,'交给用户')]
    for a,b,y,l in msgs: body+=arrow([(a,y),(b,y)],accent=l in ['更新输入，再次调用','最终回答'],label=l,lx=(a+b)/2,ly=y-16)
    body+=txt(610,555,'成功结果或错误信息，都先回程序再决定下一步',16,500,fill=C['muted'])
    return base('一次任务可以包含多次模型调用','用户、程序、模型和工具之间的时序；工具结果或错误先回程序，再进入更新后的输入。',body)

def selection():
    body=box(40,105,280,410,'候选历史与资料','并非全部进入本轮',False,fill='#F7FAFC')
    for i,l in enumerate(['反馈 ID 与原文','统计口径','输出约束','旧草稿 / 闲聊']): body+=box(65,175+i*72,230,50,l,focal=False,fill='#FFFFFF')
    body+=arrow([(320,250),(390,250),(390,300)],accent=True,label='选择',lx=352,ly=216)
    body+=box(390,230,190,140,'选择器','相关性 · 边界 · 可用性',True)
    body+=arrow([(580,300),(690,300)],accent=True)
    body+=box(690,245,220,110,'本轮输入','为下次活动改进服务',False)
    body+=txt(480,550,'选入：目标、原文、口径、约束　｜　移出：旧草稿、放弃方案、闲聊',16,500,fill=C['muted'])
    return base('上下文选择服务于当前任务','从历史与资料中选取相关内容构成本轮输入，无关记录留在保存状态。',body)

def feedback():
    return pipeline('可执行反馈写清偏差、动作与验收','以F09的真实修订说明：先指出误分，再明确保留原文、修改分类、重算计数并核对。',['观察具体偏差','指明保留 / 修改 / 验收','产出新结果','按验收点核对'],['F09 被误分为声音问题','保留原文；改归练习与节奏','重新列 ID 并计数','声音 2 条；节奏 5 条'],['F09：“声音清楚，但演示切换得太快。”','反馈指出具体误分与通过条件，才能复核。'])

def execution():
    return pipeline('把检查任务变成可复核执行','从定义任务到核对十二条样本、按ID分类、人工复核并形成报告。',['任务定义','核对 12 条样本','带 ID 分类','人工复核','报告'],['范围与口径','逐条保留来源','错误可回溯','处理边界样本','结论与证据'],['ID 贯穿样本、分类与报告，便于复查。'])

def evidence_chain():
    body=''; labs=[('原始反馈 ID','事实来源'),('分类计数','汇总事实'),('结论','对事实的解释'),('建议','下一步选择')]
    for i,(a,b) in enumerate(labs):
        x=60+i*225; body+=box(x,210,180,90,a,b,focal=i==0)
        if i<3: body+=arrow([(x+180,255),(x+225,255)])
    body+=f'<path d="M736 300 L736 372 Q736 380 728 380 L520 380 Q512 380 512 372 L512 300" fill="none" stroke="{C["rule"]}" stroke-width="1.5" stroke-dasharray="4 4"/>'+txt(624,412,'建议应能追溯依据，但仍属于判断',16,500,fill=C['muted'])
    body+=f'<rect x="192" y="460" width="576" height="56" rx="8" fill="{C["pale"]}" stroke="{C["rule"]}"/>'+txt(480,496,'事实：ID 与计数　｜　判断：结论与建议',16,600)
    return base('从原始反馈到建议的证据链','原始反馈ID经过分类计数支持结论，建议与事实保持区分。',body)

def alignment():
    marker=f'{ACTIVE_NAME}-arrow'; body=f'<line x1="160" y1="496" x2="880" y2="496" stroke="{C["deep"]}" stroke-width="2" marker-end="url(#{marker})"/><line x1="160" y1="496" x2="160" y2="96" stroke="{C["deep"]}" stroke-width="2" marker-end="url(#{marker})"/><line x1="520" y1="112" x2="520" y2="496" stroke="{C["rule"]}" stroke-width="1.5"/><line x1="160" y1="304" x2="864" y2="304" stroke="{C["rule"]}" stroke-width="1.5"/>'
    body+=txt(520,544,'下一次反馈前的投入与承诺：低 → 高',16,600)+lines(76,272,['有证据支持','的对齐'],16,600,gap=24)
    body+=txt(132,476,'低',16,500,fill=C['muted'])+txt(132,120,'高',16,500,fill=C['muted'])
    for x,y,l,sub,f in [(336,400,'探索','低投入 · 低对齐',False),(336,208,'轻量交付','低投入 · 高对齐',True),(704,208,'深度建设','高投入 · 高对齐',True),(704,400,'高暴露','高投入 · 低对齐',False)]: body+=box(x-104,y-44,208,88,l,sub,focal=f)
    body+=txt(520,584,'坐标描述下一次反馈前的承诺，不表示累计投入或能力等级',16,500,fill=C['muted'])
    return base('投入与对齐的四种状态','横轴是下一次反馈前的投入与承诺，纵轴是有证据支持的对齐程度。',body)

def knowledge():
    body=txt(560,104,'是否掌握知识',20,650)+txt(392,136,'否',16,600,fill=C['muted'])+txt(728,136,'是',16,600,fill=C['muted'])
    body+=lines(88,280,['是否','意识到'],20,650,gap=28)+txt(176,224,'是',16,600,fill=C['muted'])+txt(176,408,'否',16,600,fill=C['muted'])
    body+=f'<line x1="544" y1="152" x2="544" y2="496" stroke="{C["rule"]}" stroke-width="1.5"/><line x1="208" y1="324" x2="880" y2="324" stroke="{C["rule"]}" stroke-width="1.5"/>'
    cells=[(224,160,'知道自己不知道','明确缺口'),(560,160,'知道自己知道','可陈述知识'),(224,344,'不知道自己不知道','盲区'),(560,344,'不知道自己知道','隐性经验')]
    for x,y,a,b in cells: body+=box(x,y,304,136,a,b,focal=a=='知道自己不知道')
    body+=txt(544,560,'用于实践自查；两项均为“是 / 否”，不是量表或等级',16,500,fill=C['muted'])
    return base('知识的四种自知状态','以是否意识到和是否掌握知识组成四象限；该图用于实践自查，不是量表或等级。',body)

def action_network():
    body=''
    for y in [176,320,464]:
        body+=arrow([(320,y-12),(608,y-12)])+arrow([(608,y+12),(320,y+12)])
    for x in [240,688]:
        for y in [176,320]:body+=arrow([(x,y+32),(x,y+112)])
    for x,y,l in [(240,176,'提问'),(688,176,'研究'),(240,320,'比较'),(688,320,'原型'),(240,464,'验证'),(688,464,'收敛')]:
        body+=box(x-80,y-32,160,64,l,focal=l=='验证')
    body+=txt(480,560,'按当前问题选择入口；连线表示可尝试的转向',16,500,fill=C['muted'])
    return base('行动之间可以往返与切换','提问与研究、比较与原型、验证与收敛之间可以往返，并可根据发现向下游转向。',body)

def production():
    return pipeline('课程从资料到成片的制作链','既有资料与讨论转为文章、图形设计和动画代码，静音预览已完成，旁白成片待制作。',['资料与讨论','文章','图形设计','动画代码','静音预览','旁白成片'],['既有输入','已形成','本轮制作','已实现','已完成','待制作'],['状态只描述“AI 的输入与输出”课程现有输入与产出。'],w=1280)

def revision():
    body=txt(250,105,'早期方案',20,650)+txt(710,105,'当前方案',20,650)
    body+=box(70,145,360,110,'九镜 · 96 状态','细分阶段多，叙事链较长')
    body+=arrow([(430,200),(520,200)],accent=True,label='收敛',lx=475,ly=182)
    body+=box(520,145,370,110,'三主镜头','首次输入 → 生成执行 → 结果回流',True)
    body+=box(70,330,360,125,'原图细节','伪代码 · 多余箭头 · 阴影')
    body+=arrow([(430,392),(520,392)],accent=True,label='修订',lx=475,ly=374)
    body+=box(520,315,370,155,'按真实 Schema 重建','第三镜强调：更新输入 → 再次调用',True)
    body+=txt(480,535,'两组对照记录真实修订，不模拟成果截图',17,500,fill=C['muted'])
    return base('分镜与图形如何收敛','输入输出课程从早期九镜九十六状态收敛为三主镜头；图形按真实Schema修订，第三镜突出更新输入后再次调用。',body)

DIAGRAMS={
'01-problem-map':problem_map,'01-evidence':evidence,'03-context':context,'03-tool-loop':tool_loop,
'04-context-selection':selection,'04-feedback':feedback,'05-execution':execution,'05-evidence-chain':evidence_chain,
'06-alignment':alignment,'06-knowledge':knowledge,'06-action-network':action_network,'07-production':production,'07-revision':revision}

for name,fn in DIAGRAMS.items():
    ACTIVE_NAME=name
    OUT = next(ROOT.glob(name[:2]+'-*'))/'配图'
    OUT.mkdir(exist_ok=True)
    html,svg=fn(); (OUT/f'{name}.html').write_text(html,encoding='utf-8'); (OUT/f'{name}.svg').write_text(svg,encoding='utf-8')
print(f'generated {len(DIAGRAMS)} html and {len(DIAGRAMS)} svg files in {OUT}')
