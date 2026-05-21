/**
 * Bethel Web Push — subscribe to church events, news, and sermons on phone.
 */
(function () {
  if (window.__bethelPushLoaded) return;
  window.__bethelPushLoaded = true;

  function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent)
      || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  }

  function isStandalonePWA() {
    return window.matchMedia('(display-mode: standalone)').matches
      || window.navigator.standalone === true;
  }

  function hasPushAPI() {
    return ('serviceWorker' in navigator) && ('PushManager' in window);
  }

  function storageKey(churchId, suffix) {
    return 'bethel_push_' + suffix + '_' + churchId;
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

  function getBanner(churchId) {
    return document.querySelector('[data-bethel-push-banner][data-church-id="' + churchId + '"]');
  }

  function hideBanner(banner) {
    if (!banner) return;
    banner.classList.add('hidden');
    banner.setAttribute('aria-hidden', 'true');
    banner.setAttribute('hidden', 'hidden');
    banner.style.display = 'none';
  }

  function showBanner(banner) {
    if (!banner) return;
    banner.classList.remove('hidden');
    banner.removeAttribute('aria-hidden');
    banner.removeAttribute('hidden');
    banner.style.display = '';
  }

  function pushSetupMessage() {
    if (window.__bethelWebpushEnabled === false) {
      return 'Phone notifications are not set up on the server yet. Please try again later.';
    }
    if (isIOS() && !isStandalonePWA()) {
      return 'On iPhone: add this site to your Home Screen (Share → Add to Home Screen), open that app icon, then tap Enable here.';
    }
    if (!hasPushAPI()) {
      return 'This browser does not support notifications. Use Chrome/Android, or open from your iPhone Home Screen app.';
    }
    return '';
  }

  function isDismissed(churchId) {
    try {
      return localStorage.getItem(storageKey(churchId, 'dismissed')) === '1';
    } catch (e) {
      return false;
    }
  }

  function setDismissed(churchId, dismissed) {
    try {
      if (dismissed) {
        localStorage.setItem(storageKey(churchId, 'dismissed'), '1');
      } else {
        localStorage.removeItem(storageKey(churchId, 'dismissed'));
      }
    } catch (e) { /* private browsing */ }
  }

  function setEnabled(churchId, enabled) {
    try {
      if (enabled) {
        localStorage.setItem(storageKey(churchId, 'enabled'), '1');
        localStorage.removeItem(storageKey(churchId, 'dismissed'));
      } else {
        localStorage.removeItem(storageKey(churchId, 'enabled'));
      }
    } catch (e) { /* ignore */ }
  }

  function registerServiceWorker() {
    return navigator.serviceWorker.register('/sw.js', { scope: '/' });
  }

  function fetchPublicKey() {
    return fetch('/api/push/vapid-public-key/')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        window.__bethelWebpushEnabled = !!data.enabled;
        if (!data.enabled || !data.publicKey) {
          throw new Error(pushSetupMessage() || 'Push not configured on server');
        }
        return data.publicKey;
      });
  }

  function requestNotificationPermission() {
    if (!('Notification' in window)) {
      return Promise.resolve('default');
    }
    if (Notification.permission === 'granted' || Notification.permission === 'denied') {
      return Promise.resolve(Notification.permission);
    }
    return Notification.requestPermission();
  }

  function subscribeUser(churchId) {
    var setupMsg = pushSetupMessage();
    if (setupMsg) {
      return Promise.reject(new Error(setupMsg));
    }
    return requestNotificationPermission()
      .then(function (perm) {
        if (perm === 'denied') {
          throw new Error('Notifications are blocked. In iPhone Settings → Notifications, allow alerts for Bethel.');
        }
        if (perm !== 'granted') {
          throw new Error('Tap Allow when your phone asks for notification permission.');
        }
        return registerServiceWorker();
      })
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
        if (!r.ok) throw new Error('Could not save subscription. Refresh and try again.');
        return r.json();
      });
  }

  function unsubscribeUser() {
    if (!hasPushAPI()) {
      return Promise.resolve();
    }
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

  function hasActiveSubscription() {
    if (!hasPushAPI()) {
      return Promise.resolve(false);
    }
    return Promise.race([
      navigator.serviceWorker.ready
        .then(function (reg) { return reg.pushManager.getSubscription(); })
        .then(function (sub) { return !!sub; }),
      new Promise(function (resolve) { setTimeout(function () { resolve(false); }, 2000); }),
    ]).catch(function () { return false; });
  }

  function syncSettingsToggle(churchId, on) {
    var toggle = document.querySelector('[data-push-settings-toggle][data-church-id="' + churchId + '"]');
    if (toggle) toggle.checked = !!on;
    var status = document.querySelector('[data-push-settings-status][data-church-id="' + churchId + '"]');
    if (status) {
      status.textContent = on
        ? 'Notifications are on for this church.'
        : 'Notifications are off.';
    }
  }

  function getStatusEl(churchId) {
    var banner = getBanner(churchId);
    if (!banner) return null;
    var statusEl = banner.querySelector('[data-push-status]');
    if (!statusEl) {
      statusEl = document.createElement('p');
      statusEl.setAttribute('data-push-status', '');
      statusEl.className = 'text-xs mt-1 text-yellow-200 min-h-[1rem]';
      var textBlock = banner.querySelector('.min-w-0');
      if (textBlock) textBlock.appendChild(statusEl);
    }
    return statusEl;
  }

  function showStatus(churchId, message, isError) {
    var statusEl = getStatusEl(churchId);
    if (!statusEl) return;
    statusEl.textContent = message;
    statusEl.classList.remove('hidden');
    statusEl.className = 'text-xs mt-1 min-h-[1rem] ' + (isError ? 'text-yellow-200' : 'text-green-200');
  }

  function syncEnableButton(churchId) {
    var banner = getBanner(churchId);
    if (!banner) return;
    var enableBtn = banner.querySelector('[data-push-enable]');
    if (!enableBtn) return;
    enableBtn.disabled = false;
    enableBtn.removeAttribute('aria-disabled');
  }

  function dismissBanner(churchId) {
    setDismissed(churchId, true);
    hideBanner(getBanner(churchId));
  }

  function enableBanner(churchId) {
    var setupMsg = pushSetupMessage();
    if (setupMsg) {
      showStatus(churchId, setupMsg, true);
      return Promise.resolve();
    }

    var banner = getBanner(churchId);
    var enableBtn = banner && banner.querySelector('[data-push-enable]');
    if (enableBtn) enableBtn.disabled = true;
    showStatus(churchId, 'Enabling…', false);

    return subscribeUser(churchId)
      .then(function () {
        setEnabled(churchId, true);
        syncSettingsToggle(churchId, true);
        hideBanner(banner);
      })
      .catch(function (err) {
        if (enableBtn) enableBtn.disabled = false;
        showBanner(banner);
        var msg = (err && err.message) ? err.message : 'Could not enable notifications.';
        showStatus(churchId, msg, true);
        syncSettingsToggle(churchId, false);
      });
  }

  function refreshBannerVisibility(churchId) {
    var banner = getBanner(churchId);
    if (!banner) return;

    if (isDismissed(churchId)) {
      hideBanner(banner);
      return;
    }

    syncEnableButton(churchId);
    var setupMsg = pushSetupMessage();
    if (setupMsg) {
      showBanner(banner);
      showStatus(churchId, setupMsg, true);
      return;
    }

    hasActiveSubscription().then(function (active) {
      if (isDismissed(churchId)) {
        hideBanner(banner);
        return;
      }
      if (active) {
        hideBanner(banner);
        setEnabled(churchId, true);
      } else {
        showBanner(banner);
      }
    });
  }

  function initBanner(banner) {
    var churchId = banner.getAttribute('data-church-id');
    if (!churchId || banner.getAttribute('data-push-init') === '1') return;
    banner.setAttribute('data-push-init', '1');

    fetch('/api/push/vapid-public-key/')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        window.__bethelWebpushEnabled = !!data.enabled;
        syncEnableButton(churchId);
        refreshBannerVisibility(churchId);
      })
      .catch(function () {
        window.__bethelWebpushEnabled = false;
        syncEnableButton(churchId);
        refreshBannerVisibility(churchId);
      });

    if (hasPushAPI()) {
      registerServiceWorker().catch(function () {});
    }
  }

  function initSettingsModal() {
    var modal = document.getElementById('bethel-push-settings-modal');
    if (!modal || modal.getAttribute('data-push-init') === '1') return;
    modal.setAttribute('data-push-init', '1');

    var churchId = modal.getAttribute('data-church-id');
    if (!churchId) return;

    var openBtns = document.querySelectorAll('[data-push-settings-open]');
    var closeBtns = modal.querySelectorAll('[data-push-settings-close]');
    var toggle = modal.querySelector('[data-push-settings-toggle]');
    var showPromptBtn = modal.querySelector('[data-push-show-prompt]');
    var statusEl = modal.querySelector('[data-push-settings-status]');

    function openModal() {
      modal.classList.remove('hidden');
      modal.style.display = '';
      document.body.style.overflow = 'hidden';
      refreshSettingsState();
    }

    function closeModal() {
      modal.classList.add('hidden');
      modal.style.display = 'none';
      document.body.style.overflow = '';
    }

    function refreshSettingsState() {
      var setupMsg = pushSetupMessage();
      if (setupMsg && statusEl) {
        statusEl.textContent = setupMsg;
        if (toggle) toggle.checked = false;
        return;
      }
      hasActiveSubscription().then(function (active) {
        var enabled = active || localStorage.getItem(storageKey(churchId, 'enabled')) === '1';
        if (toggle) toggle.checked = enabled;
        if (statusEl) {
          statusEl.textContent = enabled
            ? 'You will receive updates about events, sermons, and news.'
            : 'Turn on to get events, sermons, and news on your phone.';
        }
      });
    }

    openBtns.forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        openModal();
        var mobileMenu = document.getElementById('mobile-menu');
        if (mobileMenu) mobileMenu.classList.add('hidden');
      });
    });

    closeBtns.forEach(function (btn) {
      btn.addEventListener('click', closeModal);
    });

    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeModal();
    });

    if (toggle) {
      toggle.addEventListener('change', function () {
        if (toggle.checked) {
          if (statusEl) statusEl.textContent = 'Enabling…';
          enableBanner(churchId);
        } else {
          if (statusEl) statusEl.textContent = 'Turning off…';
          unsubscribeUser()
            .then(function () {
              localStorage.removeItem(storageKey(churchId, 'enabled'));
              setDismissed(churchId, true);
              refreshSettingsState();
              hideBanner(getBanner(churchId));
            })
            .catch(function () {
              toggle.checked = true;
              if (statusEl) statusEl.textContent = 'Could not turn off. Try again.';
            });
        }
      });
    }

    if (showPromptBtn) {
      showPromptBtn.addEventListener('click', function () {
        setDismissed(churchId, false);
        refreshBannerVisibility(churchId);
        closeModal();
      });
    }
  }

  function runInit() {
    document.querySelectorAll('[data-bethel-push-banner]').forEach(initBanner);
    initSettingsModal();

    document.addEventListener('click', function (e) {
      var enableBtn = e.target.closest('[data-push-enable]');
      if (enableBtn) {
        e.preventDefault();
        e.stopPropagation();
        var churchId = enableBtn.getAttribute('data-church-id')
          || (enableBtn.closest('[data-bethel-push-banner]') || {}).getAttribute('data-church-id');
        if (!churchId) return;
        enableBanner(churchId);
        return;
      }
      var dismissBtn = e.target.closest('[data-push-dismiss]');
      if (dismissBtn) {
        e.preventDefault();
        e.stopPropagation();
        var dismissId = dismissBtn.getAttribute('data-church-id')
          || (dismissBtn.closest('[data-bethel-push-banner]') || {}).getAttribute('data-church-id');
        if (dismissId) dismissBanner(dismissId);
      }
    }, true);
  }

  window.bethelPushEnableClick = function (churchId, evt) {
    if (evt && evt.preventDefault) evt.preventDefault();
    enableBanner(churchId);
    return false;
  };

  window.bethelPushDismissClick = function (churchId, evt) {
    if (evt && evt.preventDefault) evt.preventDefault();
    dismissBanner(churchId);
    return false;
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runInit);
  } else {
    runInit();
  }

  window.BethelPush = {
    subscribe: subscribeUser,
    unsubscribe: unsubscribeUser,
    dismiss: dismissBanner,
    enable: enableBanner,
    showBanner: function (churchId) {
      setDismissed(churchId, false);
      refreshBannerVisibility(churchId);
    },
    hideBanner: dismissBanner,
  };

  window.BethelPushUI = {
    dismiss: dismissBanner,
    enable: enableBanner,
    refresh: refreshBannerVisibility,
  };
})();
