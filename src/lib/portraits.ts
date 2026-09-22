// Some historical harvest sources report a president identifier that doesn't match
// the canonical slug used in data/presidents.json and public/portraits/*.jpg (e.g.
// distinguishing Trump's two non-consecutive terms, or "george-bush" for the 41st
// president). Resolve those known aliases so portrait images actually load instead
// of silently 404ing.
export const PORTRAIT_SLUG_ALIASES: Record<string, string> = {
  "george-bush": "george-h-w-bush",
  "donald-j-trump-1st-term": "donald-trump",
  "donald-j-trump-2nd-term": "donald-trump",
  "gerald-r-ford": "gerald-ford",
  "joseph-r-biden-jr": "joe-biden",
  "william-j-clinton": "bill-clinton"
};

export function resolvePortraitSlug(slug?: string | null): string {
  if (!slug) return "default";
  return PORTRAIT_SLUG_ALIASES[slug] || slug;
}
