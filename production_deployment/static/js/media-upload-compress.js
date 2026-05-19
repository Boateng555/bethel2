/**
 * Compress images in the browser before upload so large phone photos
 * (WhatsApp, camera) do not hit server size limits (413 errors).
 */
(function () {
  'use strict';

  var MAX_IMAGE_DIM = 1920;
  var IMAGE_QUALITY = 0.82;
  var TARGET_MAX_BYTES = 400 * 1024;
  var WARN_VIDEO_BYTES = 15 * 1024 * 1024;

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function showStatus(form, message, isError) {
    var el = form.querySelector('[data-compress-status]');
    if (!el) {
      el = document.createElement('p');
      el.setAttribute('data-compress-status', 'true');
      el.className = 'mt-3 text-sm rounded-lg px-3 py-2 ' + (isError ? 'bg-red-50 text-red-700' : 'bg-blue-50 text-blue-800');
      var submit = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submit && submit.parentNode) {
        submit.parentNode.insertBefore(el, submit);
      } else {
        form.appendChild(el);
      }
    }
    el.textContent = message;
    el.className = 'mt-3 text-sm rounded-lg px-3 py-2 ' + (isError ? 'bg-red-50 text-red-700' : 'bg-blue-50 text-blue-800');
  }

  function clearStatus(form) {
    var el = form.querySelector('[data-compress-status]');
    if (el) el.remove();
  }

  function compressImageFile(file) {
    return new Promise(function (resolve, reject) {
      if (!file.type || file.type.indexOf('image/') !== 0) {
        resolve(file);
        return;
      }

      var reader = new FileReader();
      reader.onload = function (ev) {
        var img = new Image();
        img.onload = function () {
          var w = img.width;
          var h = img.height;
          if (w > MAX_IMAGE_DIM || h > MAX_IMAGE_DIM) {
            if (w >= h) {
              h = Math.round(h * (MAX_IMAGE_DIM / w));
              w = MAX_IMAGE_DIM;
            } else {
              w = Math.round(w * (MAX_IMAGE_DIM / h));
              h = MAX_IMAGE_DIM;
            }
          }

          var canvas = document.createElement('canvas');
          canvas.width = w;
          canvas.height = h;
          var ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, w, h);

          function tryQuality(quality) {
            canvas.toBlob(
              function (blob) {
                if (!blob) {
                  reject(new Error('Could not compress image'));
                  return;
                }
                if (blob.size <= TARGET_MAX_BYTES || quality <= 0.35) {
                  var base = file.name.replace(/\.[^.]+$/, '') || 'image';
                  var out = new File([blob], base + '.jpg', { type: 'image/jpeg', lastModified: Date.now() });
                  resolve(out);
                } else {
                  tryQuality(Math.max(0.35, quality - 0.1));
                }
              },
              'image/jpeg',
              quality
            );
          }

          tryQuality(IMAGE_QUALITY);
        };
        img.onerror = function () { reject(new Error('Invalid image')); };
        img.src = ev.target.result;
      };
      reader.onerror = function () { reject(new Error('Could not read file')); };
      reader.readAsDataURL(file);
    });
  }

  function replaceFileInput(input, newFile) {
    try {
      var dt = new DataTransfer();
      dt.items.add(newFile);
      input.files = dt.files;
    } catch (e) {
      /* older browsers */
    }
  }

  function processForm(form) {
    var imageInputs = form.querySelectorAll('input[type="file"][data-compress-image], input[type="file"][accept*="image"]');
    var videoInputs = form.querySelectorAll('input[type="file"][data-compress-video], input[type="file"][accept*="video"]');
    var tasks = [];

    imageInputs.forEach(function (input) {
      if (!input.files || !input.files[0]) return;
      var file = input.files[0];
      if (!file.type || file.type.indexOf('image/') !== 0) return;
      tasks.push(
        compressImageFile(file).then(function (compressed) {
          replaceFileInput(input, compressed);
          return { type: 'image', before: file.size, after: compressed.size };
        })
      );
    });

    videoInputs.forEach(function (input) {
      if (!input.files || !input.files[0]) return;
      var file = input.files[0];
      if (file.size > WARN_VIDEO_BYTES) {
        tasks.push(Promise.reject(new Error(
          'Video is ' + formatSize(file.size) + '. Please use a shorter clip (under 15 MB) or connect to Wi‑Fi. The server will compress it after upload.'
        )));
      }
    });

    if (!tasks.length) return Promise.resolve();

    return Promise.all(tasks).then(function (results) {
      var parts = results.map(function (r) {
        if (r.type === 'image') {
          return 'Image optimized: ' + formatSize(r.before) + ' → ' + formatSize(r.after);
        }
        return '';
      }).filter(Boolean);
      if (parts.length) showStatus(form, parts.join('. ') + ' Uploading…', false);
    });
  }

  function attachForm(form) {
    if (form.getAttribute('data-compress-attached')) return;
    form.setAttribute('data-compress-attached', 'true');

    form.addEventListener('submit', function (ev) {
      if (form.getAttribute('data-compress-done') === 'true') {
        form.removeAttribute('data-compress-done');
        return;
      }

      var hasFiles = form.querySelector('input[type="file"]');
      if (!hasFiles) return;

      var needsWork = false;
      form.querySelectorAll('input[type="file"]').forEach(function (input) {
        if (input.files && input.files[0]) needsWork = true;
      });
      if (!needsWork) return;

      ev.preventDefault();
      clearStatus(form);
      showStatus(form, 'Optimizing files for upload…', false);

      var submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      processForm(form)
        .then(function () {
          form.setAttribute('data-compress-done', 'true');
          if (submitBtn) submitBtn.disabled = false;
          form.submit();
        })
        .catch(function (err) {
          if (submitBtn) submitBtn.disabled = false;
          showStatus(form, err.message || 'Could not prepare files.', true);
        });
    });
  }

  function init() {
    document.querySelectorAll('form[enctype="multipart/form-data"]').forEach(attachForm);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
