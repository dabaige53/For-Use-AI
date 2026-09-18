import { createHash } from "node:crypto";
import { cp, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import MarkdownIt from "markdown-it";
import { icon } from "./icons.mjs";
import { lessons, slugify } from "./course.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const course = resolve(root, "..");
const articlesDir = course;
const terrainDisplay = JSON.parse(await readFile(join(course, "04-需求表达与反馈闭环/素材/gif-display.json"), "utf8"));

const dist = join(root, "dist");
const missing = [];
for (const lesson of lessons) {
  try { await readFile(join(articlesDir, lesson.source)); } catch { missing.push(lesson.source); }
}
if (missing.length) {
  console.error(`缺少 ${missing.length} 篇课程文章：\n${missing.map((x) => `- ../${x}`).join("\n")}`);
  process.exit(1);
}

await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });
await cp(join(root, "public"), dist, { recursive: true });
for (const lesson of lessons) {
  for (const folder of ["素材", "交互"]) {
    try { await cp(join(course, lesson.slug, folder), join(dist, lesson.slug, folder), { recursive: true }); }
    catch (error) { if (error.code !== "ENOENT") throw error; }
  }
}

async function findPlayableVideo(chapterDir) {
  const candidates = [];
  async function walk(dir) {
    let entries;
    try { entries = await readdir(dir, { withFileTypes: true }); } catch { return; }
    for (const entry of entries) {
      if (["node_modules", "dist", ".trash", ".git"].includes(entry.name)) continue;
      const full = join(dir, entry.name);
      if (entry.isDirectory()) await walk(full);
      else if (/\.(?:mp4|webm)$/i.test(entry.name)) candidates.push(full);
    }
  }
  await walk(chapterDir);
  const rank = (path) => {
    const name = path.toLowerCase();
    const finalScore = /(?:final|成片|有声|voice|review|preview|预览)/i.test(name) ? 0 : 1;
    const formatScore = extname(path).toLowerCase() === ".mp4" ? 0 : 1;
    return finalScore * 100000 + formatScore * 10000 + path.length;
  };
  candidates.sort((a, b) => rank(a) - rank(b) || a.localeCompare(b, "zh-CN"));
  return candidates[0] || null;
}

await mkdir(join(dist, "media"), { recursive: true });
for (const [chapter, target] of [
  ["02-AI的能力从哪里来", "video-01"],
  ["03-信息输入与工具执行", "video-02"]
]) {
  const source = await findPlayableVideo(join(course, chapter));
  if (!source) {
    console.warn(`未找到 ${chapter} 的 MP4/WebM；演示页将保留海报与视频占位。`);
    continue;
  }
  const extension = extname(source).toLowerCase();
  await cp(source, join(dist, "media", `${target}${extension}`));
  console.log(`演示视频：${relative(course, source)} → media/${target}${extension}`);
}

const sources = await Promise.all(lessons.map(async (lesson) => {
  const markdown = await readFile(join(articlesDir, lesson.source), "utf8");
  const title = markdown.match(/^#\s+(.+)$/m)?.[1].trim() || lesson.fallbackTitle;
  return { ...lesson, markdown, title, hash: createHash("sha256").update(markdown).digest("hex") };
}));

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}

function rewriteUrl(url, item) {
  if (/^(?:[a-z]+:|#|\/\/)/i.test(url)) return url;
  const [, path, suffix] = url.match(/^([^?#]*)(.*)$/s);
  const target = relative(course, resolve(course, item.slug, decodeURIComponent(path)));
  const lesson = lessons.find(entry => entry.source === target);
  return encodeURI(lesson ? lesson.output : target) + suffix;
}

function renderArticle(item) {
  const md = new MarkdownIt({ html: true, linkify: true, typographer: false });
  const headings = [];
  const used = new Map();
  const defaultHeading = md.renderer.rules.heading_open || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options));
  md.renderer.rules.heading_open = (tokens, idx, options, env, self) => {
    const level = Number(tokens[idx].tag.slice(1));
    const inline = tokens[idx + 1];
    const text = inline?.content || "";
    const id = slugify(text, used);
    tokens[idx].attrSet("id", id);
    if (level === 2 || level === 3) headings.push({ level, text, id });
    return defaultHeading(tokens, idx, options, env, self);
  };
  for (const rule of ["link_open", "image"]) {
    const fallback = md.renderer.rules[rule] || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options));
    const attr = rule === "image" ? "src" : "href";
    md.renderer.rules[rule] = (tokens, idx, options, env, self) => {
      const value = tokens[idx].attrGet(attr);
      if (value) tokens[idx].attrSet(attr, rewriteUrl(value, item));
      if (rule === "image") {
        tokens[idx].attrSet("loading", "lazy");
        tokens[idx].attrSet("tabindex", "0");
        tokens[idx].attrSet("role", "button");
      }
      const crop = rule === "image" && item.slug === "04-需求表达与反馈闭环" ? terrainDisplay[value?.split("/").pop()] : null;
      if (crop) {
        tokens[idx].attrSet("style", `width:${crop.sourceWidth / crop.width * 100}%;left:${-crop.x / crop.width * 100}%;top:${-crop.y / crop.height * 100}%`);
        return `<span class="terrain-frame" style="aspect-ratio:${crop.width}/${crop.height}">${fallback(tokens, idx, options, env, self)}</span>`;
      }
      return fallback(tokens, idx, options, env, self);
    };
  }
  const rendered = md.render(item.markdown);
  const body = rendered.replace(/(<h[23] id="([^"]+)"[^>]*>)(.*?)(<\/h[23]>)/gs, (_, open, id, title, close) => `${open}${title}<a class="heading-anchor" href="#${encodeURIComponent(id)}" data-heading-copy aria-label="复制章节链接：${escapeHtml(title.replace(/<[^>]*>/g, ""))}">${icon("link")}</a>${close}`);
  return { body, headings };
}

const searchEntries = [];
const plainText = (html) => html.replace(/<[^>]*>/g, " ").replace(/&(?:amp|lt|gt|quot|#39|nbsp);/g, (x) => ({"&amp;":"&","&lt;":"<","&gt;":">","&quot;":'"',"&#39;":"'","&nbsp;":" "}[x])).replace(/\s+/g, " ").trim();
await mkdir(join(dist, "markdown"), { recursive: true });
const lessonIcons = ["question", "brain", "flow", "chat", "check", "compass", "layers"];
for (const item of sources) {
  const { body, headings } = renderArticle(item);
  const lessonNav = sources.map((entry) => `${entry.index === 0 ? '<div class="nav-group-label">开始学习</div>' : entry.index === 1 ? '<div class="nav-group-label">理解 AI</div>' : entry.index === 3 ? '<div class="nav-group-label">协作与实践</div>' : entry.index === 6 ? '<div class="nav-group-label">课程幕后</div>' : ''}<a href="${encodeURI(entry.output)}"${entry.output === item.output ? ' class="active" aria-current="page"' : ""}><span class="lesson-label">第 ${entry.index + 1} 篇：${escapeHtml(entry.title)}</span></a>`).join("\n");
  const toc = headings.length ? headings.map((h) => `<a href="#${encodeURIComponent(h.id)}" class="level-${h.level}" data-section="${escapeHtml(h.id)}">${escapeHtml(h.text)}</a>`).join("\n") : '<p class="toc-empty">本篇没有小节</p>';
  const previous = sources[item.index - 1];
  const next = sources[item.index + 1];
  const pager = `<nav class="pager" aria-label="文章翻页">${previous ? `<a rel="prev" href="${encodeURI(previous.output)}">← 上一篇<span>${escapeHtml(previous.title)}</span></a>` : "<span></span>"}${next ? `<a rel="next" href="${encodeURI(next.output)}">下一篇 →<span>${escapeHtml(next.title)}</span></a>` : ""}</nav>`;
  const markdownPath = `markdown/${String(item.index + 1).padStart(2, "0")}.md`;
  await writeFile(join(dist, markdownPath), item.markdown);
  for (const section of body.split(/(?=<h[23]\s)/)) {
    const heading = section.match(/^<h[23] id="([^"]+)"[^>]*>(.*?)<\/h[23]>/s);
    searchEntries.push({ title: item.title, heading: heading ? plainText(heading[2]) : "开篇", url: encodeURI(item.output) + (heading ? "#" + encodeURIComponent(heading[1]) : ""), text: plainText(section) });
  }
  const html = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="source-sha256" content="${item.hash}"><title>${escapeHtml(item.title)}｜AI 机制与协作</title>
<link rel="alternate" type="text/plain" href="llms.txt" title="全站文档索引"><link rel="stylesheet" href="assets/site.css"></head><body>
<a class="skip-link" href="#reading-content">Skip to main content</a><a class="agent-index" href="llms.txt">/llms.txt</a>
<header class="site-header"><div class="header-inner">
<button class="mobile-menu icon-button" type="button" data-menu aria-label="打开课程目录">${icon("menu")}</button>
<a class="site-logo" href="${encodeURI(sources[0].output)}">${icon("gear")}<strong>AI 机制与协作</strong></a>
<button class="search-trigger" type="button" data-search-open aria-label="搜索全部课程">${icon("search")}<span>搜索全部课程…</span><kbd>⌘ K</kbd></button>
<details class="more-actions"><summary class="icon-button" aria-label="更多页面操作">${icon("more")}</summary><div class="action-popover"><a href="${markdownPath}" download>下载 Markdown</a><a href="llms.txt">文档索引</a><button type="button" data-print>打印本篇</button></div></details>
<button class="mobile-toc-button icon-button" type="button" data-toc aria-label="打开本篇目录">${icon("list")}</button>
</div></header>
<nav class="breadcrumb" aria-label="面包屑"><button class="icon-button" type="button" data-breadcrumb-menu aria-label="展开课程目录">${icon("menu")}</button><a href="${encodeURI(sources[0].output)}">开始学习</a><span aria-hidden="true">›</span><span aria-current="page">${escapeHtml(item.title)}</span></nav>
<div class="scrim" data-close></div><div class="layout">
<aside class="course-nav"><button class="nav-collapse" type="button" data-nav-collapse aria-expanded="true" aria-label="向左收起课程目录" title="向左收起课程目录">‹</button><nav aria-label="课程目录">${lessonNav}</nav></aside>
<main id="reading-content" tabindex="-1"><details class="mobile-toc"><summary>本篇目录</summary><nav aria-label="本篇目录">${toc}</nav></details><article>${body.replace(/(<h1[^>]*>.*?<\/h1>)\s*(<p>.*?<\/p>)/s, (_, title, lead) => `<header class="article-header"><span class="chapter-kicker">第 ${item.index + 1} 篇 · ${item.index < 3 ? "理解 AI" : item.index < 6 ? "协作与实践" : "课程幕后"}</span>${title}<div class="copy-controls"><button class="copy-page" type="button" data-copy-kind="markdown" data-source="${markdownPath}">${icon("copy")}<span>Copy page</span></button><details class="copy-menu"><summary aria-label="更多复制方式">${icon("down")}</summary><div class="action-popover"><button type="button" data-copy-kind="markdown" data-source="${markdownPath}">复制 Markdown</button><button type="button" data-copy-kind="text">复制纯文本</button><button type="button" data-copy-kind="link">复制页面链接</button></div></details></div><div class="article-lead">${lead}</div><span class="copy-status" role="status"></span></header>`)}</article>${item.index === 0 ? `<section class="course-grid-section" aria-label="课程学习导航"><h2>继续学习</h2><div class="knowledge-grid">${sources.slice(1).map(entry => `<a class="knowledge-card" href="${encodeURI(entry.output)}">${icon(lessonIcons[entry.index])}<h3>${escapeHtml(entry.title)}</h3><p>${["", "了解训练与生成的基本机制", "理解输入、工具与结果回流", "用案例改善需求表达与反馈", "从任务到可核验的成果", "判断下一步行动与投入", "回看课程制作与修订"][entry.index]}</p></a>`).join("")}</div></section>` : ""}${pager}<footer class="reader-footer"><span>AI 机制与协作 · 图文课程</span><a href="llms.txt">文档索引</a><a href="${markdownPath}">Markdown</a></footer></main>
<aside class="page-toc"><div><strong>${icon("list")}本篇目录</strong><button type="button" data-toc-collapse aria-expanded="true" aria-label="向右收起本篇目录" title="向右收起本篇目录">›</button></div><nav aria-label="本篇目录">${toc}</nav></aside>
</div><dialog class="lightbox"><button type="button" aria-label="关闭大图">×</button><img alt=""></dialog>
<dialog class="search-dialog" aria-label="搜索全部课程"><div class="search-input-row">${icon("search")}<input type="search" data-search-input aria-label="搜索关键词" placeholder="搜索概念、案例或正文…" autocomplete="off"><button class="icon-button" type="button" data-search-close aria-label="关闭搜索">${icon("close")}</button></div><p class="search-status" role="status">输入关键词，搜索全部七篇课程</p><div class="search-results" aria-label="搜索结果"></div><footer>↑ ↓ 选择结果 · Enter 打开 · Esc 关闭</footer></dialog>
<script type="module" src="assets/site.js"></script></body></html>`;
  await writeFile(join(dist, item.output), html);
}
await writeFile(join(dist, "llms.txt"), "# AI 机制与协作\n\n> 七篇课程，涵盖 AI 机制、需求表达、任务执行与行动选择。\n\n## 课程正文\n\n" + sources.map(item => `- [${item.title}](markdown/${String(item.index + 1).padStart(2, "0")}.md): 阅读页 ${encodeURI(item.output)}`).join("\n") + "\n");
await writeFile(join(dist, "index.html"), await readFile(join(root, "public/presentation.html"), "utf8"));
await writeFile(join(dist, "search-index.json"), JSON.stringify(searchEntries) + "\n");
await writeFile(join(dist, "manifest.json"), JSON.stringify({ lessons: sources.map(({ source, output, title, hash }) => ({ source, output, title, hash })) }, null, 2) + "\n");
console.log(`已构建 ${sources.length} 篇文章到 ${relative(process.cwd(), dist) || "dist"}`);
