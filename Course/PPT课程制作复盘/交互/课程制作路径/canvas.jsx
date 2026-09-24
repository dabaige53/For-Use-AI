import Panzoom from '@panzoom/panzoom';
import './canvas.css';
let panzoom,cleanup=()=>{},readSize=()=>{};
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
function attach(){
 cleanup();panzoom?.destroy();
 const svg=document.querySelector('#canvas svg'),viewport=document.getElementById('viewport');if(!svg)return;
 const {width,height}=svg.viewBox.baseVal;
 svg.style.width=width+'px';svg.style.height=height+'px';svg.style.maxWidth='none';
 panzoom=Panzoom(svg,{minScale:.08,maxScale:3,origin:'0 0',cursor:'grab',step:.15});
 let frame=0,lastTime=0,target=null;
 const stop=()=>{cancelAnimationFrame(frame);frame=0;target=null;lastTime=0;};
 const zoomAt=(scale,point)=>{const r=viewport.getBoundingClientRect(),old=panzoom.getScale(),p=panzoom.getPan(),px=point.clientX-r.left,py=point.clientY-r.top;const x=p.x+px/scale-px/old,y=p.y+py/scale-py/old;panzoom.zoom(scale,{animate:false});panzoom.pan(x,y,{animate:false});};
 const update=now=>{
  const dt=lastTime?Math.min(40,now-lastTime):16;lastTime=now;
  const alpha=reduced?1:1-Math.exp(-dt/65),s=panzoom.getScale(),p=panzoom.getPan();
  if(target.kind==='zoom'){
   const next=s+(target.scale-s)*alpha;zoomAt(next,target.point);
   if(Math.abs(target.scale-next)<.0003){zoomAt(target.scale,target.point);stop();return;}
  }else{
   const ns=s+(target.scale-s)*alpha,nx=p.x+(target.x-p.x)*alpha,ny=p.y+(target.y-p.y)*alpha;
   panzoom.zoom(ns,{animate:false});panzoom.pan(nx,ny,{animate:false});
   if(Math.abs(target.scale-ns)<.0003&&Math.abs(nx-target.x)+Math.abs(ny-target.y)<.1){panzoom.zoom(target.scale);panzoom.pan(target.x,target.y);stop();return;}
  }
  frame=requestAnimationFrame(update);
 };
 const run=()=>{if(!frame)frame=requestAnimationFrame(update);};
 const center=()=>{const r=viewport.getBoundingClientRect();return {clientX:r.left+r.width/2,clientY:r.top+r.height/2};};
 const zoom=(scale,point=center())=>{target={kind:'zoom',scale:Math.max(.08,Math.min(3,scale)),point};run();};
 const fit=(immediate=false)=>{stop();const scale=Math.min((viewport.clientWidth-48)/width,(viewport.clientHeight-48)/height);const x=(viewport.clientWidth/scale-width)/2,y=24/scale;if(immediate){panzoom.zoom(scale);panzoom.pan(x,y);}else{target={kind:'view',scale,x,y};run();}};
 document.getElementById('fit').onclick=()=>fit();
 document.getElementById('plus').onclick=()=>zoom((target?.scale||panzoom.getScale())*1.25);
 document.getElementById('minus').onclick=()=>zoom((target?.scale||panzoom.getScale())/1.25);
 const wheel=e=>{
  if(e.target.closest('#detail-dialog'))return;e.preventDefault();
  const unit=e.deltaMode===1?16:e.deltaMode===2?viewport.clientHeight:1;
  if(e.ctrlKey||e.metaKey){zoom((target?.scale||panzoom.getScale())*Math.exp(-e.deltaY*unit*.008),{clientX:e.clientX,clientY:e.clientY});}
  else{const scale=panzoom.getScale(),p=target?.kind==='view'?target:panzoom.getPan();target={kind:'view',scale,x:p.x-e.deltaX*unit/scale,y:p.y-e.deltaY*unit/scale};run();}
 };
 viewport.addEventListener('wheel',wheel,{passive:false});
 svg.addEventListener('panzoomstart',stop);
 svg.addEventListener('panzoomchange',()=>{document.getElementById('zoom').textContent=Math.round(panzoom.getScale()*100)+'%';window.dispatchEvent(new Event('canvas-moved'));});
 readSize=()=>{svg.style.width=width+'px';svg.style.height=height+'px';const selected=svg.querySelector('[aria-expanded="true"]');const r=selected?.getBoundingClientRect();zoom(1,r?{clientX:r.left+r.width/2,clientY:r.top+r.height/2}:center());};
 const status=document.getElementById('status');requestAnimationFrame(()=>requestAnimationFrame(()=>{fit(true);status.textContent='拖动平移 · 双指滑动平移 · 双指捏合 / Ctrl＋滚轮缩放 · 点击节点查看材料';}));
 cleanup=()=>{stop();viewport.removeEventListener('wheel',wheel);};
}
document.addEventListener('mermaid-rendered',attach);
if(document.querySelector('#canvas svg'))attach();
window.addEventListener('mermaid-reading-size',()=>readSize());
