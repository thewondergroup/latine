# Latine Mayfair — website

Static site for GitHub Pages, served from the repo root on `main`.

## Structure
- Repo root — the built website (index.html, page folders, css/, js/, images/). Generated: don't edit by hand.
- `_src/` — source (underscore keeps it off the live site): `build.py` (all page content + shared nav/footer), `base.css` + `pages.css`, `site.js`, `home_body.html`, `legal_body.html`.

## Edit & rebuild
    cd _src && python3 build.py --local

## Before go-live
1. **Images:** real photography lives in `_src/photos/` and is mapped to each image slot in the `PHOTOS` table in `build.py`. To add or swap a photo, drop it in `_src/photos/`, update `PHOTOS`, and run `python3 build.py --local`. Still missing: a dessert shot and people/team shots (those slots reuse other photos for now).
   **Video:** clips live in `_src/video/` (720×1280 H.264 MP4 + poster JPG, encoded from the Jude Black / Latine originals). Use `VID('name', P)` in `build.py` or `{{VID:name}}` in `home_body.html`; site.js lazy-loads them and only plays them on screen.
2. **Forms (done):** all forms post to a Google Apps Script web app (code in `_src/server/google-apps-script.gs`, attached to the "Latine Website Enquiries" Google Sheet). Events/Christmas enquiries → Enquiries tab + email to contact@latinemayfair.com; newsletter and LACAV → Sign-ups tab. Change recipients via `NOTIFY` in the script, then redeploy as a new version.
   _Old note:_ the events/Christmas enquiry form and newsletter forms are front-end only. Wire to Latine's events inbox + Google Sheet (search `TODO` in build.py / home_body.html).
3. **Christmas:** add festive menus, prices and any Christmas Eve / NYE details once supplied (christmas() in build.py).
4. **Tracking (done 2026-11-16):** GTM-NKBCGM2N is in `head()` / `<body>` (see `GTM_ID` in build.py) and carries GA4 G-FH9929DM7Q. `site.js` pushes `enquiry_submit` and `newsletter_signup` to the dataLayer. Meta pixel not added yet. Search Console is verified by `_src/static/googlea5421e877b5b6937.html` (copied to the root, must stay).
5. **Domain:** always build with `python3 build.py --local --domain`. Without `--domain` the build deletes `CNAME` and the live domain breaks. Needs Python 3.12+ (uses newer f-string syntax) and Pillow.
6. Old URLs kept: /the-restaurant/, /private-dining-room/, /our-menu/, /portfolio-gallery/, /about-us/, /lacav/, /lucky-7/, /careers/, /reservation-policy/, /legal/. Redirects: /journal/ → /press/, /team/ → /about-us/, /main-home/ → /.

## Hosting: Krystal (cPanel)
Upload the contents of the repo root (everything except `.git`, `_src`, `README.md`, `images.txt`, `.gitignore`) into `public_html`. `.htaccess` handles HTTPS, no-www, clean URLs (no .html), old WordPress redirects, 404 page and caching. Keep `public_html/wp-content/uploads/` on the server: the set-lunch and dessert PDFs still link there.

## SEO and AI search
- Every page: unique title + description, canonical, Open Graph/Twitter tags, Restaurant JSON-LD (`restaurant_ld()` in build.py), breadcrumbs.
- FAQPage JSON-LD is generated automatically wherever `faq()` is used (home, The Restaurant, Private Dining, Christmas). Menu JSON-LD on the Menus page is generated from `_src/menus/*.json`.
- `llms.txt` (facts for AI assistants), `robots.txt` (allows search + AI crawlers) and `sitemap.xml` are regenerated on every build from the same data, so prices stay in sync.
- Photos: build makes WebP versions (1600px + 800px) with srcset; JPGs are kept for social-share previews. Alt text lives in the `ALT` table in build.py.
- Favicons are in `_src/static/`.
