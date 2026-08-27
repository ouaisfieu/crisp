/* ============================================================
   Fan club CRISP — comportements de l'interface
   Aucune dépendance.
   ============================================================ */
(function () {
  "use strict";
  var BASE = document.documentElement.getAttribute("data-base") || "/";

  /* ---------- Thème ---------- */
  var KEY = "crisp-fc-theme";
  function applyTheme(t) {
    if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t);
    else document.documentElement.removeAttribute("data-theme");
  }
  try { applyTheme(localStorage.getItem(KEY)); } catch (e) {}

  function currentTheme() {
    var t = document.documentElement.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-theme-toggle]");
    if (!btn) return;
    var next = currentTheme() === "dark" ? "light" : "dark";
    applyTheme(next);
    try { localStorage.setItem(KEY, next); } catch (err) {}
    btn.setAttribute("aria-label", next === "dark" ? "Passer au thème clair" : "Passer au thème sombre");
  });

  /* ---------- Navigation mobile ---------- */
  var navToggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) { if (e.target.tagName === "A") nav.classList.remove("open"); });
  }

  /* ---------- Barre de progression ---------- */
  var prog = document.querySelector(".progress");
  if (prog) {
    var onScroll = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      prog.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + "%";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Apparitions ---------- */
  var revealables = document.querySelectorAll(".reveal");
  if (revealables.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    revealables.forEach(function (el, i) { el.style.transitionDelay = Math.min(i % 6, 5) * 55 + "ms"; io.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Compteurs ---------- */
  var counters = document.querySelectorAll("[data-count]");
  if (counters.length && "IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, target = parseFloat(el.dataset.count), pre = el.dataset.pre || "", suf = el.dataset.suf || "";
        var t0 = performance.now(), dur = 1100;
        function step(t) {
          var k = Math.min(1, (t - t0) / dur);
          var e = 1 - Math.pow(1 - k, 3);
          el.textContent = pre + Math.round(target * e).toLocaleString("fr-BE") + suf;
          if (k < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
        co.unobserve(el);
      });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { co.observe(el); });
  }

  /* ---------- Partage ---------- */
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-share]");
    if (!b) return;
    var kind = b.dataset.share;
    var url = location.href, title = document.title;
    if (kind === "native" && navigator.share) {
      e.preventDefault();
      navigator.share({ title: title, url: url }).catch(function () {});
    } else if (kind === "copy") {
      e.preventDefault();
      navigator.clipboard.writeText(url).then(function () {
        var old = b.getAttribute("aria-label");
        b.setAttribute("aria-label", "Lien copié !");
        b.classList.add("ok");
        setTimeout(function () { b.setAttribute("aria-label", old); b.classList.remove("ok"); }, 1800);
      });
    }
  });

  /* ---------- Filtres glossaire ---------- */
  var gq = document.getElementById("gloss-q");
  var gitems = document.querySelectorAll(".gloss-item");
  var gcats = document.querySelectorAll("[data-gloss-cat]");
  var activeCat = "*";
  function filterGloss() {
    var q = (gq && gq.value || "").trim().toLowerCase();
    var shown = 0;
    gitems.forEach(function (it) {
      var okCat = activeCat === "*" || it.dataset.cat === activeCat;
      var okQ = !q || it.textContent.toLowerCase().indexOf(q) >= 0;
      var vis = okCat && okQ;
      it.hidden = !vis;
      if (vis) shown++;
    });
    var empty = document.getElementById("gloss-empty");
    if (empty) empty.hidden = shown > 0;
    var count = document.getElementById("gloss-count");
    if (count) count.textContent = shown;
  }
  if (gq) gq.addEventListener("input", filterGloss);
  gcats.forEach(function (b) {
    b.addEventListener("click", function () {
      gcats.forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
      b.setAttribute("aria-pressed", "true");
      activeCat = b.dataset.glossCat;
      filterGloss();
    });
  });

  /* ---------- Filtres publications ---------- */
  var pfilters = document.querySelectorAll("[data-pub-filter]");
  var pubs = document.querySelectorAll("[data-themes]");
  pfilters.forEach(function (b) {
    b.addEventListener("click", function () {
      pfilters.forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
      b.setAttribute("aria-pressed", "true");
      var f = b.dataset.pubFilter;
      var n = 0;
      pubs.forEach(function (p) {
        var ok = f === "*" || (" " + p.dataset.themes + " ").indexOf(" " + f + " ") >= 0;
        p.hidden = !ok; if (ok) n++;
      });
      var c = document.getElementById("pub-count");
      if (c) c.textContent = n;
    });
  });

  /* ---------- Recherche globale (⌘K) ---------- */
  var omni = document.getElementById("omni");
  var omniInput = document.getElementById("omni-input");
  var omniResults = document.getElementById("omni-results");
  var INDEX = null, sel = 0, results = [];

  function loadIndex() {
    if (INDEX) return Promise.resolve(INDEX);
    return fetch(BASE + "assets/data/search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (d) { INDEX = d; return d; });
  }

  function openOmni() {
    if (!omni) return;
    omni.classList.add("open");
    omni.setAttribute("aria-hidden", "false");
    loadIndex().then(function () { render(omniInput.value); });
    setTimeout(function () { omniInput.focus(); omniInput.select(); }, 20);
  }
  function closeOmni() {
    if (!omni) return;
    omni.classList.remove("open");
    omni.setAttribute("aria-hidden", "true");
  }

  function score(item, q) {
    var t = item.t.toLowerCase(), b = (item.b || "").toLowerCase();
    if (t === q) return 100;
    if (t.indexOf(q) === 0) return 80;
    if (t.indexOf(q) > 0) return 60;
    if (b.indexOf(q) >= 0) return 30;
    // sous-séquence approximative
    var i = 0;
    for (var j = 0; j < t.length && i < q.length; j++) if (t[j] === q[i]) i++;
    return i === q.length ? 12 : 0;
  }

  function render(q) {
    if (!omniResults) return;
    q = (q || "").trim().toLowerCase();
    if (!INDEX) return;
    if (!q) {
      results = INDEX.filter(function (i) { return i.pin; }).slice(0, 8);
    } else {
      results = INDEX.map(function (i) { return { i: i, s: score(i, q) }; })
        .filter(function (x) { return x.s > 0; })
        .sort(function (a, b) { return b.s - a.s || a.i.t.length - b.i.t.length; })
        .slice(0, 12).map(function (x) { return x.i; });
    }
    sel = 0;
    if (!results.length) {
      omniResults.innerHTML = '<div class="omni-empty">Aucun résultat pour « ' + q.replace(/[<>&]/g, "") + ' »</div>';
      return;
    }
    omniResults.innerHTML = results.map(function (r, k) {
      return '<a href="' + r.u + '" class="' + (k === 0 ? "sel" : "") + '"><span class="kind">' + r.k + '</span>' +
        '<strong>' + r.t + '</strong><span>' + (r.b || "") + '</span></a>';
    }).join("");
  }

  if (omniInput) {
    omniInput.addEventListener("input", function () { render(omniInput.value); });
    omniInput.addEventListener("keydown", function (e) {
      var items = omniResults.querySelectorAll("a");
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!items.length) return;
        items[sel] && items[sel].classList.remove("sel");
        sel = (sel + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items[sel].classList.add("sel");
        items[sel].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (items[sel]) location.href = items[sel].getAttribute("href");
      } else if (e.key === "Escape") { closeOmni(); }
    });
  }
  if (omni) omni.addEventListener("click", function (e) { if (e.target === omni) closeOmni(); });
  document.addEventListener("click", function (e) { if (e.target.closest("[data-omni-open]")) { e.preventDefault(); openOmni(); } });
  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openOmni(); }
    else if (e.key === "/" && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); openOmni(); }
    else if (e.key === "Escape" && omni && omni.classList.contains("open")) closeOmni();
  });

  /* ---------- Service worker ---------- */
  if ("serviceWorker" in navigator && location.protocol.indexOf("http") === 0) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register(BASE + "sw.js").catch(function () {});
    });
  }
})();
