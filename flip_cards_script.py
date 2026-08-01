#!/usr/bin/env python3
import pathlib

path = pathlib.Path("site/index.html")
text = path.read_text()

replacements = [
    ("tomato_card",
     '''<div class="flip-face flip-front">
            <div class="tag"><div class="eyebrow">Heirloom Tomato</div><h3>Cherokee Purple</h3></div>
          </div>''',
     '''<div class="flip-face flip-front" style="background-image:linear-gradient(0deg,rgba(20,14,10,0.55),rgba(20,14,10,0.1)),url('../images/webp/IMG_0614.webp');background-size:cover;background-position:center">
            <div class="tag"><div class="eyebrow">Heirloom Tomato</div><h3>Cherokee Purple</h3></div>
          </div>'''
    ),
    ("sunflower_card",
     '''<div class="flip-face flip-front">
            <div class="tag"><div class="eyebrow">Flower</div><h3>Lemon Queen Sunflower</h3></div>
          </div>''',
     '''<div class="flip-face flip-front" style="background-image:linear-gradient(0deg,rgba(20,14,10,0.55),rgba(20,14,10,0.1)),url('../images/webp/PXL_20240831_013053462%202.webp');background-size:cover;background-position:center">
            <div class="tag"><div class="eyebrow">Flower</div><h3>Lemon Queen Sunflower</h3></div>
          </div>'''
    ),
    ("produce_card",
     '''<div class="flip-face flip-front">
            <div class="tag"><div class="eyebrow">In Season</div><h3>Fresh Produce</h3></div>
          </div>''',
     '''<div class="flip-face flip-front" style="background-image:linear-gradient(0deg,rgba(20,14,10,0.55),rgba(20,14,10,0.1)),url('../images/webp/PXL_20210724_013539146.webp');background-size:cover;background-position:center">
            <div class="tag"><div class="eyebrow">In Season</div><h3>Fresh Produce</h3></div>
          </div>'''
    ),
    ("seed_card",
     '''<div class="flip-face flip-front">
            <div class="tag"><div class="eyebrow">Coming Soon</div><h3>Seed Packets</h3></div>
          </div>''',
     '''<div class="flip-face flip-front" style="background-image:linear-gradient(0deg,rgba(20,14,10,0.55),rgba(20,14,10,0.1)),url('../images/webp/PXL_20240828_014733573.webp');background-size:cover;background-position:center">
            <div class="tag"><div class="eyebrow">Coming Soon</div><h3>Seed Packets</h3></div>
          </div>'''
    ),
    ("card_note",
     '<p class="card-note">Card photos are placeholders, swap in real produce shots whenever you\'re ready. Hover or tap a card to flip it.</p>',
     '<p class="card-note">Hover or tap a card to flip it.</p>'
    ),
]

for name, old, new in replacements:
    if old in text:
        text = text.replace(old, new, 1)
        print(f"OK: {name}")
    else:
        print(f"NO MATCH: {name}")

path.write_text(text)
print("done")