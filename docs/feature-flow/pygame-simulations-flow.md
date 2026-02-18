# Flow: Pygame Simulations

**Last Updated:** 2026-02-18
**Status:** Active

---

## Overview

A unified system for running 11 Python pygame simulations in the browser using PyScript 2025.3.1 with pygame-ce (Pygame Community Edition compiled to WebAssembly). All simulations are served by a single shared player page that injects the correct Python script dynamically based on a URL parameter, rendering game output to an HTML5 `<canvas>` element. Nine simulations are standalone scripts with no external assets; two (First Game and Minesweeper) require `pyscript.toml` to map image assets into Pyodide's virtual filesystem.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         Browser Environment                               │
│                                                                           │
│  User visits:                                                             │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ Landing Page (index.html)                          │                  │
│  │ - Dark theme gallery of simulation cards           │                  │
│  │ - Links: pygame/?sim=moving-square, etc.           │                  │
│  └────────────────┬───────────────────────────────────┘                  │
│                   │ Click sim card                                       │
│                   ↓                                                       │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ Player Page (pygame/index.html?sim=<name>)         │                  │
│  │ - Reads ?sim= param, looks up SIMS metadata        │                  │
│  │ - Sets canvas dimensions from SIMS[sim].size       │                  │
│  │ - Injects <script type="py-game" src="<name>/main.py">│               │
│  │ - For asset sims: adds config="<name>/pyscript.toml"│                 │
│  │ - Appends tag to <body> AFTER <canvas>             │                  │
│  └────────────────┬───────────────────────────────────┘                  │
│                   │ PyScript CDN core.js (type="module", deferred)       │
│                   ↓                                                       │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ PyScript Bootstrap (2025.3.1)                       │                  │
│  │ - Loads Pyodide (CPython WASM) + pygame-ce         │                  │
│  │ - If pyscript.toml present: fetches & maps assets  │                  │
│  │ - into Pyodide's virtual filesystem                │                  │
│  └────────────────┬───────────────────────────────────┘                  │
│                   │ type="py-game" execution                             │
│                   ↓                                                       │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ Simulation Code (pygame/<name>/main.py)            │                  │
│  │ - Top-level try/except detects browser event loop  │                  │
│  │ - Browser: loop.create_task(main())                │                  │
│  │ - main() calls pygame.init(), set_mode(), game loop│                  │
│  └────────────────┬───────────────────────────────────┘                  │
│                   │ pygame-ce renders frames                             │
│                   ↓                                                       │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ HTML5 Canvas + Event System                        │                  │
│  │ - pygame-ce blits surfaces to <canvas id="canvas"> │                  │
│  │ - Browser keyboard/mouse events forwarded to       │                  │
│  │   pygame.event queue by PyScript runtime           │                  │
│  └────────────────────────────────────────────────────┘                  │
│                                                                           │
│  Loading overlay hides when:                                             │
│  1. py:ready event fires (PyScript interpreter ready), OR                │
│  2. document.title changes (pygame.display.set_caption → title change),  │
│  3. OR 30s timeout fires as final fallback                               │
│                                                                           │
│  Alternative flow — No sim selected:                                     │
│  pygame/index.html (no ?sim=) → Shows grid of all 11 sims as cards      │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## User Flow

1. User visits landing page at `index.html`
2. User scrolls to "Pygame" section (11 simulation cards)
3. User clicks a simulation card (e.g., "Moving Square")
4. Browser navigates to `pygame/?sim=moving-square`
5. Player page shows loading overlay with spinner while PyScript + Pyodide download (~15 MB on first visit)
6. PyScript bootstraps pygame-ce; loading overlay hides when `py:ready` fires or page title changes
7. Game canvas appears; keyboard focus is automatically set (`canvas.focus()` in `hideLoading()`)
8. User interacts with the simulation via keyboard and/or mouse
9. User clicks "Back to Gallery" to return to landing page

**Edge case:** User navigates to `pygame/` with no `?sim=` parameter — player shows a grid of all 11 simulation cards as internal navigation

---

## Technical Flow

### Frontend

| Component | File | Line(s) | Purpose |
|-----------|------|---------|---------|
| Landing page gallery | `index.html` | 83-139 | Pygame section with 11 cards linking to `pygame/?sim=<name>` |
| Shared player page | `pygame/index.html` | 1-502 | Single-page player for all pygame sims; injects `<script type="py-game">` |
| Sim metadata config | `pygame/index.html` | 14-26 | SIMS object mapping sim names to titles, descriptions, canvas sizes, and config flag |
| URL param parsing | `pygame/index.html` | 28-33 | Reads `?sim=` param, sets `document.title` immediately |
| PyScript CSS import | `pygame/index.html` | 10 | `core.css` from PyScript CDN 2025.3.1 |
| PyScript JS import | `pygame/index.html` | 34 | `core.js` as `type="module"` (always deferred) from CDN 2025.3.1 |
| Canvas element | `pygame/index.html` | 391 | `<canvas id="canvas" tabindex="0">` — `tabindex` ensures keyboard focus without a click |
| Loading overlay | `pygame/index.html` | 393-397 | Absolute-positioned overlay with spinner; sits above canvas until game starts |
| Error state div | `pygame/index.html` | 400 | Hidden `<div id="error">` for displaying runtime errors |
| Canvas dimension setup | `pygame/index.html` | 418-422 | Sets `canvas.width` and `canvas.height` from `meta.size` to match original `set_mode()` |
| Script tag injection | `pygame/index.html` | 425-431 | Creates `<script type="py-game" src="${sim}/main.py">`, appends to body |
| Config attribute injection | `pygame/index.html` | 428-430 | Adds `config="${sim}/pyscript.toml"` only when `meta.config === true` |
| Loading hide — py:ready | `pygame/index.html` | 441 | `document.addEventListener('py:ready', hideLoading)` — primary trigger |
| Loading hide — title poll | `pygame/index.html` | 444-447 | Polls `document.title` every 300ms; hides when `set_caption()` changes it |
| Loading hide — timeout | `pygame/index.html` | 450 | 30-second ultimate fallback: `setTimeout(() => hideLoading(), 30000)` |
| Sim listing fallback | `pygame/index.html` | 452-498 | When no `?sim=`, shows grid of 11 sim cards with "Pygame" badge for live sims |

### API Routes

**N/A** — No backend API. All code runs client-side in the browser.

### Controllers / Business Logic

**N/A** — Pure frontend static site. Logic implemented in JavaScript (player page) and Python (simulation scripts).

### Database

**N/A** — No database. All simulations are ephemeral, running entirely in browser memory.

### Real-time Events

**Browser ↔ Pygame Event Bridge:**

| Event | Direction | Payload | Purpose |
|-------|-----------|---------|---------|
| `keydown` / `keyup` | Browser → pygame-ce | Key code | PyScript forwards DOM keyboard events to `pygame.event` queue |
| `mousemove` / `mousedown` / `mouseup` | Browser → pygame-ce | Coordinates, button | PyScript forwards DOM mouse events to `pygame.event` queue |
| `pygame.display.update()` | Python → Canvas | Frame buffer | pygame-ce blits current surface to `<canvas id="canvas">` |
| `pygame.display.set_caption(title)` | Python → `document.title` | String | PyScript maps `set_caption()` to `document.title`, used by player's title-change poll to detect game start |

### State Management

**N/A** — No global state management library. State is managed via:
- URL parameters (`?sim=<name>`) for simulation selection
- In-memory Python variables within each `async def main()` game loop
- HTML5 canvas pixel buffer for rendered frames (managed by pygame-ce)

---

## Authentication & Authorization

**N/A** — Publicly accessible static site. No authentication or authorization.

---

## Dual-Mode Pattern

Every `main.py` uses `async def main()` so the same file runs both in the browser and locally. The top-level try/except block detects the environment at import time.

**File:** `pygame/moving-square/main.py:51-57` (pattern used by all 11 sims)

```python
# Detect environment: browser (Pyodide) has a running loop, local Python does not
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())   # Browser: schedule main() on PyScript's existing loop
except RuntimeError:
    asyncio.run(main())        # Local: create a new event loop and run
    pygame.quit()
```

**How it works:**

| Environment | `asyncio.get_running_loop()` result | Execution path |
|-------------|-------------------------------------|----------------|
| Browser (PyScript/Pyodide) | Returns the JS-driven event loop | `loop.create_task(main())` schedules game as a coroutine on the existing loop |
| Local Python | Raises `RuntimeError` (no loop running) | `asyncio.run(main())` creates a new loop; `pygame.quit()` cleans up after |

**Key difference from turtle sims:** Pygame sims use `loop.create_task(main())` in the browser, not a passive "do nothing" approach. The task must be scheduled explicitly because PyScript does not auto-call `main()` — it only executes the top-level code of the script. Turtle sims use a passive pattern (player page explicitly calls `await main()` after running the script); pygame sims self-schedule via `create_task()`.

**Local execution:**

```bash
# Requires pygame-ce installed via poetry
poetry run python pygame/moving-square/main.py
# Opens a native SDL window at 500x500, runs at 10 FPS with arrow key control
```

---

## Frame Rate Conversion

All simulations replace blocking delays with `await asyncio.sleep()` to yield to the browser event loop. The sleep duration is chosen to match the original frame rate.

| Original call | Converted to | FPS | Sims using this |
|---------------|-------------|-----|-----------------|
| `pygame.time.delay(100)` | `await asyncio.sleep(0.1)` | 10 | Moving Square, Paint Board, Jumping Square |
| `pygame.time.delay(50)` | `await asyncio.sleep(0.05)` | 20 | Pendulum |
| `clock.tick(27)` | `await asyncio.sleep(1/27)` | 27 | First Game |
| `clock.tick(30)` | `await asyncio.sleep(1/30)` | 30 | Minesweeper |
| `(none)` | `await asyncio.sleep(1/60)` | 60 | Sine Wave, Paint Random Color, Sierpinski Triangle |
| Per-strip batch | `await asyncio.sleep(0.02)` per 10 rects | ~animation | RGB Strips |
| Per-row batch | `await asyncio.sleep(0.05)` per row | ~animation | Paint Random Screen |

**Rule:** `delay(ms)` → `await asyncio.sleep(ms/1000)`. `clock.tick(N)` → `await asyncio.sleep(1/N)`. Never change the sleep duration without also scaling velocity/physics values, or game behavior will change.

---

## Per-Simulation Details

### 1. Moving Square

**File:** `pygame/moving-square/main.py`
**Canvas:** 500×500 (`pygame/index.html:15`)
**Original repo:** `dev-arctik/Moving-Square`

Arrow keys move a 4×4 red square across the screen with edge wrapping on all four sides. The simplest simulation — no assets, no physics, no font rendering.

Key adaptations:
- `pygame.time.delay(100)` → `await asyncio.sleep(0.1)` at line 48, preserving 10 FPS
- `pygame.quit()` and `sys.exit()` removed (browser manages lifecycle)
- `print()` call removed (not useful in browser context)
- Dual-mode pattern at lines 52-57

---

### 2. Jumping Square

**File:** `pygame/jumping-square/main.py`
**Canvas:** 500×500 (`pygame/index.html:16`)
**Original repo:** `dev-arctik/Jumping-Square-`

Arrow keys move a 4×4 red square; spacebar triggers a parabolic jump using a squared `jumpcount` counter. Notable: the original had `set_caption("First Game")` — corrected to `"Jumping Square"` at line 9. The velocity-wrapping behavior on screen edges (`vel = 0.5 * vel` on left/top, `vel = 2 * vel` on right/bottom) is intentional — it is preserved, not treated as a bug.

Key adaptations:
- `pygame.time.delay(100)` → `await asyncio.sleep(0.1)` at line 69
- Caption typo corrected: line 9
- Dual-mode pattern at lines 73-78

---

### 3. Pendulum

**File:** `pygame/pendulum/main.py`
**Canvas:** 500×500 (`pygame/index.html:17`)
**Original repo:** `dev-arctik/Pendulum`

Physics-based pendulum: angular acceleration is computed from `g * sin(angle)`, angular velocity is damped by 0.99 per frame, and polar coordinates are converted to Cartesian for rendering. The pivot draws a white dot, the rod is a red line, and the bob is a yellow circle.

Key adaptations:
- `pygame.time.delay(50)` → `await asyncio.sleep(0.05)` at line 50, preserving 20 FPS
- Dual-mode pattern at lines 54-59

---

### 4. Sine Wave

**File:** `pygame/sine-wave/main.py`
**Canvas:** 500×500 (`pygame/index.html:18`)
**Original repo:** `dev-arctik/Sine-Wave`

Animates a scrolling sine wave by drawing 50 circles per frame and incrementing a `phase offset` variable each frame. The original placed a `delay(25)` inside the per-point loop (50 per frame); the conversion removes all per-point delays and yields once per completed frame instead, which eliminates the sequential drawing animation but keeps the wave scrolling smoothly at 60 FPS.

Key adaptations:
- Per-point `delay(25)` removed; `await asyncio.sleep(1/60)` added once after `display.update()` at line 32
- All 50 points drawn in a single batch per frame
- Dual-mode pattern at lines 36-41

---

### 5. Sierpinski Triangle (Pygame)

**File:** `pygame/sierpinski-triangle/main.py`
**Canvas:** 500×500 (`pygame/index.html:19`)
**Original repo:** `dev-arctik/Sierpinski-s-Triangle`

Chaos game implementation: three triangle vertices are fixed, a random point starts somewhere in the triangle, and each iteration moves the point halfway toward a randomly chosen vertex. The original had no delay at all — it drew one point per iteration, which would run at CPU speed in native Python but would never yield to the browser event loop. The conversion batches 200 points per frame before yielding.

Key adaptations:
- 200 points drawn per frame (line 55) before `await asyncio.sleep(1/60)` at line 61
- Original music load was already commented out in source; no audio stubs needed
- Spacebar exit (`pygame.K_SPACE`) preserved at line 52
- Dual-mode pattern at lines 65-70

---

### 6. Paint Board

**File:** `pygame/paint-board/main.py`
**Canvas:** 500×500 (`pygame/index.html:20`)
**Original repo:** `dev-arctik/Paint-board`

Arrow keys move a 4×4 red rectangle, leaving a red trail on the black canvas (no `win.fill()` per frame). Press `C` to clear. The original contained a `pygame.mouse.get_pos([x, y])` call — this was both a bug (incorrect API, `get_pos()` takes no arguments) and dead code (result was never used). It was removed entirely.

Key adaptations:
- `pygame.mouse.get_pos([x, y])` dead code removed (was both incorrect API usage and unused)
- `pygame.time.delay(100)` → `await asyncio.sleep(0.1)` at line 52
- No `win.fill()` per frame — drawing persists as a trail (line 48 comment)
- Dual-mode pattern at lines 56-61

---

### 7. Paint Random Screen

**File:** `pygame/paint-random-screen/main.py`
**Canvas:** 800×560 (`pygame/index.html:21`)
**Original repo:** `dev-arctik/Paint-Canvas`

Fills the screen with 20×20 randomly colored rectangles, row by row (28 rows × 40 columns). The original had `delay(8)` inside the per-rectangle inner loop, producing 1,120 blocking delays per fill. The conversion yields once per row (every 40 rectangles) with `await asyncio.sleep(0.05)`, preserving the progressive painting effect while reducing async context switches from 1,120 to 28. After a complete fill, the screen holds for 1 second then clears.

Key adaptations:
- Per-rectangle `delay(8)` removed; `await asyncio.sleep(0.05)` added per row at line 30
- `pygame.display.update()` called once per row (line 29) for progressive visual
- 1-second hold before clear: `await asyncio.sleep(1)` at line 33
- Dual-mode pattern at lines 38-43

---

### 8. Paint Random Color

**File:** `pygame/paint-random-color/main.py`
**Canvas:** 800×550 (`pygame/index.html:22`)
**Original repo:** `dev-arctik/Paint-Canvas`

Click and drag to paint random-colored 8-pixel circles at the mouse position. Uses `pygame.mouse.get_pressed()[0]` and `pygame.mouse.get_pos()` — both work natively in pygame-ce via PyScript's event bridge. The original had no frame rate limiter; `await asyncio.sleep(1/60)` was added to prevent 100% CPU usage.

Key adaptations:
- `await asyncio.sleep(1/60)` added at line 29 (original had no delay at all)
- `pygame.display.update()` moved outside the `if mouse_pressed` block so the display stays responsive even when not painting (line 26-27 comment)
- Dual-mode pattern at lines 33-38

---

### 9. RGB Strips

**File:** `pygame/rgb-strips/main.py`
**Canvas:** 675×600 (`pygame/index.html:23`)
**Original repo:** `dev-arctik/Paint-Canvas`

Paints three horizontal strips (red top third, green middle third reversed, blue bottom third) one rectangle column at a time. Each strip uses 226 3-pixel-wide columns. The green strip fills right-to-left (reversed loop: `range(225, -1, -1)`) — this is intentional from the original. Yields `await asyncio.sleep(0.02)` every 10 columns within each strip for a visible animated paint effect, then holds the completed image for 1.5 seconds before clearing.

Key adaptations:
- Per-rectangle `delay(5)` removed; yields every 10 columns with `await asyncio.sleep(0.02)` at lines 23, 31, 39
- `pygame.display.update()` every 10 columns to show progressive paint
- Green loop direction reversed preserved: `range(225, -1, -1)` at line 27
- 1.5-second hold: `await asyncio.sleep(1.5)` at line 43
- Dual-mode pattern at lines 49-53

---

### 10. First Game

**File:** `pygame/first-game/main.py`
**Config:** `pygame/first-game/pyscript.toml`
**Canvas:** 500×480 (`pygame/index.html:24`, `config: true`)
**Original repo:** `dev-arctik/Python-Game`

Side-scrolling shooter: a player character (64×64 sprite) runs left/right and jumps; a goblin enemy patrols between two x-coordinates; the player fires projectiles with spacebar. Score is displayed; 5 points are deducted on player-enemy collision.

This is the most complex simulation due to four interrelated adaptations:

**Classes inside `async def main()` (image path closure):**
The `player`, `projectile`, and `enemy` classes are defined inside `async def main()` at lines 33-149. This was required so that sprite lists (`walkRight`, `walkLeft`, `enemyWalkRight`, `enemyWalkLeft`) loaded after `display.set_mode()` are in the closure scope of all class methods. In the original, these were module-level globals — but PyScript's `type="py-game"` execution context differs from standard module globals, making closure capture the reliable approach.

**Audio disabled via no-op stubs:**
`pygame.mixer` does not work reliably in the browser. Instead of commenting out audio calls (which would cause `NameError` on `bulletSound.play()`), a `_NoSound` class is defined at lines 7-9 and stub instances are assigned at lines 28-29:

```python
class _NoSound:
    def play(self):
        pass

bulletSound = _NoSound()
hitSound = _NoSound()
```

**`hit()` made async:**
The original `hit()` method contained a blocking delay loop (`while i < 200: pygame.time.delay(10)` = 2-second pause). This was converted to an `async def hit()` method at line 66 using `for i in range(200): await asyncio.sleep(0.01)`. The game loop awaits it at line 177: `result = await man.hit()`.

**`SysFont` replaced:**
Two `pygame.font.SysFont()` calls were replaced (lines 75, 163):
- `player.hit()`: `SysFont('comicsans', 100)` → `pygame.font.Font(None, 100)`
- Main loop setup: `SysFont('comicsans', 30, True)` → `pygame.font.Font(None, 30)`

Frame rate: `await asyncio.sleep(1/27)` at line 171, matching original `clock.tick(27)`.
Dual-mode pattern at lines 250-255.

---

### 11. Minesweeper

**File:** `pygame/minesweeper/main.py`
**Config:** `pygame/minesweeper/pyscript.toml`
**Canvas:** 400×440 (`pygame/index.html:25`, `config: true`)
**Original repo:** `dev-arctik/python-minesweeper`

Full minesweeper: 10×10 board with 15 mines, left-click to reveal, right-click to flag, click on a revealed number to chord (auto-reveal neighbors if flag count matches). Timer displayed in stats bar. Win/game-over overlay with click-to-restart.

The original was 5 separate Python files with a `ui/` subdirectory. Multi-file imports in Pyodide are unreliable (namespace package issues without `__init__.py`), so all files were merged into a single `main.py` in dependency order:

| Original file | Merged position | Lines in `main.py` |
|---------------|----------------|--------------------|
| `cell.py` | Top of file | 13-47 |
| `board.py` | After Cell | 50-172 |
| `ui/renderer.py` | After Board | 175-314 |
| `game.py` | After GameRenderer | 317-373 |
| `main.py` (loop) | Bottom | 376-478 |

**numpy eliminated:**
The original `board.py` used `numpy.ndarray` for the grid. This was replaced with a plain list-of-lists at line 61: `self.grid = [[Cell() for _ in range(width)] for _ in range(height)]`. This eliminates the 15 MB numpy dependency — no `packages` declaration is needed in `pyscript.toml`.

**Asset paths updated:**
Original paths: `os.path.join('ui', 'assets', 'bomb.png')`. After flattening the directory structure, updated to `os.path.join('assets', 'bomb.png')` at lines 208-209.

**`SysFont` replaced (3 instances in `GameRenderer`):**
- `GameRenderer.__init__()` line 201: `SysFont('Arial', cell_size // 2)` → `pygame.font.Font(None, cell_size // 2)`
- `GameRenderer.__init__()` line 202: `SysFont('Arial', 18)` → `pygame.font.Font(None, 18)`
- `GameRenderer.draw_board()` line 283: inline `SysFont('Arial', 32)` → `pygame.font.Font(None, 32)`

**Graceful image fallback:**
`load_images()` at lines 206-220 uses `os.path.exists()` before loading. If an asset is missing, a fallback shape is drawn instead (orange square for flag, red circle for bomb).

Frame rate: `await asyncio.sleep(1/30)` at line 469, matching original `Clock().tick(30)`.
Dual-mode pattern at lines 473-478.

---

## Asset Loading

### How pyscript.toml Works

PyScript's `[files]` table fetches static files from the web server and writes them into Pyodide's virtual filesystem (VFS) before the Python script starts executing. Format: `"<URL to fetch>" = "<path in VFS>"`. Paths are relative to the TOML file's directory.

**Why individual file mappings are required:**
Static hosting (GitHub Pages) does not support directory listing. There is no API to enumerate `assets/` contents — each file must be explicitly declared. A single `"./assets" = "./assets"` shorthand would require server-side directory enumeration, which GitHub Pages does not provide.

### First Game Asset Mapping

**File:** `pygame/first-game/pyscript.toml`

42 image files declared individually:
- Player walk right: `R1.png` through `R9.png` (9 frames) at lines 7-15
- Player walk left: `L1.png` through `L9.png` (9 frames) at lines 17-25
- Enemy walk right: `R1E.png` through `R11E.png` (11 frames) at lines 27-37
- Enemy walk left: `L1E.png` through `L11E.png` (11 frames) at lines 39-49
- Background: `bg.jpg` at line 51
- Standing character: `standing.png` at line 52

No `packages` declaration — audio is disabled, numpy is not used.

### Minesweeper Asset Mapping

**File:** `pygame/minesweeper/pyscript.toml`

2 image files declared:

```toml
[files]
"./assets/bomb.png" = "./assets/bomb.png"
"./assets/flag.png" = "./assets/flag.png"
```

No `packages` declaration — numpy was eliminated from the converted code.

---

## Browser Adaptations

| Original pattern | Browser adaptation | Reason | Files affected |
|------------------|--------------------|--------|----------------|
| `pygame.font.SysFont('name', size)` | `pygame.font.Font(None, size)` | No system fonts in Pyodide/browser | `first-game/main.py:75,163`; `minesweeper/main.py:201,202,283` |
| `pygame.time.delay(ms)` | `await asyncio.sleep(ms/1000)` | Blocking sleep freezes browser tab | All 9 simple sims |
| `clock.tick(fps)` | `await asyncio.sleep(1/fps)` | Same reason; also Clock object not needed | `first-game/main.py:171`; `minesweeper/main.py:469` |
| `pygame.quit()` | Removed entirely | Browser manages page lifecycle; calling `quit()` would tear down the Pyodide runtime | All 11 sims |
| `sys.exit()` | Removed entirely | Would terminate Python interpreter, not just the game | `minesweeper/main.py` |
| `pygame.mixer.Sound('file')` / `.play()` | `_NoSound()` stub | `pygame.mixer` unreliable in browser | `first-game/main.py:7-9,28-29` |
| `pygame.mixer.music.load()` / `.play(-1)` | Commented out | Same reason | `first-game/main.py` (background music removed) |
| `pygame.display.set_caption(title)` | Kept as-is | No visible effect in browser UI but preserves local execution and triggers player's title-poll to hide loading overlay | All 11 sims |
| `numpy.ndarray` for 2D grid | `[[Cell() for _ in range(w)] for _ in range(h)]` | Eliminates 15 MB Pyodide package download | `minesweeper/main.py:61` |
| Multi-file imports (`from ui.renderer import`) | Merged into single file | No `__init__.py` in `ui/`; namespace packages unreliable in Pyodide | `minesweeper/main.py` |
| Module-level class definitions that capture loaded images | Classes defined inside `async def main()` | Ensures image lists are in closure scope after `display.set_mode()` | `first-game/main.py:33-149` |
| Blocking `while i < 200: delay(10)` in `hit()` | `async def hit()`: `for i in range(200): await asyncio.sleep(0.01)` | Blocking loops freeze the browser event loop | `first-game/main.py:66-85` |
| `pygame.mouse.get_pos([x, y])` | Removed (dead code) | Incorrect API; `get_pos()` takes no arguments; result was never used | `paint-board/main.py` |

---

## Error Handling

**Loading errors (PyScript/Pyodide):**
- PyScript's `py:ready` event never fires if Pyodide fails to load — loading overlay remains visible
- Browser console will show the Pyodide or PyScript error
- No user-facing error message is surfaced for load failures

**Python runtime errors:**
- Unhandled exceptions in `async def main()` are caught by PyScript's task wrapper and logged to the browser console
- The game loop stops; the canvas freezes at its last rendered frame
- No in-page error display (unlike the turtle player, which has a visible error-state div)

**Asset loading failures (First Game / Minesweeper):**
- `pygame.image.load()` raises `FileNotFoundError` if a file is not listed in `pyscript.toml`
- For Minesweeper: `load_images()` uses `os.path.exists()` before loading, falling back to drawn shapes if images are missing (`minesweeper/main.py:213-220`)
- For First Game: no fallback — a missing sprite PNG will crash `main()` on startup

**Error states:**
- CDN unreachable → Loading overlay remains with spinner; no error shown
- Python syntax error in `main.py` → Loop never starts; browser console shows traceback
- Asset fetch failure (not listed in `pyscript.toml`) → `FileNotFoundError` at image load; console shows traceback

---

## Edge Cases

**No `?sim=` Parameter:**
- Player page shows internal sim listing (lines 452-498 in `pygame/index.html`)
- Canvas frame becomes transparent with no border
- Grid of 11 sim cards displayed with "Pygame" badge for each
- All 11 sims are marked implemented in the `implemented` Set at lines 466-470

**Invalid `?sim=` Parameter:**
- `meta` is `undefined` → same path as no param (listing shown)
- No "sim not found" error message is shown explicitly

**Canvas Sizing Mismatch:**
- `SIMS[sim].size` in `pygame/index.html` must match the `pygame.display.set_mode()` dimensions in `main.py`
- If they differ, pygame-ce may render at the wrong resolution or clip content
- All 11 sims have been verified to match

**User Refreshes During Gameplay:**
- Game restarts from initial state (entire Pyodide runtime reloads)
- Pyodide WASM uses browser cache after first visit — subsequent loads are fast
- No game state persistence — expected behavior

**Multiple Tabs:**
- Each tab runs an independent Pyodide runtime and pygame-ce instance
- No shared state between tabs
- Each tab consumes ~50-100 MB memory for Pyodide runtime

**Mobile / Touch Devices:**
- Canvas has `tabindex="0"` for keyboard focus; focus is set programmatically in `hideLoading()` at line 438
- Keyboard events (arrow keys, spacebar) do not fire on touch screens — keyboard-only sims (Moving Square, Jumping Square, Paint Board) are non-functional on mobile
- Mouse sims (Paint Random Color) may work via tap events if pygame-ce maps touch → mouse
- No mobile-specific handling implemented

**Slow Network:**
- Pyodide + pygame-ce download is ~15-20 MB on first visit; loading overlay remains until `py:ready` fires
- Subsequent visits use browser cache — load time drops to seconds
- 30-second timeout fallback at line 450 hides overlay even if `py:ready` never fires

---

## Key Code Snippets

### Script Tag Injection (Core Player Mechanism)

**File:** `pygame/index.html:424-431`

```javascript
// Inject <script type="py-game"> in the body (after canvas, per PyScript docs)
const tag = document.createElement('script');
tag.type = 'py-game';
tag.src = `${sim}/main.py`;
if (meta.config) {
    tag.setAttribute('config', `${sim}/pyscript.toml`);
}
document.body.appendChild(tag);
```

**Why this matters:** The `<script type="py-game">` tag must be appended to `<body>` after the `<canvas>` element already exists in the DOM. PyScript discovers the canvas by ID (`canvas`) at initialization time. The regular `<script>` block runs synchronously during HTML parsing; `core.js` is loaded as `type="module"` (always deferred), so it runs after parsing completes — the injected tag is already in the DOM when PyScript initializes. For sims that need assets (`config: true`), the `config` attribute points to `pyscript.toml` which triggers asset pre-loading before the Python script executes.

---

### Canvas Dimension Pre-Sizing

**File:** `pygame/index.html:418-422`

```javascript
// Set canvas dimensions to match original pygame.display.set_mode()
const canvas = document.getElementById('canvas');
if (meta.size) {
    canvas.width = meta.size[0];
    canvas.height = meta.size[1];
}
```

**Why this matters:** The HTML canvas must be sized to match the pygame surface dimensions before PyScript starts. If the canvas dimensions do not match `set_mode()` dimensions, pygame-ce may render content at the wrong resolution or clip the game view. The `size` field in SIMS metadata is read from each sim's original `pygame.display.set_mode()` call (e.g., `(500, 500)` for most sims, `(800, 560)` for Paint Random Screen).

---

### Loading Overlay — Triple-Trigger Hide

**File:** `pygame/index.html:435-450`

```javascript
function hideLoading() {
    const el = document.getElementById('loading');
    if (el) el.style.display = 'none';
    canvas.focus();          // Give keyboard focus so arrow keys work immediately
    clearInterval(poll);
}
document.addEventListener('py:ready', hideLoading);

// Fallback: pygame.display.set_caption() changes document.title
const origTitle = document.title;
const poll = setInterval(() => {
    if (document.title !== origTitle) hideLoading();
}, 300);

// Ultimate fallback: hide after 30s regardless
setTimeout(() => hideLoading(), 30000);
```

**Why this matters:** `py:ready` fires when the PyScript interpreter bootstraps — but for `type="py-game"` (an experimental tag), this event may not fire reliably. The title-change poll detects when the game's `pygame.display.set_caption()` call runs (which maps to `document.title` in PyScript), indicating the game loop has started. The 30-second timeout is a last resort to prevent the loading overlay from blocking the canvas indefinitely.

---

### Dual-Mode Execution Pattern

**File:** `pygame/moving-square/main.py:51-57` (representative — all 11 sims identical)

```python
# Detect environment: browser (Pyodide) has a running loop, local Python does not
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
```

**Why this matters:** PyScript executes the top-level code of `<script type="py-game">` immediately, but does not auto-call `main()`. `create_task(main())` schedules the coroutine on PyScript's existing JavaScript-backed event loop without blocking top-level execution. Locally, no event loop is running so `get_running_loop()` raises `RuntimeError`, falling into `asyncio.run(main())` which creates a new loop and runs the game synchronously until the window is closed, then `pygame.quit()` tears down SDL properly.

---

### No-Op Audio Stub (First Game)

**File:** `pygame/first-game/main.py:7-9`

```python
# No-op audio stub — pygame.mixer may not work in the browser
class _NoSound:
    def play(self):
        pass
```

**Why this matters:** Rather than commenting out `bulletSound.play()` and `hitSound.play()` calls (which would require finding every call site), stub instances replace the real Sound objects at module level. The game code calls `.play()` normally — the calls succeed silently. This approach preserves the original call-site structure and makes future re-enabling of audio straightforward.

---

### Sim Listing Fallback (No ?sim= Parameter)

**File:** `pygame/index.html:452-498`

```javascript
} else {
    // No sim selected — show listing of all available simulations
    document.getElementById('sim-title').textContent = 'Pygame Simulations';
    document.getElementById('loading').style.display = 'none';

    const frame = document.getElementById('canvas-frame');
    frame.style.background = 'transparent';
    frame.style.border = 'none';
    // ...

    const implemented = new Set([
        'moving-square', 'jumping-square', 'pendulum', 'sine-wave',
        'sierpinski-triangle', 'paint-board', 'paint-random-screen',
        'paint-random-color', 'rgb-strips', 'first-game', 'minesweeper',
    ]);
    // ... renders cards with 'sim-card--soon' class if not in implemented set
}
```

**Why this matters:** If a future sim is added to the SIMS metadata before its `main.py` is complete, it will appear as "Coming Soon" (dashed border, non-clickable) in both the listing and the landing page. The `implemented` Set is the single source of truth for which sims are live in the player's internal navigation.

---

## Local Development

```bash
# Run any sim locally (requires pygame-ce installed via poetry)
poetry run python pygame/moving-square/main.py
poetry run python pygame/jumping-square/main.py
poetry run python pygame/pendulum/main.py
poetry run python pygame/sine-wave/main.py
poetry run python pygame/sierpinski-triangle/main.py
poetry run python pygame/paint-board/main.py
poetry run python pygame/paint-random-screen/main.py
poetry run python pygame/paint-random-color/main.py
poetry run python pygame/rgb-strips/main.py
poetry run python pygame/first-game/main.py
poetry run python pygame/minesweeper/main.py
```

**What happens locally:**
1. `asyncio.get_running_loop()` raises `RuntimeError` — no event loop exists yet
2. `asyncio.run(main())` creates a new event loop and runs the game in an SDL window
3. `pygame.quit()` tears down SDL after the game loop exits (QUIT event received)
4. Window shows native pygame graphics with system fonts available

**Local vs browser differences:**

| Aspect | Local | Browser |
|--------|-------|---------|
| Font rendering | System fonts available (`SysFont` works) | Only `Font(None, size)` works |
| Audio | `pygame.mixer` works | No-op stubs / disabled |
| Assets | File system paths | Pyodide VFS (pre-loaded via pyscript.toml) |
| Loop start | `asyncio.run(main())` | `loop.create_task(main())` |
| Cleanup | `pygame.quit()` called after loop | Not called (browser manages lifecycle) |
| FPS | `await asyncio.sleep(x)` returns nearly instantly (actual timing from OS scheduler) | `await asyncio.sleep(x)` yields to JS event loop; pygame-ce paces frames via WASM |

**Poetry configuration:** `pyproject.toml` at project root; `pygame-ce = ">=2.4,<3"` declared as dependency.

---

## Related Flows

**Turtle Simulations (7/7 Live):**
- Same `?sim=` URL param pattern but uses Pyodide directly (not PyScript)
- Renders to SVG inside a white lightbox; no canvas element
- Progressive animation via monkey-patched `asyncio.sleep` → `show_scene()`
- Flow doc: `docs/feature-flow/turtle-simulations-flow.md`

**Landing Page Gallery:**
- Flow: User visits `index.html` → Sees Pygame section with 11 cards → Clicks card → Navigates to `pygame/?sim=<name>`
- File: `index.html:83-139`
- Styling: `assets/style.css` (dark theme with orange `#ff6b35` accent for pygame cards)

**Planning Document:**
- `docs/planning/pygame-projects.md` — full conversion notes for all 11 sims, per-project adaptation details, frame rate conversion rules, risk mitigations

**Deployment:**
- Deployed to GitHub Pages at `dev-arctik.github.io/py-playground/`
- Deployment doc: `docs/deployment/github-pages.md`
