import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, copyFile, readFile, writeFile, rm, access } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const courseSource = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
async function fixture(t) {
  const course = await mkdtemp(join(tmpdir(), 'course-slides-'));
  t.after(() => rm(course, { recursive: true, force: true }));
  for (const file of [
    '网页/scripts/build-slides.mjs',
    ...['deck.html', 'deck.css', 'deck.js'].map(name => `网页/presentation/${name}`),
    '06-行动选择与投入控制/交互/06-seven-slides.html',
  ]) {
    const target = join(course, file);
    await mkdir(dirname(target), { recursive: true });
    await copyFile(join(courseSource, file), target);
  }
  const write = async (file, data) => {
    const target = join(course, file);
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, data);
    return target;
  };
  const build = (overrides = {}) => {
    const env = { ...process.env };
    delete env.COURSE_LLM_VIDEO;
    delete env.COURSE_IO_VIDEO;
    return spawnSync(process.execPath, [join(course, '网页/scripts/build-slides.mjs')], {
      env: { ...env, ...overrides }, encoding: 'utf8', timeout: 10000,
    });
  };
  const media = async () => {
    const html = await readFile(join(course, '网页/dist/slides.html'), 'utf8');
    return JSON.parse(html.match(/<script[^>]*id="course-media"[^>]*>([^<]*)<\/script>/)[1]);
  };
  return { course, write, build, media };
}

test('rebuilding without previews removes old generated videos and disables their URLs', async t => {
  const f = await fixture(t);
  const llm = await f.write('input/llm.mp4', 'llm fixture bytes');
  const io = await f.write('input/io.mp4', 'io fixture bytes');
  assert.equal(f.build({ COURSE_LLM_VIDEO: llm, COURSE_IO_VIDEO: io }).status, 0);
  assert.deepEqual(await f.media(), { llm: 'media/llm.mp4', io: 'media/io.mp4' });
  assert.equal(f.build().status, 0);
  assert.deepEqual(await f.media(), { llm: null, io: null });
  for (const name of ['llm.mp4', 'io.mp4']) {
    await assert.rejects(access(join(f.course, '网页/dist/media', name)), { code: 'ENOENT' });
  }
  const sources = JSON.parse(await readFile(join(f.course, '网页/dist/slides-sources.json')));
  assert.equal(sources.taskCount, 45);
  assert.deepEqual(sources.mediaStatus, { llm: 'missing-use-picker', io: 'missing-use-picker' });
});

test('ambiguous IO previews do not retain an earlier video or delete unrelated media', async t => {
  const f = await fixture(t);
  const io = await f.write('input/io.mp4', 'previous selection');
  assert.equal(f.build({ COURSE_IO_VIDEO: io }).status, 0);
  const untouched = await f.write('网页/dist/media/notes.txt', 'keep me');
  const previews = '03-信息输入与工具执行/AI的输入与输出/生成';
  await f.write(`${previews}/one/AI_IO_480p_silent.mp4`, 'first candidate');
  await f.write(`${previews}/two/AI_IO_1080p_silent.mp4`, 'second candidate');
  assert.equal(f.build().status, 0);
  assert.equal((await f.media()).io, null);
  await assert.rejects(access(join(f.course, '网页/dist/media/io.mp4')), { code: 'ENOENT' });
  assert.equal(await readFile(untouched, 'utf8'), 'keep me');
  const sources = JSON.parse(await readFile(join(f.course, '网页/dist/slides-sources.json')));
  assert.equal(sources.mediaStatus.io, 'multiple-previews-use-picker');
});

test('invalid explicit input leaves the previous successful build intact', async t => {
  const f = await fixture(t);
  const llm = await f.write('input/llm.mp4', 'original video');
  assert.equal(f.build({ COURSE_LLM_VIDEO: llm }).status, 0);
  const output = join(f.course, '网页/dist/slides.html');
  const before = await readFile(output, 'utf8');
  const result = f.build({ COURSE_IO_VIDEO: join(f.course, 'missing.mp4') });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /COURSE_IO_VIDEO: file does not exist/);
  assert.equal(await readFile(output, 'utf8'), before);
  assert.equal(await readFile(join(f.course, '网页/dist/media/llm.mp4'), 'utf8'), 'original video');
});

test('format changes replace owned variants and can safely reuse a generated input', async t => {
  const f = await fixture(t);
  const mp4 = await f.write('input/llm.mp4', 'old format');
  assert.equal(f.build({ COURSE_LLM_VIDEO: mp4 }).status, 0);
  const webm = await f.write('input/llm.webm', 'new format');
  assert.equal(f.build({ COURSE_LLM_VIDEO: webm }).status, 0);
  const output = join(f.course, '网页/dist/media/llm.webm');
  await assert.rejects(access(join(f.course, '网页/dist/media/llm.mp4')), { code: 'ENOENT' });
  assert.equal((await f.media()).llm, 'media/llm.webm');
  assert.equal(f.build({ COURSE_LLM_VIDEO: output }).status, 0);
  assert.equal(await readFile(output, 'utf8'), 'new format');
});
