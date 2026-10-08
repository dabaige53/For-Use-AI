import {imageStack} from '/image-stack.js';
// Node content is data, never executable Mermaid click directives.
let data, lastTrigger;
const dialog=document.createElement('dialog');dialog.id='detail-dialog';dialog.setAttribute('aria-labelledby','detail-title');
dialog.innerHTML='<div class="detail-head"><h2 id="detail-title"></h2><button class="detail-close" aria-label="关闭弹窗">×</button></div><div class="detail-scroll"><div class="record-view"></div></div>';
document.getElementById('viewport').append(dialog);
let anchor;
function placeCard(){
 if(!dialog.open||!anchor)return;
 const viewport=document.getElementById('viewport'),v=viewport.getBoundingClientRect(),r=anchor.getBoundingClientRect();
 const w=dialog.offsetWidth,h=dialog.offsetHeight;
 let x=r.right-v.left+14;if(x+w>v.width-12)x=r.left-v.left-w-14;
 dialog.style.left=Math.max(12,Math.min(x,v.width-w-12))+viewport.scrollLeft+'px';
 dialog.style.top=Math.max(12,Math.min(r.top-v.top,v.height-h-12))+viewport.scrollTop+'px';
}
window.addEventListener('canvas-moved',placeCard);window.addEventListener('resize',placeCard);
new ResizeObserver(placeCard).observe(dialog);
const q=s=>dialog.querySelector(s);
q('.detail-close').onclick=()=>dialog.close();
dialog.addEventListener('click',e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();});
dialog.addEventListener('close',()=>{window.dispatchEvent(new Event('detail-closed'));document.querySelectorAll('[data-detail]').forEach(n=>n.setAttribute('aria-expanded','false'));lastTrigger?.focus({preventScroll:true});});
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
  const h=line.match(/^(#{1,6})\s+(.*)/);const element=el(h?'h'+h[1].length:line.startsWith('> ')?'blockquote':'p');
  inline(element,h?h[2]:line.replace(/^> /,'').replace(/^[-*] /,'• '),url);root.append(element);
 }
 if(code)root.append(code);return root;
}
function roleIcon(role){
 const icon=el('span');icon.className='record-icon';icon.setAttribute('aria-hidden','true');
 icon.innerHTML=role==='user'?'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="8" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/></svg>':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="7" width="16" height="13" rx="4"/><path d="M12 3v4M1 12v4m22-4v4M8 16h8"/><circle cx="8" cy="12" r="1"/><circle cx="16" cy="12" r="1"/></svg>';return icon;
}
function resource(link,view){
 const asset=link.asset?data.assets[link.asset]:null;
 const href=asset?.url||link.url;if(!href)return;
 const a=el('a');a.className='record-resource';a.href=href;a.target='_blank';a.rel='noopener';
 const symbol=el('span',asset?.kind==='video'?'▷':asset?.kind==='interactive'?'↗':'↗');symbol.className='resource-symbol';symbol.setAttribute('aria-hidden','true');
 const text=el('span');text.className='resource-copy';text.append(el('strong',link.title||asset?.title));
 if(link.label)text.append(el('small',link.label));
 if(link.description||asset?.description){const summary=el('span',link.description||asset.description);summary.className='resource-description';text.append(summary);}
 if(!link.label&&!link.description&&!asset?.description)a.classList.add('resource-compact');
 a.append(symbol,text);
 if(link.preview){
  const card=el('section');card.className='resource-feature';card.append(a);
  if(link.preview&&data.assets[link.preview])card.append(imageStack([data.assets[link.preview]]));
  view.append(card);
 }else view.append(a);
}
function renderRecord(n,view){
 const record=n.record;if(!record)return;
 if(record.links?.length){const inputs=el('div');inputs.className='record-inputs';for(const link of record.links)resource(link,inputs);view.append(inputs);}
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
 if(record.outputs?.length){const outputs=el('div');outputs.className='record-links';for(const link of record.outputs)resource(link,outputs);view.append(outputs);}
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
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&dialog.open&&!document.getElementById('image-lightbox')?.open)dialog.close();});
try{
 const response=await fetch('/details');if(!response.ok)throw Error('无法读取节点材料');data=await response.json();
 if(!document.body.classList.contains('flow-canvas')){
 document.body.classList.add('has-details');document.title=data.title;document.querySelector('header strong').textContent=data.title;
 const read=el('button','阅读大小');read.onclick=()=>{window.dispatchEvent(new CustomEvent('mermaid-reading-size'));};document.getElementById('fit').after(read);
 connect();
 }
}catch(error){console.error(error);}
