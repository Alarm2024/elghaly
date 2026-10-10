#!/usr/bin/env python3
"""Turn one source image into the sizes and formats the site serves.

    python3 tools/art/build_art.py NAME SOURCE.png      # one image
    python3 tools/art/build_art.py --list               # what NAME can be

NAME is one of the slots in SLOTS below (the prompt for each is in
tools/art/PROMPTS.md). The source is cropped to the slot's shape from the
centre, scaled to each width, and written to assets/art/ as AVIF and WebP.
The og-* slots are link-preview cards: the source becomes the background and
the wordmark and title are drawn on it, written as one 1200x630 JPEG (the
format every link preview reads).

Needs Pillow 11.2+ (AVIF built in). Nothing is downloaded.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets", "art")
FONT = os.path.join(ROOT, "fonts", "outfit-latin-500-normal.woff2")
FONT_LIGHT = os.path.join(ROOT, "fonts", "outfit-latin-400-normal.woff2")
FONT_BOLD = os.path.join(ROOT, "fonts", "outfit-latin-700-normal.woff2")

CARD = (13, 11, 31)  # #0d0b1f
SHIFT = 280  # px the og-* picture moves right
GOLD = (245, 197, 66)  # #f5c542
LAVENDER = (185, 179, 230)  # #b9b3e6

# name: (aspect w, aspect h, widths). Widths are what the pages' srcset lists.
SLOTS = {
    "hero-wide": (16, 9, [1280, 1920]),
    "hero-tall": (3, 4, [600, 900]),
    "svc-servers": (16, 10, [400, 800]),
    "svc-bots": (16, 10, [400, 800]),
    "svc-tools": (16, 10, [400, 800]),
    "plumb": (16, 10, [400, 800, 1200]),
    "quay": (16, 10, [400, 800, 1200]),
}

# Link-preview cards: title on two lines at most, no claims.
OG = {
    "og-home": ("Linux servers, Telegram bots", "and tools for Solana", "elghaly.dev"),
    "og-plumb": ("Plumb", "Solana bot software on your own server", "elghaly.dev/plumb"),
    "og-quay": ("QUAY", "A second pair of eyes on your Solana bot", "elghaly.dev/quay"),
}


def crop_to(im, aw, ah):
    w, h = im.size
    if w * ah > h * aw:
        nw = h * aw // ah
        x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = w * ah // aw
    y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


def build_slot(name, src):
    aw, ah, widths = SLOTS[name]
    im = crop_to(Image.open(src).convert("RGB"), aw, ah)
    for w in widths:
        h = w * ah // aw
        out = im.resize((w, h), Image.LANCZOS)
        base = os.path.join(OUT, "%s-%d" % (name, w))
        out.save(base + ".avif", quality=52, speed=4)
        out.save(base + ".webp", quality=74, method=6)
        print("wrote %s.avif / .webp (%dx%d)" % (os.path.relpath(base, ROOT), w, h))


def build_og(name, src):
    big, small, url = OG[name]
    art = crop_to(Image.open(src).convert("RGB"), 1200, 630).resize((1200, 630), Image.LANCZOS)
    # The words take the left; slide the picture right so its subject sits
    # in the right third instead of under the title.
    im = Image.new("RGB", (1200, 630), CARD)
    im.paste(art.crop((0, 0, 1200 - SHIFT, 630)), (SHIFT, 0))
    im.paste(art.crop((0, 0, SHIFT, 630)).transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    # Darken the left half so the words stay readable on any picture.
    shade = Image.new("L", (1200, 630), 0)
    d = ImageDraw.Draw(shade)
    for x in range(1200):
        d.line([(x, 0), (x, 630)], fill=int(225 * min(1.0, max(0.0, 1.25 - x / 640))))
    im = Image.composite(Image.new("RGB", im.size, CARD), im, shade)
    d = ImageDraw.Draw(im)
    d.text((80, 92), "elghaly", font=ImageFont.truetype(FONT, 46), fill=GOLD)
    f1 = ImageFont.truetype(FONT_BOLD, 72 if len(big) < 12 else 58)
    d.text((80, 250), big, font=f1, fill=(255, 255, 255))
    f2 = ImageFont.truetype(FONT_LIGHT, 40 if len(small) < 34 else 34)
    d.text((80, 250 + f1.size + 22), small, font=f2, fill=LAVENDER)
    d.text((80, 530), url, font=ImageFont.truetype(FONT_LIGHT, 30), fill=LAVENDER)
    d.rounded_rectangle((80, 200, 176, 206), radius=3, fill=GOLD)
    out = os.path.join(OUT, name + "-1200x630.jpg")
    im.save(out, quality=84, optimize=True, progressive=True)
    print("wrote %s (1200x630)" % os.path.relpath(out, ROOT))


def main(argv):
    if len(argv) == 2 and argv[1] == "--list":
        for k, (aw, ah, ws) in SLOTS.items():
            print("%-12s %d:%d  widths %s" % (k, aw, ah, ws))
        for k in OG:
            print("%-12s link preview, 1200x630 JPEG" % k)
        return 0
    if len(argv) != 3 or (argv[1] not in SLOTS and argv[1] not in OG):
        print(__doc__)
        return 2
    os.makedirs(OUT, exist_ok=True)
    if argv[1] in OG:
        build_og(argv[1], argv[2])
    else:
        build_slot(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
