/* Player: narration audio is the master clock; the canvas is redrawn from t.
 *
 * URL parameters
 *   ?t=12.5    start at 12.5 s
 *   ?render    renderer mode (no UI); exposes AIIO.frameDataURL(i)
 */
(function (root) {
  'use strict';
  const A = root.AIIO;
  const D = root.AIIO_DATA;
  const params = new URLSearchParams(root.location.search);
  const renderMode = params.has('render');
  const $ = (id) => root.document.getElementById(id);
  const canvas = $('c');
  const ctx = canvas.getContext('2d');
  const audio = $('vo');
  const DUR = D.duration;
  const FPS = D.fps;

  if (renderMode) root.document.body.classList.add('render');

  let t = clamp(parseFloat(params.get('t')) || 0);
  let playing = false;
  let clockBase = 0; // fallback clock when audio is unavailable
  let audioOK = false;
  function clamp(x) {
    return Math.min(DUR, Math.max(0, x || 0));
  }

  function draw() {
    A.drawScene(ctx, t);
  }

  A.ready = A.loadFonts().then(() => {
    draw();
    return true;
  });

  // -------------------------------------------------------------- renderer API
  A.renderFrame = (i) => {
    t = i / FPS;
    draw();
  };
  A.frameDataURL = (i, type = 'image/png') => {
    A.renderFrame(i);
    return canvas.toDataURL(type);
  };
  A.frameCount = Math.round(DUR * FPS);
  if (renderMode) return;

  // -------------------------------------------------------------- audio
  audio.src = D.audio;
  audio.addEventListener('canplay', () => (audioOK = true), { once: true });
  audio.addEventListener('error', () => (audioOK = false));
  // the audio may finish loading after a seek: keep it on the animation clock
  audio.addEventListener('loadedmetadata', () => {
    try {
      audio.currentTime = t;
    } catch (e) {
      /* not seekable yet */
    }
  });

  // -------------------------------------------------------------- UI
  const seek = $('seek');
  seek.max = String(DUR);
  const track = $('track');
  for (const ch of A.chapters || []) {
    if (ch.t <= 0) continue;
    const m = root.document.createElement('span');
    m.className = 'mark';
    m.style.left = `calc(${(ch.t / DUR) * 100}% - 1px)`;
    m.title = ch.title;
    track.appendChild(m);
  }
  let subsOn = false;
  try {
    subsOn = root.localStorage.getItem('aiio-subs') === '1';
  } catch (e) {
    /* storage unavailable */
  }
  const subs = $('subs');
  const ccBtn = $('cc');

  function chapterAt(time) {
    let cur = null;
    for (const ch of A.chapters || []) if (ch.t <= time + 1e-3) cur = ch;
    return cur;
  }
  function updateUI() {
    $('time').textContent = `${A.fmtTime(t)} / ${A.fmtTime(DUR)}`;
    if (root.document.activeElement !== seek) seek.value = String(t);
    const ch = chapterAt(t);
    $('chapter').textContent = ch ? ch.title : '';
    $('play').textContent = playing ? '暂停' : '播放';
    root.document.body.classList.toggle('paused', !playing);
    ccBtn.setAttribute('aria-pressed', String(subsOn));
    const cue = subsOn ? D.subtitles.find((c) => t >= c.start && t <= c.end) : null;
    subs.style.display = cue ? 'block' : 'none';
    if (cue && subs.textContent !== cue.text) subs.textContent = cue.text;
  }

  function setTime(x) {
    t = clamp(x);
    if (audioOK || audio.readyState > 0) {
      try {
        audio.currentTime = t;
      } catch (e) {
        /* not seekable yet */
      }
    }
    clockBase = performance.now() / 1000 - t;
    draw();
    updateUI();
  }

  function play() {
    if (t >= DUR - 0.05) setTime(0);
    playing = true;
    clockBase = performance.now() / 1000 - t;
    if (audio.readyState > 0 && Math.abs(audio.currentTime - t) > 0.05) {
      try {
        audio.currentTime = t;
      } catch (e) {
        /* not seekable yet */
      }
    }
    const p = audio.play();
    if (p && p.catch) p.catch(() => (audioOK = false));
    updateUI();
  }
  function pause() {
    playing = false;
    audio.pause();
    updateUI();
  }
  const toggle = () => (playing ? pause() : play());

  function tick() {
    if (playing) {
      const useAudio = audioOK && !audio.paused && !audio.ended && !audio.seeking;
      t = clamp(useAudio ? audio.currentTime : performance.now() / 1000 - clockBase);
      if (t >= DUR) {
        t = DUR;
        pause();
      }
      draw();
      updateUI();
    }
    root.requestAnimationFrame(tick);
  }

  $('play').addEventListener('click', toggle);
  $('big').addEventListener('click', play);
  canvas.addEventListener('click', toggle);
  seek.addEventListener('input', () => setTime(parseFloat(seek.value)));
  ccBtn.addEventListener('click', () => {
    subsOn = !subsOn;
    try {
      root.localStorage.setItem('aiio-subs', subsOn ? '1' : '0');
    } catch (e) {
      /* storage unavailable */
    }
    updateUI();
  });
  const fullscreen = () => {
    const el = root.document.documentElement;
    if (root.document.fullscreenElement) root.document.exitFullscreen();
    else if (el.requestFullscreen) el.requestFullscreen();
  };
  $('fs').addEventListener('click', fullscreen);
  audio.addEventListener('ended', () => {
    t = DUR;
    pause();
  });

  root.addEventListener('keydown', (e) => {
    if (e.target && e.target.tagName === 'INPUT' && e.key !== ' ') return;
    const k = e.key.toLowerCase();
    if (k === ' ' || k === 'k') toggle();
    else if (k === 'arrowleft') setTime(t - 5);
    else if (k === 'arrowright') setTime(t + 5);
    else if (k === 'j') setTime(t - 10);
    else if (k === 'l') setTime(t + 10);
    else if (k === ',') setTime(t - 1 / FPS);
    else if (k === '.') setTime(t + 1 / FPS);
    else if (k === 'home') setTime(0);
    else if (k === 'end') setTime(DUR);
    else if (k === 'c') ccBtn.click();
    else if (k === 'f') fullscreen();
    else return;
    e.preventDefault();
  });

  let idleTimer = 0;
  const wake = () => {
    root.document.body.classList.remove('idle');
    root.clearTimeout(idleTimer);
    idleTimer = root.setTimeout(() => playing && root.document.body.classList.add('idle'), 2200);
  };
  root.addEventListener('mousemove', wake);
  root.addEventListener('touchstart', wake, { passive: true });

  A.ready.then(() => {
    setTime(t);
    root.requestAnimationFrame(tick);
  });
})(window);
