#!/usr/bin/env python3
"""
Vectorist page builder. Local tool, never served to the browser.

    python tools/pages.py

Writes every HTML page from the templates below. Nav, footer, head and the
mobile buy bar exist ONCE here. Edit this file, never the generated .html.

Pack data comes from js/catalog.js (written by tools/build.py) and the copy
fields (blurb, description) from tools/packs.json.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Public URL, used only for canonical and social-share tags. Links are relative.
SITE_URL = "https://vectorist.co/"
LOGIN = "https://payhip.com/auth/login"
TERMS_UPDATED = "23 November 2026"

CAT = json.loads(re.search(r"=(\{.*\});", (ROOT / "js" / "catalog.js").read_text()).group(1))
COPY = {p["slug"]: p for p in json.loads((ROOT / "tools" / "packs.json").read_text())["packs"]}
PACKS = CAT["packs"]
for _p in PACKS:
    _p["blurb"] = COPY[_p["slug"]].get("blurb", "")
    _p["description"] = COPY[_p["slug"]].get("description", "")
    _p["buy"] = f"https://payhip.com/buy?link={_p['payhip']}"
    _p["page"] = f"https://payhip.com/b/{_p['payhip']}"
LEAD = PACKS[0]

VER = hashlib.sha1(b"".join((ROOT / p).read_bytes() for p in ("css/site.css", "js/site.js", "js/catalog.js"))).hexdigest()[:8]

# ---------------------------------------------------------------------------
# Small SVGs
# ---------------------------------------------------------------------------
I_USER = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></svg>'
I_MENU = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
I_ARR = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
I_YES = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#18A957" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
I_NO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#E5484D" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
I_CHK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
I_PLUS = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>'


def art(icon, cls="", style="", hidden=False):
    c = f"art {cls}".strip()
    st = f' style="{style}"' if style else ""
    ah = ' aria-hidden="true"' if hidden else ""
    return f'<div class="{c}" data-icon="{icon}"{st}{ah}></div>'


def buy_btn(p, label="Get the pack", size="btn-lg"):
    return f'<a class="btn btn-y {size}" href="{p["buy"]}">{label} <span class="p">{p["price"]}</span></a>'


def explore_btn(R, size="btn-lg"):
    return f'<a class="btn btn-y {size}" href="{R}packs/">Explore packs {I_ARR}</a>'


# ---------------------------------------------------------------------------
# Chrome
# ---------------------------------------------------------------------------
HEAD = """<!DOCTYPE html>
<html lang="en" data-style="outline">
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
<meta property="og:image" content="{site}{cover}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2350FF">
{extra}<link rel="icon" href="{R}assets/mark.svg" type="image/svg+xml">
<link rel="preload" href="{R}assets/fonts/fredoka-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{R}assets/fonts/bricolage-grotesque-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{R}css/site.css?v={ver}">
<script>try{{if(localStorage.getItem('vx.style')==='plain')document.documentElement.setAttribute('data-style','plain')}}catch(e){{}}</script>
</head>
<body class="{bodycls}">
"""


def nav(R, cur):
    home = R or "./"

    def a(href, label, key):
        ac = ' aria-current="page"' if key == cur else ""
        return f'<a href="{href}"{ac}>{label}</a>'
    return f"""<header class="nav">
  <div class="wrap">
    <a class="logo" href="{home}"><img src="{R}assets/mark.svg" alt="" width="34" height="34">Vectorist</a>
    <nav class="nav-links" aria-label="Main">
      {a(R + "packs/", "Packs", "packs")}
      {a(home + "#in-game", "In-game", "-")}
      {a(home + "#faq", "FAQ", "-")}
      {a(R + "terms/", "Terms", "terms")}
    </nav>
    <div class="nav-r">
      <a class="icon-btn dl" href="{LOGIN}" title="My downloads" aria-label="My downloads">{I_USER}</a>
      {explore_btn(R, "btn-sm")}
      <button class="icon-btn burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="sheet">{I_MENU}</button>
    </div>
  </div>
</header>
<div class="sheet" id="sheet">
  <a href="{R}packs/">Packs {I_ARR}</a>
  <a href="{home}#in-game">In-game {I_ARR}</a>
  <a href="{home}#faq">FAQ {I_ARR}</a>
  <a href="{R}terms/">Terms {I_ARR}</a>
  <hr>
  <a href="{LOGIN}">My downloads {I_USER}</a>
</div>
"""


def foot(R):
    home = R or "./"
    packs = "\n".join(f'        <li><a href="{R}packs/{p["slug"]}/">{p["name"]}</a></li>' for p in PACKS)
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="brand">
      <a class="logo" href="{home}"><img src="{R}assets/mark.svg" alt="" width="34" height="34">Vectorist</a>
      <p>Hand-made icon packs for Roblox and every other engine.</p>
    </div>
    <div>
      <h4>Packs</h4>
      <ul>
        <li><a href="{R}packs/">All packs</a></li>
{packs}
      </ul>
    </div>
    <div>
      <h4>Help</h4>
      <ul>
        <li><a href="{LOGIN}">My downloads</a></li>
        <li><a href="{home}#faq">FAQ</a></li>
        <li><a href="{R}terms/">Terms of Service</a></li>
      </ul>
    </div>
  </div>
  <div class="foot-b"><div class="wrap"><span>&copy; 2026 Vectorist</span><span>Not affiliated with Roblox Corporation</span></div></div>
</footer>
"""


def page(path, R, title, desc, body, cur="", plain=True, mbar="", ogtype="website", extra="", cover=None):
    url = SITE_URL + path.replace("index.html", "")
    h = HEAD.format(title=title, desc=desc, url=url, site=SITE_URL, cover=cover or LEAD["cover"], R=R, ver=VER,
                    bodycls="page-plain" if plain else "", ogtype=ogtype, extra=extra)
    out = h + nav(R, cur) + "<main>\n" + body + "\n</main>\n" + foot(R) + mbar
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
def style_switch():
    return """<div class="seg" role="group" aria-label="Icon style">
        <button type="button" data-set-style="outline" aria-pressed="true">Outline</button>
        <button type="button" data-set-style="plain" aria-pressed="false">No outline</button>
      </div>"""


def pack_cards(R):
    cards = []
    for p in PACKS:
        cards.append(f"""      <a class="pack" href="{R}packs/{p['slug']}/">
        <div class="cv"><img src="{R}{p['cover']}" alt="{p['name']}" width="1280" height="720" loading="lazy" draggable="false"></div>
        <div class="bd">
          <h3>{p['name']}</h3>
          <p>{p['blurb']}</p>
          <div class="row"><span class="pr">{p['price']}</span><span class="btn btn-line btn-sm">View pack {I_ARR}</span></div>
        </div>
      </a>""")
    cards.append(f"""      <div class="pack soon">
        {art("egg", hidden=True)}
        <h3>More packs on the way</h3>
        <p>Existing packs keep growing too. Buy once and new icons arrive free.</p>
      </div>""")
    return '<div class="packs rv">\n' + "\n".join(cards) + "\n    </div>"


FAQS = [
    ("What format are the icons?",
     "Transparent PNGs at a high resolution, so they scale down cleanly to any button or HUD size. Each icon comes "
     "with an outline and a no-outline version."),
    ("Can I use them outside Roblox?",
     "Yes. They work in Unity, Godot, Unreal, GameMaker or a web game. Use them in your own games on any platform."),
    ("How do updates work?",
     "Buy a pack once and every update to it is included. Re-insert the model from your Roblox inventory to get the "
     "latest version, or download the files again from your Payhip account."),
    ("Where&rsquo;s my download?",
     f"Payhip emails your download link straight after checkout. You can also <a href=\"{LOGIN}\">sign in to Payhip</a> "
     "with the same email to download it again."),
]


def faq_block(R):
    items = "\n".join(
        f'        <details><summary>{q}<span class="pm">{I_PLUS}</span></summary><p>{a}</p></details>' for q, a in FAQS)
    return f"""<section class="sec" id="faq">
  <div class="wrap faq-l">
    <div class="sec-h rv"><div><h2 class="d d-l ink">Questions, <em>answered.</em></h2><p class="lede">Anything else? Message us through <a href="{LEAD['page']}">Payhip</a>.</p></div></div>
    <div class="faq rv">
{items}
    </div>
  </div>
</section>
"""


def licence_block(R):
    return f"""<section class="sec">
  <div class="wrap">
    <div class="sec-h rv">
      <h2 class="d d-l ink">What you can <em>do with them.</em></h2>
      <a class="link" href="{R}terms/">Full terms {I_ARR}</a>
    </div>
    <div class="lic rv">
      <div>
        <h3>{art("padlock-unlocked", hidden=True)}You can</h3>
        <ul>
          <li>{I_YES}<span>Use them in your own games, on Roblox or any other engine.</span></li>
          <li>{I_YES}<span>Resize, recolour and edit them for those games.</span></li>
          <li>{I_YES}<span>Get every future update to the pack free.</span></li>
        </ul>
      </div>
      <div class="no">
        <h3>{art("padlock-locked", hidden=True)}You can&rsquo;t</h3>
        <ul>
          <li>{I_NO}<span>Re-upload them anywhere, including the Creator Store.</span></li>
          <li>{I_NO}<span>Resell them, alone or inside another kit or template.</span></li>
          <li>{I_NO}<span>Share the files with anyone outside your team.</span></li>
        </ul>
      </div>
    </div>
  </div>
</section>
"""


def final_block(R, title_w, title_y, button, icons=("star", "chest-open-gems", "trophy")):
    return f"""<section class="final">
  <div class="wrap">
    <div>
      <h2 class="d d-l"><span class="ex-w">{title_w}</span><br><span class="ex-y">{title_y}</span></h2>
      {button}
    </div>
    <div class="final-art" aria-hidden="true">{"".join(art(i, hidden=True) for i in icons)}</div>
  </div>
</section>
"""


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------
def home():
    R = ""
    ghosts = "".join(art(i, "", s, hidden=True) for i, s in [
        ("sword", "left:-3%;top:20%;width:150px;transform:rotate(-12deg)"),
        ("paw-print", "left:3%;bottom:10%;width:110px;transform:rotate(14deg)"),
        ("timer", "left:44%;bottom:-4%;width:150px"),
        ("spin-wheel", "right:-5%;bottom:-8%;width:190px"),
    ])
    tiles = [("chest-open-coins", True), ("coin", False), ("potion", False), ("flame", False), ("trophy", False), ("gem", False)]
    names = {ic["id"]: ic["name"] for ic in LEAD["icons"]}
    board = "\n".join(
        f'        <div class="spec{" big" if big else ""}"><div class="fl">{art(i)}</div><span class="nm">{names[i]}</span></div>'
        for i, big in tiles)
    hud_l = [("shop", "c-y", "Shop", ""), ("egg", "c-p", "Hatch", ""), ("backpack", "c-g", "Items", ""),
             ("trade", "c-v", "Trade", ""), ("index", "c-b", "Index", ""), ("friends", "c-o", "Invite", "")]
    hud_r = [("quest-scroll", "c-o", "Quests", ""), ("rebirth", "c-p", "Rebirth", "rebirth"),
             ("spin-wheel", "c-b", "Spin", "wheel"), ("calendar", "c-g", "Daily", ""),
             ("present", "c-y", "Gifts", ""), ("settings", "c-v", "Settings", "cog")]

    def gbs(lst):
        out = []
        for i, c, lab, sp in lst:
            cls = "gb spin" if sp else "gb"
            data = ' data-spin="%s"' % sp if sp else ""
            out.append(f'<button class="{cls}" type="button"{data} tabindex="-1">'
                       f'<span class="k {c}">{art(i, hidden=True)}</span><span>{lab}</span></button>')
        return "\n          ".join(out)

    body = f"""<section class="hero" id="hero">
  <div class="hero-ghosts" aria-hidden="true">{ghosts}</div>
  <div class="wrap hero-grid">
    <div>
      <h1 class="d d-xl"><span class="ex-w">Hand-made</span><span class="ex-y">game icons.</span></h1>
      <p class="hero-sub">Glossy icon packs for Roblox and every other engine, drawn by hand and ready to drop into your game&rsquo;s UI.</p>
      <div class="hero-cta">
        {explore_btn(R)}
        <a class="btn btn-ghost btn-lg" href="#in-game">See them in-game</a>
      </div>
    </div>
    <div class="board" aria-label="Icon previews">
{board}
    </div>
  </div>
</section>

<section class="sec" id="packs">
  <div class="wrap">
    <div class="sec-h rv">
      <h2 class="d d-l ink">Latest <em>packs.</em></h2>
      <a class="link" href="packs/">View all {I_ARR}</a>
    </div>
    {pack_cards(R)}
  </div>
</section>

<section class="sec night" id="in-game">
  <div class="wrap">
    <div class="sec-h c rv">
      <h2 class="d d-l ink">See them in a <em>real game.</em></h2>
      <p class="lede">Tap the chest.</p>
      {style_switch()}
    </div>
    <div class="hud-frame rv">
      <div class="hud">
        <svg class="hud-scene" viewBox="0 0 800 500" preserveAspectRatio="none" aria-hidden="true">
          <rect width="800" height="500" fill="#7CCBFF"/>
          <rect width="800" height="150" fill="#6BC0FB"/>
          <circle cx="640" cy="120" r="46" fill="#FFF3B0"/>
          <g fill="#fff"><ellipse cx="200" cy="110" rx="70" ry="22"/><ellipse cx="240" cy="96" rx="44" ry="26"/><ellipse cx="520" cy="70" rx="56" ry="16"/><ellipse cx="548" cy="60" rx="30" ry="18"/></g>
          <path d="M0 330 L120 250 L230 310 L360 230 L470 300 L600 240 L800 320 L800 500 L0 500Z" fill="#59C46B"/>
          <path d="M0 380 L160 330 L330 370 L520 320 L700 360 L800 340 L800 500 L0 500Z" fill="#46AE57"/>
          <path d="M0 440 L800 420 L800 500 L0 500Z" fill="#3C9A4C"/>
          <path d="M330 500 L380 380 L420 380 L470 500Z" fill="#E8C98A"/>
        </svg>
        <div class="hud-cur">
          <div class="pill">{art("coin", hidden=True)}<span data-count="coin">12,480</span></div>
          <div class="pill">{art("gem", hidden=True)}<span>342</span></div>
        </div>
        <div class="hud-boost">
          <div class="boost">{art("flame", hidden=True)}<i>2x</i><b data-timer="754">12:34</b></div>
          <div class="boost">{art("lightning-bolt", hidden=True)}<b data-timer="299">4:59</b></div>
          <div class="boost">{art("luck-clover", hidden=True)}<i>x3</i><b data-timer="1460">24:20</b></div>
        </div>
        <div class="hud-col l">
          {gbs(hud_l)}
        </div>
        <div class="hud-col r">
          {gbs(hud_r)}
        </div>
        <button class="hud-chest" type="button" aria-label="Open the chest"><span class="tip">Open me!</span>{art("chest-closed", hidden=True)}</button>
        <div class="hud-toast d ex-y" aria-hidden="true">+250</div>
      </div>
    </div>
  </div>
</section>

<section class="sec" id="how">
  <div class="wrap">
    <div class="sec-h rv"><h2 class="d d-l ink">Buy once. <em>Keep getting icons.</em></h2></div>
    <div class="steps rv">
      <div class="step">{art("present", hidden=True)}<h3>Pick a pack</h3><p>Pay once through Payhip and your download link arrives by email straight away.</p></div>
      <div class="step">{art("backpack", hidden=True)}<h3>Drop them in</h3><p>Transparent PNGs, plus a Roblox model you can insert straight into Studio.</p></div>
      <div class="step">{art("rebirth", hidden=True)}<h3>Get every update</h3><p>New icons land in the packs you own. Re-insert the model to get them, free.</p></div>
    </div>
  </div>
</section>

{faq_block(R)}
{final_block(R, "Make your game", "look finished.", explore_btn(R))}"""
    page("index.html", R, "Vectorist | Hand-made game icons for Roblox",
         "Hand-made, glossy icon packs for Roblox and every other game engine. Transparent PNG, outline and no-outline "
         "styles, free updates.", body, plain=False)


# ---------------------------------------------------------------------------
# Packs index
# ---------------------------------------------------------------------------
def packs():
    R = "../"
    body = f"""<section class="ph">
  <div class="wrap">
    <h1 class="d d-l ink">All <em>packs.</em></h1>
    <p class="lede">Every pack is a one-time purchase with free updates.</p>
  </div>
</section>
<section style="padding-bottom:112px">
  <div class="wrap">
    {pack_cards(R)}
  </div>
</section>"""
    page("packs/index.html", R, "Packs | Vectorist",
         "Hand-made icon packs for Roblox and any game engine. One-time purchase, free updates.", body, cur="packs")


# ---------------------------------------------------------------------------
# Product pages (one per pack)
# ---------------------------------------------------------------------------
def about_block(p):
    n = len(p["icons"])
    cats = []
    for c in p["categories"]:
        ics = [ic for ic in p["icons"] if ic["cat"] == c]
        if not ics:
            continue
        shown, more = ics[:4], len(ics) - 4
        stack = "".join(f'<span>{art(ic["id"], hidden=True)}</span>' for ic in shown)
        if more > 0:
            stack += f'<b>+{more}</b>'
        names = ", ".join(ic["name"] for ic in ics)
        cats.append(f'<div class="cat"><div class="stack">{stack}</div><h3>{c}</h3><p>{names}</p></div>')
    deco = "".join(art(i, hidden=True) for i in ("potion", "star", "egg"))
    return f"""<div class="about">
      <div class="about-intro">
        <div class="deco" aria-hidden="true">{deco}</div>
        <h2 class="d"><span class="ex-w">Your everyday</span><br><span class="ex-y">icon pack.</span></h2>
        <p>Made for Roblox games and drawn by hand by Magma, with no AI. {n} glossy cartoon icons, each with an outline and a no-outline version, so you get {n * 2} images in total.</p>
      </div>
      <div class="cats">
        {"".join(cats)}
      </div>
      <div class="feats">
        <div class="feat">
          <div class="auto" data-style="outline" aria-hidden="true">{art("coin", hidden=True)}<span class="st">Outline</span></div>
          <h3>Swap styles, nothing moves</h3>
          <p>Every icon is centred with the same padding, so they line up cleanly in buttons and grids. Both versions sit in exactly the same spot.</p>
        </div>
        <div class="feat">
          <div class="upd" aria-hidden="true">{art("rebirth", hidden=True)}</div>
          <h3>Buy once, get every update</h3>
          <p>We&rsquo;re actively adding new icons. Re-insert the model from your inventory to get the latest version.</p>
        </div>
      </div>
    </div>"""


def product(p):
    R = "../../"
    n = len(p["icons"])
    first, rest = p["name"].rsplit(" ", 1) if " " in p["name"] else (p["name"], "")
    body = f"""<section>
  <div class="wrap pp">
    <div class="cv"><img src="{R}{p['cover']}" alt="{p['name']}" width="1280" height="720" draggable="false"></div>
    {about_block(p)}
    <aside class="buy">
      <h1 class="d d-l ink">{first} <em>{rest}</em></h1>
      <p class="desc">{p['blurb']}</p>
      <div class="pr">{p['price']}</div>
      {buy_btn(p)}
      <ul>
        <li>{I_CHK}<span>{n} icons, each in an outline and a no-outline version</span></li>
        <li>{I_CHK}<span>High-resolution transparent PNGs</span></li>
        <li>{I_CHK}<span>Same centred padding, so they line up in any button</span></li>
        <li>{I_CHK}<span>Every future update included</span></li>
      </ul>
      <p class="owned">Already bought it? <a href="{LOGIN}">Get your download</a></p>
    </aside>
  </div>
</section>
<section class="sec" id="icons">
  <div class="wrap">
    <div class="sec-h rv">
      <h2 class="d d-l ink">All {n} <em>icons.</em></h2>
      {style_switch()}
    </div>
    <div data-wall></div>
  </div>
</section>
{licence_block(R)}
{faq_block(R)}
{final_block(R, "One payment.", "Every future icon.", buy_btn(p))}"""
    mbar = f"""<div class="mbar" data-after=".buy .btn-y" data-hide=".final">
  <b>{p['name']}</b>
  {buy_btn(p, "Get it", "btn-sm")}
</div>
"""
    page(f"packs/{p['slug']}/index.html", R, f"{p['name']} | Vectorist",
         f"{n} hand-made glossy icons for Roblox and any engine. {p['blurb']} {p['price']}, free updates.",
         body, cur="packs", mbar=mbar, ogtype="product", cover=p["cover"])


# ---------------------------------------------------------------------------
# Terms of Service
# ---------------------------------------------------------------------------
def terms():
    R = "../"
    body = f"""<section class="ph">
  <div class="wrap">
    <h1 class="d d-l ink">Terms of <em>Service.</em></h1>
    <p class="lede">The rules for buying and using Vectorist icon packs.</p>
  </div>
</section>
<section>
  <div class="wrap"><div class="prose">
    <p>These terms apply whenever you buy, download or use an icon pack or any other digital product from Vectorist (a &ldquo;Product&rdquo;). By doing any of those things you agree to them, whether or not you have read them. If you don&rsquo;t agree, don&rsquo;t buy or use the Products.</p>

    <h2>1. Your licence</h2>
    <ul>
      <li>Every Product, and all rights in it, stays the property of Vectorist and its artists. Buying a Product gives you a licence to use it. It does not sell you the artwork.</li>
      <li>The licence is personal, non-exclusive and non-transferable. You can&rsquo;t pass it on, sell it or sublicense it.</li>
      <li>You may use Products in games and experiences that you make or publish, on Roblox or any other platform, including games that earn money.</li>
      <li>You may resize, recolour, crop and edit Products for those games. Edited versions are still Products and stay covered by these terms.</li>
      <li>You may not claim that you created a Product, or present it, edited or not, as your own original artwork.</li>
    </ul>

    <h2>2. What isn&rsquo;t allowed</h2>
    <ul>
      <li>Reselling, sharing, leaking, trading or giving away Product files, original or edited, in any format.</li>
      <li>Uploading Products anywhere other people can get them as files, including the Roblox Creator Store and Toolbox, asset marketplaces, file hosts, Discord servers and social media.</li>
      <li>Including Products in anything sold or given away as a resource, such as UI kits, game templates, asset packs or uncopylocked places.</li>
      <li>Using Products to train, fine-tune or prompt AI image models.</li>
    </ul>

    <h2>3. Teams</h2>
    <p>You may share a Product with people working on your game, for that game only. You are responsible for everyone you share it with. If a team member leaks or misuses a Product, we treat it as a breach by you.</p>

    <h2>4. Payments and refunds</h2>
    <ul>
      <li>Payments are processed by Payhip. Prices are shown in US dollars.</li>
      <li>Products are digital and delivered instantly, so all sales are final and we don&rsquo;t offer refunds or exchanges, except where the law requires us to.</li>
      <li>If you file a chargeback or payment dispute without contacting us first, we may cancel your licence to every Product you have bought and refuse future sales. We report fraudulent disputes to the payment provider.</li>
    </ul>

    <h2>5. Updates and support</h2>
    <ul>
      <li>Buying a Product includes the updates we release for it. We decide what each update contains, and we may change or stop updating a Product at any time.</li>
      <li>Support covers problems with the files themselves, such as a missing or damaged file. We don&rsquo;t teach Roblox Studio, scripting or UI design, and not knowing how to use a Product is not grounds for a refund.</li>
    </ul>

    <h2>6. Disclaimers and liability</h2>
    <ul>
      <li>Products are provided &ldquo;as is&rdquo;, without warranties of any kind, to the fullest extent the law allows.</li>
      <li>We don&rsquo;t promise any result from using a Product, including game popularity, player numbers or revenue.</li>
      <li>We aren&rsquo;t responsible if a Roblox or other platform update changes how a Product looks or works, or for moderation action taken against your game or account.</li>
      <li>To the fullest extent the law allows, our total liability for any claim relating to a Product is limited to the amount you paid for it.</li>
    </ul>

    <h2>7. Enforcement</h2>
    <ul>
      <li>If you break these terms, your licence ends immediately. You must stop using the affected Products and delete every copy. We may also block your access to current and future Products.</li>
      <li>We file DMCA and platform takedown notices against unauthorised copies, including against games, listings and accounts that contain them, and may take further legal action.</li>
    </ul>

    <h2>8. Changes to these terms</h2>
    <p>We may update these terms. The version on this page applies from the date below. Changes don&rsquo;t take away rights you already had for Products bought before the change.</p>

    <h2>9. Governing law</h2>
    <p>These terms are governed by the laws of New Zealand. Nothing in them limits rights you have under consumer protection laws that apply to you.</p>

    <h2>Contact</h2>
    <p>Questions about these terms, or not sure whether your use is covered? Ask before you use a Product. Message us through <a href="{LEAD['page']}">Payhip</a>.</p>

    <p class="upd">Last updated {TERMS_UPDATED}</p>
  </div></div>
</section>"""
    page("terms/index.html", R, "Terms of Service | Vectorist",
         "Terms of Service and licence for Vectorist icon packs.", body, cur="terms")


def licence_redirect():
    # Old URL from the first version of the site; may already be linked from Payhip.
    out = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Terms of Service | Vectorist</title>
<link rel="canonical" href="{SITE_URL}terms/"><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=../terms/"></head>
<body><a href="../terms/">Terms of Service</a></body></html>
"""
    with open(ROOT / "licence" / "index.html", "w", newline="\n") as f:
        f.write(out)
    print("wrote licence/index.html (redirect)")


# ---------------------------------------------------------------------------
# 404 (served at any depth; base resolves to the site root)
# ---------------------------------------------------------------------------
def notfound():
    body = f"""<section class="nf">
  <div>
    {art("padlock-locked", hidden=True)}
    <h1 class="d d-l ink">This page is <em>locked.</em></h1>
    <p>The link might be old, or the page has moved.</p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      {explore_btn("", "")}
      <a class="btn btn-line" href="./">Home</a>
    </div>
  </div>
</section>"""
    page("404.html", "", "Page not found | Vectorist", "This page doesn't exist.", body,
         extra='<meta name="robots" content="noindex">\n<base href="/">\n')


if __name__ == "__main__":
    home(); packs()
    for _p in PACKS:
        product(_p)
    terms(); licence_redirect(); notfound()
