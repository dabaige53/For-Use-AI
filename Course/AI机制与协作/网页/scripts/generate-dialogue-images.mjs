import { createCanvas, GlobalFonts } from '@napi-rs/canvas';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WIDTH = 1400;
const BODY_SIZE = 32;
const LINE_HEIGHT = 52;
const CARD_X = 64;
const CARD_WIDTH = WIDTH - CARD_X * 2;
const CARD_Y = 44;
const CARD_PADDING_TOP = 48;
const CARD_PADDING_BOTTOM = 48;
const CARD_PADDING_LEFT = 48;
const CARD_PADDING_RIGHT = 64;
const MARKER_COLUMN = 52;
const TURN_GAP = 16;
const RADIUS = 26;
const LINE_START_PUNCTUATION = new Set([
  '，', '。', '！', '？', '：', '；', '、', '）', '】', '》', '」', '』', '〕', '］', '〉', '”', '’', '…',
  ',', '.', '!', '?', ':', ';', ')', ']', '}', '>', '%', '‰', '"', "'",
]);

const scriptDir = dirname(fileURLToPath(import.meta.url));
const courseDir = resolve(scriptDir, '../..');
const chapterDir = join(courseDir, '04-表达需求与反馈');
const defaultInput = join(chapterDir, '案例', '对话.json');
const defaultOutput = join(chapterDir, '配图');

const usage = `用法：
  node scripts/generate-dialogue-images.mjs [--input 文件] [--output 目录]

选项：
  --input   对话 JSON，默认 ../04-表达需求与反馈/案例/对话.json
  --output  PNG 和 manifest 输出目录，默认 ../04-表达需求与反馈/配图
  --help    显示帮助
`;

function fail(message) {
  throw new Error(`${message}\n\n${usage.trim()}`);
}

function parseArgs(argv) {
  // pnpm forwards a standalone `--` when arguments are passed as
  // `pnpm run dialogues:04 -- --input ...`.
  if (argv[0] === '--') argv = argv.slice(1);
  if (argv.includes('--help') || argv.includes('-h')) {
    if (argv.length !== 1) fail('--help 不能和其他参数同时使用');
    console.log(usage.trimEnd());
    return null;
  }

  let input = defaultInput;
  let output = defaultOutput;
  for (let index = 0; index < argv.length; index += 1) {
    const option = argv[index];
    if (option !== '--input' && option !== '--output') {
      fail(`未知参数：${option}`);
    }
    const value = argv[index + 1];
    if (!value || value.startsWith('--')) {
      fail(`${option} 需要一个路径参数`);
    }
    if (option === '--input') input = resolve(value);
    if (option === '--output') output = resolve(value);
    index += 1;
  }
  return { input, output };
}

function validateDocument(document, inputPath) {
  if (!document || typeof document !== 'object' || Array.isArray(document)) {
    fail(`${inputPath} 顶层必须是 JSON 对象`);
  }
  if (document.version !== 1) {
    fail(`${inputPath} 的 version 必须为 1`);
  }
  if (!Array.isArray(document.dialogues) || document.dialogues.length === 0) {
    fail(`${inputPath} 的 dialogues 必须是非空数组`);
  }

  const ids = new Set();
  return document.dialogues.map((dialogue, dialogueIndex) => {
    const prefix = `dialogues[${dialogueIndex}]`;
    if (!dialogue || typeof dialogue !== 'object' || Array.isArray(dialogue)) {
      fail(`${prefix} 必须是对象`);
    }
    if (typeof dialogue.id !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(dialogue.id)) {
      fail(`${prefix}.id 必须是安全的非空文件名片段`);
    }
    if (ids.has(dialogue.id)) fail(`${prefix}.id 重复：${dialogue.id}`);
    ids.add(dialogue.id);
    if (typeof dialogue.title !== 'string') fail(`${prefix}.title 必须是字符串`);
    if (!Array.isArray(dialogue.turns) || dialogue.turns.length === 0) {
      fail(`${prefix}.turns 必须是非空数组`);
    }

    const turns = dialogue.turns.map((turn, turnIndex) => {
      const turnPrefix = `${prefix}.turns[${turnIndex}]`;
      if (!turn || typeof turn !== 'object' || Array.isArray(turn)) {
        fail(`${turnPrefix} 必须是对象`);
      }
      if (!['human', 'ai', 'tool'].includes(turn.role)) {
        fail(`${turnPrefix}.role 必须是 human、ai 或 tool`);
      }
      if (typeof turn.text !== 'string') fail(`${turnPrefix}.text 必须是字符串`);
      const highlights = turn.highlights ?? [];
      if (!Array.isArray(highlights) || highlights.some((highlight) => typeof highlight !== 'string' || !highlight)) {
        fail(`${turnPrefix}.highlights 必须是非空字符串数组`);
      }
      for (const highlight of highlights) {
        if (!turn.text.includes(highlight)) {
          fail(`${turnPrefix}.highlights 中的文本未出现在对应 text 中：${highlight}`);
        }
      }
      return { role: turn.role, text: turn.text, highlights };
    });

    return { id: dialogue.id, title: dialogue.title, turns };
  });
}

function availableFontFamilies() {
  try {
    const families = JSON.parse(GlobalFonts.getFamilies().toString());
    return new Set(families.map(({ family }) => family));
  } catch {
    return new Set();
  }
}

function chooseFontFamily(families, fallback) {
  const available = availableFontFamilies();
  return families.find((family) => available.has(family)) ?? fallback;
}

function fontString(size, family) {
  return `${size}px "${family}"`;
}

function isAsciiWord(character) {
  return /^[A-Za-z0-9_]$/.test(character);
}

function highlightedCharacters(text, highlights) {
  // Normalize only line separator characters for layout. The original text is
  // still used for the manifest hash, so no source text is lost.
  const normalized = text.replace(/\r\n?/g, '\n');
  const characters = Array.from(normalized);
  const highlighted = new Array(characters.length).fill(false);

  for (const highlight of highlights) {
    const needle = Array.from(highlight.replace(/\r\n?/g, '\n'));
    if (needle.length === 0) continue;
    for (let start = 0; start <= characters.length - needle.length; start += 1) {
      let matches = true;
      for (let offset = 0; offset < needle.length; offset += 1) {
        if (characters[start + offset] !== needle[offset]) {
          matches = false;
          break;
        }
      }
      if (matches) {
        for (let offset = 0; offset < needle.length; offset += 1) {
          highlighted[start + offset] = true;
        }
      }
    }
  }
  return { characters, highlighted };
}

function lineSegments(characters, highlighted) {
  if (characters.length === 0) return [];
  const segments = [];
  let start = 0;
  for (let index = 1; index <= characters.length; index += 1) {
    if (index === characters.length || highlighted[index] !== highlighted[start]) {
      segments.push({ text: characters.slice(start, index).join(''), highlighted: highlighted[start] });
      start = index;
    }
  }
  return segments;
}

function wrapText(context, text, highlights, font, maxWidth) {
  context.font = font;
  const { characters, highlighted } = highlightedCharacters(text, highlights);
  const wrapped = [];
  let currentCharacters = [];
  let currentHighlighted = [];
  let currentWidth = 0;

  const pushLine = (breakAfter = null) => {
    wrapped.push({
      segments: lineSegments(currentCharacters, currentHighlighted),
      empty: currentCharacters.length === 0,
      breakAfter,
    });
    currentCharacters = [];
    currentHighlighted = [];
    currentWidth = 0;
  };

  let index = 0;
  while (index < characters.length) {
    const character = characters[index];
    if (character === '\n') {
      pushLine('explicit');
      index += 1;
      continue;
    }
    const characterWidth = context.measureText(character).width;
    if (currentCharacters.length > 0 && currentWidth + characterWidth > maxWidth) {
      const previousCharacter = currentCharacters[currentCharacters.length - 1];
      const previousWidth = context.measureText(previousCharacter).width;
      const spaceIndex = currentCharacters.findLastIndex((item) => item === ' ' || item === '\t');
      const preferWordBreak = (
        isAsciiWord(character) && isAsciiWord(previousCharacter)
      ) || (
        character === '.' && isAsciiWord(previousCharacter)
      );
      if (preferWordBreak && spaceIndex >= 0) {
        // Keep ordinary English words together when there is a visible space
        // on the current line. The space itself remains in the output.
        const carriedCharacters = currentCharacters.splice(spaceIndex + 1);
        const carriedHighlighted = currentHighlighted.splice(spaceIndex + 1);
        const carriedWidth = carriedCharacters.reduce(
          (total, item) => total + context.measureText(item).width,
          0,
        );
        pushLine('wrap');
        currentCharacters.push(...carriedCharacters);
        currentHighlighted.push(...carriedHighlighted);
        currentWidth = carriedWidth;
      } else if (
        LINE_START_PUNCTUATION.has(character)
        && previousWidth + characterWidth <= maxWidth
      ) {
        const previousHighlighted = currentHighlighted.pop();
        currentCharacters.pop();
        currentWidth -= previousWidth;
        pushLine('wrap');
        currentCharacters.push(previousCharacter);
        currentHighlighted.push(previousHighlighted);
        currentWidth += previousWidth;
      } else {
        // An overlong word/path, or a Chinese line without an ASCII word
        // boundary, falls through to a hard character break.
        pushLine('wrap');
      }
    }
    currentCharacters.push(character);
    currentHighlighted.push(highlighted[index]);
    currentWidth += characterWidth;
    index += 1;
  }
  // Keep an empty final line for an empty text or text ending in a newline.
  pushLine();
  const renderedText = wrapped
    .map((line) => `${line.segments.map((segment) => segment.text).join('')}${line.breakAfter === 'explicit' ? '\n' : ''}`)
    .join('');
  const normalizedText = text.replace(/\r\n?/g, '\n');
  if (renderedText !== normalizedText) {
    throw new Error('排版覆盖校验失败：换行后的字符与原文不一致');
  }
  return wrapped;
}

function roundedRectangle(context, x, y, width, height, radius) {
  context.beginPath();
  context.moveTo(x + radius, y);
  context.lineTo(x + width - radius, y);
  context.arcTo(x + width, y, x + width, y + radius, radius);
  context.lineTo(x + width, y + height - radius);
  context.arcTo(x + width, y + height, x + width - radius, y + height, radius);
  context.lineTo(x + radius, y + height);
  context.arcTo(x, y + height, x, y + height - radius, radius);
  context.lineTo(x, y + radius);
  context.arcTo(x, y, x + radius, y, radius);
  context.closePath();
}

function renderDialogue(dialogue, fonts) {
  const textX = CARD_X + CARD_PADDING_LEFT + MARKER_COLUMN;
  const markerX = CARD_X + CARD_PADDING_LEFT;
  const maxWidth = CARD_X + CARD_WIDTH - CARD_PADDING_RIGHT - textX;
  const blocks = dialogue.turns.map((turn) => ({
    ...turn,
    font: turn.role === 'tool' ? fonts.tool : fonts.body,
    lines: wrapText(
      fonts.measureContext,
      turn.text,
      turn.highlights,
      turn.role === 'tool' ? fonts.tool : fonts.body,
      maxWidth,
    ),
  }));
  const lineCount = blocks.reduce((total, block) => total + block.lines.length, 0);
  const height = Math.ceil(
    CARD_Y * 2
      + CARD_PADDING_TOP
      + CARD_PADDING_BOTTOM
      + lineCount * LINE_HEIGHT
      + Math.max(0, blocks.length - 1) * TURN_GAP,
  );
  const canvas = createCanvas(WIDTH, height);
  const context = canvas.getContext('2d');
  context.fillStyle = '#ffffff';
  context.fillRect(0, 0, WIDTH, height);
  roundedRectangle(context, CARD_X, CARD_Y, CARD_WIDTH, height - CARD_Y * 2, RADIUS);
  context.fillStyle = '#f7f8fa';
  context.fill();
  context.strokeStyle = '#eaecf0';
  context.lineWidth = 1;
  context.stroke();
  context.textBaseline = 'alphabetic';

  let baseline = CARD_Y + CARD_PADDING_TOP + BODY_SIZE;
  for (const block of blocks) {
    block.lines.forEach((line, lineIndex) => {
      const firstLine = lineIndex === 0;
      if (firstLine) {
        context.font = fonts.marker;
        context.fillStyle = block.role === 'human'
          ? '#111827'
          : block.role === 'ai'
            ? '#dc2626'
            : '#7c3aed';
        context.fillText(block.role === 'human' ? '>' : block.role === 'ai' ? '●' : '$', markerX, baseline);
      }

      context.font = block.font;
      let x = textX;
      for (const segment of line.segments) {
        context.fillStyle = segment.highlighted
          ? '#dc2626'
          : block.role === 'tool'
            ? '#433850'
            : '#111827';
        context.fillText(segment.text, x, baseline);
        x += context.measureText(segment.text).width;
      }
      baseline += LINE_HEIGHT;
    });
    baseline += TURN_GAP;
  }

  return { canvas, lineCount };
}

function textSha256(turns) {
  return createHash('sha256')
    .update(turns.map(({ text }) => text).join('\n'), 'utf8')
    .digest('hex');
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (!options) return;

  let document;
  try {
    document = JSON.parse(await readFile(options.input, 'utf8'));
  } catch (error) {
    fail(`无法读取或解析输入 JSON：${options.input}\n${error.message}`);
  }
  const dialogues = validateDocument(document, options.input);

  try {
    GlobalFonts.loadSystemFonts();
  } catch {
    // The canvas package still supplies generic sans/monospace fallbacks when
    // system font discovery is unavailable.
  }
  const bodyFamily = chooseFontFamily(
    ['PingFang SC', 'Hiragino Sans GB', 'Hiragino Sans', 'Heiti SC', 'Heiti TC', 'Arial Unicode MS'],
    'sans-serif',
  );
  const toolFamily = chooseFontFamily(
    ['Menlo', 'SFMono-Regular', 'DejaVu Sans Mono', 'Consolas'],
    'monospace',
  );
  const fonts = {
    body: fontString(BODY_SIZE, bodyFamily),
    tool: fontString(BODY_SIZE, toolFamily),
    marker: `700 ${BODY_SIZE}px "${bodyFamily}"`,
    measureContext: createCanvas(1, 1).getContext('2d'),
  };

  await mkdir(options.output, { recursive: true });
  const images = [];
  for (const dialogue of dialogues) {
    const { canvas, lineCount } = renderDialogue(dialogue, fonts);
    const file = `04-dialogue-${dialogue.id}.png`;
    await writeFile(join(options.output, file), canvas.toBuffer('image/png'));
    images.push({
      id: dialogue.id,
      title: dialogue.title,
      file,
      textSha256: textSha256(dialogue.turns),
      width: canvas.width,
      height: canvas.height,
      turns: dialogue.turns.length,
      turnCount: dialogue.turns.length,
      lineCount,
    });
  }

  const manifestPath = join(options.output, '04-dialogue-manifest.json');
  await writeFile(
    manifestPath,
    `${JSON.stringify({ version: 1, width: WIDTH, images }, null, 2)}\n`,
    'utf8',
  );
  console.log(`已生成 ${images.length} 张 PNG：${options.output}`);
  console.log(`manifest：${manifestPath}`);
}

main().catch((error) => {
  console.error(`错误：${error.message}`);
  process.exitCode = 1;
});
