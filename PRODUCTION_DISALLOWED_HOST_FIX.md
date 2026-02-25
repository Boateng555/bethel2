# Fix: DisallowedHost for bethelprayerministryinternational.com

If you see **Invalid HTTP_HOST header: 'bethelprayerministryinternational.com'** and **ALLOWED_HOSTS** shows only `['127.0.0.1', 'localhost']`, the app on the server is not using the updated settings or not loading your production env.

---

## Option 1: Deploy latest code (recommended)

1. **Copy `.env.production` to the server** (if you use it) so it’s in the project root next to `manage.py`. The updated `backend/settings.py` **loads `.env.production` automatically** if that file exists (after `.env`), so `DJANGO_ALLOWED_HOSTS` from `.env.production` will be used.
2. On the server (e.g. `/home/testsite.local`), pull the latest code:
   ```bash
   cd /home/testsite.local
   git pull origin main
   ```
3. Restart the app (e.g. Gunicorn):
   ```bash
   sudo systemctl restart gunicorn
   # or however you restart (e.g. supervisor, docker)
   ```
4. The updated `backend/settings.py` also **includes** `bethelprayerministryinternational.com` and `www.bethelprayerministryinternational.com` in the **default** `ALLOWED_HOSTS`, so even without any `.env` file the site will work after deploy.

---

## Option 2: Fix without deploy (env var on server)

If you cannot deploy right now, set the env var so the **current** settings on the server see the domain.

1. On the server, ensure your app loads a `.env` file that contains:
   ```env
   DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,bethelprayerministryinternational.com,www.bethelprayerministryinternational.com
   ```
2. **Important:** Django’s `load_dotenv()` in `backend/settings.py` loads **`.env`** by default, not `.env.production`. So either:
   - **Copy** your production env into `.env` on the server:
     ```bash
     cp .env.production .env
     ```
   - Or **symlink:** `ln -sf .env.production .env`
   - Or in the command that starts Gunicorn, set the variable:
     ```bash
     export DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,bethelprayerministryinternational.com,www.bethelprayerministryinternational.com
     ```
3. Restart Gunicorn (or your app server) so it picks up the new env.

---

## Option 3: Load `.env.production` in settings

To use `.env.production` on the server without renaming it, you can load it explicitly in `backend/settings.py` (e.g. only when not in DEBUG or when a certain env is set). Alternatively, on the server you can start the app with:

```bash
export DJANGO_SETTINGS_MODULE=backend.settings
# Load .env.production into environment before starting gunicorn
set -a && source .env.production && set +a
gunicorn ...
```

---

## Verify

After applying one of the options, open:

- https://bethelprayerministryinternational.com/robots.txt  
- https://bethelprayerministryinternational.com/sitemap.xml  
- https://bethelprayerministryinternational.com/churches/ghana/accra/  

They should load without DisallowedHost.
