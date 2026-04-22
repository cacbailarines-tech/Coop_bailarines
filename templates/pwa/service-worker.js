const CACHE_NAME = 'bailarines-{{ static_version }}';
const APP_SHELL = [
  '/',
  '/login/',
  '/offline/',
  '/manifest.webmanifest',
  '/static/img/logo.png',
  '/static/img/logo-icon.png',
  '/static/img/logo-app-192.png',
  '/static/img/logo-app-512.png',
  '/static/img/logo-app-full-192.png',
  '/static/img/logo-app-full-512.png',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(key => {
        if (key !== CACHE_NAME) {
          return caches.delete(key);
        }
      }))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(response => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
        return response;
      })
      .catch(async () => {
        const cached = await caches.match(event.request);
        if (cached) {
          return cached;
        }
        if (event.request.mode === 'navigate') {
          return caches.match('/offline/');
        }
        return new Response('', { status: 504, statusText: 'Offline' });
      })
  );
});

self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Cooperativa Bailarines';
  const options = {
    body: data.body || 'Tiene una nueva notificación.',
    icon: data.icon || '/static/img/logo-app-full-192.png',
    badge: data.badge || '/static/img/logo-app-full-192.png',
    tag: data.tag || 'bailarines-push',
    data: {
      url: data.url || '/portal/inicio/',
    },
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const targetUrl = (event.notification.data && event.notification.data.url) || '/portal/inicio/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
      for (const client of windowClients) {
        if ('focus' in client) {
          client.navigate(targetUrl);
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
