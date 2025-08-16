// Simple cache-first SW for static assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open("desander-cache-v1").then((cache) => cache.addAll([
      "./",
      "./manifest.json",
      "./logo.png"
    ]))
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  );
});
