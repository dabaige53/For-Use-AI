import { readFile, writeFile, mkdir, copyFile, stat, readdir } from 'node:fs/promises';
import { dirname, join, resolve, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

// Companion to the article build. Never changes Course articles or source media.
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const course = resolve(root, '..');
const source = join(course, '06-行动选择与投入控制/素材/七页演示内容.json');
const presentation = join(root, 'presentation');
const dist = join(root, 'dist');
const dataText = await readFile(source, 'utf8');
const raw = JSON.parse(dataText).tasks;
if (!Array.isArray(raw) || raw.length !== 45 || new Set(raw.map(t => t.id)).size !== 45) {
  throw new Error('Expected 45 unique Course tasks. Review the presentation copy if the source count changes.');
}
const tasks = raw.map(({ id, text, investment, alignment, reason, cat }) => {
  if (!Number.isInteger(id) || typeof text !== 'string' || typeof reason !== 'string' ||
      ![investment, alignment].every(x => Number.isFinite(x) && x >= 0 && x <= 100) ||
      !Number.isInteger(cat) || cat < 0 || cat > 5) throw new Error(`Invalid Course task: ${id}`);
  return { id, text, investment, alignment, reason, cat };
});
const [template, css, js] = await Promise.all(['deck.html', 'deck.css', 'deck.js'].map(name => readFile(join(presentation, name), 'utf8')));
function replaceOnce(text, marker, value) {
  if (text.split(marker).length !== 2) throw new Error(`Expected exactly one template marker: ${marker}`);
  return text.replace(marker, () => value);
}
const json = value => JSON.stringify(value).replace(/</g, '\\u003c');
let html = replaceOnce(template, '<!-- PRESENTATION_STYLE -->', `<style>\n${css}</style>`);
html = replaceOnce(html, '<!-- PRESENTATION_SCRIPT -->', `<script>\n${js}</script>`);
html = replaceOnce(html, '__COURSE_TASKS__', json(tasks));
await mkdir(join(dist, 'media'), { recursive: true });
const exists = async p => { try { return (await stat(p)).isFile(); } catch (e) { if (e.code === 'ENOENT') return false; throw e; } };
const llmDefault = join(course, '02-AI的能力从哪里来/大语言模型简要说明/生成/mini-llm-zh-480p-0000-0659.mp4');
const ioRoot = join(course, '03-信息输入与工具执行/AI的输入与输出/生成');
async function ioCandidates() {
  let dirs;
  try { dirs = await readdir(ioRoot, { withFileTypes: true }); }
  catch (e) { if (e.code === 'ENOENT') return []; throw e; }
  const paths = [];
  // Only the documented full-length preview outputs, never individual scene clips.
  for (const dir of dirs.filter(d => d.isDirectory())) {
    for (const quality of ['1080p', '480p']) {
      const path = join(ioRoot, dir.name, `AI_IO_${quality}_silent.mp4`);
      if (await exists(path)) paths.push(path);
    }
  }
  return paths;
}
const candidates = process.env.COURSE_IO_VIDEO ? [] : await ioCandidates();
const media = { llm: 'media/llm.mp4', io: 'media/io.mp4' };
const mediaStatus = {};
for (const [key, setting, defaultPath] of [
  ['llm', 'COURSE_LLM_VIDEO', llmDefault],
  ['io', 'COURSE_IO_VIDEO', candidates.length === 1 ? candidates[0] : null]
]) {
  const override = process.env[setting];
  const path = override ? resolve(course, override) : defaultPath;
  if (override && !(await exists(path))) throw new Error(`${setting}: file does not exist: ${path}`);
  if (path && await exists(path)) {
    const ext = extname(path).toLowerCase();
    if (!['.mp4', '.webm', '.m4v'].includes(ext)) throw new Error(`${setting}: use a browser-compatible MP4 or WebM file`);
    media[key] = `media/${key}${ext}`;
    await copyFile(path, join(dist, media[key]));
    mediaStatus[key] = override ? 'explicit-local-file' : 'documented-preview-output';
    console.log(`[slides] ${key}: copied ${path}`);
    if (!override) console.log('[slides] Automatically found a preview, not a verified narrated final.');
  } else {
    mediaStatus[key] = key === 'io' && candidates.length > 1 ? 'multiple-previews-use-picker' : 'missing-use-picker';
    console.log(`[slides] ${key}: ${mediaStatus[key]}. Set ${setting} or choose a local file in the slide.`);
  }
}
html = replaceOnce(html, '{"llm":"media/llm.mp4","io":"media/io.mp4"}', json(media));
await writeFile(join(dist, 'slides.html'), html);
await writeFile(join(dist, 'slides-sources.json'), JSON.stringify({
  tasks: '06-行动选择与投入控制/素材/七页演示内容.json',
  taskCount: tasks.length,
  taskSourceSha256: createHash('sha256').update(dataText).digest('hex'),
  terrainCore: '04-需求表达与反馈闭环/交互/思维地形.html',
  terrainSourceBlob: '4085e70d5df13dacf95589aa16752e53644f822a',
  mediaStatus,
  note: 'Slides do not claim source videos or teaching examples were executed as real-world tasks.'
}, null, 2) + '\n');
console.log(`[slides] Built ${join(dist, 'slides.html')} (10 slides; ${tasks.length} source tasks).`);
