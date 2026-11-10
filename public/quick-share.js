// Quick Share Hub Client Controller
(function() {
const modal = document.getElementById('quick-share-modal');
  const closeBtn = document.getElementById('quick-share-close-btn');
  const modalDateBadge = document.getElementById('modal-date-badge');
  const tabBtns = document.querySelectorAll('.quick-tab-btn');
  const submodeBtns = document.querySelectorAll('.submode-btn');
  const submodeTodayControls = document.getElementById('submode-today-controls');
  const submodeMilestonesControls = document.getElementById('submode-milestones-controls');
  const submodeRouletteControls = document.getElementById('submode-roulette-controls');
  const submodeLatestYear = document.getElementById('submode-latest-year');
  const submodeOldestYear = document.getElementById('submode-oldest-year');
  const categoryBadge = document.getElementById('preview-category-badge');
  const scoreBadge = document.getElementById('preview-score-badge');
  const previewTitle = document.getElementById('preview-title');
  const previewSnippet = document.getElementById('preview-snippet');
  const previewPortrait = document.getElementById('preview-portrait');
  const previewPresident = document.getElementById('preview-president');
  const previewDate = document.getElementById('preview-date');
  const previewViewLink = document.getElementById('preview-view-link');
  const shareTextOutput = document.getElementById('share-text-output');
  const nativeShareBtn = document.getElementById('modal-native-share-btn');
  const copyTextBtn = document.getElementById('modal-copy-text-btn');
  const copyLinkBtn = document.getElementById('modal-copy-link-btn');
  const xLink = document.getElementById('modal-x-link');
  const redditLink = document.getElementById('modal-reddit-link');
  const threadsLink = document.getElementById('modal-threads-link');
  const bskyLink = document.getElementById('modal-bsky-link');
  const linkedinLink = document.getElementById('modal-linkedin-link');
  const facebookLink = document.getElementById('modal-facebook-link');
  const whatsappLink = document.getElementById('modal-whatsapp-link');
  const emailLink = document.getElementById('modal-email-link');
  const rouletteSpinBtn = document.getElementById('roulette-spin-btn');
  const spinDiceIcon = document.getElementById('spin-dice-icon');
  const milestoneBtns = document.querySelectorAll('.milestone-pick-btn');
  const toast = document.getElementById('quick-share-toast');
  const toastMsg = document.getElementById('quick-share-toast-msg');

  // Dynamic seed data loader
  let seedData = { todayOrders: [], milestones: [], rouletteSeed: [], dateInfo: {} };
  let seedDataPromise = null;

  function loadSeedData() {
    if (!seedDataPromise) {
      seedDataPromise = fetch('/quick-share-data.json')
        .then(r => r.json())
        .then(data => {
          if (data) {
            seedData = data;
            if (!activeDateOrders || activeDateOrders.length === 0) {
              activeDateOrders = seedData.todayOrders || [];
            }
            if (!currentDate || !currentDate.monthName) {
              currentDate = seedData.dateInfo || {};
            }
            if (modalDateBadge && currentDate.monthName && currentDate.dayInt) {
              modalDateBadge.textContent = currentDate.monthName + ' ' + currentDate.dayInt;
            }
            if (submodeLatestYear && activeDateOrders.length > 0) {
              const latest = activeDateOrders[0];
              submodeLatestYear.textContent = latest.signing_date ? latest.signing_date.slice(0, 4) : 'Recent';
            }
            if (submodeOldestYear && activeDateOrders.length > 0) {
              const oldest = activeDateOrders[activeDateOrders.length - 1];
              submodeOldestYear.textContent = oldest.signing_date ? oldest.signing_date.slice(0, 4) : 'Earliest';
            }
          }
          return seedData;
        })
        .catch(err => {
          console.error('Failed to load quick-share seed data', err);
          return seedData;
        });
    }
    return seedDataPromise;
  }

  // Preload on idle or trigger hover
  if (typeof window !== 'undefined') {
    if ('requestIdleCallback' in window) {
      window.requestIdleCallback(() => loadSeedData());
    } else {
      setTimeout(loadSeedData, 1000);
    }
    document.addEventListener('pointerenter', (e) => {
      if (e.target && e.target.closest && (e.target.closest('[data-open-quick-share]') || e.target.closest('[data-quick-share-type]'))) {
        loadSeedData();
      }
    }, { passive: true });
  }

  // Modal state. The modal is closed/open via the `hidden` class on #quick-share-modal;
  // while open, what it previews is (activeTab, activeSubmode, customOrder):
  //   tab 'today'      -> submode 'latest' | 'oldest' | 'random' | 'summary' over activeDateOrders,
  //                       unless customOrder (an order picked from a card) overrides it
  //   tab 'milestones' -> seedData.milestones[activeMilestoneIndex]
  //   tab 'roulette'   -> customOrder (set by rollRoulette)
  // openModal() is the single transition entry point; it repaints tab/submode buttons.
  let activeTab = 'today'; // 'today' | 'milestones' | 'roulette'
  let activeSubmode = 'latest'; // 'latest' | 'oldest' | 'random' | 'summary'
  let activeMilestoneIndex = 0;
  let customOrder = null; // Specific order picked from page
  let randomTodayOrder = null; // Sticky pick for submode 'random'; cleared when the date changes
  let activeDateOrders = seedData.todayOrders || [];
  let currentDate = seedData.dateInfo || {};
  let fullSearchData = null;
  let lastFocusedTrigger = null;

  function showToast(msg) {
    if (!toast) return;
    if (toastMsg) toastMsg.textContent = msg;
    toast.classList.remove('opacity-0');
    toast.classList.add('opacity-100');
    setTimeout(() => {
      toast.classList.remove('opacity-100');
      toast.classList.add('opacity-0');
    }, 2200);
  }

  function getBaseSiteUrl() {
    return window.location.origin || 'https://executiveordersarchive.org';
  }

  function resolvePortrait(slug) {
    if (window.resolvePortraitSlug) return window.resolvePortraitSlug(slug);
    return slug || 'default';
  }

  function formatSigningDateClean(dateStr) {
    if (!dateStr) return '';
    try {
      const parts = dateStr.slice(0, 10).split('-').map(Number);
      if (parts.length === 3 && !parts.some(isNaN)) {
        const dt = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
        return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
      }
      return dateStr.slice(0, 4);
    } catch (e) {
      return dateStr.slice(0, 4);
    }
  }

  function formatScore(order) {
    if (!order) return '';
    const rawScore = order.sentiment_compound !== undefined ? order.sentiment_compound : (order.comp !== undefined ? order.comp : null);
    if (rawScore === null || rawScore === undefined) return '';
    const num = Number(rawScore);
    if (isNaN(num)) return '';
    return ` (${num >= 0 ? '+' : ''}${num.toFixed(2)})`;
  }

  function classifyYoungstown(order) {
    if (!order) {
      return {
        zone: 2,
        name: 'Zone 2: Zone of Twilight',
        shortName: 'Zone 2 (Zone of Twilight)'
      };
    }

    const valence = order.val || order.sentiment_valence || '';
    const comp = order.comp !== undefined ? order.comp : (order.sentiment_compound !== undefined ? order.sentiment_compound : 0);
    const toneTag = order.tag || order.tone_tag || '';
    const title = (order.title || '').toLowerCase();

    // Zone 3: Lowest Ebb / Severe Constitutional Friction / Incompatible with Congressional Will
    const isZone3 = 
      valence === 'Constitutional Friction / Overreach' ||
      valence === 'Urgent/Negative' ||
      comp <= -0.08 ||
      toneTag.includes('Tension') ||
      toneTag.includes('Scrutiny') ||
      title.includes('habeas corpus') ||
      title.includes('martial law') ||
      title.includes('taking into military possession') ||
      title.includes('confiscating and vesting');

    if (isZone3) {
      return {
        zone: 3,
        name: 'Zone 3: Lowest Ebb',
        shortName: 'Zone 3 (Lowest Ebb)',
        tagline: 'Incompatible with Expressed Will of Congress or High Friction'
      };
    }

    // Zone 1: Maximum Authority / Statutory Execution
    const isZone1 =
      valence === 'Constitutional Fidelity' ||
      valence === 'Positive' ||
      comp >= 0.08 ||
      toneTag.includes('Faithful Execution') ||
      toneTag.includes('Delegated') ||
      toneTag.includes('Intergovernmental Federalism') ||
      title.includes('pursuant to') ||
      title.includes('authorized by');

    if (isZone1) {
      return {
        zone: 1,
        name: 'Zone 1: Maximum Authority',
        shortName: 'Zone 1 (Maximum Authority)',
        tagline: 'Express or Implied Congressional Authorization'
      };
    }

    // Zone 2: Zone of Twilight / Concurrent Authority / Congressional Silence
    return {
      zone: 2,
      name: 'Zone 2: Zone of Twilight',
      shortName: 'Zone 2 (Zone of Twilight)',
      tagline: 'Concurrent Authority / Congressional Silence'
    };
  }

  // Generate rich share text & tweet text
  function generateSharePayload() {
    const siteUrl = getBaseSiteUrl();

    if (activeTab === 'today') {
      if (activeSubmode === 'summary') {
        const count = activeDateOrders.length;
        const oldest = activeDateOrders.length > 0 ? activeDateOrders[activeDateOrders.length - 1] : null;
        const latest = activeDateOrders.length > 0 ? activeDateOrders[0] : null;
        const oldestYear = oldest?.signing_date ? oldest.signing_date.slice(0, 4) : (oldest?.date ? oldest.date.slice(0, 4) : '');
        const latestYear = latest?.signing_date ? latest.signing_date.slice(0, 4) : (latest?.date ? latest.date.slice(0, 4) : '');

        let zone1Count = 0;
        let zone2Count = 0;
        let zone3Count = 0;
        let fidelityCount = 0;
        let frictionCount = 0;
        let neutralCount = 0;

        activeDateOrders.forEach(o => {
          const z = classifyYoungstown(o).zone;
          if (z === 1) zone1Count++;
          else if (z === 3) zone3Count++;
          else zone2Count++;

          const val = o.sentiment_valence || o.val || '';
          if (val.includes('Fidelity') || val.includes('Positive')) fidelityCount++;
          else if (val.includes('Friction') || val.includes('Urgent') || val.includes('Negative')) frictionCount++;
          else neutralCount++;
        });

        const summaryUrl = `${siteUrl}/#this-day-section`;
        const prefixLine = `U.S. Executive Orders Daily Digest (${currentDate.monthName} ${currentDate.dayInt})`;

        const bodyLines = [
          prefixLine,
          '',
          `On This Day in Presidential History:`,
          count > 0 ? `• Total: ${count} U.S. Executive Order${count === 1 ? '' : 's'} signed across history${oldestYear && latestYear ? ` (${oldestYear} – ${latestYear})` : ''}` : `• Exploring executive actions signed on this calendar date.`
        ];
        if (oldest) {
          bodyLines.push(`• Oldest: "${oldest.title}" (${oldest.president_name || oldest.pres}, ${oldestYear})`);
        }
        if (latest && latest.id !== oldest?.id) {
          bodyLines.push(`• Latest: "${latest.title}" (${latest.president_name || latest.pres}, ${latestYear})`);
        }
        if (count > 0) {
          bodyLines.push('');
          bodyLines.push('⚖️ Constitutional Alignment Overview:');
          bodyLines.push(`• Separation of Powers: ${zone1Count} Zone 1 (Statutory) • ${zone2Count} Zone 2 (Twilight) • ${zone3Count} Zone 3 (Friction)`);
          const dominantValence = frictionCount > fidelityCount && frictionCount > neutralCount 
            ? 'Constitutional Friction / Scrutiny' 
            : (fidelityCount >= frictionCount && fidelityCount >= neutralCount ? 'Constitutional Fidelity' : 'Constitutional Neutral / Procedural');
          bodyLines.push(`• Prevailing Valence: ${dominantValence} (${fidelityCount} Fidelity, ${frictionCount} Friction, ${neutralCount} Neutral)`);
        }
        bodyLines.push('');
        bodyLines.push(`Explore historical context & constitutional scoring:`);

        const shareBody = bodyLines.join('\n');
        const text = `${shareBody}\n${summaryUrl}`;
        const tweet = `${prefixLine}\nOn This Day: ${count} historic decrees spanning ${oldestYear}–${latestYear}.\n⚖️ Zones: ${zone1Count} Z1 • ${zone2Count} Z2 • ${zone3Count} Z3\nExplore historical context & constitutional scoring:`;

        return {
          title: prefixLine,
          text,
          shareBody,
          tweetText: tweet,
          url: summaryUrl
        };
      }

      const order = getActiveTodayOrder();
      if (!order) {
        return {
          title: `Executive Orders Archive`,
          text: `Explore presidential executive orders on Executive Orders Archive:\n${siteUrl}`,
          shareBody: `Explore presidential executive orders on Executive Orders Archive:`,
          tweetText: `Explore presidential executive orders on Executive Orders Archive`,
          url: siteUrl
        };
      }

      const year = order.signing_date ? order.signing_date.slice(0, 4) : (order.date ? order.date.slice(0, 4) : '');
      const formattedDate = formatSigningDateClean(order.signing_date || order.date);
      const eoLabel = (order.eo_number !== undefined && order.eo_number !== null) ? `U.S. Executive Order ${order.eo_number}` : (order.num ? `U.S. Executive Order ${order.num}` : 'U.S. Executive Order');
      const presName = order.president_name || order.pres || '';
      const valence = order.sentiment_valence || order.val || '';
      const yst = classifyYoungstown(order);
      const scoreStr = formatScore(order);
      const toneTag = order.tone_tag || order.tag || '';
      const orderUrl = `${siteUrl}/orders/${order.id}`;

      let prefixLine = '';
      if (!customOrder) {
        if (activeSubmode === 'latest') {
          prefixLine = `Latest U.S. Executive Order (${year || 'Recent'})`;
        } else if (activeSubmode === 'oldest') {
          prefixLine = `Oldest U.S. Executive Order (${year || 'Earliest'})`;
        } else if (activeSubmode === 'random') {
          prefixLine = `Random U.S. Executive Order from this day in ${year || 'History'}`;
        }
      }

      const bodyLines = [];
      if (prefixLine) {
        bodyLines.push(prefixLine);
        bodyLines.push('');
      }
      bodyLines.push(`${eoLabel}: "${order.title}"`);
      if (presName) {
        bodyLines.push(`Signed by ${presName}${formattedDate ? ` (${formattedDate})` : (year ? ` (${year})` : '')}`);
      }
      bodyLines.push('');
      bodyLines.push(`⚖️ Constitutional Alignment:`);
      if (yst.name) {
        const tagSuffix = yst.tagline ? ` (${yst.tagline})` : '';
        bodyLines.push(`• Separation of Powers: ${yst.name}${tagSuffix}`);
      }
      if (toneTag) {
        bodyLines.push(`• Constitutional Authority: ${toneTag}`);
      }
      if (valence) {
        bodyLines.push(`• Constitutional Valence: ${valence}${scoreStr}`);
      }
      bodyLines.push('');
      bodyLines.push(`Explore historical context & constitutional scoring:`);

      const shareBody = bodyLines.join('\n');
      const text = `${shareBody}\n${orderUrl}`;

      const shortTitle = order.title.length > 55 ? order.title.substring(0, 52).trim() + '...' : order.title;
      const zoneShort = yst.zone ? `Zone ${yst.zone}` : '';
      const valenceShort = valence ? `${valence}${scoreStr}` : '';
      const alignShort = [zoneShort, valenceShort].filter(Boolean).join(' • ');

      const tweetPrefix = prefixLine ? `${prefixLine}\n` : '';
      const tweetText = `${tweetPrefix}${order.eo_number || order.num ? `U.S. EO ${order.eo_number || order.num}` : 'U.S. Order'}${presName ? ` (${presName})` : ''}: "${shortTitle}"\n⚖️ Alignment: ${alignShort}${toneTag ? `\n📜 Authority: ${toneTag}` : ''}`;

      return {
        title: `${eoLabel}: ${order.title}`,
        text,
        shareBody,
        tweetText,
        url: orderUrl
      };
    }

    if (activeTab === 'milestones') {
      const milestone = seedData.milestones?.[activeMilestoneIndex];
      const order = milestone?.order;
      if (!order) return { title: 'Milestone', text: '', shareBody: '', tweetText: '', url: siteUrl };

      const orderUrl = `${siteUrl}/orders/${order.id}`;
      const year = order.signing_date ? order.signing_date.slice(0, 4) : '';
      const formattedDate = formatSigningDateClean(order.signing_date);
      const eoLabel = (order.eo_number !== undefined && order.eo_number !== null) ? `U.S. Executive Order ${order.eo_number}` : (order.num ? `U.S. Executive Order ${order.num}` : 'U.S. Executive Order');
      const presName = order.president_name || order.pres || '';
      const valence = order.sentiment_valence || order.val || '';
      const yst = classifyYoungstown(order);
      const scoreStr = formatScore(order);
      const toneTag = order.tone_tag || order.tag || '';

      const prefixLine = `${milestone.badge}: ${milestone.shortLabel}`;
      const bodyLines = [
        prefixLine,
        '',
        `${eoLabel}: "${order.title}"`,
        presName ? `Signed by ${presName}${formattedDate ? ` (${formattedDate})` : (year ? ` (${year})` : '')}` : '',
        '',
        `⚖️ Constitutional Alignment:`,
        `• Separation of Powers: ${yst.name} (${yst.tagline})`,
        toneTag ? `• Constitutional Authority: ${toneTag}` : null,
        `• Constitutional Valence: ${valence}${scoreStr}`,
        `• Landmark Note: ${milestone.description}`,
        '',
        `Explore historical context & constitutional scoring:`
      ].filter(line => line !== null && line !== undefined);

      const shareBody = bodyLines.join('\n');
      const text = `${shareBody}\n${orderUrl}`;

      const shortTitle = order.title.length > 55 ? order.title.substring(0, 52).trim() + '...' : order.title;
      const zoneShort = yst.zone ? `Zone ${yst.zone}` : '';
      const valenceShort = valence ? `${valence}${scoreStr}` : '';
      const alignShort = [zoneShort, valenceShort].filter(Boolean).join(' • ');

      const tweetText = `${milestone.badge}: ${eoLabel} "${shortTitle}" (${order.president_name}, ${year})\n⚖️ Alignment: ${alignShort}`;

      return {
        title: `${milestone.shortLabel} — Executive Orders Archive`,
        text,
        shareBody,
        tweetText,
        url: orderUrl
      };
    }

    // Archive Roulette Pick
    const order = customOrder || seedData.rouletteSeed?.[0];
    if (!order) return { title: 'Executive Order', text: '', shareBody: '', tweetText: '', url: siteUrl };

    const orderUrl = `${siteUrl}/orders/${order.id}`;
    const year = order.signing_date ? order.signing_date.slice(0, 4) : (order.date ? order.date.slice(0, 4) : '');
    const formattedDate = formatSigningDateClean(order.signing_date || order.date);
    const eoLabel = (order.eo_number !== undefined && order.eo_number !== null) ? `U.S. Executive Order ${order.eo_number}` : (order.num ? `U.S. Executive Order ${order.num}` : 'U.S. Executive Order');
    const presName = order.president_name || order.pres || '';
    const valence = order.sentiment_valence || order.val || '';
    const yst = classifyYoungstown(order);
    const scoreStr = formatScore(order);
    const toneTag = order.tone_tag || order.tag || '';

    const prefixLine = `Random U.S. Executive Order (${year || 'Archive Discovery'})`;
    const bodyLines = [
      prefixLine,
      '',
      `${eoLabel}: "${order.title}"`,
      presName ? `Signed by ${presName}${formattedDate ? ` (${formattedDate})` : (year ? ` (${year})` : '')}` : '',
      '',
      `⚖️ Constitutional Alignment:`,
      `• Separation of Powers: ${yst.name} (${yst.tagline})`,
      toneTag ? `• Constitutional Authority: ${toneTag}` : null,
      `• Constitutional Valence: ${valence}${scoreStr}`,
      '',
      `Explore historical context & constitutional scoring:`
    ].filter(line => line !== null && line !== undefined);

    const shareBody = bodyLines.join('\n');
    const text = `${shareBody}\n${orderUrl}`;

    const shortTitle = order.title.length > 55 ? order.title.substring(0, 52).trim() + '...' : order.title;
    const zoneShort = yst.zone ? `Zone ${yst.zone}` : '';
    const valenceShort = valence ? `${valence}${scoreStr}` : '';
    const alignShort = [zoneShort, valenceShort].filter(Boolean).join(' • ');

    const tweetText = `${prefixLine}\n${eoLabel} (${presName}): "${shortTitle}"\n⚖️ Alignment: ${alignShort}`;

    return {
      title: `${eoLabel}: ${order.title}`,
      text,
      shareBody,
      tweetText,
      url: orderUrl
    };
  }

  function getActiveTodayOrder() {
    if (customOrder && activeTab === 'today') return customOrder;
    if (!activeDateOrders || activeDateOrders.length === 0) return null;
    if (activeSubmode === 'latest') return activeDateOrders[0];
    if (activeSubmode === 'oldest') return activeDateOrders[activeDateOrders.length - 1];
    if (activeSubmode === 'random') {
      if (!randomTodayOrder || !activeDateOrders.includes(randomTodayOrder)) {
        randomTodayOrder = activeDateOrders[Math.floor(Math.random() * activeDateOrders.length)];
      }
      return randomTodayOrder;
    }
    return activeDateOrders[0];
  }

  // Update Preview UI
  function updateModalUI() {
    const payload = generateSharePayload();
    if (shareTextOutput) {
      shareTextOutput.value = payload.text;
    }

    // Social URLs
    const encUrl = encodeURIComponent(payload.url);
    const encText = encodeURIComponent(payload.tweetText);
    const encBsky = encodeURIComponent(`${payload.tweetText}\n${payload.url}`);

    const shareTitle = encodeURIComponent(payload.title || payload.tweetText.split('\n')[0] || 'U.S. Executive Order');
    const encFullBody = encodeURIComponent(`${payload.text}\n\n${payload.url}`);

    if (xLink) xLink.href = `https://twitter.com/intent/tweet?url=${encUrl}&text=${encText}`;
    if (redditLink) redditLink.href = `https://www.reddit.com/submit?url=${encUrl}&title=${shareTitle}`;
    if (threadsLink) threadsLink.href = `https://www.threads.net/intent/post?text=${encBsky}`;
    if (bskyLink) bskyLink.href = `https://bsky.app/intent/compose?text=${encBsky}`;
    if (linkedinLink) linkedinLink.href = `https://www.linkedin.com/sharing/share-offsite/?url=${encUrl}`;
    if (facebookLink) facebookLink.href = `https://www.facebook.com/sharer/sharer.php?u=${encUrl}`;
    if (whatsappLink) whatsappLink.href = `https://api.whatsapp.com/send?text=${encBsky}`;
    if (emailLink) emailLink.href = `mailto:?subject=${shareTitle}&body=${encFullBody}`;

    // Update Card UI
    if (activeTab === 'today') {
      if (activeSubmode === 'summary') {
        const count = activeDateOrders.length;
        const oldest = activeDateOrders.length > 0 ? activeDateOrders[activeDateOrders.length - 1] : null;
        const latest = activeDateOrders.length > 0 ? activeDateOrders[0] : null;
        const oldestYear = oldest?.signing_date ? oldest.signing_date.slice(0, 4) : (oldest?.date ? oldest.date.slice(0, 4) : '');
        const latestYear = latest?.signing_date ? latest.signing_date.slice(0, 4) : (latest?.date ? latest.date.slice(0, 4) : '');

        if (categoryBadge) categoryBadge.textContent = `📜 Historic Day Digest`;
        if (scoreBadge) {
          scoreBadge.textContent = `${count} Orders Found`;
          scoreBadge.className = `text-[10px] font-medium px-2 py-0.5 rounded-full border text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900`;
        }
        if (previewTitle) previewTitle.textContent = `Presidential Executive Actions on ${currentDate.monthName} ${currentDate.dayInt}`;
        if (previewSnippet) {
          previewSnippet.textContent = count > 0 ? 
            `From ${oldest?.president_name || 'Early Presidents'} in ${oldestYear || 'early history'} to ${latest?.president_name || 'Modern Presidents'} in ${latestYear || 'recent times'}, discover all ${count} decrees signed on this day.` :
            `No executive orders recorded on this calendar date. Try another date in the date picker!`;
        }
        if (previewPortrait) previewPortrait.src = `/portraits/george-washington.jpg`;
        if (previewPresident) previewPresident.textContent = `United States Presidents`;
        if (previewDate) previewDate.textContent = `(${currentDate.monthName} ${currentDate.dayInt})`;
        if (previewViewLink) {
          previewViewLink.href = `/#this-day-section`;
          previewViewLink.innerHTML = `<span>Browse Section</span> <span>&rarr;</span>`;
        }
        return;
      }

      const order = getActiveTodayOrder();
      const year = order?.signing_date ? order.signing_date.slice(0, 4) : (order?.date ? order.date.slice(0, 4) : '');
      const badgeText = customOrder ?
        `📅 U.S. Executive Order (${year || 'Historic'})` :
        (activeSubmode === 'latest' ? `⚡ Latest U.S. Executive Order (${year || 'Recent'})` : activeSubmode === 'oldest' ? `🏛️ Oldest U.S. Executive Order (${year || 'Earliest'})` : `🎲 Random U.S. Executive Order (${year || 'History'})`);
      renderOrderInPreview(order, badgeText);
      return;
    }

    if (activeTab === 'milestones') {
      const milestone = seedData.milestones?.[activeMilestoneIndex];
      if (milestone && milestone.order) {
        renderOrderInPreview(milestone.order, milestone.badge, milestone.description);
      }
      return;
    }

    if (activeTab === 'roulette') {
      const order = customOrder || seedData.rouletteSeed?.[0];
      const year = order?.signing_date ? order.signing_date.slice(0, 4) : (order?.date ? order.date.slice(0, 4) : '');
      renderOrderInPreview(order, `🎲 Random U.S. Executive Order (${year || 'Discovery'})`);
      return;
    }
  }

  function renderOrderInPreview(order, badgeText, customDesc) {
    if (!order) {
      if (categoryBadge) categoryBadge.textContent = badgeText || 'Executive Order';
      if (scoreBadge) scoreBadge.textContent = 'None';
      if (previewTitle) previewTitle.textContent = 'No Order Available';
      if (previewSnippet) previewSnippet.textContent = 'No orders available for this selection.';
      return;
    }

    const presName = order.president_name || order.pres || 'President';
    const presSlug = order.president_slug || order.slug || '';
    const valence = order.sentiment_valence || order.val || 'Executive Order';
    const yst = classifyYoungstown(order);
    const scoreStr = formatScore(order);

    if (categoryBadge) categoryBadge.textContent = badgeText || 'Executive Order';
    if (scoreBadge) {
      scoreBadge.textContent = `${yst.shortName} • ${valence}${scoreStr}`;
      let colorClass = "text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700";
      if (yst.zone === 1) {
        colorClass = "text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/40";
      } else if (yst.zone === 3) {
        colorClass = "text-rose-700 dark:text-rose-300 border-rose-300 dark:border-rose-800 bg-rose-50 dark:bg-rose-950/40";
      } else {
        colorClass = "text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/40";
      }
      scoreBadge.className = `text-[10px] font-medium px-2 py-0.5 rounded-full border ${colorClass}`;
    }

    if (previewTitle) previewTitle.textContent = order.title || 'Executive Order';
    if (previewSnippet) previewSnippet.textContent = customDesc || order.snippet || order.snip || 'Plain-English summary and constitutional scoring available on Executive Orders Archive.';
    if (previewPortrait) {
      previewPortrait.style.display = '';
      previewPortrait.src = `/portraits/${resolvePortrait(presSlug)}.jpg`;
    }
    if (previewPresident) previewPresident.textContent = presName;
    if (previewDate) previewDate.textContent = `(${formatSigningDateClean(order.signing_date || order.date)})`;
    if (previewViewLink) {
      previewViewLink.href = `/orders/${encodeURIComponent(order.id || '')}`;
      previewViewLink.innerHTML = `<span>View Full Order</span> <span>&rarr;</span>`;
    }
  }

  // Open modal
  async function openModal(tab = 'today', submode = 'latest', custom = null) {
    await loadSeedData();
    if (modal?.classList.contains('hidden')) {
      lastFocusedTrigger = document.activeElement;
    }
    activeTab = tab;
    activeSubmode = submode;
    customOrder = custom;

    // Switch tab buttons
    tabBtns.forEach(btn => {
      const match = btn.getAttribute('data-quick-tab') === tab;
      btn.classList.toggle('active', match);
      btn.classList.toggle('bg-blue-50', match);
      btn.classList.toggle('dark:bg-blue-950/60', match);
      btn.classList.toggle('text-blue-700', match);
      btn.classList.toggle('dark:text-blue-300', match);
      btn.classList.toggle('border-blue-300', match);
      btn.classList.toggle('dark:border-blue-800', match);
      btn.classList.toggle('border-transparent', !match);
    });

    // Toggle controls
    submodeTodayControls?.classList.toggle('hidden', tab !== 'today');
    submodeMilestonesControls?.classList.toggle('hidden', tab !== 'milestones');
    submodeRouletteControls?.classList.toggle('hidden', tab !== 'roulette');

    // Switch submodes
    submodeBtns.forEach(btn => {
      const match = !customOrder && btn.getAttribute('data-submode') === submode;
      btn.classList.toggle('active', match);
      btn.classList.toggle('bg-amber-50/80', match);
      btn.classList.toggle('dark:bg-amber-950/40', match);
      btn.classList.toggle('border-amber-300', match);
      btn.classList.toggle('dark:border-amber-800', match);
      btn.classList.toggle('text-amber-900', match);
      btn.classList.toggle('dark:text-amber-200', match);
      btn.classList.toggle('border-slate-200', !match);
      btn.classList.toggle('dark:border-slate-800', !match);
    });

    if (tab === 'roulette' && !customOrder) {
      rollRoulette();
    }

    updateModalUI();
    modal?.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    setTimeout(() => closeBtn?.focus(), 20);
  }

  function closeModal() {
    modal?.classList.add('hidden');
    document.body.style.overflow = '';
    if (lastFocusedTrigger && typeof lastFocusedTrigger.focus === 'function') {
      try { lastFocusedTrigger.focus(); } catch (e) {}
    }
    lastFocusedTrigger = null;
  }

  // Roll archive roulette
  async function rollRoulette() {
    spinDiceIcon?.classList.add('animate-spin');
    setTimeout(() => spinDiceIcon?.classList.remove('animate-spin'), 600);

    // Try picking from search index if available
    if (fullSearchData && fullSearchData.length > 0) {
      const pick = fullSearchData[Math.floor(Math.random() * fullSearchData.length)];
      customOrder = {
        id: pick.id,
        eo_number: pick.num,
        title: pick.title,
        president_name: pick.pres,
        president_slug: pick.slug,
        signing_date: pick.date,
        sentiment_valence: pick.val,
        sentiment_compound: pick.comp,
        tone_tag: pick.tag || '',
        snippet: pick.snip || ''
      };
    } else if (seedData.rouletteSeed && seedData.rouletteSeed.length > 0) {
      const pick = seedData.rouletteSeed[Math.floor(Math.random() * seedData.rouletteSeed.length)];
      customOrder = pick;
      // Preload search index via shared EOSearch singleton for subsequent rolls
      const loader = window.EOSearch?.loadIndex
        ? window.EOSearch.loadIndex()
        : fetch('/search_index.json').then(r => r.json());
      loader.then(d => { fullSearchData = d; }).catch(() => {});
    }

    updateModalUI();
  }

  // Update date & sync orders
  function updateDateContext(dateInfo, orders) {
    currentDate = dateInfo;
    activeDateOrders = orders || [];
    if (modalDateBadge) {
      modalDateBadge.textContent = `${dateInfo.monthName} ${dateInfo.dayInt}`;
    }

    const latest = activeDateOrders.length > 0 ? activeDateOrders[0] : null;
    const oldest = activeDateOrders.length > 0 ? activeDateOrders[activeDateOrders.length - 1] : null;

    if (submodeLatestYear) {
      submodeLatestYear.textContent = latest?.signing_date ? latest.signing_date.slice(0, 4) : 'Recent';
    }
    if (submodeOldestYear) {
      submodeOldestYear.textContent = oldest?.signing_date ? oldest.signing_date.slice(0, 4) : 'Earliest';
    }

    randomTodayOrder = null;
    if (activeTab === 'today') {
      updateModalUI();
    }
  }

  // Event Listeners
  closeBtn?.addEventListener('click', closeModal);

  modal?.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  window.addEventListener('keydown', (e) => {
    if (!modal || modal.classList.contains('hidden')) return;
    if (e.key === 'Escape') {
      closeModal();
      return;
    }
    if (e.key === 'Tab') {
      const focusable = Array.from(
        modal.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])')
      ).filter(el => el.offsetParent !== null);
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      customOrder = null;
      const tab = btn.getAttribute('data-quick-tab');
      if (tab) openModal(tab, tab === 'today' ? activeSubmode : 'latest');
    });
  });

  submodeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      customOrder = null;
      const sub = btn.getAttribute('data-submode');
      if (sub === 'random') {
        // Pick new random on date
        if (activeDateOrders && activeDateOrders.length > 0) {
          randomTodayOrder = activeDateOrders[Math.floor(Math.random() * activeDateOrders.length)];
        }
      }
      openModal('today', sub);
    });
  });

  milestoneBtns.forEach((btn, idx) => {
    btn.addEventListener('click', () => {
      activeMilestoneIndex = idx;
      milestoneBtns.forEach((b, i) => {
        b.classList.toggle('active', i === idx);
        b.classList.toggle('bg-blue-50/80', i === idx);
        b.classList.toggle('dark:bg-blue-950/40', i === idx);
        b.classList.toggle('border-blue-400', i === idx);
        b.classList.toggle('dark:border-blue-700', i === idx);
        b.classList.toggle('font-semibold', i === idx);
      });
      updateModalUI();
    });
  });

  rouletteSpinBtn?.addEventListener('click', rollRoulette);

  // Native share / rich copy
  nativeShareBtn?.addEventListener('click', async () => {
    const payload = generateSharePayload();
    if (typeof navigator !== 'undefined' && typeof navigator.share === 'function') {
      try {
        await navigator.share({
          title: payload.title,
          text: payload.shareBody || payload.text,
          url: payload.url
        });
        return;
      } catch (err) {
        if (err?.name === 'AbortError') return;
      }
    }

    // Fallback: copy to clipboard (contains exactly one link at the end)
    try {
      await navigator.clipboard.writeText(payload.text);
      showToast('Summary and link copied to clipboard!');
    } catch (e) {
      showToast('Failed to copy');
    }
  });

  // Copy formatted text
  copyTextBtn?.addEventListener('click', async () => {
    const payload = generateSharePayload();
    try {
      await navigator.clipboard.writeText(payload.text);
      showToast('Formatted post copied to clipboard!');
    } catch (e) {
      showToast('Failed to copy');
    }
  });

  // Copy clean link
  copyLinkBtn?.addEventListener('click', async () => {
    const payload = generateSharePayload();
    try {
      await navigator.clipboard.writeText(payload.url);
      showToast('Clean link copied to clipboard!');
    } catch (e) {
      showToast('Failed to copy');
    }
  });

  // Global listeners for buttons on the page
  document.addEventListener('click', (e) => {
    // Open trigger without specific type
    const trigger = e.target.closest('[data-open-quick-share]');
    if (trigger) {
      e.preventDefault();
      openModal('today', 'latest');
      return;
    }

    // Quick share type trigger
    const typeBtn = e.target.closest('[data-quick-share-type]');
    if (typeBtn) {
      e.preventDefault();
      const type = typeBtn.getAttribute('data-quick-share-type');
      if (type === 'latest') openModal('today', 'latest');
      else if (type === 'oldest') openModal('today', 'oldest');
      else if (type === 'random-date') {
        if (activeDateOrders && activeDateOrders.length > 0) {
          randomTodayOrder = activeDateOrders[Math.floor(Math.random() * activeDateOrders.length)];
        }
        openModal('today', 'random');
      }
      else if (type === 'summary') openModal('today', 'summary');
      else if (type === 'milestones') openModal('milestones', 'latest');
      else if (type === 'roulette') openModal('roulette', 'latest');
      else openModal('today', 'latest');
      return;
    }

    // Order card share trigger
    const cardBtn = e.target.closest('[data-card-share-btn]');
    if (cardBtn) {
      e.preventDefault();
      e.stopPropagation();
      const orderId = cardBtn.getAttribute('data-order-id');
      const orderMeta = cardBtn.getAttribute('data-order-meta');
      let order = null;
      if (orderMeta) {
        try { order = JSON.parse(orderMeta); } catch (err) {}
      }
      if (!order && activeDateOrders) {
        order = activeDateOrders.find(o => o.id === orderId);
      }
      if (order) {
        openModal('today', 'latest', order);
      } else {
        openModal('today', 'latest');
      }
      return;
    }
  });

  // Listen for custom date change events from ThisDayInHistory
  document.addEventListener('eo-this-day-updated', (e) => {
    const detail = e.detail;
    if (detail && detail.dateInfo && detail.orders) {
      updateDateContext(detail.dateInfo, detail.orders);
    }
  });

  // Pick up initial state if ThisDayInHistory updated before modal listener was registered
  if (window._currentThisDayState && window._currentThisDayState.dateInfo && window._currentThisDayState.orders) {
    updateDateContext(window._currentThisDayState.dateInfo, window._currentThisDayState.orders);
  }

  // Expose global controller
  window.EOQuickShare = {
    open: openModal,
    close: closeModal,
    setTodayOrders: updateDateContext
  };
})();
