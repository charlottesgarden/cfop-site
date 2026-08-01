#!/usr/bin/env python3
import pathlib

path = pathlib.Path("site/index.html")
text = path.read_text()

EASTER_EGGS = """
<style>
.bee-fly{position:fixed;top:20%;left:-60px;font-size:28px;z-index:500;pointer-events:none;opacity:0}
.bee-fly.active{animation:bee-path 9s linear forwards}
@keyframes bee-path{
  0%{left:-60px;top:22%;opacity:0;transform:rotate(0deg)}
  8%{opacity:1}
  25%{top:12%;transform:rotate(-8deg)}
  50%{top:30%;transform:rotate(6deg)}
  75%{top:16%;transform:rotate(-4deg)}
  92%{opacity:1}
  100%{left:110%;top:24%;opacity:0;transform:rotate(0deg)}
}
body.dusk{filter:brightness(0.88) saturate(1.08) hue-rotate(-6deg);transition:filter 1.2s ease}
.luffa-toast{position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--aubergine-deep);color:var(--cream);padding:14px 24px;border-radius:6px;font-family:'Bodoni Moda',Georgia,serif;font-size:15px;box-shadow:0 8px 24px rgba(0,0,0,0.25);z-index:999;opacity:0;pointer-events:none;transition:opacity 0.35s,transform 0.35s}
.luffa-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.brand-mark{cursor:pointer}
</style>
<script>
(function(){
  function spawnBee(){
    var bee=document.createElement('div');
    bee.className='bee-fly active';
    bee.textContent='\\u{1F41D}';
    document.body.appendChild(bee);
    setTimeout(function(){bee.remove();},9200);
    scheduleBee();
  }
  function scheduleBee(){
    setTimeout(spawnBee,45000+Math.random()*45000);
  }
  scheduleBee();

  var mark=document.querySelector('.brand-mark');
  if(mark){
    mark.addEventListener('click',function(){
      document.body.classList.toggle('dusk');
    });
  }

  var buffer='';
  var toastTimer=null;
  window.addEventListener('keydown',function(e){
    if(e.key.length!==1) return;
    buffer=(buffer+e.key).slice(-5).toLowerCase();
    if(buffer==='luffa'){
      var toast=document.querySelector('.luffa-toast');
      if(!toast){
        toast=document.createElement('div');
        toast.className='luffa-toast';
        toast.textContent='Still not a sea sponge.';
        document.body.appendChild(toast);
      }
      toast.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer=setTimeout(function(){toast.classList.remove('show');},3200);
      buffer='';
    }
  });
})();
</script>
"""

replacements = [
    ("meta_description",
     '<meta name="description" content="Drought-tested, organically grown produce and seeds from Charlotte\'s garden in Colorado City, Arizona. Open Saturdays 10AM, in season.">',
     '<meta name="description" content="Organically grown produce and seeds from Charlotte\'s garden in Colorado City, Arizona \u2014 open Saturdays at 10AM, in season.">'
    ),
    ("easter_eggs",
     '</body>',
     EASTER_EGGS + '</body>'
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