# 🌐 Kim Lab Website Deployment Plan

> **Goal.** Take the static site sitting in this folder and put it on the public internet under a professional URL, with the lowest sane cost and the cleanest handoff path for whoever maintains it next.

---

## ⚠️ Before You Touch Anything Else

Find out what **CUNY School of Medicine** expects for faculty/lab websites. This single answer determines which of the three paths below you take, and skipping it risks building the wrong thing twice.

> 💡 **Who to ask.** The CUNY SoM communications office, or Dr. Kim directly if he already knows the policy.

Four questions to bring:

1. Is institutional hosting required for lab websites, or optional?
2. Will they host a static HTML site as-is, or do they require WordPress or another CMS?
3. Can the lab get a subdomain like `kimlab.med.cuny.edu` even if hosted externally?
4. Is there a branding, accessibility, or content policy the site has to comply with?

The answer maps to one of three paths:

| If CUNY says... | Then... |
|---|---|
| Institutional hosting is required and they want WordPress | Skip the steps below. Work with their team to migrate the design into their CMS |
| Institutional hosting is required and they accept static HTML | Hand them this folder, ask for a subdomain. No domain purchase needed |
| Institutional hosting is optional or hands-off | Follow the full plan below |

---

## 🛣️ The Full Plan (Cloudflare Pages Path)

These are the steps assuming CUNY's answer is "do whatever you want." Eight steps, roughly 30 to 45 minutes of active work plus some waiting for domain and DNS propagation.

### Step 1: Agree on a domain name with Dr. Kim

Pick something short, professional, and memorable. Three reasonable directions:

- **Lab name based.** `kimlab.org`, `kimlab.science`, `kimlab.io`
- **Lab function based.** `clinicalneuroimaginglab.org`, `cnl-cuny.org`
- **PI initials based.** `jkimlab.org` (less common but distinctive)

> ⚠️ **Check availability before committing.** Type each candidate into [cloudflare.com/products/registrar](https://www.cloudflare.com/products/registrar/) and see what's actually for sale. The `.org` TLD is the academic convention; `.com` is fine; `.science` and `.io` work but cost more.

### Step 2: Buy the domain

Register at **Cloudflare Registrar** (recommended) or Namecheap. Cost is roughly $10 to $15 per year for `.org` or `.com`, more for trendy TLDs.

> 💡 **Why Cloudflare Registrar.** They sell domains at wholesale cost with no markup, and the registration auto-integrates with Cloudflare Pages in the next steps. Namecheap is fine but adds one extra DNS configuration step later.

✅ Set auto-renew on. Lab websites that expire because nobody renewed the domain are a real and embarrassing failure mode.

✅ Use the lab credit card or whatever payment method Dr. Kim approves. Keep the receipt for reimbursement.

### Step 3: Move the site into its own GitHub repo

Right now this folder lives inside Yifei's personal `ai-ap` class workspace. That has to change before the site goes public.

1. On GitHub, create a new repository named `kim-lab-site` (or similar). Public is fine; private works too.
2. Clone it to your machine: `git clone https://github.com/YOUR_USERNAME/kim-lab-site.git`
3. Copy the contents of this Hoon_Lab_Site folder into the new repo folder (everything except this plan file).
4. Commit and push: `git add . && git commit -m "Initial commit" && git push`

> 📌 **Why a separate repo.** Three reasons. It keeps the lab's public infrastructure separate from Yifei's class work, it makes the deploy configuration cleaner, and it gives whoever inherits the site a single repo to clone without inheriting unrelated material.

### Step 4: Sign up for Cloudflare and connect the repo

1. Create a free account at [cloudflare.com](https://www.cloudflare.com/) using the lab email if there is one, or Yifei's email for now.
2. In the dashboard, go to **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**.
3. Authorize Cloudflare to read your GitHub account, select the `kim-lab-site` repo.
4. **Build settings.** Framework preset: **None**. Build command: leave blank. Build output directory: leave as `/` (root).
5. Click **Save and Deploy**.

Within about 60 seconds the site is live at a temporary URL like `kim-lab-site.pages.dev`. Test it. Every page should load, every image should appear, every internal link should work.

### Step 5: Connect the custom domain

1. In the Cloudflare Pages project dashboard, click **Custom domains** → **Set up a domain**.
2. Enter the domain you bought in Step 2 (e.g., `kimlab.org`).
3. If you registered through Cloudflare Registrar, DNS configures itself automatically. If through Namecheap, Cloudflare will give you two nameservers to paste into Namecheap's DNS settings (one-time, takes 5 minutes).
4. Wait for SSL/HTTPS to provision. Usually a few minutes, occasionally up to an hour.

### Step 6: Verify everything works

Open the custom domain in a browser. Walk through this checklist:

- [ ] Homepage loads with HTTPS (lock icon in address bar)
- [ ] All nav links work (Research, Members, Publications, Funding, Photos, Contact)
- [ ] Images load on every page
- [ ] Mobile layout renders correctly (test on phone or browser dev tools)
- [ ] External links (DOI links on publications page) open correctly
- [ ] Mailto links on contact page launch email client
- [ ] No console errors when you open browser dev tools

### Step 7: Document the maintenance workflow

Add a short `README.md` to the GitHub repo explaining how future updates happen. Three sentences is enough:

> To update the site, edit the HTML files in this repo, commit, and push to `main`. Cloudflare Pages will automatically rebuild and redeploy within a minute. To add a new lab member, follow the existing pattern in `members.html`.

### Step 8: Hand the keys over

Decide who has admin access to:

- The GitHub repo (add Dr. Kim as a collaborator at minimum)
- The Cloudflare account (transfer to a lab-owned email eventually, not Yifei's personal one)
- The domain registrar account (same)

> ⚠️ **The handoff trap.** If the site is registered under Yifei's personal accounts and Yifei graduates, the lab loses control of its own website when the account holder leaves. Move ownership to a lab-controlled email address before that becomes a problem.

---

## 💰 Cost Summary

| Item | One-time | Annual | Notes |
|---|---|---|---|
| Domain registration (`.org`) | None | $10 to $15 | Only real ongoing cost |
| Cloudflare Pages hosting | None | $0 | Free tier covers this site forever |
| GitHub repo | None | $0 | Public repos are free, private repos are free for personal accounts |
| **Total** | **$0** | **~$12/year** | About a dollar a month |

---

## 📋 Decision Log

Fill these in as you make each decision. Future you (or your replacement) will thank present you.

- **CUNY institutional answer:** _to be filled in after the meeting_
- **Chosen domain name:** _to be filled in after Dr. Kim agrees_
- **Domain registered at:** _Cloudflare Registrar / Namecheap / other_
- **Domain purchase date:** _YYYY-MM-DD_
- **Domain renewal date:** _YYYY-MM-DD (one year later)_
- **GitHub repo URL:** _https://github.com/USERNAME/REPO_
- **Cloudflare Pages project URL:** _https://...pages.dev_
- **Site went live on:** _YYYY-MM-DD_

---

## ✅ Key Takeaways

| What | Why it matters |
|---|---|
| Ask CUNY first | One conversation prevents building the wrong thing |
| Cloudflare Pages over Squarespace | Free, fast, professional, already compatible with what you built |
| Buy the domain through Cloudflare Registrar | At-cost pricing, simpler DNS setup |
| Own everything under a lab email, not a personal one | Sites that get lost when people leave are the most common lab-website failure mode |
| Auto-renew the domain | An expired domain is worse than no domain |
| Total cost: about $12 per year | Hosting is free, the domain is the only line item |
