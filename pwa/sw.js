/* KIRO Service Worker — offline cache untuk PWA
 * Strategi:
 *   - App shell (HTML/CSS/JS/icon): cache-first, update di background
 *   - API (/api/*): network-first, fallback cache
 *   - Aset statis lain: stale-while-revalidate
 */
const VERSION = 'kiro-v1';
const SHELL = [
  '/', '/index.html',
  '/manifest.json',
  '/favicon.svg', '/favicon.ico', '/favicon-180.png',
  '/icon-192.png', '/icon-512.png',
  '/icon-192-maskable.png', '/icon-512-maskable.png',
  '/og-image.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(VERSION).then((c) =>
      // pakai Promise.allSettled -> satu 404 tidak menggagalkan install
      Promise.allSettled(SHELL.map((u) => c.add(u).catch(() => null)))
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;   // jangan cache lintas-origin

  // API -> network-first
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(
      fetch(req).then((r) => {
        const cp = r.clone();
        caches.open(VERSION).then((c) => c.put(req, cp)).catch(() => {});
        return r;
      }).catch(() => caches.match(req))
    );
    return;
  }

  // App shell & aset -> cache-first + revalidate
  e.respondWith(
    caches.match(req).then((hit) => {
      const net = fetch(req).then((r) => {
        if (r && r.status === 200 && r.type === 'basic') {
          const cp = r.clone();
          caches.open(VERSION).then((c) => c.put(req, cp)).catch(() => {});
        }
        return r;
      }).catch(() => hit);
      return hit || net;
    })
  );
});

// pesan dari halaman: {type:'SKIP_WAITING'} atau {type:'CLEAR_CACHE'}
self.addEventListener('message', (e) => {
  const d = e.data || {};
  if (d.type === 'SKIP_WAITING') self.skipWaiting();
  if (d.type === 'CLEAR_CACHE') caches.keys().then((ks) => ks.forEach((k) => caches.delete(k)));
});
