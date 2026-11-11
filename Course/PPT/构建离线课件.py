#!/usr/bin/env python3
"""把云端课件快照拼成可离线放映的网页版。

输入：云端下载/<日期>/project（deck.json + slides/*.html）、云端下载/<日期>/assets（图片）、
assets/clips（视频片段）。输出：交付/和AI做同事-离线版/（index.html + img/ + video/）。
用法：python3 构建离线课件.py [快照目录]
"""
import json
import re
import shutil
import sys
from pathlib import Path

PPT = Path(__file__).resolve().parent
SNAP = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else PPT / '云端下载' / '2026-10-23'
OUT = PPT / '交付' / '和AI做同事-离线版'

# 云端视频编号 → 本地片段文件（见 云端下载/<日期>/assets/README.md）
CLIPS = {
    'c3cb91ef77313656ce27caff31395f4f': 'video-generate.mp4',
    'bb2647bc68738e14c119dcac6b31ef8b': 'video-train.mp4',
    'a39509f6fcc5cab4b94d58cfc9344ad4': 'video-feedback.mp4',
    '56928fc213e691daf97c6b3b384fbbc1': 'video-io-1.mp4',
    '25eb665ca63d90e8c095242a4d7c7f30': 'video-io-2.mp4',
}

# Lucide 线性图标（只收录课件用到的）
ICONS = {
    'Book': '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/>',
    'Chart': '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    'Chat': '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    'CheckCircle': '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    'Clock': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    'Lightbulb': '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    'Search': '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    'Settings': '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
    'Star': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    'Users': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'Warning': '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    'Wrench': '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
}

STYLE = r"""
@font-face{font-family:'Noto Sans SC';font-weight:400;src:local('Noto Sans SC'),local('NotoSansSC-Regular'),local('PingFangSC-Regular'),local('Microsoft YaHei')}
@font-face{font-family:'Noto Sans SC';font-weight:700;src:local('Noto Sans SC Bold'),local('NotoSansSC-Bold'),local('PingFangSC-Semibold'),local('Microsoft YaHei Bold')}
*{margin:0;box-sizing:border-box}
html,body{height:100%;background:#0d1118;overflow:hidden}
body{font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif}
#stage{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:center}
section{position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:hidden;display:none;flex-direction:column;font-family:'Noto Sans SC',sans-serif}
section.on{display:flex}
section div{display:flex;flex-direction:column}
h1{font-size:96px;font-weight:600;line-height:1.1}h2{font-size:64px;font-weight:600;line-height:1.15}
h3{font-size:44px;font-weight:600;line-height:1.2}p{font-size:32px;line-height:1.4}
img,video,svg{display:block}
x-shape{display:block}x-shape[kind=ellipse]{border-radius:50%}
x-icon{display:inline-block;flex:none}x-icon svg{width:100%;height:100%}
table{border-collapse:collapse}th,td{padding:.35em .6em;border-bottom:1px solid #e3e7ed;text-align:left}th{font-weight:700}
aside{display:none}
video{cursor:pointer;background:#000}
.video-seek{position:absolute;left:84px;top:919px;width:1139px;height:32px;accent-color:#3b5ba9;cursor:pointer}
[data-build-in]{transition:opacity .45s ease,transform .45s ease}
.hide[data-build-in]{opacity:0;pointer-events:none}
.hide[data-fx=rise]{transform:translateY(48px)}
.hide[data-fx=pop]{transform:scale(.85)}
.hide[data-fx=drop]{transform:translateY(-48px)}
#notes{position:fixed;left:0;right:0;bottom:0;max-height:38vh;overflow:auto;padding:16px 24px;background:rgba(13,17,24,.92);color:#e8ecf3;font:18px/1.6 'PingFang SC',sans-serif;display:none}
#notes.on{display:block}
#hud{position:fixed;right:14px;bottom:10px;color:#8a93a3;font:14px sans-serif;opacity:0;transition:opacity .3s}
body:hover #hud{opacity:1}
#help{position:fixed;left:14px;bottom:10px;color:#8a93a3;font:14px 'PingFang SC',sans-serif;opacity:0;transition:opacity .3s}
body:hover #help{opacity:1}
"""

SCRIPT = r"""
const stage=document.getElementById('stage'),slides=[...stage.querySelectorAll('section')];
const notes=document.getElementById('notes'),hud=document.getElementById('hud');
const STATIC=new URLSearchParams(location.search).has('static');
let cur=0,step=0;
function fit(){const k=Math.min(innerWidth/1920,innerHeight/1080);stage.style.transform=`translate(-50%,-50%) scale(${k})`}
function groups(s){return [...new Set([...s.querySelectorAll('[data-build-in]')].map(e=>+e.dataset.order))].sort((a,b)=>a-b)}
function paint(){const s=slides[cur],g=groups(s);s.querySelectorAll('[data-build-in]').forEach(e=>e.classList.toggle('hide',!STATIC&&g.indexOf(+e.dataset.order)>=step));
  notes.textContent=(s.querySelector('aside')||{}).textContent||'';hud.textContent=`${cur+1} / ${slides.length}`+(g.length?`  ·  ${Math.min(step,g.length)}/${g.length}`:'');
  history.replaceState(null,'',location.search+'#'+(cur+1))}
function stopVideos(s){s.querySelectorAll('video').forEach(v=>{v.pause();v.currentTime=0})}
function go(i,full){if(i<0||i>=slides.length)return;stopVideos(slides[cur]);slides[cur].classList.remove('on');cur=i;slides[cur].classList.add('on');step=full?groups(slides[cur]).length:0;paint()}
function next(){const g=groups(slides[cur]);if(step<g.length){step++;paint()}else go(cur+1)}
function prev(){if(step>0){step--;paint()}else go(cur-1,true)}
addEventListener('keydown',e=>{const k=e.key;
  if(e.target.matches('input[type="range"]'))return;
  if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(k)){e.preventDefault();next()}
  else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(k)){e.preventDefault();prev()}
  else if(k==='Home')go(0);else if(k==='End')go(slides.length-1,true);
  else if(k==='n'||k==='N')notes.classList.toggle('on');
  else if(k==='f'||k==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}});
stage.addEventListener('click',e=>{if(e.target.closest('video,.video-seek'))return;next()});
stage.querySelectorAll('.video-seek').forEach(seek=>{
  const slide=seek.closest('section'),video=slide.querySelector('video'),elapsed=slide.querySelector('.video-elapsed');
  const update=()=>{if(!Number.isFinite(video.duration))return;seek.value=video.currentTime/video.duration*100;
    const s=Math.floor(video.currentTime);elapsed.textContent=String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')};
  video.addEventListener('timeupdate',update);video.addEventListener('loadedmetadata',update);
  seek.addEventListener('input',()=>{video.currentTime=video.duration*seek.value/100});
});
addEventListener('resize',fit);fit();
const h=parseInt(location.hash.slice(1));go(h>0&&h<=slides.length?h-1:0,STATIC);
"""


def blob_files():
    m = {}
    for f in (SNAP / 'assets').iterdir():
        if re.fullmatch(r'[0-9a-f]{32}\.\w+', f.name):
            m[f.stem] = f.name
    return m


def convert(html, imgs, used_img, used_clip):
    seek = '<input class="video-seek" type="range" min="0" max="100" value="0" step="0.1" aria-label="调整视频播放进度">'
    if any(f'id="{sid}"' in html for sid in ('video-generate', 'video-train', 'video-feedback')):
        html = re.sub(
            r'<p style="position:absolute;left:84px;top:884px;width:120px;font-size:24px;color:#677184">\d\d:\d\d</p>',
            '<p class="video-elapsed" style="position:absolute;left:84px;top:884px;width:120px;font-size:24px;color:#677184">00:00</p>',
            html,
        )
        html = re.sub(
            r'<div style="position:absolute;left:84px;top:932px;width:1139px;height:7px;[^"]+"></div>\s*'
            r'<div style="position:absolute;left:84px;top:932px;width:\d+px;height:7px;[^"]+"></div>\s*'
            r'<div style="position:absolute;left:\d+px;top:927px;width:17px;height:17px;[^"]+"></div>',
            seek,
            html,
        )
    elif any(f'id="{sid}"' in html for sid in ('video-io-1', 'video-io-2')):
        html = html.replace(
            '<p style="position:absolute;left:1304px;top:400px;',
            seek + '<p class="video-elapsed" style="position:absolute;left:84px;top:960px;font-size:24px;color:#677184">00:00</p>'
            '<p style="position:absolute;left:1304px;top:400px;',
        )

    def img_src(match):
        bid = match.group(1)
        if bid not in imgs:
            raise SystemExit(f'缺少图片 {bid}，先从云端下载到 assets/')
        used_img.add(imgs[bid])
        return f'src="img/{imgs[bid]}"'

    # 视频：带 data-video 的静帧图换成 <video>
    def video(match):
        tag = match.group(0)
        clip_match = re.search(r'data-video="/_blob/([0-9a-f]{32})"', tag)
        poster_match = re.search(r'src="/_blob/([0-9a-f]{32})"', tag)
        style_match = re.search(r'style="([^"]*)"', tag)
        if not (clip_match and poster_match and style_match):
            raise SystemExit(f'视频标签缺少有效的视频、图片或样式：{tag}')
        clip = clip_match.group(1)
        poster = poster_match.group(1)
        style = style_match.group(1)
        alt = (re.search(r'alt="([^"]*)"', tag) or [None, ''])[1]
        used_clip.add(CLIPS[clip])
        poster_attr = ''
        if CLIPS[clip] not in ('video-io-1.mp4', 'video-io-2.mp4'):
            used_img.add(imgs[poster])
            poster_attr = f' poster="img/{imgs[poster]}"'
        return (f'<video src="video/{CLIPS[clip]}"{poster_attr} controls preload="metadata" playsinline '
                f'aria-label="{alt}" style="{style}"></video>')

    html = re.sub(r'<img[^>]*data-video="[^"]*"[^>]*>', video, html)
    html = re.sub(r'src="/_blob/([0-9a-f]{32})"', img_src, html)

    def icon(match):
        name, rest = match.group(1), match.group(2)
        body = ICONS.get(name)
        if body is None:
            raise SystemExit(f'图标 {name} 没有收录，补进 ICONS')
        return (f'<x-icon name="{name}"{rest}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</svg></x-icon>')

    html = re.sub(r'<x-icon name="([A-Za-z]+)"([^>]*)>\s*</x-icon>', icon, html)

    def connector(match):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', match.group(0)))
        x1, y1, x2, y2 = (float(a[k]) for k in ('x1', 'y1', 'x2', 'y2'))
        st = a.get('style', '')
        color_match = re.search(r'color:\s*([^;]+)', st)
        width_match = re.search(r'border-width:\s*([\d.]+)', st)
        color = color_match.group(1).strip() if color_match else '#a7b0bf'
        w = float(width_match.group(1)) if width_match else 2.0
        dash = ' stroke-dasharray="8 6"' if 'dashed' in st else ''
        head = a.get('head', 'end')
        build = f' data-build-in="{a["data-build-in"]}"' if 'data-build-in' in a else ''
        mk = f'<marker id="h{id(match)}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{4 + w}" markerHeight="{4 + w}" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="{color}"/></marker>'
        ends = (f' marker-end="url(#h{id(match)})"' if head in ('end', 'both') else '') + \
               (f' marker-start="url(#h{id(match)})"' if head == 'both' else '')
        return (f'<svg{build} width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;pointer-events:none">'
                f'<defs>{mk}</defs><line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{dash}{ends}/></svg>')

    html = re.sub(r'<x-connector[^>]*>(\s*</x-connector>)?', connector, html)
    html = re.sub(r'<x-shape([^>]*)>\s*</x-shape>', r'<x-shape\1></x-shape>', html)

    # 逐步显示：拆出效果和顺序，供播放脚本使用
    def build(match):
        fx, order = match.group(1), match.group(2)
        return f'data-build-in="{fx} {order}" data-fx="{fx}" data-order="{order}"'

    html = re.sub(r'data-build-in="(\w+) (\d+)(?: auto)?"', build, html)
    return html


def main():
    deck = json.loads((SNAP / 'project' / 'deck.json').read_text())
    imgs = blob_files()
    used_img, used_clip, parts = set(), set(), []
    for sid in deck['order']:
        html = (SNAP / 'project' / 'slides' / f'{sid}.html').read_text()
        parts.append(convert(html, imgs, used_img, used_clip))

    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ('img', 'video'):
        if (OUT / sub).exists():
            shutil.rmtree(OUT / sub)
        (OUT / sub).mkdir()
    for f in used_img:
        shutil.copy2(SNAP / 'assets' / f, OUT / 'img' / f)
    for f in used_clip:
        src = PPT / 'assets' / 'clips' / f
        if not src.exists():
            raise SystemExit(f'缺少视频片段 {src}，按 assets/README.md 的区间重新剪')
        shutil.copy2(src, OUT / 'video' / f)

    title = deck.get('title', '课件')
    page = (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{title}</title>'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><style>{STYLE}</style></head><body>'
            f'<div id="stage">{"".join(parts)}</div><div id="notes"></div><div id="hud"></div>'
            f'<div id="help">→ / 空格 / 点击：下一步　← 上一步　F 全屏　N 讲师备注　使用视频控件播放 / 暂停</div>'
            f'<script>{SCRIPT}</script></body></html>')
    (OUT / 'index.html').write_text(page)
    (OUT / '.gitignore').write_text('img/\nvideo/\n')
    print(f'{OUT}/index.html：{len(parts)} 页，图片 {len(used_img)} 张，视频 {len(used_clip)} 段')


if __name__ == '__main__':
    main()
