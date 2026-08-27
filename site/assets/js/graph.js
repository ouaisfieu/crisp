/* ============================================================
   Graphe de connaissances — moteur maison
   Simulation de forces + rendu canvas, sans aucune dépendance.
   (c) fan club CRISP — MIT
   ============================================================ */
(function () {
  "use strict";

  var TYPE_LABEL = {
    institution: "Institution",
    person: "Personne",
    collection: "Collection",
    publication: "Publication",
    concept: "Concept",
    party: "Parti",
    database: "Base de données",
    event: "Événement / jalon"
  };

  function cssVar(name, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  }

  function palette() {
    return {
      institution: cssVar("--n-institution", "#7aa2f7"),
      person: cssVar("--n-person", "#f2c14e"),
      collection: cssVar("--n-collection", "#c39bf5"),
      publication: cssVar("--n-publication", "#4ec9b0"),
      concept: cssVar("--n-concept", "#f58ba8"),
      party: cssVar("--n-party", "#e4483d"),
      database: cssVar("--n-database", "#ef925a"),
      event: cssVar("--n-event", "#8ec36d"),
      fg: cssVar("--fg", "#e9ebf2"),
      muted: cssVar("--fg-muted", "#98a1b3"),
      faint: cssVar("--fg-faint", "#6b7385"),
      bg: cssVar("--bg-elev", "#0c0e13"),
      line: cssVar("--line-strong", "rgba(255,255,255,.16)")
    };
  }

  /* ---------- Simulation ---------- */
  function Sim(nodes, links, opts) {
    opts = opts || {};
    this.nodes = nodes;
    this.links = links;
    this.alpha = 1;
    this.alphaDecay = opts.alphaDecay || 0.018;
    this.charge = opts.charge || -1150;
    this.linkDist = opts.linkDist || 74;
    this.linkStr = opts.linkStr || 0.07;
    this.gravity = opts.gravity || 0.05;
    this.cx = 0; this.cy = 0;
    this.index = {};
    var i;
    for (i = 0; i < nodes.length; i++) this.index[nodes[i].id] = nodes[i];
  }

  Sim.prototype.tick = function () {
    var n = this.nodes, L = this.links, i, j, a, b, dx, dy, d2, d, f;
    var alpha = this.alpha;
    if (alpha < 0.0015) return false;

    // repulsion (O(n^2) — parfaitement tenable en dessous de ~400 nœuds)
    for (i = 0; i < n.length; i++) {
      a = n[i];
      for (j = i + 1; j < n.length; j++) {
        b = n[j];
        dx = b.x - a.x; dy = b.y - a.y;
        d2 = dx * dx + dy * dy;
        if (d2 === 0) { dx = (Math.random() - 0.5) * 2; dy = (Math.random() - 0.5) * 2; d2 = 1; }
        if (d2 > 260000) continue;
        f = (this.charge * alpha) / d2;
        dx *= f; dy *= f;
        a.vx += dx / a.m; a.vy += dy / a.m;
        b.vx -= dx / b.m; b.vy -= dy / b.m;
      }
    }

    // ressorts
    for (i = 0; i < L.length; i++) {
      a = L[i].source; b = L[i].target;
      dx = b.x - a.x; dy = b.y - a.y;
      d = Math.sqrt(dx * dx + dy * dy) || 0.01;
      f = ((d - this.linkDist) / d) * alpha * this.linkStr;
      dx *= f; dy *= f;
      a.vx += dx * (b.m / (a.m + b.m)) * 2;
      a.vy += dy * (b.m / (a.m + b.m)) * 2;
      b.vx -= dx * (a.m / (a.m + b.m)) * 2;
      b.vy -= dy * (a.m / (a.m + b.m)) * 2;
    }

    // gravité vers le centre + intégration
    for (i = 0; i < n.length; i++) {
      a = n[i];
      a.vx += (this.cx - a.x) * this.gravity * alpha;
      a.vy += (this.cy - a.y) * this.gravity * alpha;
      if (a.fixed) { a.vx = 0; a.vy = 0; continue; }
      a.vx *= 0.82; a.vy *= 0.82;
      var sp = Math.sqrt(a.vx * a.vx + a.vy * a.vy);
      if (sp > 22) { a.vx = a.vx / sp * 22; a.vy = a.vy / sp * 22; }
      a.x += a.vx; a.y += a.vy;
    }

    this.alpha *= (1 - this.alphaDecay);
    return true;
  };

  Sim.prototype.reheat = function (v) { this.alpha = Math.max(this.alpha, v || 0.5); };

  /* ---------- Vue canvas ---------- */
  function GraphView(canvas, data, options) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.opts = options || {};
    this.pal = palette();
    this.scale = this.opts.scale || 1;
    this.tx = 0; this.ty = 0;
    this.hover = null;
    this.selected = null;
    this.filters = {};
    this.query = "";
    this.pointer = { x: 0, y: 0, down: false, moved: false, id: null };
    this.decorative = !!this.opts.decorative;
    this.build(data);
    this.bind();
    this.resize();
    this.loop();
  }

  GraphView.prototype.build = function (data) {
    var self = this;
    var nodes = data.nodes.map(function (d, i) {
      var ang = (i / data.nodes.length) * Math.PI * 2;
      var rad = 60 + Math.random() * 320;
      return Object.assign({}, d, {
        x: Math.cos(ang) * rad, y: Math.sin(ang) * rad,
        vx: 0, vy: 0,
        r: 3.2 + (d.w || 4) * 1.28,
        m: 1 + (d.w || 4) * 0.16,
        deg: 0
      });
    });
    var byId = {};
    nodes.forEach(function (n) { byId[n.id] = n; });
    var links = [];
    data.edges.forEach(function (e) {
      var s = byId[e[0]], t = byId[e[1]];
      if (!s || !t) return;
      s.deg++; t.deg++;
      links.push({ source: s, target: t, rel: e[2] || "" });
    });
    this.nodes = nodes; this.links = links; this.byId = byId;
    this.adj = {};
    links.forEach(function (l) {
      (self.adj[l.source.id] = self.adj[l.source.id] || []).push({ n: l.target, rel: l.rel, dir: "out" });
      (self.adj[l.target.id] = self.adj[l.target.id] || []).push({ n: l.source, rel: l.rel, dir: "in" });
    });
    this.sim = new Sim(nodes, links, this.opts.sim);
  };

  GraphView.prototype.resize = function () {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var r = this.canvas.getBoundingClientRect();
    this.w = r.width; this.h = r.height;
    this.canvas.width = Math.round(r.width * dpr);
    this.canvas.height = Math.round(r.height * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (!this._centered) { this.tx = this.w / 2; this.ty = this.h / 2; this._centered = true; }
  };

  GraphView.prototype.toWorld = function (px, py) {
    return { x: (px - this.tx) / this.scale, y: (py - this.ty) / this.scale };
  };

  GraphView.prototype.pick = function (px, py) {
    var p = this.toWorld(px, py), best = null, bd = 1e9;
    for (var i = 0; i < this.nodes.length; i++) {
      var n = this.nodes[i];
      if (this.isDim(n) === 2) continue;
      var dx = n.x - p.x, dy = n.y - p.y, d = dx * dx + dy * dy;
      var rr = (n.r + 7) * (n.r + 7);
      if (d < rr && d < bd) { bd = d; best = n; }
    }
    return best;
  };

  // 0 = normal, 1 = atténué, 2 = masqué
  GraphView.prototype.isDim = function (n) {
    if (this.filters[n.type] === false) return 2;
    if (this.query) {
      var q = this.query.toLowerCase();
      var hit = n.label.toLowerCase().indexOf(q) >= 0 || (n.summary || "").toLowerCase().indexOf(q) >= 0;
      if (!hit) return 1;
    }
    var focus = this.selected || this.hover;
    if (focus) {
      if (n.id === focus.id) return 0;
      var nb = this.adj[focus.id] || [];
      for (var i = 0; i < nb.length; i++) if (nb[i].n.id === n.id) return 0;
      return 1;
    }
    return 0;
  };

  GraphView.prototype.draw = function () {
    var c = this.ctx, pal = this.pal, i;
    c.clearRect(0, 0, this.w, this.h);
    c.save();
    c.translate(this.tx, this.ty);
    c.scale(this.scale, this.scale);

    var focus = this.selected || this.hover;

    // liens
    for (i = 0; i < this.links.length; i++) {
      var l = this.links[i];
      var ds = this.isDim(l.source), dt = this.isDim(l.target);
      if (ds === 2 || dt === 2) continue;
      var active = focus && (l.source.id === focus.id || l.target.id === focus.id);
      c.beginPath();
      c.moveTo(l.source.x, l.source.y);
      var mx = (l.source.x + l.target.x) / 2, my = (l.source.y + l.target.y) / 2;
      var ox = -(l.target.y - l.source.y) * 0.075, oy = (l.target.x - l.source.x) * 0.075;
      c.quadraticCurveTo(mx + ox, my + oy, l.target.x, l.target.y);
      if (active) {
        c.strokeStyle = pal[l.source.type] || pal.muted;
        c.globalAlpha = 0.75; c.lineWidth = 1.5 / this.scale + 0.6;
      } else {
        c.strokeStyle = pal.line;
        c.globalAlpha = focus ? 0.1 : (this.decorative ? 0.5 : 0.42);
        c.lineWidth = 1 / this.scale;
      }
      c.stroke();
    }
    c.globalAlpha = 1;

    // nœuds
    for (i = 0; i < this.nodes.length; i++) {
      var n = this.nodes[i];
      var dim = this.isDim(n);
      if (dim === 2) continue;
      var col = pal[n.type] || pal.muted;
      var alpha = dim === 1 ? 0.22 : 1;

      if (dim === 0 && (n.deg > 5 || (focus && n.id === focus.id))) {
        c.beginPath();
        c.arc(n.x, n.y, n.r * 2.6, 0, 6.2832);
        var g = c.createRadialGradient(n.x, n.y, n.r * 0.4, n.x, n.y, n.r * 2.6);
        g.addColorStop(0, hexA(col, 0.28)); g.addColorStop(1, hexA(col, 0));
        c.fillStyle = g; c.fill();
      }

      c.globalAlpha = alpha;
      c.beginPath();
      c.arc(n.x, n.y, n.r, 0, 6.2832);
      c.fillStyle = col;
      c.fill();
      if (focus && n.id === focus.id) {
        c.lineWidth = 2.4 / this.scale; c.strokeStyle = pal.fg; c.stroke();
      } else {
        c.lineWidth = 1.2 / this.scale; c.strokeStyle = hexA(pal.bg, 0.85); c.stroke();
      }
      c.globalAlpha = 1;
    }

    // libellés (avec évitement de collisions)
    if (!this.decorative) {
      c.textAlign = "center"; c.textBaseline = "top";
      var boxes = [];
      var order = this.nodes.slice().sort(function (a, b) { return b.deg - a.deg; });
      for (i = 0; i < order.length; i++) {
        var m = order[i];
        var dm = this.isDim(m);
        if (dm === 2 || dm === 1) continue;
        var isFocus = focus && (m.id === focus.id);
        var show = isFocus || m.deg >= 6 || this.scale > 1.35 ||
                   (focus && this.scale > 0.9) || (this.query && this.query.length > 1);
        if (!show) continue;
        var fs = Math.max(9.5, Math.min(13.5, 8 + m.r * 0.34)) / this.scale;
        c.font = "600 " + fs + "px Inter, system-ui, sans-serif";
        var label = m.label;
        var wLab = c.measureText(label).width;
        var pad = 4 / this.scale;
        var bx = m.x - wLab / 2 - pad, by = m.y + m.r + 3 / this.scale;
        var bw = wLab + pad * 2, bh = fs * 1.35;
        var clash = false;
        for (var k = 0; k < boxes.length; k++) {
          var o = boxes[k];
          if (bx < o[0] + o[2] && bx + bw > o[0] && by < o[1] + o[3] && by + bh > o[1]) { clash = true; break; }
        }
        if (clash && !isFocus) continue;
        boxes.push([bx, by, bw, bh]);
        c.globalAlpha = 0.88;
        c.fillStyle = hexA(pal.bg, 0.7);
        roundRect(c, bx, by, bw, bh, 4 / this.scale);
        c.fill();
        c.globalAlpha = 1;
        c.fillStyle = isFocus ? pal.fg : pal.muted;
        c.fillText(label, m.x, by + 1 / this.scale);
      }
    }
    c.restore();
  };

  function roundRect(c, x, y, w, h, r) {
    c.beginPath();
    c.moveTo(x + r, y);
    c.arcTo(x + w, y, x + w, y + h, r);
    c.arcTo(x + w, y + h, x, y + h, r);
    c.arcTo(x, y + h, x, y, r);
    c.arcTo(x, y, x + w, y, r);
    c.closePath();
  }

  function hexA(col, a) {
    col = (col || "").trim();
    if (col.charAt(0) === "#") {
      var h = col.slice(1);
      if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
      var num = parseInt(h, 16);
      return "rgba(" + ((num >> 16) & 255) + "," + ((num >> 8) & 255) + "," + (num & 255) + "," + a + ")";
    }
    if (col.indexOf("rgb") === 0) return col.replace(/rgba?\(([^)]+)\)/, function (_, v) {
      var p = v.split(",").map(function (s) { return s.trim(); });
      return "rgba(" + p[0] + "," + p[1] + "," + p[2] + "," + a + ")";
    });
    return "rgba(128,128,128," + a + ")";
  }

  GraphView.prototype.fit = function (pad) {
    if (!this.nodes.length) return;
    var minX = 1e9, minY = 1e9, maxX = -1e9, maxY = -1e9;
    for (var i = 0; i < this.nodes.length; i++) {
      var n = this.nodes[i];
      if (this.filters[n.type] === false) continue;
      minX = Math.min(minX, n.x - n.r); maxX = Math.max(maxX, n.x + n.r);
      minY = Math.min(minY, n.y - n.r); maxY = Math.max(maxY, n.y + n.r);
    }
    pad = pad || 48;
    var sx = (this.w - pad * 2) / Math.max(1, maxX - minX);
    var sy = (this.h - pad * 2) / Math.max(1, maxY - minY);
    this.scale = Math.max(0.28, Math.min(this.decorative ? 1.0 : 1.25, Math.min(sx, sy)));
    this.tx = this.w / 2 - ((minX + maxX) / 2) * this.scale;
    this.ty = this.h / 2 - ((minY + maxY) / 2) * this.scale;
    if (this.decorative) { this.scale *= 0.72; this.tx = this.w * 0.78 - ((minX + maxX) / 2) * this.scale; this.ty = this.h / 2 - ((minY + maxY) / 2) * this.scale; }
    this.needsDraw = true;
  };

  GraphView.prototype.loop = function () {
    var self = this;
    function frame() {
      var moving = self.sim.tick();
      if (moving || self.needsDraw) { self.draw(); self.needsDraw = false; }
      self._f = (self._f || 0) + 1;
      if (!self._touched && self._f % 12 === 0 && self.sim.alpha > 0.004) {
        self.fit(self.decorative ? 6 : 46);
      }
      if (self.decorative && self.sim.alpha < 0.006) { self.sim.reheat(0.03); }
      self.raf = requestAnimationFrame(frame);
    }
    frame();
  };

  GraphView.prototype.bind = function () {
    var self = this, cv = this.canvas;
    var ro = new ResizeObserver(function () { self.resize(); self.needsDraw = true; });
    ro.observe(cv);

    if (this.decorative) return;

    cv.addEventListener("pointerdown", function (e) {
      cv.setPointerCapture(e.pointerId);
      self._touched = true;
      self.pointer.down = true; self.pointer.moved = false;
      self.pointer.x = e.offsetX; self.pointer.y = e.offsetY;
      var n = self.pick(e.offsetX, e.offsetY);
      self.dragNode = n;
      if (n) { n.fixed = true; }
      cv.classList.add("dragging");
    });

    cv.addEventListener("pointermove", function (e) {
      var dx = e.offsetX - self.pointer.x, dy = e.offsetY - self.pointer.y;
      if (self.pointer.down) {
        if (Math.abs(dx) + Math.abs(dy) > 3) self.pointer.moved = true;
        if (self.dragNode) {
          var p = self.toWorld(e.offsetX, e.offsetY);
          self.dragNode.x = p.x; self.dragNode.y = p.y;
          self.sim.reheat(0.35);
        } else {
          self.tx += dx; self.ty += dy;
        }
        self.pointer.x = e.offsetX; self.pointer.y = e.offsetY;
        self.needsDraw = true;
      } else {
        var h = self.pick(e.offsetX, e.offsetY);
        if (h !== self.hover) { self.hover = h; self.needsDraw = true; cv.style.cursor = h ? "pointer" : "grab"; }
        if (h && self.tip) {
          self.tip.hidden = false;
          self.tip.textContent = h.label + " · " + (TYPE_LABEL[h.type] || h.type);
          self.tip.style.left = (e.offsetX + 14) + "px";
          self.tip.style.top = (e.offsetY + 14) + "px";
        } else if (self.tip) { self.tip.hidden = true; }
      }
    });

    function up(e) {
      cv.classList.remove("dragging");
      if (self.dragNode) { self.dragNode.fixed = false; }
      if (!self.pointer.moved) {
        var n = self.pick(e.offsetX, e.offsetY);
        self.select(n);
      }
      self.pointer.down = false; self.dragNode = null;
    }
    cv.addEventListener("pointerup", up);
    cv.addEventListener("pointercancel", function () { self.pointer.down = false; self.dragNode = null; cv.classList.remove("dragging"); });

    cv.addEventListener("wheel", function (e) {
      e.preventDefault();
      self._touched = true;
      var f = Math.exp(-e.deltaY * 0.0016);
      self.zoomAt(e.offsetX, e.offsetY, f);
    }, { passive: false });

    cv.addEventListener("dblclick", function (e) {
      var n = self.pick(e.offsetX, e.offsetY);
      if (n) self.focusNode(n);
    });
  };

  GraphView.prototype.zoomAt = function (px, py, f) {
    var ns = Math.max(0.25, Math.min(4, this.scale * f));
    f = ns / this.scale;
    this.tx = px - (px - this.tx) * f;
    this.ty = py - (py - this.ty) * f;
    this.scale = ns;
    this.needsDraw = true;
  };

  GraphView.prototype.focusNode = function (n) {
    this._touched = true;
    this.scale = 1.6;
    var cx = this.w > 900 ? (this.w - Math.min(360, this.w * 0.88)) / 2 : this.w / 2;
    this.tx = cx - n.x * this.scale;
    this.ty = this.h / 2 - n.y * this.scale;
    this.needsDraw = true;
  };

  GraphView.prototype.select = function (n) {
    this.selected = n;
    this.needsDraw = true;
    if (this.onSelect) this.onSelect(n);
  };

  /* ---------- Page graphe ---------- */
  function initGraphPage(data) {
    var canvas = document.getElementById("graph-canvas");
    if (!canvas) return;
    var shell = canvas.parentElement;
    var tip = document.createElement("div");
    tip.className = "graph-hint";
    tip.style.position = "absolute";
    tip.hidden = true;
    shell.appendChild(tip);

    var view = new GraphView(canvas, data, {});
    view.tip = tip;
    window.__graph = view;

    var panel = document.getElementById("node-panel");
    var types = Object.keys(TYPE_LABEL);

    // légende / filtres
    var legend = document.getElementById("graph-legend");
    if (legend) {
      types.forEach(function (t) {
        var b = document.createElement("button");
        b.className = "chip chip-btn";
        b.setAttribute("aria-pressed", "true");
        b.innerHTML = '<span class="dot" style="background:var(--n-' + t + ')"></span>' + TYPE_LABEL[t];
        b.addEventListener("click", function () {
          var on = b.getAttribute("aria-pressed") === "true";
          b.setAttribute("aria-pressed", on ? "false" : "true");
          view.filters[t] = on ? false : true;
          view.sim.reheat(0.3);
          view.needsDraw = true;
        });
        legend.appendChild(b);
      });
    }

    var input = document.getElementById("graph-q");
    if (input) {
      input.addEventListener("input", function () {
        view.query = input.value.trim();
        view.needsDraw = true;
      });
      input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          var q = input.value.trim().toLowerCase();
          var hit = view.nodes.filter(function (n) { return n.label.toLowerCase().indexOf(q) >= 0; })[0];
          if (hit) { view.select(hit); view.focusNode(hit); }
        }
      });
    }

    var zi = document.getElementById("zoom-in"), zo = document.getElementById("zoom-out"), zr = document.getElementById("zoom-reset");
    if (zi) zi.addEventListener("click", function () { view.zoomAt(view.w / 2, view.h / 2, 1.3); });
    if (zo) zo.addEventListener("click", function () { view.zoomAt(view.w / 2, view.h / 2, 1 / 1.3); });
    if (zr) zr.addEventListener("click", function () {
      view.select(null); view.query = ""; if (input) input.value = "";
      view.sim.reheat(0.6); view._touched = false; view.fit(); view.needsDraw = true;
    });

    view.onSelect = function (n) {
      if (!panel) return;
      if (!n) { panel.classList.remove("open"); history.replaceState(null, "", location.pathname); return; }
      var nb = (view.adj[n.id] || []).slice().sort(function (a, b) { return b.n.deg - a.n.deg; });
      var links = "";
      if (n.url) links += '<a class="btn btn-ghost" href="' + n.url + '" target="_blank" rel="noopener">Source officielle ↗</a> ';
      if (n.href) links += '<a class="btn btn-ghost" href="' + BASE + n.href.replace(/^\//, "") + '">Voir la fiche →</a>';
      panel.innerHTML =
        '<button class="icon-btn close" aria-label="Fermer">' + ICON_X + '</button>' +
        '<span class="chip type-tag tag-' + n.type + '"><span class="dot"></span>' + (TYPE_LABEL[n.type] || n.type) + '</span>' +
        '<h2>' + esc(n.label) + '</h2>' +
        '<p>' + esc(n.summary || "") + '</p>' +
        (links ? '<div class="pill-row" style="margin-top:1rem">' + links + '</div>' : '') +
        '<h4>' + nb.length + ' relation' + (nb.length > 1 ? 's' : '') + '</h4>' +
        '<ul class="rel-list">' + nb.map(function (r) {
          return '<li><button data-id="' + r.n.id + '"><span class="dot" style="width:7px;height:7px;border-radius:50%;background:var(--n-' + r.n.type + ');display:inline-block"></span> ' +
            esc(r.n.label) + ' <em>' + esc(r.rel) + '</em></button></li>';
        }).join("") + '</ul>';
      panel.classList.add("open");
      panel.querySelector(".close").addEventListener("click", function () { view.select(null); });
      Array.prototype.forEach.call(panel.querySelectorAll(".rel-list button"), function (b) {
        b.addEventListener("click", function () {
          var t = view.byId[b.dataset.id];
          if (t) { view.select(t); view.focusNode(t); }
        });
      });
      history.replaceState(null, "", "#n=" + encodeURIComponent(n.id));
    };

    // deep link
    function fromHash() {
      var m = /#n=([^&]+)/.exec(location.hash);
      if (m) {
        var n = view.byId[decodeURIComponent(m[1])];
        if (n) setTimeout(function () { view.select(n); view.focusNode(n); }, 900);
      }
    }
    fromHash();
    window.addEventListener("hashchange", fromHash);

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && view.selected) view.select(null);
    });
  }

  var ICON_X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>';
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]; }); }

  /* ---------- Hero décoratif ---------- */
  function initHero(data) {
    var canvas = document.getElementById("hero-canvas");
    if (!canvas) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var sub = { nodes: data.nodes.filter(function (n) { return (n.w || 0) >= 5; }).slice(0, 62), edges: [] };
    var ids = {};
    sub.nodes.forEach(function (n) { ids[n.id] = 1; });
    data.edges.forEach(function (e) { if (ids[e[0]] && ids[e[1]]) sub.edges.push(e); });
    new GraphView(canvas, sub, { decorative: true, sim: { charge: -1600, linkDist: 96, alphaDecay: 0.012, gravity: 0.045 } });
  }

  /* ---------- Boot ---------- */
  function boot() {
    var need = document.getElementById("graph-canvas") || document.getElementById("hero-canvas");
    if (!need) return;
    fetch(BASE + "assets/data/graph.json")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        initHero(data);
        initGraphPage(data);
      })
      .catch(function (e) { console.warn("graphe indisponible", e); });
  }

  var BASE = (document.documentElement.getAttribute("data-base") || "/");
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
