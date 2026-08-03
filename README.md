# Clinical Neuroimaging Lab — Website

The public website of the **Clinical Neuroimaging Lab (Kim Lab)**, directed by
Junghoon Kim, PhD, at the CUNY School of Medicine, The City College of New York.

**Live site:** <https://cnl-cunymed.github.io/lab-website/>

The lab studies neurodegeneration and neuroplasticity after traumatic brain
injury, combining advanced neuroimaging with neuropsychological assessment to
understand the mechanisms of functional recovery and to develop new treatments.

---

## About this repository

A hand-built static website: plain HTML, one stylesheet, one JavaScript file. No
framework, no build step, no external dependencies. Nothing is fetched from a
third-party CDN at run time, so the site loads quickly, works offline once
cached, and will keep working without maintenance for years.

Maintained by **Yifei Li** on behalf of the lab.

| | |
|---|---|
| Hosting | GitHub Pages, built from `main` at the repository root |
| Repository | `cnl-cunymed/lab-website` |
| Pages | 9 (Home, Lab Members, Research, Publications, Techniques, Funding, Photos, Contact, 404) |
| Brand color | `#007064`, the CUNY School of Medicine teal |
| Typography | Inter (body) and Fraunces (display), both self-hosted |

---

## Repository layout

```
lab-website/
├── index.html              Home — hero, mission, news, research preview, recent publications
├── members.html            Lab Members — PI, research scientist, PhD and master's students, alumni
├── research.html           Research — featured tPBM trial, CVR, biomarkers, cognitive rehabilitation
├── publications.html       Publications — 39 entries, searchable and filterable by year
├── techniques.html         Techniques — imaging and assessment methods
├── funding.html            Funding and partner institutions
├── photos.html             Photos — scans and imaging, lab life, conferences
├── contact.html            Contact details, map, and how to join
├── 404.html                Page-not-found fallback
│
├── css/style.css           Design tokens and every component style
├── js/main.js              Navigation, scroll reveal, publication filter, photo lightbox
├── fonts/                  Self-hosted Inter and Fraunces (woff2)
├── images/                 People, hero, research, techniques, funding logos, gallery
│
├── partials/               Single source for the chrome repeated on every page
│   ├── header.html
│   ├── footer.html
│   └── head-common.html
│
├── scripts/                Maintenance helpers, run while editing — never in the browser
│   ├── sync_partials.py    Push the shared header/footer into every page
│   ├── build_seo.py        Rebuild canonical/Open Graph/structured data, sitemap, robots
│   └── optimize_images.py  Generate WebP alongside each image and wire up <picture>
│
├── CONTENT.md              Source of truth for every fact the site states
├── CREDITS.md              Attribution and licensing for third-party imagery
├── DEPLOY.md               How to publish an update
├── README.md               This file
├── robots.txt
└── sitemap.xml
```

---

## Editing the site

Each page is a single HTML file. Find the commented section, edit the text, save,
refresh the browser. There is nothing to compile.

Preview locally before publishing:

```bash
cd /path/to/lab-website
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

### Adding a lab member

Open `members.html`, find the relevant section, and copy an existing
`<article class="member-card">` block. Add the headshot to `images/people/` as a
square image, then run `python3 scripts/optimize_images.py` to generate the WebP
version. Record the person's details in `CONTENT.md` at the same time.

### Adding a publication

Copy an existing `<li class="pub-item">` in `publications.html` and set
`data-year` to match the publication year. **If that year has no chip in the
`.year-chips` block, add one**, otherwise the filter will silently hide the
entry. Wrap Dr. Kim's name in `<span class="pi">` so it renders in brand teal.
Only papers with Junghoon Kim on the author list belong on this page.

### Editing the header or footer

These are identical on every page, so they live in one place. Edit
`partials/header.html` or `partials/footer.html`, then run:

```bash
python3 scripts/sync_partials.py
```

This rewrites the region between the `<!-- @sync:header -->` and
`<!-- @end:header -->` markers on every page. The published site is still plain
HTML; the script only runs while editing.

### Before committing

```bash
python3 scripts/sync_partials.py --check
python3 scripts/build_seo.py --check
python3 scripts/optimize_images.py --check
```

Each reports what has drifted and exits non-zero if anything is out of date.

---

## Publishing

See **[DEPLOY.md](DEPLOY.md)** for the full procedure, including how to replace
the published site with a new version without changing its address.

---

## Standards

- **Accessibility.** WCAG AA contrast throughout, full keyboard navigation, skip
  link, semantic landmarks, visible focus rings, and `prefers-reduced-motion`
  honoured. Every image carries alternative text and intrinsic dimensions so the
  page does not shift while loading.
- **Privacy.** Only institutional contact details appear on the site. Personal
  telephone numbers, personal email addresses, and curricula vitae are never
  committed to this repository.
- **Performance.** One stylesheet, one script, self-hosted fonts, WebP images
  with fallbacks, lazy loading below the fold, and inline SVG icons.
- **Browser support.** All current versions of Chrome, Safari, Firefox, and Edge.

---

## Content and attribution

`CONTENT.md` records every fact the site states, so no page detail depends on a
document that exists only on one person's computer. Update it whenever the site
changes.

Biographical and publication content comes from Dr. Kim's CUNY faculty page, his
public PubMed bibliography, the Department of Defense grant announcement, lab
members' own submissions, and direct lab knowledge. The publication list is
reconciled against the PubMed API rather than transcribed by hand.

Photographs and brain imagery that the lab did not produce are credited
individually in `CREDITS.md`, and are being replaced with the lab's own material.

---

© Clinical Neuroimaging Lab, CUNY School of Medicine.
