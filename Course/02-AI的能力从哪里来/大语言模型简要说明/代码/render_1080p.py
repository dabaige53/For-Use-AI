"""Render timeline sources at 1080p30, then compose 419 seconds.

UV_CACHE_DIR=/private/tmp/course-uv-cache uv run --no-sync python render_1080p.py
"""
from pathlib import Path
import json
import subprocess
import sys
import hashlib
import shutil
from datetime import datetime
ROOT = Path(__file__).resolve().parent
COURSE = ROOT.parent
MODULES = {g: 'reconstruction_' + g + ('_zh' if g not in ('chat','flow') else '') + '.py' for g in ('core','chat','flow','feedback','gpu','paper','overlays')}
def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def main():
    manifest=json.loads((COURSE/'时间线.json').read_text())
    sources=list(dict.fromkeys(l['source'] for s in manifest['shots'] for l in s['layers'] if 'source' in l))
    logs=ROOT/'logs/1080p'; logs.mkdir(parents=True,exist_ok=True)
    records=[]
    completed = {r['source'] for r in json.loads((logs/'source-report.json').read_text())} if (logs/'source-report.json').exists() else set()
    for source in sources:
        target=ROOT/source
        if 'zh-1080p' in source or not target.exists():
            group=target.parent.name.removeprefix('reconstruction-').removesuffix('-zh-1080p')
            scene=target.stem.removesuffix('-final')
            module = MODULES[group] if group in MODULES else ('group_a.py' if scene == 'ManyComputationsPerUnitTimeV2' else 'group_b.py')
            if not target.exists() or source not in completed:
                target.parent.mkdir(parents=True,exist_ok=True)
                print('Rendering',scene,flush=True)
                command=[sys.executable,'-m','manimlib',module,scene,'-w','-r','1920x1080','--fps','30','--file_name',str(target)]
                with (logs/(scene+'.log')).open('w') as log:
                    subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        media=probe(target); video=media['streams'][0]
        assert (video['width'],video['height'],video['avg_frame_rate'])==(1920,1080,'30/1'),source
        subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True)
        records.append({'source':source,'size':[1920,1080],'fps':30,'decode':'passed','duration':float(media['format']['duration'])})
        (logs/'source-report.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
        print(f'Verified {len(records)}/{len(sources)}: {source}', flush=True)
    subprocess.run([sys.executable,str(ROOT/'compose_reconstruction.py')],cwd=ROOT,check=True)
    final = COURSE/'生成/mini-llm-zh-1080p-0000-0659.mp4'
    media = probe(final)
    video = media['streams'][0]
    assert (video['width'], video['height'], video['avg_frame_rate'], int(video['nb_frames'])) == (1920,1080,'30/1',12570)
    assert float(media['format']['duration']) == 419 and len(media['streams']) == 1
    subprocess.run(['ffmpeg','-v','error','-i',str(final),'-f','null','-'],check=True)
    previous_validation = json.loads((COURSE/'验收.json').read_text()) if (COURSE/'验收.json').exists() else {}
    archive = COURSE/'.trash'/('1080p-upgrade-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    archive.mkdir(parents=True,exist_ok=True)
    for name in ('视频.mp4','镜头','验收.json'):
        if (COURSE/name).exists(): shutil.move(str(COURSE/name),str(archive/name))
    shutil.move(str(final),str(COURSE/'视频.mp4'))
    shutil.move(str(COURSE/'生成/镜头'),str(COURSE/'镜头'))
    validation = previous_validation | {'duration_seconds':419,'size':[1920,1080],'fps':30,'frames':12570,'audio_streams':0,'subtitle_streams':0,'decode':'passed','subtitle_cues':86,'video_sha256':hashlib.sha256((COURSE/'视频.mp4').read_bytes()).hexdigest(),'source_render_report':'代码/logs/1080p/source-report.json','reproduce':'cd 代码 && UV_CACHE_DIR=/private/tmp/course-uv-cache uv run --no-sync python render_1080p.py','visual_review':'pending: review this newly rendered export','previous_outputs':str(archive.relative_to(COURSE))}
    validation.pop('original_38_sha256_unchanged', None)
    (COURSE/'验收.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
    print('Final 1080p video verified and installed:',COURSE/'视频.mp4',flush=True)
if __name__=='__main__': main()
