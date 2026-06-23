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
  /* Start gate: a real button the player taps, so requestFullscreen() runs
     inside a genuine user gesture (the only way browsers allow it). Hidden once
     the game has started. */
  #fs-gate {{
    position: fixed; inset: 0; z-index: 2147483000;
    display: flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at 50% 38%, #06245e, #001026 72%);
    font-family: Arial, Helvetica, sans-serif; color: #eaf1ff; text-align: center;
  }}
  body.started #fs-gate {{ display: none; }}
  #fs-gate .fg-title {{ font-size: 24px; font-weight: bold; letter-spacing: .5px; margin-bottom: 26px; }}
  #fs-btn {{
    -webkit-appearance: none; appearance: none; border: 0; cursor: pointer;
    background: #ffcd00; color: #06245e; font-weight: bold; font-family: inherit;
    font-size: 22px; padding: 16px 46px; border-radius: 999px; box-shadow: 0 6px 0 #b88f00;
  }}
  #fs-btn:active {{ transform: translateY(3px); box-shadow: 0 3px 0 #b88f00; }}
  #fs-gate .fg-sub {{ margin-top: 18px; font-size: 14px; opacity: .75; }}
  /* Loading screen with progress bar, shown after JOGAR until the game boots so
     the player never stares at a blank screen wondering if it is working. */
  #loading {{
    position: fixed; inset: 0; z-index: 2147482000; display: none;
    flex-direction: column; align-items: center; justify-content: center;
    background: radial-gradient(circle at 50% 38%, #06245e, #001026 72%);
    font-family: Arial, Helvetica, sans-serif; color: #eaf1ff;
  }}
  body.loading #loading {{ display: flex; }}
  #loading .ld-title {{ font-size: 20px; font-weight: bold; margin-bottom: 22px; }}
  #loading .ld-track {{
    width: 62%; max-width: 360px; height: 12px; border-radius: 999px;
    background: rgba(255,255,255,.15); overflow: hidden; position: relative;
  }}
  #loading .ld-fill {{
    position: absolute; top: 0; left: 0; height: 100%; width: 35%;
    border-radius: 999px; background: #ffcd00;
  }}
  #loading.indet .ld-fill {{ animation: ld-slide 1.1s ease-in-out infinite; }}
  @keyframes ld-slide {{ 0% {{ left: -40%; width: 40%; }} 50% {{ width: 55%; }} 100% {{ left: 100%; width: 40%; }} }}
  #loading .ld-status {{ margin-top: 16px; font-size: 13px; opacity: .7; min-height: 1em; }}
</style>
{END}"""

BODY_BLOCK = f"""{START}
<div id="rotate-lock">
  <div class="ico">&#128241;</div>
  <div class="t1">Rode o telemovel</div>
  <div class="t2">Please rotate your device to landscape</div>
</div>
<div id="fs-gate">
  <div>
    <div class="fg-title">Cabo Verde &mdash; Mundial 2026</div>
    <button id="fs-btn">&#9654;&nbsp; JOGAR</button>
    <div class="fg-sub">Toque para jogar em ecra inteiro</div>
  </div>
</div>
<div id="loading">
  <div class="ld-title">A carregar o jogo&hellip;</div>
  <div class="ld-track"><div class="ld-fill"></div></div>
  <div class="ld-status">A iniciar&hellip;</div>
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

  // --- Start gate / fullscreen ----------------------------------------------
  var docEl = document.documentElement;
  function fsRequest() {{ return docEl.requestFullscreen || docEl.webkitRequestFullscreen || docEl.mozRequestFullScreen || docEl.msRequestFullscreen; }}
  function fsElement() {{ return document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement; }}
  var fsSupported = !!fsRequest();

  // --- Loading screen --------------------------------------------------------
  var loadingEl = document.getElementById('loading');
  var loadTimer = null;
  function bootedCanvas() {{
    var c = document.getElementById('canvas');
    return c && c.width > 1;
  }}
  function showLoading() {{
    if (!loadingEl) return;
    document.body.classList.add('loading');
    loadingEl.classList.add('indet');
    if (loadTimer) return;
    loadTimer = setInterval(function () {{
      if (bootedCanvas()) {{           // game is up -> drop the loader
        document.body.classList.remove('loading');
        clearInterval(loadTimer); loadTimer = null; fitCanvas(); return;
      }}
      // Mirror pygbag's own status text so the player sees real stages.
      var ib = document.getElementById('infobox');
      var st = loadingEl.querySelector('.ld-status');
      if (ib && st) {{ var t = (ib.innerText || '').trim(); if (t) st.textContent = t; }}
      // If pygbag exposes a real download figure, switch to a determinate bar.
      var pr = document.getElementById('progress');
      var fill = loadingEl.querySelector('.ld-fill');
      if (pr && fill && pr.value > 0 && pr.value < pr.max) {{
        loadingEl.classList.remove('indet');
        fill.style.width = (100 * pr.value / pr.max) + '%';
      }}
    }}, 200);
  }}

  function lockLandscape() {{
    // Only valid once a fullscreen element exists; pin the orientation so
    // rotating the phone no longer flips the game.
    try {{
      if (screen.orientation && screen.orientation.lock) {{
        var lr = screen.orientation.lock('landscape');
        if (lr && lr.catch) lr.catch(function () {{}});
      }}
    }} catch (e) {{}}
  }}

  var started = false;
  function startGame() {{
    if (started) return;
    started = true;
    // Must run synchronously inside this tap for the browser to allow it. The
    // orientation lock can only be applied once fullscreen is actually active,
    // so do it when the request resolves / on fullscreenchange, not now.
    var req = fsRequest();
    if (req) {{
      try {{
        var r = req.call(docEl);
        if (r && r.then) r.then(lockLandscape, function () {{}});
        else lockLandscape();
      }} catch (e) {{}}
    }}
    document.body.classList.add('started');
    if (!bootedCanvas()) showLoading();
    fitCanvas();
  }}

  var btn = document.getElementById('fs-btn');
  if (btn) btn.addEventListener('click', startGame);

  // Enforce fullscreen-only ONLY where the browser actually supports it: if the
  // player leaves fullscreen, bring the gate back. On platforms without the
  // Fullscreen API (e.g. iPhone Safari) we skip this so the game is still
  // playable instead of being soft-locked behind a button that can't work.
  if (fsSupported) {{
    function onFsChange() {{
      if (fsElement()) {{
        lockLandscape();                  // entered fullscreen -> pin orientation
      }} else if (started) {{
        started = false;                  // left fullscreen -> show the gate again
        document.body.classList.remove('started');
      }}
    }}
    document.addEventListener('fullscreenchange', onFsChange);
    document.addEventListener('webkitfullscreenchange', onFsChange);
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
