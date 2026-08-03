#!/usr/bin/env python3
"""
build_seo.py — regenerate per-page SEO metadata, sitemap, and robots.txt.

For every page it rebuilds the <head> into one consistent structure while
PRESERVING that page's own <title> and meta description:

    charset, viewport
    title, description, canonical
    Open Graph (og:*), Twitter card
    JSON-LD structured data (index + members)
    shared head-common block (theme-color, stylesheet, favicon) inlined from
        partials/head-common.html  (still single-sourced; sync_partials.py also
        keeps it in step)

It then writes sitemap.xml and robots.txt.

The site stays plain static HTML — this only runs while editing/deploying.

Usage
-----
    python3 scripts/build_seo.py                      # uses the default base URL
    python3 scripts/build_seo.py --base https://lab.example.org   # set real domain (one command)
    python3 scripts/build_seo.py --check              # report drift, write nothing (exit 1 if any)

When the lab's real domain is chosen, re-run with --base and commit.
"""

import argparse
import json
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_BASE = "https://hoon-lab-site-v2.pages.dev"  # Cloudflare Pages default (see DEPLOYMENT_PLAN.md)

SITE_NAME = "Clinical Neuroimaging Lab — Kim Lab"


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def page_url(base, fname):
    return base + "/" if fname == "index.html" else f"{base}/{fname}"


def jsonld_for(fname, base):
    """Return a list of schema.org objects for this page (empty if none)."""
    if fname == "index.html":
        return [
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Clinical Neuroimaging Lab (Kim Lab)",
                "alternateName": "Kim Lab",
                "url": base + "/",
                "logo": base + "/images/social-card.jpg",
                "email": "jkim@med.cuny.edu",
                "parentOrganization": {
                    "@type": "CollegeOrUniversity",
                    "name": "CUNY School of Medicine",
                },
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "160 Convent Avenue",
                    "addressLocality": "New York",
                    "addressRegion": "NY",
                    "postalCode": "10031",
                    "addressCountry": "US",
                },
            },
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": SITE_NAME,
                "url": base + "/",
            },
        ]
    if fname == "members.html":
        return [
            {
                "@context": "https://schema.org",
                "@type": "Person",
                "name": "Junghoon Kim",
                "jobTitle": "Principal Investigator",
                "email": "jkim@med.cuny.edu",
                "worksFor": {
                    "@type": "Organization",
                    "name": "Clinical Neuroimaging Lab (Kim Lab)",
                    "url": base + "/",
                },
                "affiliation": {
                    "@type": "CollegeOrUniversity",
                    "name": "CUNY School of Medicine",
                },
            }
        ]
    return []


def build_head(fname, title, desc, base, head_common):
    """Return the inner HTML of <head> for one page."""
    url = page_url(base, fname)
    og_title = title.split(" | ")[0].strip()  # drop the institution suffix for social previews
    img = base + "/images/social-card.jpg"
    lines = [
        "",
        '  <meta charset="UTF-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        "",
        f"  <title>{title}</title>",
        f'  <meta name="description" content="{desc}" />',
        f'  <link rel="canonical" href="{url}" />',
        "",
        "  <!-- Open Graph -->",
        '  <meta property="og:type" content="website" />',
        f'  <meta property="og:url" content="{url}" />',
        f'  <meta property="og:title" content="{og_title}" />',
        f'  <meta property="og:description" content="{desc}" />',
        f'  <meta property="og:image" content="{img}" />',
        f'  <meta property="og:site_name" content="{SITE_NAME}" />',
        "",
        "  <!-- Twitter -->",
        '  <meta name="twitter:card" content="summary_large_image" />',
        f'  <meta name="twitter:title" content="{og_title}" />',
        f'  <meta name="twitter:description" content="{desc}" />',
        f'  <meta name="twitter:image" content="{img}" />',
    ]
    blocks = jsonld_for(fname, base)
    if blocks:
        payload = blocks[0] if len(blocks) == 1 else blocks
        lines += ["", '  <script type="application/ld+json">',
                  json.dumps(payload, indent=2, ensure_ascii=False), "  </script>"]
    lines += [
        "",
        # Markers at column 0 to match sync_partials.py's convention, so the two
        # tools agree on this region regardless of which runs last.
        "<!-- @sync:head-common -->",
        head_common.rstrip("\n"),
        "<!-- @end:head-common -->",
        "",
    ]
    return "\n".join(lines)


def rebuild_page(text, fname, base, head_common):
    title_m = re.search(r"<title>(.*?)</title>", text, re.S)
    desc_m = re.search(r'<meta name="description" content="(.*?)"\s*/?>', text, re.S)
    if not title_m or not desc_m:
        raise ValueError(f"{fname}: could not find <title> or meta description")
    title = title_m.group(1).strip()
    desc = desc_m.group(1).strip()
    new_inner = build_head(fname, title, desc, base, head_common)
    return re.sub(r"(<head>).*?(</head>)", lambda m: m.group(1) + new_inner + m.group(2),
                  text, count=1, flags=re.S)


def write_sitemap(base, pages):
    urls = []
    for p in pages:
        if p == "404.html":
            continue
        urls.append(f"  <url><loc>{page_url(base, p)}</loc></url>")
    body = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")
    return body


def write_robots(base):
    return ("User-agent: *\n"
            "Allow: /\n\n"
            f"Sitemap: {base}/sitemap.xml\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE, help="production base URL (no trailing slash)")
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    head_common = read(os.path.join(ROOT, "partials", "head-common.html"))
    pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.html")))

    changed = []
    for fname in pages:
        path = os.path.join(ROOT, fname)
        original = read(path)
        updated = rebuild_page(original, fname, base, head_common)
        if updated != original:
            changed.append(fname)
            if not args.check:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(updated)

    sitemap = write_sitemap(base, pages)
    robots = write_robots(base)
    for name, content in (("sitemap.xml", sitemap), ("robots.txt", robots)):
        path = os.path.join(ROOT, name)
        old = read(path) if os.path.exists(path) else None
        if old != content:
            changed.append(name)
            if not args.check:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(content)

    if args.check:
        if changed:
            print("OUT OF SYNC: " + ", ".join(changed))
            return 1
        print("SEO metadata is up to date.")
        return 0
    print(f"Base URL: {base}")
    print("Updated: " + (", ".join(changed) if changed else "(nothing — already current)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
