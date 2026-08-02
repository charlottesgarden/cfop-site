#!/usr/bin/env python3
"""
build-gallery.py  --  Charlotte's Garden image library

  cd ~/Desktop/charlottesgarden
  python3 build-gallery.py

Reads every .webp in ./webp (or a folder you pass as an argument), auto-sorts
them into categories by looking at the actual pixels, and writes:

    gallery.html        the page
    gallery-data.json   the editable list

Re-run it any time. It MERGES with gallery-data.json, so every title you
rename and every photo you prune STAYS renamed and pruned. New photos get
appended. Nothing you edit is ever overwritten.

To prune one:   set  "keep": false
To rename one:  change  "title"
To recategorise: change  "cat"
...then re-run. That's the whole loop.

Needs Pillow:   pip3 install Pillow
"""

import json, sys, colorsys
from pathlib import Path

try:
    from PIL import Image, ExifTags
except ImportError:
    sys.exit("Pillow missing.  Run:  pip3 install Pillow")

MAX_DIM = 1200   # long edge, px  -- gallery thumbnails never need more
QUALITY = 85

ROOT   = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.cwd()
WEBP   = ROOT / "webp" if (ROOT / "webp").is_dir() else ROOT
DATA   = ROOT / "gallery-data.json"
OUT    = ROOT / "gallery.html"

SKIP_EXT = {".mov", ".mp4", ".avi", ".heic", ".heif"}

CATS = [
    ("stand",     "The Stand"),
    ("garden",    "In the Garden"),
    ("tomatoes",  "Tomatoes"),
    ("peppers",   "Peppers & Chiles"),
    ("squash",    "Squash & Gourds"),
    ("flowers",   "Flowers & Pollinators"),
    ("house",     "The Yellow House"),
    ("land",      "Red Rock & Sky"),
    ("unsorted",  "Needs a Home"),
]

MONTHS = ["", "January","February","March","April","May","June",
          "July","August","September","October","November","December"]


# ---------------------------------------------------------------- analysis
def resize_if_needed(path):
    """Cap any oversized webp down to gallery size, in place."""
    im = Image.open(path)
    w, h = im.size
    long_edge = max(w, h)
    if long_edge > MAX_DIM:
        scale = MAX_DIM / long_edge
        im = im.convert("RGB").resize((int(w*scale), int(h*scale)), Image.LANCZOS)
        im.save(path, "WEBP", quality=QUALITY)


def profile(path):
    """Look at the pixels and guess what this photo is of."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    small = im.resize((120, 120))
    raw = small.tobytes()
    px = [(raw[i], raw[i+1], raw[i+2]) for i in range(0, len(raw), 3)]

    n = len(px)
    buckets = dict(blue=0, green=0, red=0, yellow=0, orange=0, dirt=0, bright=0)
    for r, g, b in px:
        rr, gg, bb = r / 255, g / 255, b / 255
        hu, li, sa = colorsys.rgb_to_hls(rr, gg, bb)
        hu *= 360
        if li > .80: buckets["bright"] += 1
        if sa < .12: continue
        if 185 <= hu <= 250 and li > .35:      buckets["blue"]   += 1
        elif 70  <= hu <= 165:                 buckets["green"]  += 1
        elif hu >= 340 or hu <= 12:            buckets["red"]    += 1
        elif 40  <= hu <= 68:                  buckets["yellow"] += 1
        elif 13  <= hu <= 39 and li > .42:     buckets["orange"] += 1
        elif 13  <= hu <= 39:                  buckets["dirt"]   += 1
    p = {k: v / n for k, v in buckets.items()}

    # shot date, if the camera left one
    when = ""
    try:
        ex = im.getexif()
        tag = {ExifTags.TAGS.get(k, k): v for k, v in ex.items()}
        raw = tag.get("DateTimeOriginal") or tag.get("DateTime") or ""
        if raw:
            y, mo = raw[:4], int(raw[5:7])
            when = f"{MONTHS[mo]} {y}"
    except Exception:
        pass

    # ---- the guess ----
    if p["blue"] > .16 and p["green"] < .22:      cat = "land"
    elif p["blue"] > .10 and p["yellow"] > .10:   cat = "house"
    elif p["red"] > .13 and p["green"] < .30:     cat = "tomatoes"
    elif p["yellow"] > .18 and p["green"] > .18:  cat = "squash"
    elif p["yellow"] > .22:                       cat = "flowers"
    elif p["green"] > .40:                        cat = "garden"
    elif p["orange"] > .16:                       cat = "peppers"
    else:                                         cat = "unsorted"

    return dict(w=w, h=h, when=when, cat=cat,
                portrait=h > w,
                tone="#%02X%02X%02X" % small.resize((1, 1)).getpixel((0, 0)))


def title_from(stem, when, cat):
    label = dict(CATS).get(cat, "Photo")
    return f"{label}{' · ' + when if when else ''}"


# ---------------------------------------------------------------- gather
def main():
    if not WEBP.is_dir():
        sys.exit(f"No folder at {WEBP}")

    files = sorted(f for f in WEBP.iterdir()
                   if f.is_file()
                   and f.suffix.lower() == ".webp"
                   and f.suffix.lower() not in SKIP_EXT
                   and not f.name.startswith("."))
    if not files:
        sys.exit(f"No .webp files in {WEBP}")

    old = {}
    if DATA.exists():
        try:
            old = {e["file"]: e for e in json.loads(DATA.read_text())}
            print(f"  merging with {len(old)} existing entries")
        except Exception:
            print("  gallery-data.json unreadable, starting fresh")

    rel = WEBP.name if WEBP != ROOT else "."
    items, added = [], 0

    for i, f in enumerate(files, 1):
        if f.name in old:                    # YOUR edits win, always
            e = dict(old[f.name]); e["n"] = i
            items.append(e); continue
        try:
            resize_if_needed(f)
            info = profile(f)
        except Exception as ex:
            print(f"  skipped {f.name} ({ex})"); continue
        items.append(dict(
            n=i, file=f.name, src=f"{rel}/{f.name}",
            title=title_from(f.stem, info["when"], info["cat"]),
            cat=info["cat"], when=info["when"], note="",
            portrait=info["portrait"], tone=info["tone"], keep=True))
        added += 1
        if added % 25 == 0:
            print(f"  ...{added} new")

    DATA.write_text(json.dumps(items, indent=1))

    live = [x for x in items if x.get("keep", True)]
    used = [(k, lbl) for k, lbl in CATS if any(x["cat"] == k for x in live)]
    counts = {k: sum(1 for x in live if x["cat"] == k) for k, _ in used}

    OUT.write_text(page(live, used, counts))

    print(f"\n  {len(files)} webp files, {added} new, "
          f"{len(items)-len(live)} pruned, {len(live)} showing")
    for k, lbl in used:
        print(f"     {lbl:24} {counts[k]}")
    print(f"\n  wrote {OUT.name} and {DATA.name}")
    print(f"  open it:  open {OUT.name}")


# ---------------------------------------------------------------- the page
def page(items, cats, counts):
    tiles = []
    for x in items:
        note = f'<span class="note">{esc(x.get("note",""))}</span>' if x.get("note") else ""
        tiles.append(f'''
    <figure class="tile{' tall' if x.get('portrait') else ''}" data-cat="{x['cat']}" data-n="{x['n']}">
      <span class="n">{x['n']}</span>
      <img loading="lazy" src="{esc(x['src'])}" alt="{esc(x['title'])}" style="background:{x.get('tone','#ccc')}">
      <figcaption>
        <span class="t">{esc(x['title'])}</span>
        <span class="w">{esc(x.get('when','')) or '&nbsp;'}</span>
        {note}
      </figcaption>
    </figure>''')

    chips = '\n      '.join(
        f'<button class="chip" data-f="{k}">{lbl} <em>{counts[k]}</em></button>'
        for k, lbl in cats)

    return TEMPLATE.replace("{{CHIPS}}", chips)\
                   .replace("{{TILES}}", "".join(tiles))\
                   .replace("{{TOTAL}}", str(len(items)))


def esc(s):
    return (str(s).replace("&","&amp;").replace("<","&lt;")
                  .replace(">","&gt;").replace('"',"&quot;"))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Charlotte's Garden · Image Library</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400..900&family=Source+Serif+4:opsz,wght@8..60,300..700&display=swap" rel="stylesheet">
<style>
/* Southwest palette. Every hue sampled from John and Charlotte's own photos,
   then rebuilt on a deliberate lightness ladder and contrast-checked.
     yellow  = the stucco on the house
     burgundy= the metal roof
     orange  = the road out front
     sage    = garden foliage
     teal    = the plaid Charlotte stages produce on            */
:root{
  --sw-yellow-pale:#F7E4B4;   --sw-yellow:#D8B942;
  --sw-orange:#CC7532;        --sw-orange-deep:#A05008;
  --sw-burgundy:#75322D;      --sw-sage:#768149;
  --sw-teal:#096E71;          --sw-teal-light:#6FABAC;
  --sw-ink:#472825;
  --display:'Fraunces',Georgia,serif;
  --body:'Source Serif 4',Georgia,serif;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--body);font-size:17px;line-height:1.6;
  color:var(--sw-ink);background:var(--sw-yellow-pale)}
img{display:block;max-width:100%}

.top{background:var(--sw-teal);color:var(--sw-yellow-pale);
  padding:52px 0 44px;border-bottom:7px solid var(--sw-burgundy)}
.wrap{max-width:1500px;margin:0 auto;padding:0 40px}
.ey{display:flex;align-items:center;gap:12px;margin-bottom:12px;font-size:14px;
  font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--sw-yellow)}
.ey::before{content:'';width:34px;height:1px;background:var(--sw-yellow)}
h1{font-family:var(--display);font-weight:500;font-size:clamp(32px,4.4vw,54px);
  line-height:1.08;color:var(--sw-yellow-pale)}
.sub{margin-top:12px;font-size:16px;color:rgba(247,228,180,.72)}

/* a thin southwest band, colour only, no cowboy anything */
.band{display:flex;height:9px}
.band i{flex:1}
.band i:nth-child(1){background:var(--sw-burgundy)}
.band i:nth-child(2){background:var(--sw-orange)}
.band i:nth-child(3){background:var(--sw-yellow)}
.band i:nth-child(4){background:var(--sw-sage)}
.band i:nth-child(5){background:var(--sw-teal)}

.bar{position:sticky;top:0;z-index:30;background:var(--sw-yellow-pale);
  border-bottom:2px solid var(--sw-burgundy);padding:16px 0;min-height:64px}
.bar-wrap{display:flex;align-items:center;gap:12px}
.bar-logo{display:flex;align-items:center;justify-content:center;width:40px;height:40px;flex-shrink:0;transition:opacity .2s}
.bar-logo:hover{opacity:.7}
.bar-logo img{width:40px;height:40px;display:block}
.chips{display:flex;flex-wrap:wrap;gap:9px;align-items:center}
.chip{font:inherit;font-size:14px;font-weight:600;letter-spacing:.08em;
  text-transform:uppercase;cursor:pointer;padding:9px 15px;border-radius:0;
  border:2px solid var(--sw-burgundy);background:transparent;color:var(--sw-burgundy);
  transition:background .15s,color .15s}
.chip em{font-style:normal;opacity:.6;margin-left:5px}
.chip:hover{background:var(--sw-yellow)}
.chip.on{background:var(--sw-burgundy);color:var(--sw-yellow-pale)}
.chip.on em{opacity:.75}

main{padding:36px 0 90px}
.grid{columns:5 250px;column-gap:18px}
.tile{break-inside:avoid;margin:0 0 18px;position:relative;background:var(--sw-yellow);
  border:3px solid var(--sw-burgundy);cursor:zoom-in;
  transition:transform .18s ease,box-shadow .18s ease}
.tile:hover{transform:translateY(-4px);box-shadow:0 16px 34px rgba(71,40,37,.30);z-index:2}
.tile img{width:100%;height:auto}
.n{position:absolute;top:0;left:0;z-index:3;background:var(--sw-burgundy);
  color:var(--sw-yellow-pale);font-size:12px;font-weight:700;letter-spacing:.06em;
  padding:5px 10px;min-width:38px;text-align:center}
figcaption{padding:11px 12px 12px;background:var(--sw-yellow-pale);
  border-top:2px solid var(--sw-burgundy)}
.t{display:block;font-family:var(--display);font-size:15px;line-height:1.2;
  color:var(--sw-burgundy);font-weight:500}
.w{display:block;margin-top:3px;font-size:14px;font-weight:600;letter-spacing:.08em;
  text-transform:uppercase;color:var(--sw-orange-deep)}
.note{display:block;margin-top:6px;font-size:13px;color:var(--sw-sage)}
.tile.hide{display:none}

.lb{position:fixed;inset:0;z-index:90;background:rgba(30,16,14,.94);
  display:none;align-items:center;justify-content:center;padding:34px;cursor:zoom-out}
.lb.open{display:flex}
.lb img{max-width:94vw;max-height:80vh;width:auto;border:5px solid var(--sw-yellow-pale)}
.lbi{position:fixed;left:0;right:0;bottom:0;padding:16px 24px;text-align:center;
  background:var(--sw-burgundy);color:var(--sw-yellow-pale);font-size:14px}
.lbi b{font-family:var(--display);font-size:19px;font-weight:500}
.lbi span{opacity:.66;margin-left:12px;font-size:12px}

.help{margin-top:26px;padding:22px 24px;background:var(--sw-yellow);
  border:3px solid var(--sw-burgundy);font-size:15px;max-width:900px}
.help b{color:var(--sw-burgundy)}
.help code{background:var(--sw-yellow-pale);padding:1px 6px;font-size:13.5px}

@media(max-width:820px){
  .wrap{padding:0 20px}
  .bar{overflow-x:visible;overflow-y:visible;padding:12px 0;transition:transform .35s cubic-bezier(0.4,0,0.2,1),opacity .35s cubic-bezier(0.4,0,0.2,1)}
  .bar.scrolled{transform:translateY(-100%);opacity:0;pointer-events:none}
  .bar-wrap{padding:0 20px}
  .chips{flex-wrap:nowrap;min-width:min-content;overflow-x:auto}
  .grid{columns:2 150px;column-gap:12px}
  .tile{margin-bottom:12px}
  .top{padding:36px 0 30px}
}
@media(prefers-reduced-motion:reduce){.tile{transition:none}}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="ey">Charlotte's Fresh Organic Produce</div>
    <h1>The Image Library</h1>
    <!-- Image count and correction workflow: {{TOTAL}} photographs, numbered. To rename/move/prune: edit gallery-data.json and re-run build-gallery.py -->
  </div>
</header>
<div class="band"><i></i><i></i><i></i><i></i><i></i></div>

<div class="bar">
  <div class="wrap bar-wrap">
    <a href="/" class="bar-logo" aria-label="Charlotte's Fresh Organic Produce - home">
      <img src="webp/logo.webp" alt="">
    </a>
    <div class="chips">
      <button class="chip on" data-f="all">Everything <em>{{TOTAL}}</em></button>
      {{CHIPS}}
    </div>
  </div>
</div>

<main>
  <div class="wrap">
    <div class="grid">{{TILES}}
    </div>

    <!-- Gallery workflow: Edit gallery-data.json (set "keep": false to prune, edit "title" to rename, change "cat" to recategorise), then re-run python3 build-gallery.py. Edits merge, never overwritten. New photos append. -->
  </div>
</main>

<div class="lb" id="lb">
  <img id="lbimg" src="" alt="">
  <div class="lbi"><b id="lbt"></b><span id="lbf"></span></div>
</div>

<script>
document.querySelectorAll('.chip').forEach(function(c){
  c.addEventListener('click', function(){
    document.querySelectorAll('.chip').forEach(function(o){o.classList.remove('on')});
    c.classList.add('on');
    var f = c.dataset.f;
    document.querySelectorAll('.tile').forEach(function(t){
      t.classList.toggle('hide', f !== 'all' && t.dataset.cat !== f);
    });
  });
});
var lb=document.getElementById('lb'), li=document.getElementById('lbimg'),
    lt=document.getElementById('lbt'), lf=document.getElementById('lbf');
document.querySelectorAll('.tile').forEach(function(t){
  t.addEventListener('click', function(){
    li.src = t.querySelector('img').src;
    lt.textContent = t.querySelector('.t').textContent;
    lf.textContent = '#' + t.dataset.n;
    lb.classList.add('open');
  });
});
lb.addEventListener('click', function(){ lb.classList.remove('open'); });
document.addEventListener('keydown', function(e){
  if(e.key === 'Escape') lb.classList.remove('open');
});

// Bar hide/show on scroll
(function(){
  var bar = document.querySelector('.bar');
  var lastScrollY = 0;
  var scrollDirection = 'up';
  var hysteresis = 70;  // Scroll threshold to prevent jitter

  window.addEventListener('scroll', function(){
    var currentScrollY = window.scrollY;

    if(currentScrollY > lastScrollY + hysteresis){
      // Scrolling down
      if(scrollDirection !== 'down'){
        scrollDirection = 'down';
        bar.classList.add('scrolled');
      }
    } else if(currentScrollY < lastScrollY - hysteresis){
      // Scrolling up - immediate reveal for responsiveness
      if(scrollDirection !== 'up'){
        scrollDirection = 'up';
        bar.classList.remove('scrolled');
      }
    }

    lastScrollY = currentScrollY;
  }, {passive:true});
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
