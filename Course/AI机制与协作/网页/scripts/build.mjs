import { createHash } from "node:crypto";
import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import MarkdownIt from "markdown-it";
import { lessons, slugify } from "./course.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const course = resolve(root, "..");
const articlesDir = course;

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
  for (const folder of ["配图", "案例"]) {
    try { await cp(join(course, lesson.slug, folder), join(dist, lesson.slug, folder), { recursive: true }); }
    catch (error) { if (error.code !== "ENOENT") throw error; }
  }
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
      return fallback(tokens, idx, options, env, self);
    };
  }
  const body = md.render(item.markdown);
  return { body, headings };
}

for (const item of sources) {
  const { body, headings } = renderArticle(item);
  const lessonNav = sources.map((entry) => `<a href="${encodeURI(entry.output)}"${entry.output === item.output ? ' class="active" aria-current="page"' : ""}><span>${String(entry.index + 1).padStart(2, "0")}</span>${escapeHtml(entry.title)}</a>`).join("\n");
  const toc = headings.length ? headings.map((h) => `<a href="#${encodeURIComponent(h.id)}" class="level-${h.level}" data-section="${escapeHtml(h.id)}">${escapeHtml(h.text)}</a>`).join("\n") : '<p class="toc-empty">本篇没有小节</p>';
  const previous = sources[item.index - 1];
  const next = sources[item.index + 1];
  const pager = `<nav class="pager" aria-label="文章翻页">${previous ? `<a rel="prev" href="${encodeURI(previous.output)}">← 上一篇<span>${escapeHtml(previous.title)}</span></a>` : "<span></span>"}${next ? `<a rel="next" href="${encodeURI(next.output)}">下一篇 →<span>${escapeHtml(next.title)}</span></a>` : ""}</nav>`;
  const html = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="source-sha256" content="${item.hash}"><title>${escapeHtml(item.title)}｜AI 机制与协作</title>
<link rel="stylesheet" href="assets/site.css"></head><body>
<header class="mobile-header"><button type="button" data-menu aria-label="打开课程目录">☰</button><span>AI 机制与协作</span><button type="button" data-toc aria-label="打开本篇目录">本篇</button></header>
<div class="scrim" data-close></div><div class="layout">
<aside class="course-nav"><div class="brand"><strong>AI 机制与协作</strong><small>图文课程 · 共 7 篇</small></div><nav aria-label="课程目录">${lessonNav}</nav></aside>
<main><details class="mobile-toc"><summary>本篇目录</summary><nav aria-label="本篇目录">${toc}</nav></details><article>${body}</article>${pager}</main>
<aside class="page-toc"><div><strong>本篇目录</strong><button type="button" data-toc-collapse aria-expanded="true">收起</button></div><nav aria-label="本篇目录">${toc}</nav></aside>
</div><dialog class="lightbox"><button type="button" aria-label="关闭大图">×</button><img alt=""></dialog>
<script src="assets/site.js" defer></script></body></html>`;
  await writeFile(join(dist, item.output), html);
}
await writeFile(join(dist, "index.html"), `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=${encodeURI(sources[0].output)}"><link rel="canonical" href="${encodeURI(sources[0].output)}"></head><body><a href="${encodeURI(sources[0].output)}">打开第一篇</a></body></html>`);
await writeFile(join(dist, "manifest.json"), JSON.stringify({ lessons: sources.map(({ source, output, title, hash }) => ({ source, output, title, hash })) }, null, 2) + "\n");
console.log(`已构建 ${sources.length} 篇文章到 ${relative(process.cwd(), dist) || "dist"}`);
