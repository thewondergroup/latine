#!/usr/bin/env python3
"""Builds the Latine Mayfair static site into the repo root (served by GitHub Pages)
   python3 build.py           -> images load from latinemayfair.com (current)
   python3 build.py --local   -> images load from /images (after running fetch_images.sh)
"""
import os, sys, re, html, shutil, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..'))  # repo root = GitHub Pages root
LOCAL = '--local' in sys.argv
REMOTE = 'https://latinemayfair.com/wp-content/uploads/'
BOOK = 'https://www.opentable.co.uk/r/latine-mayfair-reservations-london?restref=474459&lang=en-GB&ot_source=Restaurant%20website'
SITE = 'https://latinemayfair.com/'
GTM_ID = 'GTM-NKBCGM2N'   # Google Tag Manager container (account "Latine Mayfair Account"); carries GA4 G-FH9929DM7Q
GTM_HEAD = ("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
            "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
            "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','" + GTM_ID + "');</script>\n")
GTM_BODY = ('<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=' + GTM_ID + '" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n')
USED = set()

# Real photography (in _src/photos) mapped onto each image slot. Slots not listed keep their placeholder.
PHOTOS = {
 'LATINE_RESTAURANT1.jpg': 'dining-room.jpg', 'Restaurant-2-scaled.jpg': 'dining-room.jpg', 'LATINE-sala-1024x684.png': 'dining-room.jpg',
 'LATINE-carr-1024x684.png': 'terrace-guests.jpg', 'Restaurant-5-1300x650.jpg': 'dining-room.jpg',
 'Restaurant-1-scaled.jpg': 'dining-room-render.jpg', 'Restaurant-8-scaled.jpg': 'dining-room-render.jpg', 'LATINE-restautant-1024x684.png': 'dining-room-render.jpg',
 'Restaurant-6-1300x650.jpg': 'dining-room-render.jpg', 'Restaurant-10-1300x650.jpg': 'dining-room-render.jpg',
 'Restaurant-3-scaled.jpg': 'crudo-bar.jpg', 'House-Story-e1779786021844-1024x684.png': 'crudo-bar.jpg',
 'CANDELA_LATINE-e1779785134779.jpg': 'la-candela.jpg', 'bar-candela-latine.jpg': 'cocktail.jpg',
 'latine-linee.jpg': 'la-candela-stripes.jpg', 'PHOTO-2026-02-25-09-15-34.jpg': 'la-candela-stripes.jpg',
 'PDR1-scaled.jpg': 'el-cielo-table.jpg', 'PDR4-scaled.jpg': 'el-cielo-table.jpg', 'PDR5-scaled.jpg': 'el-cielo-table.jpg',
 'PDR2-scaled.jpg': 'el-cielo-chandelier.jpg', 'PDR6-scaled.jpg': 'el-cielo-chandelier.jpg',
 'Terrace-scaled.jpg': 'terrace-guests.jpg', 'Terrace-2-scaled.jpg': 'terrace-guests.jpg', 'Terrace3-1300x650.jpg': 'terrace.jpg', 'stairs-latine.jpg': 'crudo-bar.jpg',
 'ChatGPT-Image-Apr-15-2026-10_36_38-PM.png': 'prawn-ceviche.jpg', 'ChatGPT-Image-Apr-15-2026-10_41_32-PM.png': 'oysters.jpg',
 'ChatGPT-Image-Apr-16-2026-09_33_05-AM.png': 'tuna-tiradito.jpg', 'ChatGPT-Image-Apr-16-2026-09_35_51-AM.png': 'beef-fillet.jpg',
 'ChatGPT-Image-Apr-16-2026-09_44_31-AM.png': 'ribeye.jpg',
 'DSC_6256-copy-2-scaled.jpg': 'dessert-tatin.jpg',
}

def IMG(p, P=''):
    USED.add(p)
    b = os.path.basename(p)
    if p.startswith('photos/'):          # direct reference to a photo in _src/photos
        return P + 'images/' + b
    if LOCAL:
        return P + 'images/' + PHOTOS.get(b, b)
    return REMOTE + p

def VID(name, P='', eager=False, cls=''):
    # lazy, muted, looping, inline; site.js loads + plays when on screen, pauses when off
    return (f'<video class="vid {cls}" muted loop playsinline preload="none"{" data-eager" if eager else ""} '
            f'poster="{P}video/{name}.jpg" data-src="{P}video/{name}.mp4" aria-hidden="true"></video>')

# ---------------------------------------------------------------- chrome
NAV_L = [('the-restaurant', 'The Restaurant'), ('our-menu', 'Menus'), ('private-dining-room', 'Private Dining'), ('christmas', 'Christmas')]
NAV_R = [('portfolio-gallery', 'Gallery'), ('about-us', 'About')]

ALT = {
 'dining-room': 'The dining room and marble crudo bar at Latine Mayfair',
 'dining-room-render': 'The dining room at Latine Mayfair, with chandelier and marble tables',
 'crudo-bar': 'The marble crudo bar at Latine Mayfair',
 'la-candela': 'La Candela, the first-floor lounge and bar at Latine Mayfair',
 'la-candela-stripes': 'The striped banquette room at La Candela, Latine Mayfair',
 'el-cielo-table': 'El Cielo, the private dining room at Latine Mayfair, with a long table set for dinner',
 'el-cielo-chandelier': 'Candle chandelier and hand-painted woodland walls in El Cielo, Latine Mayfair\'s private dining room',
 'terrace': 'The terrace at Latine in Lancashire Court, Mayfair',
 'terrace-guests': 'Guests at lunch on the terrace at Latine, Lancashire Court, Mayfair',
 'beef-fillet': 'Chargrilled beef fillet with Périgord sauce at Latine Mayfair',
 'ribeye': 'Chargrilled ribeye on the bone with chimichurri Béarnaise at Latine Mayfair',
 'duck-magret': 'Duck magret with confit potimarron and guava sauce at Latine Mayfair',
 'duck-magret-wide': 'Duck magret with confit potimarron and guava sauce at Latine Mayfair',
 'prawn-ceviche': 'Red prawn ceviche with mango and yuzu leche de tigre and plantain chips at Latine Mayfair',
 'oysters': 'Oysters from the crudo bar at Latine Mayfair',
 'tuna-tiradito': 'Tuna tiradito with coconut cream at Latine Mayfair',
 'tuna-tiradito-table': 'Tuna tiradito with bread and butter on the table at Latine Mayfair',
 'steak-tartare': 'Steak tartare on crisp potato pavé at Latine Mayfair',
 'escargots': 'Escargots baked in chimichurri butter at Latine Mayfair',
 'dessert-tatin': 'Tarte tatin au plantain served on a Latine plate',
 'dessert-caramel': 'Caramel dessert with vanilla cream at Latine Mayfair',
 'wine': 'A glass of red wine at Latine Mayfair',
 'cocktail': 'An old fashioned cocktail at La Candela, Latine Mayfair',
}
WEBP = {}   # photo name -> full width, filled at build time
EXTRA_LD = []   # JSON-LD blocks collected while a page body is built (FAQ, menu)

def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>\n'

def plain(t):
    return html.unescape(re.sub(r'<[^>]+>', '', t)).replace('\xa0', ' ').strip()

def restaurant_ld():
    return {
     '@context': 'https://schema.org', '@type': 'Restaurant', '@id': SITE + '#restaurant',
     'name': 'Latine Mayfair', 'alternateName': 'Latine',
     'description': 'French–Latin American restaurant in Lancashire Court, Mayfair, London, with a terrace, crudo bar, the La Candela lounge and El Cielo private dining room.',
     'url': SITE, 'telephone': '+442038873126', 'email': 'contact@latinemayfair.com',
     'image': [SITE + 'images/dining-room.jpg', SITE + 'images/el-cielo-table.jpg', SITE + 'images/terrace-guests.jpg', SITE + 'images/prawn-ceviche.jpg', SITE + 'images/ribeye.jpg'],
     'servesCuisine': ['French', 'Latin American', 'Seafood'], 'priceRange': '£££',
     'address': {'@type': 'PostalAddress', 'streetAddress': '10-11 Lancashire Court', 'addressLocality': 'London', 'addressRegion': 'Greater London', 'postalCode': 'W1S 1EY', 'addressCountry': 'GB'},
     'hasMap': 'https://maps.app.goo.gl/iFrZtrJGWiLJnQhD7',
     'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], 'opens': '12:00', 'closes': '23:59'}],
     'hasMenu': SITE + 'our-menu/', 'acceptsReservations': 'True',
     'potentialAction': {'@type': 'ReserveAction', 'target': {'@type': 'EntryPoint', 'urlTemplate': BOOK}},
     'amenityFeature': [
       {'@type': 'LocationFeatureSpecification', 'name': 'Private dining room (El Cielo): 20 seated, 40+ standing', 'value': True},
       {'@type': 'LocationFeatureSpecification', 'name': 'Outdoor terrace', 'value': True},
       {'@type': 'LocationFeatureSpecification', 'name': 'Cocktail lounge with DJs (La Candela)', 'value': True}],
     'makesOffer': [{'@type': 'Offer', 'name': 'Champagne & oysters', 'description': 'A bottle of Champagne and a dozen oysters. Thursday and Friday 5pm–7pm, Saturday 2pm–5pm.', 'price': '60', 'priceCurrency': 'GBP'}],
     'employee': [{'@type': 'Person', 'name': 'Francisco Lafee', 'jobTitle': 'Executive Chef'}, {'@type': 'Person', 'name': 'Cyril Blaret', 'jobTitle': 'General Manager'}],
     'sameAs': ['https://www.instagram.com/latinemayfair', 'https://www.opentable.co.uk/r/latine-mayfair-reservations-london'],
    }

def head(P, title, desc, path, og, noindex=False):
    ogb = PHOTOS.get(os.path.basename(og), os.path.basename(og))
    oga = ALT.get(os.path.splitext(ogb)[0], 'Latine Mayfair')
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{GTM_HEAD}<title>{html.escape(title, quote=False)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="{'noindex, follow' if noindex else 'index, follow, max-image-preview:large, max-snippet:-1'}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="{'restaurant' if path == '' else 'website'}">
<meta property="og:site_name" content="Latine Mayfair">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{SITE}images/{ogb}">
<meta property="og:image:alt" content="{html.escape(oga)}">
<meta property="og:url" content="{SITE}{path}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1D2A24">
<link rel="icon" href="{P}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{P}favicon.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="{P}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Julius+Sans+One&family=Libre+Franklin:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{P}css/site.css">
{'<link rel="preload" as="image" href="video/latine-film.jpg" fetchpriority="high">' + chr(10) if path == '' else ''}"""


def nav(P, active):
    def li(items):
        return ''.join(f'<li><a href="{P}{s}/"{" class=\"active\"" if s == active else ""}>{t}</a></li>' for s, t in items)
    MO = [('', 'Home', 'dining-room.jpg'), ('the-restaurant/', 'The Restaurant', 'dining-room-render.jpg'), ('our-menu/', 'Menus', 'ribeye.jpg'), ('private-dining-room/', 'Private Dining', 'el-cielo-table.jpg'), ('christmas/', 'Christmas', 'el-cielo-chandelier.jpg'), ('new-year/', 'New Year', 'la-candela.jpg'), ('portfolio-gallery/', 'Gallery', 'terrace-guests.jpg'), ('about-us/', 'About', 'crudo-bar.jpg')]
    cur_i = next((i for i, (u, _, _) in enumerate(MO) if u.strip('/') == active or (u == '' and active == 'home')), 0)
    mo_imgs = ''.join(f'<img src="{P}images/{im}" alt="" data-i="{i}"{" class=\"on\"" if i == cur_i else ""} loading="lazy">' for i, (_, _, im) in enumerate(MO))
    mo_links = ''.join(f'<a href="{(P + u) or './'}" data-i="{i}" style="--i:{i}"{" class=\"cur\"" if (u.strip("/") == active or (u == "" and active == "home")) else ""}><span class="mo-n">{["i","ii","iii","iv","v","vi","vii","viii"][i]}.</span><span class="mo-t">{t}</span></a>' for i, (u, t, _) in enumerate(MO))
    return f'''<div class="festive-bar"><span class="star">✦</span><span class="hide-s">Christmas &amp; New Year at Latine · Festive dining &amp; private parties · </span>Now booking <a href="{P}christmas/">Christmas</a><a href="{P}new-year/">New Year</a></div>
<nav class="nav" id="nav">
  <div class="left" style="display:flex;align-items:center">
    <button class="burger" aria-label="Open menu" id="burger"><span></span><span></span><span></span></button>
    <ul>{li(NAV_L)}</ul>
  </div>
  <a href="{P or './'}" class="wordmark" aria-label="Latine home">Latine</a>
  <div class="right" style="display:flex">
    <ul style="margin-right:30px">{li(NAV_R)}</ul>
    <a class="btn" href="{BOOK}" target="_blank" rel="noopener">Book a table</a>
  </div>
</nav>
<div class="menu-overlay" id="overlay" aria-hidden="true">
  <div class="mo-media" aria-hidden="true">{mo_imgs}</div>
  <div class="mo-main">
    <div class="mo-top"><span class="wordmark">Latine</span><button class="close" id="close" aria-label="Close menu"><span></span><span></span></button></div>
    <nav class="mo-links">{mo_links}</nav>
    <div class="mo-small"><a href="{P}press/">Press</a><a href="{P}careers/">Careers</a><a href="{P}lacav/">LACAV</a><a href="https://www.instagram.com/latinemayfair" target="_blank" rel="noopener">Instagram</a></div>
    <div class="mo-foot">
      <div><span class="eyebrow">Find us</span><p>10–11 Lancashire Court<br>Mayfair, London W1S 1EY</p></div>
      <div><span class="eyebrow">Hours</span><p>Mon – Sat, 12pm – midnight<br><a href="tel:+442038873126">020 3887 3126</a></p></div>
      <div class="mo-ctas"><a class="btn btn-gold" href="{BOOK}" target="_blank" rel="noopener">Book a table</a><a class="btn btn-line" href="{P}christmas/#enquire">Christmas enquiry</a></div>
    </div>
  </div>
</div>
'''

def footer(P):
    return f'''<footer>
  <div class="f-top">
    <div>
      <div class="wordmark">Latine</div>
      <p style="margin-top:18px;font-family:var(--serif);font-size:20px;font-style:italic;color:var(--gold-l)">French elegance. Latin soul.</p>
      <p style="margin-top:22px;font-size:14px;line-height:1.9">10–11 Lancashire Court<br>Mayfair, London W1S 1EY<br><a href="tel:+442038873126">020 3887 3126</a><br><a href="mailto:contact@latinemayfair.com">contact@latinemayfair.com</a></p>
    </div>
    <div>
      <h4>Explore</h4>
      <ul>
        <li><a href="{P}the-restaurant/">The Restaurant</a></li>
        <li><a href="{P}the-restaurant/#la-candela">La Candela</a></li>
        <li><a href="{P}our-menu/">Menus</a></li>
        <li><a href="{P}private-dining-room/">El Cielo private dining</a></li>
        <li><a href="{P}christmas/">Christmas</a></li>
        <li><a href="{P}new-year/">New Year</a></li>
        <li><a href="{P}portfolio-gallery/">Gallery</a></li>
      </ul>
    </div>
    <div>
      <h4>Latine</h4>
      <ul>
        <li><a href="{P}about-us/">About us</a></li>
        <li><a href="{P}press/">Press</a></li>
        <li><a href="{P}careers/">Careers</a></li>
        <li></li>
        <li><a href="{P}lacav/">LACAV</a></li>
        <li><a href="https://www.instagram.com/latinemayfair" target="_blank" rel="noopener">Instagram</a></li>
      </ul>
    </div>
    <div>
      <h4>Hours</h4>
      <p style="font-size:14px;line-height:1.9">Monday – Saturday<br>12pm – midnight<br>Closed Sunday</p>
      <h4 style="margin-top:30px">Invitations &amp; news</h4>
      <p style="font-size:14px">New menus, events and LACAV, opening soon.</p>
      <form class="news" action="https://script.google.com/macros/s/AKfycbxJuxezp2XgzqYO22tVfzeNw8EKvIfsY_Isp0xqpPSo44ozssgDz1rbXOA4F3IJ-64tFQ/exec" method="post"><input type="hidden" name="form" value="Newsletter sign-up"><input type="email" name="email" placeholder="Your email" required aria-label="Email"><button>Join</button></form>
    </div>
  </div>
  <div class="f-bot">
    <span>© 2026 Latine Mayfair Limited</span>
    <span class="credit">Created by <a href="https://thewonderagency.co/" target="_blank" rel="noopener">The Wonder Agency</a></span>
    <span><a href="{P}reservation-policy/">Reservation policy</a><a href="{P}legal/">Privacy</a></span>
  </div>
</footer>
<div class="mbook" id="mbook">
  <a href="{P}christmas/">Christmas</a>
  <a href="{BOOK}" target="_blank" rel="noopener">Book a table</a>
</div>
<script src="{P}js/site.js"></script>
</body>
</html>
'''

FOCUS = {'tuna-tiradito': '48% 62%', 'tuna-tiradito-table': '50% 72%', 'prawn-ceviche': '50% 66%', 'steak-tartare': '52% 55%', 'escargots': '46% 62%',
         'ribeye': '55% 55%', 'duck-magret-wide': '45% 48%', 'duck-magret': '50% 52%', 'beef-fillet': '50% 60%'}

def post(out):
    """webp + srcset for photos, and fill in empty alt text"""
    def img_fix(m):
        tag = m.group(0)
        sm = re.search(r'src="((?:\.\./)*images/)([^"/]+)\.jpg"', tag)
        if not sm or sm.group(2) not in WEBP: return tag
        pre, name = sm.group(1), sm.group(2)
        tag = tag.replace(sm.group(0), f'src="{pre}{name}.webp" srcset="{pre}{name}-800.webp 800w, {pre}{name}.webp {WEBP[name]}w" sizes="(max-width: 900px) 100vw, 60vw"')
        if 'alt=""' in tag and 'data-i=' not in tag and name in ALT:
            tag = tag.replace('alt=""', 'alt="' + html.escape(ALT[name]) + '"')
        if name in FOCUS and 'style=' not in tag:
            tag = tag.replace('<img ', f'<img style="object-position:{FOCUS[name]}" ', 1)
        return tag
    out = re.sub(r'<img\b[^>]*>', img_fix, out)
    return re.sub(r'href="((?:\.\./)*images/[^"/]+)\.jpg"', r'href="\1.webp"', out)

def page(path, title, desc, body_fn, active='', plain=False, og='2026/03/LATINE_RESTAURANT1.jpg', schema=False, crumb='', noindex=False):
    depth = 0 if path == '' else path.strip('/').count('/') + 1
    P = '../' * depth
    del EXTRA_LD[:]
    body = body_fn(P)
    out = head(P, title, desc, path, og, noindex)
    if not noindex:
        out += ld(restaurant_ld())
        if path == '':
            out += ld({'@context': 'https://schema.org', '@type': 'WebSite', '@id': SITE + '#website', 'name': 'Latine Mayfair', 'url': SITE, 'inLanguage': 'en-GB', 'about': {'@id': SITE + '#restaurant'}})
        else:
            out += ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Latine Mayfair', 'item': SITE},
                {'@type': 'ListItem', 'position': 2, 'name': crumb or title.split(' | ')[0], 'item': SITE + path}]})
        out += ''.join(ld(x) for x in EXTRA_LD)
    out += '</head>\n'
    out += f'<body{" class=\"plain\"" if plain else ""}>\n' + GTM_BODY + nav(P, active) + body + footer(P)
    out = post(out)
    d = os.path.join(OUT, path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html') if path else os.path.join(OUT, 'index.html'), 'w').write(out)

def redirect(path, to):
    d = os.path.join(OUT, path); os.makedirs(d, exist_ok=True)
    depth = path.strip('/').count('/') + 1
    rel = '../' * depth + to
    open(os.path.join(d, 'index.html'), 'w').write(f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>Latine Mayfair</title><meta name="robots" content="noindex, follow"><link rel="canonical" href="{SITE}{to}"><meta http-equiv="refresh" content="0; url={rel}"></head><body><a href="{rel}">Continue</a></body></html>')

# ---------------------------------------------------------------- components
def phero(P, img, eyebrow, h1, sub='', ctas='', cls=''):
    return f"""<header class="phero {cls}">
  <img src="{IMG(img, P)}" alt="" fetchpriority="high">
  <div class="pin">
    <h1 class="rv d1"><span class="eyebrow h1-eyebrow">{eyebrow}</span>{h1}</h1>
    {f'<p class="sub rv d2">{sub}</p>' if sub else ''}
    {f'<div class="ctas rv d3">{ctas}</div>' if ctas else ''}
  </div>
</header>
"""

def btn_book(cls='btn-solid', label='Book a table'):
    return f'<a class="btn {cls}" href="{BOOK}" target="_blank" rel="noopener">{label}</a>'

def split(P, img, eyebrow, h2, paras, extra='', rev=False, wide=False, sid='', floor=''):
    ps = ''.join(f'<p class="rv d2">{p}</p>' for p in paras)
    return f'''<div class="split{' rev' if rev else ''}"{f' id="{sid}"' if sid else ''}>
  <div class="split-ph{' wide' if wide else ''} rv">{VID(img[6:], P) if img.startswith('video:') else f'<img src="{IMG(img, P)}" alt="" loading="lazy">'}</div>
  <div class="copy">
    <p class="eyebrow rv">{eyebrow}</p>
    <h2 class="rv d1">{h2}</h2>
    {f'<p class="floor rv d1">{floor}</p>' if floor else ''}
    {ps}
    {f'<div class="rv d3">{extra}</div>' if extra else ''}
  </div>
</div>'''

def enquiry(P, occasion='Christmas party', eyebrow='Events &amp; Christmas enquiries', title='Tell us about your <em>occasion</em>',
            intro='Share a few details and our events team will come back to you with availability, menus and ideas for your day.'):
    occs = ['Christmas party', 'New Year', 'Corporate dinner', 'Birthday', 'Celebration', 'Other']
    labels = {'Other': 'Something else'}
    chips = ''.join(f'<input type="radio" name="occasion" id="o{i}" value="{o}"{" checked" if o == occasion else ""}><label for="o{i}">{labels.get(o, o)}</label>' for i, o in enumerate(occs))
    return f'''<section class="enquire" id="enquire">
  <div class="enq-wrap">
    <div class="enq-head">
      <p class="eyebrow rv">{eyebrow}</p>
      <h2 class="rv d1">{title}</h2>
      <p class="rv d2">{intro}</p>
    </div>
    <form class="enq rv d2" id="enqForm" action="https://script.google.com/macros/s/AKfycbxJuxezp2XgzqYO22tVfzeNw8EKvIfsY_Isp0xqpPSo44ozssgDz1rbXOA4F3IJ-64tFQ/exec" method="post">
      <input type="hidden" name="form" value="Events enquiry"><div class="hp" aria-hidden="true"><label>Leave blank<input name="website" tabindex="-1" autocomplete="off"></label></div>
      <div class="f full"><label>Occasion</label><div class="chips" id="chips">{chips}</div></div>
      <div class="f"><label for="n">Name</label><input id="n" name="name" required autocomplete="name"></div>
      <div class="f"><label for="c">Company (optional)</label><input id="c" name="company" autocomplete="organization"></div>
      <div class="f"><label for="e">Email</label><input id="e" name="email" type="email" required autocomplete="email"></div>
      <div class="f"><label for="p">Phone</label><input id="p" name="phone" type="tel" required autocomplete="tel"></div>
      <div class="f"><label for="d">Preferred date</label><input id="d" name="date" type="date"></div>
      <div class="f"><label for="g">Guests</label><select id="g" name="guests"><option>2–8</option><option>9–14</option><option selected>15–20 (seated)</option><option>21–40 (reception)</option><option>40+</option></select></div>
      <div class="f"><label for="t">Time</label><select id="t" name="time"><option>Lunch (12:00–14:00)</option><option selected>Dinner (19:00–21:00)</option><option>Not sure yet</option></select></div>
      <div class="f"><label for="b">Space</label><select id="b" name="space"><option>El Cielo (private room)</option><option>The Restaurant</option><option>La Candela</option><option selected>Advise me</option></select></div>
      <div class="f full"><label for="m">Anything else?</label><textarea id="m" name="message" placeholder="Budget, dietary needs, a drinks reception, a surprise…"></textarea></div>
      <div class="enq-submit">
        <small>Prefer to talk? Call <a href="tel:+442038873126" style="border-bottom:1px solid">020 3887 3126</a> or email <a href="mailto:contact@latinemayfair.com" style="border-bottom:1px solid">contact@latinemayfair.com</a></small>
        <button class="btn btn-solid" type="submit">Send enquiry</button>
      </div>
    </form>
    <div class="thanks" id="thanks">Thank you, we'll be in touch shortly.<small>Our events team usually replies within one working day.</small></div>
  </div>
</section>
'''

def faq(items):
    EXTRA_LD.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in items]})
    return '<div class="faq">' + ''.join(f'<details class="rv"><summary>{q}</summary><p>{a}</p></details>' for q, a in items) + '</div>'

def visit_band(P, img='2026/09/Terrace3-1300x650.jpg'):
    return f'''<section class="visit" id="visit">
  <div class="bg"><img src="{IMG(img, P)}" alt="" loading="lazy"></div>
  <div class="visit-inner">
    <div>
      <p class="eyebrow">Visit us</p>
      <h2>Moments from<br><em>Bond Street</em></h2>
      <div style="margin-top:34px;display:flex;gap:12px;flex-wrap:wrap">
        {btn_book()}
        <a class="btn btn-line" href="https://maps.app.goo.gl/iFrZtrJGWiLJnQhD7" target="_blank" rel="noopener" style="color:#fff">Directions</a>
      </div>
    </div>
    <div class="col"><p class="eyebrow">Find us</p><p>10–11 Lancashire Court<br>Mayfair, London W1S 1EY</p><p style="margin-top:14px"><a class="u" href="tel:+442038873126">020 3887 3126</a></p></div>
    <div class="col"><p class="eyebrow">Hours</p><p>Monday – Saturday<br>12pm – midnight<br>Closed Sunday</p></div>
  </div>
</section>
'''

PRESS = [
 ('Wallpaper*','Review','https://www.wallpaper.com/travel/restaurants/latine-mayfair-london-review'),
 ('Forbes','New restaurants to try','https://www.forbes.com/sites/joanneshurvell/2026/08/09/7-new-london-restaurants-to-try-summer-2026/'),
 ('The London Standard','Best restaurants for interiors','https://www.standard.co.uk/homesandproperty/interiors/best-restaurants-for-interiors-b1286552.html'),
 ('SheerLuxe','Best restaurants in London','https://sheerluxe.com/culture/restaurants-bars/best-restaurants-in-london'),
 ('Quintessentially','New restaurants in London','https://quintessentially.com/noted/new-restaurants-in-london'),
 ('Country &amp; Town House','First sitting','https://www.countryandtownhouse.com/food-and-drink/latine-mayfair-first-sitting-review/'),
 ('10 Magazine','Feature','https://10magazine.com/latine-mayfair/'),
 ('Luxury Lifestyle Magazine','Meet the chef','https://www.luxurylifestylemag.co.uk/food-and-drink/meet-the-chef-francisco-lafee-executive-chef-at-latine-mayfair-in-london/'),
 ('The Rakish Gent','Review','https://www.therakishgent.co.uk/lifestyle/dining-out-latine-mayfair-review'),
 ('Foodism','Restaurant openings','https://foodism.co.uk/guides/restaurant-openings-london/'),
 ("Harden's",'Coming soon','https://www.hardens.com/restaurants/coming-soon/'),
 ('The Caterer','New openings','https://www.thecaterer.com/news/new-openings-in-june-2026-restaurants-hotels-and-bars'),
 ('The Handbook','June openings','https://www.thehandbook.com/june-restaurant-openings/'),
 ('Yahoo!','Feast for the eyes','https://ca.news.yahoo.com/best-restaurants-serving-feast-interiors-060350840.html'),
 ('Hospitality Interiors','News','https://www.hospitality-interiors.net/news/latine-a-french-latin-mayfair-restaurant-set-to-launch-in-june/'),
 ('Luxury Hospitality Magazine','Introducing Latine','https://lhmagazine.co.uk/introducing-latine-french-latin-mayfair-restaurant-launching-in-june/'),
 ('Restaurant Online','News','https://www.restaurantonline.co.uk/Article/2026/05/20/more-details-released-for-soon-to-launch-mayfair-restaurant-latine/'),
 ('Hospitality &amp; Catering News','Introducing Latine','https://www.hospitalityandcateringnews.com/2026/05/introducing-latine-french-latin-mayfair-restaurant-launching-in-june/'),
 ('FACT Magazine','Launch','https://www.factmagazines.com/london/london/food/french-latin-restaurant-latine-to-launch-in-london-this-summer'),
 ("That's Up",'Best new in Mayfair','https://thatsup.co.uk/london/guide/the-best-new-restaurants-in-mayfair/'),
 ('Miss Jones Group','June openings','https://missjonesgroup.com/june-new-openings/'),
 ('The Sybarite','On the radar','https://thesybarite.co/whats-on-sybarite-radar-june-2026'),
 ('Citizen Femme','Top tables','https://citizen-femme.com/2026/06/08/top-tables-london-restaurants-to-book-in-june-2026-2/'),
 ('DesignMyNight','New restaurants','https://www.designmynight.com/london/blog/new-restaurants-london'),
 ('The Sauce','This weekend','https://thesaucemag.com/things-to-do-in-london-this-weekend-w-london-pride/'),
 ('Sphere Life','Summer openings','https://www.spherelife.com/restaurants/new-restaurants-london-summer-opening'),
 ('The Mayfair Musings','Summer dining','https://www.themayfairmusings.com/home/mayfair-summer-dining-2026'),
 ('Meat &amp; One Veg','Review','https://meatandoneveg.blog/latine-london/'),
 ('Travel &amp; Society','Feature','https://travelandsociety.com/latinemayfair/'),
 ('Travel And Tour World','News','https://www.travelandtourworld.com/news/article/h7rnm0ddrkps/'),
]

def press_marquee():
    return '''<section class="press">
  <p class="eyebrow">As featured in</p>
  <div class="marquee" id="marquee">''' + ''.join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, _, u in PRESS[:12]) + '''</div>
</section>
'''


def offer(P, compact=False):
    times = ('<ul class="of-times">'
             '<li><span>Thursday</span><b>5pm – 7pm</b></li>'
             '<li><span>Friday</span><b>5pm – 7pm</b></li>'
             '<li><span>Saturday</span><b>2pm – 5pm</b></li></ul>')
    return ('<section class="offer' + (' compact' if compact else '') + '" id="champagne-oysters">'
            '<div class="of-ph rv"><img src="' + IMG('2026/04/ChatGPT-Image-Apr-15-2026-10_41_32-PM.png', P) + '" alt="A dozen oysters" loading="lazy">'
            '</div>'
            '<div class="of-copy">'
            '<p class="eyebrow rv">Champagne &amp; oysters</p>'
            '<h2 class="rv d1">A bottle of Champagne,<br><em>a dozen oysters</em></h2>'
            '<p class="of-price rv d1"><span>£60</span></p>'
            '<p class="rv d2">Twelve oysters from the crudo bar with a bottle of Champagne to share. Three afternoons a week.</p>'
            '<div class="rv d2">' + times + '</div>'
            '<div class="rv d3" style="margin-top:34px;display:flex;gap:12px;flex-wrap:wrap">' + btn_book('btn-gold', 'Book your table') + '</div>'
            '</div></section>')

# ---------------------------------------------------------------- HOME
def home_faq(P):
    lunch = MJ('lunch'); xm = MJ('christmas')
    L = 'style="border-bottom:1px solid"'
    items = [
     ('Where is Latine Mayfair?', 'Latine is at 10–11 Lancashire Court, London W1S 1EY, in the cobbled mews between Brook Street and New Bond Street in Mayfair. Bond Street station is a short walk away.'),
     ('What kind of food does Latine serve?', f'French technique with the flavours of Latin America: ceviche, tiradito and oysters from the crudo bar, sharing starters, and fish and meat from the grill, alongside Latin-spirit cocktails and a French and South American wine list. <a href="{P}our-menu/" {L}>See the menus</a>.'),
     ('What are the opening hours?', 'Monday to Saturday, 12pm until midnight, for lunch, dinner and late drinks. Latine is closed on Sundays.'),
     ('How do I book a table?', f'Book online through <a href="{BOOK}" target="_blank" rel="noopener" {L}>OpenTable</a> or call 020 3887 3126. For tables of nine or more, <a href="{P}private-dining-room/#enquire" {L}>send an enquiry</a>.'),
     ('Does Latine have a private dining room?', f'Yes. El Cielo, on the second floor, seats up to 20 guests or holds more than 40 for a standing reception, with menus tailored to the occasion. <a href="{P}private-dining-room/" {L}>Private dining at Latine</a>.'),
     ('Can I book a Christmas party at Latine?', f'Yes. The Christmas menu, {xm["title"]}, is £{xm["price"]} per person, and El Cielo is available for private Christmas parties, with the La Candela lounge downstairs for afterwards. <a href="{P}christmas/" {L}>Christmas at Latine</a>.'),
     ('Is there a set lunch menu?', f'Yes. The set lunch is served {lunch["note"].replace("Monday – Friday", "Monday to Friday").replace("12 – 3pm", "12pm to 3pm")}: {lunch["price"].replace(" · ", " or ")}.'),
     ('What is the Champagne and oysters offer?', 'A bottle of Champagne and a dozen oysters for £60, available Thursday and Friday from 5pm to 7pm and Saturday from 2pm to 5pm.'),
     ('Is there a dress code?', 'There is no strict dress code; most guests choose smart casual. We ask guests to avoid sportswear, beachwear and flip-flops.'),
     ('Does Latine have outdoor seating and a bar?', 'Yes. There is a terrace in Lancashire Court, a marble crudo bar on the ground floor, and La Candela, the first-floor lounge, with cocktails and DJs later in the evening.'),
    ]
    return ('<section class="sec tint" id="faq"><div class="sec-head"><p class="eyebrow rv">Good to know</p>'
            '<h2 class="rv d1">Questions, <em>answered</em></h2></div>' + faq(items) + '</section>\n')

def home(P):
    b = open(os.path.join(HERE, 'home_body.html')).read()
    b = re.sub(r'https://latinemayfair\.com/wp-content/uploads/([^"\)]+\.(?:jpe?g|png|webp))', lambda m: IMG(m.group(1), P), b)
    b = b.replace('{{OFFER}}', offer(P)).replace('{{FAQ}}', home_faq(P))
    b = re.sub(r'\{\{VID:([a-z-]+)(:eager)?\}\}', lambda m: VID(m.group(1), P, bool(m.group(2))), b)
    b = b.replace('<section class="xmas on-dark" id="christmas">', '<section class="xmas on-dark sparkles" id="christmas">')
    # link out to the new inner pages
    b = b.replace('<h3>Afternoon in the mews</h3>', f'<h3><a href="{P}the-restaurant/#terrace">Afternoon in the mews</a></h3>')
    b = b.replace('<h3>Dinner, by candlelight</h3>', f'<h3><a href="{P}the-restaurant/">Dinner, by candlelight</a></h3>')
    b = b.replace('<h3>Later, at La Candela</h3>', f'<h3><a href="{P}the-restaurant/#la-candela">Later, at La Candela</a></h3>')
    b = b.replace('</p>\n  </div>\n  <div class="acts-grid">', f'</p>\n  </div>\n  <div class="acts-grid">', 1)
    b = b.replace('</div>\n    </div>\n    <div class="mosaic', f'</div>\n      <a class="link rv d3" href="{P}our-menu/" style="display:inline-block;margin-top:34px;color:var(--terra)">All menus</a>\n    </div>\n    <div class="mosaic', 1)
    b = b.replace('<div class="xmas-foot rv">', f'<div class="xmas-foot rv">\n      <a class="btn btn-line" href="{P}christmas/">Christmas at Latine</a>\n      <a class="btn btn-line" href="{P}new-year/">New Year at Latine</a>', 1)
    b = b.replace('<div style="margin-top:36px" class="rv d3"><a class="btn btn-solid" href="#enquire">Make an enquiry</a></div>',
                  f'<div style="margin-top:36px;display:flex;gap:12px;flex-wrap:wrap" class="rv d3"><a class="btn btn-solid" href="#enquire">Make an enquiry</a><a class="btn btn-line" href="{P}private-dining-room/">Discover El Cielo</a></div>')
    b = b.replace('<p class="sig rv d3">Hospitality, at the heart of everything.</p>',
                  f'<p class="sig rv d3">Hospitality, at the heart of everything.</p>\n    <a class="link rv d3" href="{P}about-us/" style="margin-top:30px;align-self:flex-start;color:#fff">About Latine</a>')
    return b

# ---------------------------------------------------------------- THE RESTAURANT
def restaurant(P):
    return phero(P, '2026/09/Restaurant-1-scaled.jpg', 'The Restaurant · Latine Mayfair', 'A house of<br><em>many moods</em>',
        'Set across several levels in Lancashire Court, Latine unfolds through a series of distinct spaces, each with its own rhythm, from lunch on the terrace to late nights upstairs.',
        btn_book() + f'<a class="btn btn-line" href="{P}our-menu/">See the menus</a>') + f'''
<section class="sec">
  <div class="levels rv">
    <a href="#terrace"><span class="lv">Ground · outside</span><h3>The Terrace</h3><p>Champagne in the mews, moments from Bond Street.</p></a>
    <a href="#restaurant"><span class="lv">Ground floor</span><h3>The Restaurant</h3><p>Lunch and dinner, with the crudo bar at its heart.</p></a>
    <a href="#la-candela"><span class="lv">First floor</span><h3>La Candela</h3><p>Cocktails, Champagne and DJs as the night turns.</p></a>
    <a href="{P}private-dining-room/"><span class="lv">Second floor</span><h3>El Cielo</h3><p>Our private room, for up to 20 seated.</p></a>
  </div>
</section>
<section class="sec tint" id="restaurant">
''' + split(P, '2026/09/Restaurant-2-scaled.jpg', 'The dining room', 'French gastronomy,<br><em>Latin soul</em>', [
        'In the heart of Mayfair, the dining room is all white linen, warm terracotta walls and soft lamplight, a room that feels as right for a working lunch as for a long, celebratory dinner.',
        'The kitchen explores a dialogue between French gastronomy and Latin American flavour: classic technique, precision and respect for the product, set against bold ingredients, colour and fire.',
        'Wherever possible, everything is prepared in-house.'],
        btn_book(), floor='Ground floor') + '''
</section>
<section class="sec">
''' + split(P, '2026/09/Restaurant-3-scaled.jpg', 'The crudo bar', 'The day\'s catch,<br><em>on marble</em>', [
        'At the centre of the room, the crudo bar showcases the freshest seafood of the day, with oysters, crudos and ceviche-inspired plates made in front of you.',
        'Pull up a stool for a glass of Champagne and a few plates, or start the evening here before moving to your table.'],
        f'<a class="link" href="{P}our-menu/" style="color:var(--terra)">View the menus</a>', rev=True, wide=True) + '''
</section>
''' + offer(P) + '''
<section class="sec tint" id="terrace">
''' + split(P, '2026/09/Terrace-2-scaled.jpg', 'The terrace', 'A pause<br><em>in the mews</em>', [
        'Tucked into the cobbled courtyard of Lancashire Court, our terrace is a quiet corner moments from the bustle of Bond Street.',
        'It\'s the perfect stop after a day of shopping, whether for a glass of Champagne, a cocktail or a relaxed lunch.'],
        btn_book('btn-line', 'Reserve'), floor='Lancashire Court') + f'''
</section>
<section class="sec dark sparkles" id="la-candela" style="position:relative;overflow:hidden">
''' + split(P, 'video:negroni', 'La Candela', 'As the night<br><em>turns</em>', [
        'On the first floor, La Candela brings a different rhythm to the evening. As the night progresses, the space becomes a vibrant lounge where DJs play, bringing energy without losing the restaurant\'s sense of refinement.',
        'With music, cocktails and Champagne flowing, the atmosphere grows livelier, and a carefully curated cocktail programme lets the night carry on well beyond the table.'],
        btn_book('btn-gold', 'Book your evening'), rev=True, floor='First floor') + f'''
  <div class="strip rv" style="margin-top:80px">
    <div><img src="{IMG('2026/04/bar-candela-latine.jpg', P)}" alt="The bar at La Candela" loading="lazy"></div>
    <div><img src="{IMG('2026/04/latine-linee.jpg', P)}" alt="Striped banquettes" loading="lazy"></div>
    <div><img src="{IMG('2026/04/stairs-latine.jpg', P)}" alt="The staircase" loading="lazy"></div>
    <div><img src="{IMG('2026/04/PHOTO-2026-02-25-09-15-34.jpg', P)}" alt="Latine interior" loading="lazy"></div>
  </div>
</section>
<section class="sec">
  <div class="sec-head"><p class="eyebrow rv">Good to know</p><h2 class="rv d1">Before you <em>visit</em></h2></div>
''' + faq([
        ('What are your opening hours?', 'We are open Monday to Saturday from 12pm until midnight, for lunch, dinner and late drinks at La Candela. We are closed on Sundays.'),
        ('Is there a dress code?', 'We don\'t operate a strict formal dress code; most guests choose smart casual. We kindly ask guests to avoid beachwear, sportswear, flip-flops or overly casual clothing, in keeping with the atmosphere of the restaurant.'),
        ('Can you cater for dietary requirements and allergies?', 'Yes. Please add any dietary requirements or allergies to your booking, and always tell our team when you arrive and before ordering.'),
        ('Do you take bookings for larger groups?', f'Yes. For larger tables, private dining in El Cielo or exclusive events, please <a href="{P}private-dining-room/#enquire" style="border-bottom:1px solid">send us an enquiry</a> and our events team will be in touch.'),
        ('What is your cancellation policy?', f'We kindly ask for at least 24 hours\' notice. Late cancellations or no-shows may incur a charge where applicable. See our <a href="{P}reservation-policy/" style="border-bottom:1px solid">reservation policy</a>.'),
    ]) + '''
</section>
''' + visit_band(P)

# ---------------------------------------------------------------- MENUS
import json
def MJ(n): return json.load(open(os.path.join(HERE, 'menus', n + '.json'), encoding='utf-8'))
def esc(t): return html.escape(t, quote=False)
def price(p): return '' if not p else ('£' + (p[:-2] if p.endswith('.0') else p))
def tags(t): return ''.join(f'<span class="tag">{x.upper()}</span>' for x in (t or []))

def dish(i, priced=True):
    pr = '<span class="pr">' + price(i.get('price')) + '</span>' if priced else ''
    d = '<p>' + esc(i['desc']) + '</p>' if i.get('desc') else ''
    return '<div class="dish rv"><div class="dish-top"><h4>' + esc(i['name']) + tags(i.get('tags')) + '</h4>' + pr + '</div>' + d + '</div>'

ORN = '<svg class="orn" viewBox="0 0 84 14" fill="none" stroke="currentColor" stroke-width=".8"><path d="M0 7h34M50 7h34"/><path d="M42 1l6 6-6 6-6-6z"/></svg>'

def food_menu(P):
    food = MJ('food')
    out = []
    breaks = {'Oysters': ('photos/prawn-ceviche.jpg', 'photos/tuna-tiradito.jpg'), 'Mains': ('photos/duck-magret-wide.jpg', None)}
    for s in food:
        cls = 'msec two' if len(s['items']) > 3 else 'msec'
        notes = ''.join(f'<p class="mnote">{esc(n)}</p>' for n in s.get('notes', []))
        if s['title'] in breaks:
            a, b2 = breaks[s['title']]
            imgs = ''.join('<div><img src="' + IMG(x, P) + '" alt="" loading="lazy"></div>' for x in (a, b2) if x)
            out.append('<div class="minter rv">' + imgs + '</div>')
        out.append(f'<section class="{cls}"><h3 class="mh rv">{esc(s["title"])}</h3>{ORN}<div class="dishes">{"".join(dish(i) for i in s["items"])}</div>{notes}</section>')
    return ''.join(out)

def drinks_menu(P, which):
    d = MJ('drinks')
    if which == 'cocktails':
        secs = [x for x in d if x['title'] in ('Signature cocktails', 'Apéritifs', 'Non-alcoholic')]
        secs.sort(key=lambda x: ['Signature cocktails', 'Apéritifs', 'Non-alcoholic'].index(x['title']))
        o = ''
        for x in secs:
            note = '<p class="mnote">' + esc(x['note']) + '</p>' if x.get('note') else ''
            o += '<section class="msec' + (' two' if len(x['items']) > 4 else '') + '"><h3 class="mh rv">' + esc(x['title']) + '</h3>' + ORN + '<div class="dishes">' + ''.join(dish(i) for i in x['items']) + '</div>' + note + '</section>'
        return o
    secs = [x for x in d if x['title'] not in ('Signature cocktails', 'Apéritifs', 'Non-alcoholic')]
    o = '<div class="spirits">'
    for x in secs:
        lis = ''
        for i in x['items']:
            em = '<em>' + esc(i['desc']) + '</em>' if i.get('desc') else ''
            lis += '<li><span>' + esc(i['name']) + em + '</span><b>' + price(i['price']) + '</b></li>'
        o += '<div class="sp rv"><h4>' + esc(x['title']) + '</h4><ul>' + lis + '</ul></div>'
    return o + '</div><p class="mnote">Spirits served at 50ml (25ml on request).</p>'

def wine_menu(P):
    w = MJ('wine')
    def rows(items): return ''.join(f'<li><span class="vt">{i["vintage"]}</span><span class="wn">{esc(i["name"])}</span><b>{price(i["price"])}</b></li>' for i in items)
    def body(sec):
        o = ''
        for r in sec['regions']:
            if r['title']: o += f'<h5 class="wr">{esc(r["title"])}</h5>'
            for x in r['subs']:
                if x['title']: o += f'<h6 class="ws">{esc(x["title"])}</h6>'
                o += f'<ul class="wl">{rows(x["items"])}</ul>'
        return o
    glass = w[0]
    out = f'<section class="msec"><h3 class="mh rv">By the glass</h3>{ORN}<div class="wine-glass">{body(glass)}</div><p class="mnote">{esc(glass.get("note", ""))}</p></section>'
    out += '<section class="msec"><h3 class="mh rv">By the bottle</h3>' + ORN + '<div class="wacc">'
    for i, sec in enumerate(w[1:]):
        n = sum(len(x['items']) for r in sec['regions'] for x in r['subs'])
        out += f'<details class="wd rv"{" open" if i == 0 else ""}><summary><span>{esc(sec["title"])}</span><small>{n} wines</small></summary><div class="wd-b">{body(sec)}</div></details>'
    return out + '</div></section>'

def lunch_menu(P):
    m = MJ('lunch')
    secs = ''.join('<section class="msec"><h3 class="mh rv">' + esc(x['title']) + '</h3>' + ORN + '<div class="dishes">' + ''.join(dish(i, False) for i in x['items']) + '</div></section>' for x in m['sections'])
    return ('<div class="lunch-bar rv"><span>' + esc(m['note']) + '</span><b>' + esc(m['price']) + '</b></div>' + secs)

def dessert_menu(P):
    m = MJ('desserts'); o = ''
    for x in m['sections']:
        note = '<p class="mnote">' + esc(x['note']) + '</p>' if x.get('note') else ''
        if 'list' in x:
            lis = ''.join('<li><span>' + esc(a) + '</span><b>' + esc(b) + '</b></li>' for a, b in x['list'])
            o += '<div class="sp rv"><h4>' + esc(x['title']) + '</h4><ul>' + lis + '</ul>' + note + '</div>'
        elif x['title'].startswith('Glaces'):
            o += '<section class="msec"><h3 class="mh rv">' + esc(x['title']) + '</h3>' + ORN + '<p class="scoops rv">' + ' · '.join(esc(i['name']) for i in x['items']) + '</p>' + note + '</section>'
        else:
            o += '<section class="msec' + (' two' if len(x['items']) > 3 else '') + '"><h3 class="mh rv">' + esc(x['title']) + '</h3>' + ORN + '<div class="dishes">' + ''.join(dish(i, bool(i.get('price'))) for i in x['items']) + '</div></section>'
    # wrap the two list blocks side by side
    o = o.replace('<div class="sp rv"><h4>Coffee', '<div class="hot"><div class="sp rv"><h4>Coffee', 1) + '</div>'
    return o

def set_menu_card(xm, eyebrow):
    secs = ''.join(f'<div class="xm-sec"><h4 class="xm-h">{esc(s["title"])}</h4>' + ''.join(
        f'<div class="xm-i"><h5>{esc(i["name"])}{tags(i.get("tags"))}</h5><p>{esc(i["desc"])}</p>'
        + (f'<p class="xm-plus">{esc(i["note"])}</p>' if i.get('note') else '') + '</div>' for i in s['items'])
        + (f'<p class="xm-note">{esc(s["note"])}</p>' if s.get('note') else '') + '</div>' for s in xm['sections'])
    addon = f'<p class="xm-add">{esc(xm["addon"])}</p>' if xm.get('addon') else ''
    return f"""<div class="xm-card rv">
      <p class="eyebrow">{eyebrow}</p>
      <h3>{esc(xm['title'])}</h3>
      <p class="xm-price">£{xm['price']} <span>per person</span></p>
      {addon}
      {ORN}
      {secs}
      <p class="xm-foot">All prices include VAT. A discretionary 13.5% service charge will be added to your bill.</p>
    </div>"""

def christmas_menu(P, compact=False):
    return set_menu_card(MJ('christmas'), 'Christmas &amp; festive season')

def newyear_menus(P):
    return '<div class="xm-duo">' + ''.join(set_menu_card(m, 'New Year') for m in MJ('newyear')['menus']) + '</div>'

ALLERGEN = ('(V) Vegetarian · (VG) Vegan. Please always inform your server of any allergies or intolerances before ordering. '
            'Not all ingredients are listed and we cannot guarantee the total absence of allergens; information on the fourteen legal allergens is available on request. '
            'All prices include VAT. A discretionary 13.5% service charge will be added to your bill.')

def menu_ld():
    def item(i, priced=True):
        o = {'@type': 'MenuItem', 'name': i['name'].capitalize() if i['name'].isupper() else i['name']}
        if i.get('desc'): o['description'] = i['desc']
        if priced and i.get('price'): o['offers'] = {'@type': 'Offer', 'price': i['price'], 'priceCurrency': 'GBP'}
        if 'vg' in (i.get('tags') or []): o['suitableForDiet'] = 'https://schema.org/VeganDiet'
        elif 'v' in (i.get('tags') or []): o['suitableForDiet'] = 'https://schema.org/VegetarianDiet'
        return o
    def sec(title, items, priced=True): return {'@type': 'MenuSection', 'name': title, 'hasMenuItem': [item(i, priced) for i in items]}
    lunch = MJ('lunch'); xm = MJ('christmas'); des = MJ('desserts'); dr = MJ('drinks')
    cocktails = [x for x in dr if x['title'] in ('Signature cocktails', 'Apéritifs', 'Non-alcoholic')]
    return {'@context': 'https://schema.org', '@type': 'Menu', '@id': SITE + 'our-menu/#menu', 'name': 'Latine Mayfair menus', 'url': SITE + 'our-menu/', 'inLanguage': 'en-GB',
            'mainEntityOfPage': SITE + 'our-menu/', 'hasMenuSection': [
        {'@type': 'MenuSection', 'name': 'À la carte', 'hasMenuSection': [sec(x['title'], x['items']) for x in MJ('food')]},
        {'@type': 'MenuSection', 'name': 'Set lunch', 'description': lunch['note'] + '. ' + lunch['price'], 'hasMenuSection': [sec(x['title'], x['items'], False) for x in lunch['sections']]},
        {'@type': 'MenuSection', 'name': 'Desserts', 'hasMenuSection': [sec(x['title'], x['items']) for x in des['sections'] if 'items' in x]},
        {'@type': 'MenuSection', 'name': 'Cocktails', 'hasMenuSection': [sec(x['title'], x['items']) for x in cocktails]},
        {'@type': 'MenuSection', 'name': 'Christmas menu: ' + xm['title'], 'description': '£' + xm['price'] + ' per person',
         'offers': {'@type': 'Offer', 'price': xm['price'], 'priceCurrency': 'GBP'}, 'hasMenuSection': [sec(x['title'], x['items'], False) for x in xm['sections']]},
    ]}

def menus(P):
    EXTRA_LD.append(menu_ld())
    tabs = [('carte', 'À la carte'), ('lunch', 'Set lunch'), ('desserts', 'Desserts'), ('cocktails', 'Cocktails'), ('wine', 'Wine'), ('bar', 'Spirits &amp; more'), ('christmas-menu', 'Christmas')]
    return phero(P, 'photos/ribeye.jpg', 'Menus · Latine Mayfair', 'Precision,<br>with <em>passion</em>',
        'Rooted in French technique, inspired by Latin America. Crudo and seafood, plates from the grill, a cocktail list built around Latin spirits and a cellar of great houses and new discoveries.',
        btn_book() + '<a class="btn btn-line" href="#carte">Explore the menus</a>') + f"""
<nav class="mtabs" id="mtabs" aria-label="Menus">
  <div class="mtabs-in">{''.join(f'<a href="#{a}">{t}</a>' for a, t in tabs)}</div>
</nav>

<section class="mpage" id="carte">
  <div class="mhead"><p class="eyebrow rv">Lunch &amp; dinner</p><h2 class="rv d1">À la <em>carte</em></h2>
  <p class="rv d2">Crudo from the bar, plates for sharing and mains from the grill. Dishes change with the seasons.</p></div>
  {offer(P, True)}
  <div class="mcard-p">{food_menu(P)}</div>

  <p class="allergen">{ALLERGEN}</p>
</section>

<section class="mpage tint2" id="lunch">
  <div class="mhead"><p class="eyebrow rv">Weekday lunch</p><h2 class="rv d1">Set <em>lunch</em></h2>
  <p class="rv d2">A lighter, quicker lunch in Mayfair: two or three courses from a short seasonal menu.</p></div>
  <div class="mcard-p">{lunch_menu(P)}</div>
</section>

<section class="mpage" id="desserts">
  <div class="mhead"><p class="eyebrow rv">To finish</p><h2 class="rv d1">Desserts</h2>
  <p class="rv d2">French pastry with a Latin accent, house ice creams, and coffee, digestifs and teas.</p></div>
  <div class="mcard-p">{dessert_menu(P)}</div>
</section>

<section class="mpage dark" id="cocktails">
  <div class="mhead"><p class="eyebrow rv">The bar</p><h2 class="rv d1">Cocktails</h2>
  <p class="rv d2">Signatures built around tequila, mezcal, pisco and cachaça, French aperitifs and serious non-alcoholic serves.</p></div>
  <div class="mwith-vid">
    <div class="mvid rv">{VID('martini', P)}</div>
    <div class="mcard-p">{drinks_menu(P, 'cocktails')}</div>
  </div>
</section>

<section class="mpage" id="wine">
  <div class="mhead"><p class="eyebrow rv">The cellar</p><h2 class="rv d1">Wine</h2>
  <p class="rv d2">Burgundy and Bordeaux beside Mendoza, Patagonia and the Uco Valley. Coravin pours of fine wines by the glass.</p></div>
  <div class="mcard-p wide">{wine_menu(P)}</div>
</section>

<section class="mpage dark" id="bar">
  <div class="mhead"><p class="eyebrow rv">Back bar</p><h2 class="rv d1">Spirits &amp; <em>more</em></h2></div>
  <div class="mcard-p wide">{drinks_menu(P, 'spirits')}</div>
</section>

<section class="mpage xmas-m" id="christmas-menu">
  <div class="mhead"><p class="eyebrow rv">Christmas 2026</p><h2 class="rv d1">The festive <em>menu</em></h2>
  <p class="rv d2">Served through the festive season in the restaurant and for private parties in El Cielo.</p></div>
  {christmas_menu(P)}
  <div style="text-align:center;margin-top:50px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap" class="rv">{btn_book('btn-solid', 'Book a festive table')}<a class="btn btn-line" href="{P}christmas/#enquire">Plan a Christmas party</a><a class="btn btn-line" href="{P}new-year/">New Year menus</a></div>
</section>
"""

# ---------------------------------------------------------------- PRIVATE DINING
def private(P):
    return phero(P, '2026/09/PDR6-scaled.jpg', 'Private dining room · Mayfair', 'El Cielo,<br><em>above it all</em>',
        'Latine\'s private room on the second floor: secluded, refined and made for dinners that matter.',
        '<a class="btn btn-solid" href="#enquire">Make an enquiry</a><a class="btn btn-line" href="' + P + 'christmas/">Christmas parties</a>') + f'''
<section class="sec">
''' + split(P, '2026/09/PDR5-scaled.jpg', 'The room', 'An intimate room<br>with <em>a view of its own</em>', [
        'Known as El Cielo, our private dining room sits above the main dining room, a more intimate and secluded setting for private dinners, celebrations and business gatherings.',
        'Hand-painted walls, a single long table, candlelight and the quiet of the mews outside. The room is refined yet relaxed, and lets you enjoy Latine\'s cuisine in a more personal setting.'],
        '''<div class="stats"><div><b>20</b><span>Seated</span></div><div><b>40+</b><span>Reception</span></div><div><b>2nd</b><span>Floor, private</span></div></div>''') + f'''
</section>
<section class="sec tint">
  <div class="sec-head"><p class="eyebrow rv">Occasions</p><h2 class="rv d1">Made for <em>every kind</em> of gathering</h2><p class="rv d2">Private dining menus can be tailored to suit individual requirements, with the full Latine kitchen, cellar and cocktail bar at your disposal.</p></div>
  <div class="acts-grid">
    <article class="act rv"><div class="ph"><img src="{IMG('2026/09/PDR1-scaled.jpg', P)}" alt="" loading="lazy"></div><div class="meta eyebrow"><span>Celebrations</span><span>Up to 20</span></div><h3>Birthdays &amp; milestones</h3><p>Engagements, anniversaries, rehearsal dinners and the birthdays that deserve a long table and a proper toast.</p></article>
    <article class="act rv d1"><div class="ph"><img src="{IMG('2026/04/ChatGPT-Image-Apr-16-2026-09_35_51-AM.png', P)}" alt="" loading="lazy"></div><div class="meta eyebrow"><span>Business</span><span>Lunch or dinner</span></div><h3>Client &amp; team dinners</h3><p>A discreet room minutes from Bond Street and Hanover Square for client lunches, board dinners and team celebrations.</p></article>
    <article class="act rv d2"><div class="ph"><img src="{IMG('2026/03/CANDELA_LATINE-e1779785134779.jpg', P)}" alt="" loading="lazy"></div><div class="meta eyebrow"><span>Receptions</span><span>40+ standing</span></div><h3>Parties &amp; launches</h3><p>Standing receptions with Champagne and cocktails, from product launches to Christmas parties, with La Candela downstairs for later.</p></article>
  </div>
</section>
<section class="sec dark">
  <div class="sec-head"><p class="eyebrow rv">How it works</p><h2 class="rv d1">From first enquiry<br>to <em>last toast</em></h2></div>
  <div class="steps">
    <div class="step rv"><h3>Enquire</h3><p>Tell us your date, numbers and occasion using the form below, by phone or by email.</p></div>
    <div class="step rv d1"><h3>Shape your menu</h3><p>Our events team comes back with availability and menu options tailored to your group.</p></div>
    <div class="step rv d2"><h3>Confirm</h3><p>For private dining we may ask for card details via a secure link to secure the room. We never take full card details by phone.</p></div>
    <div class="step rv d3"><h3>Celebrate</h3><p>On the day, our team looks after every detail so you can enjoy your guests.</p></div>
  </div>
</section>
''' + enquiry(P, 'Celebration', 'Private dining enquiries', 'Plan your evening<br>in <em>El Cielo</em>') + f'''
<section class="sec">
  <div class="sec-head"><p class="eyebrow rv">Questions</p><h2 class="rv d1">Private dining <em>FAQs</em></h2></div>
''' + faq([
        ('How many guests can El Cielo hold?', 'El Cielo can accommodate up to 20 guests seated and over 40 guests for standing receptions.'),
        ('Can the menu be tailored?', 'Yes. A variety of private dining menu options are available and can be tailored to suit your group, occasion and any dietary requirements.'),
        ('Is it available for lunch as well as dinner?', 'Yes, El Cielo is available for both lunch and dinner, Monday to Saturday.'),
        ('Do you require a deposit?', 'For private dining and larger bookings we may request card details to secure the reservation, always through a secure payment link or booking platform. Cancellation terms for private dining will be confirmed at the time of booking.'),
        ('Can we carry on the party afterwards?', 'Of course. La Candela on the first floor comes alive later in the evening with DJs, cocktails and Champagne. Mention it in your enquiry and we\'ll help plan the whole night.'),
    ]) + '''
</section>
'''

# ---------------------------------------------------------------- CHRISTMAS
def christmas(P):
    return phero(P, '2026/09/PDR1-scaled.jpg', 'Christmas parties &amp; festive dining 2026', 'Christmas in Mayfair,<br><em>by candlelight</em>',
        'Long festive lunches, candlelit parties in El Cielo and late nights at La Candela. December at Latine is made for celebrating.',
        '<a class="btn btn-gold" href="#enquire" data-occasion="Christmas party">Plan a Christmas party</a>' + btn_book('btn-line', 'Book a festive table'), cls='dark') + f'''
<section class="sec dark sparkles" style="position:relative;overflow:hidden">
  <div class="sec-head"><p class="eyebrow rv">Ways to celebrate</p><h2 class="rv d1">However you <em>gather</em></h2><p class="rv d2">From a table for two after Bond Street to taking over a whole floor with your team, there's a Latine Christmas for every occasion.</p></div>
  <div class="xmas-cards" style="margin-top:0">
    <article class="xcard rv"><div class="ph"><img src="{IMG('2026/09/Restaurant-8-scaled.jpg', P)}" alt="" loading="lazy"></div><p class="eyebrow">In the restaurant</p><h3>Festive lunch &amp; dinner</h3><p>Gather friends, family or colleagues in the dining room for the season's long lunches and candlelit dinners, with French technique, Latin warmth and Champagne on the table.</p><a class="go link" href="{BOOK}" target="_blank" rel="noopener">Book a table</a></article>
    <article class="xcard rv d1"><div class="ph"><img src="{IMG('2026/09/PDR4-scaled.jpg', P)}" alt="" loading="lazy"></div><p class="eyebrow">El Cielo · Second floor</p><h3>Private Christmas parties</h3><p>Take over our private room with festive menus tailored to your group, and a team looking after every detail from the welcome drink to the last toast.</p><div class="facts"><div><b>20</b><span>Seated</span></div><div><b>40+</b><span>Standing</span></div></div><a class="go link" href="#enquire" data-occasion="Christmas party">Plan your party</a></article>
    <article class="xcard rv d2"><div class="ph">{VID('negroni', P)}</div><p class="eyebrow">La Candela · First floor</p><h3>The after-party</h3><p>When dinner's done, the night carries on upstairs with DJs, cocktails and Champagne. There's no need to leave the building to keep celebrating.</p><a class="go link" href="#enquire" data-occasion="Christmas party">Enquire for groups</a></article>
  </div>
  <div class="sec-head" style="margin-top:clamp(90px,10vw,140px)"><p class="eyebrow rv">Group sizes</p><h2 class="rv d1">Find your <em>space</em></h2></div>
  <div class="sizes rv">
    <div><b>2–8</b><span>The Restaurant</span><p>Book online for festive lunches and dinners in the dining room.</p></div>
    <div><b>9–14</b><span>Large tables</span><p>Send us an enquiry and we'll set a long table in the restaurant.</p></div>
    <div><b>Up to 20</b><span>El Cielo · seated</span><p>Your own private room with a tailored festive menu.</p></div>
    <div><b>40+</b><span>Receptions</span><p>Standing parties with Champagne, cocktails and canapés.</p></div>
  </div>
</section>
<section class="sec">
''' + '''<div class="sec-head"><p class="eyebrow rv">Festive menu</p><h2 class="rv d1">Menu <em>Gran Latine</em></h2><p class="rv d2">Our Christmas menu, served in the restaurant and for private parties in El Cielo.</p></div>
''' + christmas_menu(P) + f'''
  <div class="ny-teaser rv"><p class="eyebrow">And then, New Year</p><p>Two festive menus for seeing in the New Year, at £75 and £120 per person.</p><a class="btn btn-line" href="{P}new-year/">New Year at Latine</a></div>
</section>
'''+ enquiry(P, 'Christmas party', 'Christmas enquiries', 'Let\'s plan your<br><em>Christmas</em>',
        'December evenings go quickly. Tell us your preferred date, numbers and plans, and our events team will come back to you with availability and festive menus.') + '''
<section class="sec">
  <div class="sec-head"><p class="eyebrow rv">Questions</p><h2 class="rv d1">Christmas <em>FAQs</em></h2></div>
''' + faq([
        ('How do I book a Christmas party?', 'Use the enquiry form above, call us on 020 3887 3126 or email contact@latinemayfair.com with your date, numbers and occasion. Our events team will come back with availability and menus.'),
        ('How many people can you host?', 'Up to 8 guests can book online. For 9–14 we\'ll set a large table in the restaurant; El Cielo, our private room, seats up to 20 or holds over 40 for a standing reception.'),
        ('Do festive bookings need a deposit?', 'For larger bookings, private dining and special events we may ask for card details through a secure payment link to secure your reservation. Terms are confirmed at the time of booking.'),
        ('Can you cater for dietary requirements?', 'Yes. Let us know about any dietary requirements or allergies when you enquire, and remind our team on arrival.'),
        ('Can we stay on after dinner?', 'Yes. La Candela on the first floor turns into a lounge with DJs, cocktails and Champagne as the evening goes on, perfect for carrying on the party.'),
    ]) + '''
</section>
'''

# ---------------------------------------------------------------- NEW YEAR
def newyear(P):
    ny = MJ('newyear')['menus']
    lo, hi = ny[0]['price'], ny[1]['price']
    return phero(P, '2026/09/PDR2-scaled.jpg', 'New Year at Latine · Festive menus', 'New Year in Mayfair,<br><em>the Latine way</em>',
        'Two festive menus, oysters and Champagne, and a night that carries on upstairs at La Candela.',
        btn_book('btn-gold', 'Book a table') + '<a class="btn btn-line" href="#enquire" data-occasion="New Year">Enquire for a group</a>', cls='dark') + f"""
<section class="band band3 parallax" aria-label="From the festive menus at Latine">
  <div class="b3"><img src="{P}images/tuna-tiradito.jpg" alt="Tuna tiradito with coconut cream" loading="lazy"></div>
  <div class="b3"><img src="{P}images/steak-tartare.jpg" alt="Steak tartare on crisp potato pavé" loading="lazy"></div>
  <div class="b3"><img src="{P}images/beef-fillet.jpg" alt="Chargrilled beef fillet" loading="lazy"></div>
  <div class="band-cap rv"><span class="eyebrow">From the kitchen</span></div>
</section>
<section class="sec dark sparkles" id="menus" style="position:relative;overflow:hidden">
  <div class="sec-head"><p class="eyebrow rv">Festive menus</p><h2 class="rv d1">Two ways to <em>celebrate</em></h2><p class="rv d2">Choose between two festive menus this New Year, at £{lo} or £{hi} per person. Add six oysters to either for £26.</p></div>
  {newyear_menus(P)}
  <div style="text-align:center;margin-top:50px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap" class="rv">{btn_book('btn-gold', 'Book a table')}<a class="btn btn-line" href="#enquire" data-occasion="New Year">Enquire for a group</a></div>
  <div class="sec-head" style="margin-top:clamp(90px,10vw,140px)"><p class="eyebrow rv">Group sizes</p><h2 class="rv d1">Find your <em>space</em></h2></div>
  <div class="sizes rv">
    <div><b>2–8</b><span>The Restaurant</span><p>Book online for a table in the dining room.</p></div>
    <div><b>9–14</b><span>Large tables</span><p>Send us an enquiry and we'll set a long table in the restaurant.</p></div>
    <div><b>Up to 20</b><span>El Cielo · seated</span><p>Your own private room on the second floor.</p></div>
    <div><b>40+</b><span>Receptions</span><p>Standing parties with Champagne, cocktails and canapés.</p></div>
  </div>
</section>
""" + enquiry(P, 'New Year', 'New Year enquiries', "Let's plan your<br><em>New Year</em>",
        'Tell us your preferred date, numbers and plans, and our events team will come back to you with availability.') + """
<section class="sec">
  <div class="sec-head"><p class="eyebrow rv">Questions</p><h2 class="rv d1">New Year <em>FAQs</em></h2></div>
""" + faq([
        ('How much are the New Year menus at Latine?', f'There are two festive menus: £{lo} per person and £{hi} per person. Six oysters can be added to either for £26. Prices include VAT, and a discretionary 13.5% service charge is added to the bill.'),
        ('How do I book for New Year?', 'Up to 8 guests can book a table online. For larger groups, use the enquiry form above, call us on 020 3887 3126 or email contact@latinemayfair.com with your date and numbers.'),
        ('Are there vegetarian dishes on the New Year menus?', 'Yes. Both menus have a vegetarian choice among the crudo, starters and mains. Let us know about any dietary requirements or allergies when you book, and remind our team on arrival.'),
        ('Can we book a private room for New Year?', 'Yes. El Cielo, our private room on the second floor, seats up to 20 or holds over 40 for a standing reception. Send us an enquiry with your date and numbers.'),
        ('Can we stay on after dinner?', 'Yes. La Candela on the first floor turns into a lounge with DJs, cocktails and Champagne as the evening goes on.'),
    ]) + f"""
  <div class="ny-teaser rv" style="margin-top:70px"><p class="eyebrow">Before the New Year</p><p>Christmas parties and festive dining in the restaurant and El Cielo.</p><a class="btn btn-line" href="{P}christmas/">Christmas at Latine</a></div>
</section>
"""

# ---------------------------------------------------------------- GALLERY
GALLERY = [
 ('2026/03/LATINE_RESTAURANT1.jpg','restaurant','The dining room'),
 ('photos/tuna-tiradito.jpg','food','Tuna tiradito, coconut cream'),
 ('2026/09/PDR1-scaled.jpg','cielo','El Cielo, set for dinner'),
 ('2026/09/Terrace-scaled.jpg','terrace','The terrace in Lancashire Court'),
 ('photos/prawn-ceviche.jpg','food','Red prawn ceviche, plantain chips'),
 ('photos/ribeye.jpg','food','Ribeye, chimichurri Béarnaise'),
 ('2026/09/Restaurant-3-scaled.jpg','restaurant','The crudo bar'),
 ('2026/03/CANDELA_LATINE-e1779785134779.jpg','candela','La Candela'),
 ('photos/beef-fillet.jpg','food','Beef fillet, Périgord sauce'),
 ('photos/steak-tartare.jpg','food','Steak tartare, potato pavé'),
 ('2026/09/PDR2-scaled.jpg','cielo','The chandelier in El Cielo'),
 ('2026/09/Restaurant-1-scaled.jpg','restaurant','The dining room'),
 ('photos/escargots.jpg','food','Escargots, chimichurri butter'),
 ('photos/duck-magret-wide.jpg','food','Duck magret, guava sauce'),
 ('2026/04/latine-linee.jpg','candela','The striped room'),
 ('photos/tuna-tiradito-table.jpg','food','Tuna tiradito'),
 ('photos/duck-magret.jpg','food','Duck magret, confit potimarron'),
 ('2026/09/DSC_6256-copy-2-scaled.jpg','food','Tarte tatin'),
 ('2026/04/bar-candela-latine.jpg','candela','A cocktail at La Candela'),
 ('photos/dessert-caramel.jpg','food','Dessert'),
 ('photos/wine.jpg','candela','Wine'),
 ('photos/terrace-guests.jpg','terrace','Lunch on the terrace'),
]
def gallery(P):
    items = ''.join(f'<a href="{IMG(p, P)}" data-c="{c}"><img src="{IMG(p, P)}" alt="{a}" loading="lazy"></a>' for p, c, a in GALLERY)
    return f'''<header class="plain-head">
  <p class="eyebrow rv">Gallery</p>
  <h1 class="rv d1">Inside <em>Latine</em></h1>
  <p class="rv d2">The dining room, the crudo bar, La Candela, El Cielo and the terrace, plus a few things from the kitchen.</p>
</header>
<section style="padding:0 var(--pad) 140px">
  <div class="filters rv">
    <button class="on" data-f="all">All</button><button data-f="restaurant">Restaurant</button><button data-f="food">Food</button>
    <button data-f="cielo">El Cielo</button><button data-f="candela">La Candela</button><button data-f="terrace">Terrace</button>
  </div>
  <div class="gal">{items}</div>
  <div style="text-align:center;margin-top:70px">{btn_book()}</div>
</section>
<div class="lb" id="lb"><button class="x" aria-label="Close">×</button><button class="pv" aria-label="Previous">‹</button><img alt=""><button class="nx" aria-label="Next">›</button></div>
'''

# ---------------------------------------------------------------- ABOUT
def about(P):
    return phero(P, '2026/05/LATINE-restautant-1024x684.png', 'About Latine Mayfair', 'The meeting of<br><em>two worlds</em>',
        'Latine brings together the elegance of French culinary tradition and the vibrant soul of Latin America in the heart of Mayfair.') + f'''
<section class="sec">
''' + split(P, '2026/05/House-Story-e1779786021844-1024x684.png', 'The concept', 'French mastery,<br><em>Latin spirit</em>', [
        'Latine is built on a simple but powerful idea: the meeting of French culinary mastery with the vibrant flavours and spirit of Latin America.',
        'The kitchen is rooted in French technique, precision, structure and respect for product, while drawing inspiration from the bold ingredients, colours and traditions found across Latin cultures. The result is a menu that feels both refined and expressive.',
        'More than a restaurant, Latine is an experience that evolves through the evening, from elegant dining to a livelier atmosphere as the night goes on, where food, culture and celebration come together.']) + '''
</section>
<section class="story" id="story">
  <div class="ph"><img src="''' + IMG('2026/04/stairs-latine.jpg', P) + '''" alt="" loading="lazy"></div>
  <div class="copy">
    <p class="eyebrow rv">The story of the house</p>
    <h2 class="rv d1">A Mayfair mews,<br><em>brought back to life</em></h2>
    <p class="rv d2">Tucked within Lancashire Court, in the historic mews of Mayfair, Latine sits in a part of London long associated with craftsmanship, trade and quiet elegance.</p>
    <p class="rv d2">These cobbled courtyards were once the working heart behind the grand houses of the neighbourhood, where stables, workshops and small businesses supported the life of Mayfair's townhouses. Over time they became some of the most characterful corners of the city.</p>
    <p class="rv d2">Today Latine brings new life to a place that has always been about activity, exchange and gathering: a historic address turned into a destination for dining, conversation and celebration.</p>
  </div>
</section>
<section class="sec" id="team">
  <div class="sec-head"><p class="eyebrow rv">The team</p><h2 class="rv d1">Hospitality at the <em>heart</em></h2><p class="rv d2">Behind Latine is a team of people who genuinely love what they do. From the kitchen to the floor, everyone shares the same passion for great food, warm hospitality and attention to detail.</p></div>
  <div class="team">
    <div class="person rv"><div class="mono">CB</div><h3>Cyril Blaret</h3><p class="role">General Manager</p></div>
    <div class="person rv d1"><div class="mono">FL</div><h3>Francisco Lafee</h3><p class="role">Executive Chef</p></div>
  </div>
  <p class="note rv">We look forward to welcoming you to Latine.</p>
</section>
<section class="sec tint">
''' + split(P, '2026/05/LATINE-carr-1024x684.png', 'Careers', 'Join the <em>house</em>', [
        'Great restaurants are built by great teams. We\'re always looking for people who share our love for hospitality, food and teamwork, in the kitchen, behind the bar and on the floor.'],
        f'<a class="btn btn-solid" href="{P}careers/">Current opportunities</a>', rev=True, wide=True) + '''
</section>
''' + press_marquee()

# ---------------------------------------------------------------- CAREERS
def careers(P):
    roles = [('Kitchen', 'Chefs', 'Work with high-quality seasonal ingredients and fresh seafood, bringing French technique together with the bold flavours of Latin America, on a menu that keeps evolving.'),
             ('Bar &amp; La Candela', 'Bartenders', 'Craft refined classics and signature cocktails inspired by Latin America, from the restaurant bar to the lounge as the night comes alive.'),
             ('Front of house', 'Floor team', 'Create memorable experiences for guests, from the first welcome to the last glass, in the heart of Mayfair.')]
    cards = ''.join(f'<div class="role-c rv{" d"+str(i) if i else ""}"><p class="eyebrow">{a}</p><h3>{b}</h3><p>{c}</p><a class="link" href="mailto:backoffice@latinemayfair.com?subject=Application%20-%20{re.sub("<[^>]+>|&amp;", "", a).replace(" ", "%20")}">Apply: backoffice@latinemayfair.com</a></div>' for i, (a, b, c) in enumerate(roles))
    return phero(P, '2026/05/LATINE-carr-1024x684.png', 'Careers · Latine Mayfair', 'Great restaurants,<br><em>great teams</em>',
        'We\'re a group of passionate people who genuinely care about what we do, and we\'re always looking for people who share our love of hospitality.', cls='short') + f'''
<section class="sec">
  <div class="sec-head"><p class="eyebrow rv">Working at Latine</p><h2 class="rv d1">Grow with <em>us</em></h2><p class="rv d2">Working with us means being part of a supportive, professional environment where everyone is encouraged to grow. We value dedication, curiosity and a positive attitude, and we want our team to feel proud of the place they're helping to build.</p></div>
  <div class="roles">{cards}</div>
  <p class="note rv">To apply, email your CV to <a href="mailto:backoffice@latinemayfair.com" style="border-bottom:1px solid">backoffice@latinemayfair.com</a>, telling us which team you'd like to join.</p>
</section>
'''

# ---------------------------------------------------------------- PRESS
def press(P):
    rows = ''.join(f'<a class="rv" href="{u}" target="_blank" rel="noopener"><span class="pn">{n}</span><span class="pt">{t} ↗</span></a>' for n, t, u in PRESS)
    return f'''<header class="plain-head">
  <p class="eyebrow rv">Press</p>
  <h1 class="rv d1">As seen <em>in</em></h1>
  <p class="rv d2">Reviews, features and news about Latine from across the press. For press enquiries, email <a href="mailto:contact@latinemayfair.com" style="border-bottom:1px solid">contact@latinemayfair.com</a>.</p>
</header>
<section style="padding:20px var(--pad) 140px"><div class="press-list">{rows}</div></section>
'''

# ---------------------------------------------------------------- LACAV
def lacav(P):
    return f'''<section class="soon-wrap">
  <img src="{IMG('2026/04/bar-candela-latine.jpg', P)}" alt="">
  <div class="pin">
    <p class="eyebrow rv">Coming soon to Latine</p>
    <h1 class="rv d1">LACAV</h1>
    <p class="rv d2">Something new is taking shape at Latine. Join the list to be the first to hear when the doors open.</p>
    <form class="news rv d3" action="https://script.google.com/macros/s/AKfycbxJuxezp2XgzqYO22tVfzeNw8EKvIfsY_Isp0xqpPSo44ozssgDz1rbXOA4F3IJ-64tFQ/exec" method="post"><input type="hidden" name="form" value="LACAV waiting list"><input type="email" name="email" placeholder="Your email" required aria-label="Email"><button>Notify me</button></form>
  </div>
</section>
'''

# ---------------------------------------------------------------- POLICIES
def policy(P):
    return f'''<header class="plain-head">
  <p class="eyebrow rv">Policies</p>
  <h1 class="rv d1">Reservation <em>policy</em></h1>
</header>
<div class="prose">
  <div class="tabs-nav"><a href="#reservations">Reservations</a><a href="#cancellation">Cancellation</a><a href="#dress">Dress code</a><a href="{P}legal/">Privacy policy</a></div>
  <h2 id="reservations">Reservations</h2>
  <p>At Latine Mayfair, we may occasionally request card details to secure larger bookings, private dining reservations or selected special events. When required, this will always be completed through a secure payment link or booking platform. We will never request full card details by telephone.</p>
  <h2 id="cancellation">Cancellation policy</h2>
  <p>We understand that plans can change, and we will always do our best to be flexible should you need to amend, move or cancel your reservation.</p>
  <p>If you need to cancel your booking, we kindly ask that you provide at least 24 hours' notice. Cancellations made with less than 24 hours' notice, or failure to attend a confirmed reservation, may result in a cancellation or no-show charge where applicable.</p>
  <p>For larger bookings, private dining reservations or special events, different cancellation terms may apply. These will be confirmed at the time of booking.</p>
  <h2 id="dress">Dress code</h2>
  <p>At Latine Mayfair, we want our guests to feel comfortable, relaxed and well looked after while enjoying an elegant Mayfair dining experience.</p>
  <p>We do not operate a strict formal dress code. However, most of our guests choose smart casual attire.</p>
  <p>We kindly ask guests to avoid beachwear, sportswear, flip-flops or overly casual clothing, in keeping with the atmosphere of the restaurant.</p>
  <h2>Questions</h2>
  <p>Call us on <a href="tel:+442038873126">020 3887 3126</a> or email <a href="mailto:contact@latinemayfair.com">contact@latinemayfair.com</a>.</p>
</div>
'''

def legal(P):
    return open(os.path.join(HERE, 'legal_body.html')).read()

def notfound(P):
    return f'''<section class="soon-wrap">
  <img src="{IMG('2026/09/Restaurant-1-scaled.jpg', P)}" alt="">
  <div class="pin"><p class="eyebrow">Page not found</p><h1 style="letter-spacing:0;margin:0;font-size:clamp(60px,9vw,130px)">Lost in <em style="color:var(--gold-l)">the mews?</em></h1>
  <p>The page you're looking for has moved. Let us show you back to your table.</p>
  <div style="display:flex;gap:12px;justify-content:center;margin-top:36px;flex-wrap:wrap"><a class="btn btn-gold" href="/">Home</a>{btn_book('btn-line')}</div></div>
</section>
'''

# ---------------------------------------------------------------- llms.txt (plain facts for AI assistants)
def llms_txt():
    lunch = MJ('lunch'); xm = MJ('christmas'); food = MJ('food'); dr = MJ('drinks')
    def nm(i):
        n = re.sub(r'\s+(x\d+|\d+\s?k?g)$', '', i['name'], flags=re.I).strip().capitalize()
        return n + (' (' + i['desc'][0].lower() + i['desc'][1:] + ', £' + i['price'] + ')' if i.get('desc') else ' (£' + i['price'] + ')')
    def names(title, n=5): return '; '.join(nm(i) for x in food if x['title'] == title for i in x['items'][:n])
    sig = ', '.join(i['name'] for x in dr if x['title'] == 'Signature cocktails' for i in x['items'][:6])
    xmas = '; '.join(x['title'] + ': ' + ', '.join(i['name'].capitalize() for i in x['items']) for x in xm['sections'])
    nyl = '\n'.join('- New Year menu "' + m['title'] + '": £' + m['price'] + ' per person. ' + '; '.join(x['title'] + ': ' + ', '.join(i['name'].capitalize() for i in x['items']) for x in m['sections']) for m in MJ('newyear')['menus'])
    return f"""# Latine Mayfair

> Latine is a French–Latin American restaurant at 10–11 Lancashire Court, Mayfair, London W1S 1EY, in the cobbled mews between Brook Street and New Bond Street. It has a terrace, a marble crudo bar, a dining room, the La Candela cocktail lounge and El Cielo, a private dining room. This file is the restaurant's own summary of key facts.

## Key facts
- Name: Latine Mayfair (also written Latine)
- Cuisine: French technique with Latin American flavours; ceviche, tiradito, oysters and seafood, grilled fish and meat
- Address: 10–11 Lancashire Court, Mayfair, London W1S 1EY, United Kingdom
- Nearest station: Bond Street
- Opening hours: Monday to Saturday, 12pm to midnight. Closed Sunday
- Phone: +44 20 3887 3126
- Email: contact@latinemayfair.com
- Reservations: {BOOK.split('?')[0]} (OpenTable) or by phone
- Website: {SITE}
- Instagram: https://www.instagram.com/latinemayfair
- Executive Chef: Francisco Lafee. General Manager: Cyril Blaret
- Dress code: no strict dress code; smart casual is usual. No sportswear, beachwear or flip-flops
- Cancellations: at least 24 hours' notice is requested

## Spaces
- Terrace: outdoor tables in Lancashire Court
- The Restaurant and crudo bar (ground floor): lunch and dinner; oysters, ceviche and crudo prepared at a marble bar
- La Candela (first floor): cocktail lounge that becomes livelier later in the evening, with DJs
- El Cielo (second floor): private dining room for up to 20 guests seated or more than 40 standing, with tailored menus, available for lunch and dinner

## Menus and prices
- À la carte crudo: {names('Crudo')}
- À la carte starters: {names('Starters')}
- À la carte mains: {names('Mains')}
- Set lunch: {lunch['note'].replace(' – ', ' to ')}; {lunch['price'].replace(' · ', ', ')}
- Signature cocktails: {sig}
- Wine: around 136 wines, mainly from France (Champagne, Burgundy, Bordeaux, Loire, Rhône), Italy and South America (chiefly Argentina), with fine wines by the glass
- A discretionary 13.5% service charge is added to the bill
- Full menus with prices: {SITE}our-menu/

## Offers
- Champagne and oysters: a bottle of Champagne and a dozen oysters for £60. Thursday and Friday 5pm to 7pm, Saturday 2pm to 5pm

## Christmas 2026
- Christmas menu "{xm['title']}": £{xm['price']} per person. {xmas}
- Private Christmas parties in El Cielo (20 seated, 40+ standing); larger tables in the restaurant on request
- Details and enquiries: {SITE}christmas/

## New Year
{nyl}
- Six oysters can be added to either menu for £26
- Details and enquiries: {SITE}new-year/

## Pages
- [Home]({SITE}): overview, spaces, offers and frequently asked questions
- [The Restaurant]({SITE}the-restaurant/): terrace, dining room, crudo bar and La Candela
- [Menus]({SITE}our-menu/): à la carte, set lunch, desserts, cocktails, wine, spirits and the Christmas menu, with prices
- [Private Dining]({SITE}private-dining-room/): El Cielo private dining room, capacities and enquiry form
- [Christmas]({SITE}christmas/): festive menu, Christmas parties and enquiry form
- [New Year]({SITE}new-year/): the two New Year festive menus and enquiry form
- [Gallery]({SITE}portfolio-gallery/): photographs of the restaurant and food
- [About]({SITE}about-us/): the concept, the history of Lancashire Court and the team
- [Press]({SITE}press/): reviews and coverage, including Wallpaper*, Forbes, The London Standard and Country & Town House
- [Careers]({SITE}careers/): kitchen, bar and front-of-house roles
- [Reservation policy]({SITE}reservation-policy/): cancellations and dress code
"""

# ---------------------------------------------------------------- BUILD
if __name__ == '__main__':
    # clean only what this script generates (OUT is the repo root)
    GEN = ['index.html', '404.html', 'sitemap.xml', 'robots.txt', 'images.txt', 'CNAME', 'css', 'js', 'images', 'video', 'send.php', '.htaccess', 'llms.txt', 'favicon.svg', 'favicon.png', 'apple-touch-icon.png',
           'the-restaurant', 'our-menu', 'private-dining-room', 'christmas', 'new-year', 'portfolio-gallery', 'about-us', 'careers',
           'press', 'lacav', 'lucky-7', 'reservation-policy', 'legal', 'journal', 'team', 'main-home', '404tmp']
    for g in GEN:
        t = os.path.join(OUT, g)
        if os.path.isdir(t): shutil.rmtree(t)
        elif os.path.exists(t): os.remove(t)
    os.makedirs(os.path.join(OUT, 'css')); os.makedirs(os.path.join(OUT, 'js'))
    open(os.path.join(OUT, 'css/site.css'), 'w').write(open(os.path.join(HERE, 'base.css')).read() + open(os.path.join(HERE, 'pages.css')).read())
    shutil.copy(os.path.join(HERE, 'site.js'), os.path.join(OUT, 'js/site.js'))
    shutil.copytree(os.path.join(HERE, 'video'), os.path.join(OUT, 'video'))
    # site is on GitHub Pages: forms post to the Google Apps Script (server/google-apps-script.gs); send.php/.htaccess kept in _src/server for Apache hosting
    if LOCAL:
        if not os.path.isdir(os.path.join(HERE, 'images')): sys.exit('Run ./fetch_images.sh first')
        os.makedirs(os.path.join(OUT, 'images'))
        for f in os.listdir(os.path.join(HERE, 'images')):
            if f not in PHOTOS: shutil.copy(os.path.join(HERE, 'images', f), os.path.join(OUT, 'images', f))
        from PIL import Image
        cache = os.path.join(HERE, 'webp'); os.makedirs(cache, exist_ok=True)
        for f in sorted(os.listdir(os.path.join(HERE, 'photos'))):
            src = os.path.join(HERE, 'photos', f); name = os.path.splitext(f)[0]
            shutil.copy(src, os.path.join(OUT, 'images', f))            # jpg kept for social-share previews
            full, small = os.path.join(cache, name + '.webp'), os.path.join(cache, name + '-800.webp')
            if not (os.path.exists(full) and os.path.exists(small) and os.path.getmtime(full) >= os.path.getmtime(src)):
                im = Image.open(src).convert('RGB'); a = im.copy(); a.thumbnail((1600, 2600)); a.save(full, 'WEBP', quality=80, method=6)
                b2 = im.copy(); b2.thumbnail((800, 1600)); b2.save(small, 'WEBP', quality=78, method=6)
            WEBP[name] = Image.open(full).size[0]
            for x in (full, small): shutil.copy(x, os.path.join(OUT, 'images', os.path.basename(x)))
    for f in os.listdir(os.path.join(HERE, 'static')): shutil.copy(os.path.join(HERE, 'static', f), os.path.join(OUT, f))

    page('', 'Latine Mayfair | French–Latin Restaurant in Mayfair, London',
         'Latine is a French–Latin American restaurant in Lancashire Court, Mayfair, moments from Bond Street. Crudo bar, cocktails, private dining and Christmas parties.', home, 'home', schema=True)
    page('the-restaurant/', 'The Restaurant, Crudo Bar & La Candela | Latine Mayfair', 'Inside Latine Mayfair: a terrace in Lancashire Court, a marble crudo bar, the dining room and La Candela, the first-floor cocktail lounge with DJs.', restaurant, 'the-restaurant', og='2026/09/Restaurant-1-scaled.jpg', crumb='The Restaurant')
    page('our-menu/', 'Menus & Prices: À la Carte, Lunch, Cocktails | Latine Mayfair', 'Latine Mayfair menus with prices: ceviche, tiradito and oysters, mains from the grill, set lunch from £29, cocktails, wine and the Christmas menu.', menus, 'our-menu', og='photos/duck-magret-wide.jpg', crumb='Menus')
    page('private-dining-room/', 'Private Dining Room in Mayfair | El Cielo at Latine', 'El Cielo, Latine\'s private dining room in Mayfair near Bond Street: up to 20 seated or 40+ standing, with tailored menus for dinners and parties.', private, 'private-dining-room', og='2026/09/PDR6-scaled.jpg', crumb='Private Dining')
    page('christmas/', 'Christmas Parties & Festive Menu in Mayfair | Latine', 'Christmas at Latine Mayfair: the Menu Gran Latine at £120 per person, and private Christmas parties in El Cielo for up to 20 seated or 40+ standing.', christmas, 'christmas', og='2026/09/PDR1-scaled.jpg', crumb='Christmas')
    page('new-year/', 'New Year in Mayfair | Festive Menus at Latine', 'New Year at Latine Mayfair: two festive menus at £75 and £120 per person, with oysters, Champagne and La Candela upstairs. Book a table or enquire for a group.', newyear, 'new-year', og='2026/09/PDR2-scaled.jpg', crumb='New Year')
    page('portfolio-gallery/', 'Gallery | Latine Mayfair Restaurant, London', 'Inside Latine Mayfair: the dining room, crudo bar, La Candela, El Cielo private dining room, terrace and food.', gallery, 'portfolio-gallery', plain=True, crumb='Gallery')
    page('about-us/', 'About Latine | French–Latin Restaurant in Mayfair, London', 'The story of Latine Mayfair: French culinary tradition meets Latin American flavour in a historic mews off Bond Street. Meet the team.', about, 'about-us', og='2026/05/LATINE-restautant-1024x684.png', crumb='About')
    page('careers/', 'Careers | Restaurant Jobs in Mayfair at Latine', 'Join the kitchen, bar or front of house team at Latine, a French–Latin restaurant in Mayfair.', careers, og='2026/05/LATINE-carr-1024x684.png', crumb='Careers')
    page('press/', 'Press & Reviews | Latine Mayfair', 'Latine Mayfair in the press: Wallpaper*, Forbes, The London Standard, SheerLuxe, Quintessentially and more.', press, plain=True, crumb='Press')
    page('lacav/', 'LACAV | Coming Soon to Latine Mayfair', 'LACAV is coming soon to Latine Mayfair. Join the list to hear first.', lacav, crumb='LACAV')
    page('reservation-policy/', 'Reservation Policy | Latine Mayfair', 'Reservation, cancellation and dress code policy at Latine Mayfair.', policy, plain=True, crumb='Reservation Policy')
    page('legal/', 'Privacy Policy | Latine Mayfair', 'Privacy policy for Latine Mayfair Limited.', legal, plain=True, crumb='Privacy Policy')
    # 404 (absolute paths, GitHub Pages serves it from any depth)
    page('404tmp/', 'Page not found | Latine Mayfair', 'Page not found.', notfound, noindex=True)
    t = open(os.path.join(OUT, '404tmp/index.html')).read().replace('href="../', 'href="/').replace('src="../', 'src="/').replace('srcset="../', 'srcset="/').replace(', ../', ', /')
    open(os.path.join(OUT, '404.html'), 'w').write(t); shutil.rmtree(os.path.join(OUT, '404tmp'))
    # old URLs
    redirect('journal/', 'press/'); redirect('lucky-7/', ''); redirect('team/', 'about-us/'); redirect('main-home/', '')
    # At go-live: run with --domain to add the CNAME, then point latinemayfair.com DNS at GitHub Pages
    if '--domain' in sys.argv: open(os.path.join(OUT, 'CNAME'), 'w').write('latinemayfair.com\n')
    urls = ['', 'the-restaurant/', 'our-menu/', 'private-dining-room/', 'christmas/', 'new-year/', 'portfolio-gallery/', 'about-us/', 'careers/', 'press/', 'lacav/', 'reservation-policy/', 'legal/']
    today = datetime.date.today().isoformat()
    prio = {'': '1.0', 'our-menu/': '0.9', 'private-dining-room/': '0.9', 'christmas/': '0.9', 'new-year/': '0.9', 'the-restaurant/': '0.8'}
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod><priority>{prio.get(u, "0.5")}</priority></url>\n' for u in urls) + '</urlset>\n')
    bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot-Extended', 'Bingbot', 'Amazonbot', 'meta-externalagent', 'CCBot']
    open(os.path.join(OUT, 'robots.txt'), 'w').write('# Latine Mayfair: search engines and AI assistants are welcome\nUser-agent: *\nAllow: /\n\n' + ''.join(f'User-agent: {b}\nAllow: /\n\n' for b in bots) + f'Sitemap: {SITE}sitemap.xml\n')
    open(os.path.join(OUT, 'llms.txt'), 'w').write(llms_txt())
    # image list for fetch_images.sh
    open(os.path.join(OUT, 'images.txt'), 'w').write('\n'.join(REMOTE + p for p in sorted(USED)) + '\n')
    print('built', len(urls), 'pages;', len(USED), 'images; local=' + str(LOCAL))
