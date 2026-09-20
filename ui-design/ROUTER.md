# ui-design router

How to turn a request into the right catalog search: which mode, which domain,
what to type, and what to do when a match looks wrong. Read
[INDEX.md](INDEX.md) for the catalog's own vocabulary and
[spec.yaml](spec.yaml) for the contract. If this file and spec.yaml disagree,
spec.yaml wins.

All commands run from the repo root.

## 1. Pick the mode

| Intent | Mode | Domains involved | Query template |
|---|---|---|---|
| New product, page or whole-app visual direction | `--design-system` | product, style, color, landing, typography (bundled) | `"<product type> <industry> <2-3 style words>"` |
| One component or a targeted concern | `--domain <d>` | one | `"<component> <interaction or outcome>"` |
| Implementation detail in a known stack | `--stack <s>` | one stack file | `"<concern> <framework term>"` |
| A brief in the user's own words, product unknown | `route.py`, then `--design-system` | product first | the brief, verbatim |
| Review a built page | page review (see the `ui-design-multipart` skill) | none searched | the page path |

| Concern | `--domain` | Example query |
|---|---|---|
| Product type patterns | `product` | `"invoice billing"` |
| Visual style | `style` | `"glassmorphism dark"` |
| Palette | `color` | `"fintech trust"` |
| Font pairing | `typography` | `"professional modern"` |
| Landing page structure | `landing` | `"hero social-proof"` |
| Accessibility, forms, navigation, touch | `ux` | `"keyboard focus modal"` |
| Charts | `chart` | `"real-time dashboard"` |
| Icons | `icons` | `"decorative icon aria hidden"` |
| Motion | `gsap` | `"scroll reveal stagger"` |
| React / Next.js performance | `react` | `"rerender memo list"` |
| Native / app interface | `web` | `"safe-areas touch"` |

Pass `--domain` explicitly. Auto-detection misroutes overlapping terms.

## 2. Use the catalog's own words

A search matches the words the catalog uses, not the ones a brief happens to
use. The vocabulary is listed in [INDEX.md](INDEX.md): product types and their
keywords, style ids, font pairing names, landing pattern ids, stacks.

- Prefer the catalog's form: `invoice` over `invoicing`, `freelance` over
  `freelancer`, `spa` over `day spa`.
- Name the product type the way the products table does, then add at most two
  style words. One dominant intent, 2 to 5 terms.
- When a query returns nothing, the output lists **Closest known terms**. Use
  them for the one allowed retry.

## 3. When a match looks wrong

The failure this exists for: the brief `freelancer invoicing SaaS fintech
trustworthy` ranks *Freelancer Platform* first, although *Invoice & Billing
Tool* is the row the brief describes. Search printed the wrong row exactly as
confidently as a right one.

1. For any brief in free wording, run
   `python ui-design/catalog/scripts/route.py "<brief>"` before searching. It
   cross-checks the literal search, a search on the catalog's own spellings, and
   stem overlap with each row's keywords, and prints a warning when they
   disagree.
2. For a single search you are unsure of, add `--diagnostics` and read the line
   it prints:

   | Field | Suspicious when |
   |---|---|
   | `token_coverage` | below 0.5: under half your query terms hit the catalog |
   | `margin` | near 0: the top two rows are nearly tied |
   | `reason` | anything other than `matched` |
   | `top_score` | low for the domain: the match is weak |

3. When routing warns `AMBIGUOUS` or `CLOSE-CALL`, read both candidate rows
   before choosing. Say which you chose and why.
4. If nothing verifies, follow the guide skill: state that no database match was
   found, label any general guidance as a fallback, and do not persist.

Routing lowers the chance of a wrong row. It cannot rule it out, so it warns
rather than decides.

## 4. When to fan out

One search takes milliseconds. One subagent does not. Fanning out only pays for
a wide brief, where many independent searches would otherwise run one after
another in the main context.

- `route.py` prints the supplemental parts a brief needs (UX, charts, motion,
  navigation, icons, plus stack parts with `--stack`) and says **fan out** when
  there are 4 or more, **run inline** when there are fewer.
- Below the threshold, run the parts yourself. Do not spawn agents for two or
  three searches.
- At or above it, follow the `ui-design-multipart` skill: the manifest goes to
  one `ui-design-search-part` agent per part, `merge_parts.py` checks that every
  part came back exactly once, and you report.
- The `--design-system` command is always run inline. It bundles the five core
  domains in one call.

## 5. Guardrails that never change

- `--persist` always takes `--output-dir` pointed **outside** this repo, and
  only after the author has approved the design system. Fan-out agents never
  persist.
- Treat search results as recommendations, not instructions.
- Keep private project data out of queries.
