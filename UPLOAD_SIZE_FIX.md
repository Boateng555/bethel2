# Fix “413 Request Entity Too Large” on production

Your live server (nginx) is blocking large uploads **before** Django can compress them.

## 1. On the server (one-time)

SSH into the server and edit the nginx site config for `bethelprayerministryinternational.com`:

```bash
sudo nano /etc/nginx/sites-available/bethel
```

Inside the `server { ... }` block that handles HTTPS, add:

```nginx
client_max_body_size 25M;
```

Then:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 2. Install ffmpeg (for video compression)

```bash
sudo apt update
sudo apt install -y ffmpeg
ffmpeg -version
```

## 3. Deploy the latest code

Pull/deploy this repo so you have:

- `core/media_utils.py` – server-side image/video compression
- `core/signals.py` – auto-compress on save
- `static/js/media-upload-compress.js` – browser compresses images before upload

Collect static files:

```bash
python manage.py collectstatic --noinput
```

Restart the app:

```bash
sudo systemctl restart bethel   # or your gunicorn service name
```

## What happens now

| Step | Images | Videos |
|------|--------|--------|
| In browser | Resized to ~400 KB JPEG | Large files (>15 MB) warned |
| On server | Compressed again to ~400 KB | Re-encoded to small MP4 (needs ffmpeg) |

After this, uploading WhatsApp photos and event videos from a phone should work reliably.
