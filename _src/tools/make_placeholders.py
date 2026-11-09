#!/usr/bin/env python3
"""Generates on-brand placeholder photos in src/images/ (same filenames as the real photos).
   ./fetch_images.sh overwrites them with the real photography."""
import os, glob, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'images'); os.makedirs(OUT, exist_ok=True)
F = os.path.join(HERE, 'fonts')
serif_i = os.path.join(F, 'cormorant-garamond-latin-400-italic.woff')
sans = os.path.join(F, 'libre-franklin-latin-400-normal.woff')

PAL = {  # base, glow, text, accent
 'restaurant': ((96, 44, 26), (205, 128, 84), (250, 238, 222), (217, 196, 154)),
 'cielo':      ((24, 36, 31), (150, 116, 66), (243, 238, 227), (217, 196, 154)),
 'candela':    ((38, 24, 22), (170, 92, 58), (243, 228, 214), (217, 196, 154)),
 'terrace':    ((120, 128, 108), (236, 230, 212), (31, 27, 23), (140, 69, 41)),
 'food':       ((222, 214, 196), (248, 244, 236), (60, 50, 42), (169, 87, 58)),
 'people':     ((70, 52, 40), (210, 150, 110), (250, 238, 222), (217, 196, 154)),
}
IMAGES = {  # filename: (w, h, palette, label)
 'LATINE_RESTAURANT1.jpg': (1600, 1067, 'restaurant', 'The dining room'),
 'Restaurant-1-scaled.jpg': (1600, 1067, 'restaurant', 'The dining room, evening'),
 'Restaurant-2-scaled.jpg': (1600, 1067, 'restaurant', 'The dining room'),
 'Restaurant-3-scaled.jpg': (1600, 1067, 'restaurant', 'The crudo bar'),
 'Restaurant-5-1300x650.jpg': (1300, 650, 'restaurant', 'The dining room'),
 'Restaurant-6-1300x650.jpg': (1300, 650, 'restaurant', 'The dining room'),
 'Restaurant-10-1300x650.jpg': (1300, 650, 'restaurant', 'The room'),
 'Restaurant-8-scaled.jpg': (1024, 1280, 'restaurant', 'Table detail'),
 'stairs-latine.jpg': (1024, 1365, 'restaurant', 'The staircase'),
 'PHOTO-2026-02-25-09-15-34.jpg': (1200, 1200, 'restaurant', 'Interior'),
 'PDR1-scaled.jpg': (1600, 1067, 'cielo', 'El Cielo by candlelight'),
 'PDR2-scaled.jpg': (1024, 1535, 'cielo', 'Candelabra, El Cielo'),
 'PDR4-scaled.jpg': (1600, 1067, 'cielo', 'El Cielo set for dinner'),
 'PDR5-scaled.jpg': (1024, 1535, 'cielo', 'El Cielo'),
 'PDR6-scaled.jpg': (1600, 1067, 'cielo', 'The painted walls of El Cielo'),
 'CANDELA_LATINE-e1779785134779.jpg': (1600, 1067, 'candela', 'La Candela'),
 'bar-candela-latine.jpg': (1200, 1200, 'candela', 'The bar'),
 'latine-linee.jpg': (1024, 1280, 'candela', 'Striped banquettes'),
 'Terrace-scaled.jpg': (1024, 1280, 'terrace', 'The terrace'),
 'Terrace-2-scaled.jpg': (1024, 1535, 'terrace', 'Lancashire Court'),
 'Terrace3-1300x650.jpg': (1300, 650, 'terrace', 'The terrace'),
 'ChatGPT-Image-Apr-15-2026-10_36_38-PM.png': (1024, 1365, 'food', 'Seafood pasta'),
 'ChatGPT-Image-Apr-15-2026-10_41_32-PM.png': (1024, 1024, 'food', 'Oysters'),
 'ChatGPT-Image-Apr-16-2026-09_33_05-AM.png': (1024, 1024, 'food', 'Squid ink'),
 'ChatGPT-Image-Apr-16-2026-09_35_51-AM.png': (1024, 1024, 'food', 'Beef, jus'),
 'ChatGPT-Image-Apr-16-2026-09_44_31-AM.png': (1024, 1279, 'food', 'Signature main'),
 'DSC_6256-copy-2-scaled.jpg': (1024, 1365, 'food', 'Dessert'),
 'House-Story-e1779786021844-1024x684.png': (1024, 684, 'food', 'The Latine plate'),
 'LATINE-sala-1024x684.png': (1024, 684, 'people', 'Lunch at Latine'),
 'LATINE-restautant-1024x684.png': (1024, 684, 'people', 'Latine at night'),
 'LATINE-carr-1024x684.png': (1024, 684, 'people', 'The team'),
}

def make(name, w, h, pal, label):
    base, glow, txt, acc = PAL[pal]
    rnd = random.Random(name)
    im = Image.new('RGB', (w, h), base)
    # soft lamp glows
    g = Image.new('RGB', (w, h), base); d = ImageDraw.Draw(g)
    for _ in range(3):
        cx, cy = rnd.uniform(.2, .8) * w, rnd.uniform(.15, .6) * h
        r = rnd.uniform(.35, .6) * max(w, h)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=glow)
    g = g.filter(ImageFilter.GaussianBlur(max(w, h) * .18))
    im = Image.blend(im, g, .75)
    if pal == 'food':  # a plate
        d = ImageDraw.Draw(im); r = min(w, h) * .3; cx, cy = w / 2, h / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 248, 243), outline=(225, 218, 205), width=3)
        d.ellipse((cx - r * .62, cy - r * .62, cx + r * .62, cy + r * .62), outline=(232, 226, 214), width=2)
    # vignette
    v = Image.new('L', (w, h), 0); dv = ImageDraw.Draw(v)
    dv.ellipse((-w * .25, -h * .25, w * 1.25, h * 1.25), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(max(w, h) * .12))
    im = Image.composite(im, Image.new('RGB', (w, h), tuple(int(c * .45) for c in base)), v)
    # grain
    n = Image.effect_noise((w, h), 18).convert('RGB')
    im = Image.blend(im, n, .04)
    ext = os.path.splitext(name)[1].lower()
    im.save(os.path.join(OUT, name), 'PNG' if ext == '.png' else 'JPEG', **({} if ext == '.png' else {'quality': 82, 'optimize': True}))

if __name__ == '__main__':
    for n, (w, h, p, l) in IMAGES.items():
        make(n, w, h, p, l)
    print('made', len(IMAGES), 'placeholders in', os.path.normpath(OUT))
