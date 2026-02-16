# Py-Playground

## Project Overview
A portfolio website that runs Python turtle and pygame simulations directly in the browser. Turtle sims use Pyodide + RPi Foundation's SVG turtle library; pygame sims use PyScript. Deployed on GitHub Pages at `dev-arctik.github.io/py-playground/`.

## Tech Stack
- **Turtle projects:** Pyodide (v0.26.4) + [RPi Foundation turtle wheel](https://github.com/RaspberryPiFoundation/turtle) — renders to SVG (not canvas). The standard `turtle` module is removed from Pyodide due to tkinter dependency.
- **Pygame projects:** PyScript (`<script type="py-game">`) — runs pygame-ce via Pyodide with a `<canvas>` element
- **Landing page:** Pure HTML/CSS, dark theme, responsive grid
- **Deployment:** GitHub Pages from main branch

## Project Structure
```
py-playground/                     # Target structure (to be created during implementation)
├── pyproject.toml              # Poetry config — needed for local execution
├── index.html                  # Landing page gallery (dark theme)
├── assets/style.css            # Shared landing page styles
├── turtle/
│   ├── index.html              # Shared turtle player (Pyodide + RPi turtle, reads ?sim= param)
│   ├── turtle-0.0.1-py3-none-any.whl  # RPi Foundation SVG turtle wheel
│   ├── flower/main.py
│   ├── polygon/main.py
│   ├── curved-graph/main.py
│   ├── chaos-pi-e/main.py
│   ├── sierpinski-triangle/main.py
│   ├── barnsley-fern/main.py
│   └── fractal-tree/main.py
├── pygame/
│   ├── index.html              # Shared pygame player (reads ?sim= param)
│   ├── moving-square/main.py
│   ├── jumping-square/main.py
│   ├── pendulum/main.py
│   ├── sine-wave/main.py
│   ├── sierpinski-triangle/main.py
│   ├── paint-board/main.py
│   ├── paint-random-screen/main.py
│   ├── paint-random-color/main.py
│   ├── rgb-strips/main.py
│   ├── first-game/             # Has pyscript.toml + assets/
│   │   ├── main.py
│   │   ├── pyscript.toml
│   │   └── assets/
│   └── minesweeper/            # Has pyscript.toml + assets/
│       ├── main.py
│       ├── pyscript.toml
│       └── assets/
├── docs/
│   └── planning/
│       ├── 2026-02-16-turtle-projects.md
│       └── 2026-02-16-pygame-projects.md
└── CLAUDE.md
```

## Key Conventions

### Architecture: Shared Player Pages
- Only **3 HTML files** total: `index.html` (landing), `turtle/index.html` (player), `pygame/index.html` (player)
- All Python code lives in `.py` files — **never inline in HTML**
- Landing page cards link to `turtle/?sim=flower`, `pygame/?sim=moving-square`, etc.

**Turtle player** (`turtle/index.html`):
- Uses **Pyodide directly** (not PyScript) — loads `https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js`
- Loads RPi Foundation turtle wheel (`turtle-0.0.1-py3-none-any.whl`) for SVG rendering
- Registers a fake `basthon` JS module, fetches `<sim>/main.py`, runs it via `runPythonAsync()`, then calls `show_scene()` to render SVG
- Disables animations (`turtle.Screen().animation('off')`) for static SVG output
- `tracer()`, `begin_fill()`/`end_fill()` are not fully supported — sims render as line drawings

**Pygame player** (`pygame/index.html`):
- Uses **PyScript CDN** (2024.1.1 stable): `https://pyscript.net/releases/2024.1.1/core.js`
- Injects `<script type="py-game" src="<sim>/main.py">` with `<canvas id="canvas">`

### Dual-Mode Python Files
- Every `main.py` wraps code in `async def main()` — works in both browser and locally
- Environment detection: `asyncio.get_running_loop()` succeeds in Pyodide (browser), raises `RuntimeError` locally
- **Turtle sims (browser):** Player page calls `await main()` via `runPythonAsync()` — the try block detects the loop and does nothing
- **Pygame sims (browser):** `loop.create_task(main())` schedules in PyScript's existing event loop
- **Local:** `asyncio.run(main())` + cleanup (`turtle.exitonclick()` or `pygame.quit()`)
- Run locally: `poetry run python turtle/flower/main.py` or `poetry run python pygame/moving-square/main.py` (requires tkinter for turtle, pygame-ce for pygame)
- `await asyncio.sleep(0)` yields to browser event loop; returns instantly when run locally

### Turtle simulations
- Each sim is a folder in `turtle/<name>/` containing `main.py`
- Remove `exitonclick()`, `mainloop()`, and `print()` calls from inside `async def main()`
- Local cleanup: `turtle.exitonclick()` in the `except RuntimeError` block (see dual-mode pattern above)
- Cap infinite loops and large iteration counts to avoid freezing the browser
- Add `await asyncio.sleep(0)` periodically in long-running loops

### Pygame simulations
- Each sim is a folder in `pygame/<name>/` containing `main.py`
- Only First Game and Minesweeper need `pyscript.toml` + `assets/`
- Match original frame rates: `delay(ms)` → `await asyncio.sleep(ms/1000)`, `clock.tick(fps)` → `await asyncio.sleep(1/fps)`
- Local cleanup: `pygame.quit()` in the `except RuntimeError` block (see dual-mode pattern above)
- Use `pygame.font.Font(None, size)` instead of `SysFont` (no system fonts in browser)
- Keep `pygame.display.set_caption()` calls as-is — no visible effect in browser UI but preserves local execution and may assist accessibility tools

### Code comments
- Add `# Original repo: dev-arctik/<repo-name>` as the first line of every converted script
- Keep comments concise — explain adaptations made for browser compatibility

### Theme conventions
- **Unified dark theme** across all pages — landing page, turtle player, pygame player
- Typography: Instrument Serif (headings) + IBM Plex Mono (body) via Google Fonts
- Background: deep charcoal (`#08080d`) with dot grid pattern + film-grain SVG overlay
- Accent colors: teal (`#00d4aa`) for turtle, orange (`#ff6b35`) for pygame
- SVG canvas frame stays white (`#ffffff`) as a lightbox — artwork needs contrast

### Landing page (`index.html`)
- Each simulation gets a card with: name, description, category badge (Turtle teal / Pygame orange), demo link
- "Coming soon" badge (gray, dashed border) for simulations not yet ported
- Responsive CSS grid, staggered card entrance animations
- Cards link to `turtle/?sim=<name>` or `pygame/?sim=<name>`
- See `assets/style.css` for shared landing page styles

## Source Repos
All original Python code lives in `github.com/dev-arctik/` repos:
- **Turtle (7):** Python-Turtle (Polygon, Sierpinski, Curved Graph, Barnsley Fern, Fractal Tree, Flower, Chaos PI+E)
- **Pygame (11):** Moving-Square, Paint-board, Jumping-Square-, Python-Game, Sierpinski-s-Triangle, Pendulum, Sine-Wave, Paint-Canvas (3 scripts), python-minesweeper

## Build Order
0. Create `pyproject.toml` and run `poetry install`:
   ```toml
   [tool.poetry]
   name = "py-playground"
   version = "0.1.0"
   description = "Python turtle and pygame simulations in the browser"
   package-mode = false  # Not a Python package — just scripts

   [tool.poetry.dependencies]
   python = ">=3.12"
   pygame-ce = ">=2.4,<3"  # Should approximate Pyodide's bundled pygame-ce version
   numpy = "*"

   [build-system]
   requires = ["poetry-core>=2.0"]
   build-backend = "poetry.core.masonry.api"
   ```
1. Create shared player pages (`turtle/index.html`, `pygame/index.html`) and shared CSS
2. Convert turtle projects (simplest first: Flower → Fractal Tree)
3. Pygame Phase 1: Simple conversions (Moving Square, Jumping Square, Pendulum, Sine Wave, Sierpinski)
4. Pygame Phase 2: Interactive conversions (Paint-board, Paint Random Screen, Paint Random Color, RGB Strips)
5. Pygame Phase 3: Evaluate and attempt complex projects (First Game, Minesweeper) — mark "coming soon" if blocked
6. Finalize landing page, test all sims locally + in browser, deploy to GitHub Pages

## Runtime Version Upgrades
**Pyodide (turtle player):**
- CDN: `https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js`
- Update in `turtle/index.html` — test all 7 turtle sims before committing

**PyScript (pygame player):**
- CDN: `https://pyscript.net/releases/2024.1.1/core.js`
- Update in `pygame/index.html` — test all 11 pygame sims before committing

**When to upgrade:** critical security fixes, compatibility issues, or a new release unblocks "coming soon" projects
**If any sim breaks:** revert the upgrade or fix the compatibility issue first

## Planning Docs
- **Turtle plan:** `docs/planning/2026-02-16-turtle-projects.md` — 7 turtle conversions with per-project conversion notes
- **Pygame plan:** `docs/planning/2026-02-16-pygame-projects.md` — 11 pygame conversions (9 simple + 2 complex)

## Important Rules
- Read the relevant planning doc before starting any conversion (turtle or pygame)
- Never skip a simulation — port all of them or mark as "coming soon"
- Test each `main.py` runs locally (`poetry run python <path>/main.py`) AND in browser before moving to the next
- Keep original code logic intact — only adapt for browser compatibility
- Projects marked "coming soon" should be retried after PyScript version upgrades or when upstream blockers (pygame-ce, Pyodide) are resolved
