/* Service worker — cache-first pour les ressources, réseau d'abord pour les pages. */
var V = 'crisp-fc-202608270836';
var PRECACHE = ["/crisp/", "/crisp/graphe/", "/crisp/glossaire/", "/crisp/assets/css/site.css", "/crisp/assets/js/app.js", "/crisp/assets/js/graph.js", "/crisp/assets/data/graph.json", "/crisp/assets/data/search-index.json", "/crisp/offline.html"];
self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(V).then(function (c) { return c.addAll(PRECACHE); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (k) {
    return Promise.all(k.filter(function (n) { return n !== V; }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(function (r) {
      var copy = r.clone(); caches.open(V).then(function (c) { c.put(req, copy); }); return r;
    }).catch(function () { return caches.match(req).then(function (m) { return m || caches.match('/crisp/offline.html'); }); }));
    return;
  }
  e.respondWith(caches.match(req).then(function (m) {
    return m || fetch(req).then(function (r) {
      var copy = r.clone(); caches.open(V).then(function (c) { c.put(req, copy); }); return r;
    });
  }));
});
