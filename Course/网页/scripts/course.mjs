export const lessons = [
  ["01-使用AI的核心问题", "使用AI的核心问题", "使用 AI 的核心问题"],
  ["02-AI的能力从哪里来", "AI的能力从哪里来", "AI 的能力从哪里来"],
  ["03-信息输入与工具执行", "信息输入与工具执行", "信息输入与工具执行"],
  ["04-需求表达与反馈闭环", "需求表达与反馈闭环", "需求表达与反馈闭环"],
  ["05-任务执行与证据核验", "任务执行与证据核验", "任务执行与证据核验"],
  ["06-行动选择与投入控制", "行动选择与投入控制", "行动选择与投入控制"],
  ["07-课程制作与人机取舍", "课程制作与人机取舍", "课程制作与人机取舍"]
].map(([slug, basename, fallbackTitle], index) => ({
  source: `${slug}/${basename}.md`,
  slug,
  fallbackTitle,
  index,
  output: `${slug}.html`
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
