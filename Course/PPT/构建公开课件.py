#!/usr/bin/env python3
"""Export the presentation and its linked interactive materials for Cloudflare Pages."""
import argparse
import html
import json
import re
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / 'Course'
PPT = COURSE / 'PPT/AI协作-动态幻灯片.html'
REVIEW = COURSE / 'PPT课程制作复盘/交互/课程制作路径'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='A new output directory')
    parser.add_argument('--preview', default='http://127.0.0.1:4189')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    copied = set()
    omitted = set()

    def write(name, text):
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def public_path(path):
        if path.is_relative_to(COURSE):
            return Path('Course') / path.relative_to(COURSE)
        return Path('references') / path.relative_to(ROOT)

    def include(path):
        path = path.resolve()
        if not path.is_relative_to(ROOT) or any(x in path.parts for x in ('.trash', '.git', '.codex', '对话数据')):
            omitted.add(str(path))
            return None
        if not path.is_file():
            return None
        dest = public_path(path)
        if path in (PPT.parent / 'assets/video_llm.mp4', PPT.parent / 'assets/video_io.mp4'):
            return '/' + urllib.parse.quote(dest.as_posix())
        if path in copied:
            return '/' + urllib.parse.quote(dest.as_posix())
        copied.add(path)
        if path.stat().st_size > 25 * 1024 * 1024:
            raise ValueError(f'Pages asset exceeds 25 MiB: {path}')
        target = out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix in ('.html', '.js', '.css', '.md'):
            text = path.read_text()
            if path == PPT:
                text = text.replace('data-course-src="/mermaid"', 'data-course-src="/mermaid.html"')
                text = text.replace('<title>AI × WORK — 可编辑 HTML</title>', '<title>AI × WORK · 伍文渊</title>')
            # Copy runtime dependencies and media; prose links do not pull in private working records.
            if path.suffix != '.md':
                refs = re.findall(r'''(?:["']|url\()([^\s<>"'()]{1,300}\.(?:html|js|css|png|jpg|jpeg|gif|webp|svg|mp4|woff2?|json|md)(?:\?[^<>"'()\s]*)?)(?:["']|\))''', text)
            else:
                refs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)|(?:src|poster)=["\']([^"\']+)["\']', text)
                refs = [a or b for a, b in refs]
            for ref in refs:
                url = urllib.parse.urlsplit(html.unescape(ref))
                if url.scheme or url.netloc or not url.path or url.path.startswith('/'):
                    continue
                include(path.parent / urllib.parse.unquote(url.path))
            # Machine-local links are not useful on the public site.
            text = re.sub(r'\[([^\]]+)\]\((?:file://)?/Users/[^)]+\)', r'\1', text)
            target.write_text(text, encoding='utf-8')
        else:
            shutil.copyfile(path, target)
        return '/' + urllib.parse.quote(dest.as_posix())

    data = json.loads((REVIEW / '节点材料.json').read_text())
    records = json.loads((REVIEW / '节点对话.json').read_text())
    used = set()
    def collect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ('asset', 'preview'):
                    used.add(item)
                elif key == 'images':
                    used.update(item)
                if key not in ('evidence', 'verification', 'imageOrigin'):
                    collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)
        elif isinstance(value, str):
            used.update(re.findall(r'asset:([A-Za-z0-9_-]+)', value))
    collect(records)
    assets = {}
    for key in sorted(used):
        asset = data['assets'][key]
        source_path = Path(asset['path'])
        url = include(source_path if source_path.is_absolute() else COURSE / source_path)
        if url:
            assets[key] = {k: asset[k] for k in ('title', 'kind', 'description') if k in asset}
            assets[key].update(url=url, download=url)

    def links(items):
        return [{k:v for k,v in item.items() if k in ('asset','url','title','label','description','preview')}
                for item in items if item.get('asset') in assets or item.get('url','').startswith('https://')]

    def messages(items):
        return [{'role': item['role'], 'text': item['text'], 'images': [x for x in item.get('images',[]) if x in assets]} for item in items]

    nodes = {}
    for key, node in data['nodes'].items():
        record = records[key]
        clean = {'links': links(record.get('links',[])), 'outputs': links(record.get('outputs',[])), 'messages': messages(record.get('messages',[]))}
        if record.get('conversations'):
            threads = {}
            clean['conversations'] = []
            for section in record['conversations']:
                thread = section.get('threadId','default')
                threads.setdefault(thread, str(len(threads)))
                clean['conversations'].append({'threadId':threads[thread], 'messages':messages(section.get('messages',[]))})
        nodes[key] = {'title': node['title'], 'record':clean}
    edges = [{k: edge[k] for k in ('from', 'to', 'label') if k in edge}
             for edge in data['edges']]
    write('details.json', json.dumps({'title':data['title'], 'assets':assets, 'nodes':nodes, 'edges':edges}, ensure_ascii=False))
    include(PPT)
    include(PPT.parent / 'AI协作-演讲稿.md')
    include(PPT.parent / 'AI协作-演讲稿-90分钟版-新课件.md')
    page = urllib.request.urlopen(args.preview + '/mermaid').read().decode()
    page = page.replace("fetch('/files')", "fetch('/files.json')").replace('fetch(`/source/${id}`', 'fetch(`/source/${id}.json`')
    write('mermaid.html', page)
    write('files.json', '[{"id":0,"name":"课程制作主路径.mmd"}]')
    source = COURSE / 'PPT课程制作复盘/图解/课程制作主路径.mmd'
    write('source/0.json', json.dumps({'name':source.name,'code':source.read_text()},ensure_ascii=False))
    for name in ('details.js','details.css','image-stack.js','build/canvas.js','build/canvas.css'):
        write(name, (REVIEW / name).read_text().replace("fetch('/details')", "fetch('/details.json')"))
    if '/vendor/mermaid/' in page:
        raise ValueError('Re-render the flowchart SVG and restart the preview before publishing.')
    write('index.html', '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>AI × WORK</title><script>location.replace('+json.dumps('/'+urllib.parse.quote(public_path(PPT).as_posix()))+'+location.hash)</script></html>')
    write('404.html', '<!doctype html><meta charset="utf-8"><title>页面不存在</title><p>页面不存在。<a href="/">返回课件</a></p>')
    write('_headers', '/*.json\n  Content-Type: application/json; charset=utf-8\n/*.mjs\n  Content-Type: text/javascript; charset=utf-8\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')
    write('_worker.js', (PPT.parent / 'pages-video-worker.mjs').read_text())
    write('_routes.json', json.dumps({'version':1,'include':['/Course/PPT/assets/*.mp4'],'exclude':[]}))
    files = [p for p in out.rglob('*') if p.is_file()]
    for p in files:
        if p.stat().st_size > 25*1024*1024:
            raise ValueError(f'Asset too large: {p}')
    print(json.dumps({'output':str(out),'files':len(files),'sizeMiB':round(sum(p.stat().st_size for p in files)/1024**2,1),'nodes':len(nodes),'assets':len(assets),'omittedArchivedAssets':len(omitted)},ensure_ascii=False))

if __name__ == '__main__':
    main()
