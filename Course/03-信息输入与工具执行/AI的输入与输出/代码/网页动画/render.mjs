#!/usr/bin/env node
/* Frame-by-frame export of index.html (?render) to MP4.
 *
 *   node render.mjs --check                 load the page, verify fonts and a few frames
 *   node render.mjs --stills 3.2,47.5 --dir out/   write PNG stills at the given seconds
 *   node render.mjs                         full render (4770 frames) + narration + subtitles
 *   node render.mjs --from 40 --to 60       render a time range (video only, for review)
 *
 * Options: --out <mp4>  --workers <n>  --crf <n>  --no-ppt-clips
 * Needs Node 18+, Playwright with Chromium, and ffmpeg/ffprobe on PATH.
 * All paths are relative to this file; nothing is fetched from the network.
 */
import { createRequire } from 'node:module';
import { execFileSync, spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const LESSON = path.resolve(HERE, '..', '..');
const VOICE = path.join(LESSON, '生成', '配音');
const OUT_DIR = path.join(LESSON, '生成', '网页动画');
const PAGE = pathToFileURL(path.join(HERE, 'index.html')).href + '?render';
const PPT_CLIPS = [
  ['video-io-1.mp4', 0, 64],
  ['video-io-2.mp4', 64, 159],
];

function args() {
  const a = process.argv.slice(2);
  const o = { workers: Math.max(1, Math.min(4, os.cpus().length - 1)), crf: 16, pptClips: true };
  for (let i = 0; i < a.length; i++) {
    const k = a[i];
    const v = () => a[++i];
    if (k === '--check') o.check = true;
    else if (k === '--stills') o.stills = v().split(',').map(Number);
    else if (k === '--dir') o.dir = path.resolve(v());
    else if (k === '--out') o.out = path.resolve(v());
    else if (k === '--workers') o.workers = Math.max(1, parseInt(v(), 10));
    else if (k === '--crf') o.crf = parseInt(v(), 10);
    else if (k === '--from') o.from = parseFloat(v());
    else if (k === '--to') o.to = parseFloat(v());
    else if (k === '--no-ppt-clips') o.pptClips = false;
    else if (k === '--help' || k === '-h') o.help = true;
    else throw new Error(`unknown option ${k}`);
  }
  return o;
}

function loadPlaywright() {
  const require = createRequire(import.meta.url);
  try {
    return require('playwright');
  } catch (e) {
    const root = execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim();
    return require(path.join(root, 'playwright'));
  }
}

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  await page.goto(PAGE);
  await page.waitForFunction(() => window.AIIO && window.AIIO.ready, null, { timeout: 30000 });
  await page.evaluate(() => window.AIIO.ready);
  return { page, errors };
}

const frameBuffer = async (page, i) => {
  const url = await page.evaluate((n) => window.AIIO.frameDataURL(n), i);
  return Buffer.from(url.slice(url.indexOf(',') + 1), 'base64');
};

function ffmpeg(argv, opts = {}) {
  return spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', ...argv], { stdio: [opts.stdin ? 'pipe' : 'ignore', 'inherit', 'inherit'] });
}
const waitExit = (proc) => new Promise((res, rej) => proc.on('exit', (c) => (c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}`)))));

async function renderRange(browser, first, last, file, crf, label) {
  const { page, errors } = await openPage(browser);
  const enc = ffmpeg(['-y', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', String(crf),
    '-pix_fmt', 'yuv420p', '-g', '30', '-keyint_min', '30', '-sc_threshold', '0', '-tune', 'animation', file], { stdin: true });
  const done = waitExit(enc);
  const t0 = Date.now();
  for (let i = first; i < last; i++) {
    const buf = await frameBuffer(page, i);
    if (!enc.stdin.write(buf)) await new Promise((r) => enc.stdin.once('drain', r));
    if ((i - first) % 150 === 0) {
      const rate = (i - first + 1) / ((Date.now() - t0) / 1000);
      process.stdout.write(`  [${label}] frame ${i}/${last - 1}  ${rate.toFixed(1)} fps\n`);
    }
  }
  enc.stdin.end();
  await done;
  await page.close();
  if (errors.length) throw new Error(`page errors in ${label}: ${errors.join('; ')}`);
}

function probe(file) {
  return JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', file], { encoding: 'utf8' }));
}

async function main() {
  const o = args();
  if (o.help) {
    process.stdout.write(fs.readFileSync(fileURLToPath(import.meta.url), 'utf8').split('*/')[0] + '*/\n');
    return;
  }
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch();
  try {
    if (o.check) {
      const { page, errors } = await openPage(browser);
      const info = await page.evaluate(() => {
        const A = window.AIIO;
        const n = A.frameCount;
        const sizes = [0, Math.floor(n / 2), n - 1].map((i) => A.frameDataURL(i).length);
        for (let i = 0; i < n; i++) A.renderFrame(i); // every frame: catches missing glyphs and runtime errors
        return { frames: n, fonts: Object.keys(A.fonts), missing: [...A.missingGlyphs], sizes, chapters: A.chapters.length };
      });
      await page.close();
      process.stdout.write(JSON.stringify(info, null, 1) + '\n');
      if (errors.length || info.missing.length) throw new Error(`check failed: ${errors.join('; ')} missing=${info.missing.join('')}`);
      process.stdout.write('check passed\n');
      return;
    }
    if (o.stills) {
      const dir = o.dir || path.join(OUT_DIR, 'stills');
      fs.mkdirSync(dir, { recursive: true });
      const { page, errors } = await openPage(browser);
      for (const s of o.stills) {
        const buf = await frameBuffer(page, Math.round(s * 30));
        const name = path.join(dir, `t${s.toFixed(2).padStart(6, '0')}.png`);
        fs.writeFileSync(name, buf);
      }
      await page.close();
      if (errors.length) throw new Error(errors.join('; '));
      process.stdout.write(`wrote ${o.stills.length} stills to ${dir}\n`);
      return;
    }

    // full or partial render
    const total = await (async () => {
      const { page } = await openPage(browser);
      const n = await page.evaluate(() => window.AIIO.frameCount);
      await page.close();
      return n;
    })();
    const first = o.from != null ? Math.round(o.from * 30) : 0;
    const last = o.to != null ? Math.min(total, Math.round(o.to * 30)) : total;
    const partial = first !== 0 || last !== total;
    fs.mkdirSync(OUT_DIR, { recursive: true });
    const out = o.out || path.join(OUT_DIR, partial ? `预览-${o.from || 0}-${o.to || 159}.mp4` : 'AI的输入与输出-网页动画.mp4');
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'aiio-'));
    // split on whole seconds so every segment starts on a global keyframe
    const span = last - first;
    const per = Math.ceil(span / o.workers / 30) * 30;
    const jobs = [];
    for (let k = 0; k < o.workers; k++) {
      const a = first + k * per, b = Math.min(last, a + per);
      if (a < b) jobs.push([a, b, path.join(tmp, `seg${k}.mp4`)]);
    }
    const t0 = Date.now();
    process.stdout.write(`rendering frames ${first}-${last - 1} with ${jobs.length} workers\n`);
    await Promise.all(jobs.map(([a, b, f], k) => renderRange(browser, a, b, f, o.crf, `w${k}`)));
    const list = path.join(tmp, 'list.txt');
    fs.writeFileSync(list, jobs.map(([, , f]) => `file '${f}'\n`).join(''));
    const video = partial ? out : path.join(tmp, 'video.mp4');
    await waitExit(ffmpeg(['-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', video]));
    if (!partial) {
      await waitExit(ffmpeg(['-y', '-i', video, '-i', path.join(VOICE, '旁白.wav'), '-i', path.join(VOICE, '字幕.srt'),
        '-map', '0:v', '-map', '1:a', '-map', '2:s', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        '-c:s', 'mov_text', '-metadata:s:s:0', 'language=chi', '-metadata:s:s:0', 'title=中文',
        '-movflags', '+faststart', out]));
      if (o.pptClips) {
        for (const [name, a, b] of PPT_CLIPS) {
          // segments start on whole seconds, so every cut point is a keyframe; -frames:v keeps the cut frame-exact
          await waitExit(ffmpeg(['-y', '-ss', String(a), '-i', out, '-t', String(b - a), '-frames:v', String((b - a) * 30),
            '-map', '0:v', '-map', '0:a', '-c', 'copy', '-avoid_negative_ts', 'make_zero', '-movflags', '+faststart', path.join(OUT_DIR, name)]));
        }
      }
      await waitExit(ffmpeg(['-xerror', '-i', out, '-f', 'null', '-']));
      const media = probe(out);
      const v = media.streams.find((s) => s.codec_type === 'video');
      const report = {
        kind: 'html-canvas-frame-render',
        page: 'AI的输入与输出/代码/网页动画/index.html',
        output: path.relative(LESSON, out),
        frames: Number(v.nb_frames), fps: v.avg_frame_rate, size: [v.width, v.height],
        duration: Number(media.format.duration),
        streams: media.streams.map((s) => s.codec_type + ':' + s.codec_name),
        decode: 'passed',
        sha256: createHash('sha256').update(fs.readFileSync(out)).digest('hex'),
        ppt_clips: o.pptClips ? PPT_CLIPS.map(([n, a, b]) => ({ file: n, start: a, end: b })) : [],
        render_seconds: Math.round((Date.now() - t0) / 1000),
      };
      fs.writeFileSync(path.join(OUT_DIR, 'verification.json'), JSON.stringify(report, null, 2) + '\n');
      process.stdout.write(JSON.stringify(report, null, 2) + '\n');
    }
    fs.rmSync(tmp, { recursive: true, force: true });
    process.stdout.write(`done: ${out}\n`);
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  process.stderr.write(String(e && e.stack ? e.stack : e) + '\n');
  process.exit(1);
});
