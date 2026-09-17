import { chromium } from '/Users/w/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const HTML_PATH = 'file:///Users/w/code/For-Use-AI/Course/AI机制与协作/06-行动与投入/配图/06-seven-slides.html';
const OUT_DIR = '/Users/w/code/For-Use-AI/Course/AI机制与协作/06-行动与投入/配图';

const browser = await chromium.launch({
  executablePath: '/Users/w/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell'
});

const page = await browser.newPage({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1
});

await page.goto(HTML_PATH, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(500);
await page.mouse.move(1919, 1079);

// 隐藏底部播放控件，保证纯净截图
await page.evaluate(() => {
  const controls = document.querySelector('.controls');
  if (controls) controls.style.visibility = 'hidden';
});

const slideConfigs = [
  { index: 0, file: '06-slide-01-article.png', expectedSteps: 0, finalStep: 0 },
  { index: 1, file: '06-slide-02-article.png', expectedSteps: 3, finalStep: 2 },
  { index: 2, file: '06-slide-03-article.png', expectedSteps: 0, finalStep: 0 },
  { index: 3, file: '06-slide-04-article.png', expectedSteps: 0, finalStep: 0 },
  { index: 4, file: '06-slide-05-article.png', expectedSteps: 0, finalStep: 0 },
  { index: 5, file: '06-slide-06-article.png', expectedSteps: 0, finalStep: 0 },
  { index: 6, file: '06-slide-07-article.png', expectedSteps: 4, finalStep: 3 }
];

for (const cfg of slideConfigs) {
  const targetPath = join(OUT_DIR, cfg.file);
  await page.evaluate(({ idx, step }) => {
    window.show(idx, step);
  }, { idx: cfg.index, step: cfg.finalStep });

  // 等待过渡与布局稳定
  await page.waitForTimeout(1200);

  const state = await page.evaluate(() => ({
    page,
    step,
    heading: document.querySelector('#heading')?.textContent,
    panelText: document.querySelector('#panel')?.textContent.trim(),
    prevStepDisabled: document.querySelector('#prevStep')?.disabled,
    nextStepDisabled: document.querySelector('#nextStep')?.disabled,
    playDisabled: document.querySelector('#play')?.disabled,
    replayDisabled: document.querySelector('#replay')?.disabled,
    steps: [...document.querySelectorAll('.step')].map(e => ({
      on: e.classList.contains('on'),
      opacity: getComputedStyle(e).opacity
    })),
    animations: document.getAnimations().filter(a => a.playState === 'running').length,
    stage: {
      width: document.querySelector('.stage')?.clientWidth,
      height: document.querySelector('.stage')?.clientHeight
    }
  }));

  assert.equal(state.page, cfg.index, `Page mismatch on slide ${cfg.index + 1}`);
  assert.equal(state.steps.length, cfg.expectedSteps, `Steps length mismatch on slide ${cfg.index + 1}`);
  if (cfg.expectedSteps > 0) {
    assert.ok(
      state.steps.every(s => s.on && s.opacity === '1'),
      `Not all steps on or opacity 1 on slide ${cfg.index + 1}`
    );
  }
  if (cfg.index >= 2 && cfg.index <= 5) {
    assert.equal(state.panelText, '', `Slide ${cfg.index + 1} has right-side text!`);
    assert.equal(state.prevStepDisabled, true, `Slide ${cfg.index + 1} prevStep should be disabled`);
    assert.equal(state.nextStepDisabled, true, `Slide ${cfg.index + 1} nextStep should be disabled`);
    assert.equal(state.playDisabled, true, `Slide ${cfg.index + 1} play should be disabled`);
    assert.equal(state.replayDisabled, true, `Slide ${cfg.index + 1} replay should be disabled`);
  }
  assert.equal(state.animations, 0, `Animations still running on slide ${cfg.index + 1}`);
  assert.deepEqual(state.stage, { width: 1920, height: 1080 });

  const firstShot = await page.screenshot();
  await page.waitForTimeout(500);
  const secondShot = await page.screenshot();
  assert.ok(firstShot.equals(secondShot), `Slide ${cfg.index + 1} screenshot is not stable after 500ms`);

  await writeFile(targetPath, secondShot);
  console.log(`Saved slide ${cfg.index + 1} (${cfg.file}) - Heading: [${state.heading}]`);
}

await browser.close();
console.log('Successfully captured all 7 slides to', OUT_DIR);
