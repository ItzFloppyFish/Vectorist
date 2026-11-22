#!/usr/bin/env python3
"""
Vectorist pack builder. Local tool, never served to the browser.

    python3 tools/build.py <source_root>

<source_root> is a folder OUTSIDE this repo that holds each pack's original
folder (as named by "source" in tools/packs.json) and its cover image.
The originals are never copied into the repo.

For every pack this writes:
  assets/p/<slug>-<hash>.webp   one scrambled preview atlas (both styles)
  assets/p/<slug>-cover.jpg     the pack thumbnail, resized and flattened
and then regenerates js/catalog.js.

Protection model: previews are 256px (originals are 1150px), cut into 32px
blocks, shuffled across the whole atlas and rotated, so "save image" or the
network tab yields confetti. js/site.js reassembles them onto <canvas>.
This stops casual ripping. It does not stop a screenshot, and a determined
developer can read the JS. The real protection is that no clean, full-size,
transparent file ever leaves Payhip.
"""
import hashlib
import json
import os
import random
import sys
from pathlib import Path

from PIL import Image

TILE = 256   # preview size per icon
BLOCK = 32   # scramble block; multiple of 16 keeps blocks codec-aligned
M = 0xFFFFFFFF

ROOT = Path(__file__).resolve().parent.parent


def imul(a, b):
    return ((a & M) * (b & M)) & M


def mulberry32(seed):
    """Bit-identical to m32() in js/site.js. Returns uint32s."""
    state = seed & M

    def nxt():
        nonlocal state
        state = (state + 0x6D2B79F5) & M
        t = imul(state ^ (state >> 15), state | 1)
        t = ((t + imul(t ^ (t >> 7), t | 61)) & M) ^ t
        return (t ^ (t >> 14)) & M
    return nxt


def plan(n_blocks, seed):
    rnd = mulberry32(seed)
    perm = list(range(n_blocks))
    for i in range(n_blocks - 1, 0, -1):
        j = rnd() % (i + 1)
        perm[i], perm[j] = perm[j], perm[i]
    rots = [rnd() % 4 for _ in range(n_blocks)]
    return perm, rots


def find_icons(src):
    found = {}
    for p in src.rglob("*.png"):
        stem = p.stem
        for suffix, v in (("_no-outline", 1), ("_outline", 0)):
            if stem.endswith(suffix):
                ident = stem[: -len(suffix)]
                found.setdefault(ident, {"cat": p.parent.parent.name, "name": p.parent.name, "files": {}})
                found[ident]["files"][v] = p
                break
    return found


def build_pack(pack, src_root):
    src = src_root / pack["source"]
    if not src.is_dir():
        sys.exit(f"missing source folder: {src}")
    found = find_icons(src)
    order = pack.get("order") or sorted(found)
    missing = [i for i in order if i not in found or len(found[i]["files"]) != 2]
    extra = sorted(set(found) - set(order))
    if missing:
        sys.exit(f"{pack['slug']}: icons missing a file: {missing}")
    if extra:
        print(f"  note: not in 'order', appended: {extra}")
        order = order + extra

    n = len(order)
    per = (TILE // BLOCK) ** 2
    total = n * per
    cols = 1
    while cols * cols < total:
        cols += 1
    g = TILE // BLOCK
    out = ROOT / "assets" / "p"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob(f"{pack['slug']}-*.webp"):
        old.unlink()

    # One atlas per style so the outline set (shown first) loads on its own.
    atlases = []
    for v in (0, 1):
        seed = random.SystemRandom().randrange(1, 2**31)
        perm, rots = plan(total, seed)
        atlas = Image.new("RGBA", (cols * BLOCK, cols * BLOCK), (0, 0, 0, 0))
        for i, ident in enumerate(order):
            im = Image.open(found[ident]["files"][v]).convert("RGBA").resize((TILE, TILE), Image.LANCZOS)
            for by in range(g):
                for bx in range(g):
                    b = i * per + by * g + bx
                    blk = im.crop((bx * BLOCK, by * BLOCK, (bx + 1) * BLOCK, (by + 1) * BLOCK))
                    if rots[b]:
                        blk = blk.rotate(90 * rots[b])  # counter-clockwise
                    s = perm[b]
                    atlas.paste(blk, ((s % cols) * BLOCK, (s // cols) * BLOCK))
        tmp = out / "_tmp.webp"
        # Lossless on purpose: lossy WebP leaves a visible block grid after reassembly.
        atlas.save(tmp, "WEBP", lossless=True, quality=100, method=6, exact=True)
        h = hashlib.sha1(tmp.read_bytes()).hexdigest()[:10]
        name = f"{pack['slug']}-{h}.webp"
        tmp.rename(out / name)
        print(f"  atlas {name}  {(out / name).stat().st_size // 1024} KB")
        atlases.append({"src": f"assets/p/{name}", "seed": seed})

    cover = None
    if pack.get("cover") and (src_root / pack["cover"]).is_file():
        c = Image.open(src_root / pack["cover"]).convert("RGB")
        c.thumbnail((1280, 1280), Image.LANCZOS)
        cover = f"{pack['slug']}-cover.jpg"
        c.save(out / cover, "JPEG", quality=84, optimize=True, progressive=True)

    cats = pack["categories"]
    icons = [{"id": i, "name": found[i]["name"], "cat": found[i]["cat"]} for i in order]
    unknown = sorted({ic["cat"] for ic in icons} - set(cats))
    if unknown:
        cats = cats + unknown
    return {
        "slug": pack["slug"], "name": pack["name"], "version": pack["version"],
        "price": pack["price"], "currency": pack["currency"], "payhip": pack["payhip"],
        "sourcePx": pack["sourcePx"], "cover": f"assets/p/{cover}" if cover else None,
        "categories": cats, "icons": icons,
        "atlas": {"tile": TILE, "block": BLOCK, "cols": cols, "styles": atlases},
    }


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src_root = Path(sys.argv[1]).resolve()
    if ROOT in src_root.parents or src_root == ROOT:
        sys.exit("source_root must be outside the repo, or the originals get published")
    cfg = json.loads((ROOT / "tools" / "packs.json").read_text())
    built = []
    for pack in cfg["packs"]:
        print(pack["slug"])
        built.append(build_pack(pack, src_root))
    js = "/* Generated by tools/build.py. Do not edit by hand. */\nwindow.VX_CATALOG=" + json.dumps(
        {"packs": built}, separators=(",", ":")) + ";\n"
    with open(ROOT / "js" / "catalog.js", "w", newline="\n") as f:
        f.write(js)
    print("wrote js/catalog.js")


if __name__ == "__main__":
    main()
