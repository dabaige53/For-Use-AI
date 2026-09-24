#!/usr/bin/env python3
"""Preview Mermaid locally with ELK and ChatGPT-like flowchart styling.

Usage: python mermaid-preview.py [one.mmd two.mmd ...] [--port 8765] [--open]
First run downloads pinned MIT-licensed Mermaid/ELK browser distributions from
npm into the OS cache. Subsequent runs work offline; no npm install is required.
This is an independent approximation, not ChatGPT's proprietary renderer.
"""

import argparse
import base64
import hashlib
import io
import json
import mimetypes
import os
from pathlib import Path
import sys
import tarfile
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, unquote, urlsplit
import webbrowser


PACKAGES = {"mermaid": ("mermaid", "11.12.0"), "elk": ("@mermaid-js/layout-elk", "0.2.0")}


def prepare_dependencies():
    if sys.platform == "darwin":
        cache_root = Path.home() / "Library/Caches"
    elif os.name == "nt":
        cache_root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    else:
        cache_root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    roots = {}
    for alias, (name, version) in PACKAGES.items():
        root = cache_root / "mermaid-chatgpt-preview" / f"{alias}-{version}"
        roots[alias] = root
        if (root / ".ready").exists():
            continue
        print(f"下载并缓存 {name}@{version} …", flush=True)
        with urllib.request.urlopen(f"https://registry.npmjs.org/{name}/{version}", timeout=60) as response:
            dist = json.load(response)["dist"]
        with urllib.request.urlopen(dist["tarball"], timeout=120) as response:
            archive = response.read()
        integrity = "sha512-" + base64.b64encode(hashlib.sha512(archive).digest()).decode()
        if integrity != dist["integrity"]:
            raise RuntimeError(f"{name} 下载校验失败，请重新运行。")
        root.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as package:
            for member in package:
                if not member.isfile() or not member.name.startswith("package/"):
                    continue
                relative = Path(member.name.removeprefix("package/"))
                if ".." in relative.parts or relative.is_absolute():
                    continue
                if relative.parts[0] != "dist" and not relative.name.upper().startswith("LICENSE"):
                    continue
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                source = package.extractfile(member)
                if source is None:
                    raise RuntimeError(f"依赖包中的文件无法读取：{member.name}")
                with source:
                    target.write_bytes(source.read())
        (root / ".ready").write_text(integrity, encoding="utf-8")
    return roots


HTML = r'''<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mermaid 预览</title>
<style>
:root{color-scheme:light;--bg:#fff;--panel:#f7f7f8;--ink:#27272a;--line:#e4e4e7}
:root[data-dark]{color-scheme:dark;--bg:#181818;--panel:#212121;--ink:#e8e8e8;--line:#383838}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif}
header{min-height:62px;padding:12px 18px;display:flex;align-items:center;flex-wrap:wrap;gap:8px;border-bottom:1px solid var(--line)}
header strong{margin-right:12px}button,select{font:inherit;color:inherit;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:7px 11px;cursor:pointer}
button:hover{background:var(--panel)}button:disabled{opacity:.45;cursor:default}#files{max-width:280px}#zoom{min-width:48px;text-align:center;font-variant-numeric:tabular-nums}
main{display:flex;height:calc(100dvh - 104px)}aside{display:flex;flex-direction:column;width:340px;min-width:200px;border-right:1px solid var(--line);background:var(--panel)}
aside[hidden]{display:none}aside p{margin:12px 14px;color:var(--ink);opacity:.65;font-size:12px}textarea{flex:1;resize:none;border:0;border-top:1px solid var(--line);outline:none;padding:16px;background:transparent;color:inherit;font:12px/1.7 ui-monospace,Menlo,monospace;tab-size:4}
#viewport{flex:1;overflow:auto;min-width:0}#canvas{padding:32px;min-width:100%;min-height:100%;width:max-content}#canvas svg{display:block;max-width:none!important;margin:auto}
footer{height:42px;border-top:1px solid var(--line);padding:10px 18px;overflow:auto;white-space:nowrap;font-size:12px}footer[data-error]{color:#d65454}
@media(max-width:760px){aside{width:38%}header{padding:8px}main{height:75dvh}}
</style>
<header>
  <strong>Mermaid 预览</strong><select id="files" aria-label="选择文件"></select>
  <button id="load">打开文件</button><input id="upload" type="file" accept=".mmd,.mermaid,.txt" hidden>
  <button id="reload">重读文件</button><button id="toggle">代码</button><button id="render" disabled>渲染</button>
  <button id="minus" aria-label="缩小">−</button><span id="zoom">100%</span><button id="plus" aria-label="放大">＋</button>
  <button id="fit">适应窗口</button><button id="theme">深色</button><button id="export" disabled>导出 SVG</button>
</header>
<main><aside id="editor"><p>粘贴或修改 Mermaid，点击渲染；不修改原文件。</p><textarea id="code" spellcheck="false" aria-label="Mermaid 代码"></textarea></aside>
<section id="viewport" aria-label="图形预览"><div id="canvas"></div></section></main>
<footer id="status" role="status">正在加载本地渲染器…</footer>
<script type="module">
const $ = id => document.getElementById(id);
let mermaid, elkLayouts, busy = false, pending = false, dark = false, scale = 1, width = 0, height = 0, serial = 0;
let filename = 'diagram.mmd', currentFile = null, svg = null;
const font = '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif';
function status(text, error = false) {
  $('status').textContent = text; $('status').toggleAttribute('data-error', error);
}
function colors() {
  return dark
    ? {bg:'#181818',surface:'#212121',text:'#99ceff',node:'#00284d',decision:'#000e1a',line:'#1a3e5f',border:'rgba(255,255,255,.1)',ink:'#e8e8e8'}
    : {bg:'#ffffff',surface:'#f7f7f8',text:'#004f99',node:'#e5f3ff',decision:'#f5faff',line:'#cedbe5',border:'rgba(0,0,0,.1)',ink:'#27272a'};
}
function flowCSS(c) {
  return `
  .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:${c.text}}
  .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-.08px;fill:${c.text}}
  .node tspan[font-weight="normal"],.edgeLabels tspan[font-weight="normal"]{font-weight:600}
  .node rect,.node circle,.node ellipse,.node polygon,.node path{fill:${c.node};stroke:${c.border};stroke-width:1px}
  .node rect{rx:16px;ry:16px}
  .node.preview-decision .label-container{fill:${c.decision};stroke:${c.line};stroke-dasharray:2 2}
  .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:${c.decision};stroke:${c.line};stroke-width:1px}
  .edgePaths .flowchart-link{stroke:${c.line};stroke-width:1px;stroke-linecap:round;stroke-linejoin:round}
  .marker{fill:${c.line};stroke:${c.line}}
  `;
}
function registerLayout() {
  const elk = elkLayouts.find(item => item.name === 'elk');
  mermaid.registerLayoutLoaders([...elkLayouts, {
    ...elk, name:'chatgpt-like', loader:async () => {
      const engine = await elk.loader();
      return {async render(graph, selection, helpers, ...rest) {
        for (const node of graph.nodes) {
          if (node.isGroup) continue;
          if (['diamond','diam','decision','question'].includes(node.shape)) {
            node.shape = 'rect'; node.cssClasses = `${node.cssClasses || ''} preview-decision`;
          }
          if (['rect','squareRect','proc','process','rectangle','rounded','roundedRect','event'].includes(node.shape)) {
            node.shape = 'rect'; node.padding = 16; node.labelPaddingX = 36;
            node.height = Math.max(node.height || 0, 60);
          }
        }
        await engine.render(graph, selection, {
          ...helpers,
          insertEdge(parent, edge, ...args) {
            const points = (edge.points || []).map(point => ({...point}));
            for (const [end, neighbor, arrow] of [[0,1,edge.arrowTypeStart],[points.length-1,points.length-2,edge.arrowTypeEnd]]) {
              if (arrow !== 'arrow_point' || !points[end] || !points[neighbor]) continue;
              const dx = points[neighbor].x - points[end].x, dy = points[neighbor].y - points[end].y;
              const length = Math.hypot(dx,dy);
              if (length) {const gap = Math.min(8,Math.max(0,length/2-4)); points[end].x += dx/length*gap; points[end].y += dy/length*gap;}
            }
            return helpers.insertEdge(parent,{...edge,points},...args);
          },
          async insertEdgeLabel(parent, edge) {
            const label = await helpers.insertEdgeLabel(parent,edge);
            const rect = label.querySelector('rect.background'), text = label.querySelector('text');
            if (edge.label && rect && text) {
              const box = text.getBBox(), h = Math.max(26,box.height+8);
              for (const [key,value] of Object.entries({x:box.x-12,y:box.y-(h-box.height)/2,width:box.width+24,height:h})) rect.setAttribute(key,value);
              rect.style.removeProperty('stroke');
              const bounds = label.getBBox(); edge.width = bounds.width; edge.height = bounds.height;
              label.parentElement?.setAttribute('transform',`translate(${-bounds.x-bounds.width/2},${-bounds.y-bounds.height/2})`);
            }
            return label;
          }
        }, ...rest);
        selection.selectAll('marker').each(function() {
          if (!/-point(?:End|Start)(?:_|$)/.test(this.id)) return;
          for (const [key,value] of Object.entries({viewBox:'-5 -5 10 10',markerWidth:10,markerHeight:10,refX:0,refY:0})) this.setAttribute(key,value);
          const sign = this.id.includes('-pointStart') ? -1 : 1, rise = 4.5/Math.SQRT2;
          for (const path of this.querySelectorAll('path')) {
            path.setAttribute('d',`M 0 0 L ${sign*4} 0 M ${sign*(4-rise)} ${-rise} L ${sign*4} 0 L ${sign*(4-rise)} ${rise}`);
            Object.assign(path.style,{fill:'none',strokeWidth:'1',strokeDasharray:'none',strokeLinecap:'round',strokeLinejoin:'round'});
          }
        });
      }};
    }
  }]);
}
function zoom(value) {
  if (!svg) return;
  scale = Math.max(.02,Math.min(4,value));
  svg.style.width = `${width*scale}px`; svg.style.height = `${height*scale}px`;
  $('zoom').textContent = `${Math.round(scale*100)}%`;
}
function fit() { if (svg) zoom(Math.min(1,($('viewport').clientWidth-64)/width,($('viewport').clientHeight-64)/height)); }
async function render() {
  if (!mermaid) return;
  if (busy) {pending = true; return;}
  busy = true; $('render').disabled = true; $('export').disabled = true;
  status('正在布局…'); $('canvas').dataset.state = 'rendering';
  try {
    const source = $('code').value.trim().replace(/%%\{[\s\S]*?\}%%/g,'').replace(/^\s*click\s+.*$/gm,'');
    const isFlow = /^(?:\s*%%[^\n]*\n)*\s*(?:flowchart|graph)\b/.test(source), c = colors();
    mermaid.initialize({startOnLoad:false,securityLevel:'strict',suppressErrorRendering:true,
      theme:'base',layout:isFlow?'chatgpt-like':'elk',look:'classic',htmlLabels:false,
      maxEdges:2000, maxTextSize:200000, fontFamily:font, darkMode:dark,
      themeVariables:{fontFamily:font,fontSize:'14px',background:c.bg,primaryColor:c.node,primaryTextColor:c.ink,
        primaryBorderColor:c.border,lineColor:c.line,textColor:c.ink,mainBkg:c.node,nodeBorder:c.border,
        clusterBkg:c.surface,clusterBorder:c.border,edgeLabelBackground:c.decision},
      themeCSS:isFlow?flowCSS(c):'',flowchart:{useMaxWidth:false,htmlLabels:false}});
    await document.fonts.ready;
    const result = await mermaid.render(`preview-${++serial}`,source);
    $('canvas').innerHTML = result.svg; svg = $('canvas').querySelector('svg');
    if (dark) for (const rect of svg.querySelectorAll('.node > .label-container[style*="fill"]')) {
      const fill = rect.style.getPropertyValue('fill');
      if (fill && fill !== 'transparent') rect.style.setProperty('fill',`color-mix(in oklab, ${fill} 22%, ${c.bg})`,'important');
      for (const text of rect.closest('.node').querySelectorAll('text,tspan')) text.style.setProperty('fill',c.ink,'important');
    }
    ({width,height} = svg.viewBox.baseVal); fit();
    $('canvas').dataset.state = 'ready'; $('export').disabled = false;
    document.dispatchEvent(new Event('mermaid-rendered'));
    status(`${filename} · ${svg.querySelectorAll('.node').length} 个节点 · ELK · ${dark?'深色':'浅色'}`);
  } catch (error) {
    $('canvas').replaceChildren(); svg = null; $('canvas').dataset.state = 'error';
    status(`无法渲染：${error.message || error}`,true);
  } finally {
    busy = false; $('render').disabled = false;
    if (pending) {pending = false; render();}
  }
}
async function loadFile(id) {
  try {
    const response = await fetch(`/source/${id}`,{cache:'no-store'});
    if (!response.ok) throw Error(await response.text());
    const data = await response.json(); filename = data.name; currentFile = id;
    $('code').value = data.code; await render();
  } catch (error) {status(`无法读取：${error.message}`,true);}
}
$('render').onclick = render;
$('code').addEventListener('input',() => { $('export').disabled = true; status('代码已修改，点击渲染查看。'); });
$('code').addEventListener('keydown',event => {if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') render();});
$('files').onchange = event => loadFile(event.target.value);
$('reload').onclick = () => currentFile === null ? render() : loadFile(currentFile);
$('load').onclick = () => $('upload').click();
$('upload').onchange = async event => {
  const file = event.target.files[0]; if (!file) return;
  filename = file.name; currentFile = null; $('files').selectedIndex = -1;
  $('code').value = await file.text(); render(); event.target.value = '';
};
$('toggle').onclick = () => {$('editor').hidden = !$('editor').hidden;fit();};
window.addEventListener('mermaid-reading-size',()=>zoom(1));
$('minus').onclick = () => zoom(scale/1.25); $('plus').onclick = () => zoom(scale*1.25); $('fit').onclick = fit;
$('theme').onclick = () => {dark=!dark;document.documentElement.toggleAttribute('data-dark',dark);$('theme').textContent=dark?'浅色':'深色';render();};
$('export').onclick = () => {
  if (!svg) return;
  const copy = svg.cloneNode(true); copy.setAttribute('xmlns','http://www.w3.org/2000/svg');
  copy.setAttribute('width',width); copy.setAttribute('height',height);
  copy.style.transform='none';copy.style.width=`${width}px`;copy.style.height=`${height}px`;copy.style.background=colors().bg;
  const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(copy)],{type:'image/svg+xml;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download=filename.replace(/\.[^.]+$/,'')+'.svg';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
try {
  [{default:mermaid},{default:elkLayouts}] = await Promise.all([
    import('/vendor/mermaid/dist/mermaid.esm.min.mjs'),import('/vendor/elk/dist/mermaid-layout-elk.esm.min.mjs')]);
  registerLayout(); $('render').disabled=false;
  const files=await (await fetch('/files')).json();
  for (const file of files) $('files').add(new Option(file.name,file.id));
  $('files').hidden = files.length === 0;
  if (files.length) await loadFile(files[0].id);
  else {$('code').value='flowchart LR\n    A[原始文章] --> B[HTML 原型]\n    B --> C{检查表达}\n    C -->|调整| B\n    C -->|采用| D[接入课件]';await render();}
} catch(error) {status(`渲染器加载失败：${error.message}`,true);}
</script>
</html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="要预览的 .mmd 文件，可同时指定多个")
    parser.add_argument("--port", type=int, default=8765, help="本地端口；0 表示自动选择")
    parser.add_argument("--open", action="store_true", help="启动后打开默认浏览器")
    parser.add_argument("--details", type=Path, help="节点材料 JSON，启用点击弹窗")
    parser.add_argument("--materials-root", type=Path, help="材料根目录，保留 HTML 与图片的相对引用")
    args = parser.parse_args()
    page = HTML
    details = None
    asset_paths = {}
    material_root = args.materials_root.expanduser().resolve() if args.materials_root else None
    if args.details:
        details_dir = args.details.expanduser().resolve().parent
        details = json.loads(args.details.read_text())
        records = details_dir / "节点对话.json"
        if records.is_file():
            for node_id, record in json.loads(records.read_text()).items():
                if node_id in details["nodes"]:
                    details["nodes"][node_id]["record"] = record
        for key, asset in details["assets"].items():
            path = Path(asset.pop("path")).resolve()
            if not path.is_file():
                parser.error(f"材料不存在：{path}")
            asset_paths[key] = path
            if path.name == "SKILL.md":
                asset_paths.setdefault(path.parent.name, path)
            asset["url"] = "/materials/" + quote(path.relative_to(material_root).as_posix()) if material_root and path.is_relative_to(material_root) else "/artifact/" + quote(key) + "/" + quote(path.name)
            asset["download"] = "/download/" + quote(key)
        page = page.replace("</style>", '</style><link rel="stylesheet" href="/details.css">')
        page = page.replace("</html>", '<link rel="stylesheet" href="/build/canvas.css"><script type="module" src="/details.js"></script><script type="module" src="/build/canvas.js"></script></html>')
    files = [path.expanduser().resolve() for path in args.files]
    for path in files:
        if not path.is_file():
            parser.error(f"文件不存在：{path}")
    try:
        roots = prepare_dependencies()
    except Exception as error:
        parser.exit(1, f"依赖准备失败：{error}\n首次运行需要连接 npm；下载完成后可离线使用。\n")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, body, kind, code=200):
            if isinstance(body, str):
                body = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def send_file(self, path, download=False):
            size = path.stat().st_size
            start, end, partial = 0, size - 1, False
            requested = self.headers.get("Range")
            if requested and not download:
                try:
                    unit, span = requested.split("=", 1)
                    first, last = span.split("-", 1)
                    if unit != "bytes" or "," in span:
                        raise ValueError()
                    if first:
                        start = int(first)
                        end = min(int(last), size - 1) if last else size - 1
                    else:
                        length = int(last)
                        if length <= 0:
                            raise ValueError()
                        start = max(0, size - length)
                    if not 0 <= start <= end < size:
                        raise ValueError()
                    partial = True
                except ValueError:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
            kind = {".md": "text/plain; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript"}.get(path.suffix, mimetypes.guess_type(path)[0] or "application/octet-stream")
            self.send_response(206 if partial else 200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(max(0, end - start + 1)))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("X-Content-Type-Options", "nosniff")
            if partial:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            if download:
                self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + quote(path.name))
            self.end_headers()
            try:
                with path.open("rb") as source:
                    source.seek(start)
                    remaining = end - start + 1
                    while remaining > 0:
                        chunk = source.read(min(65536, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            route = unquote(urlsplit(self.path).path)
            if route == "/favicon.ico":
                return self.send(b"", "image/x-icon", 204)
            if route in ("/", "/mermaid"):
                return self.send(page, "text/html; charset=utf-8")
            if details and route in ("/build/canvas.js", "/build/canvas.css"):
                return self.send_file(details_dir / route[1:])
            if details and route == "/details":
                return self.send(json.dumps(details, ensure_ascii=False), "application/json; charset=utf-8")
            if details and route in ("/details.css", "/details.js", "/image-stack.js"):
                return self.send_file(details_dir / route[1:])
            if details and route.startswith(("/artifact/", "/download/")):
                parts = route.split("/", 3)
                path = asset_paths.get(parts[2])
                if path and route.startswith("/artifact/") and len(parts) == 4:
                    root = path.parent
                    path = (root / parts[3]).resolve()
                    if not path.is_relative_to(root):
                        return self.send("Not found", "text/plain", 404)
                if path and path.is_file():
                    return self.send_file(path, route.startswith("/download/"))
            if details and material_root and route.startswith("/materials/"):
                path = (material_root / route.removeprefix("/materials/")).resolve()
                if path.is_relative_to(material_root) and path.is_file():
                    return self.send_file(path)
            if route == "/files":
                return self.send(json.dumps([{"id":i,"name":p.name} for i,p in enumerate(files)]), "application/json")
            if route.startswith("/source/"):
                try:
                    index = int(route.removeprefix("/source/"))
                    if not 0 <= index < len(files):
                        raise ValueError("无效文件编号")
                    path = files[index]
                    return self.send(json.dumps({"name":path.name,"code":path.read_text(encoding="utf-8-sig")}), "application/json")
                except (ValueError, IndexError, OSError) as error:
                    return self.send(str(error), "text/plain; charset=utf-8", 404)
            if route.startswith("/vendor/"):
                parts = route.split("/", 3)
                if len(parts) == 4 and parts[2] in roots:
                    root = roots[parts[2]].resolve()
                    path = (root / parts[3]).resolve()
                    if path.is_relative_to(root) and path.is_file():
                        kind = "text/javascript" if path.suffix in (".mjs", ".js") else mimetypes.guess_type(path)[0] or "application/octet-stream"
                        return self.send(path.read_bytes(), kind)
            self.send("Not found", "text/plain", 404)

    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as error:
        parser.exit(1, f"无法启动：{error}；可通过 --port 0 自动选择空闲端口。\n")
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"预览地址：{url}\n文件只读；修改源文件后点击「重读文件」。Ctrl+C 退出。", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
