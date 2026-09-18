import { createHash } from "node:crypto";
import { access, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { lessons } from "./course.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");
const articles = resolve(root, "..");
const errors = [];
let manifest;
try { manifest = JSON.parse(await readFile(join(dist, "manifest.json"), "utf8")); } catch { errors.push("dist/manifest.json 缺失或无效，请先运行 pnpm build"); }
if (manifest && manifest.lessons.length !== lessons.length) errors.push(`构建页数应为 ${lessons.length}，实际为 ${manifest.lessons.length}`);

for (const item of manifest?.lessons || []) {
  const lessonIndex = lessons.findIndex((lesson) => lesson.source === item.source);
  const source = await readFile(join(articles, item.source), "utf8");
  const actualHash = createHash("sha256").update(source).digest("hex");
  if (actualHash !== item.hash) errors.push(`${item.source} 在构建后有变更`);
  const html = await readFile(join(dist, item.output), "utf8");
  if (!html.includes(`content="${actualHash}"`)) errors.push(`${item.output} 未对应当前 Markdown`);
  const idList = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => decodeURIComponent(m[1]));
  const ids = new Set(idList);
  if (ids.size !== idList.length) errors.push(`${item.output} 存在重复 id`);
  const activePages = [...html.matchAll(/<a href="([^"]+)" class="active" aria-current="page">/g)].map((m) => decodeURIComponent(m[1]));
  if (activePages.length !== 1 || activePages[0] !== item.output) errors.push(`${item.output} 的当前篇导航状态不正确`);
  for (const lesson of lessons) if (!html.includes(`href="${encodeURI(lesson.output)}"`)) errors.push(`${item.output} 的课程目录缺少 ${lesson.output}`);
  const previous = lessons[lessonIndex - 1];
  const next = lessons[lessonIndex + 1];
  const previousRef = html.match(/rel="prev" href="([^"]+)"/)?.[1];
  const nextRef = html.match(/rel="next" href="([^"]+)"/)?.[1];
  if ((previousRef && decodeURIComponent(previousRef)) !== previous?.output || (!previousRef) !== (!previous)) errors.push(`${item.output} 的上一篇链接不正确`);
  if ((nextRef && decodeURIComponent(nextRef)) !== next?.output || (!nextRef) !== (!next)) errors.push(`${item.output} 的下一篇链接不正确`);
  const refs = [...html.matchAll(/(?:href|src)="([^"]+)"/g)].map((m) => m[1]);
  for (const ref of refs) {
    if (/^(?:[a-z]+:|\/\/)/i.test(ref)) continue;
    const [pathPart, fragment] = ref.split("#");
    if (!pathPart && !fragment) continue;
    if (!pathPart && fragment && !ids.has(decodeURIComponent(fragment))) errors.push(`${item.output} 缺少锚点 #${fragment}`);
    if (!pathPart) continue;
    const target = join(dist, decodeURIComponent(pathPart.split(/[?#]/)[0]));
    try { await access(target); } catch { errors.push(`${item.output} 的链接目标不存在：${ref}`); continue; }
    if (fragment && pathPart.endsWith(".html")) {
      const targetHtml = await readFile(target, "utf8");
      const targetIds = new Set([...targetHtml.matchAll(/\sid="([^"]+)"/g)].map((m) => decodeURIComponent(m[1])));
      if (!targetIds.has(decodeURIComponent(fragment))) errors.push(`${item.output} 的跨页锚点不存在：${ref}`);
    }
  }
  const tocTargets = [...html.matchAll(/data-section="([^"]+)"/g)].map((m) => m[1]);
  for (const id of tocTargets) if (!ids.has(id)) errors.push(`${item.output} 的目录锚点不存在：#${id}`);
}
try {
  const deckHtml = await readFile(join(dist, "index.html"), "utf8");
  const slideCount = (deckHtml.match(/\sdata-slide(?:\s|>)/g) || []).length;
  if (slideCount !== 18) errors.push(`课程演示应有 18 页，实际为 ${slideCount} 页`);
  const videoCount = (deckHtml.match(/<video\b/g) || []).length;
  if (videoCount !== 2) errors.push(`课程演示应有 2 个独立视频页，实际检测到 ${videoCount} 个 video`);

  for (const required of ["assets/presentation.css", "assets/presentation.js", "presentation.html"]) {
    try { await access(join(dist, required)); }
    catch { errors.push(`课程演示缺少 ${required}`); }
  }

  const deckRefs = [...deckHtml.matchAll(/(?:href|src)="([^"]+)"/g)].map((match) => match[1]);
  for (const ref of deckRefs) {
    if (/^(?:[a-z]+:|\/\/|#)/i.test(ref) || ref.startsWith("media/")) continue;
    const pathPart = decodeURIComponent(ref.split(/[?#]/)[0]);
    if (!/\.(?:html|css|js|svg|png|jpe?g)$/i.test(pathPart)) continue;
    try { await access(join(dist, pathPart)); }
    catch { errors.push(`课程演示引用不存在：${ref}`); }
  }
} catch {
  errors.push("课程演示 index.html 缺失或无法读取");
}

if (errors.length) { console.error(`检查失败（${errors.length} 项）：\n${errors.map((x) => `- ${x}`).join("\n")}`); process.exit(1); }
console.log(`检查通过：${lessons.length} 篇 Markdown 与 HTML 一致，页面、锚点、图片和内部链接均有效。`);
