// Shared by read-only previews and the cloud Artifact Session. No local deck export.
globalThis.buildCh03 = function (p, d, assets, page, geometry = []) {
  if (d.nativeElements) {
    if (typeof globalThis.reviseCourseSlide !== 'function') throw new Error('先载入制作稿/对话改造/页面构建.js');
    const slide=p.slides.add({width:1672,height:941,background:{fill:'#FFFFFF'}});
    return globalThis.reviseCourseSlide(p,{...d,id:slide.id,page,elements:d.nativeElements},assets);
  }
  const C={navy:'#0E1E36',body:'#46556B',muted:'#6B778A',blue:'#2F5BD3',orange:'#D98B3A',line:'#D7DFE9',pale:'#F5F6F8'};
  const s=p.slides.add({width:1672,height:941,background:{fill:'#FFFFFF'}}), prefix='ch03-'+d.key+'-';
  const box=(n,x,y,w,h,fill='none',stroke='none',sw=0)=>s.shapes.add({name:prefix+n,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{style:'solid',fill:stroke,width:sw}});
  const t=(n,text,x,y,w,h,size=28,color=C.body,bold=false,align='left')=>{const e=box(n,x,y,w,h);e.text=text;e.text.style={typeface:'PingFang SC',fontSize:size,color,bold,alignment:align,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};return e;};
  const line=(n,x1,y1,x2,y2,color=C.line,sw=1.5)=>s.shapes.add({name:prefix+n,geometry:'custom',position:{left:Math.min(x1,x2),top:Math.min(y1,y2),width:Math.max(1,Math.abs(x2-x1)),height:Math.max(1,Math.abs(y2-y1))},fill:'none',line:{style:'solid',fill:color,width:sw},customPaths:[{width:Math.max(1,Math.abs(x2-x1)),height:Math.max(1,Math.abs(y2-y1)),commands:[{moveTo:{x:x1<=x2?0:Math.abs(x2-x1),y:y1<=y2?0:Math.abs(y2-y1)}},{lineTo:{x:x1<=x2?Math.abs(x2-x1):0,y:y1<=y2?Math.abs(y2-y1):0}}]}]});
  const arrow=(n,x1,y,x2)=>{line(n,x1,y,x2,y,C.muted,2);const k=x2>x1?-10:10;line(n+'a',x2+k,y-5,x2,y,C.muted,2);line(n+'b',x2+k,y+5,x2,y,C.muted,2);};
  const image=(n,key,x,y,w)=>{const a=assets[key],h=w*a.height/a.width;const source=a.reference?{path:a.reference}:{blob:a.bytes};const im=s.images.add({...source,contentType:'image/png',name:prefix+n,alt:n,fit:'contain',position:{left:x,top:y,width:w,height:h}});im.lockAspectRatio=true;geometry.push({key:d.key,image:key,width:w,height:h,sourceWidth:a.width,sourceHeight:a.height,crop:'none'});return im;};
  const footer=(color=C.muted)=>{t('footer','AI × WORK',72,890,260,34,18,C.muted);t('page',String(page).padStart(2,'0'),1540,890,60,34,18,color,false,'right');};
  const title=()=>{t('title',d.title,72,72,1528,72,52,C.navy,true);box('accent',72,163,40,3,C.orange);};
  const label=(n,v,x,y,w=500)=>t(n,v,x,y,w,45,24,C.blue,true);
  const conclusion=(v,y=776)=>t('conclusion',v,72,y,1528,66,32,C.navy,true);
  const k=d.key;
  if(k==='cover'){
    image('章节山景','cover',0,0,1672);box('white',0,0,820,941,'#FFFFFF');box('fade',820,0,270,941,{type:'gradient',gradientKind:'linear',angleDeg:0,stops:[{offset:0,color:'#FFFFFF'},{offset:100000,color:'#FFFFFF/0'}]});
    t('number','03',72,164,550,290,240,'#E2EAF6',true);t('title','用好它',80,440,760,110,72,C.navy,true);t('question','怎样交代任务并逐步改进？',80,586,760,55,28);t('track','了解它    /    看清它    /    用好它',80,760,760,50,28);footer('#FFFFFF');
  }else if(k==='quote'){
    t('quote1','AI 不会读心：',150,300,1372,100,72,C.navy,true);t('quote2','先说清楚，再拉回来。',150,425,1372,110,72,C.blue,true);box('accent',150,637,70,3,C.orange);footer();
  }else{
    title();
    if(k==='gap'){
      label('spoken','已经说出口',72,228);t('request','“帮我写个通知。”',72,300,760,140,60,C.navy,true);
      image('同事对照材料','review',80,468,580);
      line('divider',864,240,864,822);label('missing','还没有交代',960,228);
      ['发给谁？','通知什么事？','发在哪里？','看完要做什么？'].forEach((v,i)=>{t('n'+i,String(i+1).padStart(2,'0'),960,308+i*125,90,65,40,C.blue,true);t('q'+i,v,1090,312+i*125,510,64,40,C.navy,true);});
    }else if(k==='context'){
      label('paper','这次请求里的材料',72,225);box('paper',72,300,800,410,'#FFFFFF',C.line,1.5);
      [['任务与要求','项目会改期通知'],['文件与示例','这次会议安排＋通知样例'],['已确认反馈','补上时间地点，保留简短语气']].forEach((r,i)=>{let y=330+i*124;t('h'+i,r[0],104,y,220,50,28,C.navy,true);t('b'+i,r[1],360,y,460,80,28);if(i<2)line('l'+i,104,y+90,840,y+90);});
      arrow('to-model',912,498,1050);t('model','模型',1130,430,400,70,52,C.navy,true);t('model-note','按这次收到的内容处理',1130,535,470,100,28);conclusion('关键条件，确认已经带入这次请求。');
    }else if(k==='feedback'){
      ['第一版','指出差别','再看一版'].forEach((v,i)=>t('scene'+i,v,72+i*532,218,464,60,40,C.navy,true));
      const a=assets.feedback;
      for(let i=0;i<3;i++){const w=400,h=w*(a.height/(a.width/3));const source=a.reference?{path:a.reference}:{blob:a.bytes};const im=s.images.add({...source,contentType:'image/png',alt:['交草稿','指出缺失','对照修订'][i],fit:'contain',position:{left:104+i*532,top:266,width:w,height:h},crop:{left:i/3,top:0,right:(2-i)/3,bottom:0}});im.lockAspectRatio=true;geometry.push({key:k,image:'feedback',panel:i,width:w,height:h,sourceWidth:a.width/3,sourceHeight:a.height,crop:'horizontal thirds'});}
      const captions=['“本周五开会，\n请大家准时参加。”','“补上15:00与301室，\n请大家回复能否参加。”','“周五15:00，301室。\n请回复能否参加，谢谢。”'];
      captions.forEach((v,i)=>t('caption'+i,v,72+i*532,748,464,94,28,i===1?C.blue:C.body));
    }else if(k==='feedback-transfer'){
      label('opinion','评价',72,224);label('action','可执行的修改动作',540,224);
      const a=[['太啰嗦了。','把背景缩成一句，保留时间、地点和回复要求。'],['不像我们部门的。','参照样例的称呼和结尾，事实仍用本次材料。']];
      a.forEach((r,i)=>{const y=330+i*190;t('left'+i,'“'+r[0]+'”',72,y,400,105,40,C.navy,true);arrow('a'+i,448,y+31,510);t('right'+i,r[1],540,y,1060,112,32);line('sep'+i,72,y+140,1600,y+140);});
      conclusion('你会怎样改：“还不够清楚”？',780);
    }else if(k==='map'||k==='method-summary'){
      const rows=k==='map'?[['交代清楚','① 说清使用条件    ② 给出具体标准\n③ 用参照定语气    ④ 给一份样子'],['先弄明白','⑤ 先看不同方向    ⑥ 先确认含义\n⑦ 先核对前提'],['偏离目标','⑧ 重申当前交付物']]:[['交代清楚','我能用……；标准是……\n语气像……；参照这份……'],['先弄明白','先给不同方向；先确认含义；先核对前提。'],['偏离目标','本轮先交……，其他事项暂缓。']];
      rows.forEach((r,i)=>{const y=250+i*194;t('group'+i,r[0],72,y,360,70,40,C.navy,true);t('methods'+i,r[1],492,y,1108,120,32);if(i<2)line('sep'+i,492,y+148,1600,y+148);});
    }else if(k==='case1'){
      t('task','统计每月考勤',72,220,1528,60,40,C.navy,true);line('fork',836,330,836,588);
      label('a','方案 A',72,340);t('a-text','安装环境\n运行脚本',72,416,650,150,40,C.body,true);
      label('b','方案 B',940,340);t('b-text','在现有 Excel 表里\n填写公式',940,416,660,150,40,C.body,true);
      t('question','哪一个你现在能用？',72,618,1528,65,40,C.orange,true);
      t('prompt','我只会用 Excel，不会编程。\n请按我提供的表头给出公式，并说明放在哪一格。',72,726,1528,112,32);
    }else if(k==='case2-question'){
      label('request','只有一个形容词',72,250);t('task','“写一份专业的周报。”',72,348,1528,110,60,C.navy,true);t('question','你会用哪两条标准验收？',72,620,1528,90,40,C.orange,true);
    }else if(k==='case2-answer'){
      label('source','原始材料',72,217);t('facts','走访12家客户；收到5项需求，\n其中3项已确认，2项待补充。\n下周周三前回访。',72,278,640,180,28);
      label('standard','验收标准',72,520);t('rules','150字以内，分三段；\n保留数量和时间；\n不补造业绩。',72,580,640,180,32,C.navy,true);
      box('document',800,222,800,580,'#FFFFFF',C.line,1.5);[['本周完成','走访12家客户，收到5项需求，\n已确认3项。'],['遇到问题','2项需求仍待客户补充信息。'],['下周计划','周三前回访，确认剩余2项需求。']].forEach((r,i)=>{let y=252+i*177;t('h'+i,r[0],836,y,728,48,32,C.blue,true);t('b'+i,r[1],836,y+60,728,105,28);});
    }else if(k==='case3'){
      label('fact','共同事实：周一9:00，到前台领取工牌。',72,218,1528);
      const a=[['办事指南','周一9:00，请到前台领取工牌。'],['带教同事','欢迎加入！周一9:00到前台领工牌，我们到时见。'],['活动主持人','新同事，欢迎到场！周一9:00，前台领取你的工牌。']];
      a.forEach((r,i)=>{let y=310+i*156;t('role'+i,r[0],72,y,300,65,40,C.navy,true);t('phrase'+i,r[1],450,y,1150,100,32);if(i<2)line('sep'+i,450,y+110,1600,y+110);});conclusion('选一种语气，再说出需要保留的事实。',800);
    }else if(k==='case4-question'){
      t('task','整理成我们部门的会议纪要',72,218,1528,60,40,C.navy,true);
      [['A','简洁、有条理，重点突出。'],['B','参照样例结构，事实使用本次记录。']].forEach((r,i)=>{let y=350+i*178;t('letter'+i,r[0],72,y,120,100,80,C.blue,true);t('prompt'+i,r[1],236,y+12,740,125,32);});
      box('sample',1120,340,480,310,'#FFFFFF',C.line,1.5);label('sample-label','样例结构',1152,364,410);t('fields','结论\n行动项 · 负责人 · 截止时间',1152,438,410,168,28,C.navy,true);
      conclusion('哪一份更方便检查是否符合格式？');
    }else if(k==='case4-answer'){
      label('source','本次记录',72,222);t('facts','李明周三18:00前补齐预算。\n周晴周五12:00前确认场地。',72,293,1528,125,40,C.navy,true);
      const cols=[72,660,1050];['行动项','负责人','截止时间'].forEach((v,i)=>label('h'+i,v,cols[i],478,500));line('head',72,538,1600,538);
      [['补齐预算','李明','周三18:00'],['确认场地','周晴','周五12:00']].forEach((r,j)=>r.forEach((v,i)=>t('cell'+j+i,v,cols[i],574+j*90,500,64,32)));
      conclusion('学格式，旧样例的名字和日期不要带过来。',790);
    }else if(k==='opening-summary'){
      ['我要交付什么？','我能用什么工具？','好的结果怎样检查？','有什么材料或样例？'].forEach((v,i)=>{const y=240+i*145;t('n'+i,String(i+1).padStart(2,'0'),72,y,130,95,80,C.blue,true);t('q'+i,v,300,y+16,1300,80,40,C.navy,true);});
    }else if(k==='case5-options'){
      t('constraints','80人 · 预算3万元 · 2小时 · 15人远程',72,220,1528,60,32,C.body);t('source','年会方向',72,464,340,90,52,C.navy,true);line('stem',490,356,490,788);arrow('input',365,508,490);
      ['年度颁奖＋远程连线','团队挑战＋线上同步答题','年度故事＋跨地分享','成果展览＋实时投票','时间胶囊＋明年承诺'].forEach((v,i)=>{let y=326+i*108;line('branch'+i,490,y+30,566,y+30);t('letter'+i,'ABCDE'[i],608,y,70,60,40,C.blue,true);t('option'+i,v,728,y,872,65,40,C.navy,true);});
    }else if(k==='case5-select'){
      label('selection','课堂演练：年度颁奖＋远程连线',72,222,1528);
      t('time-title','先核对2小时',72,310,650,65,40,C.navy,true);
      [['开场','10'],['成果回顾','20'],['颁奖与连线','50'],['交流','30'],['收尾','10']].forEach((r,i)=>{let y=400+i*70;t('step'+i,r[0],72,y,460,55,28);t('min'+i,r[1]+' 分钟',554,y,210,55,28,C.blue,true,'right');});
      line('divider',836,300,836,790);t('check-title','再检查可执行性',940,310,660,65,40,C.navy,true);t('checks','费用：还需报价确认\n远程：安排连线与互动\n设备：提前测试音视频\n人员：明确每项负责人',940,420,660,250,32);t('limit','120分钟排得下，\n不等于预算已经核实。',940,724,660,100,32,C.orange,true);
    }else if(k==='case6-explore'){
      t('question','季度汇报的“高级”，你指哪一种？',72,218,1528,65,40,C.navy,true);
      [72,604,1136].forEach((x,i)=>{label('sample'+i,'ABC'[i],x,328,464);line('sample-top'+i,x,390,x+464,390);});
      t('sample-a-title','一个结论',72,440,464,110,60,C.navy,true);t('sample-a-body','大标题，少量说明。',72,596,464,90,28);
      [110,160,210].forEach((h,i)=>box('bar'+i,620+i*128,680-h,80,h,i===2?C.blue:'#E2EAF6'));t('sample-b-body','图表与证据标注。',604,730,464,65,28);
      t('sample-c-title','一个场景\n解释一次变化',1136,450,464,160,40,C.navy,true);t('sample-c-body','故事与大幅配图。',1136,730,464,65,28);
    }else if(k==='case6-brief'){
      label('explore','探索时的说法',72,230);['高级一点','别太花','简洁但别空'].forEach((v,i)=>{let y=334+i*120;t('phrase'+i,v,72,y,480,70,40,C.muted);line('strike'+i,72,y+32,460,y+32,C.line,2);});
      arrow('to-brief',570,505,710);box('brief',780,230,820,565,'#FFFFFF',C.line,1.5);label('brief-title','确认后的制作要求',820,270,740);
      t('brief-text','10页季度汇报；每页一个结论。\n关键数字配图表。\n深蓝文字，少量橙色强调。\n保留业务目标与原始数据。',820,355,740,260,32,C.navy,true);
      t('next','复述要求，再做一页样稿。',820,704,740,60,28,C.blue,true);
    }else if(k==='case7-question'){
      label('action','30秒，找出冲突。',72,218,1528);t('q2','二季度',72,335,650,60,40,C.navy,true);t('q3','三季度',940,335,660,60,40,C.navy,true);t('v2','1,200 万元',72,435,650,110,70,C.navy,true);t('v3','1,440 万元',940,435,660,110,70,C.navy,true);line('divider',836,330,836,552);
      t('request','请求：销售额下降20%，请分析原因。',72,646,1528,70,32);t('response','待检查的回答：下降可能与竞争加剧有关……',72,758,1528,70,32);
    }else if(k==='case7-answer'){
      t('calculation','(1,440 − 1,200) ÷ 1,200 = 20%',72,270,1528,110,60,C.navy,true);t('answer','是增长20%，不是下降。',72,425,1528,90,52,C.blue,true);
      line('divider',72,580,1600,580);t('prompt','先核对数据、单位和比较口径；\n发现冲突，先指出，再分析。',72,640,1528,130,32);t('limit','仅凭两个总额，还不能确定增长原因。',72,800,1528,50,28,C.orange,true);
    }else if(k==='case8-question'){
      label('goal','目标：12个城市的月度销售汇总表',72,220,1528);t('task','汇总数据',72,370,360,75,40,C.navy,true);arrow('main1',360,405,700);t('deliverable','交总表',754,370,410,75,40,C.navy,true);arrow('main2',1050,405,1370);t('missing','还没有',1390,377,210,60,28,C.orange,true);
      line('branch1',500,405,500,580);arrow('branch2',500,580,720);t('drift','发现异常 → 解释原因 → 提议调研',754,548,846,100,32);t('wrong','最后交了：异常分析报告',754,672,846,65,32,C.body,true);conclusion('用1分钟，写一句话把任务拉回来。',800);
    }else if(k==='case8-answer'){
      t('one-task','现在先交12个城市的汇总表。',72,245,1528,110,52,C.navy,true);t('boundary','保留原值，异常项另列清单，暂不分析原因。',72,400,1528,95,32);
      label('accept','交付时逐项核对',72,560,1528);[['城市','是否齐全'],['列名','是否一致'],['行数与合计','是否对得上']].forEach((r,i)=>{let x=72+i*532;t('h'+i,r[0],x,638,464,60,40,C.blue,true);t('b'+i,r[1],x,730,464,65,32);});
    }else if(k==='exercise'){
      t('task','选课前记录的一件工作。',72,222,1528,65,40,C.navy,true);const rows=[['交付物','我要完成……'],['材料与标准','我提供……；完成时应当……'],['具体反馈','第一版的……需要改成……']];
      rows.forEach((r,i)=>{let y=350+i*143;t('field'+i,r[0],72,y,350,60,32,C.blue,true);t('hint'+i,r[1],490,y,1110,60,32,C.muted);line('blank'+i,490,y+78,1600,y+78);});conclusion('同桌互看：还缺哪条关键条件？',804);
    }else if(k==='practice'){
      label('task','任务：把材料整理成一份可检查的周报',72,220,1528);
      box('material',72,312,800,360,'#FFFFFF',C.line,1.5);label('material-title','课堂练习材料',104,344,736);t('material-text','走访12家客户，收到5项需求。\n3项已确认，2项待补充。\n下周周三前回访。',104,424,736,175,32);
      t('standard','150字以内；\n完成 / 问题 / 计划三段；\n不添加材料里没有的数据。',968,344,632,190,32,C.navy,true);t('feedback','核对后，给一次具体反馈。',968,610,632,100,32,C.blue,true);conclusion('也可以选自己的任务，按同样步骤练习。',794);
    }else if(k==='closing'){
      [['了解它','说得像，还要核对。'],['看清它','说完成，还要看执行结果。'],['用好它','交代清楚，再按标准反馈。']].forEach((r,i)=>{let y=252+i*160;t('chapter'+i,r[0],72,y,360,65,40,C.blue,true);t('meaning'+i,r[1],492,y,1108,65,40,C.navy,true);});conclusion('选一件工作，试一次，留下有效的要求。',800);
    }else if(k==='complex'){
      const items=['确认目标','列出步骤','先做样稿','按标准检查','继续下一步'];items.forEach((v,i)=>{let x=72+i*316;t('n'+i,String(i+1).padStart(2,'0'),x,300,264,120,80,C.blue,true);t('step'+i,v,x,462,264,120,40,C.navy,true);if(i<4)arrow('a'+i,x+220,370,x+282);});
      t('result','每一步，都要有能看见的结果。',72,660,1528,80,40,C.navy,true);t('keep','要求确认后，留下一份可复用说明。',72,780,1528,65,32);
    }else throw new Error('Unknown chapter 3 key: '+k);
    footer();
  }
  s.speakerNotes.text=d.notes;
  return {key:k,id:s.id,page,title:d.title};
};
