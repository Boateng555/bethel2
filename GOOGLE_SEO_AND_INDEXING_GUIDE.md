# Google Search Console & SEO – Step-by-Step Guide

This guide walks you through getting Google to **fully recognize and index** all your Bethel church pages (including when **new churches are created**), while **keeping the dynamic nearest-church feature** working.

---

## 1. Submit your site to Google Search Console

1. **Go to Google Search Console**  
   [https://search.google.com/search-console](https://search.google.com/search-console)

2. **Add a property**
   - Click **“Add property”**.
   - Choose **“URL prefix”** and enter your live site URL (e.g. `https://www.yourbethelsite.org`).
   - Use the **exact** URL people use (with or without `www`) and stick to that everywhere (canonical, sitemap, etc.).

3. **Verify ownership** (pick one):
   - **HTML file upload:** Download the file, put it in your site’s root (e.g. so `https://www.yourbethelsite.org/xxxxx.html` is reachable), then click “Verify”.
   - **HTML meta tag:** Add the tag to your main template’s `<head>`. In `templates/core/base.html` you can add:
     ```html
     <meta name="google-site-verification" content="YOUR_CODE_HERE">
     ```
     Then click “Verify” in Search Console.
   - **DNS (recommended if you can):** Add the TXT record Google gives you at your domain DNS. Then verify.

4. **After verification**  
   You’ll see the property in the dashboard. This is required before submitting a sitemap.

---

## 2. Set your site domain for sitemaps (important)

Sitemap URLs must use your **real production domain**. Set it once so the sitemap and Django “Sites” stay correct.

1. **Run migrations** (if you haven’t already) so the Sites table exists:
   ```bash
   python manage.py migrate
   ```

2. **In your production `.env`** (or environment variables), add:
   ```env
   SITE_DOMAIN=www.yourbethelsite.org
   ```
   Use your real domain (with or without `www`, same as in Search Console).

3. **Run the management command** (on the server or after deploy):
   ```bash
   python manage.py set_site_domain
   ```
   Or override from the command line:
   ```bash
   python manage.py set_site_domain --domain=www.yourbethelsite.org
   ```
   This updates Django’s “Sites” so that sitemap URLs are generated with the correct domain.

4. **If you use Django’s Sites in Admin**  
   You can also set it manually: **Admin → Sites → edit the default site** and set **Domain** to `www.yourbethelsite.org` (and **Name** to something like “Bethel”).

---

## 3. Create and submit your sitemap

The project already has a **dynamic sitemap** that includes:

- Static pages (home, events, ministries, churches, about, contact, etc.)
- **Every active, approved church** (directory + church hub and subpages)
- **All public events** (global and church-specific URLs)
- **All ministries** (global and church-specific)
- **All public news**

When you **create and approve a new church**, it is **automatically included** in the sitemap; no extra step is needed.

1. **Check that the sitemap is live**
   - Open: `https://www.yourbethelsite.org/sitemap.xml`
   - You should see an index of sitemaps (static, churches, church_pages, events, etc.) and all URLs should use your real domain.

2. **Submit in Google Search Console**
   - In Search Console, go to **Sitemaps** (left menu).
   - Under “Add a new sitemap”, enter: `sitemap.xml`
   - Click **Submit**.

3. **Re-submit after big changes (optional)**  
   You can use “Request indexing” for the sitemap URL again after adding many new churches or pages. Normally Google will re-crawl on its own.

---

## 4. Ensure all pages are crawlable

1. **Robots.txt**
   - The site serves `/robots.txt` automatically.
   - It allows all crawlers and points to your sitemap:
     - `Allow: /`
     - `Disallow: /admin/`, `/local-admin/`, `/global-admin/`, `/accounts/`, `/api/`
     - `Sitemap: https://www.yourbethelsite.org/sitemap.xml`
   - Check: `https://www.yourbethelsite.org/robots.txt`

2. **No blocking of important pages**
   - Church pages, events, ministries, and news are **not** in any `Disallow`. Only admin and account areas are blocked.

3. **Nearest-church redirect (root `/`)**
   - The root URL `/` redirects users to the nearest church (or global home). This is **fine for SEO**:
     - The sitemap includes both `/` and `/global/` so Google can crawl both.
     - Each church has stable URLs like `/church/<id>/` and `/churches/<id>/`, so indexing is not hurt by the redirect on `/`.

---

## 5. Canonical URLs

- **Base template** (`templates/core/base.html`) includes a **default canonical** for every page:
  ```html
  <link rel="canonical" href="{{ request.scheme }}://{{ request.get_host }}{{ request.path }}">
  ```
- So each URL has a single canonical version (the one you see in the address bar), which helps Google avoid duplicate-content issues.

- **If you ever need a different canonical** (e.g. church event page pointing to the global event URL), you can override in the page template:
  ```django
  {% block canonical %}
  <link rel="canonical" href="https://www.yourbethelsite.org/events/{{ event.id }}/">
  {% endblock %}
  ```

---

## 6. Meta tags for SEO

The base layout already supports:

- **Description**
  - A default description is set for the whole site.
  - Any view can pass `meta_description` in the context to override for that page (e.g. church name, event title).

- **Canonical**
  - As above, automatic per-page canonical.

- **Open Graph (og:title, og:description, og:image, og:url)**
  - Defaults are in the base template; views can pass `og_title`, `og_description`, `og_image` for richer sharing and hints for search.

**Example in a view (e.g. church detail):**
```python
context = {
    'church': church,
    'meta_description': f"{church.name} – {church.city}, {church.country}. Services, events, and ministries.",
    'og_title': church.name,
    'og_description': church.description[:160] if church.description else f"{church.name} in {church.city}",
    'og_image': request.build_absolute_uri(church.logo.url) if church.logo else None,
}
return render(request, 'core/church_detail.html', context)
```

---

## 7. When a new church is created

1. **Admin:** Create the church in Django Admin and set **Active** and **Approved**.
2. **Sitemap:** The next time Google (or anyone) requests `sitemap.xml`, the new church and its pages will **automatically** be included. No manual sitemap edit or re-submission is required.
3. **Optional:** In Search Console you can “Request indexing” for:
   - `https://www.yourbethelsite.org/churches/`
   - The new church URL, e.g. `https://www.yourbethelsite.org/church/<new-church-uuid>/`

---

## 8. Checklist summary

| Step | Action |
|------|--------|
| 1 | Add property in Google Search Console and verify ownership. |
| 2 | Set `SITE_DOMAIN` in `.env` and run `python manage.py set_site_domain` (or set the default Site in Admin). |
| 3 | Open `https://www.yourbethelsite.org/sitemap.xml` and confirm URLs use your domain. |
| 4 | In Search Console → Sitemaps, submit `sitemap.xml`. |
| 5 | Confirm `https://www.yourbethelsite.org/robots.txt` allows `/` and shows your Sitemap URL. |
| 6 | Optionally add `meta_description` (and og_*) in key views (church, event, ministry, news) for better snippets. |

---

## 9. Optional: Request indexing for key URLs

In Search Console:

- **URL Inspection** → enter a URL (e.g. homepage, church list, a specific church) → **Request indexing**.

Use this for a few important URLs after going live or after adding many new churches; you don’t need to do it for every single page.

---

## 10. Keeping the nearest-church feature

- The **nearest-church redirect** on `/` is implemented in the `smart_home` view and is **unchanged** by this SEO setup.
- The sitemap lists both `/` and `/global/` so Google can crawl the global site and all church URLs.
- Canonicals and meta tags do not affect the redirect logic.

With this, Google can discover and index all your church pages (including new ones), while the dynamic nearest-church behavior continues to work as before.
