# Publishing the Site

The published address is fixed by the **organisation and repository name**, not
by anything on your computer:

```
https://cnl-cunymed.github.io/lab-website/
   └── organisation ──┘        └─ repository ─┘
```

GitHub Pages serves the `main` branch from the repository root. Dr. Kim links to
this address from his faculty profile, so **it must not change.**

Your local folder can be called anything at all. `Hoon_Lab_Site_v3` on the
external drive publishes to exactly the same URL as any other name would, because
only the repository name reaches the address bar. Nothing about the folder name
needs to be kept in step.

---

## What must never be published

This repository is **public**. Anything committed to it can be downloaded by
anyone, and stays recoverable from the commit history even after it is deleted
from the current version.

Never commit:

- Curricula vitae (`YLi_CV_NIW.pdf` and similar)
- Personal headshot source files (`Yifei_Headshot.pdf`, camera-resolution
  originals sent in by lab members)
- Personal telephone numbers, personal email addresses, home addresses
- The PI review documents (`READ ME FIRST…docx`, `Website Feedback Form…docx`)
- Anything under `images/_raw/`

Only the cropped, web-sized derivative of a headshot belongs in
`images/people/`. Keep the originals on the drive.

Run this before every publish. It should print nothing:

```bash
find . -name '*.pdf' -o -name '*.docx' -o -name '*_CV_*' -o -name '*Headshot*' \
  | grep -v '^./.git/'
```

---

## Routine update

For ordinary content changes once the repository is set up locally.

```bash
cd /path/to/lab-website

# 1. Confirm the generated layers are current
python3 scripts/sync_partials.py --check
python3 scripts/build_seo.py --check
python3 scripts/optimize_images.py --check

# 2. Review exactly what is about to be published
git status
git diff

# 3. Publish
git add -A
git commit -m "Describe the change"
git push
```

GitHub Pages rebuilds automatically. The change is live in roughly one to two
minutes. Confirm with a hard refresh (`Cmd-Shift-R`), because browsers cache the
stylesheet aggressively.

---

## Replacing the published site with a new version

Use this when the working copy is a **new folder** rather than an edit of the
cloned repository, which is the case when moving from one version of the site to
the next. It replaces every file in the repository in a single commit, so files
that no longer exist are removed from the live site rather than left behind.

Working from a clone keeps the repository's identity and settings intact. Do
**not** delete and recreate the repository: that would take the site offline,
break the link on Dr. Kim's profile until Pages is re-enabled, and require
organisation-owner access.

```bash
# 1. Clone the published repository to a scratch location
cd /tmp
git clone https://github.com/cnl-cunymed/lab-website.git
cd lab-website

# 2. Remove every tracked file, keeping the .git directory
git rm -r --quiet .

# 3. Copy the new version in, excluding local-only material
rsync -a --exclude '.git' --exclude '.DS_Store' --exclude '._*' \
      --exclude '*.pdf' --exclude '*.docx' --exclude 'images/_raw' \
      "/Volumes/Yifei-LaCie/Hoon Lab Project/Hoon_Lab_Site_v3/" .

# 4. Check what will be published — read this list properly
git add -A
git status

# 5. Publish
git commit -m "Publish site refresh: CUNY School of Medicine teal, alumni section, expanded publications"
git push
```

Step 4 is the one that matters. `git status` at that point is the complete list
of what the world will be able to download. Read it before continuing.

---

## Removing something already published

Deleting a file and pushing removes it from the **site**, but not from the
**history**. The old version stays downloadable by anyone who knows the commit
reference until the history itself is replaced.

To replace the history entirely, so previous commits no longer exist on the
default branch:

```bash
cd /tmp/lab-website

# Build a branch with no ancestry
git checkout --orphan clean-main
git add -A
git commit -m "Publish site refresh"

# Replace main with it
git branch -D main
git branch -m main
git push --force origin main
```

Afterwards, confirm the file is gone:

```bash
curl -o /dev/null -w '%{http_code}\n' https://cnl-cunymed.github.io/lab-website/THE_FILE.pdf
```

`404` means it is no longer served.

Two caveats worth knowing:

- A force-push removes the old commits from the branch, but GitHub keeps
  unreferenced objects for a period and they remain reachable by their exact
  commit reference until garbage collection runs. To have them purged
  immediately, an organisation owner should ask GitHub Support. For a document
  that was briefly public this is usually unnecessary, but for anything
  genuinely sensitive it is the only complete remedy.
- If the repository has been forked, each fork keeps its own copy and must be
  handled separately. `lab-website` currently has no forks.

Treat anything that was public as having been seen. For a document containing
personal details, removing it is the right first step, but assume it was
retrievable while it was up.

---

## Checking the live site

```bash
curl -o /dev/null -w '%{http_code}\n' https://cnl-cunymed.github.io/lab-website/
```

`200` means it is serving. To confirm which version is live, look at the brand
colour in the page source: the current site declares
`<meta name="theme-color" content="#007064">`. The previous version used
`#0033A1`.

Also check, after any publish:

- The site loads over the `/lab-website/` sub-path, not from the domain root.
  All internal links are relative, so they follow the sub-path correctly. Never
  change them to start with `/`, which would break every link.
- `sitemap.xml` and every `<link rel="canonical">` point at
  `https://cnl-cunymed.github.io/lab-website/…`. If the address ever changes,
  correct them all in one step:
  ```bash
  python3 scripts/build_seo.py --base https://the-new-address
  ```

---

## If the site stops building

GitHub emails the pusher when a Pages build fails. Check
**Settings → Pages** in the repository: the source must remain **`main`,
folder `/ (root)`**.

A build that succeeds but serves a stale page is nearly always browser cache.
Confirm with:

```bash
curl -s https://cnl-cunymed.github.io/lab-website/ | grep theme-color
```

That bypasses the cache entirely and shows what the server is actually sending.
