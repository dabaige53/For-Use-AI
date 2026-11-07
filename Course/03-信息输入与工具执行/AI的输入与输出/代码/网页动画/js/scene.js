/* AI 的输入与输出 · 分镜
 *
 * One continuous 159 s scene.  Every element computes its own state from the
 * global time t, using the narration cue sheet below (clause onsets measured
 * on 生成/配音/旁白.wav).  Coordinates are world units (14.22 x 8, y up).
 */
(function (root) {
  'use strict';
  const A = root.AIIO;
  const { clamp, lerp, prog, kf, mix } = A;
  const R = A.rate;

  // ---------------------------------------------------------------- palette
  const C = {
    ink: '#ECECEC', soft: '#C4C9CF', dim: '#878D95', faint: '#3A3F46', edge: '#5C626A',
    panel: '#0B0E13', user: '#58A6FF', sys: '#83C167', env: '#DADDE1', tool: '#F4D35E',
    res: '#5CE1E6', prog: '#B39DFF', teal: '#5CD0B3', red: '#FC6255', yellow: '#FFFF00',
  };
  const KIND = {
    user: { color: C.user, tag: '用户消息' },
    sys: { color: C.sys, tag: '系统指令' },
    env: { color: C.env, tag: '环境信息' },
    tool: { color: C.tool, tag: '工具定义' },
    req: { color: C.tool, tag: '请求记录' },
    res: { color: C.res, tag: '工具结果' },
  };
  const ROWS = ['user', 'sys', 'env', 'tool'];

  // ---------------------------------------------------------------- narration cues (s)
  const S = {
    ask: 0.31, askText: 1.81, askTextEnd: 3.93, beyond: 4.5, organize: 5.56,
    userMsg: 8.57, sysMsg: 10.08, envMsg: 11.94, notice: 14.57, pathIn: 15.28, notYet: 16.78,
    toolDef: 21.81, canRequest: 23.27, schema: 25.11, required: 27.55, optional: 29.79, describe: 31.6, notExec: 33.1,
    four: 40.19, together: 40.89,
    putUser: 42.63, putSys: 44.97, putEnv: 46.2, putTool: 47.25, whole: 48.48, wholeEnd: 50.89,
    give: 56.3, based: 58.75, genNext: 60.08,
    genName: 64.75, genPath: 67.89, genOthers: 68.91, notRead: 70.11,
    complete: 73.22, isOutput: 75.46, receive: 78.48, identify: 79.95, branch: 80.71,
    select: 81.7, pass: 83.22, trigger: 84.23, read: 85.21, giveBack: 86.62, simulated: 88.24,
    received: 90.62, keepBoth: 92.35, pair: 95.23,
    orgNext: 97.29, keepBounds: 99.29, addReq: 101.0, addRes: 102.95,
    noNewQ: 108.95, secondCall: 110.31, kUser: 113.35, kSys: 114.01, kEnv: 115.09, kTool: 115.98, kKeep: 117.09,
    addCall: 123.21, addResult: 125.46,
    origNew: 130.21, updated: 132.08, give2: 134.1, thumb: 136.51,
    basedOn: 141.32, genAnswer: 142.89, deliver: 147.0,
    once: 152.1, twice: 153.42, resultIn: 154.98, cont: 156.62,
  };

  A.chapters = [
    { t: 0, title: '一句请求' },
    { t: 8.5, title: '用户消息、系统指令、环境信息' },
    { t: 21.7, title: '工具定义' },
    { t: 42.5, title: '首次完整输入' },
    { t: 56.1, title: '模型生成下一条消息' },
    { t: 73.0, title: '程序识别并执行' },
    { t: 90.4, title: '结果回流' },
    { t: 108.8, title: '第二次模型调用' },
    { t: 141.2, title: '生成会议纪要' },
    { t: 151.8, title: '两次调用对照' },
  ];

  // ---------------------------------------------------------------- small helpers
  const P = (t, t0, d, r) => prog(t, t0, d, r);
  const T = (content, size, color = C.ink, extra) => A.text(content, Object.assign({ size, color }, extra || {}));
  const B = (content, size, color = C.ink, extra) => A.text(content, Object.assign({ size, color, weight: 800 }, extra || {}));
  const M = (content, size, color = C.ink, extra) => A.text(content, Object.assign({ size, color, font: 'mono' }, extra || {}));
  const MONO = (color = C.ink, size = 30) => ({ font: 'mono', color, size });
  const lerpPt = (p, q, k) => [lerp(p[0], q[0], k), lerp(p[1], q[1], k)];
  const pulseScale = (t, t0, d = 0.6, amt = 0.2) => 1 + amt * A.indicate(clamp((t - t0) / d));

  /** Move along a circular arc from p to q (ManimGL path_arc). */
  const arcPos = (p, q, k, angle) => {
    if (Math.abs(angle) < 1e-3 || Math.hypot(q[0] - p[0], q[1] - p[1]) < 1e-4) return lerpPt(p, q, k);
    return A.arcBetween(p, q, angle, 24).at(k);
  };
  const arcPt = (p, q, k, angle) => {
    const a = arcPos(p, q, k, angle);
    return a.x !== undefined ? [a.x, a.y] : a;
  };

  /** Draw something inside a translated / scaled frame. */
  const at = (ctx, x, y, s, alpha, fn) => A.group(ctx, { x, y, s, alpha }, fn);

  /** Cross-fade between two drawings while interpolating their boxes. */
  const fadeTransform = (ctx, k, src, dst, drawSrc, drawDst) => {
    const cur = {
      cx: lerp(src.cx, dst.cx, k), cy: lerp(src.cy, dst.cy, k),
      w: lerp(src.w, dst.w, k), h: lerp(src.h, dst.h, k),
    };
    const draw = (box, alpha, fn) => {
      if (alpha <= 0.002) return;
      ctx.save();
      ctx.translate(cur.cx, cur.cy);
      ctx.scale(cur.w / box.w, cur.h / box.h);
      ctx.translate(-box.cx, -box.cy);
      ctx.globalAlpha *= alpha;
      fn();
      ctx.restore();
    };
    draw(src, 1 - R.smooth(clamp(k * 1.25)), drawSrc);
    draw(dst, R.smooth(clamp(k * 1.25 - 0.25)), drawDst);
  };

  const blink = (t, rate = 2.2) => (Math.floor(t * rate) % 2 === 0 ? 1 : 0.15);

  // ---------------------------------------------------------------- icons
  function drawIcon(ctx, kind, x, y, s = 1, alpha = 1, color) {
    if (alpha <= 0.002 || s <= 0.01) return;
    const c = color || KIND[kind].color;
    const w = 5 * s;
    if (kind === 'user') {
      A.glyphMark(ctx, '”', x, y, 0.42 * s, { color: c, alpha, font: 'serif800' });
    } else if (kind === 'sys') {
      for (let k = 0; k < 3; k++) {
        const yy = y + (0.17 - 0.17 * k) * s;
        A.stroke(ctx, A.line(x - 0.28 * s, yy, x + (k === 2 ? 0.08 : 0.28) * s, yy), { color: c, width: w, alpha });
      }
    } else if (kind === 'env') {
      A.stroke(ctx, A.line(x - 0.25 * s, y, x + 0.25 * s, y), { color: c, width: w, alpha });
      A.stroke(ctx, A.line(x, y - 0.25 * s, x, y + 0.25 * s), { color: c, width: w, alpha });
    } else if (kind === 'tool') {
      A.stroke(ctx, A.rrect(x, y + 0.11 * s, 0.58 * s, 0.2 * s, 0.1 * s), { color: c, width: 3.6 * s, alpha });
      for (const dx of [-0.19, 0, 0.19]) A.stroke(ctx, A.circle(x + dx * s, y - 0.15 * s, 0.07 * s), { color: c, width: 3.4 * s, alpha });
    } else {
      // req / res: a small record card with a pairing dot
      A.stroke(ctx, A.rrect(x, y, 0.58 * s, 0.44 * s, 0.07 * s), { color: c, width: 3.6 * s, alpha });
      A.stroke(ctx, A.line(x - 0.17 * s, y + 0.07 * s, x + 0.17 * s, y + 0.07 * s), { color: c, width: 3 * s, alpha });
      A.stroke(ctx, A.line(x - 0.17 * s, y - 0.07 * s, x + 0.06 * s, y - 0.07 * s), { color: c, width: 3 * s, alpha });
      A.fill(ctx, A.circle(x + 0.29 * s, y, 0.06 * s), c, alpha);
    }
  }

  // ---------------------------------------------------------------- nodes
  /** Language model: three stacked slabs; act(k) flashes slab k (0 = bottom). */
  function drawModel(ctx, x, y, s, alpha, act, labelAlpha = 1, dim = 0) {
    if (alpha <= 0.002) return;
    const w = 1.85 * s, h = 0.9 * s, th = 0.14 * s, gap = 0.34 * s;
    const dk = (c) => (dim > 0 ? mix(c, '#000000', dim * 0.6) : c);
    for (let k = 0; k < 3; k++) {
      const cy = y - gap * 0.6 + k * gap;
      const f = act ? clamp(act(k)) : 0;
      const left = A.polyline([[x - w / 2, cy], [x, cy - h / 2], [x, cy - h / 2 - th], [x - w / 2, cy - th]], true);
      const right = A.polyline([[x, cy - h / 2], [x + w / 2, cy], [x + w / 2, cy - th], [x, cy - h / 2 - th]], true);
      const top = A.polyline([[x, cy + h / 2], [x + w / 2, cy], [x, cy - h / 2], [x - w / 2, cy]], true);
      A.fill(ctx, left, dk(mix('#3B4048', '#1F6F60', f)), alpha);
      A.fill(ctx, right, dk(mix('#2A2E35', '#18574B', f)), alpha);
      A.fill(ctx, top, dk(mix('#5F656E', C.teal, f * 0.85)), alpha);
      A.stroke(ctx, top, { color: dk(mix('#C9CED6', '#E8FFF8', f)), width: 2 * s + 0.4, alpha });
      A.stroke(ctx, A.polyline([[x - w / 2, cy], [x - w / 2, cy - th], [x, cy - h / 2 - th], [x + w / 2, cy - th], [x + w / 2, cy]]), { color: dk('#8A9099'), width: 1.4 * s + 0.3, alpha });
    }
    A.drawText(ctx, B('语言模型', 34, C.ink), x, y - gap * 0.6 - h / 2 - th - 0.22 * s, { anchor: [0.5, 0], alpha: alpha * labelAlpha * (1 - 0.5 * dim), scale: Math.max(0.6, s) });
  }

  /** Gear outline used inside the program node. */
  function gearPoly(x, y, r, rot) {
    const pts = [];
    const n = 8;
    for (let i = 0; i < n; i++) {
      const a = rot + (i / n) * Math.PI * 2;
      const d = Math.PI / n;
      const r1 = r * 0.78, r2 = r;
      pts.push([x + r1 * Math.cos(a - d * 0.85), y + r1 * Math.sin(a - d * 0.85)]);
      pts.push([x + r2 * Math.cos(a - d * 0.45), y + r2 * Math.sin(a - d * 0.45)]);
      pts.push([x + r2 * Math.cos(a + d * 0.45), y + r2 * Math.sin(a + d * 0.45)]);
      pts.push([x + r1 * Math.cos(a + d * 0.85), y + r1 * Math.sin(a + d * 0.85)]);
    }
    return A.polyline(pts, true);
  }

  /** Program (the application): circle + gear, label on the right. */
  function drawProgram(ctx, x, y, s, alpha, st = {}) {
    if (alpha <= 0.002 || s <= 0.01) return;
    const r = 0.62 * s;
    const c = st.color || C.prog;
    if (st.pulse > 0 && st.pulse < 1) {
      const p = st.pulse;
      A.stroke(ctx, A.circle(x, y, r * (1 + 0.7 * p)), { color: st.pulseColor || c, width: 5 * s * (1 - p), alpha: alpha * (1 - p) });
    }
    A.fill(ctx, A.circle(x, y, r), '#100C1C', alpha);
    A.stroke(ctx, A.circle(x, y, r), { color: c, width: 4.5 * s, alpha, b: st.draw == null ? 1 : st.draw });
    const g = gearPoly(x, y, 0.33 * s, st.rot || 0);
    A.stroke(ctx, g, { color: c, width: 3.2 * s, alpha: alpha * (st.draw == null ? 1 : clamp(st.draw * 2 - 1)) });
    A.stroke(ctx, A.circle(x, y, 0.1 * s), { color: c, width: 3 * s, alpha: alpha * (st.draw == null ? 1 : clamp(st.draw * 2 - 1)) });
    if (st.label !== false) {
      A.drawText(ctx, B('程序', 34, c), x + r + 0.2 * s, y, { anchor: [0, 0.5], alpha: alpha * (st.labelAlpha == null ? 1 : st.labelAlpha), scale: s });
    }
  }

  /** Transcription tool. st: active (0..1), run (scan 0..1), out (text lines 0..1). */
  function drawTool(ctx, x, y, s, alpha, st = {}) {
    if (alpha <= 0.002) return;
    const w = 2.3 * s, h = 0.86 * s;
    const act = st.active || 0;
    const c = mix('#5E646C', C.tool, act);
    const body = A.rrect(x, y, w, h, h / 2);
    if (st.glow > 0) {
      ctx.save();
      ctx.shadowColor = A.rgba(C.tool, 0.6 * st.glow);
      ctx.shadowBlur = 30 * st.glow;
      A.fill(ctx, body, '#0B0D10', alpha);
      ctx.restore();
    }
    A.fill(ctx, body, '#0B0D10', alpha);
    A.stroke(ctx, body, { color: c, width: 4 * s, alpha, b: st.draw == null ? 1 : st.draw });
    for (const dx of [-w / 2, w / 2]) {
      A.fill(ctx, A.circle(x + dx, y, 0.1 * s), '#000', alpha);
      A.stroke(ctx, A.circle(x + dx, y, 0.1 * s), { color: c, width: 3.5 * s, alpha });
    }
    // inner display: waveform -> arrow -> text lines
    const inner = alpha * (st.draw == null ? 1 : clamp(st.draw * 2 - 1));
    const hs = [0.18, 0.34, 0.5, 0.3, 0.42, 0.22, 0.14];
    const run = st.run || 0;
    for (let i = 0; i < hs.length; i++) {
      const bx = x - 0.78 * s + i * 0.085 * s;
      const lit = clamp(run * 1.6 - i / hs.length);
      A.stroke(ctx, A.line(bx, y - hs[i] * 0.5 * s, bx, y + hs[i] * 0.5 * s), { color: mix('#6E747C', C.ink, lit), width: 3 * s, alpha: inner });
    }
    A.stroke(ctx, A.line(x - 0.12 * s, y, x + 0.12 * s, y), { color: mix('#6E747C', C.tool, act), width: 2.5 * s, alpha: inner });
    A.tip(ctx, x + 0.16 * s, y, 1, 0, { color: mix('#6E747C', C.tool, act), len: 9 * s, wid: 9 * s, alpha: inner });
    const out = st.out || 0;
    for (let i = 0; i < 3; i++) {
      const ly = y + (0.16 - 0.16 * i) * s;
      const len = (i === 2 ? 0.32 : 0.5) * s;
      const k = clamp(out * 3 - i);
      A.stroke(ctx, A.line(x + 0.32 * s, ly, x + 0.32 * s + len, ly), { color: '#6E747C', width: 3 * s, alpha: inner });
      if (k > 0) A.stroke(ctx, A.line(x + 0.32 * s, ly, x + 0.32 * s + len * k, ly), { color: C.res, width: 3 * s, alpha: inner });
    }
    if (run > 0 && run < 1) {
      const sx = x - 0.85 * s + 1.7 * s * run;
      A.stroke(ctx, A.line(sx, y - 0.3 * s, sx, y + 0.3 * s), { color: C.res, width: 3 * s, alpha: inner * 0.9 });
    }
    if (st.labels !== false) {
      const la = alpha * (st.labelAlpha == null ? 1 : st.labelAlpha);
      A.drawText(ctx, B('转写工具', 30, C.ink), x, y - h / 2 - 0.16, { anchor: [0.5, 0], alpha: la });
      A.drawText(ctx, M('transcribe_audio', 22, mix(C.dim, C.tool, st.nameHL || 0)), x, y - h / 2 - 0.58, { anchor: [0.5, 0], alpha: la });
    }
  }

  const WAVE = [0.22, 0.46, 0.72, 0.4, 0.92, 0.6, 0.3, 0.7, 0.5, 0.26, 0.4];
  /** Local recording file. st.read: 0..1 (bars light up as the tool reads). */
  function drawRecording(ctx, x, y, s, alpha, st = {}) {
    if (alpha <= 0.002) return;
    const w = 1.05 * s, h = 1.2 * s;
    const card = A.polyline([[x - w / 2, y + h / 2], [x + w / 2 - 0.22 * s, y + h / 2], [x + w / 2, y + h / 2 - 0.22 * s], [x + w / 2, y - h / 2], [x - w / 2, y - h / 2]], true);
    A.fill(ctx, card, C.panel, alpha);
    A.stroke(ctx, card, { color: '#6E747C', width: 3 * s, alpha });
    A.stroke(ctx, A.polyline([[x + w / 2 - 0.22 * s, y + h / 2], [x + w / 2 - 0.22 * s, y + h / 2 - 0.22 * s], [x + w / 2, y + h / 2 - 0.22 * s]]), { color: '#6E747C', width: 2.5 * s, alpha });
    const read = st.read || 0;
    for (let i = 0; i < WAVE.length; i++) {
      const bx = x - 0.36 * s + i * 0.072 * s;
      const hh = WAVE[i] * 0.42 * s;
      const lit = clamp(read * 1.4 - i / WAVE.length);
      const base = st.bright ? C.ink : '#8E949C';
      A.stroke(ctx, A.line(bx, y + 0.1 * s - hh / 2, bx, y + 0.1 * s + hh / 2), { color: mix(base, C.tool, lit), width: 3.4 * s, alpha });
    }
    A.drawText(ctx, M('meeting.wav', 17, C.dim), x, y - 0.38 * s, { anchor: [0.5, 0.5], alpha, scale: s });
    if (st.label !== false) {
      const la = alpha * (st.labelAlpha == null ? 1 : st.labelAlpha);
      const below = st.below || 0;
      A.drawText(ctx, B('本地录音', 30, C.ink), x + w / 2 + 0.2, y, { anchor: [0, 0.5], alpha: la * (1 - below) });
      A.drawText(ctx, B('本地录音', 30, C.ink), x, y - h / 2 - 0.16, { anchor: [0.5, 0], alpha: la * below });
    }
  }

  /** User as an actor. */
  function drawUser(ctx, x, y, s, alpha, st = {}) {
    if (alpha <= 0.002) return;
    const c = st.color || C.user;
    if (st.pulse > 0 && st.pulse < 1) {
      A.stroke(ctx, A.circle(x, y, 0.55 * s * (1 + 0.6 * st.pulse)), { color: c, width: 4 * (1 - st.pulse), alpha: alpha * (1 - st.pulse) });
    }
    A.stroke(ctx, A.circle(x, y + 0.17 * s, 0.17 * s), { color: c, width: 4 * s, alpha });
    const pts = [];
    for (let i = 0; i <= 24; i++) {
      const a = Math.PI * (i / 24);
      pts.push([x + 0.33 * s * Math.cos(a), y - 0.32 * s + 0.3 * s * Math.sin(a)]);
    }
    A.stroke(ctx, A.polyline(pts), { color: c, width: 4 * s, alpha });
    if (st.label !== false) A.drawText(ctx, B('用户', 30, c), x + 0.5 * s, y - 0.04, { anchor: [0, 0.5], alpha: alpha * (st.labelAlpha == null ? 1 : st.labelAlpha) });
  }

  // ---------------------------------------------------------------- the input list (four sources)
  const LIST = { iconX: -0.85, labelX: -0.3, rowY: [1.38, 0.46, -0.46, -1.38], braceX: -1.45 };
  const listLabel = (kind) => B(KIND[kind].tag, 40, C.ink);

  /** World position of a list row's icon for a given group state. */
  const listIconPos = (g, i) => [g.x + LIST.iconX * g.s, g.y + LIST.rowY[i] * g.s];
  const listLabelEnd = (g, i) => [g.x + (LIST.labelX + listLabel(ROWS[i]).width) * g.s, g.y + LIST.rowY[i] * g.s];

  // ---------------------------------------------------------------- documents ("complete input")
  const DOC_STYLE = { pad: 0.2, gap: 0.12, minH: 0.66, tagX: 0.36, contentX: 2.2 };

  function makeDoc(width, blocks) {
    const st = DOC_STYLE;
    const out = blocks.map((b) => {
      const tagL = B(b.tag || KIND[b.kind].tag, 30, KIND[b.kind].color);
      const subL = b.sub ? M(b.sub, 20, C.dim) : null;
      const contentL = A.text(b.content, { size: b.size || 34, color: C.ink, lineHeight: b.lineHeight || 1.38 });
      const tagH = tagL.height + (subL ? subL.height + 0.08 : 0);
      const h = Math.max(st.minH, contentL.height + 0.36, tagH + 0.34);
      return Object.assign({}, b, { tagL, subL, contentL, h });
    });
    const H = out.reduce((s, b) => s + b.h, 0) + st.gap * (out.length - 1) + 2 * st.pad;
    let y = H / 2 - st.pad;
    for (const b of out) {
      b.cy = y - b.h / 2;
      y -= b.h + st.gap;
    }
    return { width, height: H, blocks: out };
  }

  /** Draw one block of a document at doc-local coordinates. */
  function drawBlock(ctx, doc, b, p, alpha, hl = 0) {
    if (p <= 0 || alpha <= 0.002) return;
    const st = DOC_STYLE;
    const bw = doc.width - 2 * st.pad;
    const x0 = -doc.width / 2 + st.pad;
    const color = KIND[b.kind].color;
    const rect = A.rrect(0, b.cy, bw, b.h, 0.1);
    A.fill(ctx, rect, mix(C.panel, color, 0.06 + 0.1 * hl), alpha * clamp(p * 2));
    A.stroke(ctx, rect, { color, width: 2.2 + 1.2 * hl, alpha: alpha * (0.75 + 0.25 * hl), b: R.smooth(clamp(p * 1.5)) });
    const stripe = clamp(p * 2.2 - 0.2);
    if (stripe > 0) {
      ctx.save();
      ctx.globalAlpha *= alpha;
      ctx.fillStyle = color;
      const sh = (b.h - 0.18) * stripe;
      ctx.fillRect(x0 + 0.08, b.cy - sh / 2, 0.065, sh);
      ctx.restore();
    }
    const ta = clamp((p - 0.3) / 0.35);
    const tagY = b.subL ? b.cy + (b.subL.height + 0.08) / 2 : b.cy;
    A.drawText(ctx, b.tagL, x0 + st.tagX, tagY, { anchor: [0, 0.5], alpha: alpha * ta });
    if (b.subL) A.drawText(ctx, b.subL, x0 + st.tagX, tagY - b.tagL.height / 2 - 0.08, { anchor: [0, 0], alpha: alpha * ta });
    const ca = clamp((p - 0.45) / 0.45);
    A.drawText(ctx, b.contentL, x0 + st.contentX + (1 - R.smooth(ca)) * 0.25, b.cy, { anchor: [0, 0.5], alpha: alpha * ca });
  }

  /**
   * Draw a document centred at (cx, cy) with scale s.
   * st: alpha, blocks (array of progress), frame (container progress),
   * header (layout), headerP, flash (0..1 passing flash), hl (per block 0..1).
   */
  function drawDoc(ctx, doc, cx, cy, s, st) {
    const alpha = st.alpha == null ? 1 : st.alpha;
    if (alpha <= 0.002) return;
    at(ctx, cx, cy, s, alpha, () => {
      const box = A.rrect(0, 0, doc.width + 0.02, doc.height, 0.16);
      if (st.frame > 0) A.stroke(ctx, box, { color: C.soft, width: 2.6, alpha: 0.9, b: R.smooth(st.frame) });
      if (st.flash > 0 && st.flash < 1) A.passingFlash(ctx, box, st.flash, { color: '#FFFFFF', width: 7, timeWidth: 0.35 });
      doc.blocks.forEach((b, i) => drawBlock(ctx, doc, b, st.blocks ? st.blocks[i] : 1, 1, st.hl ? st.hl[i] || 0 : 0));
      if (st.header && st.headerP > 0) {
        A.drawText(ctx, st.header, -doc.width / 2, doc.height / 2 + 0.2, { anchor: [0, 1], write: st.headerP, alpha: st.headerAlpha == null ? 1 : st.headerAlpha });
      }
    });
  }

  /** World centre of block i of a document drawn at (cx, cy, s). */
  const blockCenter = (doc, i, cx, cy, s) => [cx, cy + doc.blocks[i].cy * s];
  const blockTagPos = (doc, i, cx, cy, s) => [cx + (-doc.width / 2 + DOC_STYLE.pad + DOC_STYLE.tagX + 0.3) * s, cy + doc.blocks[i].cy * s];

  const MPATH = ['/audio/meeting.wav', MONO(C.ink, 30)];
  const DOC1_BLOCKS = [
    { kind: 'user', content: '把这段本地录音整理成会议纪要。' },
    { kind: 'sys', content: '使用中文，依据取得的资料回答。' },
    { kind: 'env', content: [['录音位置：', {}], MPATH] },
    {
      kind: 'tool', size: 30,
      content: [
        ['transcribe_audio', MONO(C.tool, 30)], ['  转写音频文件\n', { color: C.dim, size: 28 }],
        ['参数：', { size: 28 }], ['file_path', MONO(C.ink, 26)], ['（必填）', { size: 28, color: C.tool }],
        ['、', { size: 28 }], ['model', MONO(C.ink, 26)], ['、', { size: 28 }], ['language', MONO(C.ink, 26)],
        ['、', { size: 28 }], ['output_format', MONO(C.ink, 26)],
      ],
    },
  ];
  const DOC1 = () => makeDoc(9.0, DOC1_BLOCKS);
  const DOC2 = () =>
    makeDoc(9.0, DOC1_BLOCKS.concat([
      {
        kind: 'req', sub: 'call_id: 01', lineHeight: 1.3, size: 26,
        content: [
          ['transcribe_audio', MONO(C.tool, 26)], ['(file_path="/audio/meeting.wav",\n', MONO(C.ink, 26)],
          ['  model="large", language="zh",\n', MONO(C.ink, 26)], ['  output_format="timestamps")', MONO(C.ink, 26)],
        ],
      },
      { kind: 'res', sub: 'call_id: 01', content: [['[00:00] 本周完成原型，下周安排评审。', {}], ['  （模拟）', { color: C.dim, size: 26 }]] },
    ]));

  // ---------------------------------------------------------------- tool-definition code card
  const CODE = [
    [['name', 'k'], [': ', 'p'], ['"transcribe_audio"', 'v']],
    [['description', 'k'], [': ', 'p'], ['"Transcribe an audio file', 's']],
    [['   using Whisper."', 's'], ['   转写音频文件', 'z']],
    [['inputSchema', 'k'], [': {', 'p']],
    [['  type', 'k'], [': ', 'p'], ['"object"', 'v'], [',', 'p']],
    [['  properties', 'k'], [': {', 'p']],
    [['    file_path', 'k'], [':     ', 'p']],
    [['    model', 'k'], [':         ', 'p']],
    [['    language', 'k'], [':      ', 'p']],
    [['    output_format', 'k'], [': ', 'p']],
    [['  },', 'p']],
    [['  required', 'k'], [': [', 'p'], ['"file_path"', 'v'], [']', 'p']],
    [['}', 'p']],
  ];
  const CODE_COL = { k: '#DADDE1', p: '#7F868E', v: C.tool, s: '#C4C9CF', z: C.dim };
  const CODE_PX = 32;
  const codeLine = (parts, size = CODE_PX) =>
    A.text(parts.map(([str, role]) => [str, role === 'z' ? { color: CODE_COL.z, size: 27 } : MONO(CODE_COL[role], size)]), { size, font: 'mono' });
  const VALUE = (comma) => A.text([['{ ', MONO(CODE_COL.p, CODE_PX)], ['type', MONO(CODE_COL.k, CODE_PX)], [': ', MONO(CODE_COL.p, CODE_PX)], ['"string"', MONO(C.tool, CODE_PX)], [' }' + (comma ? ',' : ''), MONO(CODE_COL.p, CODE_PX)]], { size: CODE_PX, font: 'mono' });
  /** Advance width including trailing spaces (mono columns). */
  const rawWidth = (L) => {
    const g = L.glyphs[L.glyphs.length - 1];
    return g ? g.x + g.adv : 0;
  };

  const CARD = { cx: 2.6, cy: 0.55, w: 7.9, h: 5.6 };
  const codeX = CARD.cx - CARD.w / 2 + 0.38;
  const codeTop = CARD.cy + CARD.h / 2 - 0.8;
  const codeY = (k) => codeTop - k * 0.345;
  const NOTE_X = codeX + 5.95;

  function drawCodeCard(ctx, t, g) {
    // g: {alpha, grow (0..1 from icon), from: [x,y]}
    const k = g.grow;
    if (k <= 0 || g.alpha <= 0.002) return;
    const cx = lerp(g.from[0], CARD.cx, k), cy = lerp(g.from[1], CARD.cy, k), sc = lerp(0.08, 1, k);
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(sc, sc);
    ctx.translate(-CARD.cx, -CARD.cy);
    ctx.globalAlpha *= g.alpha * clamp(k * 1.6);
    const box = A.rrect(CARD.cx, CARD.cy, CARD.w, CARD.h, 0.16);
    A.fill(ctx, box, C.panel, 0.92);
    A.stroke(ctx, box, { color: C.tool, width: 2.8, b: R.smooth(clamp(k * 1.3)) });
    A.drawText(ctx, B('工具定义', 30, C.tool), CARD.cx - CARD.w / 2 + 0.38, CARD.cy + CARD.h / 2 - 0.36, { anchor: [0, 0.5], alpha: P(t, S.toolDef + 0.3, 0.5) });
    // line reveal schedule
    const show = [P(t, S.toolDef + 0.35, 0.9, R.linear), P(t, S.toolDef + 1.0, 0.6), P(t, S.toolDef + 1.25, 0.6)];
    for (let i = 3; i <= 12; i++) show[i] = i === 11 ? P(t, S.required + 0.55, 0.6, R.linear) : P(t, S.schema + 0.05 + (i - 3) * 0.12, 0.45);
    for (let i = 0; i < CODE.length; i++) {
      const L = codeLine(CODE[i]);
      if (i === 0 || i === 11) A.drawText(ctx, L, codeX, codeY(i), { anchor: [0, 0.5], write: show[i] });
      else A.drawText(ctx, L, codeX + (1 - show[i]) * 0.2, codeY(i), { anchor: [0, 0.5], alpha: show[i] });
    }
    // property values, aligned in one column
    const valP = [P(t, S.required + 0.05, 0.6, R.linear), P(t, S.optional + 0.05, 0.55, R.linear), P(t, S.optional + 0.3, 0.55, R.linear), P(t, S.optional + 0.55, 0.55, R.linear)];
    const valX = codeX + rawWidth(codeLine(CODE[6]));
    for (let j = 0; j < 4; j++) A.drawText(ctx, VALUE(j < 3), valX, codeY(6 + j), { anchor: [0, 0.5], write: valP[j] });
    // "可以请求什么操作": underline the operation name
    const nb = codeLine(CODE[0]).box(6, 24);
    const ul = P(t, S.canRequest + 0.1, 0.6) * (1 - P(t, S.schema - 0.3, 0.5));
    if (ul > 0) A.stroke(ctx, A.line(codeX + nb.x0, codeY(0) - 0.22, codeX + nb.x1, codeY(0) - 0.22), { color: C.tool, width: 3.5, b: ul, alpha: ul });
    // required: file_path is boxed in both places and pulses together
    const reqOut = P(t, S.optional - 0.1, 0.6);
    const pulse = A.indicate(P(t, S.required + 1.15, 0.8, R.linear));
    const k6 = codeLine(CODE[6]).box(4, 13);
    const k11 = codeLine(CODE[11]).box(13, 24);
    const b6p = P(t, S.required + 0.1, 0.6), b11p = P(t, S.required + 0.85, 0.5);
    const boxAlpha = 1 - 0.65 * reqOut;
    if (b6p > 0) {
      const sc6 = 1 + 0.08 * pulse;
      A.stroke(ctx, A.rrect(codeX + k6.cx, codeY(6), (k6.w + 0.18) * sc6, 0.4 * sc6, 0.08), { color: C.tool, width: 2.6 + 1.5 * pulse, b: b6p, alpha: boxAlpha });
    }
    if (b11p > 0) {
      const sc11 = 1 + 0.08 * pulse;
      A.stroke(ctx, A.rrect(codeX + k11.cx, codeY(11), (k11.w + 0.18) * sc11, 0.4 * sc11, 0.08), { color: C.tool, width: 2.6 + 1.5 * pulse, b: b11p, alpha: boxAlpha });
    }
    A.drawText(ctx, B('必填', 30, C.tool), NOTE_X, codeY(6), { anchor: [0, 0.5], write: P(t, S.required + 0.35, 0.7, R.linear) });
    // optional: brace on the right of lines 7-9
    const opt = P(t, S.optional + 0.55, 0.6);
    if (opt > 0) {
      const br = A.brace([NOTE_X - 0.36, codeY(9) - 0.15], [NOTE_X - 0.36, codeY(7) + 0.15], 0.22);
      A.stroke(ctx, br, { color: C.ink, width: 3, b: opt });
      A.drawText(ctx, B('可选', 30, C.ink), NOTE_X, br.tip[1], { anchor: [0, 0.5], write: P(t, S.optional + 0.8, 0.7, R.linear) });
    }
    // describe-only tag
    A.drawText(ctx, T('描述用法', 26, C.tool), CARD.cx + CARD.w / 2 - 0.35, CARD.cy + CARD.h / 2 - 0.36, { anchor: [1, 0.5], alpha: 0.85 * P(t, S.describe + 0.1, 0.6) });
    if (t > S.describe && t < S.describe + 1.6) A.passingFlash(ctx, box, P(t, S.describe, 1.4, R.linear), { color: C.tool, width: 6, timeWidth: 0.3 });
    ctx.restore();
  }

  // ---------------------------------------------------------------- tool-call message
  const MSG_LINES = [
    [['name', 'k'], [': ', 'p'], ['transcribe_audio', 'v']],
    [['arguments', 'k'], [': {', 'p']],
    [['  "file_path"', 'k'], [': ', 'p'], ['"/audio/meeting.wav"', 'v'], [',', 'p']],
    [['  "model"', 'k'], [': ', 'p'], ['"large"', 'v'], [',', 'p']],
    [['  "language"', 'k'], [': ', 'p'], ['"zh"', 'v'], [',', 'p']],
    [['  "output_format"', 'k'], [': ', 'p'], ['"timestamps"', 'v']],
    [['}', 'p']],
  ];
  const msgLayout = () =>
    A.text(MSG_LINES.flatMap((parts, i) => parts.map(([str, role], j) => [str + (j === parts.length - 1 && i < MSG_LINES.length - 1 ? '\n' : ''), MONO(CODE_COL[role], 32)])), { size: 32, font: 'mono', lineHeight: 1.3 });
  const MSG = { cx: 0.35, cy: 0.55, w: 6.6, padX: 0.42 };

  // token schedule: [time, glyph count]
  const TOKENS = (() => {
    const tk = [];
    const add = (time, str) => tk.push([time, Array.from(str).length]);
    add(64.88, 'name'); add(65.04, ': '); add(65.42, 'trans'); add(65.72, 'cribe'); add(66.05, '_audio');
    add(66.95, 'arguments'); add(67.12, ': {');
    add(67.32, '  "file'); add(67.46, '_path"'); add(67.6, ': "'); add(67.92, '/audio'); add(68.12, '/meeting'); add(68.33, '.wav'); add(68.46, '",');
    add(68.92, '  "model"'); add(69.02, ': "large",');
    add(69.13, '  "language"'); add(69.23, ': "zh",');
    add(69.34, '  "output'); add(69.43, '_format"'); add(69.52, ': "timestamps"');
    add(69.72, '}');
    return tk;
  })();
  const typed = (t) => {
    let n = 0;
    for (const [time, k] of TOKENS) n += k * clamp((t - time) / 0.07);
    return n;
  };
  const glyphTime = (() => {
    const out = [];
    for (const [time, k] of TOKENS) for (let i = 0; i < k; i++) out.push(time + (0.07 * i) / k);
    return out;
  })();

  function msgBox(scale = 1, cx = MSG.cx, cy = MSG.cy) {
    const L = msgLayout();
    const h = L.height + 0.62;
    return { cx, cy, w: MSG.w * scale, h: h * scale, L, rawH: h };
  }

  /** The generated message. st: frame (0..1), solid (0..1), tag (0..1), n (typed glyphs) */
  function drawMessage(ctx, t, st) {
    const L = msgLayout();
    const h = L.height + 0.62;
    const x0 = MSG.cx - MSG.w / 2, top = MSG.cy + h / 2;
    const frame = A.rrect(MSG.cx, MSG.cy, MSG.w, h, 0.16);
    A.fill(ctx, frame, C.panel, 0.9 * clamp(st.frame * 2));
    if (st.solid < 1) A.stroke(ctx, frame, { color: C.dim, width: 2.4, b: st.frame, dash: [14, 10], alpha: 1 - st.solid });
    if (st.solid > 0) A.stroke(ctx, frame, { color: C.tool, width: 3, b: st.solid });
    const n = st.n;
    const hlTime = (i) => (i < glyphTime.length ? glyphTime[i] : 0);
    A.drawText(ctx, L, x0 + MSG.padX, top - 0.31, {
      anchor: [0, 0], reveal: n,
      colorFn: (i, g) => {
        const age = t - hlTime(i);
        return age < 0.5 && st.live ? mix(C.yellow, g.st.color, clamp(age / 0.5)) : g.st.color;
      },
    });
    // cursor
    if (st.cursor > 0) {
      const k = Math.min(Math.floor(n), L.glyphs.length);
      let cx = x0 + MSG.padX, cy = top - 0.31 - 0.88 * L.size;
      if (k > 0) {
        const g = L.glyphs[k - 1];
        cx = x0 + MSG.padX + g.x + g.adv;
        cy = top - 0.31 + g.y;
      }
      const idle = t - (k > 0 ? hlTime(k - 1) : 0) > 0.35;
      const a = st.cursor * (idle ? blink(t) : 1);
      ctx.save();
      ctx.globalAlpha *= a;
      ctx.fillStyle = C.ink;
      ctx.fillRect(cx + 0.03, cy - 0.06, 0.035, L.size * 1.05);
      ctx.restore();
    }
    // tag
    if (st.tag > 0) {
      const tag = B('工具调用', 28, '#1A1500');
      const tw = tag.width + 0.4, th = 0.44;
      const tx = x0 + 0.3 + tw / 2, ty = top;
      const pill = A.rrect(tx, ty, tw, th, th / 2);
      A.fill(ctx, pill, C.tool, st.tag);
      A.drawText(ctx, tag, tx, ty, { anchor: [0.5, 0.5], alpha: st.tag });
    }
    return { L, h, x0, top };
  }

  // ---------------------------------------------------------------- record cards
  function drawRecordCard(ctx, kind, cx, cy, s, alpha, st = {}) {
    if (alpha <= 0.002) return;
    const color = KIND[kind].color;
    at(ctx, cx, cy, s, alpha, () => {
      const w = 4.3, h = 1.08;
      const box = A.rrect(0, 0, w, h, 0.14);
      A.fill(ctx, box, mix(C.panel, color, 0.07), 1);
      A.stroke(ctx, box, { color, width: 3 });
      drawIcon(ctx, kind, -w / 2 + 0.48, 0, 1.15, 1);
      A.drawText(ctx, B(KIND[kind].tag, 30, color), -w / 2 + 0.95, 0.2, { anchor: [0, 0.5] });
      const idHL = st.idHL || 0;
      A.drawText(ctx, M('call_id: 01', 22, mix(C.dim, C.yellow, idHL)), w / 2 - 0.25, 0.2, { anchor: [1, 0.5] });
      if (kind === 'req') A.drawText(ctx, M('transcribe_audio', 26, C.ink), -w / 2 + 0.95, -0.22, { anchor: [0, 0.5] });
      else A.drawText(ctx, T('[00:00] 本周完成原型，下周安排评审。', 24, C.ink), -w / 2 + 0.95, -0.22, { anchor: [0, 0.5] });
      A.fill(ctx, A.circle(w / 2, 0, 0.08), color, 1);
    });
  }

  /** Compact row card used inside the next-input container. */
  function drawMiniCard(ctx, kind, cx, cy, s, alpha) {
    if (alpha <= 0.002) return;
    const color = KIND[kind].color;
    at(ctx, cx, cy, s, alpha, () => {
      const w = 3.3, h = 0.62;
      const box = A.rrect(0, 0, w, h, 0.12);
      A.fill(ctx, box, mix(C.panel, color, 0.07), 1);
      A.stroke(ctx, box, { color, width: 2.8 });
      drawIcon(ctx, kind, -w / 2 + 0.42, 0, 0.95, 1);
      A.drawText(ctx, B(KIND[kind].tag, 30, color), -w / 2 + 0.85, 0, { anchor: [0, 0.5] });
      A.fill(ctx, A.circle(w / 2, 0, 0.075), color, 1);
    });
  }

  /** Meeting minutes page. p: generation progress of the body lines. */
  function drawMinutes(ctx, cx, cy, s, alpha, st = {}) {
    if (alpha <= 0.002) return;
    at(ctx, cx, cy, s, alpha, () => {
      const w = 3.7, h = 3.3, f = 0.42;
      const page = A.polyline([[-w / 2, h / 2], [w / 2 - f, h / 2], [w / 2, h / 2 - f], [w / 2, -h / 2], [-w / 2, -h / 2]], true);
      A.fill(ctx, page, '#10141A', 1);
      A.stroke(ctx, page, { color: C.ink, width: 3, b: st.draw == null ? 1 : st.draw });
      A.stroke(ctx, A.polyline([[w / 2 - f, h / 2], [w / 2 - f, h / 2 - f], [w / 2, h / 2 - f]]), { color: C.ink, width: 2.5, alpha: st.draw == null ? 1 : clamp(st.draw * 2 - 1) });
      A.drawText(ctx, B('会议纪要', 42, C.ink), -w / 2 + 0.4, h / 2 - 0.42, { anchor: [0, 0.5], write: st.title == null ? 1 : st.title });
      const body = A.text('1. 本周完成原型\n2. 下周安排评审', { size: 34, color: C.ink, lineHeight: 1.55 });
      A.drawText(ctx, body, -w / 2 + 0.4, h / 2 - 0.95, { anchor: [0, 0], reveal: st.body == null ? 99 : st.body });
      A.drawText(ctx, T('依据：转写文本 [00:00]', 22, C.dim), -w / 2 + 0.4, -h / 2 + 0.38, { anchor: [0, 0.5], alpha: st.note == null ? 1 : st.note });
    });
  }

  // ---------------------------------------------------------------- shared state functions
  /** Group state of the four-source list. */
  const listG = (t) =>
    kf(t, [
      [0, { x: 1.28, y: 0.1, s: 1.2 }],
      [8.3, { x: 1.28, y: 0.1, s: 1.2 }],
      [9.0, { x: -3.95, y: 0.55, s: 0.9 }],
      [36.0, { x: -3.95, y: 0.55, s: 0.9 }],
      [37.4, { x: 1.28, y: 0.2, s: 1.2 }],
      [42.55, { x: 1.28, y: 0.2, s: 1.2 }],
      [43.35, { x: -4.35, y: 0.1, s: 0.78 }],
    ]);
  const programCameo = [0.26, 3.18];

  /** Hub positions (world). */
  const HUB = { model: [-5.6, 0.55], prog: [5.0, 0.55], tool: [5.0, -2.45], rec: [1.0, -2.45], user: [5.0, 3.05] };
  const REC1 = [-5.5, -2.85];

  /** Model activity: flash per slab from token / processing events. */
  function modelAct(t) {
    const pulses = [];
    // processing sweeps after each input delivery
    for (const t0 of [57.95, 58.6, 59.25, 59.9, 135.75, 136.4, 141.3, 141.95, 142.6]) pulses.push([t0, 0.55]);
    for (const [time] of TOKENS) pulses.push([time - 0.1, 0.3]);
    for (let i = 0; i < 6; i++) pulses.push([142.95 + i * 0.32, 0.3]);
    return (k) => {
      let f = 0;
      for (const [t0, d] of pulses) {
        const local = (t - t0 - k * 0.08) / d;
        if (local > 0 && local < 1) f = Math.max(f, R.thereAndBack(local));
      }
      return f;
    };
  }

  const idPulse = (tt) => A.indicate(P(tt, S.pair + 0.1, 1.2, R.linear));
  /** Rows of the next-input container (world). */
  const nextRowPos = (i) => [-2.25, [2.3, 1.55, 0.8, 0.05, -0.85, -1.75][i]];

  /** Program gear angle: slow idle turn plus faster turns while it works. */
  const SPIN = [[S.identify - 0.1, S.branch + 0.8], [S.orgNext, S.addRes + 1.0], [S.give2 - 0.4, S.give2 + 0.6], [S.deliver - 0.1, S.deliver + 0.9]];
  const gearAngle = (t) => {
    let acc = 0;
    for (const [a, b] of SPIN) acc += clamp(t - a, 0, b - a);
    return -(0.25 * t + 2.4 * acc);
  };

  // ---------------------------------------------------------------- the scene
  A.drawScene = (ctx, t) => {
    A.beginFrame(ctx, { x: 0, y: 0, h: A.FH });
    const g = listG(t);
    const actFn = modelAct(t);

    // ============================================================ 0. the request (0 - 5.6)
    if (t < 6.2) {
      const appear = P(t, 0.12, 0.8);
      const leave = P(t, 4.6, 0.7);
      const a = appear * (1 - leave);
      const y = 0.35 - 0.3 * (1 - appear);
      const box = A.rrect(0.45, y, 10.0, 1.32, 0.24);
      A.fill(ctx, box, C.panel, a);
      A.stroke(ctx, box, { color: C.edge, width: 2.6, alpha: a, b: R.smooth(clamp(appear * 1.2)) });
      drawUser(ctx, -5.75, y + 0.05, 1.15, a, { label: false });
      A.drawText(ctx, B('用户', 30, C.user), -5.75, y - 0.62, { anchor: [0.5, 1], alpha: a });
      const L = T('把这段本地录音整理成会议纪要。', 46, C.ink);
      const n = L.glyphs.length * P(t, S.askText, S.askTextEnd - S.askText - 0.2, R.linear);
      // the sentence leaves the box and shrinks into the user icon of the list
      const lift = P(t, 4.45, 0.45);
      const fly = P(t, 4.8, 0.65);
      const target = listIconPos(g, 0);
      const start = [-4.35, y + 0.35 * lift];
      const pos = lerpPt(start, [target[0] - 0.25, target[1]], fly);
      A.drawText(ctx, L, pos[0], pos[1], { anchor: [0, 0.5], reveal: n, scale: lerp(1, 0.18, fly), alpha: appear * (1 - P(t, 5.2, 0.25)) });
      // caret + send button
      if (lift <= 0) {
        const k = Math.floor(n);
        const gx = k > 0 ? L.glyphs[k - 1].x + L.glyphs[k - 1].adv : 0;
        const typing = t > S.askText && t < S.askTextEnd;
        A.stroke(ctx, A.line(-4.35 + gx + 0.05, y - 0.24, -4.35 + gx + 0.05, y + 0.24), { color: C.user, width: 3, alpha: a * (typing ? 1 : blink(t)) * (t > 0.6 ? 1 : 0) });
      }
      const ready = P(t, S.askTextEnd - 0.1, 0.4);
      const press = P(t, 4.3, 0.35, R.thereAndBack);
      const bc = [4.95, y];
      A.fill(ctx, A.circle(bc[0], bc[1], 0.34 * (1 - 0.12 * press)), mix('#20252C', C.user, ready), a);
      A.stroke(ctx, A.line(bc[0], bc[1] - 0.15, bc[0], bc[1] + 0.13), { color: mix(C.dim, '#081018', ready), width: 4.5, alpha: a });
      A.tip(ctx, bc[0], bc[1] + 0.2, 0, 1, { color: mix(C.dim, '#081018', ready), len: 16, wid: 18, alpha: a });
    }

    // ============================================================ recording (persistent)
    {
      const recIn = P(t, 2.35, 0.7);
      const toHub = P(t, 52.4, 1.4);
      const pos = lerpPt(REC1, HUB.rec, toHub);
      const fade = 1 - P(t, 151.75, 0.5);
      const read = P(t, S.read, 1.1, R.linear);
      const dimA = lerp(1, 0.4, P(t, 92.6, 0.8));
      const hideDoc2 = 1 - P(t, 112.3, 0.6) + P(t, 133.6, 0.6);
      A.layer(ctx, recIn * fade * dimA * clamp(hideDoc2), (c) => drawRecording(c, pos[0], pos[1] - 0.3 * (1 - recIn), 1, 1, { read, bright: t > S.read + 1.1, below: toHub }));
    }

    // ============================================================ 1. four sources (5 - 51)
    const listAlpha = 1 - P(t, 50.95, 0.6);
    if (t > 4.6 && listAlpha > 0) {
      // program cameo that organises the other inputs
      const camIn = P(t, 5.3, 0.6, R.easeOutBack);
      const camOut = P(t, 8.0, 0.6);
      if (camIn > 0 && camOut < 1) {
        drawProgram(ctx, programCameo[0], programCameo[1] + 0.4 * camOut, 0.78 * camIn, 1 - camOut, { rot: -t * 1.6, labelAlpha: 1 });
      }
      at(ctx, g.x, g.y, g.s, listAlpha, () => {
        for (let i = 0; i < 4; i++) {
          const kind = ROWS[i];
          const y = LIST.rowY[i];
          let ia, ip;
          if (i === 0) {
            ia = P(t, 5.15, 0.4);
            ip = [LIST.iconX, y];
          } else {
            const t0 = 5.85 + (i - 1) * 0.36;
            const fly = P(t, t0, 0.75);
            ia = clamp(fly * 3);
            const src = [(programCameo[0] - g.x) / g.s, (programCameo[1] - g.y) / g.s];
            ip = arcPt(src, [LIST.iconX, y], fly, 0.7);
          }
          // indicate on "四种来源"
          const ind = A.indicate(P(t, S.four + i * 0.17, 0.55, R.linear));
          const sc = 1 + 0.3 * ind;
          drawIcon(ctx, kind, ip[0], ip[1], sc, ia, ind > 0 ? mix(KIND[kind].color, C.yellow, ind * 0.6) : null);
          const lw = i === 0 ? P(t, 5.15, 0.8, R.linear) : P(t, 6.35 + (i - 1) * 0.36, 0.8, R.linear);
          A.drawText(ctx, listLabel(kind), LIST.labelX, y, { anchor: [0, 0.5], write: lw });
        }
        const br = A.brace([LIST.braceX, 1.85], [LIST.braceX, -1.85], 0.26);
        A.stroke(ctx, br, { color: C.ink, width: 3.2, b: P(t, 6.7, 0.8) });
        const flash = P(t, S.together + 0.05, 0.8, R.linear);
        if (flash > 0 && flash < 1) A.passingFlash(ctx, br, flash, { color: C.yellow, width: 7, timeWidth: 0.5 });
        const lbl = B('首次输入', 40, C.ink);
        const labInd = A.indicate(P(t, S.together + 0.3, 0.9, R.linear));
        A.drawText(ctx, lbl, br.tip[0] - 0.18, br.tip[1], {
          anchor: [1, 0.5], write: P(t, 7.0, 0.9, R.linear), scale: 1 + 0.12 * labInd,
          color: labInd > 0 ? mix(C.ink, C.yellow, labInd) : null,
        });
      });
    }

    // ============================================================ 2. detail cards (8.5 - 21)
    if (t > S.userMsg && t < 21.2) {
      const cards = [
        { kind: 'user', y: 2.3, t0: S.userMsg, content: T('把这段本地录音整理成会议纪要。', 40) },
        { kind: 'sys', y: 0.7, t0: S.sysMsg, content: T('使用中文，依据取得的资料回答。', 40) },
        { kind: 'env', y: -0.9, t0: S.envMsg, content: A.text([['录音位置：', {}], ['/audio/meeting.wav', MONO(C.ink, 36)]], { size: 40 }) },
      ];
      const cx = 2.6, w = 7.9, h = 1.3, x0 = cx - w / 2;
      cards.forEach((c, i) => {
        const grow = P(t, c.t0 + 0.08, 0.75);
        const back = P(t, 19.5 + i * 0.15, 0.7);
        const k = grow * (1 - back);
        if (k <= 0) return;
        const lend = listLabelEnd(g, i);
        // tether
        const teth = A.cubic([lend[0] + 0.18, lend[1]], [lend[0] + 1.1, lend[1]], [x0 - 1.0, c.y], [x0 - 0.08, c.y], 30);
        A.stroke(ctx, teth, { color: KIND[c.kind].color, width: 2.2, alpha: 0.7, b: P(t, c.t0, 0.45) * (1 - back) });
        const ccx = lerp(x0 - 0.08, cx, k), ccy = c.y, sc = lerp(0.05, 1, k);
        ctx.save();
        ctx.translate(ccx, ccy);
        ctx.scale(sc, sc);
        ctx.globalAlpha *= clamp(k * 1.5);
        const box = A.rrect(0, 0, w, h, 0.14);
        A.fill(ctx, box, C.panel, 0.95);
        A.stroke(ctx, box, { color: KIND[c.kind].color, width: 2.8, b: R.smooth(clamp(k * 1.3)) });
        const ta = P(t, c.t0 + 0.45, 0.45) * (1 - back);
        A.drawText(ctx, B(KIND[c.kind].tag, 28, KIND[c.kind].color), -w / 2 + 0.32, 0.34, { anchor: [0, 0.5], alpha: ta });
        A.drawText(ctx, c.content, -w / 2 + 0.32 + (1 - ta) * 0.2, -0.2, { anchor: [0, 0.5], alpha: ta });
        if (c.kind === 'env') {
          // "路径已经进入输入"
          const r = c.content.find('/audio/meeting.wav');
          const bb = c.content.box(r[0], r[1]);
          const ox = -w / 2 + 0.32, oy = -0.2 + c.content.height / 2;
          const hp = P(t, S.pathIn + 0.05, 0.6) * (1 - back);
          const hb = A.rrect(ox + bb.cx, oy + bb.cy, bb.w + 0.2, bb.h + 0.12, 0.08);
          A.fill(ctx, hb, C.ink, 0.1 * hp);
          A.stroke(ctx, hb, { color: C.ink, width: 2.4, b: hp });
          const ck = P(t, S.pathIn + 0.45, 0.5) * (1 - back);
          A.checkMark(ctx, ox + bb.x1 + 0.45, oy + bb.cy - 0.02, 0.36, { color: C.sys, p: ck, width: 5 });
          A.drawText(ctx, B('已在输入中', 28, C.sys), ox + bb.x1 + 0.8, oy + bb.cy, { anchor: [0, 0.5], alpha: P(t, S.pathIn + 0.7, 0.5) * (1 - back) });
        }
        ctx.restore();
      });
      // "录音内容还没有": the pointer from the path to the file, and the file stays outside
      const ny = P(t, S.notYet - 0.1, 0.9);
      const nyOut = P(t, 19.3, 0.6);
      if (ny > 0 && nyOut < 1) {
        const from = [1.05, -1.35];
        const to = [REC1[0] + 0.62, REC1[1] + 0.45];
        const path = A.cubic(from, [from[0], from[1] - 1.1], [to[0] + 2.2, to[1] + 0.4], to, 50);
        A.arrow(ctx, path, { color: C.soft, width: 3, p: ny, dash: [12, 9], alpha: 1 - nyOut, len: 18, wid: 17 });
        const xa = P(t, S.notYet + 0.55, 0.5) * (1 - nyOut);
        A.crossMark(ctx, REC1[0], REC1[1] + 0.1, 0.4, { color: C.red, p: xa, width: 6 });
        A.drawText(ctx, B('内容还没有读取', 28, C.red), REC1[0] + 2.05, REC1[1], { anchor: [0, 0.5], alpha: P(t, S.notYet + 0.75, 0.5) * (1 - nyOut) });
      }
    }

    // ============================================================ 3. tool definition (21.8 - 36)
    if (t > S.toolDef && t < 36) {
      const grow = P(t, S.toolDef + 0.05, 0.8);
      const back = P(t, 34.6, 0.9);
      const lend = listLabelEnd(g, 3);
      const teth = A.cubic([lend[0] + 0.18, lend[1]], [lend[0] + 1.0, lend[1]], [CARD.cx - CARD.w / 2 - 1.0, 0.2], [CARD.cx - CARD.w / 2 - 0.08, 0.2], 30);
      A.stroke(ctx, teth, { color: C.tool, width: 2.2, alpha: 0.7, b: P(t, S.toolDef, 0.5) * (1 - back) });
      drawCodeCard(ctx, t, { alpha: 1, grow: grow * (1 - back), from: [CARD.cx - CARD.w / 2 - 0.08, 0.2] });
      // "并没有执行工具": the real tool sits idle, outside the input
      const ne = P(t, S.notExec - 0.05, 0.6) * (1 - P(t, 34.6, 0.5));
      if (ne > 0) {
        drawTool(ctx, 2.6, -3.0, 0.8, ne, { labels: false, active: 0 });
        A.drawText(ctx, B('转写工具', 28, C.soft), 2.6 - 1.15, -3.0, { anchor: [1, 0.5], alpha: ne });
        A.drawText(ctx, B('未执行', 28, C.dim), 2.6 + 1.15, -3.0, { anchor: [0, 0.5], alpha: ne });
      }
    }

    // ============================================================ 4. first complete input (42.5 - 58)
    const doc1 = DOC1();
    const D1 = { cx: 2.25, cy: 0.05 };
    if (t > 42.5 && t < 58.6) {
      const blockT = [S.putUser, S.putSys, S.putEnv, S.putTool];
      const bp = blockT.map((t0) => P(t, t0 + 0.3, 0.9, R.linear));
      // doc -> packet next to the program, then into the model
      const shrink = P(t, 50.95, 1.2);
      const travel = P(t, S.give + 0.35, 1.25);
      const intoModel = P(t, S.give + 1.55, 0.45);
      const packetPos = [3.35, 0.55];
      let cx = lerp(D1.cx, packetPos[0], shrink), cy = lerp(D1.cy, packetPos[1], shrink);
      let s = lerp(1, 0.19, shrink);
      if (travel > 0) {
        cx = lerp(packetPos[0], HUB.model[0] + 0.15, travel);
        cy = packetPos[1] + 0.35 * Math.sin(Math.PI * travel);
      }
      s *= 1 - 0.75 * intoModel;
      const alpha = 1 - intoModel;
      drawDoc(ctx, doc1, cx, cy, s, {
        alpha, blocks: bp, frame: P(t, S.whole + 0.05, 0.8), flash: P(t, S.whole + 1.1, 1.0, R.linear),
        header: B('第 1 次完整输入', 40, C.ink), headerP: P(t, S.whole + 0.25, 1.0, R.linear), headerAlpha: 1 - P(t, 50.95, 0.4),
      });
      // icon copies flying from the list rows into the blocks
      blockT.forEach((t0, i) => {
        const fly = P(t, t0, 0.75);
        if (fly <= 0 || fly >= 1) return;
        const src = listIconPos(g, i);
        const dst = blockTagPos(doc1, i, D1.cx, D1.cy, 1);
        const p = arcPt(src, [dst[0] - 0.35, dst[1]], fly, -0.5);
        drawIcon(ctx, ROWS[i], p[0], p[1], lerp(g.s, 0.8, fly), 1 - P(t, t0 + 0.55, 0.2));
      });
      if (shrink > 0.6 && travel <= 0) {
        A.drawText(ctx, T('第 1 次输入', 24, C.dim), packetPos[0], packetPos[1] - doc1.height * 0.19 / 2 - 0.12, { anchor: [0.5, 1], alpha: P(t, 51.8, 0.5) * (1 - P(t, S.give + 0.2, 0.3)) });
      }
    }
    // thumbnail of the first input, kept near the model
    const thumb1 = [-5.6, 3.15];
    {
      const a = P(t, S.give + 1.7, 0.6) * (1 - P(t, S.thumb - 0.1, 0.5)) * (1 - P(t, 112.3, 0.5) + P(t, 133.6, 0.5));
      if (a > 0) {
        const s0 = 0.17;
        const rise = P(t, S.give + 1.6, 0.8);
        const pos = lerpPt([HUB.model[0], HUB.model[1] + 0.2], thumb1, rise);
        drawDoc(ctx, doc1, pos[0], pos[1], s0, { alpha: clamp(a), blocks: [1, 1, 1, 1], frame: 1 });
        A.drawText(ctx, T('第 1 次输入', 22, C.dim), thumb1[0], thumb1[1] - 0.45, { anchor: [0.5, 0], alpha: clamp(a) * rise });
      }
    }

    // ============================================================ hub nodes (51 - 151.8)
    const hubFade = 1 - P(t, 151.7, 0.5);
    const docMode = P(t, 112.3, 0.6) * (1 - P(t, 133.6, 0.6)); // second document fills the screen
    // model
    {
      const a = P(t, 52.2, 0.9) * hubFade * (1 - docMode);
      const dimK = P(t, 78.5, 0.6) * (1 - P(t, S.secondCall - 0.2, 0.6));
      const dim = 1 - 0.5 * dimK;
      const pos = [HUB.model[0] - 0.4 * (1 - P(t, 52.2, 0.9)), HUB.model[1]];
      drawModel(ctx, pos[0], pos[1], 1, a, actFn, 1, dimK);
      // call counter
      const c1 = P(t, 58.3, 0.5);
      if (c1 > 0) {
        const flip = P(t, S.secondCall + 0.1, 0.5);
        const L1 = T('第 1 次调用', 26, C.dim), L2 = B('第 2 次调用', 26, C.yellow);
        const yy = pos[1] - 1.45;
        A.drawText(ctx, L1, pos[0], yy + 0.25 * flip, { anchor: [0.5, 0.5], alpha: a * c1 * (1 - flip) * clamp(dim) });
        const settle = P(t, S.secondCall + 1.4, 0.8);
        A.drawText(ctx, flip > 0 ? A.text('第 2 次调用', { size: 26, weight: 800, color: mix(C.yellow, C.ink, settle) }) : L2, pos[0], yy - 0.25 * (1 - flip), { anchor: [0.5, 0.5], alpha: a * flip, scale: pulseScale(t, S.secondCall + 0.4, 0.7, 0.25) });
      }
    }
    // program
    let progPulse = 0, progPulseColor = C.prog;
    for (const [t0, colr] of [[S.receive + 0.75, C.tool], [S.giveBack + 1.1, C.res], [S.received + 0.05, C.res], [S.orgNext, C.prog], [S.deliver + 0.55, C.ink]]) {
      const p = P(t, t0, 0.8, R.linear);
      if (p > 0 && p < 1) {
        progPulse = p;
        progPulseColor = colr;
      }
    }
    {
      const a = P(t, 51.55, 0.8) * hubFade * (1 - docMode);
      const draw = P(t, 51.55, 1.0);
      drawProgram(ctx, HUB.prog[0], HUB.prog[1], 1, a, { draw, rot: gearAngle(t), pulse: progPulse, pulseColor: progPulseColor });
    }
    // tool
    {
      const a = P(t, 53.2, 0.8) * hubFade * (1 - docMode);
      const dimT = t > 92.6 ? lerp(1, 0.35, P(t, 92.6, 0.8)) : 1;
      const back = t > 133.6 ? P(t, 133.6, 0.6) : 0;
      const active = P(t, S.select + 0.2, 0.6) * (1 - P(t, 92.6, 0.8));
      const run = P(t, S.read + 0.1, 1.6, R.linear);
      const out = P(t, S.read + 0.9, 0.9, R.linear);
      A.layer(ctx, a * (t > 133.6 ? lerp(0.35, 0.6, back) : dimT), (c) => drawTool(c, HUB.tool[0], HUB.tool[1], 1, 1, {
        active, run: run < 1 ? run : 0, out: out * (1 - P(t, 92.6, 0.8)),
        glow: P(t, S.trigger, 0.4) * (1 - P(t, S.giveBack + 0.6, 0.6)),
        nameHL: A.indicate(P(t, S.select + 0.3, 0.9, R.linear)),
      }));
      // status notes
      const idle = P(t, S.notRead + 1.4, 0.5) * (1 - P(t, 73.2, 0.5));
      A.drawText(ctx, B('未执行', 26, C.dim), HUB.tool[0] + 1.35, HUB.tool[1] + 0.62, { anchor: [0.5, 0.5], alpha: idle });
      const running = P(t, S.trigger + 0.05, 0.4) * (1 - P(t, S.giveBack + 0.2, 0.4));
      A.drawText(ctx, A.text('执行中' + '...'.slice(0, 1 + (Math.floor(t * 3) % 3)), { size: 26, weight: 800, color: C.tool }), HUB.tool[0] + 0.62, HUB.tool[1] + 0.68, { anchor: [0, 0.5], alpha: running });
      const sim = P(t, S.simulated + 0.05, 0.6) * (1 - P(t, 92.6, 0.6));
      const simL = T('模拟示意', 24, C.soft);
      const sp = [2.75, -3.62];
      A.stroke(ctx, A.rrect(sp[0], sp[1], simL.width + 0.34, 0.42, 0.21), { color: C.dim, width: 2, alpha: sim });
      A.drawText(ctx, simL, sp[0], sp[1], { anchor: [0.5, 0.5], alpha: sim });
    }

    // ============================================================ 5. hand the input to the model (56 - 64)
    {
      const ar = P(t, S.give, 0.6) * (1 - P(t, S.give + 2.1, 0.5));
      if (ar > 0) {
        const path = A.line(HUB.prog[0] - 0.75, HUB.prog[1], HUB.model[0] + 1.15, HUB.model[1]);
        A.arrow(ctx, path, { color: C.soft, width: 3.4, p: ar > 0 && t < S.give + 0.6 ? P(t, S.give, 0.6) : 1, alpha: ar });
      }
    }

    // ============================================================ 6. the generated message (60 - 97)
    const msgOn = t > S.genNext - 0.05 && t <= S.keepBoth + 1.05;
    if (msgOn) {
      const frame = P(t, S.genNext, 0.8);
      const solid = P(t, S.complete + 0.05, 0.9);
      const tag = P(t, S.complete + 0.35, 0.6);
      const n = typed(t);
      // message moves towards the program after "程序接收它"
      const mv = P(t, S.receive, 0.9);
      const sc = lerp(1, 0.72, mv);
      const cx = lerp(MSG.cx, 1.3, mv), cy = MSG.cy;
      // turns into the request record (92.35)
      const morph = P(t, S.keepBoth + 0.05, 1.0);
      const box = msgBox(1);
      const src = { cx, cy, w: MSG.w * sc, h: box.rawH * sc };
      const dst = { cx: 1.05, cy: 1.4, w: 4.3, h: 1.08 };
      const drawSrc = () => {
        at(ctx, cx, cy, sc, 1, () => {
          ctx.translate(-MSG.cx, -MSG.cy);
          drawMessage(ctx, t, { frame, solid, tag, n, cursor: P(t, S.genNext + 0.5, 0.3) * (1 - P(t, 70.0, 0.4)), live: true });
          // "此时，工具还没有读取录音"
          const L = msgLayout();
          const r = L.find('"/audio/meeting.wav"');
          if (r) {
            const bb = L.box(r[0], r[1]);
            const ox = MSG.cx - MSG.w / 2 + MSG.padX, oy = MSG.cy + box.rawH / 2 - 0.31;
            const hp = P(t, S.notRead + 0.1, 0.6) * (1 - P(t, 73.1, 0.5));
            A.stroke(ctx, A.rrect(ox + bb.cx, oy + bb.cy, bb.w + 0.16, bb.h + 0.1, 0.08), { color: C.ink, width: 2.4, b: hp, alpha: 1 - P(t, 73.1, 0.5) });
          }
        });
      };
      if (morph <= 0) drawSrc();
      else
        fadeTransform(ctx, morph, src, dst, drawSrc, () => drawRecordCard(ctx, 'req', dst.cx, dst.cy, 1, 1));
      // "生成中..." label
      const gen = P(t, S.genNext + 0.3, 0.4) * (1 - P(t, 69.8, 0.4));
      if (gen > 0) {
        const dots = '.'.repeat(1 + (Math.floor(t * 3) % 3));
        A.drawText(ctx, A.text('生成中' + dots, { size: 28, weight: 800, color: C.soft }), MSG.cx - MSG.w / 2, MSG.cy + box.rawH / 2 + 0.14, { anchor: [0, 1], alpha: gen });
      }
      // arrow model -> message, labelled "模型输出"
      const ao = P(t, S.genNext, 0.5) * (1 - P(t, S.receive, 0.5));
      if (ao > 0) {
        const path = A.line(HUB.model[0] + 1.05, HUB.model[1], MSG.cx - MSG.w / 2 - 0.12, MSG.cy);
        A.arrow(ctx, path, { color: C.soft, width: 3.4, p: P(t, S.genNext, 0.5), alpha: ao });
        A.drawText(ctx, B('模型输出', 26, C.soft), (HUB.model[0] + 1.05 + MSG.cx - MSG.w / 2) / 2, MSG.cy + 0.3, { anchor: [0.5, 0], write: P(t, S.isOutput + 0.05, 0.8, R.linear), alpha: ao });
      }
      // dashed pointer from the path to the (unread) recording
      const np = P(t, S.notRead + 0.5, 0.8) * (1 - P(t, 73.1, 0.5));
      if (np > 0) {
        const from = [-0.15, 0.05];
        const to = [HUB.rec[0] - 0.1, HUB.rec[1] + 0.7];
        A.arrow(ctx, A.cubic(from, [from[0], from[1] - 1.0], [to[0], to[1] + 1.0], to, 40), { color: C.soft, width: 3, p: np, dash: [12, 9], alpha: 1 - P(t, 73.1, 0.5), len: 18, wid: 17 });
        A.drawText(ctx, B('未读取', 26, C.red), HUB.rec[0] - 0.75, HUB.rec[1] + 0.05, { anchor: [1, 0.5], alpha: P(t, S.notRead + 1.1, 0.5) * (1 - P(t, 73.1, 0.5)) });
      }
      // message -> program arrow
      const mp = P(t, S.receive + 0.6, 0.45) * (1 - P(t, S.keepBoth, 0.5));
      if (mp > 0) {
        const path = A.line(cx + (MSG.w * sc) / 2 + 0.1, cy, HUB.prog[0] - 0.72, HUB.prog[1]);
        A.arrow(ctx, path, { color: C.tool, width: 3.6, p: mp, alpha: 1 - P(t, S.keepBoth, 0.5), len: 18, wid: 17 });
      }
    }

    // ============================================================ 7. program identifies the type and branches (80 - 92)
    {
      const tagFly = P(t, S.identify, 0.6);
      const out = P(t, S.keepBoth, 0.6);
      if (tagFly > 0 && out < 1) {
        const readout = [3.35, 2.15];
        const tagSrc = [1.3 - (MSG.w * 0.72) / 2 + 0.3 + 0.55, MSG.cy + (msgBox(1).rawH * 0.72) / 2];
        const p = arcPt(tagSrc, readout, tagFly, -0.5);
        const L = A.text([['类型：', { color: C.soft }], ['工具调用', { color: C.tool }]], { size: 28, weight: 800 });
        const a = (1 - out) * clamp(tagFly * 2);
        A.stroke(ctx, A.rrect(p[0], p[1], L.width + 0.4, 0.5, 0.12), { color: C.prog, width: 2.4, alpha: a * clamp(tagFly * 2 - 1) });
        A.drawText(ctx, L, p[0], p[1], { anchor: [0.5, 0.5], alpha: a, scale: lerp(0.7, 1, tagFly) });
        if (tagFly > 0.6) {
          const link = A.line(readout[0] + (L.width + 0.4) / 2, readout[1] - 0.05, HUB.prog[0] - 0.42, HUB.prog[1] + 0.48);
          A.stroke(ctx, link, { color: C.prog, width: 2.2, alpha: a * 0.7, b: P(t, S.identify + 0.4, 0.4), dash: [8, 7] });
        }
      }
      // two branches
      const br = P(t, S.branch, 0.6);
      if (br > 0 && out < 1) {
        const a = 1 - out;
        const up = A.line(HUB.prog[0], HUB.prog[1] + 0.66, HUB.prog[0], HUB.user[1] - 0.55);
        A.stroke(ctx, up, { color: C.dim, width: 3, b: br, alpha: a * 0.6 });
        A.drawText(ctx, T('回答', 26, C.dim), HUB.prog[0] + 0.25, (HUB.prog[1] + HUB.user[1]) / 2 + 0.25, { anchor: [0, 0.5], alpha: a * P(t, S.branch + 0.3, 0.4) });
        const down = A.line(HUB.prog[0], HUB.prog[1] - 0.66, HUB.prog[0], HUB.tool[1] + 0.52);
        A.stroke(ctx, down, { color: C.tool, width: 4, b: br, alpha: a });
        A.tip(ctx, HUB.prog[0], HUB.tool[1] + 0.5, 0, -1, { color: C.tool, alpha: a * clamp(br * 3 - 2), len: 18, wid: 17 });
        A.drawText(ctx, B('执行', 28, C.tool), HUB.prog[0] + 0.25, HUB.prog[1] - 1.1, { anchor: [0, 0.5], alpha: a * P(t, S.branch + 0.3, 0.4) });
        const fl = P(t, S.select, 0.9, R.linear);
        if (fl > 0 && fl < 1) A.passingFlash(ctx, down, fl, { color: C.yellow, width: 8, timeWidth: 0.6 });
      }
    }
    // user node (top right), appears with the branches
    {
      const a = P(t, S.branch + 0.1, 0.6) * hubFade * (1 - docMode);
      const bright = t > S.noNewQ - 0.3 ? P(t, S.noNewQ - 0.3, 0.6) : 0;
      drawUser(ctx, HUB.user[0], HUB.user[1], 0.95, a * lerp(0.45, 1, bright), { pulse: P(t, S.deliver + 1.35, 0.8, R.linear) });
    }

    // ============================================================ 8. parameters, execution, result (83 - 92)
    {
      // parameter copies fly into the tool
      const L = msgLayout();
      for (let j = 0; j < 4; j++) {
        const fly = P(t, S.pass + j * 0.12, 0.8);
        if (fly <= 0 || fly >= 1) continue;
        const line = L.lines[2 + j];
        const sx = 1.3 - (MSG.w * 0.72) / 2 + MSG.padX * 0.72 + 1.6;
        const sy = MSG.cy + (msgBox(1).rawH * 0.72) / 2 - 0.31 * 0.72 + line.baseline * 0.72 + 0.1;
        const p = arcPt([sx, sy], [HUB.tool[0] - 0.7, HUB.tool[1] + 0.2], fly, 0.6);
        const sub = A.text(line.glyphs.map((g) => g.ch).join('').trim(), { size: 32, font: 'mono', color: C.tool });
        A.drawText(ctx, sub, p[0], p[1], { anchor: [0.5, 0.5], scale: lerp(0.72, 0.25, fly), alpha: 1 - P(t, S.pass + j * 0.12 + 0.55, 0.25) });
      }
      // the recording is read: bars stream into the tool
      const rd = P(t, S.read, 1.2, R.linear);
      if (rd > 0 && rd < 1) {
        const rng = A.rng(7);
        for (let i = 0; i < 14; i++) {
          const ph = rd * 1.6 - i * 0.045;
          if (ph < 0 || ph > 1) continue;
          const x = lerp(HUB.rec[0] + 0.65, HUB.tool[0] - 1.25, ph);
          const h = (0.15 + 0.35 * rng()) * Math.sin(Math.PI * ph);
          A.stroke(ctx, A.line(x, HUB.tool[1] - h / 2, x, HUB.tool[1] + h / 2), { color: C.tool, width: 4, alpha: 0.9 });
        }
        A.stroke(ctx, A.line(HUB.rec[0] + 0.65, HUB.tool[1], HUB.tool[0] - 1.25, HUB.tool[1]), { color: C.tool, width: 2, alpha: 0.35 * Math.sin(Math.PI * rd) });
      }
      // the result card rises from the tool to the program
      const rise = P(t, S.giveBack, 1.1);
      const toCenter = P(t, S.keepBoth + 0.25, 1.1);
      if (rise > 0) {
        const p0 = [HUB.tool[0] + 1.0, HUB.tool[1] + 0.5];
        const p1 = [HUB.prog[0] + 1.0, HUB.prog[1] - 1.7];
        let p = lerpPt(p0, p1, rise);
        let s = lerp(0.25, 0.45, rise);
        p = lerpPt(p, [1.05, -0.15], toCenter);
        s = lerp(s, 1, toCenter);
        const shift = P(t, S.orgNext, 0.9);
        p = lerpPt(p, [2.25, -0.35], shift);
        s = lerp(s, 0.9, shift);
        const mvOut = P(t, S.addRes, 0.95);
        const target = nextRowPos(5);
        p = lerpPt(p, target, mvOut);
        if (mvOut < 1) {
          if (mvOut > 0) fadeTransform(ctx, mvOut, { cx: p[0], cy: p[1], w: 4.3 * s, h: 1.08 * s }, { cx: target[0], cy: target[1], w: 3.3 * 0.9, h: 0.62 * 0.9 }, () => drawRecordCard(ctx, 'res', p[0], p[1], s, 1, { idHL: idPulse(t) }), () => drawMiniCard(ctx, 'res', target[0], target[1], 0.9, 1));
          else drawRecordCard(ctx, 'res', p[0], p[1], s, clamp(rise * 3), { idHL: idPulse(t) });
        }
        // cyan return trace
        const tr = P(t, S.giveBack, 0.6) * (1 - P(t, S.received + 1.0, 0.6));
        if (tr > 0) A.stroke(ctx, A.line(HUB.tool[0] + 0.55, HUB.tool[1] + 0.48, HUB.prog[0] + 0.45, HUB.prog[1] - 0.48), { color: C.res, width: 3, b: P(t, S.giveBack, 1.1), alpha: tr * 0.8, dash: [10, 8] });
      }
    }

    // ============================================================ 9. pair request & result, next input (92 - 112)
    {
      // request record card: from the message (morph handled above) to row 5
      const mvReq = P(t, S.addReq, 0.95);
      const base = [1.05, 1.4];
      const shifted = lerpPt(base, [2.25, 1.15], P(t, S.orgNext, 0.9));
      if (t > S.keepBoth + 1.05 && mvReq < 1) {
        const target = nextRowPos(4);
        const sc = lerp(1, 0.9, P(t, S.orgNext, 0.9));
        if (mvReq > 0) fadeTransform(ctx, mvReq, { cx: shifted[0], cy: shifted[1], w: 4.3 * sc, h: 1.08 * sc }, { cx: target[0], cy: target[1], w: 3.3 * 0.9, h: 0.62 * 0.9 }, () => drawRecordCard(ctx, 'req', shifted[0], shifted[1], sc, 1, { idHL: idPulse(t) }), () => drawMiniCard(ctx, 'req', target[0], target[1], 0.9, 1));
        else drawRecordCard(ctx, 'req', shifted[0], shifted[1], sc, 1, { idHL: idPulse(t) });
      }
      // the result card shifts right too while the container opens
      // (position handled in section 8 via toCenter; shift here)
      // pairing bracket "同一次调用"
      const pr = P(t, S.pair, 0.7) * (1 - P(t, S.orgNext, 0.5));
      if (pr > 0) {
        const xL = 1.05 - 2.15 - 0.15;
        const br = A.brace([xL, -0.15], [xL, 1.4], 0.22);
        A.stroke(ctx, br, { color: C.ink, width: 3, b: pr });
        A.drawText(ctx, B('同一次调用', 28, C.ink), br.tip[0] - 0.15, br.tip[1], { anchor: [1, 0.5], alpha: P(t, S.pair + 0.3, 0.5) * (1 - P(t, S.orgNext, 0.5)) });
      }
      // next-input container
      const open = P(t, S.orgNext + 0.1, 0.9);
      const toDoc = P(t, 112.3, 0.8);
      if (open > 0 && toDoc < 1) {
        const a = 1 - toDoc;
        const cbox = A.rrect(-2.25, 0.25, 3.95, 5.05, 0.16);
        A.stroke(ctx, cbox, { color: C.soft, width: 2.6, b: open, alpha: a });
        const cf = P(t, S.addRes + 1.6, 1.1, R.linear);
        if (cf > 0 && cf < 1) A.passingFlash(ctx, cbox, cf, { color: '#FFFFFF', width: 6, timeWidth: 0.35 });
        const hdr = P(t, S.secondCall + 0.2, 0.6);
        A.drawText(ctx, B('下一次输入', 34, C.ink), -2.25, 3.1, { anchor: [0.5, 0.5], write: P(t, S.orgNext + 0.3, 0.9, R.linear), alpha: a * (1 - hdr) });
        A.drawText(ctx, B('第 2 次调用的输入', 34, C.yellow), -2.25, 3.1, { anchor: [0.5, 0.5], alpha: a * hdr });
        // rows 1-4 copied from the first-input thumbnail, each inside its own boundary
        for (let i = 0; i < 4; i++) {
          const k = P(t, S.keepBounds + i * 0.25, 0.8);
          if (k <= 0) continue;
          const target = nextRowPos(i);
          const src = blockCenter(doc1, i, thumb1[0], thumb1[1], 0.17);
          const p = lerpPt(src, target, k);
          const s = lerp(0.35, 1, k);
          at(ctx, p[0], p[1], s, a * clamp(k * 1.5), () => {
            A.stroke(ctx, A.rrect(0, 0, 3.3 * 0.9, 0.56, 0.1), { color: KIND[ROWS[i]].color, width: 2.4, alpha: 0.75 });
            drawIcon(ctx, ROWS[i], -1.12, 0, 0.82, 1);
            A.drawText(ctx, B(KIND[ROWS[i]].tag, 30, C.ink), -0.72, 0, { anchor: [0, 0.5] });
          });
        }
        // rows 5-6 (record cards) once they have arrived
        if (P(t, S.addReq, 0.95) >= 1) drawMiniCard(ctx, 'req', nextRowPos(4)[0], nextRowPos(4)[1], 0.9, a);
        if (P(t, S.addRes, 0.95) >= 1) drawMiniCard(ctx, 'res', nextRowPos(5)[0], nextRowPos(5)[1], 0.9, a);
        // pairing dots link
        const lk = P(t, S.addRes + 1.0, 0.6);
        if (lk > 0) {
          const xR = -2.25 + (3.3 * 0.9) / 2;
          const link = A.polyline([[xR, nextRowPos(4)[1]], [xR + 0.3, nextRowPos(4)[1]], [xR + 0.3, nextRowPos(5)[1]], [xR, nextRowPos(5)[1]]]);
          A.stroke(ctx, link, { color: C.soft, width: 2.6, b: lk, alpha: a });
        }
      }
      // the user did not ask again
      const nq = P(t, S.noNewQ, 0.7) * (1 - P(t, 112.3, 0.5));
      const uq = P(t, S.deliver + 1.3, 0.6) * (1 - P(t, 151.7, 0.5));
      const pa = Math.max(nq, P(t, S.deliver + 1.2, 0.6) * hubFade);
      if (pa > 0) {
        const px = 2.05, py = 3.1;
        const panel = A.rrect(px, py, 3.9, uq > 0 ? 1.25 : 0.95, 0.14);
        A.fill(ctx, panel, C.panel, pa);
        A.stroke(ctx, panel, { color: C.edge, width: 2.2, alpha: pa });
        const bub = T('整理成会议纪要', 24, '#081018');
        const by = py + (uq > 0 ? 0.28 : 0.13);
        const bw = bub.width + 0.36;
        A.fill(ctx, A.rrect(px + 1.85 - 0.15 - bw / 2, by, bw, 0.42, 0.14), C.user, pa);
        A.drawText(ctx, bub, px + 1.85 - 0.15 - bw / 2, by, { anchor: [0.5, 0.5], alpha: pa });
        const note = T('没有新的提问', 24, C.dim);
        A.drawText(ctx, note, px - 1.75, py - 0.22, { anchor: [0, 0.5], alpha: nq * (1 - uq) });
        if (uq > 0) {
          const rb = T('会议纪要 · 2 条', 24, C.ink);
          const rw = rb.width + 0.36;
          A.stroke(ctx, A.rrect(px - 1.75 + rw / 2, py - 0.25, rw, 0.42, 0.14), { color: C.ink, width: 2, alpha: uq });
          A.drawText(ctx, rb, px - 1.75 + rw / 2, py - 0.25, { anchor: [0.5, 0.5], alpha: uq });
        }
      }
    }

    // ============================================================ 10. the second complete input (112 - 137)
    const doc2 = DOC2();
    const D2 = { cx: 2.2, cy: -0.25 };
    if (t > 112.2 && t < 137.2) {
      const appear = P(t, 112.3, 0.8);
      const blockT = [S.kUser, S.kSys, S.kEnv, S.kTool, S.addCall, S.addResult];
      const bp = blockT.map((t0, i) => P(t, t0 + (i < 4 ? -0.1 : 0.25), 0.9, R.linear));
      const shrink = P(t, S.give2, 0.8);
      const travel = P(t, S.give2 + 0.75, 1.0);
      const into = P(t, S.give2 + 1.7, 0.4);
      const packetPos = [3.35, 0.55];
      let cx = lerp(D2.cx, packetPos[0], shrink), cy = lerp(D2.cy, packetPos[1], shrink);
      let s = lerp(1, 0.17, shrink);
      if (travel > 0) {
        cx = lerp(packetPos[0], HUB.model[0] + 0.15, travel);
        cy = packetPos[1] + 0.35 * Math.sin(Math.PI * travel);
      }
      s *= 1 - 0.75 * into;
      const keep = A.indicate(P(t, S.kKeep, 0.8, R.linear));
      const hl = [keep, keep, keep, keep, 0, 0];
      const idHL = A.indicate(P(t, S.addResult + 1.3, 1.1, R.linear));
      // placeholders announce the two records that will be appended
      const ph = P(t, 118.6, 0.8) * (1 - P(t, S.addResult + 0.6, 0.4));
      if (ph > 0 && shrink <= 0) {
        [4, 5].forEach((i, j) => {
          const b = doc2.blocks[i];
          const bw = doc2.width - 2 * DOC_STYLE.pad;
          const pA = ph * (1 - P(t, (j === 0 ? S.addCall : S.addResult) + 0.25, 0.4)) * P(t, 118.6 + j * 0.25, 0.6);
          if (pA <= 0) return;
          A.stroke(ctx, A.rrect(cx, cy + b.cy, bw, b.h, 0.1), { color: KIND[b.kind].color, width: 2.2, dash: [12, 10], alpha: 0.7 * pA, b: P(t, 118.6 + j * 0.25, 0.8) });
          A.drawText(ctx, B(j === 0 ? '待加入：请求记录' : '待加入：工具结果', 28, KIND[b.kind].color), cx, cy + b.cy, { anchor: [0.5, 0.5], alpha: 0.75 * pA });
        });
      }
      drawDoc(ctx, doc2, cx, cy, s, {
        alpha: appear * (1 - into), blocks: bp, frame: P(t, S.updated + 0.05, 0.8), flash: P(t, S.updated + 0.9, 1.0, R.linear), hl,
        header: B('第 2 次完整输入', 40, C.ink), headerP: P(t, S.updated + 0.2, 1.0, R.linear), headerAlpha: 1 - P(t, S.give2, 0.4),
      });
      // call_id highlight boxes in blocks 5 and 6
      if (idHL > 0 && shrink <= 0) {
        for (const i of [4, 5]) {
          const b = doc2.blocks[i];
          const x0 = cx - doc2.width / 2 + DOC_STYLE.pad + DOC_STYLE.tagX;
          const yy = cy + (b.cy + (b.subL.height + 0.08) / 2 - b.tagL.height / 2 - 0.08 - b.subL.height / 2);
          A.stroke(ctx, A.rrect(x0 + b.subL.width / 2, yy, b.subL.width + 0.18, b.subL.height + 0.14, 0.06), { color: C.yellow, width: 2.6, alpha: idHL });
        }
      }
      // braces: "原有信息" and "两条新记录"
      const bo = P(t, S.origNew, 0.7) * (1 - P(t, S.updated + 1.4, 0.6));
      if (bo > 0 && shrink <= 0) {
        const xL = cx - doc2.width / 2 - 0.15;
        const top = cy + doc2.blocks[0].cy + doc2.blocks[0].h / 2, mid = cy + doc2.blocks[3].cy - doc2.blocks[3].h / 2;
        const b1 = A.brace([xL, top], [xL, mid], 0.24);
        A.stroke(ctx, b1, { color: C.ink, width: 3, b: bo });
        A.drawText(ctx, B('原有信息', 30, C.ink), b1.tip[0] - 0.15, b1.tip[1], { anchor: [1, 0.5], alpha: bo });
        const t2 = cy + doc2.blocks[4].cy + doc2.blocks[4].h / 2, b2y = cy + doc2.blocks[5].cy - doc2.blocks[5].h / 2;
        const bo2 = P(t, S.origNew + 0.7, 0.7) * (1 - P(t, S.updated + 1.4, 0.6));
        const b2 = A.brace([xL, t2], [xL, b2y], 0.24);
        A.stroke(ctx, b2, { color: C.yellow, width: 3, b: bo2 });
        A.drawText(ctx, B('两条新记录', 30, C.yellow), b2.tip[0] - 0.15, b2.tip[1], { anchor: [1, 0.5], alpha: bo2 });
      }
      // icon copies from the compact rows (left column) into the new blocks
      const colA = P(t, 112.3, 0.8) * (1 - P(t, S.origNew - 0.6, 0.6));
      if (colA > 0) {
        // left column: the six compact rows, moved from the container
        const kinds = ['user', 'sys', 'env', 'tool', 'req', 'res'];
        kinds.forEach((kind, i) => {
          const from = nextRowPos(i);
          const to = [-5.25, 2.4 - i * 0.7];
          const k = P(t, 112.3, 0.8);
          const p = lerpPt(from, to, k);
          at(ctx, p[0], p[1], lerp(1, 0.8, k), colA, () => {
            if (i < 4) {
              A.stroke(ctx, A.rrect(0, 0, 3.3 * 0.9, 0.56, 0.1), { color: KIND[kind].color, width: 2.4, alpha: 0.75 });
              drawIcon(ctx, kind, -1.12, 0, 0.82, 1);
              A.drawText(ctx, B(KIND[kind].tag, 30, C.ink), -0.72, 0, { anchor: [0, 0.5] });
            } else {
              drawMiniCard(ctx, kind, 0, 0, 0.9, 1);
            }
          });
        });
      }
      blockT.forEach((t0, i) => {
        const fly = P(t, t0 - (i < 4 ? 0.35 : 0), 0.7);
        if (fly <= 0 || fly >= 1) return;
        const src = [-5.25 - 0.9, 2.4 - i * 0.7];
        const dst = blockTagPos(doc2, i, D2.cx, D2.cy, 1);
        const p = arcPt(src, [dst[0] - 0.35, dst[1]], fly, -0.4);
        drawIcon(ctx, ['user', 'sys', 'env', 'tool', 'req', 'res'][i], p[0], p[1], 0.8, 1 - P(t, t0 + 0.2, 0.2));
      });
    }
    // thumbnail of the second input
    {
      const a = P(t, S.thumb, 0.7) * hubFade;
      if (a > 0) {
        const rise = P(t, S.thumb - 0.1, 0.9);
        const pos = lerpPt([HUB.model[0], HUB.model[1] + 0.2], thumb1, rise);
        drawDoc(ctx, doc2, pos[0], pos[1], 0.15, { alpha: a, blocks: [1, 1, 1, 1, 1, 1], frame: 1 });
        A.drawText(ctx, T('第 2 次输入（含请求与结果）', 22, C.dim), thumb1[0], thumb1[1] - 0.55, { anchor: [0.5, 0], alpha: a * rise });
      }
      // arrow program -> model for the second call
      const ar = P(t, S.give2 + 0.5, 0.5) * (1 - P(t, S.give2 + 2.2, 0.5));
      if (ar > 0) {
        const path = A.line(HUB.prog[0] - 0.75, HUB.prog[1], HUB.model[0] + 1.15, HUB.model[1]);
        A.arrow(ctx, path, { color: C.soft, width: 3.4, p: P(t, S.give2 + 0.5, 0.5), alpha: ar });
      }
    }

    // ============================================================ 11. the answer (141 - 152)
    {
      const ap = P(t, S.genAnswer - 0.1, 0.8);
      if (ap > 0 && t < 152.4) {
        const toProg = P(t, S.deliver, 0.7);
        const toUser = P(t, S.deliver + 0.75, 0.75);
        let p = [0.2, 0.3];
        let s = 1;
        p = lerpPt(p, [HUB.prog[0] - 1.45, HUB.prog[1]], toProg);
        s = lerp(1, 0.32, toProg);
        p = arcPt(p, [HUB.user[0] - 1.2, HUB.user[1] - 0.05], toUser, -0.5);
        s = lerp(s, 0.18, toUser);
        const a = (1 - P(t, S.deliver + 1.4, 0.4)) * hubFade;
        drawMinutes(ctx, p[0], p[1], s, a, {
          draw: ap, title: P(t, S.genAnswer + 0.2, 0.8, R.linear),
          body: 18 * P(t, S.genAnswer + 0.9, 2.2, R.linear), note: P(t, S.genAnswer + 3.2, 0.6),
        });
        const ao = P(t, S.genAnswer - 0.2, 0.5) * (1 - P(t, S.deliver - 0.2, 0.4));
        if (ao > 0) {
          A.arrow(ctx, A.line(HUB.model[0] + 1.05, HUB.model[1], 0.2 - 1.95, 0.3), { color: C.soft, width: 3.4, p: ao, alpha: ao });
          A.drawText(ctx, B('给用户阅读', 26, C.soft), (HUB.model[0] + 1.05 + 0.2 - 1.95) / 2, 0.66, { anchor: [0.5, 1], alpha: P(t, S.genAnswer + 0.6, 0.6) * (1 - P(t, S.deliver - 0.2, 0.4)) });
        }
      }
    }

    // ============================================================ 12. comparison (151.8 - 159)
    if (t > 151.7) drawComparison(ctx, t);
  };

  // ---------------------------------------------------------------- comparison layout
  function compactInput(ctx, kinds, x, y, s, alpha, hlRes) {
    at(ctx, x, y, s, alpha, () => {
      const n = kinds.length;
      const step = 0.46;
      const top = ((n - 1) * step) / 2;
      kinds.forEach((kind, i) => {
        const yy = top - i * step;
        const glow = kind === 'res' ? hlRes : 0;
        if (kind === 'req' || kind === 'res') {
          const box = A.rrect(0.22, yy, 2.3, 0.38, 0.08);
          A.fill(ctx, box, mix(C.panel, KIND[kind].color, 0.1 + 0.25 * glow), 1);
          A.stroke(ctx, box, { color: KIND[kind].color, width: 2.2 + 2 * glow });
        }
        drawIcon(ctx, kind, -0.62, yy, 0.62, 1);
        A.drawText(ctx, B(KIND[kind].tag, 26, kind === 'req' || kind === 'res' ? KIND[kind].color : C.ink), -0.3, yy, { anchor: [0, 0.5] });
      });
      const h = (n - 1) * step + 0.62;
      const left = A.polyline([[-0.82, h / 2], [-0.98, h / 2], [-0.98, -h / 2], [-0.82, -h / 2]]);
      const right = A.polyline([[1.55, h / 2], [1.71, h / 2], [1.71, -h / 2], [1.55, -h / 2]]);
      A.stroke(ctx, left, { color: C.soft, width: 2.6 });
      A.stroke(ctx, right, { color: C.soft, width: 2.6 });
    });
  }

  function drawComparison(ctx, t) {
    const a1 = P(t, 152.0, 0.7);
    const a2 = P(t, 152.45, 0.7);
    const X = { input: -4.75, a1: [-2.55, -1.55], model: -0.3, a2: [0.95, 1.95], out: 3.85 };
    const rows = [
      { y: 2.05, a: a1, title: '第一次调用', titleY: 3.55, kinds: ['user', 'sys', 'env', 'tool'], caption: '给程序执行' },
      { y: -1.3, a: a2, title: '第二次调用', titleY: 0.62, kinds: ['user', 'sys', 'env', 'tool', 'req', 'res'], caption: '给人阅读' },
    ];
    const hlRes = A.indicate(P(t, S.resultIn + 0.05, 1.3, R.linear));
    const flash1 = P(t, S.resultIn + 0.45, 0.9, R.linear);
    const flash2 = P(t, S.cont + 0.1, 0.9, R.linear);
    rows.forEach((r, i) => {
      if (r.a <= 0) return;
      A.drawText(ctx, B(r.title, 34, C.ink), -6.85, r.titleY, { anchor: [0, 0.5], write: clamp(r.a * 1.2) });
      compactInput(ctx, r.kinds, X.input, r.y, 1.1, r.a, i === 1 ? hlRes : 0);
      const arrow1 = A.line(X.a1[0], r.y, X.a1[1], r.y);
      A.arrow(ctx, arrow1, { color: C.soft, width: 3.6, p: r.a, alpha: r.a });
      drawModel(ctx, X.model, r.y + 0.12, 0.82, r.a, null, 1);
      const arrow2 = A.line(X.a2[0], r.y, X.a2[1], r.y);
      A.arrow(ctx, arrow2, { color: C.soft, width: 3.6, p: r.a, alpha: r.a });
      if (i === 1) {
        if (flash1 > 0 && flash1 < 1) A.passingFlash(ctx, arrow1, flash1, { color: C.res, width: 10, timeWidth: 0.9 });
        if (flash2 > 0 && flash2 < 1) A.passingFlash(ctx, arrow2, flash2, { color: C.res, width: 10, timeWidth: 0.9 });
        const glow = A.indicate(P(t, S.cont + 0.7, 1.1, R.linear));
        drawMinutes(ctx, X.out, r.y + 0.12, 0.6 * (1 + 0.06 * glow), r.a, {});
        A.drawText(ctx, B(r.caption, 32, mix(C.ink, C.yellow, glow)), X.out, r.y - 0.98, { anchor: [0.5, 0], alpha: r.a });
      } else {
        const card = A.rrect(X.out, r.y, 3.4, 0.7, 0.16);
        A.fill(ctx, card, mix(C.panel, C.tool, 0.08), r.a);
        A.stroke(ctx, card, { color: C.tool, width: 3, alpha: r.a });
        A.drawText(ctx, M('transcribe_audio', 28, C.tool), X.out, r.y, { anchor: [0.5, 0.5], alpha: r.a });
        A.drawText(ctx, B('工具请求', 28, C.tool), X.out, r.y + 0.5, { anchor: [0.5, 1], alpha: r.a });
        A.drawText(ctx, B(r.caption, 32, C.ink), X.out, r.y - 0.52, { anchor: [0.5, 0], alpha: r.a });
      }
    });
    const same = P(t, 152.9, 0.6);
    A.drawText(ctx, T('同一个模型', 28, C.dim), X.model, 0.4, { anchor: [0.5, 0.5], alpha: same });
    const s1 = B('用户问了一次，', 52, C.ink), s2 = B('模型调用了两次。', 52, C.ink);
    const total = s1.width + s2.width;
    const x0 = -total / 2;
    A.drawText(ctx, s1, x0, -3.48, { anchor: [0, 0.5], write: P(t, S.once, 0.95, R.linear) });
    A.drawText(ctx, s2, x0 + s1.width, -3.48, { anchor: [0, 0.5], write: P(t, S.twice, 1.0, R.linear) });
  }
})(typeof window !== 'undefined' ? window : globalThis);
