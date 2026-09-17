const body = document.body;
const closePanels = () => body.classList.remove("menu-open");
document.querySelector("[data-menu]")?.addEventListener("click", () => body.classList.toggle("menu-open"));
document.querySelector("[data-toc]")?.addEventListener("click", () => {
  const details = document.querySelector(".mobile-toc");
  details.open = true;
  details.scrollIntoView({ behavior: "smooth", block: "start" });
});
document.querySelector("[data-close]")?.addEventListener("click", closePanels);
document.querySelectorAll(".course-nav a,.page-toc a").forEach((link) => link.addEventListener("click", closePanels));
const panelPreferences = [
  { name: "nav", selector: "[data-nav-collapse]", close: "‹", open: "›", label: "课程目录", direction: "左" },
  { name: "toc", selector: "[data-toc-collapse]", close: "›", open: "‹", label: "本篇目录", direction: "右" },
];
for (const panel of panelPreferences) {
  const button = document.querySelector(panel.selector);
  if (!button) continue;
  const apply = (collapsed) => {
    body.classList.toggle(`${panel.name}-collapsed`, collapsed);
    button.textContent = collapsed ? panel.open : panel.close;
    button.setAttribute("aria-expanded", String(!collapsed));
    const label = collapsed ? `展开${panel.label}` : `向${panel.direction}收起${panel.label}`;
    button.setAttribute("aria-label", label);
    button.title = label;
  };
  try { apply(localStorage.getItem(`course-${panel.name}-collapsed`) === "true"); }
  catch { apply(false); }
  button.addEventListener("click", () => {
    const collapsed = !body.classList.contains(`${panel.name}-collapsed`);
    apply(collapsed);
    try { localStorage.setItem(`course-${panel.name}-collapsed`, String(collapsed)); } catch {}
  });
}
const tocLinks = [...document.querySelectorAll("[data-section]")];
const sections = [...new Set(tocLinks.map((link) => document.getElementById(link.dataset.section)).filter(Boolean))];
let scheduled = false;
const updateCurrentSection = () => {
  scheduled = false;
  const hashId = decodeURIComponent(location.hash.slice(1));
  let current = sections.find((section) => section.id === hashId) || sections[0];
  for (const section of sections) if (section.getBoundingClientRect().top <= 140) current = section;
  tocLinks.forEach((link) => link.classList.toggle("active", link.dataset.section === current?.id));
};
addEventListener("scroll", () => {
  if (!scheduled) { scheduled = true; requestAnimationFrame(updateCurrentSection); }
}, { passive: true });
addEventListener("hashchange", updateCurrentSection);
updateCurrentSection();
const lightbox = document.querySelector(".lightbox");
const lightboxImage = lightbox?.querySelector("img");
document.querySelectorAll("article img").forEach((img) => {
  const open = () => { lightboxImage.src = img.currentSrc || img.src; lightboxImage.alt = img.alt; lightbox.showModal(); };
  img.addEventListener("click", open);
  img.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") { event.preventDefault(); open(); }
  });
});
lightbox?.querySelector("button")?.addEventListener("click", () => lightbox.close());
lightbox?.addEventListener("click", (event) => { if (event.target === lightbox) lightbox.close(); });

// Search is entirely local: no query or course text is sent to an external service.
const { searchEntries } = await import('./search.js');
const searchDialog = document.querySelector('.search-dialog');
const searchInput = document.querySelector('[data-search-input]');
const results = document.querySelector('.search-results');
const searchStatus = document.querySelector('.search-status');
let indexPromise;
let activeResult = -1;
let searchOpener;
const loadIndex = () => indexPromise ||= fetch(new URL('../search-index.json', import.meta.url))
  .then(response => { if (!response.ok) throw Error('index'); return response.json(); })
  .catch(error => { indexPromise = null; throw error; });
function highlight(text, query) {
  const fragment = document.createDocumentFragment();
  const terms = query.trim().split(/\s+/).filter(Boolean).sort((a,b) => b.length-a.length);
  const pattern = new RegExp(terms.map(term => term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|'),'gi');
  let from = 0;
  for (const match of text.matchAll(pattern)) {
    fragment.append(document.createTextNode(text.slice(from, match.index)));
    const mark = document.createElement('mark'); mark.textContent = match[0]; fragment.append(mark);
    from = match.index + match[0].length;
  }
  fragment.append(document.createTextNode(text.slice(from))); return fragment;
}
async function renderSearch() {
  const query = searchInput.value.trim();
  results.replaceChildren(); activeResult = -1;
  if (!query) { searchStatus.textContent = '输入关键词，搜索全部七篇课程'; return; }
  searchStatus.textContent = '正在搜索…';
  try {
    const entries = await loadIndex();
    if (searchInput.value.trim() !== query) return;
    const matches = searchEntries(entries, query);
    searchStatus.textContent = matches.length ? `找到 ${matches.length} 个相关章节` : '没有找到结果，试试更短的关键词';
    for (const item of matches) {
      const a = document.createElement('a'); a.href = item.url; a.className = 'search-result';
      const title = document.createElement('strong'); title.append(highlight(item.heading, query));
      const course = document.createElement('small'); course.textContent = item.title;
      const snippet = document.createElement('p'); snippet.append(highlight(item.snippet, query));
      a.append(course, title, snippet); results.append(a);
    }
  } catch { if (searchInput.value.trim() === query) searchStatus.textContent = '搜索暂时无法加载，请重新输入以重试'; }
}
function openSearch() { searchOpener = document.activeElement; searchDialog.showModal(); searchInput.focus(); renderSearch(); }
document.querySelector('[data-search-open]')?.addEventListener('click', openSearch);
document.querySelector('[data-search-close]')?.addEventListener('click', () => searchDialog.close());
searchDialog?.addEventListener('close', () => searchOpener?.focus());
searchDialog?.addEventListener('click', e => { if (e.target === searchDialog) searchDialog.close(); });
searchInput?.addEventListener('input', renderSearch);
searchDialog?.addEventListener('keydown', event => {
  const links = [...results.querySelectorAll('a')];
  if (['ArrowDown', 'ArrowUp'].includes(event.key) && links.length) {
    event.preventDefault(); activeResult = (activeResult + (event.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length;
    links.forEach((link,i) => link.classList.toggle('selected', i === activeResult));
    links[activeResult].focus(); links[activeResult].scrollIntoView({block:'nearest'});
  } else if (event.key === 'Enter' && event.target === searchInput && links.length) {
    event.preventDefault(); links[Math.max(0, activeResult)].click();
  }
});
addEventListener('keydown', event => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault(); if (searchDialog.open) searchDialog.close(); else openSearch();
  }
});
document.querySelectorAll('[data-copy-kind]').forEach(button => button.addEventListener('click', async () => {
  const status = document.querySelector('.copy-status'); button.disabled = true;
  try {
    let text = location.href;
    if (button.dataset.copyKind === 'markdown') {
      const response = await fetch(button.dataset.source); if (!response.ok) throw Error('copy'); text = await response.text();
    } else if (button.dataset.copyKind === 'text') text = document.querySelector('article').innerText;
    await navigator.clipboard.writeText(text); status.textContent = '已复制'; const menu = button.closest('details'); if (menu) menu.open = false;
  } catch { status.textContent = '复制失败，请允许剪贴板访问后重试'; }
  finally { button.disabled = false; }
}));
document.querySelectorAll('[data-heading-copy]').forEach(link => link.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(link.href); document.querySelector('.copy-status').textContent = '章节链接已复制'; }
  catch { document.querySelector('.copy-status').textContent = '已定位章节，可复制地址栏链接'; }
}));
document.querySelector('[data-print]')?.addEventListener('click', () => { document.querySelector('.more-actions').open = false; window.print(); });
document.querySelector('[data-breadcrumb-menu]')?.addEventListener('click', () => {
  if (matchMedia('(max-width:1023px)').matches) body.classList.toggle('menu-open');
  else if (body.classList.contains('nav-collapsed')) document.querySelector('[data-nav-collapse]').click();
  else document.querySelector('.course-nav a').focus();
});
document.addEventListener('click', event => document.querySelectorAll('.copy-menu[open],.more-actions[open]').forEach(menu => { if (!menu.contains(event.target)) menu.open = false; }));
document.addEventListener('keydown', event => { if (event.key === 'Escape') document.querySelectorAll('.copy-menu[open],.more-actions[open]').forEach(menu => { menu.open = false; menu.querySelector('summary').focus(); }); });
