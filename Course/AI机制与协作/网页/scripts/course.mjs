export const lessons = [
  ["01-使用AI的问题.md", "使用 AI 的核心问题"],
  ["02-AI的能力从哪里来.md", "AI 的能力从哪里来"],
  ["03-输入输出与执行.md", "信息输入与工具执行"],
  ["04-表达需求与反馈.md", "需求表达与反馈闭环"],
  ["05-执行任务.md", "任务执行与证据核验"],
  ["06-行动与投入.md", "行动选择与投入控制"],
  ["07-课程制作.md", "课程制作与人机取舍"]
].map(([source, fallbackTitle], index) => ({
  source: source.replace(/\.md$/, "/正文.md"),
  slug: source.replace(/\.md$/, ""),
  fallbackTitle,
  index,
  output: source.replace(/\.md$/i, ".html")
}));

export function slugify(text, used = new Map()) {
  const base = text.trim().toLowerCase()
    .replace(/<[^>]+>/g, "")
    .replace(/[\s/]+/g, "-")
    .replace(/[^\p{Letter}\p{Number}\-_]/gu, "") || "section";
  const count = used.get(base) || 0;
  used.set(base, count + 1);
  return count ? `${base}-${count + 1}` : base;
}
