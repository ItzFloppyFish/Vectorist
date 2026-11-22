/* ==========================================================================
   Vectorist — site behaviour
   - Reassembles scrambled preview atlases onto <canvas> (see tools/build.py)
   - Bakes a watermark into icons on the product wall (data-wm)
   - Style switch (outline / no outline), hero board, in-game demo, nav, mobile bar
   ========================================================================== */
(function () {
  'use strict';

  var doc = document, html = doc.documentElement;
  var me = doc.currentScript && doc.currentScript.src;
  var ROOT = me ? me.replace(/js\/site\.js(\?.*)?$/, '') : '/';
  var CAT = window.VX_CATALOG || { packs: [] };
  var PACK = CAT.packs[0] || null;
  var REDUCED = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FINE = window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches;
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

  var INDEX = {}, CACHE = [null, null], READY = [];
  if (PACK) PACK.icons.forEach(function (ic, i) { INDEX[ic.id] = i; });

  function loadStyle(v) {
    if (READY[v]) return READY[v];
    // The style on screen loads first; the other waits for it.
    var first = store('style') === 'plain' ? 1 : 0;
    var gate = v !== first ? loadStyle(first).catch(function () {}) : Promise.resolve();
    READY[v] = gate.then(function () { return new Promise(function (res, rej) {
      if (!PACK) return rej(new Error('no catalog'));
      var A = PACK.atlas, S = A.styles[v], img = new Image();
      img.decoding = 'async';
      img.onload = function () {
        var B = A.block, g = A.tile / B, per = g * g, n = PACK.icons.length, p = plan(n * per, S.seed), out = [];
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

  // Watermark is drawn INTO the pixels (clipped to the icon), so removing CSS doesn't remove it.
  function watermark(x, px) {
    var fs = Math.round(px * 0.16);
    x.save();
    x.globalCompositeOperation = 'source-atop';
    x.translate(px / 2, px / 2); x.rotate(-0.5);
    x.font = '700 ' + fs + 'px Fredoka, ui-rounded, sans-serif';
    x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
    x.lineWidth = Math.max(1, fs * 0.14); x.strokeStyle = 'rgba(12,18,48,.28)'; x.strokeText('VECTORIST', 0, 0);
    x.fillStyle = 'rgba(255,255,255,.62)'; x.fillText('VECTORIST', 0, 0);
    x.restore();
  }

  function draw(cv, v, id) {
    var src = CACHE[v] && CACHE[v][INDEX[id]];
    if (!src) return;
    var host = cv.parentNode, w = host.clientWidth || 64;
    var px = Math.max(16, Math.min(256, Math.round(w * DPR)));
    if (cv.width !== px) cv.width = cv.height = px;
    var x = cv.getContext('2d');
    x.clearRect(0, 0, px, px);
    x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
    x.drawImage(src, 0, 0, px, px);
    if (host.hasAttribute('data-wm')) watermark(x, px);
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
    var name = PACK.icons[INDEX[id]].name;
    if (!el.hasAttribute('aria-hidden')) { el.setAttribute('role', 'img'); el.setAttribute('aria-label', name); }
    el.setAttribute('data-label', name);
    var pending = 0;
    [0, 1].forEach(function (v) {
      if (CACHE[v]) draw(cvs[v], v, id);
      else { pending++; loadStyle(v).then(function () { draw(cvs[v], v, id); el.classList.remove('is-loading'); }, function () { el.classList.add('is-error'); el.classList.remove('is-loading'); }); }
    });
    if (pending === 2) el.classList.add('is-loading');
  }
  function setIcon(el, id) { el.setAttribute('data-icon', id); paint(el); }
  function paintAll(scope) { $$('.art[data-icon]', scope).forEach(paint); }

  var rzT;
  window.addEventListener('resize', function () {
    clearTimeout(rzT);
    rzT = setTimeout(function () {
      $$('.art[data-icon]').forEach(function (el) { var c = el.querySelector('canvas'); if (c && Math.abs(c.width - Math.min(256, el.clientWidth * DPR)) > c.width * .2) paint(el); });
    }, 200);
  });

  // Keep previews out of "Save image", drag-out and long-press menus.
  doc.addEventListener('contextmenu', function (e) { if (e.target.closest && e.target.closest('.art,.cv')) e.preventDefault(); });
  doc.addEventListener('dragstart', function (e) { if (e.target.closest && e.target.closest('.art,.cv')) e.preventDefault(); });

  /* ---------------- Style switch ---------------- */
  var style = store('style') === 'plain' ? 'plain' : 'outline';
  function applyStyle() {
    html.setAttribute('data-style', style);
    $$('[data-set-style]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-set-style') === style)); });
  }
  doc.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('[data-set-style]');
    if (!t) return;
    style = t.getAttribute('data-set-style'); store('style', style); applyStyle();
  });
  applyStyle();

  /* ---------------- Nav ---------------- */
  var nav = $('.nav'), hero = $('.hero');
  function onScroll() { if (nav && hero) nav.classList.toggle('solid', window.scrollY > 24); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  var burger = $('.burger'), sheet = $('.sheet');
  if (burger && sheet) {
    var close = function () { sheet.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); onScroll(); };
    burger.addEventListener('click', function () {
      var open = !sheet.classList.contains('open');
      sheet.classList.toggle('open', open); burger.setAttribute('aria-expanded', String(open));
      if (open && nav) nav.classList.add('solid'); else onScroll();
    });
    $$('a', sheet).forEach(function (a) { a.addEventListener('click', close); });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && sheet.classList.contains('open')) { close(); burger.focus(); } });
  }

  /* ---------------- Hero board ---------------- */
  var board = $('.board');
  if (board && PACK && !REDUCED) {
    var smalls = $$('.spec:not(.big)', board), last = -1;
    setInterval(function () {
      if (doc.hidden) return;
      var shown = $$('.art', board).map(function (a) { return a.getAttribute('data-icon'); });
      var pool = PACK.icons.filter(function (ic) { return shown.indexOf(ic.id) < 0; });
      var k; do { k = Math.floor(Math.random() * smalls.length); } while (k === last && smalls.length > 1); last = k;
      var tile = smalls[k], el = $('.art', tile), lab = $('.nm', tile), next = pool[Math.floor(Math.random() * pool.length)];
      el.classList.add('swap'); if (lab) lab.classList.add('swap');
      setTimeout(function () { setIcon(el, next.id); if (lab) { lab.textContent = next.name; lab.classList.remove('swap'); } el.classList.remove('swap'); }, 380);
    }, 2800);
    if (FINE && hero) {
      var raf = 0;
      hero.addEventListener('pointermove', function (e) {
        if (raf) return;
        raf = requestAnimationFrame(function () {
          raf = 0;
          var r = board.getBoundingClientRect();
          var dx = Math.max(-1, Math.min(1, (e.clientX - (r.left + r.width / 2)) / (r.width)));
          var dy = Math.max(-1, Math.min(1, (e.clientY - (r.top + r.height / 2)) / (r.height)));
          board.style.setProperty('--ry', (dx * 9).toFixed(2) + 'deg');
          board.style.setProperty('--rx', (-dy * 7).toFixed(2) + 'deg');
        });
      });
      hero.addEventListener('pointerleave', function () { board.style.setProperty('--ry', '0deg'); board.style.setProperty('--rx', '0deg'); });
    }
  }

  /* ---------------- In-game demo ---------------- */
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
        var f = doc.createElement('div'); f.className = 'art fly'; f.setAttribute('data-icon', 'coin'); f.setAttribute('aria-hidden', 'true');
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

  /* ---------------- Style swap demo ---------------- */
  var autos = $$('.auto');
  if (autos.length && !REDUCED) setInterval(function () {
    if (doc.hidden) return;
    autos.forEach(function (a) {
      var plain = a.getAttribute('data-style') !== 'plain';
      a.setAttribute('data-style', plain ? 'plain' : 'outline');
      var st = $('.st', a); if (st) st.textContent = plain ? 'No outline' : 'Outline';
    });
  }, 1800);

  /* ---------------- Product wall ---------------- */
  var wallRoot = $('[data-wall]');
  if (wallRoot) {
    if (!PACK) wallRoot.innerHTML = '<p class="lede">Previews could not load. Refresh the page to try again.</p>';
    else {
      wallRoot.innerHTML = '<div class="wall">' + PACK.icons.map(function (ic) {
        return '<div class="wt"><div class="art" data-wm data-icon="' + ic.id + '"></div><span class="nm" title="' + ic.name + '">' + ic.name + '</span></div>';
      }).join('') + '</div>';
      // Wait for the watermark font, otherwise the first paint uses a fallback face.
      var go = function () { paintAll(wallRoot); };
      if (doc.fonts && doc.fonts.load) doc.fonts.load('700 40px Fredoka').then(go, go); else go();
    }
  }

  /* ---------------- Mobile buy bar ---------------- */
  var mbar = $('.mbar'), watch = $(mbar && mbar.getAttribute('data-after'));
  if (mbar && watch && window.IntersectionObserver) {
    doc.body.classList.add('has-mbar');
    var past = false, blocked = new Set();
    var sync = function () { mbar.classList.toggle('on', past && blocked.size === 0); };
    new IntersectionObserver(function (en) { past = !en[0].isIntersecting && en[0].boundingClientRect.top < 0; sync(); }).observe(watch);
    var bio = new IntersectionObserver(function (en) { en.forEach(function (e) { if (e.isIntersecting) blocked.add(e.target); else blocked.delete(e.target); }); sync(); });
    $$(mbar.getAttribute('data-hide') || '.final').forEach(function (el) { bio.observe(el); });
  }

  /* ---------------- Reveal ---------------- */
  if (window.IntersectionObserver && !REDUCED) {
    var io = new IntersectionObserver(function (en) { en.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    $$('.rv').forEach(function (el) { io.observe(el); });
  } else $$('.rv').forEach(function (el) { el.classList.add('in'); });

  /* ---------------- Boot ---------------- */
  $$('.art[data-icon]').forEach(function (el) { if (!el.hasAttribute('data-wm')) paint(el); });
  if (!PACK) $$('.art[data-icon]').forEach(function (el) { el.classList.add('is-error'); });

  window.VX = { paint: paint, setIcon: setIcon };
})();
