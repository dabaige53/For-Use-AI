// Update an observed slide in place. All teaching text stays editable.
// Call inside a new artifactSession.run callback; confirm commit and reread before the next slide.
globalThis.reviseCourseSlide = function(p,d) {
  const s=p.slides.items.find(s=>s.id===d.id);
  if(!s) throw new Error('Slide missing: '+d.id);
  for(const x of [...s.shapes.items]) x.delete();
  for(const x of [...s.images.items]) x.delete();
  const shape=(n,x,y,w,h,fill='none')=>s.shapes.add({name:'course-revision-'+d.key+'-'+n,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}});
  const text=(n,v,x,y,w,h,size,color,bold=false)=>{const a=shape(n,x,y,w,h);a.text=v;a.text.style={typeface:'PingFang SC',fontSize:size,color,bold,alignment:'left',verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};return a;};
  text('title',d.title,72,72,1528,80,52,'#0E1E36',true);
  shape('accent',72,163,40,3,'#D98B3A');
  for(const [i,e] of d.elements.entries()){
    if(e.kind==='rect') shape('r'+i,e.x,e.y,e.w,e.h,e.fill);
    else text('t'+i,e.text,e.x,e.y,e.w,e.h,e.size,e.color,e.bold);
  }
  text('footer','AI × WORK',72,890,260,34,18,'#6B778A');
  text('page',String(d.page).padStart(2,'0'),1540,890,60,34,18,'#6B778A');
  text('example','课堂示例',1390,170,210,36,24,'#6B778A');
  s.speakerNotes.text='【'+(d.page<32?'第二章':'第三章')+'｜'+d.title+'｜'+d.minutes+'分钟】\n教学目标：'+d.goal+'\n互动：'+d.interaction+'\n'+d.notes+'\n页面上的人物、对话、数据和结果为课堂示例。未执行邮件发送、文件创建或业务操作；工具回执示意不代表实际执行。所有教学文字为原生可编辑对象。';
  return {id:s.id,title:d.title,page:d.page,shapes:s.shapes.items.length};
};
