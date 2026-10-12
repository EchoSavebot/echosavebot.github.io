"""Builds the Echo landing site from src/texts/<lang>.json.

Run from the repository root:  python src/build.py
Writes: index.html (language picker), <lang>/index.html, 404.html, assets/og-<lang>.png,
assets/logo-*.png, assets/favicon-*.png, robots.txt, sitemap.xml.

Everything a page says lives in src/texts/<lang>.json. A new language = a new JSON file
(copy ru.json, translate the values) + "ready": True in LANGS below. Pages link to each other
with relative paths, so the site works both at <name>.github.io/<repo>/ and on its own domain.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# ---- settings (one place) -------------------------------------------------------------------
# The public address of the site, without a trailing slash. Used only where a full address is
# required: link previews (og:image, og:url), canonical, hreflang, sitemap. Change it when the
# site moves (own domain) and rebuild.
SITE_URL = "https://echosave.online"
# Own domain for GitHub Pages (file CNAME). Empty — no own domain.
CNAME = "echosave.online"
BOT_URL = "https://t.me/EchoSave_bot"
SUPPORT_URL = "https://t.me/EchoSave_Support"
PRIVACY_URL = "https://telegra.ph/Politika-konfidencialnosti--EHho-09-20"
TERMS_URL = "https://telegra.ph/Pravila-ispolzovaniya-bota-EHho-09-20"
# Visit counter Umami (cloud.umami.is), no cookies — owner's decision 12.10.2026 (RULES, «Сайт»).
# Website ID from Umami → Settings → Websites. Empty — no counter, the footer says so.
UMAMI_ID = "dd294d60-2943-4dc7-b218-6d5c803ca0c1"
UMAMI_SRC = "https://cloud.umami.is/script.js"
DEFAULT_LANG = "ru"
# code, label in the switcher, ready (published). Not ready = shown greyed with "скоро".
LANGS = [
    ("ru", "RU", True),
    ("en", "EN", False),
    ("hi", "हिन्दी", False),
]
AVATAR = SRC / "img" / "bot-avatar.png"
# Brand gradient — the bot avatar's corners (#8C6FFF → #51BEFF).
GRAD_A, GRAD_B = (140, 111, 255), (81, 190, 255)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def ready_langs() -> list[str]:
    return [code for code, _, ready in LANGS if ready]


def lang_switch(current: str, prefix: str) -> str:
    items = []
    for code, label, ready in LANGS:
        if code == current:
            items.append(f'<span class="lang on" aria-current="true">{esc(label)}</span>')
        elif ready:
            items.append(f'<a class="lang" href="{prefix}{code}/" hreflang="{code}">{esc(label)}</a>')
        else:
            items.append(f'<span class="lang off" title="soon">{esc(label)}</span>')
    return "".join(items)


def counter_tag() -> str:
    """Umami: counts visits without cookies (RULES, «Сайт (лендинг)»). Empty id — no counter."""
    if not UMAMI_ID:
        return ""
    return f'\n<script defer src="{UMAMI_SRC}" data-website-id="{UMAMI_ID}"></script>'


def bot_link(cls: str, text: str, place: str) -> str:
    """A button to the bot. data-umami-event counts the click (no personal data)."""
    return f'<a class="{cls}" href="{BOT_URL}" data-umami-event="open-bot" data-umami-event-place="{place}">{text}</a>'


def head(t: dict, *, path: str, prefix: str, og: str) -> str:
    url = f"{SITE_URL}/{path}"
    alternates = "".join(
        f'\n<link rel="alternate" hreflang="{c}" href="{SITE_URL}/{c}/">' for c in ready_langs())
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{DEFAULT_LANG}/">'
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t['title'])}</title>
<meta name="description" content="{esc(t['description'])}">
<link rel="canonical" href="{url}">{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(t['brand'])}">
<meta property="og:title" content="{esc(t['og_title'])}">
<meta property="og:description" content="{esc(t['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/assets/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#7b7dff">
<link rel="icon" type="image/png" sizes="32x32" href="{prefix}assets/favicon-32.png">
<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">
<link rel="stylesheet" href="{prefix}assets/style.css">
<script>document.documentElement.classList.add("js")</script>
<script defer src="{prefix}assets/site.js"></script>{counter_tag()}
</head>"""


def header(t: dict, prefix: str, lang: str) -> str:
    nav = "".join(f'<a href="#{a}">{esc(label)}</a>' for a, label in t["nav"])
    return f"""<header class="top">
  <div class="wrap top-in">
    <a class="logo" href="./"><img src="{prefix}assets/logo-64.png" width="32" height="32" alt=""><span>{esc(t['brand'])}</span></a>
    <nav class="menu">{nav}</nav>
    <nav class="langs" aria-label="{esc(t['lang_label'])}">{lang_switch(lang, prefix)}</nav>
    {bot_link("btn btn-sm", esc(t['open_bot']), "header")}
  </div>
</header>"""


def footer(t: dict) -> str:
    note = t["footer_note"] if UMAMI_ID else t["footer_note_nocount"]
    return f"""<footer class="foot">
  <div class="wrap">
    <nav class="foot-links">
      <a href="{SUPPORT_URL}">{esc(t['footer_support'])} · @EchoSave_Support</a>
      <a href="{PRIVACY_URL}">{esc(t['footer_privacy'])}</a>
      <a href="{TERMS_URL}">{esc(t['footer_terms'])}</a>
    </nav>
    <p class="muted small">{esc(note)}</p>
  </div>
</footer>"""


WAVE = ('<svg class="wave" width="110" height="22" viewBox="0 0 110 22" fill="currentColor">'
        + "".join(f'<rect x="{i * 5.5:.1f}" y="{(22 - h) / 2}" width="3" height="{h}" rx="1.5"/>'
                  for i, h in enumerate([6, 12, 18, 10, 14, 20, 8, 16, 12, 6, 14, 18, 10, 8, 12, 16, 6, 10, 14, 8]))
        + "</svg>")


def phone(t: dict, prefix: str) -> str:
    """The hero phone. Without JavaScript (or with reduced motion) it shows the chat with the bot:
    the notice, a voice note and its transcript. site.js plays it as a story: Алина writes,
    deletes, the notice comes, a voice note gets its transcript — then again."""
    notice = (f'<div class="bubble" data-s="notice"><b>🗑 {esc(t["mock_title"])}</b><br>{esc(t["mock_who"])}<br>'
              f'{esc(t["mock_time"])}<blockquote>{esc(t["mock_quote"])}</blockquote><i>{esc(t["mock_sign"])}</i></div>')
    return f"""<div class="phone" aria-hidden="true">
      <div class="phone-bar">
        <div class="pb pb-bot"><img src="{prefix}assets/logo-64.png" width="34" height="34" alt=""><div><b>{esc(t['mock_bot'])}</b><span>bot</span></div></div>
        <div class="pb pb-chat"><span class="ava">{esc(t['story_chat'][0])}</span><div><b>{esc(t['story_chat'])}</b><span>{esc(t['story_status'])}</span></div></div>
      </div>
      <div class="screens">
        <div class="msgs scr-bot">
          {notice}
          <div class="bubble out" data-s="voice2"><div class="voice"><span class="play">▶</span>{WAVE}<span class="small">{esc(t['mock_voice_label'])}</span></div></div>
          <div class="bubble out" data-s="tr2">{t['mock_voice_text']}</div>
        </div>
        <div class="msgs scr-chat">
          <div class="bubble" data-s="msg">{esc(t['story_msg'])}<span class="gone">{esc(t['story_deleted'])}</span></div>
          <div class="bubble" data-s="voice"><div class="voice"><span class="play">▶</span>{WAVE}<span class="small">{esc(t['mock_voice_label'])}</span></div></div>
          <div class="bubble out" data-s="tr">{t['story_voice_text']}</div>
        </div>
      </div>
    </div>"""


def connect(t: dict, prefix: str) -> str:
    steps = t["steps"] + [t["step_extra"]]
    items = []
    for i, s in enumerate(steps, 1):
        extra = i > len(t["steps"])
        num = "＋" if extra else str(i)
        items.append(
            f'<li class="step{" step-extra" if extra else ""}" data-shot="{i - 1}"><span class="num">{num}</span>'
            f'<div><b>{esc(s["title"])}</b><span>{esc(s["text"])}</span></div></li>')
    shots = "".join(
        f'<img class="shot{" on" if i == 0 else ""}" src="{prefix}assets/{s["img"]}" width="450" height="975" '
        f'alt="{esc(t["shot_alt"].format(n=i + 1))}" loading="lazy">' for i, s in enumerate(steps))
    return f"""<section class="sec" id="connect">
  <div class="wrap">
    <div class="connect">
      <div class="connect-text">
        <div class="connect-head">
          <img src="{prefix}assets/logo-128.png" width="64" height="64" alt="">
          <div><h2>{esc(t['connect_title'])}</h2><p>{esc(t['connect_sub'])}</p></div>
        </div>
        <ol class="steps">{"".join(items)}</ol>
        <p class="connect-done">{esc(t['connect_done'])}</p>
        <p class="connect-note">{esc(t['connect_note'])}</p>
        {bot_link("btn btn-light", esc(t['hero_cta']), "connect")}
      </div>
      <div class="connect-phone"><div class="shots">{shots}</div></div>
    </div>
  </div>
</section>"""


def page(t: dict) -> str:
    lang = t["lang"]
    prefix = "../"
    badges = "".join(f"<li>{esc(b)}</li>" for b in t["hero_badges"])
    facts = "".join(f'<div class="fact"><b>{esc(a)}</b><span>{esc(b)}</span></div>' for a, b in t["facts"])
    features = "".join(
        f'<article class="card reveal"><div class="ico">{f["icon"]}</div><h3>{esc(f["title"])}</h3>'
        f'<p>{esc(f["text"])}</p></article>' for f in t["features"])
    privacy = "".join(
        f'<div class="pv reveal"><div class="ico">{p["icon"]}</div><div><b>{esc(p["title"])}</b>'
        f'<p>{esc(p["text"])}</p></div></div>' for p in t["privacy"])
    plans = "".join(
        '<article class="card plan reveal"><h3><span class="ico-s">' + p["icon"] + "</span>" + esc(p["title"]) + "</h3>"
        + "".join(f'<div class="row"><span>{esc(a)}</span><b>{esc(b)}</b></div>' for a, b in p["rows"])
        + f'<p class="muted small">{esc(p["note"])}</p></article>' for p in t["plans"])
    faq = "".join(
        f'<details><summary>{esc(q["q"])}</summary><p>{q["a"]}</p></details>' for q in t["faq"])
    guide = "".join(f"<p>{esc(p)}</p>" for p in t["guide"])
    privacy_links = t["privacy_links"].format(privacy_url=PRIVACY_URL, terms_url=TERMS_URL)
    return f"""{head(t, path=f"{lang}/", prefix=prefix, og=f"og-{lang}.png")}
<body>
{header(t, prefix, lang)}
<main>
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-text">
      <h1>{t['hero_title']}</h1>
      <p class="lead">{esc(t['hero_text'])}</p>
      <div class="cta">
        {bot_link("btn", esc(t['hero_cta']), "hero")}
        <a class="btn btn-ghost" href="#connect">{esc(t['hero_how'])}</a>
      </div>
      <ul class="badges">{badges}</ul>
    </div>
    {phone(t, prefix)}
  </div>
</section>

<section class="facts-sec">
  <div class="wrap"><div class="facts reveal">{facts}</div></div>
</section>

<section class="sec" id="features">
  <div class="wrap">
    <h2 class="reveal">{esc(t['features_title'])}</h2>
    <div class="grid3">{features}</div>
  </div>
</section>

{connect(t, prefix)}

<section class="sec">
  <div class="wrap">
    <h2 class="reveal">{esc(t['privacy_title'])}</h2>
    <div class="grid2">{privacy}</div>
    <p class="muted">{privacy_links}</p>
  </div>
</section>

<section class="sec" id="prices">
  <div class="wrap">
    <h2 class="reveal">{esc(t['prices_title'])}</h2>
    <div class="trial reveal"><b>{esc(t['trial_title'])}</b><p>{esc(t['trial_text'])}</p></div>
    <div class="grid3">{plans}</div>
    <p class="muted">{esc(t['prices_note'])}</p>
  </div>
</section>

<section class="sec">
  <div class="wrap narrow guide reveal">
    <h2>{esc(t['guide_title'])}</h2>
    {guide}
    <h3>{esc(t['guide_edit_title'])}</h3>
    <p>{esc(t['guide_edit'])}</p>
  </div>
</section>

<section class="sec" id="faq">
  <div class="wrap narrow">
    <h2 class="reveal">{esc(t['faq_title'])}</h2>
    <div class="faq">{faq}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="world reveal">
      <h2>{esc(t['world_title'])}</h2>
      <p>{esc(t['world_text'])}</p>
      <p class="muted" lang="en">{esc(t['world_en'])}</p>
      <p class="muted" lang="hi">{esc(t['world_hi'])}</p>
    </div>
  </div>
</section>

<section class="sec final">
  <div class="wrap reveal">
    <h2>{esc(t['final_title'])}</h2>
    <p>{esc(t['final_text'])}</p>
    {bot_link("btn", esc(t['hero_cta']), "final")}
  </div>
</section>
</main>
{footer(t)}
</body>
</html>
"""


def root_page(t: dict) -> str:
    """The bare address: picks a ready language by the browser's languages, else the default.
    No content of its own; the link below works without JavaScript."""
    ready = json.dumps(ready_langs())
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t['title'])}</title>
<meta name="description" content="{esc(t['description'])}">
<meta property="og:title" content="{esc(t['og_title'])}">
<meta property="og:description" content="{esc(t['description'])}">
<meta property="og:image" content="{SITE_URL}/assets/og-{DEFAULT_LANG}.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE_URL}/{DEFAULT_LANG}/">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<noscript><meta http-equiv="refresh" content="0; url={DEFAULT_LANG}/"></noscript>
<script>
(function () {{
  var ready = {ready}, pick = "{DEFAULT_LANG}";
  var prefs = navigator.languages || [navigator.language || ""];
  for (var i = 0; i < prefs.length; i++) {{
    var code = String(prefs[i]).toLowerCase().split("-")[0];
    if (ready.indexOf(code) !== -1) {{ pick = code; break; }}
  }}
  location.replace(pick + "/" + location.search + location.hash);
}})();
</script>
</head>
<body style="font-family:system-ui,sans-serif;text-align:center;padding:48px 16px">
<a href="{DEFAULT_LANG}/">{esc(t['brand'])} →</a>
</body>
</html>
"""


def not_found(t: dict) -> str:
    # GitHub Pages serves 404.html at any depth, so links here are absolute to the site.
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t['notfound_title'])} — {esc(t['brand'])}</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="{SITE_URL}/assets/style.css">
</head>
<body>
<main class="sec final" style="min-height:70vh">
  <div class="wrap">
    <h1>{esc(t['notfound_title'])}</h1>
    <p>{esc(t['notfound_text'])}</p>
    <a class="btn" href="{SITE_URL}/">{esc(t['notfound_home'])}</a>
  </div>
</main>
</body>
</html>
"""


# ---- images ---------------------------------------------------------------------------------
def gradient(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            k = (x / w + y / h) / 2
            px[x, y] = tuple(round(a + (b - a) * k) for a, b in zip(GRAD_A, GRAD_B))
    return img


def font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for base in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu"):
        p = Path(base) / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def rounded(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1], radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def wrap(d: ImageDraw.ImageDraw, text: str, f, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if cur and d.textlength(trial, font=f) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def og_image(t: dict, dest: Path) -> None:
    """The picture Telegram and other apps show under a shared link (1200x630)."""
    S = 2  # draw at 2x, then downscale for smooth edges
    W, H = 1200 * S, 630 * S
    img = gradient(W // 8, H // 8).resize((W, H), Image.BICUBIC).convert("RGBA")
    rings = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rings)
    for r, a in ((560, 35), (430, 50), (300, 65)):  # soft "echo" rings, as on the /start card
        cx, cy = 1120 * S, 60 * S
        rd.ellipse([cx - r * S, cy - r * S, cx + r * S, cy + r * S], outline=(255, 255, 255, a), width=5 * S)
    img.alpha_composite(rings)
    d = ImageDraw.Draw(img)
    logo = rounded(Image.open(AVATAR).convert("RGB").resize((104 * S, 104 * S), Image.LANCZOS), 26 * S)
    frame = Image.new("RGBA", (114 * S, 114 * S), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle([0, 0, 114 * S - 1, 114 * S - 1], 31 * S, fill=(255, 255, 255, 255))
    img.alpha_composite(frame, (80 * S, 70 * S))
    img.alpha_composite(logo, (85 * S, 75 * S))
    d.text((222 * S, 100 * S), t["brand"], font=font(True, 48 * S), fill="white")
    f_title = font(True, 64 * S)
    y = 230 * S
    for line in wrap(d, t["og_title"], f_title, 1000 * S)[:2]:
        d.text((80 * S, y), line, font=f_title, fill="white")
        y += 78 * S
    d.text((80 * S, y + 14 * S), t["og_subtitle"], font=font(False, 36 * S), fill=(255, 255, 255, 235))
    pill = t["og_trial"] + "  ·  @EchoSave_bot"
    f = font(True, 32 * S)
    w = d.textlength(pill, font=f)
    d.rounded_rectangle([80 * S, 500 * S, 80 * S + w + 64 * S, 564 * S], 32 * S, fill=(255, 255, 255, 255))
    d.text((112 * S, 514 * S), pill, font=f, fill=(84, 72, 200))
    img.convert("RGB").resize((1200, 630), Image.LANCZOS).save(dest, optimize=True)


def icons(assets: Path) -> None:
    av = Image.open(AVATAR).convert("RGB")
    for size in (64, 128):
        rounded(av.resize((size, size), Image.LANCZOS), size // 4).save(assets / f"logo-{size}.png", optimize=True)
    rounded(av.resize((32, 32), Image.LANCZOS), 8).save(assets / "favicon-32.png", optimize=True)
    av.resize((180, 180), Image.LANCZOS).save(assets / "apple-touch-icon.png", optimize=True)


def screenshots(assets: Path) -> None:
    """Connection screenshots from the bot (bot/assets/connect/iphone, personal data painted over)."""
    for i in range(1, 5):
        src = SRC / "img" / "connect" / f"0{i}.jpg"
        im = Image.open(src).convert("RGB")
        im.resize((450, round(im.height * 450 / im.width)), Image.LANCZOS).save(
            assets / f"connect-{i}.jpg", quality=82, optimize=True, progressive=True)


def main() -> None:
    texts = {p.stem: json.loads(p.read_text("utf-8")) for p in (SRC / "texts").glob("*.json")}
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    icons(assets)
    screenshots(assets)
    for code in ready_langs():
        t = texts[code]
        (ROOT / code).mkdir(exist_ok=True)
        (ROOT / code / "index.html").write_text(page(t), "utf-8")
        og_image(t, assets / f"og-{code}.png")
    base = texts[DEFAULT_LANG]
    (ROOT / "index.html").write_text(root_page(base), "utf-8")
    (ROOT / "404.html").write_text(not_found(base), "utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", "utf-8")
    urls = "".join(f"  <url><loc>{SITE_URL}/{c}/</loc></url>\n" for c in ready_langs())
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n", "utf-8")
    (ROOT / ".nojekyll").write_text("", "utf-8")
    if CNAME:
        (ROOT / "CNAME").write_text(CNAME + "\n", "utf-8")
    print("built:", ", ".join(ready_langs()))


if __name__ == "__main__":
    main()
