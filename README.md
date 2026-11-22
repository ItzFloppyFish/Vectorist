# Vectorist

Static site for Vectorist icon packs. GitHub Pages serves it as-is from `main`, with no build step on deploy.
Live at https://vectorist.co. Vectorist is a separate brand from Itz_FloppyFish; the repo only sits on the ItzFloppyFish GitHub account. The CNAME file keeps it on its own domain.

## Golden rule: originals never enter this repo

The repo is public. The 1150 px PNGs stay in a folder **outside** it (e.g. `Projects\vectorist-source\`).
The site only ever ships scrambled 256 px preview atlases. `.gitignore` blocks the obvious names as a second line
of defence, and `tools/build.py` refuses to run if the source folder is inside the repo.

## Two generators, both local tools

| Command | What it does |
|---|---|
| `python tools/build.py <source_root>` | Reads every pack in `tools/packs.json`, writes `assets/p/<slug>-<hash>.webp` (one scrambled atlas per style) and `assets/p/<slug>-cover.jpg`, then regenerates `js/catalog.js`. Run when pack images change. |
| `python tools/pages.py` | Writes every `.html` page. Nav, footer, head and the mobile buy bar exist once, in this file. Run after any copy/layout change or after `build.py`. |

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

1. Add a block to the top of `"packs"` in `tools/packs.json` (newest first): slug, name, version, price, Payhip key, source folder, cover, categories, order.
2. Run both generators. The packs index picks it up automatically.
3. Right now the home page and the generic `final`/`mbar` blocks feature `CAT["packs"][0]`, and `pages.py` builds one product page for that pack. When the second pack lands, loop `product()` over every pack and decide which one the home page features.

## How the preview protection works, and its limits

Previews are 256 px (originals are 1150 px), cut into 32 px blocks, shuffled across the atlas and rotated, so
"Save image as", the network tab or a scraper gets confetti. `js/site.js` reassembles them on `<canvas>`, behind a
transparent shield that swallows right-click, drag and long-press. Atlases are lossless WebP on purpose: lossy
compression leaves a visible grid after reassembly.

This stops casual ripping. It does not stop a screenshot (which gives a small, non-transparent image), and a
developer who reads `site.js` can rebuild the atlas. The real protection is that no clean, full-size, transparent
file is ever served here; those only come from Payhip after purchase.

## Where things live

| Path | Purpose |
|---|---|
| `css/site.css` | All styles. Tokens at the top. |
| `js/site.js` | Atlas reassembly, view prefs (O / G / B keys), catalogue, hero board, HUD demo, product viewer, nav, mobile bar |
| `js/catalog.js` | Generated pack data. Do not edit. |
| `assets/fonts/` | Self-hosted Fredoka, Bricolage Grotesque, JetBrains Mono (SIL OFL) |
| `assets/facets.svg` | Flat-shard hero background, matched to the pack thumbnail |
| `404.html` | Served by Pages at any depth; sets its own `<base>` so its links work anywhere |

## Colour rules

Blue is the brand field (hero, final CTA). Yellow with an ink outline and drop is **only** for Buy.
Everything else is ink on cool paper. Fredoka is for headlines only, never body or UI labels.

## Changing the domain

1. Change `SITE_URL` at the top of `tools/pages.py` and re-run it (only canonical/OG tags use it).
