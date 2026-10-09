let viewer,returnTo;
function lightbox(asset,button){
 if(!viewer){viewer=document.createElement('dialog');viewer.id='image-lightbox';viewer.setAttribute('aria-label','查看图片');const close=document.createElement('button');close.type='button';close.className='image-close';close.setAttribute('aria-label','关闭图片');close.textContent='×';const img=document.createElement('img');viewer.append(close,img);document.body.append(viewer);close.onclick=()=>viewer.close();viewer.addEventListener('click',e=>{if(e.target===viewer){const r=viewer.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)viewer.close();}});viewer.addEventListener('close',()=>{returnTo?.setAttribute('aria-expanded','false');returnTo?.focus({preventScroll:true});});}
 returnTo=button;button.setAttribute('aria-expanded','true');const img=viewer.querySelector('img');img.src=asset.url;img.alt=asset.title;viewer.showModal();
}
export function imageStack(assets){
 const wrap=document.createElement('div');wrap.className='image-stack-wrap';
 const button=document.createElement('button');button.type='button';button.className='image-stack';button.setAttribute('aria-haspopup','dialog');button.setAttribute('aria-expanded','false');
 let index=0,last=0,total=0,x=0,y=0,dragged=false;
 const front=document.createElement('img'),back=document.createElement('img');back.alt='';back.setAttribute('aria-hidden','true');front.draggable=back.draggable=false;back.className='stack-back';front.className='stack-front';
 const count=document.createElement('span');count.className='stack-count';count.setAttribute('aria-live','polite');button.append(back,front,count);wrap.append(button);
 // 多张图：主图 + 左右切换 + 缩略图条，不再叠放。
 let thumbs=[];
 if(assets.length>1){
  wrap.classList.add('multi');
  for(const [dir,label,path] of [[-1,'上一张','M15 6l-6 6 6 6'],[1,'下一张','M9 6l6 6-6 6']]){
   const nav=document.createElement('button');nav.type='button';nav.className='stack-nav '+(dir<0?'prev':'next');nav.setAttribute('aria-label',label);
   nav.innerHTML=`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${path}"/></svg>`;nav.onclick=e=>{e.stopPropagation();turn(dir);};wrap.append(nav);
  }
  const strip=document.createElement('div');strip.className='stack-thumbs';
  thumbs=assets.map((asset,i)=>{const t=document.createElement('button');t.type='button';t.setAttribute('aria-label',`第 ${i+1} 张：${asset.title}`);const img=document.createElement('img');img.src=asset.url;img.alt='';img.loading='lazy';t.append(img);t.onclick=()=>{index=i;show();};strip.append(t);return t;});
  wrap.append(strip);
 }
 function show(){const a=assets[index];front.src=a.url;front.alt=a.title;back.hidden=true;count.hidden=assets.length<2;count.textContent=`${index+1} / ${assets.length}`;button.setAttribute('aria-label',a.title+(assets.length>1?'，滑动切换，点击放大':'，点击放大'));thumbs.forEach((t,i)=>{t.setAttribute('aria-current',String(i===index));if(i===index){const s=t.parentElement;s.scrollLeft=Math.max(0,t.offsetLeft-(s.clientWidth-t.offsetWidth)/2);}});}
 function turn(d){index=(index+d+assets.length)%assets.length;show();}
 button.onclick=()=>{if(dragged){dragged=false;return;}lightbox(assets[index],button);};
 button.addEventListener('wheel',e=>{if(assets.length<2)return;e.preventDefault();e.stopPropagation();const now=performance.now();if(now-last<320){total=0;return;}const d=(Math.abs(e.deltaX)>Math.abs(e.deltaY)?e.deltaX:e.deltaY)*(e.deltaMode===1?16:1);if(Math.sign(total)!==Math.sign(d))total=0;total+=d;if(Math.abs(total)>30){turn(total>0?1:-1);last=now;total=0;}},{passive:false});
 button.onpointerdown=e=>{x=e.clientX;y=e.clientY;dragged=false;button.setPointerCapture(e.pointerId);};
 button.onpointerup=e=>{const dx=e.clientX-x,dy=e.clientY-y;if(Math.abs(dx)>35&&Math.abs(dx)>Math.abs(dy)&&assets.length>1){dragged=true;turn(dx<0?1:-1);}};
 button.onkeydown=e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();turn(e.key==='ArrowRight'?1:-1);}};
 show();return wrap;
}
