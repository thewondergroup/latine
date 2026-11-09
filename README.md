# Latine Mayfair — website

Static site for GitHub Pages. Pages serves the `docs/` folder on `main`.

## Structure
- `docs/` — the built website (generated, served by GitHub Pages). Don't edit by hand.
- `src/` — source: `build.py` (all page content + shared nav/footer), `base.css` + `pages.css`, `site.js`, `home_body.html`, `legal_body.html`.

## Edit & rebuild
    cd src && python3 build.py --local

## Before go-live
1. **Images:** the site currently uses on-brand placeholder images (`src/images/`, made by `src/tools/make_placeholders.py`). To swap in the real photos: `cd src && ./fetch_images.sh` (downloads them from the old WordPress site, same filenames, and rebuilds). Or drop new photos into `src/images/` with the same filenames and run `python3 build.py --local`.
2. **Forms:** the events/Christmas enquiry form and newsletter forms are front-end only. Wire to Latine's events inbox + Google Sheet (search `TODO` in build.py / home_body.html).
3. **Christmas:** add festive menus, prices and any Christmas Eve / NYE details once supplied (christmas() in build.py).
4. **Tracking:** add GTM / Meta pixel to `head()` in build.py.
5. **Domain:** `python3 build.py --local --domain` adds the CNAME; then point latinemayfair.com DNS to GitHub Pages.
6. Old URLs kept: /the-restaurant/, /private-dining-room/, /our-menu/, /portfolio-gallery/, /about-us/, /lacav/, /lucky-7/, /careers/, /reservation-policy/, /legal/. Redirects: /journal/ → /press/, /team/ → /about-us/, /main-home/ → /.
