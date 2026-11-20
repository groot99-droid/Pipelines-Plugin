# Juniper-Collective

**Static site for an advisory firm.** Source: https://github.com/groot99-droid/Juniper-Collective

Generated 20 November 2026 from the repository clone (`git log`, `git ls-files`, and the files at HEAD). Counts are as cloned. Commit dates are git author dates in UTC and can differ from when the work was done (merged PRs, integration passes).

## 1. Numbers

| Measure | Value |
|---|---|
| Commits (all branches) | 14 (11 non-merge, 3 merge) |
| First commit | 2026-10-28 |
| Last commit | 2026-11-19 |
| Days with commits | 3 |
| Tracked files | 76 |
| Checked-out branch | HEAD |
| Commit authors (non-merge, by name) | groot99-droid: 6; Claude: 5 |

Author names are git author names: "Claude" marks commits made by a Claude session, and the owner's GitHub handle marks commits made by the owner. Email addresses are left out.

**Tracked files by type (top 15):** .html 31; .webp 19; .md 8; .js 4; .py 3; .css 2; .txt 2; .yml 1; (none) 1; .svg 1; .m4a 1; .mp4 1; .webm 1; .xml 1

**Tracked files by top-level folder:** assets 26; (root) 18; src 18; docs 7; build 3; media 3; .github 1

## 2. Activity by month and by day

| Month | Non-merge commits |
|---|---|
| 2026-10 | 10 |
| 2026-11 | 1 |

**Per day (non-merge commits):** 2026-10-28 8; 2026-10-29 2; 2026-11-19 1

## 3. Layout (folders and file counts)

- **assets/** 26 files
  - assets/img/ 19
  - assets/js/ 4
  - assets/css/ 2
- **(repository root)** 18 files
- **src/** 18 files
  - src/pages/ 14
  - src/partials/ 2
- **docs/** 7 files
- **build/** 3 files
- **media/** 3 files
- **.github/** 1 files
  - .github/workflows/ 1

## 5. CI workflows

- `.github/workflows/pages.yml`: Deploy to GitHub Pages

## 6. Documents inventory (8 Markdown files)

Markdown files by folder (top 25): docs 7; (root) 1

- `README.md` (258 words): Juniper Collective. Sections: Layout; Working on it; Founder photos; Notes
- `docs/BRAND.md` (551 words): Juniper Collective: brand. Sections: Essence; Voice; Colour; Type; Marks and icons; Imagery
- `docs/CONTENT-TO-CONFIRM.md` (921 words): Content to confirm. Sections: Added in round two (from the owner's answers and The Reserve's public pages); From the first round (still to confirm); Process and deliverables; Engagements; Diagnostic and contact; Portal; Legal pages (drafts, not legal advice); Kept from the original, check they are current
- `docs/DESIGN.md` (597 words): Design record. Sections: Dissecting the original page; Routing the brief; Checks run
- `docs/IMAGERY.md` (262 words): Imagery record
- `docs/LAUNCH.md` (421 words): Launch checklist. Sections: 1. Register the domain; 2. Set up email on the domain (Google Workspace); 3. Point the domain at GitHub Pages; 4. Tell the site its new address; 5. Before announcing; What is not live
- `docs/OPEN-QUESTIONS.md` (721 words): Open questions. Sections: The firm and its story; Clients and promise; Offer and money; Launch; Portal (see PORTAL-SPEC.md)
- `docs/PORTAL-SPEC.md` (504 words): Client portal: specification and build plan. Sections: What the owner asked for; Why it needs a server; Recommended shape; Security requirements before any real client data; Phasing; Open decisions

## 8. Questionnaires in this repo

- `docs/OPEN-QUESTIONS.md`: 0 questions. 

## 10. Pull requests merged (2)

- 2026-10-28 #1 from `groot99-droid/claude/kind-dirac-im39ww`
- 2026-11-19 #7 from `groot99-droid/claude/inspiring-cori-juqfrm`

## 11. Source documents (verbatim)

Each file below is quoted from the repository at HEAD. Lines start with ">" so its headings do not mix with this document's.

### Source file: README.md

> # Juniper Collective
>
> Static site for Juniper Collective, an advisory firm for experience-based businesses. Published to GitHub Pages by `.github/workflows/pages.yml`.
>
> ## Layout
> ```
> src/layout.html        header, footer, head tags
> src/pages/*.html       one file per page: a front-matter comment, then the body
> src/partials/          the intro overlay, the portal illustration
> assets/css|js|img      stylesheet, scripts, WebP photographs and the favicon
> media/                 the intro video (webm; intro.js also tries an mp4, which is not
>                        versioned) and its ambience track
> build/build.py         builds the pages, sitemap.xml and robots.txt at the repo root
> build/check_site.py    heading, alt, label, id and link checks
> build/icons.py         the icon set and the logomark
> docs/                  brand, design, imagery, content to confirm, open questions,
>                        launch checklist, portal specification
> src/site-url.txt       the public address (change it when the domain goes live)
> ```
>
> ## Working on it
> ```bash
> python build/build.py          # rebuild after editing src/ or build/icons.py
> python build/build.py --check  # fail if the built files are out of date
> python build/check_site.py     # structure and link checks
> python -m http.server 8000     # then open http://localhost:8000
> ```
> The built `*.html` files at the root are committed; edit `src/`, never the root files. The deploy workflow runs both checks first.
>
> ## Founder photos
> Drop square images at `assets/img/team/elijah.webp`, `katelyn.webp` and `nathan.webp` (also `.jpg` or `.png`) and rebuild. Until then the pages show initials.
>
> ## Notes
> - No third-party scripts. Fonts come from Google Fonts; the intro uses WebGL where available and falls back to plain video.
> - The forms open the visitor's email app and store nothing.
> - Anything the copy asserts beyond the original page is listed in `docs/CONTENT-TO-CONFIRM.md`.
>

### Source file: docs/BRAND.md

> # Juniper Collective: brand
>
> The brand as the site now speaks it. Where the author's original page set something, it is kept and marked **(kept)**.
>
> ## Essence
> A **lone juniper on a ledge**: rooted where little else will grow, weathered, evergreen, still standing. The opening scene of the site is exactly this: dawn-rose sky resolving into deep marine blue over a cliff-edge tree.
>
> - **Name:** Juniper Collective. Descriptor: *Advisory & Portfolio Architecture* **(kept)**.
> - **Line:** *One vision. Every property. Open before you open.* **(kept)**
> - **Promise:** we hold the whole arc of a place: what it should become, for whom, how it reaches the world, and how it keeps its intent after the doors open.
> - **Doctrine:** The Juniper Method. One organizing thesis uniting spatial architecture, guest psychology and commercial strategy across every property **(kept)**.
>
> ## Voice
> Written in the author's *Essay / Self-Help* mode (`creative-writing/vault/CLAUDE.md`, in the Pipelines-Plugin repo): second person, present tense; **claim, then a concrete image, then the meaning stated outright, then a closing aphorism**.
>
> - Calm, exact, unhurried. Speaks to owners as peers. One image per idea.
> - Devices used: anaphoric triads, "Not X. Not Y." negation stacks (sparingly), one-line pivots ("That is the work, made visible."), named deliverables ("The Portfolio Thesis"), antithesis closers.
> - Vocabulary, one or two per page, never stacked: architecture, threshold, ledger, grammar, doctrine, stewardship, ground, arc, intent, node.
> - Never: emoji, exclamation marks, *world-class, bespoke, curated, unlock, leverage, seamless, elevate, cutting-edge, synergy, holistic*. "Journey" only in "guest journey".
> - No invented proof: no client names, testimonials, statistics, prices, durations, awards or headcounts exist on the site, because none were supplied.
>
> ## Colour
> | Token | Hex | Use |
> |---|---|---|
> | Fog | `#F6F0E6` | page **(kept as "fog white")** |
> | Paper | `#FBF8F2` | raised surfaces |
> | Ink | `#17261f` | body text (13.9:1 on fog) |
> | Ink 2 | `#4b564f` | secondary text (6.8:1) |
> | Juniper | `#3B5545` | brand green, buttons **(kept)** |
> | Juniper deep | `#243e2f` | hover, footer **(kept as "primary")** |
> | Marine | `#263F50` | headings **(kept)** |
> | Navy | `#12294a` | dusk: dark sections, the intro |
> | Rose | `#D6B4AD` | dawn accent **(kept as "morning red")** |
> | Olive | `#5c6235` | small labels on light (5.7:1) |
> | Alpine | `#7C8252` | decoration only, never text (3.6:1) |
>
> The old page set small labels in Alpine (3.6:1) and a footer note at 60% opacity (3.7:1); both fail WCAG AA for small text. Labels now use Olive.
>
> ## Type
> **Cormorant Garamond** for display and headings **(kept)**, **Manrope** for text **(kept)**. Display is semibold with tight leading; italics carry the aphorisms and the dawn-rose second line of the headline. Numerals are lining.
>
> ## Marks and icons
> Drawn for this site (`build/icons.py`), no third-party set. The mark is a pruned juniper on a rock ledge. Icons sit on a 24px grid with a 1.5px round-cap stroke, in `currentColor`, so they follow text colour.
>
> ## Imagery
> Photography only where reality matters (places, rooms, tables), generated with Higgsfield (see `IMAGERY.md`); everything diagrammatic is vector. Rules: **blue hour or first light; deep marine shadows, a trace of dusty rose, juniper greens; no people, no faces, no text or logos in frame; calm, still, unhurried.** Interfaces are built in HTML, not generated.
>

### Source file: docs/CONTENT-TO-CONFIRM.md

> # Content to confirm
>
> ## Added in round two (from the owner's answers and The Reserve's public pages)
> Facts taken from `thereserveathotsprings.com` (its history and press pages): the Brown House's age, 1919 remodel and 1986 National Register listing; twelve rooms across the Brown House, Legacy House and a cottage suite; four acres; opened summer 2021; Nathan McMurry as executive chef; the Travel + Leisure readers' ranking (No. 10 of fifteen favorite resorts in the South). **Confirm each is current, that you may cite it, and the ranking's year.**
>
> - **The founders' roles on the Reserve.** The site says Nathan and Katelyn were part of the family team that took the house on. It does not say what each did, or what Elijah did. `reserve.html` states only the public facts. Replace the three "what a place like this has to get right" cards with your own account when you can.
> - **Founder bios** are drawn from the owner's answers. Check wording, and the claim that Nathan is "known for holding a high standard at large catered events on tight budgets" (stated by Elijah from first-hand observation; no award is claimed).
> - **"Leads:" lines** on the collective page assign Elijah to brand and product design, systems and communications, and spatial curation; Katelyn to economics; Nathan to culinary and project coordination. These are inferred from the bios.
> - **Project size**, "under a million dollars to about five million", from the owner's answer. Used on the home, what-we-do and engagements pages.
> - **"We aim to reply the same day"**, from the operator brief. True only once the mailbox is monitored.
> - **Payments**: card accepted, retainers billed monthly (owner's answer). Stated on engagements and in the draft terms.
> - **"Our standard is simple: the value has to be on the table before we can build on it"** paraphrases the owner's account of who the firm declines.
> - **Portal.** The page now lists nine capabilities and six roles, as the owner specified, and states plainly that the portal is in development.
> - **"A bad plan" voice.** The home and what-we-do copy was rewritten in a warmer, outcome-first voice at the owner's direction. Anything that reads as a promise of results should be softened if counsel advises.
> - **Readiness check.** The questions, the scoring and the engagement recommendations are the firm's own tool and should reflect how you would really advise. Edit `assets/js/readiness.js`.
> - **Hero line.** The tagline "One vision. Every property. Open before you open." is kept from the original page.
>
> ## From the first round (still to confirm)
>
> The copy was drafted with the creative-writing tool from the facts on the original page (firm, offices, four phases, six steps, five specialties, three tiers, portal features, audience, confidentiality line). Everything below goes **beyond** those facts. It is plausible for the firm described, but it is the drafter's inference, not something the firm said. Confirm, correct or cut each item before the site is promoted.
>
> ## Process and deliverables
> - **What we do**, the "Likely deliverables" under each of the four phases (commercial ethos statement, property differentiation map, yield model, visual identity system, tiered guest segmentation, private interest list, editorial narrative, founder salon program, opening staging plan, operational ritual set, design governance retainer).
> - **How we work**, every "What you receive" and "What we ask of you" list for the six steps; the named deliverable "The Portfolio Thesis"; the statement that each step "leaves behind what the next needs".
> - **The collective** (`specialists.html`, formerly Specialists), the three bullets under each discipline; the three-step "how a pod is assembled" (read the engagement, seat the pod, open the line).
>
> ## Engagements
> - The fourth bullet on each tier: *a single point of contact who knows your property and its intent* (Advisory), *client portal access for the length of the project* (Project), *a standing relationship with the specialists who know your portfolio* (Retainer).
> - The "Best when" and "Not" sentences on each tier.
> - The whole comparison table except the Project scope cell and the "best for" row.
> - The FAQ answers: that engagements can move from one to another, that a single property can take Advisory or a Project, that scope and fees are discussed after the diagnostic session, that nothing is quoted on the site.
>
> ## Diagnostic and contact
> - What to bring (plans, pro formas, brand files, schedules, key contacts); what you leave with; the three steps (write, we read, we meet).
> - **Offices removed.** The original page listed Portland, New York and London. The owner said the firm is starting in Arkansas, so the site now says "Starting in Arkansas". Confirm no other office should appear.
>
> ## Portal
> - That access is issued through the engagement lead when an engagement begins, and that a client can ask by email to add a teammate.
> - The illustration's sample data (property one, two, three) is invented to show the layout, and is labelled as such on the page.
>
> ## Legal pages (drafts, not legal advice)
> - `terms.html` and `privacy.html` are plain-language drafts and say so. They need counsel before the site is promoted. The privacy page states what is true of the site as built (no cookies, no analytics, forms open the visitor's own email app, fonts load from Google, hosting on GitHub Pages). Update it if any of that changes.
>
> ## Kept from the original, check they are current
> - "Juniper Collective Advisory LLC" in the footer (the footer year is now 2026); the email `inquiries@junipercollective.co`, which does not deliver until the domain and mailbox exist (see `LAUNCH.md`).
>

### Source file: docs/DESIGN.md

> # Design record
>
> > **Status, 2026-11-19:** Historical record, kept as written on 2026-10-28 for the first redesign (#5). Current state: round two (#6) rewrote the copy around the founders, the Reserve and Arkansas, added Our work (`src/pages/reserve.html`), the readiness check and the diagnostic checklist, and renamed Specialists to The collective; the design system itself is unchanged. See `docs/OPEN-QUESTIONS.md` and `docs/LAUNCH.md` for what is open.
>
> How the redesign was reasoned, using the ui-design toolkit (`plugins/ui-design` in the Pipelines-Plugin repo). Nothing was persisted into that repo; commands were run read-only.
>
> ## Dissecting the original page
> | # | Finding | Catalog area | Now |
> |---|---|---|---|
> | 1 | No mobile navigation: the nav was `hidden lg:flex` with no menu button | ux / Navigation | Menu button, `aria-expanded`, Esc closes, focus returns |
> | 2 | Footer and "Terms", "Privacy" links went to `#`; "Enter Portal" and "Begin a diagnostic" went to sections of the same page | ux / Navigation | Every link leads to a real page |
> | 3 | The contact form faked success ("Request Received") and sent nothing | ux / Forms | Honest forms: they open the visitor's email app, and say so |
> | 4 | Small labels in Alpine green (3.6:1) and a 60%-opacity footer note (3.7:1) | ux / Accessibility (4.5:1) | Olive labels (5.7:1); footer text 7:1 or better |
> | 5 | Labels at 10-11px | Typography (12px floor) | Smallest label is 12px |
> | 6 | Icons from an icon font (Material Symbols), shown as ligature text until loaded | style / SVG icons | Inline SVG sprite, `aria-hidden` |
> | 7 | Tailwind from a CDN in production; images hot-linked from a third-party host, with no width or height | Performance (CLS, WebP, lazy) | Own CSS; local WebP with `srcset`, width and height, lazy below the fold |
> | 8 | No skip link, no visible focus style, no reduced-motion handling | ux / Accessibility | All three |
> | 9 | The portal "screenshot" was a generated picture of a UI | Honesty | A built, labelled illustration with sample data |
>
> ## Routing the brief
> `route.py "boutique hospitality advisory firm ... premium, calm, editorial, trustworthy, with a client portal" --stack html-tailwind` returned **AMBIGUOUS** and **CLOSE-CALL** between *Hotel/Hospitality* and *Luxury/Premium Brand*. I read both rows. Chosen: **Hotel/Hospitality** (it names the audience), borrowing *Luxury*'s storytelling landing pattern.
>
> - **Style:** Liquid Glass (primary row), with Minimalism & Swiss. Used for the header and the cards over photographs: translucent, blurred, with a solid fallback where `backdrop-filter` is unsupported.
> - **Pattern:** the catalog's "Hero + Testimonials + CTA" does not apply, because there are no testimonials and none were invented. The storytelling pattern is used instead (hook, chapters, climax call to action).
> - **Dials:** variance 4, motion 4, density 3 (spacious). Motion is a quiet reveal on scroll, switched off for reduced-motion.
> - **Not adopted:** the suggested navy and gold palette and the Playfair pairing. The author's own green, marine and rose, and Cormorant with Manrope, are the brand.
> - **Anti-patterns the catalog names for this product:** "poor photos", "complex booking". Photography is the main image budget; the only call to action is an email.
>
> ## Checks run
> Every page, at 1440px and 390px: no horizontal overflow, no broken images, one `h1`, no heading-level skips, every image has `alt`, every input has a label, no duplicate ids, every internal link and anchor resolves (`build/check_site.py`, which also gates the deploy). Interaction: mobile menu, form validation (including the correct-then-submit path), FAQ, the intro (first visit and returning visit).
>

### Source file: docs/IMAGERY.md

> # Imagery record
>
> Ten photographs generated with Higgsfield, model `gpt_image_2_5`, quality `high`, 2K, 2.75 credits each (27.5 in total). Exported to WebP in `assets/img/` at two widths. Prompts share one look: blue hour or first light, deep marine shadows, faint dusty rose, juniper greens, no people, no text.
>
> | File | Used on | Subject |
> |---|---|---|
> | hero-pavilion | home hero | timber and glass pavilion in conifers at blue hour |
> | cliff-juniper | closing call to action on home, What we do, How we work, The collective, Engagements, 404; social image (`og:image`) | the lone juniper above a sea of fog |
> | three-buildings | What we do | three buildings, one clearing: a portfolio |
> | scale-model | home, How we work, Begin a diagnostic | architect's model on a plinth |
> | kitchen | The collective | kitchen pass before service |
> | venue | The collective hero | empty venue before opening |
> | studio-table | How we work | swatches and sketches of a tree mark |
> | lodge-path | home, What we do | path to a lit lodge door |
> | dining-terrace | Engagements hero | set table at golden hour |
> | writing-desk | Contact, Begin a diagnostic | desk, notebook, juniper sprig at dawn |
>
> Where each photograph appears is read from the `{{photo:…}}` tokens in `src/pages/` (2026-11-19); Our work, the readiness check, the diagnostic checklist and the client portal use none.
>
> These are illustrations of an atmosphere, not photographs of real client properties, and should not be presented as such.
>

### Source file: docs/LAUNCH.md

> # Launch checklist
>
> The site is static and publishes to GitHub Pages from Actions. Going live on a real address takes about an hour, plus DNS waiting time. Do the steps in order.
>
> ## 1. Register the domain
> Register `junipercollective.co` (or the chosen domain) with any registrar. Use the LLC's legal name and a role email as the registrant. Turn on registrar lock and auto-renew.
>
> ## 2. Set up email on the domain (Google Workspace)
> 1. Create a Workspace account for the domain and verify ownership with the TXT record Google gives you.
> 2. Add the MX records Google gives you at the registrar. Remove any default MX records first.
> 3. Create the mailbox `inquiries@` and any aliases (`hello@`, `portal@`).
> 4. Add SPF (TXT) and DKIM (Workspace admin, Gmail, Authenticate email), then a DMARC TXT record: `_dmarc` with `v=DMARC1; p=none; rua=mailto:inquiries@<domain>`. Tighten `p=` after a few weeks of clean reports.
> 5. Send a test message in and out. Every form on the site opens a message to `inquiries@junipercollective.co`, so until this works, nothing a visitor writes arrives.
>
> ## 3. Point the domain at GitHub Pages
> In the registrar's DNS:
> - Apex (`junipercollective.co`): four `A` records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
> - `www`: a `CNAME` to `groot99-droid.github.io`.
>
> Then in the repository: Settings, Pages, Custom domain. Enter the domain, save, wait for the DNS check, and tick **Enforce HTTPS** once it appears.
>
> ## 4. Tell the site its new address
> Edit `src/site-url.txt` so it holds the new origin, for example `https://junipercollective.co` (no trailing slash). Run:
>
> ```
> python3 build/build.py
> python3 build/check_site.py
> ```
>
> Commit the rebuilt files. This updates canonical links, Open Graph tags and the sitemap. If the domain differs from `junipercollective.co`, also replace that address in `src/layout.html`, the page sources, `docs/` and the form code in `assets/js/site.js`.
>
> ## 5. Before announcing
> - [ ] Submit the sitemap in Google Search Console.
> - [ ] Have counsel review `terms.html` and `privacy.html`, then remove their "Draft" banners.
> - [ ] Settle or remove each item in `CONTENT-TO-CONFIRM.md`.
> - [ ] Add founder photos (`assets/img/team/`) and Reserve photos.
> - [ ] Confirm the Reserve may be named and the Travel + Leisure ranking is current.
> - [ ] Test every form from a phone: the email app should open addressed to the real mailbox.
> - [ ] Open the site in Safari and on an iPhone. The intro has only been tested in Chromium.
>
> ## What is not live
> The client portal, calendar booking, invoicing and e-signature do not exist yet. The pages say so. See `PORTAL-SPEC.md`.
>

### Source file: docs/OPEN-QUESTIONS.md

> # Open questions
>
> Questions the owner has not answered yet, kept so they can be settled later. Answer them in the two live briefs (answers save there and are read back from them), or tell Claude directly.
>
> - Round one: https://claude.ai/artifact/KcvHi9fw3Vb55a6iKBw7LH
> - Round two: https://claude.ai/artifact/PxTXeY4ipU1T6owjFomNED
>
> Answered items are not repeated here. Each question says what it unlocks.
>
> ## The firm and its story
> | Question | Unlocks |
> |---|---|
> | Tell the origin story in your own words, as if to one person across a table. (Round one's story answer was a fragment.) | An "Our story" section for the home and collective pages |
> | What exactly did each founder do on The Reserve at Hot Springs? | A sharper, accurate "who was there" section on `reserve.html` |
> | Who is Nathan's surname and title exactly as he wants it shown? The site currently uses "Nathan McMurry", from The Reserve's public pages. | Founder cards |
> | Photos of the three founders. Drop them at `assets/img/team/elijah.webp`, `katelyn.webp`, `nathan.webp` (square, 400 px or larger); the build picks them up. | Replaces the initials badges |
> | Photos and video of The Reserve you own. Add to `assets/img/reserve/` and tell Claude. | A gallery and hero on `reserve.html` |
> | Exact legal name and state of the LLC. The footer says "Juniper Collective Advisory LLC", copied from the original page. | Footer, terms, privacy |
>
> ## Clients and promise
> | Question | Unlocks |
> |---|---|
> | Describe your ideal client in two or three sentences. (Left blank twice.) | Home "who it is for" and the quiz wording |
> | What usually makes someone call you now rather than next year? | Home hook and the diagnostic page |
> | Describe a client you would turn away, and why. | A "who we are not for" line |
> | Which services do clients usually buy together? | Engagement bundles |
> | Finish this sentence: "Work with us and you will…" | The headline promise |
> | What do you refuse to promise? | An honest-limits line on engagements |
> | What do you call the thing you give clients instead of a smashed-together plan? | A named deliverable for the method |
> | Write the first line a visitor should read. | The hero headline, if it beats the current one |
> | Words to use; words and phrases never to use. | Voice rules in BRAND.md |
> | One real retreat or hospitality site whose writing you admire, and what it does well. | Voice calibration |
> | What goes above the fold: the Reserve, an outcome promise, a question, a story, or the founders' faces? | Home page order |
>
> ## Offer and money
> | Question | Unlocks |
> |---|---|
> | What fee ranges, if any, may be public? (Currently: discussed after the diagnostic.) | Engagements page |
> | Which project sizes do you decline? Under $1M to $5M is stated on the site. | Fit wording |
> | What do you give away in exchange for an email? Diagnostic checklist, field guide, readiness score and a sample decision log were chosen. Only the checklist and readiness check exist so far. | Field guide and sample decision log pages |
>
> ## Launch
> | Question | Unlocks |
> |---|---|
> | Which domain, and has it been registered? `junipercollective.co` was not registered when asked. | `docs/LAUNCH.md` steps 1 to 4 |
> | Social and professional profiles (links or handles). | Footer links, structured data |
> | Who will review Terms and Privacy, and when? | Removing the "Draft" banners |
> | Which of the items in `CONTENT-TO-CONFIRM.md` can you settle now? | Removing unconfirmed copy |
> | What is the single next thing to build after launch? (The portal was chosen.) | Roadmap |
>
> ## Portal (see PORTAL-SPEC.md)
> | Question | Unlocks |
> |---|---|
> | Who may see what? A role table per person type (owner, investor, designer, GM, lender, counsel). | Access rules |
> | Which payment provider, and is a card on file taken at signing or per invoice? | Billing design |
> | Which e-signature provider, or is a signed PDF by email acceptable at first? | Agreements |
> | Where may client documents be stored, and for how long are they retained? | Privacy page, hosting choice |
>

### Source file: docs/PORTAL-SPEC.md

> # Client portal: specification and build plan
>
> Status: not built. The public pages describe it and the illustration uses sample data. This document is the starting point for building it.
>
> ## What the owner asked for
> All of these, for every engagement: project status and milestones; read and approve decisions; open shared documents; book a session; message the team; see concept renders; pay invoices; sign agreements. Access for the founder or owner, investors, architects and designers, the general manager, lenders and legal counsel. Payment by card, with retainers billed monthly. Client information is commercially confidential.
>
> ## Why it needs a server
> The site is static, so it has no sign-in, no private storage and no way to take a payment. Everything above needs those. Client data must not go in the public repositories.
>
> ## Recommended shape
> Build it as a separate private application, not inside this repository.
>
> | Concern | Proposal | Why |
> |---|---|---|
> | Hosting | Railway (already used for other projects) | Managed Postgres, private networking, simple deploys |
> | App | One web app with server-rendered pages | Fewer moving parts to secure than a single-page app plus API |
> | Sign-in | Email magic link plus an optional passkey; invite-only | No passwords to leak; access is issued per person |
> | Roles | owner, investor, design, operations, lender, counsel, team | Per-person scopes, set per engagement |
> | Documents | Object storage, private, short-lived signed links | Never public URLs |
> | Decisions | Append-only log: proposal, approver, time, reasoning | The portal's core promise: what was decided stays decided |
> | Messages | Threads attached to a decision or document | Context stays with the thing discussed |
> | Booking | Google Calendar availability read from the firm's calendar | Already in use; avoids a second scheduler |
> | Payments | Stripe Checkout and Stripe Billing for monthly retainers | Cards and subscriptions without holding card data |
> | Signatures | A hosted e-signature provider | Legally recognized signing with an audit trail |
> | Renders | Uploaded images and video attached to a milestone | Reviewed and answered in the decision log |
>
> ## Security requirements before any real client data
> - Written data-handling terms in the engagement agreement, reviewed by counsel.
> - Every request authorised by role and engagement on the server, with tests for each role.
> - Audit log of who viewed or changed what.
> - Encrypted backups, tested restore, and a retention and deletion policy.
> - No client data in logs, analytics, or this repository.
> - A named person responsible for access requests and incidents.
>
> ## Phasing
> 1. **Record only.** Invite-only sign-in, one engagement view with milestones, a decision log and a document room.
> 2. **Conversation.** Message threads, concept renders, session booking.
> 3. **Money.** Invoices, card payments, monthly retainer billing, agreements to sign.
> 4. **Roles.** Investor, lender and counsel views with scoped access.
>
> ## Open decisions
> See `OPEN-QUESTIONS.md`, Portal section. The most urgent: who may see what, and which payment and signature providers.
>

## 12. Full commit log (date, hash, subject)

Every commit, oldest first. Merge commits are shown with their subjects.


### 2026-10

- 2026-10-28 cdab953a Initial commit
- 2026-10-28 47739134 Add Juniper Collective landing page
- 2026-10-28 df3ffc32 Merge pull request #1 from groot99-droid/claude/kind-dirac-im39ww [merge]
- 2026-10-28 9203f4f5 Deploy site to GitHub Pages from Actions (#2)
- 2026-10-28 66574d2a Add cinematic intro with music and ambience (#3)
- 2026-10-28 8aa1c833 Intro: 1.5x speed, zoom-out from the tree, ripple at full blue, 4s text, wind at 50% (#4)
- 2026-10-28 4a24092f Redesign the site: brand, copy, imagery and every linked page
- 2026-10-28 021580c6 Intro: pull the opening zoom back faster (done in 40% of the video, out-cubic)
- 2026-10-28 df63f43e Redesign the site: brand, copy, imagery and every linked page (#5)
- 2026-10-29 499a8f95 Round two: rewrite the site around the founders, the Reserve and Arkansas
- 2026-10-29 7af26748 Merge main (squash of earlier work); keep this branch's tree [merge]
- 2026-10-29 b6c298c6 Round two: rewrite the site around the founders, the Reserve and Arkansas (#6)

### 2026-11

- 2026-11-19 273ca617 docs: imagery table from the pages, Specialists is The collective, media folder as versioned, design record banner
- 2026-11-19 23bb6193 Merge pull request #7 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
