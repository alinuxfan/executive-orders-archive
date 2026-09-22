export function getYearlyOrderCounts(orders: { signing_date?: string }[], startYear = 1789): { year: number; count: number }[] {
  const counts = new Map<number, number>();
  let maxYear = startYear;

  for (const o of orders) {
    if (!o.signing_date) continue;
    const year = parseInt(o.signing_date.slice(0, 4), 10);
    if (!Number.isFinite(year)) continue;
    counts.set(year, (counts.get(year) || 0) + 1);
    if (year > maxYear) maxYear = year;
  }

  const result: { year: number; count: number }[] = [];
  for (let y = startYear; y <= maxYear; y++) {
    result.push({ year: y, count: counts.get(y) || 0 });
  }
  return result;
}
