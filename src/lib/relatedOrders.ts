import summaryOrders from '../../data/site_orders_summary.json';

// Cached once per build process (module singleton), not rebuilt per generated page.
let eoNumberMap: Map<number, any> | null = null;
let presidentOrdersMap: Map<string, any[]> | null = null;

function getEoNumberMap(): Map<number, any> {
  if (!eoNumberMap) {
    eoNumberMap = new Map();
    for (const o of summaryOrders as any[]) {
      if (o.eo_number) eoNumberMap.set(o.eo_number, o);
    }
  }
  return eoNumberMap;
}

function getPresidentOrdersMap(): Map<string, any[]> {
  if (!presidentOrdersMap) {
    presidentOrdersMap = new Map();
    for (const o of summaryOrders as any[]) {
      const slug = o.president_slug || "";
      const list = presidentOrdersMap.get(slug) || [];
      // Cache the parsed timestamp once so per-page lookups avoid re-parsing dates.
      list.push({ ...o, __time: o.signing_date ? new Date(o.signing_date).getTime() : 0 });
      presidentOrdersMap.set(slug, list);
    }
  }
  return presidentOrdersMap;
}

// Bounded top-k selection by date proximity, avoiding an O(n log n) sort of
// potentially thousands of orders (e.g. FDR) on every single order page.
function closestByDate(list: any[], targetTime: number, excludeId: string, limit: number): any[] {
  const best: { o: any; diff: number }[] = [];
  for (const o of list) {
    if (o.id === excludeId) continue;
    const diff = Math.abs(o.__time - targetTime);
    if (best.length < limit) {
      best.push({ o, diff });
      if (best.length === limit) best.sort((a, b) => a.diff - b.diff);
    } else if (diff < best[best.length - 1].diff) {
      best[best.length - 1] = { o, diff };
      best.sort((a, b) => a.diff - b.diff);
    }
  }
  best.sort((a, b) => a.diff - b.diff);
  return best.map(b => b.o);
}

export function getRelatedOrders(order: { id: string; eo_number?: number | null; president_slug?: string; signing_date?: string; full_text?: string }, limit = 6) {
  const eoMap = getEoNumberMap();

  const referencedNumbers = Array.from(
    new Set(
      Array.from((order.full_text || "").matchAll(/Executive Order\s*(?:No\.?)?\s*(\d{4,5})/gi))
        .map(m => parseInt(m[1], 10))
        .filter(n => n !== order.eo_number)
    )
  );

  const referencedOrders = referencedNumbers.map(n => eoMap.get(n)).filter(Boolean);

  const orderTime = order.signing_date ? new Date(order.signing_date).getTime() : 0;
  const samePresidentOrders = closestByDate(
    getPresidentOrdersMap().get(order.president_slug || "") || [],
    orderTime,
    order.id,
    limit
  );

  const related: any[] = [];
  const seen = new Set([order.id]);
  for (const o of [...referencedOrders, ...samePresidentOrders]) {
    if (related.length >= limit) break;
    if (seen.has(o.id)) continue;
    seen.add(o.id);
    related.push(o);
  }

  return { related, referencedCount: referencedOrders.length };
}
