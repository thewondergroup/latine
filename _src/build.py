#!/usr/bin/env python3
"""Builds the Latine Mayfair static site into the repo root (served by GitHub Pages)
   python3 build.py           -> images load from latinemayfair.com (current)
   python3 build.py --local   -> images load from /images (after running fetch_images.sh)
"""
import os, sys, re, html, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..'))  # repo root = GitHub Pages root
LOCAL = '--local' in sys.argv
REMOTE = 'https://latinemayfair.com/wp-content/uploads/'
BOOK = 'https://www.opentable.co.uk/r/latine-mayfair-reservations-london?restref=474459&lang=en-GB&ot_source=Restaurant%20website'
SITE = 'https://latinemayfair.com/'
USED = set()

# Real photography (in _src/photos) mapped onto each image slot. Slots not listed keep their placeholder.
PHOTOS = {
 'LATINE_RESTAURANT1.jpg': 'dining-room.jpg', 'Restaurant-2-scaled.jpg': 'dining-room.jpg', 'LATINE-sala-1024x684.png': 'dining-room.jpg',
 'LATINE-carr-1024x684.png': 'dining-room.jpg', 'Restaurant-5-1300x650.jpg': 'dining-room.jpg',
 'Restaurant-1-scaled.jpg': 'dining-room-render.jpg', 'Restaurant-8-scaled.jpg': 'dining-room-render.jpg', 'LATINE-restautant-1024x684.png': 'dining-room-render.jpg',
 'Restaurant-6-1300x650.jpg': 'dining-room-render.jpg', 'Restaurant-10-1300x650.jpg': 'dining-room-render.jpg',
 'Restaurant-3-scaled.jpg': 'crudo-bar.jpg', 'House-Story-e1779786021844-1024x684.png': 'crudo-bar.jpg',
 'CANDELA_LATINE-e1779785134779.jpg': 'la-candela.jpg', 'bar-candela-latine.jpg': 'cocktail.jpg',
 'latine-linee.jpg': 'la-candela-stripes.jpg', 'PHOTO-2026-02-25-09-15-34.jpg': 'la-candela-stripes.jpg',
 'PDR1-scaled.jpg': 'el-cielo-table.jpg', 'PDR4-scaled.jpg': 'el-cielo-table.jpg', 'PDR5-scaled.jpg': 'el-cielo-table.jpg',
 'PDR2-scaled.jpg': 'el-cielo-chandelier.jpg', 'PDR6-scaled.jpg': 'el-cielo-chandelier.jpg',
 'Terrace-scaled.jpg': 'terrace.jpg', 'Terrace-2-scaled.jpg': 'terrace.jpg', 'Terrace3-1300x650.jpg': 'terrace.jpg', 'stairs-latine.jpg': 'crudo-bar.jpg',
 'ChatGPT-Image-Apr-15-2026-10_36_38-PM.png': 'prawns.jpg', 'ChatGPT-Image-Apr-15-2026-10_41_32-PM.png': 'oysters.jpg',
 'ChatGPT-Image-Apr-16-2026-09_33_05-AM.png': 'squid-ink.jpg', 'ChatGPT-Image-Apr-16-2026-09_35_51-AM.png': 'beef.jpg',
 'ChatGPT-Image-Apr-16-2026-09_44_31-AM.png': 'signature-main.jpg',
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

# ---------------------------------------------------------------- chrome
NAV_L = [('the-restaurant', 'The Restaurant'), ('our-menu', 'Menus'), ('private-dining-room', 'Private Dining'), ('christmas', 'Christmas')]
NAV_R = [('portfolio-gallery', 'Gallery'), ('about-us', 'About')]

def head(P, title, desc, path, og):
    return f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{REMOTE + og}">
<meta property="og:url" content="{SITE}{path}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Libre+Franklin:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{P}css/site.css">
'''

SCHEMA = '''<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Restaurant","name":"Latine Mayfair","url":"https://latinemayfair.com/","telephone":"+44 20 3887 3126","email":"contact@latinemayfair.com","servesCuisine":["French","Latin American"],"priceRange":"£££","image":"https://latinemayfair.com/wp-content/uploads/2026/03/LATINE_RESTAURANT1.jpg","address":{"@type":"PostalAddress","streetAddress":"10-11 Lancashire Court","addressLocality":"London","postalCode":"W1S 1EY","addressCountry":"GB"},"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"12:00","closes":"24:00"}],"acceptsReservations":"''' + BOOK + '''","menu":"https://latinemayfair.com/our-menu/","sameAs":["https://www.instagram.com/latinemayfair"]}
</script>
'''

def nav(P, active):
    def li(items):
        return ''.join(f'<li><a href="{P}{s}/"{" class=\"active\"" if s == active else ""}>{t}</a></li>' for s, t in items)
    over = ''.join(f'<a href="{P}{s}/">{t}</a>' for s, t in NAV_L + NAV_R)
    return f'''<div class="festive-bar"><span class="star">✦</span>Christmas at Latine <span class="hide-s">· Festive dining &amp; private parties</span> now booking <a href="{P}christmas/">Discover</a></div>
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
<div class="menu-overlay" id="overlay">
  <button class="close" id="close" aria-label="Close menu">×</button>
  <a href="{P or './'}">Home</a>{over}
  <a class="btn btn-gold" href="{BOOK}" target="_blank" rel="noopener">Book a table</a>
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
        <li><a href="{P}portfolio-gallery/">Gallery</a></li>
      </ul>
    </div>
    <div>
      <h4>Latine</h4>
      <ul>
        <li><a href="{P}about-us/">About us</a></li>
        <li><a href="{P}press/">Press</a></li>
        <li><a href="{P}careers/">Careers</a></li>
        <li><a href="{P}lucky-7/">Lucky 7</a></li>
        <li><a href="{P}lacav/">LACAV</a></li>
        <li><a href="https://www.instagram.com/latinemayfair" target="_blank" rel="noopener">Instagram</a></li>
      </ul>
    </div>
    <div>
      <h4>Hours</h4>
      <p style="font-size:14px;line-height:1.9">Monday – Saturday<br>12pm – midnight<br>Closed Sunday</p>
      <h4 style="margin-top:30px">Invitations &amp; news</h4>
      <p style="font-size:14px">New menus, events and LACAV, opening soon.</p>
      <form class="news"><input type="email" placeholder="Your email" required aria-label="Email"><button>Join</button></form>
    </div>
  </div>
  <div class="f-bot">
    <span>© 2026 Latine Mayfair Limited</span>
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

def page(path, title, desc, body_fn, active='', plain=False, og='2026/03/LATINE_RESTAURANT1.jpg', schema=False):
    depth = 0 if path == '' else path.strip('/').count('/') + 1
    P = '../' * depth
    out = head(P, title, desc, path, og) + (SCHEMA if schema else '') + '</head>\n'
    out += f'<body{" class=\"plain\"" if plain else ""}>\n' + nav(P, active) + body_fn(P) + footer(P)
    d = os.path.join(OUT, path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html') if path else os.path.join(OUT, 'index.html'), 'w').write(out)

def redirect(path, to):
    d = os.path.join(OUT, path); os.makedirs(d, exist_ok=True)
    depth = path.strip('/').count('/') + 1
    rel = '../' * depth + to
    open(os.path.join(d, 'index.html'), 'w').write(f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>Latine Mayfair</title><link rel="canonical" href="{SITE}{to}"><meta http-equiv="refresh" content="0; url={rel}"></head><body><a href="{rel}">Continue</a></body></html>')

# ---------------------------------------------------------------- components
def phero(P, img, eyebrow, h1, sub='', ctas='', cls=''):
    return f'''<header class="phero {cls}">
  <img src="{IMG(img, P)}" alt="">
  <div class="pin">
    <p class="eyebrow rv">{eyebrow}</p>
    <h1 class="rv d1">{h1}</h1>
    {f'<p class="sub rv d2">{sub}</p>' if sub else ''}
    {f'<div class="ctas rv d3">{ctas}</div>' if ctas else ''}
  </div>
</header>
'''

def btn_book(cls='btn-solid', label='Book a table'):
    return f'<a class="btn {cls}" href="{BOOK}" target="_blank" rel="noopener">{label}</a>'

def split(P, img, eyebrow, h2, paras, extra='', rev=False, wide=False, sid='', floor=''):
    ps = ''.join(f'<p class="rv d2">{p}</p>' for p in paras)
    return f'''<div class="split{' rev' if rev else ''}"{f' id="{sid}"' if sid else ''}>
  <div class="split-ph{' wide' if wide else ''} rv"><img src="{IMG(img, P)}" alt="" loading="lazy"></div>
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
    occs = ['Christmas party', 'Corporate dinner', 'Birthday', 'Celebration', 'Other']
    labels = {'Other': 'Something else'}
    chips = ''.join(f'<input type="radio" name="occasion" id="o{i}" value="{o}"{" checked" if o == occasion else ""}><label for="o{i}">{labels.get(o, o)}</label>' for i, o in enumerate(occs))
    return f'''<section class="enquire" id="enquire">
  <div class="enq-wrap">
    <div class="enq-head">
      <p class="eyebrow rv">{eyebrow}</p>
      <h2 class="rv d1">{title}</h2>
      <p class="rv d2">{intro}</p>
    </div>
    <!-- TODO before go-live: send to Latine's events inbox + log to Google Sheet -->
    <form class="enq rv d2" id="enqForm">
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

# ---------------------------------------------------------------- HOME
def home(P):
    b = open(os.path.join(HERE, 'home_body.html')).read()
    b = re.sub(r'https://latinemayfair\.com/wp-content/uploads/([^"\)]+\.(?:jpe?g|png|webp))', lambda m: IMG(m.group(1), P), b)
    b = b.replace('<section class="xmas on-dark" id="christmas">', '<section class="xmas on-dark sparkles" id="christmas">')
    b = b.replace('href="https://latinemayfair.com/lucky-7/"', f'href="{P}lucky-7/"')
    # link out to the new inner pages
    b = b.replace('<h3>Afternoon in the mews</h3>', f'<h3><a href="{P}the-restaurant/#terrace">Afternoon in the mews</a></h3>')
    b = b.replace('<h3>Dinner, by candlelight</h3>', f'<h3><a href="{P}the-restaurant/">Dinner, by candlelight</a></h3>')
    b = b.replace('<h3>Later, at La Candela</h3>', f'<h3><a href="{P}the-restaurant/#la-candela">Later, at La Candela</a></h3>')
    b = b.replace('</p>\n  </div>\n  <div class="acts-grid">', f'</p>\n  </div>\n  <div class="acts-grid">', 1)
    b = b.replace('</div>\n    </div>\n    <div class="mosaic', f'</div>\n      <a class="link rv d3" href="{P}our-menu/" style="display:inline-block;margin-top:34px;color:var(--terra)">All menus</a>\n    </div>\n    <div class="mosaic', 1)
    b = b.replace('<div class="xmas-foot rv">', f'<div class="xmas-foot rv">\n      <a class="btn btn-line" href="{P}christmas/">Christmas at Latine</a>', 1)
    b = b.replace('<div style="margin-top:36px" class="rv d3"><a class="btn btn-solid" href="#enquire">Make an enquiry</a></div>',
                  f'<div style="margin-top:36px;display:flex;gap:12px;flex-wrap:wrap" class="rv d3"><a class="btn btn-solid" href="#enquire">Make an enquiry</a><a class="btn btn-line" href="{P}private-dining-room/">Discover El Cielo</a></div>')
    b = b.replace('<p class="sig rv d3">Hospitality, at the heart of everything.</p>',
                  f'<p class="sig rv d3">Hospitality, at the heart of everything.</p>\n    <a class="link rv d3" href="{P}about-us/" style="margin-top:30px;align-self:flex-start;color:#fff">About Latine</a>')
    return b

# ---------------------------------------------------------------- THE RESTAURANT
def restaurant(P):
    return phero(P, '2026/09/Restaurant-1-scaled.jpg', 'The Restaurant · Mayfair', 'A house of<br><em>many moods</em>',
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
<section class="sec tint" id="terrace">
''' + split(P, '2026/09/Terrace-2-scaled.jpg', 'The terrace', 'A pause<br><em>in the mews</em>', [
        'Tucked into the cobbled courtyard of Lancashire Court, our terrace is a quiet corner moments from the bustle of Bond Street.',
        'It\'s the perfect stop after a day of shopping, whether for a glass of Champagne, a cocktail or a relaxed lunch.'],
        btn_book('btn-line', 'Reserve'), floor='Lancashire Court') + f'''
</section>
<section class="sec dark sparkles" id="la-candela" style="position:relative;overflow:hidden">
''' + split(P, '2026/03/CANDELA_LATINE-e1779785134779.jpg', 'La Candela', 'As the night<br><em>turns</em>', [
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
MENUS = [
 ('À la carte', 'Lunch &amp; dinner', 'Refined French technique and the vibrant flavours of Latin America. Seasonal ingredients, fresh seafood and carefully prepared dishes, designed to be enjoyed from lunch through to dinner.', '2026/09/Menu-Summer-Latine-Aug-2.pdf', '2026/04/ChatGPT-Image-Apr-16-2026-09_44_31-AM.png'),
 ('Set lunch', 'Two or three courses', 'A lighter, quicker option, perfect for a midday break in Mayfair. Choose two or three courses from a selection of seasonal dishes.', '2026/09/Lunch-Menu_LATINE09.pdf', '2026/04/ChatGPT-Image-Apr-15-2026-10_36_38-PM.png'),
 ('Desserts', 'French pastry, Latin accent', 'Refined sweet creations bringing together French pastry technique with subtle Latin American influences: elegant, balanced and indulgent.', '2026/09/Dessert-menu-Final-16-06-26-1.pdf-4.pdf', 'photos/dessert-caramel.jpg'),
 ('Wine', 'The list', 'A carefully curated selection from renowned vineyards and emerging producers around the world, balancing classic regions with distinctive discoveries.', '2026/06/Wine-List.pdf', 'photos/wine.jpg'),
]
def menus(P):
    cards = ''.join(f'''<article class="mcard rv{' d1' if i % 2 else ''}">
      <div class="ph"><img src="{IMG(img, P)}" alt="{t}" loading="lazy"></div>
      <div class="tx"><p class="eyebrow">{sub}</p><h3>{t}</h3><p>{d}</p><a class="link" href="{REMOTE + pdf}" target="_blank" rel="noopener">View menu (PDF)</a></div>
    </article>''' for i, (t, sub, d, pdf, img) in enumerate(MENUS))
    cards += f'''<article class="mcard rv">
      <div class="ph"><img src="{IMG('2026/04/bar-candela-latine.jpg', P)}" alt="Cocktails" loading="lazy"></div>
      <div class="tx"><p class="eyebrow">Signatures &amp; classics</p><h3>Cocktails</h3><p>Refined classics and signature creations inspired by the vibrant spirit of Latin America, made with premium ingredients to match the energy of the room.</p><span class="soon">Menu coming soon</span></div>
    </article>
    <article class="mcard rv d1">
      <div class="ph"><img src="{IMG('2026/09/PDR5-scaled.jpg', P)}" alt="El Cielo" loading="lazy"></div>
      <div class="tx"><p class="eyebrow">El Cielo &amp; events</p><h3>Private dining</h3><p>Private dining menus can be tailored to your group and occasion, from seated dinners to canapé receptions.</p><a class="link" href="{P}private-dining-room/#enquire">Enquire</a></div>
    </article>'''
    return phero(P, 'photos/beef-wide.jpg', 'Menus', 'Precision,<br>with <em>passion</em>',
        'Rooted in French technique, inspired by Latin America. Seasonal produce, fresh seafood and dishes that move easily from lunch to dinner.', btn_book()) + f'''
<section class="sec tint">
  <div class="menu-list">{cards}</div>
  <p class="note rv">Menus change with the seasons; dishes may vary. Please tell our team about any allergies or dietary requirements before ordering.</p>
</section>
<section class="sec">
  <div class="sec-head"><p class="eyebrow rv">From the kitchen</p><h2 class="rv d1">A taste of <em>Latine</em></h2></div>
  <div class="strip rv">
    <div><img src="{IMG('2026/04/ChatGPT-Image-Apr-15-2026-10_41_32-PM.png', P)}" alt="Oysters" loading="lazy"></div>
    <div><img src="{IMG('2026/04/ChatGPT-Image-Apr-16-2026-09_33_05-AM.png', P)}" alt="Squid ink dish" loading="lazy"></div>
    <div><img src="{IMG('2026/04/ChatGPT-Image-Apr-16-2026-09_35_51-AM.png', P)}" alt="Beef with jus" loading="lazy"></div>
    <div><img src="{IMG('2026/09/DSC_6256-copy-2-scaled.jpg', P)}" alt="Tarte tatin on a Latine plate" loading="lazy"></div>
  </div>
  <div style="text-align:center;margin-top:60px" class="rv">{btn_book()}</div>
</section>
'''

# ---------------------------------------------------------------- PRIVATE DINING
def private(P):
    return phero(P, '2026/09/PDR6-scaled.jpg', 'Private dining &amp; events', 'El Cielo,<br><em>above it all</em>',
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
    return phero(P, '2026/09/PDR1-scaled.jpg', 'Christmas &amp; New Year 2026', 'Christmas in Mayfair,<br><em>by candlelight</em>',
        'Long festive lunches, candlelit parties in El Cielo and late nights at La Candela. December at Latine is made for celebrating.',
        '<a class="btn btn-gold" href="#enquire" data-occasion="Christmas party">Plan a Christmas party</a>' + btn_book('btn-line', 'Book a festive table'), cls='dark') + f'''
<section class="sec dark sparkles" style="position:relative;overflow:hidden">
  <div class="sec-head"><p class="eyebrow rv">Ways to celebrate</p><h2 class="rv d1">However you <em>gather</em></h2><p class="rv d2">From a table for two after Bond Street to taking over a whole floor with your team, there's a Latine Christmas for every occasion.</p></div>
  <div class="xmas-cards" style="margin-top:0">
    <article class="xcard rv"><div class="ph"><img src="{IMG('2026/09/Restaurant-8-scaled.jpg', P)}" alt="" loading="lazy"></div><p class="eyebrow">In the restaurant</p><h3>Festive lunch &amp; dinner</h3><p>Gather friends, family or colleagues in the dining room for the season's long lunches and candlelit dinners, with French technique, Latin warmth and Champagne on the table.</p><a class="go link" href="{BOOK}" target="_blank" rel="noopener">Book a table</a></article>
    <article class="xcard rv d1"><div class="ph"><img src="{IMG('2026/09/PDR4-scaled.jpg', P)}" alt="" loading="lazy"></div><p class="eyebrow">El Cielo · Second floor</p><h3>Private Christmas parties</h3><p>Take over our private room with festive menus tailored to your group, and a team looking after every detail from the welcome drink to the last toast.</p><div class="facts"><div><b>20</b><span>Seated</span></div><div><b>40+</b><span>Standing</span></div></div><a class="go link" href="#enquire" data-occasion="Christmas party">Plan your party</a></article>
    <article class="xcard rv d2"><div class="ph"><img src="{IMG('2026/04/bar-candela-latine.jpg', P)}" alt="" loading="lazy"></div><p class="eyebrow">La Candela · First floor</p><h3>The after-party</h3><p>When dinner's done, the night carries on upstairs with DJs, cocktails and Champagne. There's no need to leave the building to keep celebrating.</p><a class="go link" href="#enquire" data-occasion="Christmas party">Enquire for groups</a></article>
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
''' + split(P, '2026/09/PDR2-scaled.jpg', 'Festive menus', 'Menus made<br>for <em>the season</em>', [
        'Our festive menus bring the Latine kitchen to the Christmas table: French technique, Latin American flavour and plenty of Champagne.',
        'Menus for groups and private parties are available on request and can be tailored to your numbers, budget and dietary needs. Send an enquiry and we\'ll share the options for your date.'],
        '<a class="btn btn-solid" href="#enquire" data-occasion="Christmas party">Request festive menus</a>') + '''
</section>
''' + enquiry(P, 'Christmas party', 'Christmas enquiries', 'Let\'s plan your<br><em>Christmas</em>',
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

# ---------------------------------------------------------------- GALLERY
GALLERY = [
 ('2026/03/LATINE_RESTAURANT1.jpg','restaurant','The dining room'),
 ('2026/04/ChatGPT-Image-Apr-15-2026-10_41_32-PM.png','food','Oysters'),
 ('2026/09/PDR1-scaled.jpg','cielo','El Cielo, set for dinner'),
 ('2026/09/Terrace-scaled.jpg','terrace','The terrace in Lancashire Court'),
 ('2026/04/ChatGPT-Image-Apr-15-2026-10_36_38-PM.png','food','Prawns, plantain'),
 ('2026/09/Restaurant-3-scaled.jpg','restaurant','The crudo bar'),
 ('2026/03/CANDELA_LATINE-e1779785134779.jpg','candela','La Candela'),
 ('2026/04/ChatGPT-Image-Apr-16-2026-09_35_51-AM.png','food','Beef, red wine jus'),
 ('2026/09/PDR2-scaled.jpg','cielo','The chandelier in El Cielo'),
 ('2026/09/Restaurant-1-scaled.jpg','restaurant','The dining room'),
 ('2026/04/ChatGPT-Image-Apr-16-2026-09_33_05-AM.png','food','Squid, squid ink'),
 ('2026/04/latine-linee.jpg','candela','The striped room'),
 ('2026/04/ChatGPT-Image-Apr-16-2026-09_44_31-AM.png','food','Signature main'),
 ('2026/09/DSC_6256-copy-2-scaled.jpg','food','Tarte tatin'),
 ('2026/04/bar-candela-latine.jpg','candela','A cocktail at La Candela'),
 ('photos/dessert-caramel.jpg','food','Dessert'),
 ('photos/wine.jpg','candela','Wine'),
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
    return phero(P, '2026/05/LATINE-restautant-1024x684.png', 'About us', 'The meeting of<br><em>two worlds</em>',
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
    return phero(P, '2026/05/LATINE-carr-1024x684.png', 'Careers', 'Great restaurants,<br><em>great teams</em>',
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
    <form class="news rv d3"><input type="email" placeholder="Your email" required aria-label="Email"><button>Notify me</button></form>
  </div>
</section>
'''

# ---------------------------------------------------------------- LUCKY 7
def lucky(P):
    terms = [
     ('Eligibility', 'Lucky 7 is available to guests who make an eligible dining reservation directly through the official Latine Mayfair website.'),
     ('Selection', 'Every 7th eligible online booking is selected for the Lucky 7 complimentary dining experience, based on the chronological order in which qualifying reservations are received.'),
     ('Availability', 'Lucky 7 applies to eligible lunch and dinner reservations throughout the restaurant\'s published opening hours.'),
     ('Maximum complimentary value', 'The maximum complimentary amount is £1,000 per winning reservation and table, not per person. Any amount exceeding £1,000 must be paid by the guest.'),
     ('One winning reservation', 'Each winning reservation qualifies for one complimentary dining bill only, regardless of the number of guests at the table.'),
     ('Valid reservations', 'The winning reservation must be honoured and the guests must dine at Latine Mayfair to receive the benefit. Cancelled bookings and no-shows are not eligible for complimentary dining.'),
     ('Reveal', 'Winning guests will be informed at the end of their dining experience, when requesting their bill, and presented with the Lucky 7 Golden Card.'),
     ('No cash alternative', 'The complimentary dining benefit cannot be exchanged for cash, credit or a future reservation. Any unused portion of the £1,000 maximum cannot be refunded or carried forward.'),
     ('Non-transferable', 'The benefit applies exclusively to the selected reservation and cannot be transferred to another table or booking.'),
     ('Promotion management', 'Latine Mayfair reserves the right to amend, suspend or withdraw the experience where reasonably necessary, subject to applicable law and without unfairly affecting benefits already earned.'),
     ('Applicable law', 'These terms are governed by the laws of England and Wales and applicable UK consumer protection legislation.')]
    t = ''.join(f'<p><b>{a}.</b> {b}</p>' for a, b in terms)
    return f'''<section class="sec dark sparkles" style="padding-top:calc(38px + 160px);position:relative;overflow:hidden">
  <div class="split">
    <div class="rv"><div class="golden"><div class="t"><span>Latine Mayfair</span><span>Lucky 7</span></div><div class="n">7</div><div class="b">Your dining experience is on us</div></div></div>
    <div class="copy">
      <p class="eyebrow rv">Book direct · Lucky 7</p>
      <h1 class="rv d1" style="font-size:clamp(46px,6vw,92px)">Your next dinner<br>could be <em style="color:var(--gold-l)">on us</em></h1>
      <p class="rv d2">Every 7th online booking made through our website receives their entire bill complimentary. No competitions, no entries. Simply reserve online, enjoy the very best of Latine and leave the rest to luck.</p>
      <p class="rv d2">You won't know until the very end: instead of the bill, you'll be presented with the Lucky 7 Golden Card.</p>
      <div class="rv d3" style="margin-top:34px">{btn_book('btn-gold', 'Reserve your table')}</div>
    </div>
  </div>
</section>
<section class="sec">
  <div class="sec-head"><p class="eyebrow rv">How it works</p><h2 class="rv d1">Five simple <em>steps</em></h2></div>
  <div class="steps five">
    <div class="step rv"><h3>Reserve</h3><p>Book lunch or dinner directly through the official Latine website.</p></div>
    <div class="step rv d1"><h3>Enjoy</h3><p>French elegance meets the vibrant soul of Latin America.</p></div>
    <div class="step rv d2"><h3>Every 7th wins</h3><p>Every 7th eligible online reservation is selected. No need to enter.</p></div>
    <div class="step rv d3"><h3>The reveal</h3><p>When you ask for the bill, our team reveals whether you've been selected.</p></div>
    <div class="step rv d3"><h3>On us</h3><p>Your dining bill is complimentary, subject to the terms below.</p></div>
  </div>
</section>
<section class="sec dark">
  <div class="sec-head"><p class="eyebrow rv">Terms &amp; conditions</p><h2 class="rv d1" style="font-size:clamp(34px,3.6vw,52px)">The <em>small print</em></h2></div>
  <div class="terms rv">{t}</div>
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

# ---------------------------------------------------------------- BUILD
if __name__ == '__main__':
    # clean only what this script generates (OUT is the repo root)
    GEN = ['index.html', '404.html', 'sitemap.xml', 'robots.txt', 'images.txt', 'CNAME', 'css', 'js', 'images',
           'the-restaurant', 'our-menu', 'private-dining-room', 'christmas', 'portfolio-gallery', 'about-us', 'careers',
           'press', 'lacav', 'lucky-7', 'reservation-policy', 'legal', 'journal', 'team', 'main-home', '404tmp']
    for g in GEN:
        t = os.path.join(OUT, g)
        if os.path.isdir(t): shutil.rmtree(t)
        elif os.path.exists(t): os.remove(t)
    os.makedirs(os.path.join(OUT, 'css')); os.makedirs(os.path.join(OUT, 'js'))
    open(os.path.join(OUT, 'css/site.css'), 'w').write(open(os.path.join(HERE, 'base.css')).read() + open(os.path.join(HERE, 'pages.css')).read())
    shutil.copy(os.path.join(HERE, 'site.js'), os.path.join(OUT, 'js/site.js'))
    if LOCAL:
        if not os.path.isdir(os.path.join(HERE, 'images')): sys.exit('Run ./fetch_images.sh first')
        os.makedirs(os.path.join(OUT, 'images'))
        for f in os.listdir(os.path.join(HERE, 'images')):
            if f not in PHOTOS: shutil.copy(os.path.join(HERE, 'images', f), os.path.join(OUT, 'images', f))
        for f in os.listdir(os.path.join(HERE, 'photos')):
            shutil.copy(os.path.join(HERE, 'photos', f), os.path.join(OUT, 'images', f))

    page('', 'Latine Mayfair | French–Latin Restaurant, Private Dining & Christmas in Mayfair',
         'Latine is a French–Latin American restaurant in the cobbled mews of Lancashire Court, Mayfair, moments from Bond Street. Lunch, dinner, La Candela lounge, El Cielo private dining and Christmas parties.', home, schema=True)
    page('the-restaurant/', 'The Restaurant | Latine Mayfair', 'Terrace, crudo bar, dining room and La Candela lounge: discover the spaces at Latine, a French–Latin restaurant in Lancashire Court, Mayfair.', restaurant, 'the-restaurant', og='2026/09/Restaurant-1-scaled.jpg')
    page('our-menu/', 'Menus | Latine Mayfair', 'À la carte, set lunch, desserts and wine at Latine Mayfair: French technique meets the flavours of Latin America.', menus, 'our-menu', og='2026/04/ChatGPT-Image-Apr-16-2026-09_35_51-AM.png')
    page('private-dining-room/', 'Private Dining Room Mayfair | El Cielo at Latine', 'El Cielo, Latine\'s private dining room in Mayfair, seats up to 20 and holds 40+ for receptions. Tailored menus for celebrations, business dinners and Christmas parties.', private, 'private-dining-room', og='2026/09/PDR6-scaled.jpg')
    page('christmas/', 'Christmas Parties & Festive Dining in Mayfair | Latine', 'Christmas at Latine Mayfair: festive lunches and dinners, private Christmas parties in El Cielo for up to 20 seated or 40+ standing, and late nights at La Candela.', christmas, 'christmas', og='2026/09/PDR1-scaled.jpg')
    page('portfolio-gallery/', 'Gallery | Latine Mayfair', 'Inside Latine Mayfair: the dining room, crudo bar, La Candela, El Cielo private dining room, terrace and food.', gallery, 'portfolio-gallery', plain=True)
    page('about-us/', 'About Us | Latine Mayfair', 'The story of Latine: French culinary tradition meets the vibrant soul of Latin America in a historic Mayfair mews.', about, 'about-us', og='2026/05/LATINE-restautant-1024x684.png')
    page('careers/', 'Careers | Latine Mayfair', 'Join the kitchen, bar or front of house team at Latine, a French–Latin restaurant in Mayfair.', careers, og='2026/05/LATINE-carr-1024x684.png')
    page('press/', 'Press | Latine Mayfair', 'Latine Mayfair in the press: Wallpaper*, Forbes, The London Standard, SheerLuxe, Quintessentially and more.', press, plain=True)
    page('lacav/', 'LACAV | Coming Soon to Latine Mayfair', 'LACAV is coming soon to Latine Mayfair. Join the list to hear first.', lacav)
    page('lucky-7/', 'Lucky 7 | Book Direct at Latine Mayfair', 'Every 7th online booking at Latine Mayfair, the bill is on us. How Lucky 7 works and terms and conditions.', lucky)
    page('reservation-policy/', 'Reservation Policy | Latine Mayfair', 'Reservation, cancellation and dress code policy at Latine Mayfair.', policy, plain=True)
    page('legal/', 'Privacy Policy | Latine Mayfair', 'Privacy policy for Latine Mayfair Limited.', legal, plain=True)
    # 404 (absolute paths, GitHub Pages serves it from any depth)
    page('404tmp/', 'Page not found | Latine Mayfair', 'Page not found.', notfound)
    t = open(os.path.join(OUT, '404tmp/index.html')).read().replace('href="../', 'href="/').replace('src="../', 'src="/')
    open(os.path.join(OUT, '404.html'), 'w').write(t); shutil.rmtree(os.path.join(OUT, '404tmp'))
    # old URLs
    redirect('journal/', 'press/'); redirect('team/', 'about-us/'); redirect('main-home/', '')
    # At go-live: run with --domain to add the CNAME, then point latinemayfair.com DNS at GitHub Pages
    if '--domain' in sys.argv: open(os.path.join(OUT, 'CNAME'), 'w').write('latinemayfair.com\n')
    urls = ['', 'the-restaurant/', 'our-menu/', 'private-dining-room/', 'christmas/', 'portfolio-gallery/', 'about-us/', 'careers/', 'press/', 'lacav/', 'lucky-7/', 'reservation-policy/', 'legal/']
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{SITE}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n')
    # image list for fetch_images.sh
    open(os.path.join(OUT, 'images.txt'), 'w').write('\n'.join(REMOTE + p for p in sorted(USED)) + '\n')
    print('built', len(urls), 'pages;', len(USED), 'images; local=' + str(LOCAL))
