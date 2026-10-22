globalThis.buildCh02Final=function(p,d,A,pageNumber,geometryRecords=[],media={}){
 const C={navy:'#0E1E36',body:'#46556B',muted:'#6B778A',blue:'#2F5BD3',orange:'#D98B3A',line:'#D7DFE9'};
 const s=p.slides.add({width:1672,height:941,background:{fill:'#FFFFFF'}}),pre='ch02-final-'+d.key+'-';
 const box=(name,x,y,w,h,fill='none',line='none',lw=0)=>s.shapes.add({name:pre+name,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:line,width:lw}});
 const t=(name,text,x,y,w,h,size=28,color=C.body,bold=false,align='left')=>{const e=box(name,x,y,w,h);e.text=text;e.text.style={typeface:'PingFang SC',fontSize:size,color,bold,alignment:align,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};return e;};
 const line=(name,x1,y1,x2,y2,color=C.line,width=2)=>s.shapes.add({name:pre+name,geometry:'custom',position:{left:Math.min(x1,x2),top:Math.min(y1,y2),width:Math.max(1,Math.abs(x2-x1)),height:Math.max(1,Math.abs(y2-y1))},fill:'none',line:{style:'solid',fill:color,width},customPaths:[{width:Math.max(1,Math.abs(x2-x1)),height:Math.max(1,Math.abs(y2-y1)),commands:[{moveTo:{x:x1<=x2?0:Math.abs(x2-x1),y:y1<=y2?0:Math.abs(y2-y1)}},{lineTo:{x:x1<=x2?Math.abs(x2-x1):0,y:y1<=y2?Math.abs(y2-y1):0}}]}]});
 const arrow=(name,x1,y,x2,color=C.muted)=>{const h=x1<x2?-9:9;line(name,x1,y,x2,y,color,2);line(name+'a',x2+h,y-5,x2,y,color,2);line(name+'b',x2+h,y+5,x2,y,color,2);};
 const image=(name,k,x,y,w)=>{const a=A[k],h=w*a.crop.height/a.crop.width;const source=a.reference?{path:a.reference}:{blob:a.bytes};const e=s.images.add({...source,contentType:'image/png',alt:name,fit:'contain',position:{left:x,top:y,width:w,height:h},crop:{left:a.crop.x/a.source.width,top:a.crop.y/a.source.height,right:(a.source.width-a.crop.x-a.crop.width)/a.source.width,bottom:(a.source.height-a.crop.y-a.crop.height)/a.source.height}});e.lockAspectRatio=true;geometryRecords.push({slide_key:d.key,asset_key:k,name,source_path:a.path,source_size:a.source,crop_region:a.crop,display_frame:{x,y,width:w,height:h},ratio_error_percent:Math.abs(w/h/(a.crop.width/a.crop.height)-1)*100});return e;};
 const footer=(color=C.muted)=>{t('footer','AI × WORK',72,890,260,34,18,C.muted);t('page',String(pageNumber).padStart(2,'0'),1540,890,60,34,18,color,false,'right');};
 const title=()=>{t('title',d.title,72,72,1528,72,52,C.navy,true);box('accent',72,163,40,3,C.orange);};
 const task=()=>{t('task-label','同一封邮件',72,210,180,42,24,C.blue,true);t('task','给张经理发邮件，说明天的会改到下午三点。',262,206,1338,48,28,C.body);};
 if(d.key==='cover'){
  const h=1672*A.cover.source.height/A.cover.source.width;image('原课件章节山景','cover',0,(941-h)/2,1672);
  box('white',0,0,820,941,'#FFFFFF');box('fade',820,0,270,941,{type:'gradient',gradientKind:'linear',angleDeg:0,stops:[{offset:0,color:'#FFFFFF'},{offset:100000,color:'#FFFFFF/0'}]});
  t('number','02',72,164,550,290,240,'#E2EAF6',true);t('title','看清它',80,440,760,110,72,C.navy,true);t('question','AI 是怎么帮我们干活的？',80,586,760,55,28,C.body);t('track','了解它    /    看清它    /    用好它',80,760,760,50,28,C.body);footer('#FFFFFF');
 }else if(d.key==='roundtrip'){
  title();task();
  t('you','你',88,364,220,60,40,C.navy,true,'center');t('you-desc','发出消息\n看到结果',88,468,220,108,28,C.body,false,'center');
  t('app','AI 应用',458,304,590,60,40,C.navy,true);box('paper',458,382,590,268,'#FFFFFF',C.line,1.5);
  t('paper-title','这次发给模型的材料',488,406,530,42,28,C.navy,true);
  t('paper-text','任务：给张经理发改期邮件\n规则：发送前先确认\n可用操作：查通讯录、发邮件',488,478,530,147,28,C.body);
  arrow('user-request',316,427,430);arrow('user-result',430,574,316);
  t('model','厂家的模型服务',1216,353,384,70,40,C.navy,true,'center');
  t('model-output','返回文字\n或操作请求',1216,487,384,108,28,C.body,false,'center');
  arrow('to-model',1075,427,1188);arrow('from-model',1188,574,1075);t('request-label','请求',1075,382,113,36,24,C.muted,false,'center');t('return-label','结果',1075,592,113,36,24,C.muted,false,'center');
  t('api','API',72,735,120,50,32,C.blue,true);t('api-meaning','软件向模型服务递交请求、接收结果的约定',262,735,1338,50,32,C.navy);t('scope','以使用云端模型的应用为例；先看一次往返。',262,801,1338,42,24,C.muted);footer();
 }else if(d.key==='roomA'||d.key==='roomB'){
  title();task();image(d.key==='roomA'?'房间 A：只有纸笔，能够写草稿':'房间 B：模型在内，应用执行程序在外',d.key,72,250,1000);
  t('model-label','模型',184,484,118,42,28,C.navy,true);line('model-leader',270,510,331,510,C.muted,1.5);
  if(d.key==='roomA'){
   t('question','邮件发出去了吗？',1144,336,456,140,40,C.orange,true);t('look','桌上有一份草稿。',1144,562,456,110,28,C.body);
  }else{
   t('rule-label','规则',369,343,106,40,28,C.blue,true,'center');t('rule-content','先确认',362,386,120,37,24,C.body,false,'center');t('tools-label','可用操作',502,344,112,37,24,C.blue,true,'center');t('tools-content','查通讯录\n发邮件',501,379,116,65,24,C.body,false,'center');
   t('operator-label','应用执行程序',833,374,244,42,28,C.blue,true,'center');line('operator-leader',951,420,951,454,C.muted,1.5);
   t('question','和房间 A 比，\n多了什么？',1144,336,456,140,40,C.orange,true);t('look','看房间里增加了什么，\n再找房间外的执行者。',1144,562,456,110,28,C.body);
  }footer();
 }else if(['call1','call2','call3'].includes(d.key)){
  title();task();const n=Number(d.key.slice(-1));
  t('context-label','本轮材料 / 上下文',72,308,330,50,28,C.navy,true);
  t('kept',n===3?'原任务、规则\n查到的邮箱\n发送请求记录':'原任务\n发送前确认规则\n可用操作',72,380,320,144,28,C.muted);line('context-divider',72,534,348,534,C.line,1.5);
  const fresh=n===1?['本轮待查','张经理的邮箱']:n===2?['上轮带回的邮箱','zhang@example.com']:['上轮带回的回执','已提交发送\n编号 M-021（示意）'];
  t('new-label',fresh[0],72,562,320,42,24,C.blue,true);t('new-data',fresh[1],72,610,330,110,28,C.blue,true);
  image('同一模型与同一应用执行程序；保持角色位置','handoff',400,335,1200);
  t('model-label','同一模型 · 第 '+n+' 次',454,299,400,48,28,C.navy,true);t('operator-label','应用执行程序',1270,299,330,48,28,C.navy,true,'center');
  const req=n===1?['查询请求','张经理的邮箱']:n===2?['发送请求','收件人\n主题、正文']:['发送回执','实际执行结果'];
  t('request',req[0],979,466,222,48,32,C.blue,true);t('request-fields',req[1],980,522,220,90,28,C.body);
  if(n===3)arrow('result-return',1196,630,959,C.muted);else arrow('request-handoff',959,630,1196,C.muted);
  t('model-action',n===1?'先提出查邮箱的请求':n===2?'读到邮箱后，提出请求':'向用户说明：已提交发送',470,804,620,42,24,n===3?C.blue:C.muted);
  if(n===1){t('operator-action','查询通讯录',1190,778,410,40,28,C.orange,true);t('operator-result','返回 zhang@example.com',1190,820,410,38,24,C.body);}
  if(n===2)t('operator-action','先确认，再由邮箱发送',1190,804,410,48,28,C.orange,true);
  if(n===3)t('operator-action','把回执带入本轮输入',1190,804,410,48,28,C.orange,true);
  footer();
 }else if(d.key==='video1'||d.key==='video2'){
  title();const first=d.key==='video1';image('原视频静帧，流程模拟，非可播放控件',d.key,72,224,992);
  t('time',first?'00:00–01:04  ·  64 秒':'01:04–02:39  ·  95 秒',72,811,992,40,24,C.muted);
  t('watch','带着一个问题看',1136,270,464,50,32,C.blue,true);t('question',first?'文件路径有了，\n内容就读到了吗？':'工具执行后，\n下一次输入多了什么？',1136,378,464,155,40,C.navy,true);
  t('media-state',media.status||'原片片段预览 · 静帧\n原视频已保存到 Space',1136,647,464,105,24,C.muted);t('simulation','流程模拟',1136,788,464,40,24,C.muted);
  if(media.url){const link=t('video-link','打开原视频',1136,734,464,44,28,C.blue,true);link.text=[[{run:'打开原视频',link:{uri:media.url,isExternal:true},style:{fontSize:'28px',color:C.blue,underline:'sng'}}]];}
  footer();
 }else if(d.key==='checkEvidence'){
  title();t('no1','01',72,260,110,65,40,C.blue,true);t('case1','没有连接邮箱，聊天窗口却说“已发送”。',228,260,1372,60,32,C.body);t('question1','这能证明邮件发出了吗？',228,346,1372,65,40,C.orange,true);
  line('divider',228,457,1600,457,C.line,1.5);
  t('no2','02',72,524,110,65,40,C.blue,true);t('case2','只输入“桌面/报表.xlsx”，\n没有上传，也没有连接文件读取工具。',228,524,1372,120,32,C.body);t('question2','谁去读取文件，模型才能看到内容？',228,688,1372,65,40,C.navy,true);t('actions','先判断，再指出真正执行读取的一方。',228,797,1372,42,24,C.muted);footer();
 }else if(d.key==='checkOrder'){
  title();t('case','已经查到了张经理邮箱，接下来怎样完成这封邮件？',72,223,1528,60,32,C.body);
  const list=[['B','模型提出发送请求'],['C','应用取得确认后，调用邮箱发送'],['A','应用带回原任务、规则和查询结果']];list.forEach((a,i)=>{const y=340+i*133;t('letter'+i,a[0],72,y,115,90,80,C.blue,true);t('step'+i,a[1],240,y+8,1360,70,40,C.navy,true);if(i<2)line('divider'+i,240,y+96,1600,y+96,C.line,1.5);});
  t('followup','如果只带回邮箱地址，丢掉原任务和规则，会怎样？',240,786,1360,60,28,C.orange,true);footer();
 }else if(d.key==='quote'){
  t('title','AI 不是工具，\n而是人。',150,300,1372,255,72,C.navy,true);box('accent',150,637,70,3,C.orange);footer();
 }else if(d.key==='transition'){
  t('next','接下来 · 用好它',72,178,1528,55,32,C.blue,true);t('title','它具备这些条件，\n为什么还是做不好我的任务？',72,342,1528,250,72,C.navy,true);box('accent',72,671,70,3,C.orange);footer();
 }
 s.speakerNotes.text='【第二章｜'+d.title+'】\n'+d.notes+'\n本页为静态页面。需要停顿或逐步讲解的顺序已写在备注；未设置原生对象动画。';
 return {key:d.key,id:s.id,page:pageNumber,title:d.title};
};
