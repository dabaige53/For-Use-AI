export const lessons = [
  ["01-使用AI的问题.md", "使用 AI 时，我们到底遇到了什么问题"],
  ["02-AI的能力从哪里来.md", "AI 的能力从哪里来"],
  ["03-输入输出与执行.md", "AI 怎样接收信息并执行任务"],
  ["04-表达需求与反馈.md", "怎样表达需求、修正结果"],
  ["05-执行任务.md", "怎样用 AI 执行任务"],
  ["06-行动与投入.md", "怎样选择行动与控制投入"],
  ["07-课程制作.md", "这门课程是怎样做出来的"]
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
