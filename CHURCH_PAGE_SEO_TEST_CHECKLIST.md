# Step 3: Test Church Detail Pages – Checklist

Use this to confirm each church page is **crawlable and indexable** by Google.

---

## What was updated

- **Canonical URL**: Each church detail page now outputs `<link rel="canonical" href="https://yoursite.com/churches/<uuid>/">` so the UUID URL is the canonical version (even if users land via `/churches/country/city/`).
- **Meta title**: Already set per church: `{{ church.name }} - Bethel Church`.
- **Meta description**: Now set in the view from church description or a default (e.g. “Church name in City, Country. Services, events, ministries…”), max 160 characters.
- **Open Graph**: `og:title`, `og:description`, `og:image` (church logo or banner) and `og:url` are set for sharing and crawlers.
- **No login**: Church detail view has no `@login_required`; content is public.

---

## How to test (2–3 example churches)

### 1. Pick 2–3 churches

From your directory, choose 2–3 churches (e.g. different countries/cities). Note their **canonical URLs** (e.g. `https://bethelprayerministryinternational.com/churches/<uuid>/`). You can get UUIDs from Django Admin → Churches or from the “View” link on the church list.

### 2. For each church page, check in the browser

Open the church’s canonical URL (e.g. `https://bethelprayerministryinternational.com/churches/<uuid>/`).

| Check | How to verify |
|-------|-------------------------------|
| **Page loads** | Page loads without errors. |
| **Canonical in source** | Right‑click → View Page Source. Search for `canonical`. You should see: `<link rel="canonical" href="https://bethelprayerministryinternational.com/churches/<same-uuid>/">` and the URL should match the address bar. |
| **Meta title** | Browser tab shows “Church Name - Bethel Church”. Or in source: `<title>Church Name - Bethel Church</title>`. |
| **Meta description** | In source, find `<meta name="description" content="...">` and confirm it has a short description (church name/location or church description). |
| **Content visible** | Page content (name, location, events, ministries, etc.) is visible **without logging in**. |

### 3. Optional: check Open Graph

- In source, search for `og:title`, `og:description`, `og:image`, `og:url`. They should be present and use the same church and canonical URL.
- Or use [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/) or [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) and paste the church URL to see how it would be shared.

### 4. Optional: location URL redirect

If you use `/churches/country/city/` (e.g. `/churches/germany/hamburg/`):

- Open that URL and confirm it **redirects** to the canonical `/churches/<uuid>/` URL.
- Then on the canonical page, confirm the canonical tag in the source points to that same `/churches/<uuid>/` URL.

---

## Quick “in source” checks (one church)

1. Open: `https://bethelprayerministryinternational.com/churches/<uuid>/`
2. View Page Source (Ctrl+U / Cmd+U).
3. Confirm:
   - `<title>{{ church.name }} - Bethel Church</title>`
   - `<link rel="canonical" href="https://.../churches/<uuid>/">`
   - `<meta name="description" content="...">`
   - No `login_required`; content is visible without signing in.

If all of the above are true for your 2–3 example churches, those church pages are in good shape for Google to crawl and index.
