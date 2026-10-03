#!/usr/bin/env python3
"""sitekit: one file that brings an elghaly.dev site up to the shared baseline.

    python3 sitekit.py check  DIR...   report what is missing, change nothing
    python3 sitekit.py fix    DIR...   width/height on every local <img>, favicons,
                                       robots.txt, sitemap.xml, missing <head> tags
    python3 sitekit.py shrink DIR... [--max-width 1600] [--quality 82]
                                       re-encode oversized JPEG/PNG/WebP in place

DIR is the folder a site is published from: the one holding CNAME and
index.html. Every write is additive. An <img> that already has both width and
height is left alone, an existing favicon, robots.txt or sitemap.xml is never
replaced, and a <head> tag a page already has is never touched.

Standard library only. Pillow, if installed, adds favicon.ico +
apple-touch-icon.png and is required for `shrink`.

Width/height reserve the image's box before it loads, which is what stops the
page jumping (CLS). They set the aspect ratio, not the size, as long as the
CSS sizes the image (width:100% / max-width:100% with height:auto). Check the
page renders the same after `fix`; an image whose CSS sets one side but not
the other may need `height:auto` or `width:auto` beside it.
"""

import argparse
import datetime
import html
import os
import re
import struct
import subprocess
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
PARTIAL = os.path.join(HERE, "head.html")

# Per-site values for the partial and the generated favicon. `description` is
# used only when a root page has none; a page's own text always wins.
SITES = {
    "35.elghaly.dev": dict(name="35", mono="35", fg="#2ee6c7", bg="#0b1214"),
    "iris-35.elghaly.dev": dict(name="Iris", mono="I", fg="#2ee6c7", bg="#0b1214"),
    "plumb-35.elghaly.dev": dict(name="Plumb", mono="P", fg="#e8e6e1", bg="#050505"),
    "glance.elghaly.dev": dict(name="glance", mono="g", fg="#2ee6c7", bg="#0b1214"),
    "stale.elghaly.dev": dict(name="stale", mono="s", fg="#2ee6c7", bg="#0b1214"),
    "quay-35.elghaly.dev": dict(
        name="QUAY", mono="Q", fg="#2ee6c7", bg="#0b1214",
        description=(
            "Desk reports for Solana bots: a weekly landed-vs-failed paper, proof "
            "cards, a read-only mint score and RPC watch pings. Refunds with no "
            "form and no time limit."
        ),
    ),
}

SKIP_DIRS = {".git", ".github", "node_modules", "vendor", "_site", "target", "dist", "build"}
RASTER = (".png", ".jpg", ".jpeg", ".gif", ".webp")


# --------------------------------------------------------------------------- pages


def site_host(root):
    try:
        with open(os.path.join(root, "CNAME"), encoding="utf-8") as f:
            return f.read().strip().splitlines()[0].strip()
    except (OSError, IndexError):
        return None


def pages(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if name.endswith(".html"):
                out.append(os.path.join(dirpath, name))
    return out


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def page_url(root, host, page):
    rel = os.path.relpath(page, root).replace(os.sep, "/")
    if rel == "index.html":
        rel = ""
    elif rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    return f"https://{host}/{rel}"


def is_redirect(text):
    head = text.split("</head>", 1)[0].lower()
    return bool(re.search(r'<meta[^>]+http-equiv=["\']refresh["\']', head))


def is_listable(root, page, text):
    """A page belongs in the sitemap unless it is the 404, noindex, a redirect,
    or a page an explicit pages.yml copy list never publishes."""
    rel = os.path.relpath(page, root).replace(os.sep, "/")
    if rel == "404.html" or is_redirect(text):
        return False
    head = text.split("</head>", 1)[0].lower()
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', head):
        return False
    published = workflow_copies(root)
    if published is not None and rel.split("/", 1)[0] not in published:
        return False
    return True


# --------------------------------------------------------------------------- image sizes


def _exif_rotates(data):
    """True when a JPEG's EXIF orientation turns it a quarter (5-8): the browser
    then lays it out with width and height swapped."""
    i = data.find(b"Exif\x00\x00")
    if i < 0:
        return False
    tiff = data[i + 6:]
    if len(tiff) < 8:
        return False
    end = "<" if tiff[:2] == b"II" else ">"
    try:
        (ifd,) = struct.unpack(end + "I", tiff[4:8])
        (count,) = struct.unpack(end + "H", tiff[ifd:ifd + 2])
        for n in range(count):
            entry = tiff[ifd + 2 + 12 * n: ifd + 14 + 12 * n]
            tag, _typ, _cnt = struct.unpack(end + "HHI", entry[:8])
            if tag == 0x0112:
                (value,) = struct.unpack(end + "H", entry[8:10])
                return value in (5, 6, 7, 8)
    except struct.error:
        return False
    return False


def image_size(path):
    """(width, height) as the browser lays the image out, or None."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", data[6:10])
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", data[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            b = data[21:25]
            w = 1 + (((b[1] & 0x3F) << 8) | b[0])
            h = 1 + (((b[3] & 0x0F) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
            return w, h
        if kind == b"VP8X":
            w = 1 + int.from_bytes(data[24:27], "little")
            h = 1 + int.from_bytes(data[27:30], "little")
            return w, h
        return None
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            (length,) = struct.unpack(">H", data[i + 2:i + 4])
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return (h, w) if _exif_rotates(data) else (w, h)
            i += 2 + length
        return None
    if path.lower().endswith(".svg"):
        text = data[:4096].decode("utf-8", "replace")
        tag = re.search(r"<svg\b[^>]*>", text, re.S)
        if not tag:
            return None
        attrs = dict(re.findall(r'([\w:-]+)\s*=\s*["\']([^"\']*)["\']', tag.group(0)))

        def px(v):
            m = re.fullmatch(r"\s*([\d.]+)\s*(px)?\s*", v or "")
            return float(m.group(1)) if m else None

        w, h = px(attrs.get("width")), px(attrs.get("height"))
        if w and h:
            return round(w), round(h)
        vb = re.split(r"[\s,]+", attrs.get("viewBox", "").strip())
        if len(vb) == 4:
            try:
                return round(float(vb[2])), round(float(vb[3]))
            except ValueError:
                return None
    return None


IMG = re.compile(r"<img\b[^>]*>", re.I | re.S)
ATTR = re.compile(r'([^\s=/>]+)(?:\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+))?')


def attrs_of(tag):
    body = re.sub(r"^<\s*[\w-]+", "", tag).rstrip(">").rstrip("/")
    out = {}
    for name, value in ATTR.findall(body):
        out[name.lower()] = value.strip("\"'") if value else ""
    return out


def resolve(root, page, src):
    src = urllib.parse.unquote(src.split("#", 1)[0].split("?", 1)[0])
    if not src or re.match(r"^(?:[a-z][a-z0-9+.-]*:|//)", src, re.I):
        return None
    base = root if src.startswith("/") else os.path.dirname(page)
    return os.path.normpath(os.path.join(base, src.lstrip("/")))


def size_images(root, page, text):
    """Return (new_text, added, skipped) where skipped names images it could not size."""
    added, skipped = [], []

    def fix(m):
        tag = m.group(0)
        a = attrs_of(tag)
        has_w, has_h = a.get("width", "").isdigit(), a.get("height", "").isdigit()
        if has_w and has_h:
            return tag
        src = a.get("src", "")
        path = resolve(root, page, src)
        dims = image_size(path) if path else None
        if not dims or not all(dims):
            skipped.append(src or "(no src)")
            return tag
        w, h = dims
        if has_w:
            extra = f' height="{round(int(a["width"]) * h / w)}"'
        elif has_h:
            extra = f' width="{round(int(a["height"]) * w / h)}"'
        else:
            extra = f' width="{w}" height="{h}"'
        added.append(src)
        return tag[:4] + extra + tag[4:]

    return IMG.sub(fix, text), added, skipped


# --------------------------------------------------------------------------- favicons, robots, sitemap


# A favicon link is rel="icon" or rel="shortcut icon": the token `icon` on its
# own. apple-touch-icon and mask-icon contain the letters but are not one.
FAVICON_LINK = re.compile(r'<link[^>]+rel=["\'](?:[^"\']*\s)?icon(?:\s[^"\']*)?["\']', re.I)


def has_icon(root, page_texts):
    if any(os.path.exists(os.path.join(root, f)) for f in ("favicon.svg", "favicon.ico", "favicon.png")):
        return True
    return any(FAVICON_LINK.search(t) for t in page_texts)


def favicon_svg(cfg):
    mono = html.escape(cfg["mono"])
    size = 34 if len(cfg["mono"]) == 1 else 26
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="14" fill="{cfg["bg"]}"/>'
        f'<text x="32" y="{32 + size * 0.35:.0f}" text-anchor="middle" '
        'font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="{size}" font-weight="700" fill="{cfg["fg"]}">{mono}</text></svg>\n'
    )


def favicon_rasters(root, cfg):
    """apple-touch-icon.png (180) + favicon.ico (16/32/48). Needs Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return []
    big = 512
    im = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, big - 1, big - 1], radius=112, fill=cfg["bg"])
    size = 272 if len(cfg["mono"]) == 1 else 208
    font = None
    for name in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "Arial Bold.ttf"):
        try:
            font = ImageFont.truetype(name, size)
            break
        except OSError:
            continue
    if font is None:
        try:
            font = ImageFont.load_default(size=size)
        except TypeError:
            return []
    d.text((big / 2, big / 2), cfg["mono"], font=font, fill=cfg["fg"], anchor="mm")
    made = []
    touch, ico = os.path.join(root, "apple-touch-icon.png"), os.path.join(root, "favicon.ico")
    if not os.path.exists(touch):
        im.resize((180, 180), Image.LANCZOS).save(touch, optimize=True)
        made.append("apple-touch-icon.png")
    if not os.path.exists(ico):
        im.save(ico, sizes=[(16, 16), (32, 32), (48, 48)])
        made.append("favicon.ico")
    return made


def git_date(root, path):
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", "-1", "--format=%cs", "--", os.path.relpath(path, root)],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ""
    return out or datetime.date.today().isoformat()


def sitemap_xml(root, host, page_list):
    rows = []
    for page in page_list:
        rows.append(
            f"  <url>\n    <loc>{html.escape(page_url(root, host, page))}</loc>\n"
            f"    <lastmod>{git_date(root, page)}</lastmod>\n  </url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )


def robots_txt(host):
    return f"User-agent: *\nAllow: /\n\nSitemap: https://{host}/sitemap.xml\n"


# --------------------------------------------------------------------------- <head> partial


def partial_tags():
    text = read(PARTIAL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return [line.strip() for line in text.splitlines() if line.strip().startswith("<")]


ROOT_ONLY = ("description", "canonical", "og:", "twitter:")


def tag_key(tag):
    a = attrs_of("<x " + tag.split(None, 1)[1]) if " " in tag else {}
    for k in ("charset", "name", "property", "rel"):
        if k in a:
            return k, (a[k] if k != "charset" else "").lower()
    return None, None


def head_inserts(root, host, cfg, page, text):
    """Tags from the partial this page is missing, filled for this site."""
    head = text.split("</head>", 1)[0] if "</head>" in text else ""
    if not head:
        return []
    is_root = os.path.relpath(page, root) == "index.html"
    title = re.search(r"<title>(.*?)</title>", head, re.S | re.I)
    existing_desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', head, re.I)
    theme = re.search(r'<meta[^>]+name=["\']theme-color["\'][^>]+content=["\']([^"\']*)', head, re.I)
    og_image = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']*)', head, re.I)
    fields = {
        "theme_color": theme.group(1) if theme else cfg["bg"],
        "description": existing_desc.group(1) if existing_desc else cfg.get("description", ""),
        "url": page_url(root, host, page),
        "title": html.unescape(title.group(1).strip()) if title else "",
        "site_name": cfg["name"],
        "og_image": og_image.group(1) if og_image else cfg.get("og_image", ""),
    }
    fields["twitter_card"] = "summary_large_image" if fields["og_image"] else "summary"
    page_has_icon = FAVICON_LINK.search(head)
    out = []
    for tag in partial_tags():
        kind, value = tag_key(tag)
        if kind is None:
            continue
        if not is_root and value.startswith(ROOT_ONLY):
            continue
        if kind == "rel" and "icon" in value:
            href = attrs_of("<x " + tag.split(None, 1)[1])["href"]
            if (value == "icon" and page_has_icon) or not os.path.exists(os.path.join(root, href.lstrip("/"))):
                continue
        if kind == "charset":
            present = re.search(r"<meta[^>]+charset=", head, re.I)
        else:
            present = re.search(rf'<(?:meta|link)[^>]+{kind}=["\']{re.escape(value)}["\']', head, re.I)
        if present:
            continue
        missing = [f for f in re.findall(r"{{(\w+)}}", tag) if not fields.get(f)]
        if missing:
            continue
        filled = re.sub(r"{{(\w+)}}", lambda m: html.escape(fields[m.group(1)], quote=True), tag)
        out.append(filled)
    return out


def insert_head(text, tags):
    m = re.search(r"\n([ \t]*)</head>", text, re.I)
    indent = (m.group(1) if m else "") + "  "
    block = "".join(f"{indent}{t}\n" for t in tags)
    if m:
        return text[: m.start() + 1] + block + text[m.start() + 1:]
    return text.replace("</head>", block + "</head>", 1)


# --------------------------------------------------------------------------- deploy list


def workflow_copies(root):
    """Top-level names a pages.yml copy list publishes, or None when the repo has
    no such list (the whole branch is the site)."""
    wf = os.path.join(root, ".github", "workflows", "pages.yml")
    if not os.path.exists(wf):
        return None
    lines = [l for l in read(wf).splitlines() if re.search(r"^\s*(if .*then )?cp\b", l)]
    if not lines:
        return None
    words = set()
    for line in lines:
        words.update(w.rstrip("/;") for w in re.findall(r"[\w.@/-]+", line))
    return words


def workflow_list_gaps(root, new_files):
    """Files a pages.yml with an explicit copy list would never publish."""
    published = workflow_copies(root)
    if published is None:
        return []
    return [f for f in new_files if f not in published]


# --------------------------------------------------------------------------- commands


def run(root, apply):
    root = os.path.abspath(root)
    host = site_host(root)
    if host not in SITES:
        print(f"{root}: CNAME says {host!r}, not in SITES — skipped")
        return 1
    cfg = SITES[host]
    plist = pages(root)
    texts = {p: read(p) for p in plist}
    print(f"\n== {host}  ({root})")

    created = []
    imgs_added = imgs_skipped = 0
    for page in plist:
        text = texts[page]
        new, added, skipped = size_images(root, page, text)
        imgs_added += len(added)
        imgs_skipped += len(skipped)
        for s in skipped:
            print(f"   ·  {os.path.relpath(page, root)}: could not size <img src={s!r}> (remote, missing or unreadable)")
        tags = [] if is_redirect(new) else head_inserts(root, host, cfg, page, new)
        if tags:
            new = insert_head(new, tags)
            print(f"   +  {os.path.relpath(page, root)}: <head> gains {', '.join(t.split()[0][1:] + ' ' + (tag_key(t)[1] or 'charset') for t in tags)}")
        if added:
            print(f"   +  {os.path.relpath(page, root)}: width/height on {len(added)} <img>")
        if apply and new != text:
            write(page, new)
            texts[page] = new
    if not imgs_added:
        print("   ok images: every local <img> already has width and height" if not imgs_skipped else "   ok images: nothing more to size")

    if has_icon(root, texts.values()):
        print("   ok favicon present")
    else:
        if not apply:
            print("   +  favicon.svg (+ favicon.ico, apple-touch-icon.png with Pillow; existing files kept)")
        if apply:
            if not os.path.exists(os.path.join(root, "favicon.svg")):
                write(os.path.join(root, "favicon.svg"), favicon_svg(cfg))
                created.append("favicon.svg")
            created += favicon_rasters(root, cfg)
            print(f"   +  {', '.join(f for f in created if 'icon' in f) or 'favicon files already present'}")
            # Second pass now the files exist: link them from every page.
            for page in plist:
                if is_redirect(texts[page]):
                    continue
                tags = [t for t in head_inserts(root, host, cfg, page, texts[page]) if "icon" in t]
                if tags:
                    texts[page] = insert_head(texts[page], tags)
                    write(page, texts[page])

    if os.path.exists(os.path.join(root, "robots.txt")):
        print("   ok robots.txt present")
    else:
        print("   +  robots.txt")
        if apply:
            write(os.path.join(root, "robots.txt"), robots_txt(host))
            created.append("robots.txt")

    if os.path.exists(os.path.join(root, "sitemap.xml")):
        print("   ok sitemap.xml present")
    else:
        listed = [p for p in plist if is_listable(root, p, texts[p])]
        print(f"   +  sitemap.xml ({len(listed)} page(s): {', '.join(page_url(root, host, p) for p in listed)})")
        if apply:
            write(os.path.join(root, "sitemap.xml"), sitemap_xml(root, host, listed))
            created.append("sitemap.xml")

    gaps = workflow_list_gaps(root, created)
    if gaps:
        print(f"   !  .github/workflows/pages.yml copies an explicit file list; add: {' '.join(gaps)}")
    return 0


def shrink(root, max_width, quality, min_bytes):
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("shrink needs Pillow: pip install pillow")
        return 1
    root = os.path.abspath(root)
    saved = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in sorted(filenames):
            if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            path = os.path.join(dirpath, name)
            before = os.path.getsize(path)
            if before < min_bytes:
                continue
            with Image.open(path) as im:
                if getattr(im, "is_animated", False) or getattr(im, "n_frames", 1) > 1:
                    print(f"   ·  {os.path.relpath(path, root)}: animated, left as is")
                    continue
                im.load()
                fmt = im.format
                out = ImageOps.exif_transpose(im)
                if out.width > max_width:
                    out = out.resize((max_width, round(out.height * max_width / out.width)), Image.LANCZOS)
                tmp = path + ".sitekit"
                if fmt == "JPEG":
                    out.convert("RGB").save(tmp, "JPEG", quality=quality, optimize=True, progressive=True)
                elif fmt == "WEBP":
                    out.save(tmp, "WEBP", quality=quality, method=6)
                else:
                    out.save(tmp, "PNG", optimize=True)
            after = os.path.getsize(tmp)
            if after < before * 0.9:
                os.replace(tmp, path)
                saved += before - after
                print(f"   -  {os.path.relpath(path, root)}: {before // 1024} KiB -> {after // 1024} KiB")
            else:
                os.remove(tmp)
    print(f"   saved {saved // 1024} KiB")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=("check", "fix", "shrink"))
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--max-width", type=int, default=1600)
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--min-bytes", type=int, default=100_000)
    args = ap.parse_args(argv)
    status = 0
    for d in args.dirs:
        if args.command == "shrink":
            status |= shrink(d, args.max_width, args.quality, args.min_bytes)
        else:
            status |= run(d, apply=args.command == "fix")
    return status


if __name__ == "__main__":
    sys.exit(main())
