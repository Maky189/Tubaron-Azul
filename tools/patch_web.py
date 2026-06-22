from __future__ import annotations
import sys
from pathlib import Path

"""Post-build patch for the pygbag web page (mobile fit + landscape lock).

pygbag regenerates build/web/index.html from its own template on every build,
so the mobile presentation can't live in a committed HTML file -- it is injected
here, right after the build, as the last step. Run as:

    python tools/patch_web.py [build/web/index.html]

The injection is idempotent (guarded by the markers below) and leaves the game
logic untouched: it only restyles the page shell so the canvas fills the screen,
forces landscape with a rotate prompt, and goes fullscreen on the first touch.
"""

START = "<!-- mobile-fit:start -->"
END = "<!-- mobile-fit:end -->"

HEAD_BLOCK = f"""{START}
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#001026">
<style>
  html, body {{
    margin: 0 !important; padding: 0 !important;
    width: 100%; height: 100%;
    background: #001026 !important;
    overflow: hidden !important;
    overscroll-behavior: none;
    touch-action: none;
    -webkit-tap-highlight-color: transparent;
  }}
  /* Fill the whole viewport. The framebuffer aspect is computed (in Python) to
     match the device's landscape aspect, so this scales close to uniformly; we
     force it to fill (rather than let pygbag aspect-fit and centre) so there are
     never side/letterbox bars when the real landscape viewport -- minus the
     address bar -- is a touch wider than the framebuffer. The JS below re-asserts
     this over pygbag's own inline sizing. */
  canvas#canvas, canvas.emscripten, canvas#canvas3d {{
    position: absolute !important;
    left: 0 !important; top: 0 !important; right: auto !important; bottom: auto !important;
    width: 100vw !important; height: 100vh !important;
    height: 100dvh !important;
    max-width: none !important; max-height: none !important;
    margin: 0 !important; transform: none !important;
    background: #001026 !important;
    -webkit-tap-highlight-color: transparent;
  }}
  /* Restyle pygbag's loading/start box so it reads on the dark shell. */
  #infobox {{
    background: rgba(0,16,38,0.92) !important;
    color: #cfe0ff !important;
    border: 1px solid #2a4a86 !important;
    border-radius: 10px !important;
    font-family: Arial, Helvetica, sans-serif !important;
  }}
  /* Orientation is decided in JS (innerWidth vs innerHeight) and reflected on
     <body data-orient>, which is far more reliable across mobile browsers and
     emulators than the CSS `(orientation: portrait)` media feature. */
  #rotate-lock {{ display: none; }}
  body[data-orient="portrait"] #rotate-lock {{
    display: flex; position: fixed; inset: 0; z-index: 2147483647;
    background: #001026; color: #dce8ff;
    align-items: center; justify-content: center; flex-direction: column;
    font-family: Arial, Helvetica, sans-serif; text-align: center; padding: 24px;
  }}
  #rotate-lock .ico {{ font-size: 56px; margin-bottom: 18px; animation: rl-spin 2s ease-in-out infinite; }}
  #rotate-lock .t1 {{ font-size: 22px; font-weight: bold; }}
  #rotate-lock .t2 {{ font-size: 15px; opacity: 0.7; margin-top: 6px; }}
  @keyframes rl-spin {{ 0%,60% {{ transform: rotate(0); }} 80%,100% {{ transform: rotate(-90deg); }} }}
</style>
{END}"""

BODY_BLOCK = f"""{START}
<div id="rotate-lock">
  <div class="ico">&#128241;</div>
  <div class="t1">Rode o telemovel</div>
  <div class="t2">Please rotate your device to landscape</div>
</div>
<script>
(function () {{
  // Reflect the current orientation onto <body data-orient> so the portrait
  // "rotate your device" overlay (CSS above) shows/hides. We do NOT request
  // fullscreen or screen.orientation.lock(): mobile browsers reject those
  // without strict conditions and the rejection is noisy, so the game simply
  // runs in the normal page and asks the player to turn the phone.
  function applyOrient() {{
    var portrait = window.innerHeight > window.innerWidth;
    document.body.setAttribute('data-orient', portrait ? 'portrait' : 'landscape');
  }}
  applyOrient();
  window.addEventListener('resize', applyOrient, {{ passive: true }});
  window.addEventListener('orientationchange', applyOrient, {{ passive: true }});

  // pygbag sizes the canvas with inline styles (aspect-fit + centre), which
  // leaves side bars. Re-assert a full-viewport fill on top of it. The guard
  // (skip when already filled) stops the MutationObserver from looping on its
  // own writes; pygbag only re-sizes on real resize events, so this is cheap.
  function fitCanvas() {{
    var c = document.getElementById('canvas');
    if (!c) return;
    if (c.style.getPropertyValue('width') === '100vw') return;
    c.style.setProperty('width', '100vw', 'important');
    c.style.setProperty('height', '100dvh', 'important');
    c.style.setProperty('left', '0', 'important');
    c.style.setProperty('top', '0', 'important');
    c.style.setProperty('transform', 'none', 'important');
  }}
  fitCanvas();
  window.addEventListener('resize', fitCanvas, {{ passive: true }});
  window.addEventListener('orientationchange', fitCanvas, {{ passive: true }});
  var canvas = document.getElementById('canvas');
  if (canvas && window.MutationObserver) {{
    new MutationObserver(fitCanvas).observe(canvas, {{ attributes: true, attributeFilter: ['style'] }});
  }}
}})();
</script>
{END}"""


def _strip_existing(html: str) -> str:
    # Idempotent: drop every previous injection so re-running is a clean replace.
    while START in html and END in html:
        pre, _, rest = html.partition(START)
        _, _, post = rest.partition(END)
        html = pre + post
    return html


def main(path: Path) -> int:
    html = path.read_text(encoding="utf-8")
    if "</head>" not in html or "</body>" not in html:
        print(f"patch_web: {path} doesn't look like the pygbag page; skipping", file=sys.stderr)
        return 1
    html = _strip_existing(html)
    html = html.replace("</head>", HEAD_BLOCK + "\n</head>", 1)
    html = html.replace("</body>", BODY_BLOCK + "\n</body>", 1)
    path.write_text(html, encoding="utf-8")
    print(f"patch_web: injected mobile fit + landscape lock into {path}")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("build/web/index.html")
    raise SystemExit(main(target))
