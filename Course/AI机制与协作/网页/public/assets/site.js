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
const toc = document.querySelector(".page-toc");
document.querySelector("[data-toc-collapse]")?.addEventListener("click", (event) => {
  const collapsed = toc.classList.toggle("collapsed");
  event.currentTarget.textContent = collapsed ? "展开" : "收起";
  event.currentTarget.setAttribute("aria-expanded", String(!collapsed));
});
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
