#!/usr/bin/env python3
"""
Vectorist page builder. Local tool, never served to the browser.

    python3 tools/pages.py

Writes every HTML page from the templates below. Nav, footer, head and the
mobile buy bar exist ONCE here, so a nav change is one edit, not five.
Edit this file, never the generated .html files.

Run tools/build.py first when pack images change (it writes js/catalog.js,
which this script reads for the product page's category list).
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Site settings
# ---------------------------------------------------------------------------
# Public URL, used only for canonical and social-share tags. Links are relative.
SITE_URL = "https://vectorist.co/"
LOGIN = "https://payhip.com/auth/login"

CAT = json.loads(re.search(r"=(\{.*\});", (ROOT / "js" / "catalog.js").read_text()).group(1))
PACK = CAT["packs"][0]
BUY = f"https://payhip.com/buy?link={PACK['payhip']}"
PAYHIP_PAGE = f"https://payhip.com/b/{PACK['payhip']}"
PRICE = PACK["price"]
N = len(PACK["icons"])

VER = hashlib.sha1(b"".join((ROOT / p).read_bytes() for p in ("css/site.css", "js/site.js", "js/catalog.js"))).hexdigest()[:8]

# ---------------------------------------------------------------------------
# Small SVGs
# ---------------------------------------------------------------------------
I_USER = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></svg>'
I_MENU = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
I_ARR = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
I_L = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>'
I_R = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>'
I_YES = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#18A957" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
I_NO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#E5484D" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
I_CHK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
I_PLUS = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>'


def art(icon, cls="", style=""):
    c = f"art {cls}".strip()
    st = f' style="{style}"' if style else ""
    return f'<div class="{c}" data-icon="{icon}"{st}></div>'


def buy_btn(label="Get the pack", size="btn-lg"):
    return f'<a class="btn btn-buy {size}" href="{BUY}">{label} <span class="p">{PRICE}</span></a>'


# ---------------------------------------------------------------------------
# Chrome
# ---------------------------------------------------------------------------
HEAD = """<!DOCTYPE html>
<html lang="en" data-style="outline" data-guides="off" data-bd="paper">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Vectorist">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}assets/p/{slug}-cover.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2350FF">
{robots}<link rel="icon" href="{R}assets/mark.svg" type="image/svg+xml">
<link rel="preload" href="{R}assets/fonts/fredoka-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{R}assets/fonts/bricolage-grotesque-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{R}css/site.css?v={ver}">
<script>try{{var s=localStorage.getItem('vx.style'),b=localStorage.getItem('vx.bd'),h=document.documentElement;if(s==='plain')h.setAttribute('data-style','plain');if(b)h.setAttribute('data-bd',b)}}catch(e){{}}</script>
</head>
<body class="{bodycls}">
"""


def nav(R, cur):
    def a(href, label, key):
        ac = ' aria-current="page"' if key == cur else ""
        return f'<a href="{href}"{ac}>{label}</a>'
    home = R or "./"
    return f"""<header class="nav">
  <div class="wrap">
    <a class="logo" href="{home}"><img src="{R}assets/mark.svg" alt="" width="34" height="34">Vectorist</a>
    <nav class="nav-links" aria-label="Main">
      {a(R + "packs/", "Packs", "packs")}
      {a(home + "#catalogue", "Catalogue", "-")}
      {a(home + "#in-game", "In-game", "-")}
      {a(R + "licence/", "Licence", "licence")}
      {a(home + "#faq", "FAQ", "-")}
    </nav>
    <div class="nav-r">
      <a class="icon-btn dl" href="{LOGIN}" title="My downloads" aria-label="My downloads">{I_USER}</a>
      {buy_btn("Get the pack", "btn-sm")}
      <button class="icon-btn burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="sheet">{I_MENU}</button>
    </div>
  </div>
</header>
<div class="sheet" id="sheet">
  <a href="{R}packs/">Packs {I_ARR}</a>
  <a href="{home}#catalogue">Catalogue {I_ARR}</a>
  <a href="{home}#in-game">In-game preview {I_ARR}</a>
  <a href="{R}licence/">Licence {I_ARR}</a>
  <a href="{home}#faq">FAQ {I_ARR}</a>
  <hr>
  <a href="{LOGIN}">My downloads {I_USER}</a>
</div>
"""


def foot(R):
    home = R or "./"
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="brand">
      <a class="logo" href="{home}"><img src="{R}assets/mark.svg" alt="" width="34" height="34">Vectorist</a>
      <p>Hand-made icon packs for Roblox and every other engine.<br>Icons drawn by Magma. No AI.</p>
    </div>
    <div>
      <h4 class="mono">Shop</h4>
      <ul>
        <li><a href="{R}packs/">All packs</a></li>
        <li><a href="{R}packs/{PACK['slug']}/">{PACK['name']}</a></li>
        <li><a href="{LOGIN}">My downloads</a></li>
      </ul>
    </div>
    <div>
      <h4 class="mono">Help</h4>
      <ul>
        <li><a href="{R}licence/">Licence</a></li>
        <li><a href="{home}#faq">FAQ</a></li>
        <li><a href="{home}#how">How updates work</a></li>
      </ul>
    </div>
  </div>
  <div class="foot-b"><div class="wrap"><span>&copy; 2026 Vectorist. All icons are the property of their creator.</span><span>Checkout and downloads by Payhip.</span></div></div>
</footer>
"""


def mbar(after, hide):
    return f"""<div class="mbar" data-after="{after}" data-hide="{hide}">
  <div class="t"><b>{PACK['name']}</b><span>{N} icons &middot; free updates</span></div>
  {buy_btn("Get it", "btn-sm")}
</div>
"""


def page(path, R, title, desc, body, cur="", plain=True, after=None, hide=".final", ogtype="website", noindex=False, extra_head=""):
    url = SITE_URL + path.replace("index.html", "")
    h = HEAD.format(title=title, desc=desc, url=url, site=SITE_URL, slug=PACK["slug"], R=R, ver=VER,
                    bodycls="page-plain" if plain else "", ogtype=ogtype,
                    robots=('<meta name="robots" content="noindex">\n' if noindex else "") + extra_head)
    out = h + nav(R, cur) + "<main>\n" + body + "\n</main>\n" + foot(R)
    if after:
        out += mbar(after, hide)
    out += f'<script src="{R}js/catalog.js?v={VER}"></script>\n<script src="{R}js/site.js?v={VER}"></script>\n</body>\n</html>\n'
    out = re.sub(r"[ \t]+\n", "\n", out)
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", newline="\n") as f:
        f.write(out)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Shared blocks
# ---------------------------------------------------------------------------
def toolbar(cat_chips=True):
    return f"""<div class="seg" role="group" aria-label="Icon style">
        <button type="button" data-set-style="outline" aria-pressed="true">Outline <kbd>O</kbd></button>
        <button type="button" data-set-style="plain" aria-pressed="false">No outline <kbd>O</kbd></button>
      </div>
      <button class="tgl" type="button" data-toggle="guides" aria-pressed="false"><span class="sw"></span>Padding guides <kbd>G</kbd></button>
      <div class="bd" role="group" aria-label="Backdrop">
        <span>Backdrop</span>
        <button type="button" data-set-bd="paper" style="background:#fff" aria-label="Light backdrop"></button>
        <button type="button" data-set-bd="night" style="background:#151C48" aria-label="Dark backdrop"></button>
        <button type="button" data-set-bd="sky" style="background:#3B6BFF" aria-label="Blue backdrop"></button>
        <kbd>B</kbd>
      </div>""" + ('\n      <div class="chips" role="group" aria-label="Filter by category"></div>' if cat_chips else "")


def licence_block(R, num):
    return f"""<section class="sec" id="licence-summary">
  <div class="wrap">
    <div class="sec-h rv">
      <div>
        <div class="sec-k mono"><b>{num}</b>Licence</div>
        <h2 class="d d-l ex-ink">The licence, <em>in plain English.</em></h2>
      </div>
      <a class="btn btn-line" href="{R}licence/">Read the full licence {I_ARR}</a>
    </div>
    <div class="lic rv">
      <div>
        <h3>{art("padlock-unlocked")}You can</h3>
        <ul>
          <li>{I_YES}<span>Use the icons in your own games, on Roblox or any other engine.</span></li>
          <li>{I_YES}<span>Use the outline and no-outline versions together however you like.</span></li>
          <li>{I_YES}<span>Get every future update to the pack at no extra cost.</span></li>
        </ul>
      </div>
      <div class="no">
        <h3>{art("padlock-locked")}You can&rsquo;t</h3>
        <ul>
          <li>{I_NO}<span>Re-upload the icons anywhere, including the Roblox Creator Store.</span></li>
          <li>{I_NO}<span>Resell them, alone or bundled into another pack, kit or template.</span></li>
          <li>{I_NO}<span>Share or redistribute the files, free or paid.</span></li>
        </ul>
      </div>
    </div>
  </div>
</section>
"""


FAQS = [
    ("What do I get?",
     f"One ZIP with {N * 2} transparent PNGs: {N} icons, each in an outline and a no-outline version, at "
     f"{PACK['sourcePx']} &times; {PACK['sourcePx']} px. Every icon sits on the same centred padding."),
    ("Are these vector (SVG) files?",
     "No. They&rsquo;re high-resolution PNGs, which is the format Roblox uses for image assets. At 1150 px they "
     "scale down cleanly to any button or HUD size."),
    ("Can I use them outside Roblox?",
     "Yes. They&rsquo;re standard transparent PNGs, so they work in Unity, Godot, Unreal, GameMaker or a web game. "
     "The licence covers your own projects on any platform."),
    ("How do updates work?",
     "Buy once and every update to the pack is included. Re-insert the model from your Roblox inventory to get "
     "the latest version, or download the ZIP again from your Payhip account."),
    ("Where&rsquo;s my download?",
     f"Payhip emails your download link straight after checkout. You can also <a href=\"{LOGIN}\">sign in to Payhip</a> "
     "with the same email to download it again at any time."),
]


def faq_block(num):
    items = "\n".join(
        f'      <details><summary>{q}<span class="pm">{I_PLUS}</span></summary><p>{a}</p></details>' for q, a in FAQS)
    return f"""<section class="sec" id="faq">
  <div class="wrap">
    <div class="faq-l rv">
    <div class="sec-h"><div><div class="sec-k mono"><b>{num}</b>FAQ</div><h2 class="d d-l ex-ink">Questions, <em>answered.</em></h2><p class="lede">Anything else, ask through the <a href="{PAYHIP_PAGE}" style="color:var(--blue);text-decoration:underline;text-underline-offset:3px">pack&rsquo;s Payhip page</a>.</p></div></div>
    <div class="faq">
{items}
    </div>
    </div>
  </div>
</section>
"""


def final_block():
    return f"""<section class="final">
  <div class="wrap">
    <div>
      <h2 class="d d-l"><span class="ex-w">One payment.</span><br><span class="ex-y">Every future icon.</span></h2>
      <p class="price">{PRICE} {PACK['currency']} &middot; instant download &middot; free updates</p>
      <div class="row" style="margin-top:28px">{buy_btn()}</div>
    </div>
    <div class="final-art" aria-hidden="true">{art("star")}{art("chest-open-gems")}{art("trophy")}</div>
  </div>
</section>
"""


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------
def home():
    R = ""
    ghosts = "".join(art(i, "", s) for i, s in [
        ("sword", "left:-3%;top:20%;width:150px;transform:rotate(-12deg)"),
        ("paw-print", "left:3%;bottom:14%;width:110px;transform:rotate(14deg)"),
        ("timer", "left:44%;bottom:-3%;width:150px"),
        ("spin-wheel", "right:-5%;bottom:-6%;width:190px"),
    ])
    smalls = [("coin", "Coin"), ("potion", "Potion"), ("flame", "Flame"), ("trophy", "Trophy"), ("gem", "Gem")]
    small_html = "\n".join(
        f'        <div class="spec">{art(i)}<div class="lab mono"><span>{n}</span><span>0{k + 2}</span></div></div>'
        for k, (i, n) in enumerate(smalls))
    hud_l = [("shop", "c-y", "Shop", ""), ("egg", "c-p", "Hatch", ""), ("backpack", "c-g", "Items", ""),
             ("trade", "c-v", "Trade", ""), ("index", "c-b", "Index", ""), ("friends", "c-o", "Invite", "")]
    hud_r = [("quest-scroll", "c-o", "Quests", ""), ("rebirth", "c-p", "Rebirth", "rebirth"),
             ("spin-wheel", "c-b", "Spin", "wheel"), ("calendar", "c-g", "Daily", ""),
             ("present", "c-y", "Gifts", ""), ("settings", "c-v", "Settings", "cog")]

    def gbs(lst):
        out = []
        for i, c, lab, spin in lst:
            sp = f' data-spin="{spin}"' if spin else ""
            out.append(f'<button class="gb{" spin" if spin else ""}" type="button"{sp} tabindex="-1"><span class="k {c}">{art(i)}</span><span>{lab}</span></button>')
        return "\n          ".join(out)

    body = f"""<section class="hero" id="hero">
  <div class="hero-ghosts" aria-hidden="true">{ghosts}</div>
  <div class="wrap hero-grid">
    <div>
      <a class="eyebrow mono" href="packs/{PACK['slug']}/"><b>NEW</b>{PACK['name']} &middot; {PACK['version']}</a>
      <h1 class="d d-xl"><span class="ex-w">Hand-made</span><span class="ex-y">game icons.</span></h1>
      <p class="hero-sub">{N} glossy cartoon icons for Roblox and any other engine. Coins, chests, rebirths, pets and the rest, each in two styles that swap without moving a pixel. <strong>Drawn by Magma, no AI.</strong></p>
      <div class="hero-cta">
        {buy_btn()}
        <a class="btn btn-ghost btn-lg" href="#catalogue">See all {N} icons</a>
      </div>
      <p class="hero-note mono">Instant download<i>/</i>Free updates<i>/</i>Pay once</p>
    </div>
    <div class="board" aria-label="Icon previews">
      <div class="spec big">{art("chest-open-coins")}<div class="lab mono"><span>Chest Open (Coins)</span><span>01</span></div></div>
{small_html}
    </div>
  </div>
  <div class="specbar-o">
    <div class="wrap specbar">
      <div><b>{N}</b><span class="mono">Icons</span></div>
      <div><b>{N * 2}</b><span class="mono">PNG files</span></div>
      <div><b>2</b><span class="mono">Styles, zero shift</span></div>
      <div><b>{PACK['sourcePx']}px</b><span class="mono">Transparent source</span></div>
      <div><b>Free</b><span class="mono">Updates, forever</span></div>
    </div>
  </div>
</section>

<section class="sec" id="catalogue">
  <div class="wrap">
    <div class="sec-h rv">
      <div>
        <div class="sec-k mono"><b>01</b>Catalogue</div>
        <h2 class="d d-l ex-ink">Every icon, <em>both styles.</em></h2>
        <p class="lede">Every icon sits on the same centred padding, so they line up in buttons and grids. Switch the style or turn on the guides to check.</p>
      </div>
      <a class="btn btn-line" href="packs/{PACK['slug']}/">Open the pack page {I_ARR}</a>
    </div>
    <div data-catalogue data-href="packs/{PACK['slug']}/">
      <div class="toolbar">
      {toolbar()}
      </div>
      <div class="grid" aria-live="polite"></div>
      <div class="grid-empty" hidden>Nothing in this category yet.</div>
    </div>
  </div>
</section>

<section class="sec night" id="in-game">
  <div class="wrap hud-wrap">
    <div class="rv">
      <div class="sec-k mono"><b>02</b>In-game</div>
      <h2 class="d d-l ex-ink">Made for a <em>real HUD.</em></h2>
      <p class="lede">Built for the buttons players press hundreds of times a session. Try it: open the chest.</p>
      <ul class="ticks">
        <li>{art("padlock-unlocked")}<span>Centred on one grid, so icons drop into buttons without nudging.</span></li>
        <li>{art("trade")}<span>Both styles share the same footprint. Swap them and nothing moves.</span></li>
        <li>{art("rebirth")}<span>Re-insert the model from your inventory to pull in new icons.</span></li>
      </ul>
      <div class="seg" role="group" aria-label="Icon style">
        <button type="button" data-set-style="outline" aria-pressed="true">Outline <kbd>O</kbd></button>
        <button type="button" data-set-style="plain" aria-pressed="false">No outline <kbd>O</kbd></button>
      </div>
    </div>
    <div class="rv">
      <div class="hud-frame">
        <div class="hud">
          <svg class="hud-scene" viewBox="0 0 800 500" preserveAspectRatio="none" aria-hidden="true">
            <rect width="800" height="500" fill="#7CCBFF"/>
            <rect y="0" width="800" height="150" fill="#6BC0FB"/>
            <circle cx="640" cy="120" r="46" fill="#FFF3B0"/>
            <g fill="#fff"><ellipse cx="200" cy="110" rx="70" ry="22"/><ellipse cx="240" cy="96" rx="44" ry="26"/><ellipse cx="520" cy="70" rx="56" ry="16"/><ellipse cx="548" cy="60" rx="30" ry="18"/></g>
            <path d="M0 330 L120 250 L230 310 L360 230 L470 300 L600 240 L800 320 L800 500 L0 500Z" fill="#59C46B"/>
            <path d="M0 380 L160 330 L330 370 L520 320 L700 360 L800 340 L800 500 L0 500Z" fill="#46AE57"/>
            <path d="M0 440 L800 420 L800 500 L0 500Z" fill="#3C9A4C"/>
            <path d="M330 500 L380 380 L420 380 L470 500Z" fill="#E8C98A"/>
          </svg>
          <div class="hud-cur">
            <div class="pill">{art("coin")}<span data-count="coin">12,480</span></div>
            <div class="pill">{art("gem")}<span>342</span></div>
          </div>
          <div class="hud-boost">
            <div class="boost">{art("flame")}<i>2x</i><b data-timer="754">12:34</b></div>
            <div class="boost">{art("lightning-bolt")}<b data-timer="299">4:59</b></div>
            <div class="boost">{art("luck-clover")}<i>x3</i><b data-timer="1460">24:20</b></div>
          </div>
          <div class="hud-col l">
          {gbs(hud_l)}
          </div>
          <div class="hud-col r">
          {gbs(hud_r)}
          </div>
          <button class="hud-chest" type="button" aria-label="Open the chest"><span class="tip">Open me!</span>{art("chest-closed")}</button>
          <div class="hud-toast d ex-y" aria-hidden="true">+250</div>
        </div>
      </div>
      <p class="hud-try mono">Interactive: tap the chest, wheel, rebirth or cog</p>
    </div>
  </div>
</section>

<section class="sec" id="how">
  <div class="wrap">
    <div class="sec-h rv"><div><div class="sec-k mono"><b>03</b>How it works</div><h2 class="d d-l ex-ink">Buy once. <em>Keep getting icons.</em></h2></div></div>
    <div class="steps rv">
      <div class="step">{art("present")}<span class="n mono">Step 1</span><h3>Buy on Payhip</h3><p>One payment of {PRICE} {PACK['currency']}. Payhip handles checkout and emails your download link straight away.</p></div>
      <div class="step">{art("backpack")}<span class="n mono">Step 2</span><h3>Drop them in</h3><p>Unzip {N * 2} transparent PNGs, or insert the model into Roblox Studio and start wiring up buttons.</p></div>
      <div class="step">{art("rebirth")}<span class="n mono">Step 3</span><h3>Get every update</h3><p>New icons are added to the same pack. Re-insert the model from your inventory to get them, at no extra cost.</p></div>
    </div>
  </div>
</section>

{licence_block(R, "04")}
{faq_block("05")}
{final_block()}"""
    page("index.html", R, "Vectorist | Hand-made game icons for Roblox",
         f"{N} hand-made glossy cartoon icons for Roblox and any game engine. Outline and no-outline styles, "
         f"transparent PNG, free updates. {PRICE}.",
         body, plain=False, after="#hero")


# ---------------------------------------------------------------------------
# Packs index
# ---------------------------------------------------------------------------
def packs():
    R = "../"
    cards = []
    for i, p in enumerate(CAT["packs"]):
        new = '<span class="new">NEW</span>' if i == 0 else ""
        cards.append(f"""      <a class="pack" href="{p['slug']}/">
        <div class="cv">{new}<img src="{R}{p['cover']}" alt="{p['name']} cover" width="1280" height="720" loading="lazy" draggable="false"></div>
        <div class="bd2">
          <h3>{p['name']}</h3>
          <span class="meta mono">{p['version']} &middot; {len(p['icons'])} icons &middot; {len(p['icons']) * 2} files</span>
          <div class="row"><span class="pr">{p['price']}</span><span class="btn btn-line btn-sm">View pack {I_ARR}</span></div>
        </div>
      </a>""")
    body = f"""<section class="ph">
  <div class="wrap">
    <div class="sec-k mono"><b>{len(CAT['packs'])}</b>{"Pack" if len(CAT['packs']) == 1 else "Packs"}</div>
    <h1 class="d d-l ex-ink">The <em>packs.</em></h1>
    <p class="lede">Hand-made icon packs for game UI. Every pack is a one-time purchase with free updates.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="packs">
{chr(10).join(cards)}
      <div class="pack soon">
        {art("egg")}
        <h3>More packs are on the way</h3>
        <p>The Essential pack keeps growing too. Buy it once and new icons arrive free.</p>
      </div>
    </div>
  </div>
</section>"""
    page("packs/index.html", R, "Packs | Vectorist",
         "Hand-made icon packs for Roblox and any game engine. One-time purchase, free updates.", body, cur="packs")


# ---------------------------------------------------------------------------
# Product page
# ---------------------------------------------------------------------------
def product():
    R = "../../"
    p = PACK
    rows = []
    for c in p["categories"]:
        ics = [ic for ic in p["icons"] if ic["cat"] == c]
        if not ics:
            continue
        links = "".join(f'<a href="#{ic["id"]}" title="{ic["name"]}" aria-label="{ic["name"]}">{art(ic["id"])}</a>' for ic in ics)
        rows.append(f'      <div class="cat"><h3>{c}<small class="mono">{len(ics)} icon{"s" if len(ics) != 1 else ""}</small></h3><div class="icons">{links}</div></div>')
    body = f"""<section class="ph" style="padding-bottom:28px">
  <div class="wrap"><nav class="crumb mono" aria-label="Breadcrumb"><a href="../">Packs</a><span>/</span><span>{p['name']}</span></nav></div>
</section>
<section>
  <div class="wrap pp">
    <div class="viewer">
      <div class="stage">
        <div class="stage-top mono"><b data-v="name">&nbsp;</b><span data-v="meta"></span></div>
        <div class="pad">{art(p['icons'][0]['id'])}</div>
        <div class="stage-bot mono"><span>Preview &middot; {p['sourcePx']}px in pack</span>
          <div class="stage-nav"><button type="button" data-v="prev" aria-label="Previous icon">{I_L}</button><button type="button" data-v="next" aria-label="Next icon">{I_R}</button></div>
        </div>
      </div>
      <div class="vtools">
      {toolbar(False)}
      </div>
      <div class="strip" aria-label="All icons"></div>
    </div>
    <aside class="buy">
      <span class="mono" style="color:var(--ink-3)">{p['version']} &middot; {len(p['icons'])} icons &middot; {len(p['icons']) * 2} files</span>
      <h1 class="d d-l ex-ink">Essential <em>Icon Pack</em></h1>
      <p style="color:var(--ink-2)">Your everyday icon pack for Roblox games. Hand-made by Magma, no AI.</p>
      <div class="pr"><b>{p['price']}</b><span class="mono">{p['currency']} &middot; one-time</span></div>
      {buy_btn("Get the pack")}
      <ul>
        <li>{I_CHK}<span>{len(p['icons'])} icons, each with an outline and a no-outline version</span></li>
        <li>{I_CHK}<span>{p['sourcePx']} &times; {p['sourcePx']} px transparent PNGs</span></li>
        <li>{I_CHK}<span>Same centred padding on every icon, so they line up in buttons and grids</span></li>
        <li>{I_CHK}<span>Both styles sit in the same spot. Swap them and nothing moves</span></li>
        <li>{I_CHK}<span>Every future update included. New icons are being added</span></li>
      </ul>
      <p class="fine">Payhip handles checkout and asks for your email to send the download. Already bought it? <a href="{LOGIN}">Get your download</a>.</p>
    </aside>
  </div>
</section>
<section class="sec" id="inside">
  <div class="wrap">
    <div class="sec-h rv"><div><div class="sec-k mono"><b>01</b>What&rsquo;s inside</div><h2 class="d d-l ex-ink">{len(p['icons'])} icons, <em>{len(rows)} categories.</em></h2></div></div>
    <div class="inside rv">
{chr(10).join(rows)}
    </div>
  </div>
</section>
{licence_block(R, "02")}
{faq_block("03")}
{final_block()}"""
    page(f"packs/{p['slug']}/index.html", R, f"{p['name']} | Vectorist",
         f"{len(p['icons'])} hand-made glossy cartoon icons for Roblox: currency, boosts, rewards, pets, shop and more. "
         f"Outline and no-outline versions, transparent PNG, free updates. {p['price']}.",
         body, cur="packs", after=".stage", hide=".buy .btn-buy,.final", ogtype="product")


# ---------------------------------------------------------------------------
# Licence
# ---------------------------------------------------------------------------
def licence():
    R = "../"
    body = f"""<section class="ph">
  <div class="wrap">
    <div class="sec-k mono"><b>&sect;</b>Licence</div>
    <h1 class="d d-l ex-ink">Icon <em>licence.</em></h1>
    <p class="lede">The short version: use the icons in your own games, don&rsquo;t share or sell the files.</p>
  </div>
</section>
<section>
  <div class="wrap prose">
    <h2>What you can do</h2>
    <ul>
      <li>Use the icons in your own experiences and games, on Roblox or any other engine.</li>
      <li>Use the outline and no-outline versions in any combination.</li>
      <li>Receive every future update to a pack you&rsquo;ve bought, at no extra cost.</li>
    </ul>
    <h2>What you can&rsquo;t do</h2>
    <ul>
      <li>Re-upload the icons anywhere, including the Roblox Creator Store or any asset marketplace.</li>
      <li>Resell the icons, on their own or as part of another pack, kit, template or game file.</li>
      <li>Share or redistribute the files to anyone else, whether free or paid.</li>
    </ul>
    <h2>Updates</h2>
    <p>Re-insert the model from your Roblox inventory to get the latest version, or download the files again from your <a href="{LOGIN}">Payhip account</a>.</p>
    <h2>Questions</h2>
    <p>Not sure whether your use is covered? Ask before you use the icons. Reach us through the <a href="{PAYHIP_PAGE}">pack&rsquo;s Payhip page</a>.</p>
  </div>
</section>"""
    page("licence/index.html", R, "Licence | Vectorist", "What you can and can't do with Vectorist icon packs.", body, cur="licence")


# ---------------------------------------------------------------------------
# 404 (served at any depth, so it sets its own base URL)
# ---------------------------------------------------------------------------
def notfound():
    base = ("<script>(function(){var p=location.pathname.split('/')[1]||'';"
            "document.write('<base href=\"'+(/^vectorist$/i.test(p)?'/'+p+'/':'/')+'\">')})()</script>\n")
    body = f"""<section class="nf">
  <div>
    {art("padlock-locked")}
    <h1 class="d d-l ex-ink">This page is <em>locked.</em></h1>
    <p>The link might be old, or the page has moved. Everything else is still here.</p>
    <div class="row" style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <a class="btn btn-buy" href="./">Back to Vectorist</a>
      <a class="btn btn-line" href="packs/">Browse packs</a>
    </div>
  </div>
</section>"""
    page("404.html", "", "Page not found | Vectorist", "This page doesn't exist.", body, noindex=True, extra_head=base)


if __name__ == "__main__":
    home(); packs(); product(); licence(); notfound()
