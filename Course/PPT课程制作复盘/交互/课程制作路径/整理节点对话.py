from pathlib import Path
import re,json
OUT=Path(__file__).resolve().parent
BASE=OUT.parents[1]/'对话数据/Codex'
def message(prefix,num,images=()):
 p=next(BASE.glob(prefix+'*.md'));s=p.read_text()
 m=re.search(rf'^## M{num:03d} · ([^\n]+)\n(.*?)(?=^## M|\Z)',s,re.M|re.S)
 body=re.sub(r'^\s*来源：[^\n]+\n','',m[2]).strip()
 body=re.sub(r'<image[\s\S]*?</image>','',body).strip().removesuffix('喵～').strip()
 return {'role':'user' if ' · user ·' in m[1] else 'assistant','text':body,'images':list(images),'source':{'file':p.name,'message':f'M{num:03d}'}}
video={'title':'大语言模型简明解释','label':'YouTube · 3Blue1Brown','description':'用动画呈现语言模型预测下一个词的过程。','url':'https://www.youtube.com/watch?v=LPZh9BOjkQs'}
code={'title':'3b1b / videos · chm.py','label':'GitHub · 动画源码','description':'参考视频的场景代码，包含对话卷轴、词语预测与训练过程。','url':'https://github.com/3b1b/videos/blob/master/_2024/transformers/chm.py'}
R={
'V1':{'links':[video],'messages':[message('01a09ee5',157),message('01a09ee5',158)]},
'V2':{'links':[code,{'title':'视频官方图文版','label':'3Blue1Brown','description':'视频对应的官方图文讲解。','url':'https://www.3blue1brown.com/lessons/mini-llm/'}],'messages':[message('01a0a377',1),message('01a0a377',3)]},
'V3':{'links':[code],'messages':[message('01a0a377',38),message('01a0a377',39)]},
'V9':{'links':[],'messages':[message('01a0a41b',33),message('01a0a41b',34)],'images':['story1','story2','story3']},
'P4':{'links':[],'messages':[message('01a0c158',72,['selected']),message('01a0c158',74,['implemented'])]}
}
for node_id,asset in [('S2','animationSkill'),('S3','videoSkill')]:
 R[node_id]={'links':[{'asset':asset}], 'messages':[message('01a0a37e',11),message('01a0a37e',13)]}
for node_id in ['S1','V5']:
 R[node_id]={'links':[{'asset':'articleSkill'},{'asset':'animationSkill'},{'asset':'videoSkill'}], 'messages':[message('01a0a37e',16),message('01a0a37e',19)]}
R['V8']={
 'links':[{'asset':'ioArticle','title':'信息输入与工具执行 · 文章','description':'镜头规划的内容依据。'}, {'asset':'animationSkill','title':'manim-animation · 动画制作','description':'将对象、状态变化和动作组织为镜头。'}],
 'messages':[message('01a0a41b',27),message('01a0a41b',28),message('01a0a41b',29),message('01a0a41b',30)],
 'images':['story1','story2','story3']
}
R['V8']['messages'][1]['excerpt']=R['V8']['messages'][1]['text'].split('\n\n')[0]
R['V10']={'links':[{'asset':'ioArticle','title':'信息输入与工具执行 · 文章','description':'视频内容与分镜的依据。'}],
 'messages':[message('01a0a87b',1),message('01a0a87b',3),message('01a0a87b',22),message('01a0a87b',23)],
 'images':['story1']}
R['V10']['messages'][0]['excerpt']='代码制作，480p视频验证'
# Display excerpts retain the original full text and source location in the data.
R['V1']['messages'][0]['excerpt']=re.sub(r'https://[^；\s]+', '[3Blue1Brown 视频]('+video['url']+')', R['V1']['messages'][0]['text'])
for node_id in ['S1','V5']:
 text=R[node_id]['messages'][1]['text']
 R[node_id]['messages'][1]['excerpt']=text[text.index('三个 Skill 已衔接为：'):text.index('已补充文章')].strip()
R['V2']['messages'][0]['excerpt']=re.sub(r'https://[^\s]+',lambda m:'[3b1b/videos](https://github.com/3b1b/videos)' if 'github.com' in m[0] else '[3Blue1Brown 视频]('+video['url']+')',R['V2']['messages'][0]['text'])
R['V2']['messages'][1]['excerpt']=R['V2']['messages'][1]['text'].split('我核对了')[1].split('主要入口如下')[0]
R['V2']['messages'][1]['excerpt']='我核对了'+R['V2']['messages'][1]['excerpt']
for node_id in ['S1','S2','S3','V5']:
 R[node_id]['outputs']=R[node_id].pop('links')
 R[node_id]['links']=[]
for node_id in ['S1','V5']:
 m=R[node_id]['messages'][1]
 for name,key in [('explanatory-article','articleSkill'),('manim-animation','animationSkill'),('manim-video','videoSkill')]:
  m['excerpt']=m['excerpt'].replace('`'+name+'`','['+name+'](asset:'+key+')')
R['V8']['messages'][2]['excerpt']=R['V8']['messages'][2]['text'].replace('正文','[正文](asset:ioArticle)')
R['V8']['messages'][3]['excerpt']=R['V8']['messages'][3]['text'].replace('正文','[正文](asset:ioArticle)')
R['V10']['links'] += [{'asset':'animationSkill'},{'asset':'videoSkill'}]
R['V10']['outputs']=[{'asset':'videoIo'}]
R['V10']['messages'][1]['excerpt']=R['V10']['messages'][1]['text'].replace('`manim-animation`','[manim-animation](asset:animationSkill)').replace('`manim-video`','[manim-video](asset:videoSkill)')
quad={'asset':'quadArticle','title':'行动选择与投入控制','description':'从具体请求出发，用对齐依据与预期投入判断下一步行动。'}
for node_id,pre,u,a,inputs,outputs in [
 
 ('Q2','01a0ade0',41,42,[{'asset':'articleSkill'}],[quad]),
 ('Q3','01a0ade0',73,74,[quad],[{'asset':'quad'}]),
 ('V6','01a0a41b',1,3,[],[{'asset':'ioSources'}]),
 ('V7','01a0a41b',11,12,[{'asset':'articleSkill'}],[{'asset':'ioArticle'}]),
 ('W1','01a0a8a9',27,28,[],[]),
 ('G1','01a0a8a9',81,82,[{'asset':'terrainArticle'}],[]),
 ('G2','01a0a8a9',95,96,[{'asset':'terrainArticle'}],[{'asset':'terrain'}]),
 ('T6','01a06001',33,34,[{'asset':'terrainArticle'}],[{'asset':'terrain'}]),
 ('P1','01a09ee5',7,8,[],[]),
 ('P3','01a0b362',45,46,[{'asset':'design'}],[])]:
 R[node_id]={'links':inputs,'outputs':outputs,'messages':[message(pre,u),message(pre,a)]}
R['Q2']['messages'][0]['excerpt']='重新列举出哪些任务项，你所列举的任务或者说task 并非可被定义和理解的……需要重新研究下！ 怎么写才合理！且被受众能够理解'
R['V7']['messages'][0]['excerpt']=R['V7']['messages'][0]['text'].replace('[$explanatory-article](/Users/w/code/For-Use-AI/.agents/skills/explanatory-article/SKILL.md)','[explanatory-article](asset:articleSkill)')
R['T6']['messages'][1]['excerpt']=R['T6']['messages'][1]['text'].split('当前根因')[0].strip()
R['W1']['messages'][0]['excerpt']=R['W1']['messages'][0]['text'].split('通过 ')[0].strip()
R['P3']['messages'][1]['excerpt']=R['P3']['messages'][1]['text'].split('整改方向')[0].strip()
(OUT/'节点对话.json').write_text(json.dumps(R,ensure_ascii=False,indent=2))
print(f'{len(R)} verified node conversations')
