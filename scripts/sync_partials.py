#!/usr/bin/env python3
"""
sync_partials.py — one source of truth for the shared page chrome.

The site is plain static HTML with no build step, but the header and footer
are the same on every page. Instead of editing 8 files by hand, edit the
single source in  partials/  and run this script to push the change into
every page, between matching marker comments:

    <!-- @sync:header -->   ... injected from partials/header.html ...   <!-- @end:header -->
    <!-- @sync:footer -->   ... injected from partials/footer.html ...   <!-- @end:footer -->

The deployed site never runs this — it ships as ordinary HTML. This is only
a convenience for editing.

Usage
-----
    python3 scripts/sync_partials.py             # push partials/ into all pages
    python3 scripts/sync_partials.py --check     # report out-of-sync pages, write nothing (exit 1 if any)
    python3 scripts/sync_partials.py --bootstrap  # one-time: insert the markers into pages that don't have them yet

How it maps partials to regions
-------------------------------
Each file  partials/NAME.html  fills the region named NAME. To add a new
shared region later (e.g. head-common), drop  partials/head-common.html  and
add  <!-- @sync:head-common --> ... <!-- @end:head-common -->  where it belongs.
"""

import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTIALS_DIR = os.path.join(ROOT, "partials")

# Pages that should NOT receive a given region.
# 404.html intentionally keeps its own minimal footer (copyright bar only),
# so it is left out of the footer sync.
REGION_EXCLUDE = {
    "footer": {"404.html"},
}

# Used only by --bootstrap, to locate a region the very first time (before any
# markers exist) so the markers can be wrapped around it. After bootstrap these
# are never used again — normal runs match the markers instead.
BOOTSTRAP_PATTERNS = {
    "header": re.compile(r"[ \t]*<a href=\"#main\" class=\"skip-link\">.*?</header>", re.S),
    "footer": re.compile(r"[ \t]*<footer class=\"site-footer\".*?</footer>", re.S),
}


def load_partials():
    """Return {name: content} for every partials/*.html (trailing newlines trimmed)."""
    out = {}
    for path in sorted(glob.glob(os.path.join(PARTIALS_DIR, "*.html"))):
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as fh:
            out[name] = fh.read().rstrip("\n")
    return out


def html_pages():
    return sorted(glob.glob(os.path.join(ROOT, "*.html")))


def wrapped(name, content):
    """The full marker block that gets written into a page."""
    return f"<!-- @sync:{name} -->\n{content}\n<!-- @end:{name} -->"


def render(src, partials, bootstrap):
    """Return the page text with every applicable region replaced. Pure function."""
    base = os.path.basename(src["path"])
    text = src["text"]
    for name, content in partials.items():
        if base in REGION_EXCLUDE.get(name, set()):
            continue
        marker_re = re.compile(
            re.escape(f"<!-- @sync:{name} -->") + r".*?" + re.escape(f"<!-- @end:{name} -->"),
            re.S,
        )
        if marker_re.search(text):
            # Normal path: replace whatever is between the markers.
            text = marker_re.sub(lambda _m: wrapped(name, content), text, count=1)
        elif bootstrap and name in BOOTSTRAP_PATTERNS:
            # First-time path: wrap markers around the existing region.
            pat = BOOTSTRAP_PATTERNS[name]
            if pat.search(text):
                text = pat.sub(lambda _m: wrapped(name, content), text, count=1)
    return text


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--sync"
    if mode not in ("--sync", "--check", "--bootstrap"):
        print(f"Unknown option: {mode}", file=sys.stderr)
        return 2

    partials = load_partials()
    if not partials:
        print("No partials found in partials/ — nothing to do.", file=sys.stderr)
        return 1

    changed, stale = [], []
    for path in html_pages():
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        updated = render({"path": path, "text": original}, partials, bootstrap=(mode == "--bootstrap"))
        if updated == original:
            continue
        if mode == "--check":
            stale.append(os.path.basename(path))
        else:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(updated)
            changed.append(os.path.basename(path))

    if mode == "--check":
        if stale:
            print("OUT OF SYNC: " + ", ".join(stale))
            print("Run: python3 scripts/sync_partials.py")
            return 1
        print("All pages are in sync with partials/.")
        return 0

    print("Synced regions: " + ", ".join(partials.keys()))
    print("Updated: " + (", ".join(changed) if changed else "(nothing — already current)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
