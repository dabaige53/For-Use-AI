"""Extract cue-end frames and contact sheets for human/model visual review."""
import argparse
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    args=parser.parse_args()
    report=json.loads((args.directory/'verification.json').read_text())
    output=args.directory/'review'
    output.mkdir(exist_ok=False)
    samples=[]
    for shot in report['timeline']:
        cues=shot['cues']
        grid=Image.new('RGB',(854*3,504*((len(cues)+2)//3)))
        for index,cue in enumerate(cues):
            end=cues[index+1]['time'] if index+1<len(cues) else shot['source_out']
            time=max(cue['time'],end-.3)
            frame=output/f"{cue['key']}.png"
            subprocess.run(['ffmpeg','-v','error','-ss',str(time),'-i',str(args.directory/shot['file']),'-frames:v','1',str(frame)],check=True)
            with Image.open(frame) as image:
                grid.paste(image,(index%3*854,index//3*504+24))
                assert max(image.getpixel((0,0)))<5,'Background is not black'
            ImageDraw.Draw(grid).text((index%3*854+10,index//3*504+5),f"{cue['key']} / {time:.2f}s",fill='white')
            samples.append({'key':cue['key'],'time':time,'file':str(frame.name)})
        grid.save(output/f"{shot['scene']}-contact.png")
    (output/'samples.json').write_text(json.dumps(samples,indent=2))

if __name__=='__main__':
    main()
