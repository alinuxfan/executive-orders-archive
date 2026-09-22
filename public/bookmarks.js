(function () {
  const STORAGE_KEY = 'eo-bookmarks';

  function getAll() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      return [];
    }
  }

  function isSaved(id) {
    return getAll().includes(id);
  }

  function toggle(id) {
    let all = getAll();
    const saved = all.includes(id);
    all = saved ? all.filter((x) => x !== id) : [...all, id];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
    document.dispatchEvent(new CustomEvent('eo-bookmarks-changed', { detail: { id, saved: !saved, all } }));
    return !saved;
  }

  function updateButtonState(btn) {
    const id = btn.getAttribute('data-bookmark-btn');
    const saved = isSaved(id);
    btn.setAttribute('aria-pressed', String(saved));
    btn.setAttribute('title', saved ? 'Remove from saved orders' : 'Save this order');
    const svg = btn.querySelector('svg');
    if (svg) svg.setAttribute('fill', saved ? 'currentColor' : 'none');
    btn.classList.toggle('text-amber-500', saved);
    btn.classList.toggle('dark:text-amber-400', saved);
    const label = btn.querySelector('[data-bookmark-label]');
    if (label) label.textContent = saved ? 'Saved' : 'Save';
  }

  function refreshAllButtons() {
    document.querySelectorAll('[data-bookmark-btn]').forEach(updateButtonState);
    document.querySelectorAll('[data-bookmark-count]').forEach((el) => {
      el.textContent = String(getAll().length);
      el.classList.toggle('hidden', getAll().length === 0);
    });
  }

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-bookmark-btn]');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    const id = btn.getAttribute('data-bookmark-btn');
    toggle(id);
  });

  document.addEventListener('eo-bookmarks-changed', refreshAllButtons);
  document.addEventListener('DOMContentLoaded', refreshAllButtons);
  refreshAllButtons();

  window.EOBookmarks = { getAll, isSaved, toggle, refreshAllButtons };
})();

// Some harvested orders report a president identifier that doesn't match the
// canonical slug used for portrait filenames (e.g. Trump's two non-consecutive
// terms, or "george-bush" for the 41st president). Mirrors src/lib/portraits.ts.
(function () {
  const PORTRAIT_SLUG_ALIASES = {
    'george-bush': 'george-h-w-bush',
    'donald-j-trump-1st-term': 'donald-trump',
    'donald-j-trump-2nd-term': 'donald-trump',
    'gerald-r-ford': 'gerald-ford',
    'joseph-r-biden-jr': 'joe-biden',
    'william-j-clinton': 'bill-clinton'
  };

  window.resolvePortraitSlug = function (slug) {
    if (!slug) return 'default';
    return PORTRAIT_SLUG_ALIASES[slug] || slug;
  };
})();
