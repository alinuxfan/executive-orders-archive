// Shared client-side search helpers for /orders and /search.
(function () {
  const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (c) => ESCAPES[c]);
  }

  // "EO 11359-A" for suffixed orders that share a number with another order.
  function eoLabel(order) {
    const num = order.num !== undefined ? order.num : order.eo_number;
    if (!num) return '';
    const suffix = order.sfx || order.eo_suffix;
    return suffix ? `${num}-${suffix}` : String(num);
  }

  let indexPromise = null;
  let keywordsPromise = null;

  // Base index (titles, snippets, metadata). Each entry gets a lowercase
  // haystack for matching; body keywords are merged in later by loadKeywords().
  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch('/search_index.json')
        .then((res) => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          return res.json();
        })
        .then((orders) => {
          for (const o of orders) {
            o._title = (o.title || '').toLowerCase();
            o._pres = (o.pres || '').toLowerCase();
            o._meta = `${o.snip || ''} ${o.tag || ''} ${(o.topics || []).join(' ')}`.toLowerCase();
            o._kw = '';
            const rawDate = o.date || '';
            o._year = rawDate.length >= 4 ? parseInt(rawDate.slice(0, 4), 10) : null;
          }
          return orders;
        })
        .catch((err) => {
          indexPromise = null;
          throw err;
        });
    }
    return indexPromise;
  }

  // Body-text keywords, a parallel array to search_index.json. Only fetched
  // once the user actually types a query.
  function loadKeywords() {
    if (!keywordsPromise) {
      keywordsPromise = Promise.all([loadIndex(), fetch('/search_keywords.json').then((r) => r.json())])
        .then(([orders, keywords]) => {
          if (Array.isArray(keywords) && keywords.length === orders.length) {
            for (let i = 0; i < orders.length; i++) orders[i]._kw = keywords[i] || '';
          }
          return orders;
        })
        .catch(() => loadIndex());
    }
    return keywordsPromise;
  }

  // "14430", "EO 14430", "E.O. 11359-A", "executive order 12891"
  const EO_QUERY_RE = /^(?:e\.?\s*o\.?|executive\s+order)?\s*(?:no\.?\s*)?#?\s*(\d{1,5})(?:-?([a-z]))?$/i;

  function parseQuery(query) {
    const q = (query || '').toLowerCase().trim();
    const eo = q.match(EO_QUERY_RE);
    const terms = q.replace(/^(?:e\.?o\.?|executive order)\s+(?=\d)/, '').split(/\s+/).filter(Boolean);
    return {
      raw: q,
      terms,
      eoNumber: eo ? parseInt(eo[1], 10) : null,
      eoSuffix: eo && eo[2] ? eo[2].toUpperCase() : null,
    };
  }

  // Relevance score, or -1 when the order doesn't match every term. Exact EO
  // numbers rank first, then title hits (whole-phrase > word-start > substring),
  // then president, snippet/topic, and finally body keywords.
  function scoreOrder(o, parsed) {
    if (!parsed.raw) return 0;
    let score = 0;
    if (parsed.eoNumber !== null && o.num === parsed.eoNumber) {
      score += (o.sfx || null) === parsed.eoSuffix ? 1000 : 800;
    }
    if (parsed.raw.length > 2 && o._title.includes(parsed.raw)) score += 40;
    for (const term of parsed.terms) {
      let termScore = 0;
      const idx = o._title.indexOf(term);
      if (idx !== -1) termScore = idx === 0 || /\W/.test(o._title[idx - 1]) ? 12 : 6;
      else if (o._pres.includes(term)) termScore = 8;
      else if (String(o.num || '') === term) termScore = 8;
      else if (o._meta.includes(term)) termScore = 4;
      else if (o._kw.includes(term)) termScore = 1;
      if (!termScore && score < 800) return -1;
      score += termScore;
    }
    return score;
  }

  function rankOrders(orders, query) {
    const parsed = parseQuery(query);
    const scored = [];
    for (const o of orders) {
      const s = scoreOrder(o, parsed);
      if (s >= 0) scored.push([s, o]);
    }
    scored.sort((a, b) => b[0] - a[0] || (b[1].date || '').localeCompare(a[1].date || ''));
    return scored.map((pair) => pair[1]);
  }

  // Federal Register disposition status ("Revoked", "Amended", ...), from the
  // search index's `st` field or the summary dataset's `eo_status`.
  const STATUS_CLASSES = {
    Revoked: 'bg-rose-600 text-white border-rose-700',
    Superseded: 'bg-rose-600 text-white border-rose-700',
    Suspended: 'bg-rose-600 text-white border-rose-700',
    'Partially revoked': 'bg-amber-100 text-amber-900 border-amber-300 dark:bg-amber-950/60 dark:text-amber-200 dark:border-amber-800',
    'Partially superseded': 'bg-amber-100 text-amber-900 border-amber-300 dark:bg-amber-950/60 dark:text-amber-200 dark:border-amber-800',
    Amended: 'bg-amber-100 text-amber-900 border-amber-300 dark:bg-amber-950/60 dark:text-amber-200 dark:border-amber-800',
    Reinstated: 'bg-emerald-100 text-emerald-900 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-200 dark:border-emerald-800',
  };
  function statusBadge(order) {
    const status = order.st || order.eo_status;
    if (!status) return '';
    const cls = STATUS_CLASSES[status] || STATUS_CLASSES.Amended;
    return `<span class="text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded border ${cls}" title="Federal Register disposition: ${escapeHtml(status)}">${escapeHtml(status)}</span>`;
  }

  function sentimentBadge(order) {
    const val = order.val || order.sentiment_valence;
    const comp = order.comp !== undefined ? order.comp : (order.sentiment_compound || 0);
    if (val === 'Constitutional Fidelity' || val === 'Positive') {
      return { label: `Fidelity (${comp >= 0 ? '+' : ''}${comp.toFixed(2)})`, cls: 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800' };
    }
    if (val === 'Constitutional Friction / Overreach' || val === 'Urgent/Negative') {
      return { label: `Friction (${comp.toFixed(2)})`, cls: 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800' };
    }
    return { label: 'Constitutional Neutral', cls: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700' };
  }

  // Compact bookmark metadata (same shape as orders/[id].astro's compactMeta).
  function bookmarkMeta(order) {
    return {
      id: order.id,
      num: order.num !== undefined ? order.num : order.eo_number,
      sfx: order.sfx || order.eo_suffix || undefined,
      st: order.st || order.eo_status || undefined,
      title: order.title,
      pres: order.pres || order.president_name,
      slug: order.slug || order.president_slug,
      date: order.date || order.signing_date,
      words: order.words || order.word_count || 0,
      time: order.time || order.reading_time_minutes || 1,
      val: order.val || order.sentiment_valence,
      comp: order.comp !== undefined ? order.comp : (order.sentiment_compound || 0),
      tag: order.tag || order.tone_tag,
      snip: order.snip || order.snippet,
    };
  }

  // Single card template for every client-rendered order list. Every
  // data-derived value is escaped; titles and snippets come from scraped text.
  function renderOrderCard(order, opts = {}) {
    const meta = bookmarkMeta(order);
    const badge = sentimentBadge(order);
    const formattedDate = window.formatSigningDate ? window.formatSigningDate(meta.date) : (meta.date || 'Undated');
    const label = eoLabel(order);
    const eoBadge = label
      ? `<span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200 dark:border-blue-900">EO ${escapeHtml(label)}</span>`
      : `<span class="font-mono text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700">Order</span>`;
    const slug = window.resolvePortraitSlug ? window.resolvePortraitSlug(meta.slug) : meta.slug;
    const id = escapeHtml(meta.id);
    const bookmarkBtn = opts.savedView
      ? `<button type="button" data-bookmark-btn="${id}" aria-label="Remove from saved orders" aria-pressed="true" class="p-1 rounded-md text-amber-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
          <svg class="w-4 h-4" fill="currentColor" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
        </button>`
      : `<button type="button" data-bookmark-btn="${id}" data-order-meta="${escapeHtml(JSON.stringify(meta))}" aria-label="Save this order" aria-pressed="false" class="p-1 rounded-md text-slate-400 hover:text-amber-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path></svg>
        </button>`;

    return `
      <article class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-200 flex flex-col justify-between"${opts.savedView ? ` data-saved-card="${id}"` : ''}>
        <div>
          <div class="flex flex-wrap items-center justify-between gap-2 mb-2.5">
            <div class="flex flex-wrap items-center gap-2">
              ${eoBadge}
              ${statusBadge(order)}
              <span class="text-xs font-mono text-slate-500 dark:text-slate-400">${escapeHtml(formattedDate)}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="text-[11px] font-medium px-2 py-0.5 rounded-full border ${badge.cls}">${escapeHtml(badge.label)}</span>
              ${bookmarkBtn}
            </div>
          </div>
          <h3 class="font-serif font-bold text-slate-900 dark:text-white text-base sm:text-lg mb-2 line-clamp-2 hover:text-blue-600 dark:hover:text-blue-400">
            <a href="/orders/${encodeURIComponent(meta.id)}">${escapeHtml(meta.title)}</a>
          </h3>
          ${opts.showTag && meta.tag ? `
            <div class="mb-3">
              <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 border border-amber-200 dark:border-amber-900/60 font-medium">🏛️ ${escapeHtml(meta.tag)}</span>
            </div>` : ''}
          ${meta.snip ? `<p class="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed mb-4">${escapeHtml(meta.snip)}</p>` : ''}
        </div>
        <div class="pt-3 mt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <div class="flex items-center gap-1.5 font-medium min-w-0">
            <img src="/portraits/${escapeHtml(slug)}.jpg" alt="" loading="lazy" class="w-5 h-5 rounded-full object-cover border border-slate-300 dark:border-slate-600" onerror="this.style.display='none'" />
            <span class="text-slate-700 dark:text-slate-300 truncate max-w-[140px] sm:max-w-none">${escapeHtml(meta.pres)}</span>
          </div>
          <div class="flex items-center gap-2 font-mono text-[11px] flex-shrink-0">
            <span title="Estimated Reading Time">⏱ ${escapeHtml(meta.time)}m</span>
            <span class="opacity-40">•</span>
            <span title="Word Count">${Number(meta.words).toLocaleString()} words</span>
          </div>
        </div>
      </article>`;
  }

  // Appends HTML without re-parsing the cards already in the container
  // (container.innerHTML += ... re-serializes and rebuilds every card).
  function appendHtml(container, html) {
    container.insertAdjacentHTML('beforeend', html);
  }

  window.EOSearch = {
    escapeHtml, eoLabel, loadIndex, loadKeywords, parseQuery, scoreOrder, rankOrders,
    statusBadge, renderOrderCard, bookmarkMeta, appendHtml,
  };
})();
