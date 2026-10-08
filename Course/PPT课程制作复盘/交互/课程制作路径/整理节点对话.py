"""Build explicit popover content from the reviewed node specification."""
from pathlib import Path
import json,re
OUT=Path(__file__).resolve().parent
spec=(OUT/'课程制作路径-内容与网页制作规格.md').read_text()
manifest=json.loads((OUT/'节点材料.json').read_text())
# Each entry is adopted assets, produced assets, user images, assistant images.
slots={
'START':('','','',''),
'T1':('terrainOriginal','','',''),
'T2':('terrainOriginal','','',''),
'T3':('terrainOriginal','','',''),
'T4':('','terrain','',''),
'T5':('terrainOriginal','terrain','','terrainGif'),
'T6':('terrainOriginal terrain','terrain','',''),
'T7':('terrainArticle','terrain','','dialogue'),
'V1':('','','',''),
'V2':('','','',''),
'V3':('','videoLlm','',''),
'V4':('videoLlm','','',''),
'V5':('','articleSkill animationSkill videoSkill','',''),
'S1':('','articleSkill','',''),
'S2':('','animationSkill','',''),
'S3':('','videoSkill','',''),
'V6':('','ioSources','',''),
'V7':('ioSources articleSkill','ioArticle','',''),
'V8':('ioArticle videoSkill','','',''),
'V9':('ioArticle','','','story1 story2 story3'),
'V10':('animationSkill videoSkill','animationCode videoIo','story1 story2 story3',''),
'V11':('','videoIo','',''),
'W1':('terrainOriginal quadOriginal ioSources','','',''),
'W2':('articleSkill','terrainArticle ioArticle quadArticle','',''),
'Q1':('quadOriginal','','',''),
'Q2':('quadOriginal articleSkill','quadArticle','',''),
'Q3':('quadArticle','quad','','quadImage'),
'G1':('terrainOriginal articleSkill','terrainArticle','',''),
'G2':('terrainArticle','terrain','','terrainGif dialogue'),
'W3':('','','',''),
'W4':('articleSkill terrainArticle ioArticle quadArticle','website','',''),
'W5':('terrainArticle ioArticle quadArticle terrain quad','website','',''),
'W6':('website','','',''),
'W7':('','website','',''),
'P1':('','','',''),
'P2':('website','','',''),
'P3':('','','',''),
'P4':('','','selected',''),
'P5':('','ppt','selected','implemented'),
'P6':('videoIo videoLlm terrain','ppt','',''),
'P7':('videoIo videoLlm terrain','ppt','',''),
'P8':('quadArticle quad','ppt','',''),
'P9':('quad','ppt','',''),
'P10':('ppt','','',''),
'P11':('ppt','','',''),
'P12':('ppt','','',''),
'P13':('','ppt videoIo videoLlm terrain quad','','')}
video={'title':'大语言模型简明解释','label':'YouTube · 3Blue1Brown','description':'参考它怎样用图形讲清语言模型的预测过程。','url':'https://www.youtube.com/watch?v=LPZh9BOjkQs'}
code={'title':'3b1b / videos · chm.py','label':'GitHub · 场景源码','description':'定位参考视频中的动画场景与实现代码。','url':'https://github.com/3b1b/videos/blob/master/_2024/transformers/chm.py'}
engine={'title':'3b1b / manim','label':'GitHub · 动画引擎','url':'https://github.com/3b1b/manim'}
article={'title':'视频官方图文版','label':'3Blue1Brown','url':'https://www.3blue1brown.com/lessons/mini-llm/'}
site={'title':'ce101.ifuryst.com','label':'网站结构参考','description':'借鉴目录与正文的阅读组织方式。','url':'https://ce101.ifuryst.com'}
R={}
for m in re.finditer(r'^### ([A-Z]+\d*)｜([^\n]+)\n(.*?)(?=^### |^## 6\.|\Z)',spec,re.M|re.S):
 key,title,body=m.groups()
 fields=dict(re.findall(r'^- ([^：\n]+)：(.*)$',body,re.M))
 ins,outs,user_images,ai_images=slots[key]
 R[key]={'title':title,'links':[{'asset':a} for a in ins.split()],
         'messages':[{'role':'user','text':fields['用户'],'images':user_images.split()},
                     {'role':'assistant','text':fields['AI'],'images':ai_images.split()}],
         'outputs':[{'asset':a} for a in outs.split()],
         'status':'planned' if key in ['P12','P13'] else 'editorial-rewrite',
         'evidence':fields['记录依据'],'verification':fields['核验状态']}
 for msg in R[key]['messages']:
  msg['imageOrigin']='current-artifact' if msg['images'] else None
# Provenance-specific overrides, without pretending every image was in the original message.
R['P4']['messages'][0]['imageOrigin']='historical-user-selection'
R['P5']['messages'][0]['imageOrigin']='selected-reference'
R['P5']['messages'][1]['imageOrigin']='historical-implementation'
R['Q1']['links']=[{'asset':'quadOriginal','label':'早期框架原文','description':'关于认知状态、对齐依据与下一段投入的原始思考。'}]
R['T1']['links']=[{'asset':'terrainOriginal','label':'Henry_He · 原始文章','description':'地形、小球与语义变化的内容来源。'}]
R['V1']['links']=[video]
R['V2']['links']=[video,article];R['V2']['outputs']=[code,engine]
R['V3']['links']=[code,engine]
R['W3']['links']=[site];R['W4']['links'].insert(0,site)
# Short links refer to the context named in each sentence.
replacements={
 'V1':[(0,'这个视频','[这个视频]('+video['url']+')')],
 'V2':[(0,'这个视频','[这个视频]('+video['url']+')')],
 'V7':[(0,'输入输出机制','[输入输出机制](asset:ioSources)')],
 'V8':[(0,'文章','[文章](asset:ioArticle)')],
 'V10':[(1,'逐镜实现','按 [manim-animation](asset:animationSkill) 与 [manim-video](asset:videoSkill) 逐镜实现')],
 'Q1':[(0,'以前关于四象限的思考','[以前关于四象限的思考](asset:quadOriginal)')],
 'Q2':[(0,'原有框架','[原有框架](asset:quadOriginal)')],
 'G1':[(0,'原文案例','[原文案例](asset:terrainOriginal)')],
 'P2':[(0,'这些文章','[这些文章](asset:website)')],
 'W3':[(0,'这个网站','[这个网站]('+site['url']+')')]
}
for k,items in replacements.items():
 for i,old,new in items:R[k]['messages'][i]['text']=R[k]['messages'][i]['text'].replace(old,new,1)
# These steps describe work still to be supplied, not a completed historical artifact.
R['P12']['messages'][1]['text']='下一步按页面整理讲述要点、衔接和演示操作；讲稿尚待制作。'
R['P13']['messages'][1]['text']='课件、视频和交互已有入口；讲稿与演示编排补齐后，再完成整套交付检查。'
# Display the current implementation as such when the historical prototype is unavailable.
for k in ['T4','T5','T6','T7']:
 for link in R[k]['outputs']:
  if link['asset']=='terrain':link['title']='现有地形演示'
# Preserve reviewed multi-turn exchanges and stages; never compress them back to a single pair.
enriched=json.loads((OUT/'节点多轮对话.json').read_text())
for key,sections in enriched.items():
 R[key]['conversations']=sections
 R[key]['messages']=sections[0]['messages']
assert set(R)==set(manifest['nodes'])==set(slots)
for k,rec in R.items():
 assert rec['messages'] and all(m['role'] in ['user','assistant'] for m in rec['messages'])
 for link in rec['links']+rec['outputs']:
  if 'asset' in link:assert link['asset'] in manifest['assets'],(k,link)
 for msg in [m for section in rec.get('conversations',[{'messages':rec['messages']}]) for m in section['messages']]:
  for asset in msg['images']:assert manifest['assets'][asset]['kind']=='image'
  for asset in re.findall(r'\(asset:([^)]+)\)',msg['text']):assert asset in manifest['assets']
(OUT/'节点对话.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print(f'{len(R)} explicit node records with rewritten dialogue')
