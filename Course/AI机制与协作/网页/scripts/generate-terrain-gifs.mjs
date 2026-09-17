import {createCanvas,GlobalFonts} from '@napi-rs/canvas';
import {readFile,writeFile,mkdir,mkdtemp} from 'node:fs/promises';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {tmpdir} from 'node:os';
import {execFileSync} from 'node:child_process';
import vm from 'node:vm';
const chapter=resolve(dirname(fileURLToPath(import.meta.url)),'../../04-表达需求与反馈');
const args=process.argv.slice(2);
if(args.includes('--help')){console.log('node scripts/generate-terrain-gifs.mjs [--output DIR] [--only balance|entangle|case-better|drift|distill]\nPreserves original cases, labels, camera, black background and 26 frames at 16 fps. Requires ffmpeg.');process.exit(0)}
for(let i=0;i<args.length;i+=2)if(!['--only','--output'].includes(args[i])||!args[i+1])throw Error('Invalid option; use --help');
const opt=(key,fallback)=>args.includes(key)?args[args.indexOf(key)+1]:fallback;
const output=resolve(opt('--output',join(chapter,'配图')));
const html=await readFile(join(chapter,'案例/思维地形-体素沙盘.html'),'utf8');
const font=html.match(/src:url\(data:font\/woff;base64,([^)]+)\)/)?.[1];
if(!font||!GlobalFonts.register(Buffer.from(font,'base64'),'Terrain Sans'))throw Error('Original embedded font could not be loaded');
// Evaluate only the existing pure geometry/drawing functions; do not start a browser or DOM event loop.
const source=html.slice(html.indexOf('const $=id=>'),html.indexOf("canvas.addEventListener('pointerdown'"));
const ids=['balance','entangle','case_better','drift','distill'].filter(id=>!args.includes('--only')||id.replaceAll('_','-')===opt('--only'));
if(!ids.length)throw Error('Unknown --only');
await mkdir(output,{recursive:true});const work=await mkdtemp(join(tmpdir(),'course04-preserved-'));const audit=[];
console.log('关键帧目录：'+work);
for(const id of ids)for(const after of [false,true]){
 const canvas=createCanvas(2040,1140);
 const scope=vm.createContext({document:{getElementById:id=>id==='world'?canvas:null,documentElement:{classList:{contains:()=>true}}},Math,console});
 vm.runInContext(source,scope);scope.mechId=id;scope.afterValue=after;
 vm.runInContext(`
 W=680;H=380;DPR=3;
 naturalDistance=Math.max(23.8,H/(2*Math.tan(.355))*17/W+5.5);
 state.index=MECH.findIndex(m=>m.id===mechId);state.after=afterValue;state.playing=false;state.night=0;
 model=prepare(MECH[state.index]);resetView();
 function exportFrame(t){
 state.t=t;frameState=phaseData(t,state.after);updateCamera();shapes=[];labels=[];hits=[];
 ctx.setTransform(3,0,0,3,0,0);ctx.globalAlpha=1;ctx.fillStyle='#000000';ctx.fillRect(0,0,W,H);
 terrain();special();actors();flush();
 const drawn=[];const originalFill=ctx.fillText.bind(ctx);ctx.fillText=(text,...args)=>{drawn.push(text);return originalFill(text,...args)};
 drawLabels();ctx.fillText=originalFill;
 const missing=labels.filter(l=>!drawn.includes(l.text));if(missing.length)throw Error("Unplaced labels: "+JSON.stringify(missing));
 return {labels:labels.map(l=>l.text),ball:project(...surfaceSphere(motion(t,state.after).pos,.21))};
 }`,scope);
 const name=`04-terrain-${id.replaceAll('_','-')}-${after?'b':'a'}`;const checks=[];
 for(let f=0;f<26;f++){
  checks.push(vm.runInContext(`exportFrame(${f/25})`,scope));
  const png=canvas.toBuffer('image/png');await writeFile(join(work,`frame_${String(f).padStart(3,'0')}.png`),png);
  if([0,6,13,19,25].includes(f))await writeFile(join(work,`${name}-${f}.png`),png);
 }
 execFileSync('ffmpeg',['-y','-framerate','16','-i',join(work,'frame_%03d.png'),'-filter_complex','split[a][b];[a]palettegen=max_colors=256[p];[b][p]paletteuse=dither=sierra2_4a','-loop','0',join(output,name+'.gif')],{stdio:'ignore'});
 audit.push({name,width:2040,height:1140,sourceFrames:26,sourceFPS:16,checks});console.log('已修复 '+name+'.gif');
}
await writeFile(join(work,'audit.json'),JSON.stringify(audit,null,2)+'\n');
