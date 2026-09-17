export function searchEntries(entries, query) {
  const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return [];
  return entries.map((entry) => {
    const title = entry.title.toLocaleLowerCase();
    const heading = entry.heading.toLocaleLowerCase();
    const text = entry.text.toLocaleLowerCase();
    if (!terms.every(term => `${title} ${heading} ${text}`.includes(term))) return null;
    const score = terms.reduce((sum, term) => sum + (heading.includes(term) ? 8 : 0) + (title.includes(term) ? 4 : 0) + (text.includes(term) ? 1 : 0), 0);
    const at = Math.max(0, text.indexOf(terms[0]));
    const start = Math.max(0, at - 35);
    return { ...entry, score, snippet: (start ? '…' : '') + entry.text.slice(start, start + 150) + (entry.text.length > start + 150 ? '…' : '') };
  }).filter(Boolean).sort((a, b) => b.score - a.score).slice(0, 40);
}
