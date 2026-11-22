# Vectorist

Static site for Vectorist icon packs, live at https://vectorist.co. GitHub Pages serves it as-is from `main`,
with no build step on deploy. Vectorist is a separate brand from Itz_FloppyFish; the repo only sits on the
ItzFloppyFish GitHub account. The `CNAME` file keeps it on its own domain.

## Golden rule: originals never enter this repo

The repo is public. The 1150 px PNGs stay in a folder **outside** it (e.g. `Projects\vectorist-source\`).
The site only ever ships scrambled 256 px preview atlases. `.gitignore` blocks the obvious names as a second line
of defence, and `tools/build.py` refuses to run if the source folder is inside the repo.

## Two generators, both local tools

| Command | What it does |
|---|---|
| `python tools/build.py <source_root>` | Reads every pack in `tools/packs.json`, writes `assets/p/<slug>-<hash>.webp` (one scrambled atlas per style) and `assets/p/<slug>-cover.jpg`, then regenerates `js/catalog.js`. Run when pack images change. |
| `python tools/pages.py` | Writes every `.html` page, including one product page per pack. Nav, footer, head and the mobile buy bar exist once, in this file. Pack copy (`blurb`, `description`) comes from `tools/packs.json`. Run after any copy/layout change or after `build.py`. |

Edit `tools/pages.py`, **never** the generated HTML. Pillow is the only dependency (`pip install pillow`).

`<source_root>` holds each pack's original folder (named by `"source"` in `packs.json`) plus its cover image:

```
vectorist-source/
  Essential_Icon_Pack_V1/          <- the unzipped pack, as delivered on Payhip
  EssentialIconPackMainLogo.png    <- the thumbnail
```

## Adding icons to an existing pack

1. Drop the new PNGs into the source folder (same `<Category>/<Name>/<id>_outline.png` + `_no-outline.png` layout).
2. Add the new ids to that pack's `"order"` list in `tools/packs.json` (anything missing is appended at the end).
3. `python tools/build.py ..\vectorist-source` then `python tools/pages.py`, commit, push.

## Adding a new pack

1. Add a block to the top of `"packs"` in `tools/packs.json` (newest first): slug, name, blurb, description, version, price, Payhip key, source folder, cover, categories, order.
2. Run both generators. The home page, packs index, footer and a new `packs/<slug>/` page all pick it up.
3. `js/site.js` currently previews `VX_CATALOG.packs[0]` only (hero board, in-game demo, product wall). When a second pack lands, make the product wall read the pack slug from the page so each product page shows its own icons.

## How the preview protection works, and its limits

Previews are 256 px (originals are 1150 px), cut into 32 px blocks, shuffled across the atlas and rotated, so
"Save image as", the network tab or a scraper gets confetti. `js/site.js` reassembles them on `<canvas>`, behind a
transparent shield that swallows right-click, drag and long-press. Atlases are lossless WebP on purpose: lossy
compression leaves a visible grid after reassembly.

On product pages every icon also has a VECTORIST watermark drawn into the canvas pixels (clipped to the icon),
so it survives screenshots and deleting CSS. There is no close-up viewer by design.

This stops casual ripping. It does not stop a screenshot (which gives a small, non-transparent image), and a
developer who reads `site.js` can rebuild the atlas. The real protection is that no clean, full-size, transparent
file is ever served here; those only come from Payhip after purchase.

## Where things live

| Path | Purpose |
|---|---|
| `css/site.css` | All styles. Tokens at the top. |
| `js/site.js` | Atlas reassembly, watermark, outline/no-outline switch, hero board, in-game demo, product wall, nav, mobile bar |
| `js/catalog.js` | Generated pack data. Do not edit. |
| `assets/fonts/` | Self-hosted Fredoka and Bricolage Grotesque (SIL OFL) |
| `terms/` | Terms of Service. `licence/` is a redirect to it, kept because the old URL may be linked from Payhip. |
| `assets/facets.svg` | Flat-shard hero background, matched to the pack thumbnail |
| `404.html` | Served by Pages at any depth; `<base href="/">` keeps its links pointing at the site root |

## Colour rules

Blue is the brand field (hero, final CTA). The yellow button is the one primary action per view
(Explore packs on brand pages, Buy on product pages). Everything else is ink on cool paper.
Fredoka is for headlines only. No small uppercase labels, section numbers or kicker text.

## Changing the domain

1. Update `CNAME` and point DNS at GitHub Pages.
2. Change `SITE_URL` at the top of `tools/pages.py` and re-run it (only canonical/OG tags use it).
