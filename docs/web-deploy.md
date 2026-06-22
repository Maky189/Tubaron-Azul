# Web build & deployment (Cloudflare Pages)

The game runs in the browser via **pygbag**, which compiles the Pygame code to
WebAssembly. Keyboard works on desktop; on touchscreens an on-screen control pad
appears automatically (it stays hidden until the first touch, so desktop players
never see it).

On phones the game is **landscape-only**: a "rotate your device" prompt covers
the page in portrait, and the internal resolution is widened at startup to the
device's landscape aspect ratio (keeping a 540px reference height) so the canvas
fills the screen with no letterbox and no distortion. (We deliberately do *not*
force fullscreen or `screen.orientation.lock()` — mobile browsers reject those
without strict gesture conditions, so the game just runs in the normal page.)
This lives in `engine/platform_bridge.py` (resolution) and `tools/patch_web.py`
(page shell + orientation), and is inert on desktop.

## Build locally

```sh
python -m venv .venv-build           # keep the venv OUTSIDE the repo if you can;
                                     # if it lives in ./.venv it's excluded via pygbag.ini
source .venv-build/Scripts/activate  # (Windows: .venv-build\Scripts\Activate.ps1)
pip install -r requirements-dev.txt

# Dev server with hot reload — open the printed http://localhost:8000
python -m pygbag --width 960 --height 540 main.py

# Or produce static files only (no server) into build/web/
python -m pygbag --build --width 960 --height 540 \
    --app_name TubaraoAzul --title "Cabo Verde - Mundial 2026" main.py
python tools/patch_web.py build/web/index.html   # mobile fit + landscape lock
```

> The `--width/--height` here only seed pygbag's template; the running game
> overrides the resolution per device (see the landscape note above).

`build/web/` then contains `index.html`, the `.apk` data bundle, and a favicon.

### What gets bundled
`pygbag.ini` controls the bundle. It excludes the local `.venv`, `docs/`,
`tests/`, and the three raw player photos at the repo root (`player.png`,
`player_kick.png`, `vozinha.png`) — those are only inputs to
`tools/process_players.py`, and their processed sprites are already committed
under `assets/players/`. pygbag does **not** read `.gitignore`, so anything you
want kept out of the web build must be listed in `pygbag.ini`.

## Deploy to Cloudflare Pages

pygbag needs the page to be **cross-origin isolated** (it uses
`SharedArrayBuffer`). The repo's `_headers` file sets the two required headers;
it must land in the published directory next to `index.html`.

In the Cloudflare Pages dashboard, connect the GitHub repo and set:

- **Framework preset:** None
- **Build command** — paste as a **single line, no `\` continuations** (the
  dashboard field is one line; backslashes get mangled and the shell fails with
  `python: not found`). Use `python3`, not `python` (bare `python` isn't on
  Cloudflare's build PATH):
  ```sh
  pip install -r requirements-dev.txt && python3 -m pygbag --build --width 960 --height 540 --app_name TubaraoAzul --title "Cabo Verde - Mundial 2026" main.py && python3 tools/patch_web.py build/web/index.html && cp _headers build/web/_headers
  ```
- **Build output directory:** `build/web`
- **Environment variable:** `PYTHON_VERSION = 3.12` (Cloudflare's default Python
  is fine for running pygbag, which only packages files; the game itself runs as
  WebAssembly in the visitor's browser).

After the first deploy, confirm in DevTools → Network → the document response
that both `Cross-Origin-Opener-Policy: same-origin` and
`Cross-Origin-Embedder-Policy: credentialless` are present. `credentialless` (not
`require-corp`) is required: pygbag pulls the CPython interpreter and pygame from
the cross-origin `pygame-web.github.io` CDN, which sends no `Cross-Origin-
Resource-Policy` header, so `require-corp` blocks those loads and the game hangs
on "Loading, please wait". If the canvas stays black, a missing or wrong header
is the usual cause.

### Audio note
Browsers block audio until the player interacts with the page. pygbag shows a
"click to start" gate (`--ume_block`, on by default) which doubles as the audio
unlock, so music begins on first interaction — no code change needed.

## Saves
In-browser saves currently live in the WebAssembly in-memory filesystem: a run
persists while the tab is open but resets on reload. Making saves survive a
reload (IndexedDB-backed storage with `syncfs()`) is a self-contained follow-up.
