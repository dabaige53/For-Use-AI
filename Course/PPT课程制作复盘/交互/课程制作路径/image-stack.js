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
 function show(){const a=assets[index];front.src=a.url;front.alt=a.title;back.src=assets[(index+1)%assets.length].url;back.hidden=assets.length<2;count.hidden=assets.length<2;count.textContent=`${index+1} / ${assets.length}`;button.setAttribute('aria-label',a.title+(assets.length>1?'，滑动切换，点击放大':'，点击放大'));}
 function turn(d){index=(index+d+assets.length)%assets.length;show();}
 button.onclick=()=>{if(dragged){dragged=false;return;}lightbox(assets[index],button);};
 button.addEventListener('wheel',e=>{if(assets.length<2)return;e.preventDefault();e.stopPropagation();const now=performance.now();if(now-last<320){total=0;return;}const d=(Math.abs(e.deltaX)>Math.abs(e.deltaY)?e.deltaX:e.deltaY)*(e.deltaMode===1?16:1);if(Math.sign(total)!==Math.sign(d))total=0;total+=d;if(Math.abs(total)>30){turn(total>0?1:-1);last=now;total=0;}},{passive:false});
 button.onpointerdown=e=>{x=e.clientX;y=e.clientY;dragged=false;button.setPointerCapture(e.pointerId);};
 button.onpointerup=e=>{const dx=e.clientX-x,dy=e.clientY-y;if(Math.abs(dx)>35&&Math.abs(dx)>Math.abs(dy)&&assets.length>1){dragged=true;turn(dx<0?1:-1);}};
 button.onkeydown=e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();turn(e.key==='ArrowRight'?1:-1);}};
 show();return wrap;
}
