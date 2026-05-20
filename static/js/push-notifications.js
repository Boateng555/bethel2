/**
 * Bethel Web Push — subscribe to church events, news, and sermons on phone.
 */
(function () {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    return;
  }

  function getCsrfToken() {
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function urlBase64ToUint8Array(base64String) {
    var padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    var base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    var raw = window.atob(base64);
    var output = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) {
      output[i] = raw.charCodeAt(i);
    }
    return output;
  }

  function registerServiceWorker() {
    return navigator.serviceWorker.register('/sw.js', { scope: '/' });
  }

  function fetchPublicKey() {
    return fetch('/api/push/vapid-public-key/')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.enabled || !data.publicKey) {
          throw new Error('Push not configured on server');
        }
        return data.publicKey;
      });
  }

  function subscribeUser(churchId) {
    return registerServiceWorker()
      .then(function () { return fetchPublicKey(); })
      .then(function (publicKey) {
        return navigator.serviceWorker.ready.then(function (reg) {
          return reg.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicKey),
          });
        });
      })
      .then(function (subscription) {
        var json = subscription.toJSON();
        return fetch('/api/push/subscribe/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          credentials: 'same-origin',
          body: JSON.stringify({
            endpoint: json.endpoint,
            keys: json.keys,
            church_id: churchId,
          }),
        });
      })
      .then(function (r) {
        if (!r.ok) throw new Error('Subscribe failed');
        return r.json();
      });
  }

  function unsubscribeUser() {
    return navigator.serviceWorker.ready
      .then(function (reg) { return reg.pushManager.getSubscription(); })
      .then(function (sub) {
        if (!sub) return;
        var endpoint = sub.endpoint;
        return sub.unsubscribe().then(function () {
          return fetch('/api/push/unsubscribe/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCsrfToken(),
            },
            credentials: 'same-origin',
            body: JSON.stringify({ endpoint: endpoint }),
          });
        });
      });
  }

  function initBanner(banner) {
    var churchId = banner.getAttribute('data-church-id');
    if (!churchId) return;

    var enableBtn = banner.querySelector('[data-push-enable]');
    var dismissBtn = banner.querySelector('[data-push-dismiss]');
    var statusEl = banner.querySelector('[data-push-status]');

    if (localStorage.getItem('bethel_push_dismissed_' + churchId)) {
      banner.classList.add('hidden');
      return;
    }

    registerServiceWorker().catch(function () {});

    navigator.serviceWorker.ready.then(function (reg) {
      return reg.pushManager.getSubscription();
    }).then(function (sub) {
      if (sub) {
        banner.classList.add('hidden');
      }
    }).catch(function () {});

    if (enableBtn) {
      enableBtn.addEventListener('click', function () {
        enableBtn.disabled = true;
        if (statusEl) statusEl.textContent = 'Enabling…';
        subscribeUser(churchId)
          .then(function () {
            if (statusEl) statusEl.textContent = 'Notifications enabled!';
            banner.classList.add('hidden');
            localStorage.setItem('bethel_push_enabled_' + churchId, '1');
          })
          .catch(function (err) {
            enableBtn.disabled = false;
            if (statusEl) {
              statusEl.textContent = err.message || 'Could not enable. Try again or add site to Home Screen (iPhone).';
            }
          });
      });
    }

    if (dismissBtn) {
      dismissBtn.addEventListener('click', function () {
        localStorage.setItem('bethel_push_dismissed_' + churchId, '1');
        banner.classList.add('hidden');
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-bethel-push-banner]').forEach(initBanner);
  });

  window.BethelPush = {
    subscribe: subscribeUser,
    unsubscribe: unsubscribeUser,
  };
})();
