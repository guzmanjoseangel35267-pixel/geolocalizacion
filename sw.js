// sw.js
self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
    // Aquí podrías interceptar peticiones o gestionar caché
});