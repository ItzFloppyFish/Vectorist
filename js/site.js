/* ==========================================================================
   Vectorist — site behaviour
   - Reassembles scrambled preview atlases onto <canvas> (see tools/build.py)
   - Global view prefs: style (outline/plain), guides, backdrop  [O] [G] [B]
   - Catalogue, hero board, in-game HUD demo, product viewer, nav, mobile bar
   ========================================================================== */
(function () {
  'use strict';

  var doc = document, html = doc.documentElement;
  var me = doc.currentScript && doc.currentScript.src;
  var ROOT = me ? me.replace(/js\/site\.js(\?.*)?$/, '') : '/';
  var CAT = window.VX_CATALOG || { packs: [] };
  var PACK = CAT.packs[0] || null;
  var REDUCED = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var DPR = Math.min(window.devicePixelRatio || 1, 2);

  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem('vx.' + k); localStorage.setItem('vx.' + k, v); } catch (e) { return null; } }

  /* ---------------- Atlas reassembly ---------------- */
  function m32(a) {
    return function () {
      a = a + 0x6D2B79F5 | 0;
      var t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return (t ^ t >>> 14) >>> 0;
    };
  }
  function plan(total, seed) {
    var r = m32(seed), perm = new Array(total), rots = new Array(total), i, j, t;
    for (i = 0; i < total; i++) perm[i] = i;
    for (i = total - 1; i > 0; i--) { j = r() % (i + 1); t = perm[i]; perm[i] = perm[j]; perm[j] = t; }
    for (i = 0; i < total; i++) rots[i] = r() % 4;
    return { perm: perm, rots: rots };
  }

  var INDEX = {};           // icon id -> position in pack
  var CACHE = [null, null]; // style -> array of 256px canvases
  var READY = [];           // style -> Promise
  if (PACK) PACK.icons.forEach(function (ic, i) { INDEX[ic.id] = i; });

  function loadStyle(v) {
    if (READY[v]) return READY[v];
    // Outline (shown by default) loads first; the second atlas waits for it.
    var gate = v === 1 && store('style') !== 'plain' ? loadStyle(0).catch(function () {}) : Promise.resolve();
    READY[v] = gate.then(function () { return new Promise(function (res, rej) {
      if (!PACK) return rej(new Error('no catalog'));
      var A = PACK.atlas, S = A.styles[v], img = new Image();
      img.decoding = 'async';
      img.onload = function () {
        var B = A.block, g = A.tile / B, per = g * g, n = PACK.icons.length;
        var p = plan(n * per, S.seed), out = [];
        for (var i = 0; i < n; i++) {
          var c = doc.createElement('canvas'); c.width = c.height = A.tile;
          var x = c.getContext('2d'); x.imageSmoothingEnabled = false;
          for (var by = 0; by < g; by++) for (var bx = 0; bx < g; bx++) {
            var b = i * per + by * g + bx, s = p.perm[b], sx = (s % A.cols) * B, sy = Math.floor(s / A.cols) * B, r = p.rots[b];
            if (!r) { x.drawImage(img, sx, sy, B, B, bx * B, by * B, B, B); continue; }
            x.save(); x.translate(bx * B + B / 2, by * B + B / 2); x.rotate(r * Math.PI / 2);
            x.drawImage(img, sx, sy, B, B, -B / 2, -B / 2, B, B); x.restore();
          }
          out.push(c);
        }
        CACHE[v] = out; res(out);
      };
      img.onerror = function () { rej(new Error('atlas ' + v)); };
      img.src = ROOT + S.src;
    }); });
    return READY[v];
  }

  function draw(cv, v, id) {
    var src = CACHE[v] && CACHE[v][INDEX[id]];
    if (!src) return;
    var w = cv.parentNode.clientWidth || 64;
    var px = Math.max(16, Math.min(256, Math.round(w * DPR)));
    if (cv.width !== px) { cv.width = cv.height = px; }
    var x = cv.getContext('2d');
    x.clearRect(0, 0, px, px);
    x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
    x.drawImage(src, 0, 0, px, px);
  }

  function paint(el) {
    var id = el.getAttribute('data-icon');
    if (!(id in INDEX)) { el.classList.add('is-error'); return; }
    var cvs = el.querySelectorAll('canvas');
    if (cvs.length < 2) {
      el.innerHTML = '';
      for (var v = 0; v < 2; v++) { var c = doc.createElement('canvas'); c.className = 'v' + v; c.setAttribute('aria-hidden', 'true'); el.appendChild(c); }
      cvs = el.querySelectorAll('canvas');
    }
    if (!el.hasAttribute('role')) { el.setAttribute('role', 'img'); }
    el.setAttribute('aria-label', PACK.icons[INDEX[id]].name + ' icon');
    el.setAttribute('data-label', PACK.icons[INDEX[id]].name);
    var pending = 0;
    [0, 1].forEach(function (v) {
      if (CACHE[v]) draw(cvs[v], v, id);
      else { pending++; loadStyle(v).then(function () { draw(cvs[v], v, id); el.classList.remove('is-loading'); }, function () { el.classList.add('is-error'); el.classList.remove('is-loading'); }); }
    });
    if (pending === 2) el.classList.add('is-loading');
  }
  function setIcon(el, id) { el.setAttribute('data-icon', id); paint(el); }
  function paintAll(scope) { $$('.art[data-icon]', scope).forEach(paint); }

  // Repaint at the right pixel size when layout changes width.
  var rzT;
  window.addEventListener('resize', function () {
    clearTimeout(rzT);
    rzT = setTimeout(function () { $$('.art[data-icon]').forEach(function (el) { var c = el.querySelector('canvas'); if (c && Math.abs(c.width - Math.min(256, el.clientWidth * DPR)) > c.width * .2) paint(el); }); }, 200);
  });

  // Keep previews out of "Save image", drag-out and long-press menus.
  doc.addEventListener('contextmenu', function (e) { if (e.target.closest && e.target.closest('.art,.cv')) e.preventDefault(); });
  doc.addEventListener('dragstart', function (e) { if (e.target.closest && e.target.closest('.art,.cv')) e.preventDefault(); });

  /* ---------------- View prefs ---------------- */
  var BDS = ['paper', 'night', 'sky'];
  var pref = {
    style: store('style') === 'plain' ? 'plain' : 'outline',
    guides: 'off',
    bd: BDS.indexOf(store('bd')) > -1 ? store('bd') : 'paper'
  };
  function apply() {
    html.setAttribute('data-style', pref.style);
    html.setAttribute('data-guides', pref.guides);
    html.setAttribute('data-bd', pref.bd);
    $$('[data-set-style]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-set-style') === pref.style)); });
    $$('[data-toggle="guides"]').forEach(function (b) { b.setAttribute('aria-pressed', String(pref.guides === 'on')); });
    $$('[data-set-bd]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-set-bd') === pref.bd)); });
  }
  function setStyle(s) { pref.style = s; store('style', s); apply(); }
  doc.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-set-style],[data-toggle="guides"],[data-set-bd]');
    if (!t) return;
    if (t.hasAttribute('data-set-style')) setStyle(t.getAttribute('data-set-style'));
    else if (t.hasAttribute('data-set-bd')) { pref.bd = t.getAttribute('data-set-bd'); store('bd', pref.bd); apply(); }
    else { pref.guides = pref.guides === 'on' ? 'off' : 'on'; apply(); }
  });
  doc.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select' || e.target.isContentEditable) return;
    var k = e.key.toLowerCase();
    if (k === 'o') setStyle(pref.style === 'outline' ? 'plain' : 'outline');
    else if (k === 'g') { pref.guides = pref.guides === 'on' ? 'off' : 'on'; apply(); }
    else if (k === 'b') { pref.bd = BDS[(BDS.indexOf(pref.bd) + 1) % BDS.length]; store('bd', pref.bd); apply(); }
  });
  apply();

  /* ---------------- Nav ---------------- */
  var nav = $('.nav'), hero = $('.hero');
  function onScroll() { if (nav && hero) nav.classList.toggle('solid', window.scrollY > 24); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  var burger = $('.burger'), sheet = $('.sheet');
  if (burger && sheet) {
    burger.addEventListener('click', function () {
      var open = !sheet.classList.contains('open');
      sheet.classList.toggle('open', open); burger.setAttribute('aria-expanded', String(open));
      if (open && nav) nav.classList.add('solid'); else onScroll();
    });
    $$('a', sheet).forEach(function (a) { a.addEventListener('click', function () { sheet.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); }); });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && sheet.classList.contains('open')) { sheet.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); burger.focus(); } });
  }

  /* ---------------- Catalogue ---------------- */
  function buildCatalogue(root) {
    var grid = $('.grid', root), chips = $('.chips', root), empty = $('.grid-empty', root);
    if (!grid || !PACK) { if (grid) grid.innerHTML = '<div class="grid-empty">Previews could not load. Refresh the page to try again.</div>'; return; }
    var href = root.getAttribute('data-href') || '';
    var counts = {}; PACK.icons.forEach(function (ic) { counts[ic.cat] = (counts[ic.cat] || 0) + 1; });
    var cats = ['All'].concat(PACK.categories.filter(function (c) { return counts[c]; }));
    chips.innerHTML = cats.map(function (c, i) {
      return '<button class="chip" type="button" data-cat="' + c + '" aria-pressed="' + (i === 0) + '">' + c + ' <i>' + (i === 0 ? PACK.icons.length : counts[c]) + '</i></button>';
    }).join('');
    grid.innerHTML = PACK.icons.map(function (ic, i) {
      var n = String(i + 1).padStart(2, '0');
      return '<a class="tile" href="' + href + '#' + ic.id + '" data-cat="' + ic.cat + '">' +
        '<div class="pad"><div class="art" data-icon="' + ic.id + '"></div></div>' +
        '<div class="ft"><span class="nm" title="' + ic.name + '">' + ic.name + '</span><span class="ct mono">' + n + '</span></div></a>';
    }).join('');
    paintAll(grid);
    chips.addEventListener('click', function (e) {
      var b = e.target.closest('.chip'); if (!b) return;
      var c = b.getAttribute('data-cat'), shown = 0;
      $$('.chip', chips).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      $$('.tile', grid).forEach(function (t) { var on = c === 'All' || t.getAttribute('data-cat') === c; t.hidden = !on; if (on) shown++; });
      if (empty) empty.hidden = shown > 0;
    });
  }
  $$('[data-catalogue]').forEach(buildCatalogue);

  /* ---------------- Hero board ---------------- */
  var board = $('.board');
  if (board && PACK && !REDUCED) {
    var smalls = $$('.spec:not(.big) .art', board), last = -1;
    setInterval(function () {
      if (doc.hidden) return;
      var shown = $$('.art', board).map(function (a) { return a.getAttribute('data-icon'); });
      var pool = PACK.icons.filter(function (ic) { return shown.indexOf(ic.id) < 0; });
      var k; do { k = Math.floor(Math.random() * smalls.length); } while (k === last && smalls.length > 1); last = k;
      var el = smalls[k], next = pool[Math.floor(Math.random() * pool.length)];
      var lab = el.closest('.spec').querySelector('.lab span');
      el.classList.add('swap');
      setTimeout(function () { setIcon(el, next.id); if (lab) lab.textContent = next.name; el.classList.remove('swap'); }, 360);
    }, 2600);
  }

  /* ---------------- HUD demo ---------------- */
  var frame = $('.hud-frame');
  if (frame) {
    var hud = $('.hud', frame);
    var fit = function () { hud.style.setProperty('--s', frame.clientWidth / 800); };
    if (window.ResizeObserver) new ResizeObserver(fit).observe(frame); else window.addEventListener('resize', fit);
    fit();

    var coins = 12480, coinEl = $('[data-count="coin"]', frame), coinPill = coinEl && coinEl.closest('.pill');
    var fmt = function (n) { return n.toLocaleString('en-US'); };
    var chest = $('.hud-chest', frame), chestArt = chest && $('.art', chest), toast = $('.hud-toast', frame), busy = false;
    if (chest) chest.addEventListener('click', function () {
      if (busy) return; busy = true;
      chest.classList.add('open'); setIcon(chestArt, 'chest-open-coins');
      var fr = frame.getBoundingClientRect(), s = frame.clientWidth / 800;
      var cr = chest.getBoundingClientRect(), pr = coinPill.getBoundingClientRect();
      for (var i = 0; i < 7; i++) (function (i) {
        var f = doc.createElement('div'); f.className = 'art fly'; f.setAttribute('data-icon', 'coin');
        var x0 = (cr.left - fr.left) / s + 55 + (Math.random() * 40 - 20), y0 = (cr.top - fr.top) / s + 30;
        f.style.left = x0 + 'px'; f.style.top = y0 + 'px'; hud.appendChild(f); paint(f);
        var dx = (pr.left - fr.left) / s + 2 - x0, dy = (pr.top - fr.top) / s + 2 - y0;
        setTimeout(function () { f.style.transform = 'translate(' + dx + 'px,' + dy + 'px) scale(.7)'; }, 60 + i * 70);
        setTimeout(function () { f.style.opacity = '0'; }, 600 + i * 70);
        setTimeout(function () { f.remove(); }, 1000 + i * 70);
      })(i);
      var start = coins, end = coins + 250, t0 = 0;
      setTimeout(function () {
        coinPill.classList.remove('bump'); void coinPill.offsetWidth; coinPill.classList.add('bump');
        var step = function (ts) { if (!t0) t0 = ts; var p = Math.min(1, (ts - t0) / 600); coinEl.textContent = fmt(Math.round(start + (end - start) * p)); if (p < 1) requestAnimationFrame(step); };
        requestAnimationFrame(step); coins = end;
      }, 650);
      if (toast) { toast.classList.add('on'); setTimeout(function () { toast.classList.remove('on'); }, 1400); }
      setTimeout(function () { chest.classList.remove('open'); setIcon(chestArt, 'chest-closed'); busy = false; }, 2600);
    });

    var rot = {};
    $$('[data-spin]', frame).forEach(function (b) {
      b.addEventListener('click', function () {
        var a = $('.art', b), id = b.getAttribute('data-spin');
        rot[id] = (rot[id] || 0) + (id === 'wheel' ? 1080 + Math.floor(Math.random() * 360) : 360);
        a.style.transform = 'rotate(' + rot[id] + 'deg)';
      });
    });

    var timers = $$('[data-timer]', frame).map(function (el) { return { el: el, s: +el.getAttribute('data-timer') }; });
    setInterval(function () {
      timers.forEach(function (t) { t.s = t.s > 0 ? t.s - 1 : 900; t.el.textContent = Math.floor(t.s / 60) + ':' + String(t.s % 60).padStart(2, '0'); });
    }, 1000);
  }

  /* ---------------- Product viewer ---------------- */
  var viewer = $('.viewer');
  if (viewer && PACK) {
    var stageArt = $('.stage .art', viewer), nameEl = $('[data-v="name"]', viewer), metaEl = $('[data-v="meta"]', viewer), strip = $('.strip', viewer), cur = 0;
    strip.innerHTML = PACK.icons.map(function (ic, i) {
      return '<button type="button" data-i="' + i + '" aria-label="' + ic.name + '"><div class="art" data-icon="' + ic.id + '"></div></button>';
    }).join('');
    paintAll(strip);
    var show = function (i, push) {
      cur = (i + PACK.icons.length) % PACK.icons.length;
      var ic = PACK.icons[cur];
      setIcon(stageArt, ic.id);
      nameEl.textContent = ic.name;
      metaEl.textContent = ic.cat + ' · ' + String(cur + 1).padStart(2, '0') + ' / ' + PACK.icons.length;
      $$('button', strip).forEach(function (b, j) { b.setAttribute('aria-current', String(j === cur)); });
      if (push && history.replaceState) history.replaceState(null, '', '#' + ic.id);
    };
    strip.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) show(+b.getAttribute('data-i'), true); });
    $('[data-v="prev"]', viewer).addEventListener('click', function () { show(cur - 1, true); });
    $('[data-v="next"]', viewer).addEventListener('click', function () { show(cur + 1, true); });
    doc.addEventListener('keydown', function (e) {
      var tag = (e.target.tagName || '').toLowerCase(); if (tag === 'input' || tag === 'textarea') return;
      if (e.key === 'ArrowLeft') show(cur - 1, true); else if (e.key === 'ArrowRight') show(cur + 1, true);
    });
    var fromHash = function () { var h = location.hash.slice(1); if (h in INDEX) { show(INDEX[h]); return true; } return false; };
    if (!fromHash()) show(0);
    window.addEventListener('hashchange', function () { if (fromHash()) viewer.scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth', block: 'start' }); });
    if (location.hash.slice(1) in INDEX) setTimeout(function () { window.scrollTo(0, 0); }, 0);
  }

  /* ---------------- Mobile buy bar ---------------- */
  var mbar = $('.mbar'), watch = $(mbar && mbar.getAttribute('data-after'));
  if (mbar && watch && window.IntersectionObserver) {
    doc.body.classList.add('has-mbar');
    var past = false, blocked = new Set();
    var sync = function () { mbar.classList.toggle('on', past && blocked.size === 0); };
    new IntersectionObserver(function (en) { past = !en[0].isIntersecting && en[0].boundingClientRect.top < 0; sync(); }).observe(watch);
    // Hide while a real Buy button is already on screen.
    var bio = new IntersectionObserver(function (en) { en.forEach(function (e) { if (e.isIntersecting) blocked.add(e.target); else blocked.delete(e.target); }); sync(); });
    $$(mbar.getAttribute('data-hide') || '.final').forEach(function (el) { bio.observe(el); });
  }

  /* ---------------- Reveal ---------------- */
  if (window.IntersectionObserver && !REDUCED) {
    var io = new IntersectionObserver(function (en) { en.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    $$('.rv').forEach(function (el) { io.observe(el); });
  } else $$('.rv').forEach(function (el) { el.classList.add('in'); });

  /* ---------------- Boot ---------------- */
  paintAll();
  if (PACK) loadStyle(0).then(function () { (window.requestIdleCallback || setTimeout)(function () { loadStyle(1); }); });
  else $$('.art[data-icon]').forEach(function (el) { el.classList.add('is-error'); });

  window.VX = { paint: paint, setIcon: setIcon };
})();
