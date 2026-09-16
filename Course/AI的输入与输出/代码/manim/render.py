"""Render in explicit order; preserve cues and verify complete decoding."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
COURSE=ROOT.parents[1]
SCENES=['FirstInput','GenerateExecute','ReturnAnswer']

def run(command,log=None,env=None):
    if log:
        with log.open('w') as handle:
            subprocess.run(command,cwd=ROOT,env=env,stdout=handle,stderr=subprocess.STDOUT,check=True)
    else:
        subprocess.run(command,cwd=ROOT,env=env,check=True)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))

def main():
    parser=argparse.ArgumentParser(description='Render AI I/O silent animation and validate media.')
    parser.add_argument('--scene',choices=['all',*SCENES,'ContinuityPreview'],default='all')
    parser.add_argument('--quality',choices=['480p','1080p'],default='480p')
    parser.add_argument('--fps',type=int,default=30)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if not 1<=args.fps<=60:
        parser.error('--fps must be between 1 and 60')
    output=(args.output or COURSE/'临时渲染/代码验证'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')).resolve()
    output.mkdir(parents=True,exist_ok=False)
    env=dict(os.environ,AI_IO_CUES=str(output/'cues'))
    selected=SCENES if args.scene=='all' else [args.scene]
    resolution='854x480' if args.quality=='480p' else '1920x1080'
    timeline=[]
    cursor=0.0
    for scene in selected:
        print(f'Rendering {scene} → {output}',flush=True)
        run([sys.executable,'-m','manimlib','scenes.py',scene,'-w','-r',resolution,'--fps',str(args.fps),
             '--video_dir',str(output),'--file_name',scene],output/f'{scene}.log',env)
        clip=output/f'{scene}.mp4'
        media=probe(clip)
        video=next(s for s in media['streams'] if s['codec_type']=='video')
        assert (video['width'],video['height'])==tuple(map(int,resolution.split('x')))
        assert video['avg_frame_rate']==f'{args.fps}/1'
        assert len(media['streams'])==1,'Preview must be silent'
        run(['ffmpeg','-v','error','-xerror','-i',str(clip),'-f','null','-'],output/f'{scene}-decode.log')
        duration=float(media['format']['duration'])
        cues=json.loads((output/'cues'/f'{scene}.json').read_text())['cues']
        timeline.append({'scene':scene,'file':clip.name,'start':cursor,'end':cursor+duration,
                         'source_in':0,'source_out':duration,'audio':None,'cues':cues,'media':media,'decode':'passed'})
        cursor+=duration
    final_media=None
    if args.scene=='all':
        concat=output/'concat.txt'
        concat.write_text(''.join(f"file '{name}.mp4'\n" for name in SCENES))
        final=output/f'AI_IO_{args.quality}_silent.mp4'
        run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(final)])
        run(['ffmpeg','-v','error','-xerror','-i',str(final),'-f','null','-'],output/'full-decode.log')
        final_media=probe(final)
    sources=[ROOT/'objects.py',ROOT/'scenes.py',ROOT/'render.py',ROOT/'uv.lock',
             COURSE/'素材/来源/whisper-mcp/transcribe_audio.schema.json',COURSE/'文章/正文.md']
    report={'kind':'silent-animation-preview','quality':args.quality,'fps':args.fps,'timeline':timeline,
            'duration':cursor,'final_media':final_media,'visual_check':'pending',
            'sources':{str(p.relative_to(COURSE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (output/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f'Complete, full decode passed: {output}',flush=True)

if __name__=='__main__':
    main()
