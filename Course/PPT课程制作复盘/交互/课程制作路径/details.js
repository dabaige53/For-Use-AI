import {imageStack} from '/image-stack.js';
// Node content is data, never executable Mermaid click directives.
let data, lastTrigger;
const dialog=document.createElement('dialog');dialog.id='detail-dialog';dialog.setAttribute('aria-labelledby','detail-title');
dialog.innerHTML='<div class="detail-head"><h2 id="detail-title"></h2><button class="detail-close" aria-label="关闭弹窗">×</button></div><div class="detail-scroll"><div class="record-view"></div></div>';
document.getElementById('viewport').append(dialog);
let anchor,resizing=false;
function placeCard(){
 if(!dialog.open||!anchor||resizing)return;
 const viewport=document.getElementById('viewport'),v=viewport.getBoundingClientRect(),r=anchor.getBoundingClientRect();
 const w=dialog.offsetWidth,h=dialog.offsetHeight;
 let x=r.right-v.left+14;if(x+w>v.width-12)x=r.left-v.left-w-14;
 dialog.style.left=Math.max(12,Math.min(x,v.width-w-12))+viewport.scrollLeft+'px';
 dialog.style.top=Math.max(12,Math.min(r.top-v.top,v.height-h-12))+viewport.scrollTop+'px';
}
window.addEventListener('canvas-moved',placeCard);window.addEventListener('resize',placeCard);
new ResizeObserver(placeCard).observe(dialog);
const q=s=>dialog.querySelector(s);
const resizeHandle=document.createElement('button');
resizeHandle.className='detail-resize';resizeHandle.type='button';
resizeHandle.setAttribute('aria-label','调整浮卡大小');resizeHandle.title='拖动调整大小，或使用方向键';
resizeHandle.innerHTML='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12 12 4M9 12l3-3"/></svg>';
dialog.append(resizeHandle);
function sizeCard(width,height){
 const viewport=document.getElementById('viewport');
 dialog.classList.add('detail-sized');
 dialog.style.width=Math.min(viewport.clientWidth-24,Math.max(280,width))+'px';
 dialog.style.height=Math.min(viewport.clientHeight-24,Math.max(200,height))+'px';
}
resizeHandle.onpointerdown=e=>{
 if(e.button!==0)return;e.preventDefault();e.stopPropagation();
 const x=e.clientX,y=e.clientY,w=dialog.offsetWidth,h=dialog.offsetHeight;
 resizing=true;resizeHandle.setPointerCapture(e.pointerId);
 resizeHandle.onpointermove=event=>sizeCard(w+event.clientX-x,h+event.clientY-y);
};
resizeHandle.onpointerup=e=>{resizeHandle.releasePointerCapture(e.pointerId);};
resizeHandle.onlostpointercapture=()=>{resizing=false;resizeHandle.onpointermove=null;placeCard();};
resizeHandle.onkeydown=e=>{
 const delta={ArrowLeft:[-20,0],ArrowRight:[20,0],ArrowUp:[0,-20],ArrowDown:[0,20]}[e.key];
 if(!delta)return;e.preventDefault();sizeCard(dialog.offsetWidth+delta[0],dialog.offsetHeight+delta[1]);placeCard();
};
q('.detail-close').onclick=()=>dialog.close();
dialog.addEventListener('click',e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();});
dialog.addEventListener('close',()=>{closeViewer();window.dispatchEvent(new Event('detail-closed'));document.querySelectorAll('[data-detail]').forEach(n=>n.setAttribute('aria-expanded','false'));lastTrigger?.focus({preventScroll:true});});
function el(tag,text){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;}
function safeURL(value,base){if(value.startsWith('asset:'))value=data.assets[value.slice(6)]?.url||'';if(!value)return null;try{const u=new URL(value,base);return ['http:','https:'].includes(u.protocol)?u.href:null;}catch{return null;}}
function inline(parent,text,base){
 const pattern=/(!?)\[([^\]]*)\]\(([^)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*/g;let last=0;
 for(const m of text.matchAll(pattern)){
  parent.append(document.createTextNode(text.slice(last,m.index)));last=m.index+m[0].length;
  if(m[4])parent.append(el('code',m[4]));else if(m[5])parent.append(el('strong',m[5]));else{
   const url=safeURL(m[3],base);if(!url){parent.append(document.createTextNode(m[2]));continue;}
   if(m[1]){const img=el('img');img.src=url;img.alt=m[2];img.loading='lazy';parent.append(img);}
   else{const a=el('a',m[2]);a.href=url;a.target='_blank';a.rel='noopener';parent.append(a);}
  }
 }
 parent.append(document.createTextNode(text.slice(last)));
}
function markdown(text,url){
 const root=el('article');root.className='reading';let code=null,table=null;
 const lines=text.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/,'').split(/\r?\n/);
 for(const line of lines){
  if(line.startsWith('```')){if(code){root.append(code);code=null;}else code=el('pre');continue;}
  if(code){code.append(document.createTextNode(line+'\n'));continue;}
  if(/^\|.*\|\s*$/.test(line)){
   if(/^\|[\s:|\-]+\|\s*$/.test(line))continue;
   if(!table){table=el('table');root.append(table);}const row=el('tr');
   line.trim().slice(1,-1).split('|').forEach(c=>{const td=el('td');inline(td,c.trim(),url);row.append(td);});table.append(row);continue;
  }
  table=null;if(!line.trim())continue;
  if(/^\s*([-*_])\1{2,}\s*$/.test(line)){root.append(el('hr'));continue;}
  const h=line.match(/^(#{1,6})\s+(.*)/);const element=el(h?'h'+h[1].length:line.startsWith('> ')?'blockquote':'p');
  inline(element,h?h[2]:line.replace(/^> /,'').replace(/^[-*] /,'• '),url);root.append(element);
 }
 if(code)root.append(code);return root;
}
function roleIcon(role){
 const icon=el('span');icon.className='record-icon';icon.setAttribute('aria-hidden','true');
 icon.innerHTML=role==='user'?'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="8" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/></svg>':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="7" width="16" height="13" rx="4"/><path d="M12 3v4M1 12v4m22-4v4M8 16h8"/><circle cx="8" cy="12" r="1"/><circle cx="16" cy="12" r="1"/></svg>';return icon;
}
const KIND_ICONS={
 text:'<path d="M7 3h7l4 4v14H7zM13 3v5h5M10 12h5M10 16h5"/>',
 video:'<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M10 9.5v5l4.5-2.5z"/>',
 interactive:'<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M12 12l6 2-2.6 1 1.6 3-1.4.7-1.6-3L12 17z"/>',
 image:'<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="M5 17l5-5 4 4 2-2 3 3"/>',
 link:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/>'};
const KIND_LABEL={text:'文章',video:'视频',interactive:'交互演示',image:'图片',link:'网页'};
function resource(link,view){
 const asset=link.asset?data.assets[link.asset]:null;
 const href=asset?.url||link.url;if(!href)return;
 const kind=KIND_ICONS[asset?.kind]?asset.kind:'link';
 const a=el('a');a.className='record-resource';a.href=href;a.target='_blank';a.rel='noopener';
 const symbol=el('span');symbol.className='resource-symbol';symbol.setAttribute('aria-hidden','true');
 symbol.innerHTML=`<svg viewBox="0 0 24 24">${KIND_ICONS[kind]}</svg>`;
 const text=el('span');text.className='resource-copy';text.append(el('strong',link.title||asset?.title));
 const meta=el('small',link.label||KIND_LABEL[kind]);text.append(meta);
 if(link.description||asset?.description){const summary=el('span',link.description||asset.description);summary.className='resource-description';text.append(summary);}
 const go=el('span');go.className='resource-go';go.setAttribute('aria-hidden','true');go.innerHTML='<svg viewBox="0 0 24 24"><path d="M8 16 16 8M10 8h6v6"/></svg>';
 a.append(symbol,text,go);
 a.onclick=e=>{if(e.metaKey||e.ctrlKey||e.shiftKey||e.button)return;e.preventDefault();openViewer({title:link.title||asset?.title,kind,href});};
 if(link.preview){
  const card=el('section');card.className='resource-feature';card.append(a);
  if(link.preview&&data.assets[link.preview])card.append(imageStack([data.assets[link.preview]]));
  view.append(card);
 }else view.append(a);
}
// 资料在当前页面的阅读层中打开：文章排版显示，视频直接播放，交互演示与网页嵌入；不新开网页。
let viewer;
function viewerShell(){
 if(viewer)return viewer;
 viewer=el('section');viewer.id='resource-viewer';viewer.hidden=true;viewer.setAttribute('role','dialog');viewer.setAttribute('aria-modal','false');viewer.setAttribute('aria-labelledby','viewer-title');
 viewer.innerHTML='<div class="viewer-head"><button type="button" class="viewer-back"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>返回</button><span class="viewer-kind" aria-hidden="true"></span><h2 id="viewer-title"></h2><a class="viewer-open" target="_blank" rel="noopener">新窗口打开</a></div><div class="viewer-body"></div>';
 viewer.querySelector('.viewer-back').onclick=closeViewer;
 document.getElementById('viewport').append(viewer);
 return viewer;
}
function closeViewer(){if(!viewer||viewer.hidden)return;viewer.hidden=true;const body=viewer.querySelector('.viewer-body');body.replaceChildren();body.className='viewer-body';dialog.querySelector('.detail-scroll')?.focus?.();}
function youtubeEmbed(url){const m=url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{6,})/);return m?`https://www.youtube.com/embed/${m[1]}`:null;}
async function openViewer({title,kind,href}){
 const v=viewerShell(),body=v.querySelector('.viewer-body');
 v.querySelector('#viewer-title').textContent=title;
 v.querySelector('.viewer-kind').innerHTML=`<svg viewBox="0 0 24 24">${KIND_ICONS[kind]}</svg>`;
 const url=new URL(href,location.href);v.querySelector('.viewer-open').href=url.href;
 body.replaceChildren();body.className='viewer-body';v.hidden=false;v.querySelector('.viewer-back').focus({preventScroll:true});
 const sameOrigin=url.origin===location.origin;
 if(kind==='video'){body.classList.add('media');const video=el('video');video.src=url.href;video.controls=true;video.playsInline=true;video.preload='metadata';body.append(video);return;}
 if(kind==='image'){body.classList.add('media');const img=el('img');img.src=url.href;img.alt=title;body.append(img);return;}
 const embed=sameOrigin?url.href:youtubeEmbed(url.href);
 if(kind==='interactive'||(kind==='link'&&embed)){body.classList.add('frame');const frame=el('iframe');frame.src=embed||url.href;frame.title=title;frame.allow='fullscreen; autoplay';body.append(frame);return;}
 if(kind==='link'){
  const card=el('div');card.className='viewer-external';
  card.append(el('b','这个网站不允许嵌入当前页面'),el('span',url.host+url.pathname));
  const open=el('a','在新窗口打开');open.href=url.href;open.target='_blank';open.rel='noopener';card.append(open);body.append(card);return;
 }
 body.classList.add('loading');
 try{
  const response=await fetch(url.href);if(!response.ok)throw Error(response.status);
  const text=await response.text();if(v.hidden)return;body.classList.remove('loading');
  if(/\.(md|markdown|txt)$/i.test(url.pathname)){
   const article=markdown(text,url.href);
   // 连续多张图片排成网格，单张图片居中带边框。
   article.querySelectorAll('p').forEach(p=>{const imgs=p.querySelectorAll(':scope>img');if(imgs.length&&!p.textContent.trim())p.classList.add(imgs.length>1?'img-grid':'img-single');});
   // 文中的站内链接也在阅读层里打开。
   article.addEventListener('click',e=>{const link=e.target.closest('a');if(!link||e.metaKey||e.ctrlKey||e.shiftKey)return;const u=new URL(link.href);if(u.origin!==location.origin)return;e.preventDefault();
    const ext=u.pathname.split('.').pop().toLowerCase();const kind=['md','markdown','txt','py','js','json'].includes(ext)?'text':['mp4','webm','mov'].includes(ext)?'video':['png','jpg','jpeg','gif','webp','svg'].includes(ext)?'image':'interactive';
    openViewer({title:link.textContent.trim()||title,kind,href:u.href});});
   body.append(article);
  }else{const pre=el('pre',text);pre.className='viewer-code';body.append(pre);}
 }catch(error){body.classList.remove('loading');body.append(el('p','资料读取失败，可以点右上角在新窗口打开。'));}
}
function resourceGroup(links,side,view){
 const group=el('section');group.className='record-group '+side;
 const head=el('div');head.className='record-group-head';
 head.innerHTML=side==='inputs'?'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M4 19h16"/></svg>':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20V9M7 14l5-5 5 5M4 5h16"/></svg>';
 head.append(el('span',side==='inputs'?'输入':'产出'),el('b',String(links.length)));
 const list=el('div');list.className=side==='inputs'?'record-inputs':'record-links';
 for(const link of links)resource(link,list);
 group.append(head,list);view.append(group);
}
function renderRecord(n,view){
 const record=n.record;if(!record)return;
 if(record.links?.length)resourceGroup(record.links,'inputs',view);
 const sections=record.conversations?.length?record.conversations:[{messages:record.messages||[]}];
 const threads=new Map();
 for(const section of sections){
  const id=section.threadId||'default';
  if(!threads.has(id))threads.set(id,{messages:[]});
  threads.get(id).messages.push(...(section.messages||[]));
 }
 const conversations=[...threads.values()];
 const messages=el('div');messages.className='record-conversation';
 let tabs;
 if(conversations.length>1){
  const switcher=el('div');switcher.className='conversation-switcher';
  tabs=el('div');tabs.className='conversation-tabs';tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','对话线程');
  conversations.forEach((conversation,i)=>{
   const button=el('button',String(i+1));button.type='button';button.setAttribute('role','tab');button.id='conversation-tab-'+i;
   button.setAttribute('aria-label',`对话线程 ${i+1}`);button.setAttribute('aria-controls','conversation-panel');
   button.onclick=()=>select(i);
   button.onkeydown=e=>{let next;if(e.key==='ArrowRight')next=(i+1)%conversations.length;else if(e.key==='ArrowLeft')next=(i-1+conversations.length)%conversations.length;else if(e.key==='Home')next=0;else if(e.key==='End')next=conversations.length-1;else return;e.preventDefault();select(next);tabs.children[next].focus();};
   tabs.append(button);
  });
  messages.id='conversation-panel';messages.setAttribute('role','tabpanel');switcher.append(tabs);view.append(switcher);
 }
 view.append(messages);
 function select(index){
  messages.replaceChildren();
  if(tabs){[...tabs.children].forEach((b,i)=>{b.setAttribute('aria-selected',String(i===index));b.tabIndex=i===index?0:-1;});messages.setAttribute('aria-labelledby','conversation-tab-'+index);}
  for(const message of conversations[index].messages||[]){
  const row=el('section');row.className='record-message '+message.role;
  const who=el('div');who.className='record-role';who.append(roleIcon(message.role),el('span',message.role==='user'?'用户':'AI'));row.append(who);
  const body=markdown(message.text,location.href);body.className='record-text';row.append(body);
  if(message.images?.length)row.append(imageStack(message.images.map(k=>data.assets[k])));
  messages.append(row);
  }
 }
 select(0);
 if(record.outputs?.length)resourceGroup(record.outputs,'outputs',view);
}
function showNode(id,trigger){
 const n=data.nodes[id];if(!n)return;
 if(!dialog.open)lastTrigger=trigger||document.activeElement;
 anchor=document.querySelector('[data-detail="'+id+'"]')||trigger;
 q('#detail-title').textContent=n.title;
 const view=q('.record-view');view.replaceChildren();renderRecord(n,view);
 document.querySelectorAll('[data-detail]').forEach(node=>node.setAttribute('aria-expanded',node.dataset.detail===id?'true':'false'));
 if(!dialog.open)dialog.show();placeCard();q('.detail-scroll').scrollTop=0;q('.detail-close').focus({preventScroll:true});
}
function connect(){
 if(!data)return;
 document.querySelectorAll('#canvas svg .node').forEach(n=>{
  const id=n.getAttribute('data-id')||n.id.match(/^flowchart-(.+)-\d+$/)?.[1];if(!data.nodes[id])return;
  n.dataset.detail=id;n.setAttribute('role','button');n.setAttribute('tabindex','0');n.setAttribute('aria-label',data.nodes[id].title+'，查看材料');n.setAttribute('aria-haspopup','dialog');n.setAttribute('aria-expanded','false');
  n.onclick=()=>showNode(id,n);n.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();showNode(id,n);}};
 });
}
document.addEventListener('mermaid-rendered',connect);
window.addEventListener('open-detail',e=>showNode(e.detail.id,e.detail.trigger));
document.addEventListener('keydown',e=>{if(e.key!=='Escape'||document.getElementById('image-lightbox')?.open)return;if(viewer&&!viewer.hidden){closeViewer();return;}if(dialog.open)dialog.close();});
try{
 const response=await fetch('/details');if(!response.ok)throw Error('无法读取节点材料');data=await response.json();
 if(!document.body.classList.contains('flow-canvas')){
 document.body.classList.add('has-details');document.title=data.title;document.querySelector('header strong').textContent=data.title;
 const read=el('button','阅读大小');read.onclick=()=>{window.dispatchEvent(new CustomEvent('mermaid-reading-size'));};document.getElementById('fit').after(read);
 connect();
 }
}catch(error){console.error(error);}
