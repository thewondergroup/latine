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
2. **Forms (done):** enquiry, newsletter and LACAV forms post to `/send.php` (PHP mail on Krystal) → contact@latinemayfair.com. Change the address at the top of `_src/server/send.php`. Forms only work on the Krystal server (not on GitHub Pages).
   _Old note:_ the events/Christmas enquiry form and newsletter forms are front-end only. Wire to Latine's events inbox + Google Sheet (search `TODO` in build.py / home_body.html).
3. **Christmas:** add festive menus, prices and any Christmas Eve / NYE details once supplied (christmas() in build.py).
4. **Tracking:** add GTM / Meta pixel to `head()` in build.py.
5. **Domain:** `python3 build.py --local --domain` adds the CNAME; then point latinemayfair.com DNS to GitHub Pages.
6. Old URLs kept: /the-restaurant/, /private-dining-room/, /our-menu/, /portfolio-gallery/, /about-us/, /lacav/, /lucky-7/, /careers/, /reservation-policy/, /legal/. Redirects: /journal/ → /press/, /team/ → /about-us/, /main-home/ → /.

## Hosting: Krystal (cPanel)
Upload the contents of the repo root (everything except `.git`, `_src`, `README.md`, `images.txt`, `.gitignore`) into `public_html`. `.htaccess` handles HTTPS, no-www, clean URLs (no .html), old WordPress redirects, 404 page and caching. Keep `public_html/wp-content/uploads/` on the server: the set-lunch and dessert PDFs still link there.
