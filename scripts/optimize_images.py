#!/usr/bin/env python3
"""
optimize_images.py — shrink images and serve modern WebP with a safe fallback.

For every raster image referenced by the pages it:
  1. downsizes any original wider than MAX_WIDTH (retina-generous),
  2. writes a sibling .webp next to it (Pillow, no external tools),
  3. wraps the page's <img> in <picture> so browsers pick WebP when supported
     and fall back to the original jpg/png otherwise.

The wrap is idempotent (it strips any existing wrapper first, then re-wraps),
so you can re-run it any time — e.g. after dropping in a new image. CSS lays
out unchanged because `picture { display: contents; }` removes the wrapper box.

Usage:
    python3 scripts/optimize_images.py
    python3 scripts/optimize_images.py --check   # report work to do, change nothing
"""

import argparse
import glob
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_WIDTH = 1600
WEBP_QUALITY = 82
JPEG_QUALITY = 86
EXCLUDE = {"images/social-card.jpg"}  # og:image stays a plain JPG for max compatibility

STRIP_RE = re.compile(
    r'<picture><source type="image/webp" srcset="[^"]+"\s*/>(<img\b[^>]*?/?>)</picture>',
    re.S,
)
IMG_RE = re.compile(r'(<img\b[^>]*?src="(images/[^"]+\.(?:jpg|png))"[^>]*?/?>)', re.S)


def referenced_images():
    refs = set()
    for page in glob.glob(os.path.join(ROOT, "*.html")):
        with open(page, encoding="utf-8") as fh:
            for rel in re.findall(r'images/[^"]+\.(?:jpg|png)', fh.read()):
                refs.add(rel)
    return sorted(refs - EXCLUDE)


def webp_path(rel):
    return re.sub(r"\.(?:jpg|png)$", ".webp", rel)


def process_assets(check):
    todo = []
    for rel in referenced_images():
        src = os.path.join(ROOT, rel)
        if not os.path.exists(src):
            continue
        webp = os.path.join(ROOT, webp_path(rel))
        im = Image.open(src)
        needs_resize = im.width > MAX_WIDTH
        needs_webp = not os.path.exists(webp) or os.path.getmtime(webp) < os.path.getmtime(src)
        if not (needs_resize or needs_webp):
            continue
        todo.append(rel)
        if check:
            continue
        if needs_resize:
            h = round(im.height * MAX_WIDTH / im.width)
            im = im.resize((MAX_WIDTH, h), Image.LANCZOS)
            if rel.lower().endswith(".png"):
                im.save(src, "PNG", optimize=True)
            else:
                im.convert("RGB").save(src, "JPEG", quality=JPEG_QUALITY)
        Image.open(src).save(webp, "WEBP", quality=WEBP_QUALITY, method=6)
    return todo


def rewrap_pages(check):
    changed = []
    for page in glob.glob(os.path.join(ROOT, "*.html")):
        with open(page, encoding="utf-8") as fh:
            original = fh.read()
        text = STRIP_RE.sub(r"\1", original)  # remove old wrappers (idempotency)

        def repl(m):
            tag, src = m.group(1), m.group(2)
            if src in EXCLUDE or not os.path.exists(os.path.join(ROOT, webp_path(src))):
                return tag
            return f'<picture><source type="image/webp" srcset="{webp_path(src)}" />{tag}</picture>'

        text = IMG_RE.sub(repl, text)
        if text != original:
            changed.append(os.path.basename(page))
            if not check:
                with open(page, "w", encoding="utf-8") as fh:
                    fh.write(text)
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    assets = process_assets(args.check)
    pages = rewrap_pages(args.check)
    if args.check:
        if assets or pages:
            print("WORK PENDING — assets:", assets or "(none)", "| pages:", pages or "(none)")
            return 1
        print("Images already optimized.")
        return 0
    print("WebP/resize applied to:", ", ".join(assets) if assets else "(none new)")
    print("Pages re-wrapped:", ", ".join(pages) if pages else "(none)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
