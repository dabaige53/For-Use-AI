/* AI 的输入与输出 · 网页动画引擎
 *
 * A tiny, deterministic, Manim-flavoured 2D engine on <canvas>.
 * Every frame is a pure function of time t (seconds), so the page can be
 * scrubbed freely and the renderer can export frame i at t = i / fps.
 *
 * World units follow ManimGL: the frame is 14.22 x 8 units, origin at the
 * centre, y pointing up.  Sizes given in "px" refer to a 1080p frame.
 */
(function (root) {
  'use strict';
  const A = (root.AIIO = root.AIIO || {});

  // ------------------------------------------------------------------ constants
  A.W = 1920;
  A.H = 1080;
  A.FH = 8;
  A.FW = (8 * 16) / 9;
  A.PX = A.H / A.FH; // px per unit at the default zoom
  const u = (A.u = (px) => px / A.PX); // px (1080p) -> world units

  // ------------------------------------------------------------------ math
  const clamp = (A.clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x));
  const lerp = (A.lerp = (a, b, t) => a + (b - a) * t);
  A.invLerp = (a, b, x) => (b === a ? 0 : (x - a) / (b - a));
  A.lerp2 = (p, q, t) => [lerp(p[0], q[0], t), lerp(p[1], q[1], t)];

  // ManimGL rate functions
  const R = (A.rate = {});
  R.linear = (t) => clamp(t);
  R.smooth = (t) => {
    t = clamp(t);
    const s = 1 - t;
    return t * t * t * (10 * s * s + 5 * s * t + t * t);
  };
  R.rushInto = (t) => 2 * R.smooth(0.5 * clamp(t));
  R.rushFrom = (t) => 2 * R.smooth(0.5 * (clamp(t) + 1)) - 1;
  R.slowInto = (t) => Math.sqrt(1 - (1 - clamp(t)) ** 2);
  R.doubleSmooth = (t) => (t < 0.5 ? 0.5 * R.smooth(2 * t) : 0.5 * (1 + R.smooth(2 * t - 1)));
  R.thereAndBack = (t) => R.smooth(t < 0.5 ? 2 * t : 2 * (1 - t));
  R.thereAndBackWithPause = (t, pause = 1 / 3) => {
    const a = 2 / (1 - pause);
    if (t < 0.5 - pause / 2) return R.smooth(a * t);
    if (t < 0.5 + pause / 2) return 1;
    return R.smooth(a - a * t);
  };
  const bez = (vals, t) => {
    // de Casteljau on scalars
    const v = vals.slice();
    for (let k = v.length - 1; k > 0; k--) for (let i = 0; i < k; i++) v[i] = lerp(v[i], v[i + 1], t);
    return v[0];
  };
  R.overshoot = (t) => bez([0, 0, 1.6, 1.6, 1, 1], clamp(t));
  R.easeOutBack = (t) => {
    if (t <= 0) return 0;
    if (t >= 1) return 1;
    const c1 = 1.70158, c3 = c1 + 1;
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2;
  };

  /** Progress of an animation that starts at t0 and lasts dur seconds. */
  A.prog = (t, t0, dur, rate = R.smooth) => rate(dur <= 0 ? (t >= t0 ? 1 : 0) : (t - t0) / dur);

  /** LaggedStart: sub-progress of item i (of n) for group progress p. */
  A.lag = (p, i, n, ratio) => {
    const total = 1 + ratio * Math.max(0, n - 1);
    return clamp(p * total - i * ratio);
  };

  /** Interpolate numbers, arrays or flat objects. */
  const interp = (A.interp = (a, b, t) => {
    if (typeof a === 'number') return lerp(a, b, t);
    if (Array.isArray(a)) return a.map((v, i) => interp(v, b[i], t));
    if (a && typeof a === 'object') {
      const o = {};
      for (const k in a) o[k] = k in b ? interp(a[k], b[k], t) : a[k];
      for (const k in b) if (!(k in o)) o[k] = b[k];
      return o;
    }
    return t < 0.5 ? a : b;
  });

  /**
   * Keyframes: frames = [[time, value, rate?], ...] (sorted).  The segment that
   * arrives at a keyframe uses that keyframe's rate (default smooth).  Before
   * the first and after the last keyframe the value is held.
   */
  A.kf = (t, frames) => {
    if (t <= frames[0][0]) return frames[0][1];
    for (let i = 1; i < frames.length; i++) {
      const [t1, v1, rate] = frames[i];
      if (t <= t1) {
        const [t0, v0] = frames[i - 1];
        const r = rate || R.smooth;
        return interp(v0, v1, r(t1 === t0 ? 1 : (t - t0) / (t1 - t0)));
      }
    }
    return frames[frames.length - 1][1];
  };

  /** Deterministic PRNG (mulberry32). */
  A.rng = (seed) => {
    let s = seed >>> 0;
    return () => {
      s = (s + 0x6d2b79f5) >>> 0;
      let r = Math.imul(s ^ (s >>> 15), 1 | s);
      r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
      return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
    };
  };

  // ------------------------------------------------------------------ colour
  const colCache = new Map();
  const col = (A.col = (hex) => {
    let c = colCache.get(hex);
    if (!c) {
      const h = hex.replace('#', '');
      c = [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
      colCache.set(hex, c);
    }
    return c;
  });
  const hex2 = (v) => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, '0');
  A.mix = (a, b, t) => {
    if (t <= 0) return a;
    if (t >= 1) return b;
    const p = col(a), q = col(b);
    return '#' + hex2(lerp(p[0], q[0], t)) + hex2(lerp(p[1], q[1], t)) + hex2(lerp(p[2], q[2], t));
  };
  A.rgba = (hex, a = 1) => {
    const c = col(hex);
    return `rgba(${c[0]},${c[1]},${c[2]},${clamp(a)})`;
  };

  // ------------------------------------------------------------------ camera / frame
  /** Prepare a frame: clear to black and install the world transform. */
  A.beginFrame = (ctx, cam = { x: 0, y: 0, h: A.FH }) => {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, A.W, A.H);
    const s = A.H / cam.h;
    ctx.setTransform(s, 0, 0, -s, A.W / 2 - cam.x * s, A.H / 2 + cam.y * s);
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    A._cam = cam;
  };

  /** Run fn inside a local transform (translate, uniform scale, rotation). */
  A.group = (ctx, { x = 0, y = 0, s = 1, rot = 0, alpha = 1 }, fn) => {
    if (alpha <= 0.001 || s <= 1e-4) return;
    ctx.save();
    ctx.translate(x, y);
    if (rot) ctx.rotate(rot);
    if (s !== 1) ctx.scale(s, s);
    ctx.globalAlpha *= alpha;
    fn();
    ctx.restore();
  };

  /**
   * Group opacity: draw fn into an offscreen layer, then composite it with
   * `alpha`, so overlapping parts of a dimmed object do not show through.
   */
  let layerCanvas = null;
  A.layer = (ctx, alpha, fn) => {
    if (alpha <= 0.002) return;
    if (alpha >= 0.998) {
      fn(ctx);
      return;
    }
    if (!layerCanvas) {
      layerCanvas = typeof OffscreenCanvas !== 'undefined' ? new OffscreenCanvas(A.W, A.H) : root.document.createElement('canvas');
      layerCanvas.width = A.W;
      layerCanvas.height = A.H;
    }
    const lc = layerCanvas.getContext('2d');
    lc.setTransform(1, 0, 0, 1, 0, 0);
    lc.clearRect(0, 0, A.W, A.H);
    lc.setTransform(ctx.getTransform());
    lc.globalAlpha = 1;
    lc.lineJoin = 'round';
    lc.lineCap = 'round';
    fn(lc);
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalAlpha *= alpha;
    ctx.drawImage(layerCanvas, 0, 0);
    ctx.restore();
  };

  // ------------------------------------------------------------------ polylines
  /** Polyline with cached arc length, used for ShowCreation-style drawing. */
  class Poly {
    constructor(pts, closed = false) {
      if (closed && pts.length > 1) {
        const a = pts[0], b = pts[pts.length - 1];
        if (a[0] !== b[0] || a[1] !== b[1]) pts = pts.concat([[a[0], a[1]]]);
      }
      this.pts = pts;
      this.closed = closed;
      const cum = new Float64Array(pts.length);
      for (let i = 1; i < pts.length; i++) {
        cum[i] = cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      }
      this.cum = cum;
      this.len = cum[pts.length - 1] || 0;
    }
    /** Point and tangent at arc-length fraction f. */
    at(f) {
      const L = clamp(f) * this.len, cum = this.cum, pts = this.pts;
      let i = 1;
      while (i < pts.length - 1 && cum[i] < L) i++;
      const seg = cum[i] - cum[i - 1] || 1;
      const k = clamp((L - cum[i - 1]) / seg);
      const p = pts[i - 1], q = pts[i];
      return { x: lerp(p[0], q[0], k), y: lerp(p[1], q[1], k), dx: (q[0] - p[0]) / seg, dy: (q[1] - p[1]) / seg };
    }
    /** Trace the sub-path between fractions a and b into ctx (no stroke). */
    trace(ctx, a = 0, b = 1) {
      const pts = this.pts;
      if (pts.length < 2 || b <= a) return;
      if (a <= 0 && b >= 1) {
        ctx.moveTo(pts[0][0], pts[0][1]);
        for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
        if (this.closed) ctx.closePath();
        return;
      }
      const La = a * this.len, Lb = b * this.len, cum = this.cum;
      const s = this.at(a);
      ctx.moveTo(s.x, s.y);
      for (let i = 1; i < pts.length; i++) {
        if (cum[i] <= La) continue;
        if (cum[i] >= Lb) break;
        ctx.lineTo(pts[i][0], pts[i][1]);
      }
      const e = this.at(b);
      ctx.lineTo(e.x, e.y);
    }
    shifted(dx, dy) {
      return new Poly(this.pts.map((p) => [p[0] + dx, p[1] + dy]), this.closed);
    }
  }
  A.Poly = Poly;

  const sampleCubic = (p0, p1, p2, p3, n, out) => {
    for (let i = 1; i <= n; i++) {
      const t = i / n, s = 1 - t;
      out.push([
        s * s * s * p0[0] + 3 * s * s * t * p1[0] + 3 * s * t * t * p2[0] + t * t * t * p3[0],
        s * s * s * p0[1] + 3 * s * s * t * p1[1] + 3 * s * t * t * p2[1] + t * t * t * p3[1],
      ]);
    }
  };
  A.cubic = (p0, p1, p2, p3, n = 40) => {
    const out = [p0.slice()];
    sampleCubic(p0, p1, p2, p3, n, out);
    return new Poly(out);
  };
  A.line = (x0, y0, x1, y1) => new Poly([[x0, y0], [x1, y1]]);
  A.polyline = (pts, closed = false) => new Poly(pts.map((p) => p.slice()), closed);

  /** Circular arc from p to q bulging by `angle` (ManimGL path_arc). */
  A.arcBetween = (p, q, angle, n = 48) => {
    if (Math.abs(angle) < 1e-4) return A.line(p[0], p[1], q[0], q[1]);
    const mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2;
    const dx = q[0] - p[0], dy = q[1] - p[1];
    const d = Math.hypot(dx, dy);
    const r = d / (2 * Math.sin(angle / 2));
    const h = r * Math.cos(angle / 2);
    // centre lies to the left of p->q for positive angle
    const cx = mx - (dy / d) * h, cy = my + (dx / d) * h;
    const a0 = Math.atan2(p[1] - cy, p[0] - cx);
    const out = [];
    for (let i = 0; i <= n; i++) {
      const a = a0 + (angle * i) / n;
      out.push([cx + Math.abs(r) * Math.cos(a), cy + Math.abs(r) * Math.sin(a)]);
    }
    out[0] = p.slice();
    out[n] = q.slice();
    return new Poly(out);
  };

  /** Rounded rectangle, traced clockwise from the top-left corner. */
  A.rrect = (cx, cy, w, h, r = 0.12, n = 8) => {
    r = Math.min(r, w / 2, h / 2);
    const x0 = cx - w / 2, x1 = cx + w / 2, y0 = cy - h / 2, y1 = cy + h / 2;
    const pts = [];
    const corner = (ox, oy, a0) => {
      for (let i = 0; i <= n; i++) {
        const a = a0 - (Math.PI / 2) * (i / n);
        pts.push([ox + r * Math.cos(a), oy + r * Math.sin(a)]);
      }
    };
    corner(x0 + r, y1 - r, Math.PI); // top-left: from left going to top
    corner(x1 - r, y1 - r, Math.PI / 2);
    corner(x1 - r, y0 + r, 0);
    corner(x0 + r, y0 + r, -Math.PI / 2);
    return new Poly(pts, true);
  };

  A.circle = (cx, cy, r, start = Math.PI / 2, n = 72) => {
    const pts = [];
    for (let i = 0; i <= n; i++) {
      const a = start - (2 * Math.PI * i) / n;
      pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]);
    }
    return new Poly(pts, true);
  };

  /** Curly brace from p to q; the tip points to the right of p->q. */
  A.brace = (p, q, depth = 0.22) => {
    const dx = q[0] - p[0], dy = q[1] - p[1];
    const L = Math.hypot(dx, dy) || 1;
    const ux = dx / L, uy = dy / L; // along
    const nx = uy, ny = -ux; // normal (right side)
    const P = (s, o) => [p[0] + ux * s + nx * o, p[1] + uy * s + ny * o];
    const d = depth, m = L / 2;
    const out = [P(0, 0)];
    sampleCubic(P(0, 0), P(0, d * 0.55), P(Math.min(d * 0.6, m * 0.4), d * 0.5), P(Math.min(d, m * 0.45), d * 0.5), 14, out);
    out.push(P(m - Math.min(d, m * 0.45), d * 0.5));
    sampleCubic(P(m - Math.min(d, m * 0.45), d * 0.5), P(m - d * 0.35, d * 0.5), P(m, d * 0.6), P(m, d), 12, out);
    sampleCubic(P(m, d), P(m, d * 0.6), P(m + d * 0.35, d * 0.5), P(m + Math.min(d, m * 0.45), d * 0.5), 12, out);
    out.push(P(L - Math.min(d, m * 0.45), d * 0.5));
    sampleCubic(P(L - Math.min(d, m * 0.45), d * 0.5), P(L - Math.min(d * 0.6, m * 0.4), d * 0.5), P(L, d * 0.55), P(L, 0), 14, out);
    const poly = new Poly(out);
    poly.tip = P(m, d);
    poly.normal = [nx, ny];
    return poly;
  };

  // ------------------------------------------------------------------ stroking
  /**
   * Stroke a Poly.  opts: color, width (px), alpha, a/b (sub-range, for
   * ShowCreation), dash ([on, off] px), cap.
   */
  A.stroke = (ctx, poly, opts = {}) => {
    const { color = '#ffffff', width = 3, alpha = 1, a = 0, b = 1, dash = null, dashOffset = 0, cap = 'round' } = opts;
    if (alpha <= 0.002 || b <= a) return;
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.strokeStyle = color;
    ctx.lineWidth = u(width);
    ctx.lineCap = cap;
    if (dash) {
      ctx.setLineDash(dash.map(u));
      ctx.lineDashOffset = u(dashOffset);
    }
    ctx.beginPath();
    poly.trace(ctx, a, b);
    ctx.stroke();
    ctx.restore();
  };

  A.fill = (ctx, poly, color, alpha = 1) => {
    if (alpha <= 0.002) return;
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.fillStyle = color;
    ctx.beginPath();
    poly.trace(ctx);
    ctx.fill();
    ctx.restore();
  };

  /**
   * ShowPassingFlash: a bright segment travelling along the poly.
   * p in [0,1]; timeWidth is the segment length as a fraction of the path.
   */
  A.passingFlash = (ctx, poly, p, opts = {}) => {
    const { timeWidth = 0.3, color = '#ffffff', width = 4, alpha = 1 } = opts;
    if (p <= 0 || p >= 1) return;
    const head = p * (1 + timeWidth);
    const tail = head - timeWidth;
    const n = 8;
    for (let i = 0; i < n; i++) {
      const s0 = lerp(tail, head, i / n), s1 = lerp(tail, head, (i + 1) / n);
      const a = clamp(s0), b = clamp(s1);
      if (b <= a) continue;
      const k = (i + 0.5) / n; // thin at the tail, thick at the head
      A.stroke(ctx, poly, { color, width: width * (0.25 + 0.75 * k), alpha: alpha * (0.35 + 0.65 * k), a, b });
    }
  };

  /** Arrow head (filled triangle) at point (x, y) pointing along (dx, dy). */
  A.tip = (ctx, x, y, dx, dy, opts = {}) => {
    const { color = '#ffffff', len = 22, wid = 20, alpha = 1, scale = 1 } = opts;
    if (alpha <= 0.002 || scale <= 0.01) return;
    const L = Math.hypot(dx, dy) || 1;
    const ux = dx / L, uy = dy / L;
    const l = u(len) * scale, w = u(wid) * scale;
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x - ux * l - uy * w / 2, y - uy * l + ux * w / 2);
    ctx.lineTo(x - ux * l * 0.82, y - uy * l * 0.82);
    ctx.lineTo(x - ux * l + uy * w / 2, y - uy * l - ux * w / 2);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  };

  /** GrowArrow along a poly: progress p grows the shaft and moves the tip. */
  A.arrow = (ctx, poly, opts = {}) => {
    const { p = 1, color = '#ffffff', width = 4, alpha = 1, len = 22, wid = 20, a = 0, dash = null } = opts;
    if (p <= 0.001 || alpha <= 0.002) return;
    const endF = clamp(p);
    const tipLen = u(len);
    const back = Math.min(1, (tipLen * 0.7) / Math.max(poly.len * endF, 1e-6));
    A.stroke(ctx, poly, { color, width, alpha, a, b: endF * (1 - back * 0.98) + 1e-6, dash });
    const e = poly.at(endF);
    A.tip(ctx, e.x, e.y, e.dx, e.dy, { color, len, wid, alpha, scale: clamp(p * 3) });
  };

  // ------------------------------------------------------------------ fonts & text
  A.fonts = {};
  const b64ToBuffer = (b64) => {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return bytes.buffer;
  };

  /** Parse the embedded fonts; also register them for DOM text (subtitles). */
  A.loadFonts = async () => {
    const data = root.AIIO_FONTS || {};
    for (const key of Object.keys(data)) {
      const buf = b64ToBuffer(data[key]);
      A.fonts[key] = root.opentype.parse(buf);
      if (root.FontFace && root.document) {
        try {
          const face = new root.FontFace('AIIO-' + key, buf.slice(0));
          await face.load();
          root.document.fonts.add(face);
        } catch (err) {
          /* DOM subtitles fall back to system fonts */
        }
      }
    }
    A.missingGlyphs = new Set();
  };

  const glyphCache = new Map();
  /** Path2D (font units, y up) and flattened contours of a glyph. */
  const glyphInfo = (font, fontKey, glyph) => {
    const key = fontKey + ':' + glyph.index;
    let info = glyphCache.get(key);
    if (info) return info;
    const cmds = glyph.path.commands;
    const path = new Path2D();
    const contours = [];
    let cur = null, last = [0, 0], start = [0, 0];
    for (const c of cmds) {
      if (c.type === 'M') {
        path.moveTo(c.x, c.y);
        cur = [[c.x, c.y]];
        contours.push(cur);
        last = [c.x, c.y];
        start = last;
      } else if (c.type === 'L') {
        path.lineTo(c.x, c.y);
        cur.push([c.x, c.y]);
        last = [c.x, c.y];
      } else if (c.type === 'Q') {
        path.quadraticCurveTo(c.x1, c.y1, c.x, c.y);
        const p0 = last;
        for (let i = 1; i <= 6; i++) {
          const t = i / 6, s = 1 - t;
          cur.push([s * s * p0[0] + 2 * s * t * c.x1 + t * t * c.x, s * s * p0[1] + 2 * s * t * c.y1 + t * t * c.y]);
        }
        last = [c.x, c.y];
      } else if (c.type === 'C') {
        path.bezierCurveTo(c.x1, c.y1, c.x2, c.y2, c.x, c.y);
        sampleCubic(last, [c.x1, c.y1], [c.x2, c.y2], [c.x, c.y], 8, cur);
        last = [c.x, c.y];
      } else if (c.type === 'Z') {
        path.closePath();
        if (cur) cur.push(start.slice());
      }
    }
    const polys = contours.filter((c) => c.length > 1).map((c) => new Poly(c));
    const total = polys.reduce((s, p) => s + p.len, 0);
    info = { path, polys, total };
    glyphCache.set(key, info);
    return info;
  };

  const isCJK = (ch) => /[⺀-鿿　-〿＀-￯—…“”‘’]/.test(ch);

  /**
   * Lay out text.  content is a string or a list of [string, style] runs.
   * opts: size (px), font ('serif' | 'mono'), weight (600/800), color,
   * lineHeight (multiple of size), maxWidth (px), align ('left'|'center'|'right'),
   * tracking (em).  A run style may override color, font, weight, size.
   */
  const layoutCache = new Map();
  A.text = (content, opts = {}) => {
    const key = JSON.stringify([content, opts]);
    const hit = layoutCache.get(key);
    if (hit) return hit;
    const base = Object.assign({ size: 40, font: 'serif', weight: 600, color: '#E8E8E8', lineHeight: 1.45, align: 'left', tracking: 0 }, opts);
    const runs = typeof content === 'string' ? [[content, {}]] : content;
    const chars = [];
    for (const [str, style] of runs) {
      const st = Object.assign({}, base, style || {});
      for (const ch of Array.from(str)) chars.push({ ch, st });
    }
    const pickFont = (ch, st) => {
      const serifKey = 'serif' + st.weight;
      if (st.font === 'mono' && !isCJK(ch) && A.fonts.mono && A.fonts.mono.charToGlyphIndex(ch)) return 'mono';
      return A.fonts[serifKey] ? serifKey : Object.keys(A.fonts).find((k) => k.startsWith('serif'));
    };
    // measure + wrap (CJK may break anywhere; latin words stay together)
    const isWord = (ch) => /[A-Za-z0-9_\-./"'@]/.test(ch);
    const lines = [[]];
    let x = 0;
    const maxW = base.maxWidth ? u(base.maxWidth) : Infinity;
    const placed = [];
    for (let i = 0; i < chars.length; i++) {
      const { ch, st } = chars[i];
      if (ch === '\n') {
        lines.push([]);
        x = 0;
        continue;
      }
      const fk = pickFont(ch, st);
      const font = A.fonts[fk];
      const glyph = font.charToGlyph(ch);
      if (!glyph || glyph.index === 0) A.missingGlyphs && A.missingGlyphs.add(ch);
      const size = u(st.size);
      const scale = size / font.unitsPerEm;
      const adv = glyph.advanceWidth * scale + st.tracking * size;
      const line = lines[lines.length - 1];
      if (x + adv > maxW && line.length && ch !== ' ' && !/[，。、：；？！）》”’,.;:!?)\]]/.test(ch)) {
        let k = line.length;
        if (isWord(ch)) {
          while (k > 0 && isWord(line[k - 1].ch)) k--;
          if (k === 0) k = line.length;
        }
        const moved = line.splice(k);
        lines.push(moved);
        let nx = 0;
        for (const g of moved) {
          g.x = nx;
          nx += g.adv;
        }
        x = nx;
      }
      const g = { ch, st, fk, glyph, size, scale, adv, x, index: placed.length };
      placed.push(g);
      lines[lines.length - 1].push(g);
      x += adv;
    }
    const sizeU = u(base.size);
    const lh = sizeU * base.lineHeight;
    let width = 0;
    const lineInfo = lines.map((ln, k) => {
      let w = 0;
      for (const g of ln) w = Math.max(w, g.x + g.adv);
      // trailing spaces do not count
      for (let j = ln.length - 1; j >= 0 && ln[j].ch === ' '; j--) w = Math.min(w, ln[j].x);
      width = Math.max(width, w);
      return { glyphs: ln, w, baseline: -(0.88 * sizeU) - k * lh };
    });
    for (const li of lineInfo) {
      const off = base.align === 'center' ? (width - li.w) / 2 : base.align === 'right' ? width - li.w : 0;
      for (const g of li.glyphs) {
        g.x += off;
        g.y = li.baseline;
      }
    }
    const height = sizeU + (lineInfo.length - 1) * lh;
    const layout = { glyphs: placed, lines: lineInfo, width, height, size: sizeU, opts: base, text: chars.map((c) => c.ch).join('') };
    layout.find = (sub, occurrence = 0) => {
      const txt = placed.map((g) => g.ch).join('');
      let at = -1;
      for (let k = 0; k <= occurrence; k++) at = txt.indexOf(sub, at + 1);
      return at < 0 ? null : [at, at + Array.from(sub).length];
    };
    /** Bounding box (layout coords: x right, y up from the top edge) of glyphs [i0, i1). */
    layout.box = (i0 = 0, i1 = placed.length) => {
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      for (let i = i0; i < i1; i++) {
        const g = placed[i];
        x0 = Math.min(x0, g.x);
        x1 = Math.max(x1, g.x + g.adv);
        y0 = Math.min(y0, g.y - 0.12 * g.size);
        y1 = Math.max(y1, g.y + 0.88 * g.size);
      }
      return { x0, x1, y0, y1, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, w: x1 - x0, h: y1 - y0 };
    };
    layoutCache.set(key, layout);
    return layout;
  };

  /** World-space origin (top-left of the layout box) for an anchor. */
  A.textOrigin = (L, x, y, anchor = [0, 0], s = 1) => [x - anchor[0] * L.width * s, y + anchor[1] * L.height * s];

  /**
   * Draw a text layout.
   * opts: anchor [ax, ay] (0..1 of the box; [0,0] = top-left), scale, alpha,
   * color (override all), colorFn(i, g) -> colour, alphaFn(i, g) -> 0..1,
   * write (0..1, Write animation), reveal (number of glyphs, typewriter),
   * lag (lag ratio for write).
   */
  A.drawText = (ctx, L, x, y, opts = {}) => {
    const { anchor = [0, 0], scale = 1, alpha = 1, color = null, colorFn = null, alphaFn = null, write = null, reveal = null, lag = null } = opts;
    if (alpha <= 0.002 || !L.glyphs.length) return;
    const [ox, oy] = A.textOrigin(L, x, y, anchor, scale);
    const n = L.glyphs.length;
    const lagRatio = lag != null ? lag : Math.min(4 / Math.max(1, n), 0.2);
    ctx.save();
    ctx.translate(ox, oy);
    if (scale !== 1) ctx.scale(scale, scale);
    // Level of detail: tiny text (thumbnails) is drawn as soft bars.
    const pxPerUnit = Math.hypot(ctx.getTransform().a, ctx.getTransform().b);
    if (L.size * pxPerUnit < (opts.lodPx || 8)) {
      for (const li of L.lines) {
        if (!li.glyphs.length) continue;
        let a = alpha;
        if (reveal != null) a *= clamp(reveal - li.glyphs[0].index);
        if (write != null) a *= clamp(write * 1.5);
        const g0 = li.glyphs[0];
        const c = color || (colorFn && colorFn(g0.index, g0)) || g0.st.color;
        ctx.save();
        ctx.globalAlpha *= a * 0.75;
        ctx.fillStyle = c;
        const h = L.size * 0.55;
        ctx.fillRect(g0.x, li.baseline + 0.05 * L.size, li.w - g0.x, h);
        ctx.restore();
      }
      ctx.restore();
      return;
    }
    for (let i = 0; i < n; i++) {
      const g = L.glyphs[i];
      if (g.ch === ' ' || g.ch === '　') continue;
      let a = alpha;
      if (alphaFn) a *= alphaFn(i, g);
      if (reveal != null) a *= clamp(reveal - i);
      if (a <= 0.002) continue;
      const c = color || (colorFn && colorFn(i, g)) || g.st.color;
      const font = A.fonts[g.fk];
      const info = glyphInfo(font, g.fk, g.glyph);
      ctx.save();
      ctx.translate(g.x, g.y);
      ctx.scale(g.scale, g.scale);
      if (write == null || write >= 1) {
        ctx.globalAlpha *= a;
        ctx.fillStyle = c;
        ctx.fill(info.path);
      } else {
        const sub = A.lag(write, i, n, lagRatio);
        if (sub > 0) {
          const sw = clamp(g.size * A.PX * 0.05, 1.4, 3.0) / A.PX / g.scale;
          ctx.strokeStyle = c;
          ctx.lineWidth = sw;
          if (sub < 0.5) {
            // draw the outline progressively, contour by contour
            const target = (sub / 0.5) * info.total;
            let acc = 0;
            ctx.globalAlpha *= a;
            ctx.beginPath();
            for (const poly of info.polys) {
              if (acc >= target) break;
              const f = clamp((target - acc) / (poly.len || 1));
              poly.trace(ctx, 0, f);
              acc += poly.len;
            }
            ctx.stroke();
          } else {
            const k = (sub - 0.5) / 0.5;
            ctx.save();
            ctx.globalAlpha *= a * k;
            ctx.fillStyle = c;
            ctx.fill(info.path);
            ctx.restore();
            if (k < 1) {
              ctx.globalAlpha *= a * (1 - k);
              ctx.stroke(info.path);
            }
          }
        }
      }
      ctx.restore();
    }
    ctx.restore();
  };

  /** Draw one glyph centred on (x, y) with the given ink height (icons). */
  A.glyphMark = (ctx, ch, x, y, height, opts = {}) => {
    const { color = '#ffffff', alpha = 1, write = null } = opts;
    if (alpha <= 0.002) return;
    const fk = opts.font && A.fonts[opts.font] ? opts.font : Object.keys(A.fonts).filter((k) => k.startsWith('serif')).pop();
    const font = A.fonts[fk];
    const glyph = font.charToGlyph(ch);
    const info = glyphInfo(font, fk, glyph);
    const bb = glyph.getBoundingBox();
    const s = height / Math.max(1, bb.y2 - bb.y1);
    ctx.save();
    ctx.translate(x - ((bb.x1 + bb.x2) / 2) * s, y - ((bb.y1 + bb.y2) / 2) * s);
    ctx.scale(s, s);
    ctx.globalAlpha *= alpha;
    ctx.fillStyle = color;
    ctx.strokeStyle = color;
    if (write == null || write >= 1) ctx.fill(info.path);
    else if (write > 0) {
      ctx.lineWidth = u(2.5) / s;
      if (write < 0.5) {
        const target = (write / 0.5) * info.total;
        let acc = 0;
        ctx.beginPath();
        for (const poly of info.polys) {
          if (acc >= target) break;
          poly.trace(ctx, 0, clamp((target - acc) / (poly.len || 1)));
          acc += poly.len;
        }
        ctx.stroke();
      } else {
        const k = (write - 0.5) / 0.5;
        ctx.save();
        ctx.globalAlpha *= k;
        ctx.fill(info.path);
        ctx.restore();
        ctx.globalAlpha *= 1 - k;
        ctx.stroke(info.path);
      }
    }
    ctx.restore();
  };

  /** Convenience: lay out and draw in one call. */
  A.label = (ctx, content, x, y, opts = {}) => {
    const L = A.text(content, opts.style || opts);
    A.drawText(ctx, L, x, y, opts);
    return L;
  };

  // ------------------------------------------------------------------ helpers
  /** Indicate: scale bump + colour flash, p in [0,1]. */
  A.indicate = (p) => (p <= 0 || p >= 1 ? 0 : R.thereAndBack(p));

  /** A check mark or cross drawn as strokes (no font glyph needed). */
  A.checkMark = (ctx, x, y, size, opts = {}) => {
    const { color = '#83C167', width = 5, p = 1, alpha = 1 } = opts;
    const s = size;
    const poly = A.polyline([[x - 0.5 * s, y], [x - 0.15 * s, y - 0.38 * s], [x + 0.55 * s, y + 0.45 * s]]);
    A.stroke(ctx, poly, { color, width, alpha, b: p });
  };
  A.crossMark = (ctx, x, y, size, opts = {}) => {
    const { color = '#FC6255', width = 5, p = 1, alpha = 1 } = opts;
    const s = size / 2;
    const p1 = clamp(p * 2), p2 = clamp(p * 2 - 1);
    A.stroke(ctx, A.line(x - s, y + s, x + s, y - s), { color, width, alpha, b: p1 });
    A.stroke(ctx, A.line(x + s, y + s, x - s, y - s), { color, width, alpha, b: p2 });
  };

  /** Seconds -> "m:ss" */
  A.fmtTime = (t) => {
    t = Math.max(0, t);
    const m = Math.floor(t / 60), s = Math.floor(t % 60);
    return m + ':' + String(s).padStart(2, '0');
  };
})(typeof window !== 'undefined' ? window : globalThis);
