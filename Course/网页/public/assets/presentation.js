const deck = document.querySelector("[data-deck]");
const slides = [...document.querySelectorAll("[data-slide]")];
const overview = document.querySelector("[data-overview]");
const overviewGrid = document.querySelector("[data-overview-grid]");
const toast = document.querySelector("[data-toast]");
let current = 0;
let transitionTimer = null;
let toastTimer = null;

const pad = (value) => String(value).padStart(2, "0");
const isTypingTarget = (target) => {
  if (!(target instanceof Element)) return false;
  return Boolean(target.closest("input, textarea, select, button, a, video, [contenteditable='true'], iframe"));
};

function announce(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 1600);
}

function updateOverview() {
  if (!overviewGrid) return;
  overviewGrid.querySelectorAll("button").forEach((button, index) => {
    button.setAttribute("aria-current", index === current ? "true" : "false");
  });
}

function updateUrl(index) {
  const hash = "#slide-" + pad(index + 1);
  if (location.hash !== hash) history.replaceState(null, "", hash);
}

function stopMedia(slide) {
  slide?.querySelectorAll("video").forEach((video) => {
    if (!video.paused) video.pause();
  });
}

function showSlide(index, animate = true) {
  const next = Math.max(0, Math.min(slides.length - 1, index));
  if (next === current && slides[current]?.classList.contains("is-active")) {
    updateUrl(next);
    updateOverview();
    return;
  }

  const previous = slides[current];
  const upcoming = slides[next];
  clearTimeout(transitionTimer);
  stopMedia(previous);

  if (!animate) {
    slides.forEach((slide, i) => {
      slide.classList.toggle("is-active", i === next);
      slide.classList.remove("is-entering", "is-leaving");
    });
  } else {
    previous?.classList.remove("is-entering");
    previous?.classList.add("is-leaving");
    upcoming.classList.add("is-active", "is-entering");
    transitionTimer = setTimeout(() => {
      slides.forEach((slide, i) => {
        slide.classList.toggle("is-active", i === next);
        slide.classList.remove("is-entering", "is-leaving");
      });
    }, 460);
  }

  current = next;
  updateUrl(next);
  updateOverview();
  document.title = (slides[next].dataset.title || "课程演示") + "｜AI 驱动的新工作方式";
}

function nextSlide() {
  if (current < slides.length - 1) showSlide(current + 1);
  else announce("已经是最后一页");
}

function previousSlide() {
  if (current > 0) showSlide(current - 1);
  else announce("已经是第一页");
}

function openOverview() {
  updateOverview();
  if (overview?.showModal) overview.showModal();
}

function closeOverview() {
  if (overview?.open) overview.close();
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen?.().catch(() => announce("浏览器未允许全屏"));
  } else {
    document.exitFullscreen?.();
  }
}

function buildOverview() {
  if (!overviewGrid) return;
  overviewGrid.innerHTML = "";
  slides.forEach((slide, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.innerHTML = "<small>" + pad(index + 1) + " / " + pad(slides.length) + "</small><strong>" + (slide.dataset.title || ("第 " + (index + 1) + " 页")) + "</strong>";
    button.addEventListener("click", () => {
      showSlide(index, false);
      closeOverview();
    });
    overviewGrid.append(button);
  });
}

function bindVideos() {
  document.querySelectorAll("[data-video-shell]").forEach((shell) => {
    const video = shell.querySelector("video");
    if (!video) return;
    const markReady = () => shell.classList.remove("is-missing");
    const markMissing = () => shell.classList.add("is-missing");
    video.addEventListener("loadedmetadata", markReady, { once: true });
    video.addEventListener("error", markMissing);
    setTimeout(() => {
      if (video.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) markMissing();
    }, 1800);
  });
}

document.querySelectorAll("[data-overview-open]").forEach((button) => button.addEventListener("click", openOverview));
document.querySelector("[data-overview-close]")?.addEventListener("click", closeOverview);

document.querySelectorAll("[data-open-frame]").forEach((button) => {
  button.addEventListener("click", () => {
    const iframe = button.closest("[data-slide]")?.querySelector("iframe");
    if (!iframe?.src) return;
    const opened = window.open(iframe.src, "_blank", "noopener,noreferrer");
    if (!opened) announce("浏览器阻止了新窗口");
  });
});

document.addEventListener("keydown", (event) => {
  if (overview?.open) {
    if (event.key === "Escape") {
      event.preventDefault();
      closeOverview();
    }
    return;
  }
  if (isTypingTarget(event.target)) return;

  if (["ArrowRight", "ArrowDown", "PageDown", " "].includes(event.key)) {
    event.preventDefault();
    nextSlide();
  } else if (["ArrowLeft", "ArrowUp", "PageUp"].includes(event.key)) {
    event.preventDefault();
    previousSlide();
  } else if (event.key === "Home") {
    event.preventDefault();
    showSlide(0);
  } else if (event.key === "End") {
    event.preventDefault();
    showSlide(slides.length - 1);
  } else if (event.key.toLowerCase() === "m") {
    event.preventDefault();
    openOverview();
  } else if (event.key.toLowerCase() === "f") {
    event.preventDefault();
    toggleFullscreen();
  }
});

let touchStart = null;
deck?.addEventListener("touchstart", (event) => {
  if (event.touches.length !== 1) return;
  touchStart = { x: event.touches[0].clientX, y: event.touches[0].clientY };
}, { passive: true });

deck?.addEventListener("touchend", (event) => {
  if (!touchStart || event.changedTouches.length !== 1) return;
  const dx = event.changedTouches[0].clientX - touchStart.x;
  const dy = event.changedTouches[0].clientY - touchStart.y;
  touchStart = null;
  if (Math.abs(dx) < 72 || Math.abs(dx) < Math.abs(dy) * 1.35) return;
  dx < 0 ? nextSlide() : previousSlide();
}, { passive: true });

deck?.addEventListener("click", (event) => {
  if (isTypingTarget(event.target)) return;
  const rect = deck.getBoundingClientRect();
  const ratio = (event.clientX - rect.left) / rect.width;
  if (ratio < 0.11) previousSlide();
  if (ratio > 0.89) nextSlide();
});

overview?.addEventListener("click", (event) => {
  if (event.target === overview) closeOverview();
});

window.addEventListener("hashchange", () => {
  const match = location.hash.match(/^#slide-(\d{1,2})$/);
  if (!match) return;
  const index = Number(match[1]) - 1;
  if (Number.isInteger(index) && index >= 0 && index < slides.length && index !== current) {
    showSlide(index, false);
  }
});

buildOverview();
bindVideos();

const initialMatch = location.hash.match(/^#slide-(\d{1,2})$/);
const initial = initialMatch ? Number(initialMatch[1]) - 1 : 0;
current = Math.max(0, Math.min(slides.length - 1, Number.isInteger(initial) ? initial : 0));
showSlide(current, false);
