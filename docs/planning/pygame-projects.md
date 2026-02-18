# Feature: Pygame Projects — Browser Conversion

**Version:** v1.2
**Status:** Complete (All 11/11 simulations live)
**Author:** global-doc-master
**Created:** 2026-02-16
**Last Modified:** 2026-02-18

> **Progress update (2026-02-18):** All 11 of 11 pygame simulations are live at
> `dev-arctik.github.io/py-playground/`. The landing page has no "Coming Soon"
> cards — every card is an active link. Commit: `7442e7d`.
> - **Phase 1 (5 sims) -- DONE:** Moving Square, Jumping Square, Pendulum,
>   Sine Wave, Sierpinski Triangle. All converted and deployed.
> - **Phase 2 (4 sims) -- DONE:** Paint Board, Paint Random Screen, Paint
>   Random Color, RGB Strips. All converted and deployed.
> - **Phase 3 (2 sims) -- DONE:** First Game and Minesweeper are both converted
>   and deployed. Key implementation details:
>   - **First Game** (source: `dev-arctik/Python-Game`): 42 sprite assets
>     bundled in `assets/`; audio disabled via no-op stubs (`_NoSound` class);
>     all classes moved inside `async def main()` for image-path closure; `hit()`
>     made `async`; both `SysFont` calls replaced with `Font(None, size)`;
>     `pyscript.toml` lists all 42 assets individually.
>   - **Minesweeper** (source: `dev-arctik/python-minesweeper`): 5 source files
>     (cell.py, board.py, ui/renderer.py, game.py, main.py) merged into a single
>     `main.py`; `numpy` replaced with a plain list-of-lists (eliminates 15 MB
>     dependency); asset paths updated from `ui/assets/` to `assets/`; 3
>     `SysFont` calls replaced with `Font(None, size)`; `pyscript.toml` maps 2
>     image assets individually. Both games verified working in browser via
>     Playwright testing.
> - **CDN version:** The actual implementation uses PyScript **2025.3.1**
>   (not 2024.1.1 as originally planned). All CDN URLs in templates below
>   reference the pre-implementation plan version.

---

## Problem Statement

The dev-arctik GitHub account contains 11 Pygame scripts across 9 repositories showcasing interactive simulations, games, and visualizations (physics simulations, drawing tools, fractals, side-scrolling shooter, minesweeper). These scripts currently require a local Python environment with Pygame installed to run, limiting their accessibility and shareability.

The goal is to convert all 11 Pygame scripts to run natively in the browser using PyScript with pygame-ce (Pygame Community Edition compiled for WebAssembly), making them instantly accessible to anyone with a web browser. These conversions will form part of the py-playground portfolio website deployed on GitHub Pages.

**Who is affected:** Game developers, students, educators, and hobbyists who want to view and interact with Pygame projects without local setup.

**Why now:** The py-playground project aims to consolidate all dev-arctik visualization and game projects into a single, publicly accessible web portfolio.

**Known challenges:** Two projects (First Game and Minesweeper) are highly complex with multiple asset dependencies and may be deferred as "coming soon" if conversion proves too involved for initial release.

---

## Goals & Success Criteria

### Primary Goals
- Convert 9 simple-to-medium Pygame scripts to browser-runnable HTML pages using PyScript
- Evaluate and attempt conversion of 2 complex projects (First Game, Minesweeper)
- Maintain original game mechanics, physics, and visual output
- Ensure smooth browser performance with proper async game loops
- Provide consistent user experience across all Pygame simulations

### Success Metrics
- **Achieved:** 11/11 pygame projects successfully ported, including both complex
  multi-asset games (First Game, Minesweeper) — stretch goal met
- Each simulation loads and starts running within 5 seconds
- No browser tab freezing during gameplay
- Keyboard and mouse inputs work correctly in all interactive simulations
- All simulations verified working in browser via Playwright testing

### Definition of Done
- All 11 scripts converted to `pygame/<name>/main.py` files -- COMPLETE
- Shared player page (`pygame/index.html`) loads each sim via `?sim=` parameter -- COMPLETE
- Each `main.py` runs locally via `poetry run python pygame/<name>/main.py` -- COMPLETE
- First Game and Minesweeper include `pyscript.toml` + `assets/` -- COMPLETE
- All async game loop conversions complete (`pygame.time.delay()` → `await asyncio.sleep()`) -- COMPLETE
- All 11 simulations working in browser; landing page has no "Coming Soon" cards -- COMPLETE
- Landing page gallery cards created for all 11 pygame projects -- COMPLETE
- Code comments reference original repository -- COMPLETE

---

## Requirements

### Functional Requirements

**FR-001:** Each Pygame script must be converted to a `main.py` file in `pygame/<name>/`, loaded by the shared player page (`pygame/index.html?sim=<name>`) via `<script type="py-game" src="<name>/main.py">`

**FR-002:** All game loops must use async/await pattern with `await asyncio.sleep()` instead of blocking delays

**FR-003:** All keyboard and mouse input mechanisms must work in browser environment

**FR-004:** Physics simulations must maintain original behavior (pendulum, jumping mechanics)

**FR-005:** The shared player page (`pygame/index.html`) must include:
- `<canvas id="canvas">` element for Pygame rendering
- Dynamic `<script type="py-game" src="<sim>/main.py">` tag (injected via `?sim=` parameter)
- Sim title and description (read from a JS metadata object)
- "Back to Gallery" navigation link
- Each `main.py` must include original repository attribution in code comments

**FR-006:** All `pygame.quit()` and `sys.exit()` calls must be removed (browser manages lifecycle)

**FR-007:** `pygame.font.SysFont()` calls must be replaced with `pygame.font.Font(None, size)` (no system fonts in browser)

**FR-007b:** `pygame.display.set_caption()` calls should be kept as-is — they have no visible effect in the browser UI (the HTML page title is set by the player page JS), but keeping them preserves local execution compatibility and may assist browser accessibility tools.

**FR-008:** Asset-heavy projects (First Game, Minesweeper) must either:
- Bundle all assets in `assets/` folder and load correctly
- OR be marked "coming soon" with documented blockers

**FR-009:** `pygame.mixer` audio may have limited support — disable gracefully if unsupported

### Non-Functional Requirements

- **Performance:** Simulations must run at stable 30+ FPS in browser
- **Compatibility:** Must work in modern browsers (Chrome 120+, Firefox 120+, Safari 17+)
- **Responsiveness:** Canvas should scale reasonably on different screen sizes
- **Maintainability:** Code must retain original structure and comments from source repos

### Assumptions

- PyScript's `<script type="py-game">` tag automatically loads pygame-ce and Pyodide
- pygame-ce API is compatible with standard Pygame 2.x API
- `pygame.event`, `pygame.mouse`, and `pygame.key` work natively in browser
- `numpy` was originally assumed to be required for Minesweeper — in the actual implementation, numpy was replaced with a plain list-of-lists, eliminating the 15 MB dependency entirely. No `packages` declaration is needed in Minesweeper's `pyscript.toml`.
- Image assets (PNG) can be loaded from relative paths in `assets/` folder
- Audio playback (`pygame.mixer`) may not work reliably in browser

---

## User Stories

| Priority | Story | Acceptance Criteria |
|----------|-------|---------------------|
| Must | As a visitor, I want to click a Pygame project card and interact with the simulation using keyboard/mouse immediately | Clicking any Pygame card navigates to the simulation, loads within 5s, and accepts input |
| Must | As a player, I want to move the square with arrow keys in "Moving Square" simulation without lag | Arrow key presses are detected and square moves smoothly at 60 FPS |
| Must | As a student, I want to draw on the Paint Canvas simulation and see my strokes in real-time | Mouse click and drag creates colored circles/rectangles on canvas |
| Should | As a physics enthusiast, I want the pendulum simulation to show realistic swinging motion | Pendulum follows accurate physics equations with smooth animation |
| Should | As a developer, I want to see the Python source code to understand game loop structure | `main.py` file is readable in browser DevTools or via direct navigation |
| Could | As a gamer, I want to play the full side-scrolling shooter with sprites and scoring | "First Game" loads all 42 image assets, detects collisions, tracks score (stretch goal) |
| Could | As a puzzle solver, I want to play Minesweeper with full UI including flags and timer | Minesweeper runs with all features intact (stretch goal) |

---

## Technical Design

### Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                     Browser Environment                        │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  pygame/index.html (shared player page)                   │ │
│  │  URL: pygame/?sim=<name>                                  │ │
│  │                                                           │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  <canvas id="canvas"></canvas>                     │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  JS reads ?sim= param, injects:                    │  │ │
│  │  │  <script type="py-game" src="<name>/main.py"       │  │ │
│  │  │         config="<name>/pyscript.toml"> (if needed) │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              ↓                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  PyScript CDN (2024.1.1) → Pyodide (CPython WASM)       │ │
│  │  - pygame-ce, numpy (if declared), asyncio (stdlib)      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              ↓                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Browser Canvas API + Event Listeners                    │ │
│  │  - Renders Pygame surface to <canvas id="canvas">        │ │
│  │  - Captures keyboard/mouse events                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  Also runnable locally: poetry run python pygame/<name>/main.py│
│  (try/except detects env → create_task or asyncio.run + quit())│
└───────────────────────────────────────────────────────────────┘
```

### Component Breakdown

| # | Component | Folder | Complexity | Assets Needed |
|---|-----------|--------|------------|---------------|
| 1 | Moving Square | `pygame/moving-square/` | Low | None |
| 2 | Paint-board | `pygame/paint-board/` | Low | None |
| 3 | Jumping Square | `pygame/jumping-square/` | Low | None |
| 4 | Sierpinski Triangle (pygame) | `pygame/sierpinski-triangle/` | Low | None |
| 5 | Pendulum | `pygame/pendulum/` | Low | None |
| 6 | Sine Wave | `pygame/sine-wave/` | Low | None |
| 7 | Paint Random Screen | `pygame/paint-random-screen/` | Low | None |
| 8 | Paint Random Color | `pygame/paint-random-color/` | Low | None |
| 9 | RGB Strips | `pygame/rgb-strips/` | Low | None |
| 10 | First Game | `pygame/first-game/` | **Very High** | 42 image assets (PNG+JPG), 3 audio files |
| 11 | Minesweeper | `pygame/minesweeper/` | **Very High** | 2 images, numpy, multi-file |

**Note:** A turtle version of Sierpinski Triangle also exists — the landing page should distinguish them (e.g., "Sierpinski Triangle (Pygame)" vs "Sierpinski Triangle (Turtle)").

### Data Models / Schema Changes

**N/A** — No database or persistent storage. All simulations run in-memory client-side.

### API Contracts

**N/A** — No HTTP APIs. All code runs client-side in the browser.

### Integration Points

**PyScript CDN:**
- URL: `https://pyscript.net/releases/2024.1.1/core.js`
- Provides Pyodide runtime, pygame-ce, and PyScript framework
- `<script type="py-game">` automatically bootstraps Pygame environment

**Pyodide Runtime:**
- CPython 3.11+ compiled to WebAssembly
- pygame-ce (Pygame Community Edition) pre-compiled for WASM
- Async event loop required for game loops

**Browser Canvas API:**
- All Pygame drawing surfaces render to `<canvas id="canvas">` element
- Browser event listeners capture keyboard/mouse input and forward to pygame-ce

**Landing Page:**
- Each Pygame sim is linked from a gallery card on `index.html`
- Navigation: User clicks card → navigates to `pygame/?sim=<name>` (shared player page loads `<name>/main.py`)

---

## Implementation Plan

### Phases

| Phase | Tasks | Status |
|-------|-------|--------|
| 1. Simple Conversions | Convert Moving Square, Jumping Square, Pendulum, Sine Wave, Sierpinski | DONE |
| 2. Paint-Canvas Family | Convert Paint-board, Paint Random Screen, Paint Random Color, RGB Strips | DONE |
| 3. Complex Conversions | Convert First Game and Minesweeper | DONE |
| 4. Integration | Add all 11 cards to landing page gallery; all cards are active links | DONE |

### Suggested Build Order

**Phase 1: Simple (keyboard/physics/animation only)**

1. **Moving Square** — Simplest. Arrow key movement. Remove `print()`, add async sleep.
2. **Jumping Square** — Jump physics with velocity wrapping. Clean code, add async sleep.
3. **Pendulum** — Physics simulation. Replace `pygame.time.delay(50)` with `await asyncio.sleep(0.05)`.
4. **Sine Wave** — Math visualization. Replace `pygame.time.delay(25)` with `await asyncio.sleep(0.025)`.
5. **Sierpinski Triangle (pygame)** — Chaos game. Music already commented out, direct conversion.

**Phase 2: Paint-Canvas family (keyboard + mouse input)**

6. **Paint-board** — Keyboard-only (arrow keys + C to clear). Remove dead `pygame.mouse.get_pos([x,y])` call (bug + dead code), add async sleep.
7. **Paint Random Screen** — Replace `pygame.time.delay(8)` with `await asyncio.sleep(0.008)`.
8. **Paint Random Color** — Mouse painting with `get_pressed()` and `get_pos()`. Add async sleep.
9. **RGB Strips** — Animated color strips. Replace `pygame.time.delay(5)` with `await asyncio.sleep(0.005)`.

**Phase 3: Complex — DONE**

10. **First Game** — Converted from `dev-arctik/Python-Game`. 42 sprite assets bundled in `assets/`; audio disabled via `_NoSound` stubs; all classes moved inside `async def main()` for image-path closure; `hit()` made `async`; both `SysFont` calls replaced with `Font(None, size)`; `pyscript.toml` lists all 42 assets individually.
11. **Minesweeper** — Converted from `dev-arctik/python-minesweeper`. 5 source files merged into single `main.py`; `numpy` replaced with plain list-of-lists; asset paths updated from `ui/assets/` to `assets/`; 3 `SysFont` calls replaced with `Font(None, size)`; `pyscript.toml` maps 2 image assets.

---

## Testing Strategy

### Unit Tests
**N/A** — These are interactive simulations without isolated testable logic. Manual verification required.

### Integration Tests

- [ ] All HTML pages load without JavaScript errors in console
- [ ] PyScript CDN loads successfully (check Network tab)
- [ ] pygame-ce initializes without Pyodide errors
- [ ] Canvas element renders game surface
- [ ] Keyboard input works (arrow keys in Moving Square)
- [ ] Mouse input works (click and drag in Paint Random Color)
- [ ] Game loop runs at stable FPS without freezing browser
- [ ] "Back to Gallery" link navigates correctly to `index.html`
- [ ] Player page with no `?sim=` parameter shows list of available simulations

### Edge Cases

| Edge Case | Expected Behavior |
|-----------|------------------|
| User refreshes page mid-game | Game restarts from initial state |
| User opens multiple Pygame sims in different tabs | Each tab runs independently without interference |
| User resizes browser window during gameplay | Canvas maintains aspect ratio, may clip on small screens |
| User holds down arrow key continuously | Character moves smoothly without stuck key issues |
| `pygame.mixer.music.load()` fails (audio unsupported) | Game continues without audio, no crash |
| Pyodide first-load WASM download (~15-20 MB) takes several seconds on slow connections | Show a loading indicator or informational message; subsequent visits use browser cache |
| Asset file not found (image/sound) | Pygame throws error — must test asset paths carefully |
| `pygame.font.SysFont()` used (system fonts unavailable) | Replace with `pygame.font.Font(None, size)` before deployment |
| numpy not declared in pyscript.toml (minesweeper) | Pyodide throws import error — must declare in config |

### Browser Compatibility Testing

Test all working simulations in:
- [ ] Chrome 120+ (macOS, Windows)
- [ ] Firefox 120+ (macOS, Windows)
- [ ] Safari 17+ (macOS)
- [ ] Chrome mobile (Android) — limited, keyboard/mouse may not work well on touch
- [ ] Safari mobile (iOS) — limited, keyboard/mouse may not work well on touch

---

## Rollout & Deployment

### Deployment Steps — COMPLETED

All steps are complete as of commit `7442e7d`. Recorded for reference:

1. Created `pyproject.toml` in project root and ran `poetry install`
2. Created shared player page `pygame/index.html`
3. Converted all 9 simple/medium Pygame scripts to `main.py` files in `pygame/<name>/` folders
4. Converted First Game and Minesweeper (Phase 3 — not deferred)
5. Tested each simulation locally (`poetry run python pygame/<name>/main.py`) and in browser (`pygame/?sim=<name>`); Phase 3 sims verified via Playwright
6. Added all 11 gallery cards to `index.html` with "Pygame" category badge
7. All cards are active links — no "Coming Soon" cards remain
8. Committed all files to git (commit `7442e7d`)
9. Pushed to `dev-arctik/py-playground` on GitHub
10. GitHub Pages deployed from main branch
11. All 11 sims live at `https://dev-arctik.github.io/py-playground/`

### Feature Flag Strategy

**N/A** — Static site, no feature flags. All 11 simulations are live with no "Coming Soon" cards. If a future regression breaks a simulation, mark the affected card as "Coming Soon" on the landing page until a fix is deployed.

### Rollback Plan

If a Pygame simulation is broken in production:
1. Add `<span class="badge coming-soon">Coming Soon</span>` to the card on landing page
2. Remove the broken sim's entry from the player page's SIMS config or remove its `main.py`
3. Commit and push fix
4. GitHub Pages redeploys automatically within 1-2 minutes

---

## Risks & Mitigations

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| `pygame.time.delay()` not replaced → browser freezes | Critical | High | Audit ALL scripts for `delay()` and `clock.tick()` — replace with async sleep |
| `pygame.font.SysFont()` unavailable in browser | High | High | Replace all instances with `pygame.font.Font(None, size)` during conversion |
| Asset loading paths incorrect (relative paths broken) | High | Medium | Test asset loading early in First Game. Use correct relative paths in pyscript.toml |
| `pygame.mixer` audio doesn't work in browser | Medium | High | Disable audio gracefully or comment out mixer code. Not critical for MVP. |
| First Game: 42 image assets too large/slow to load | Medium | Medium | Bundle assets efficiently. If too slow, defer to "coming soon". |
| Minesweeper: Multi-file imports don't work in PyScript | High | Medium | Test PyScript module import mechanism. If broken, merge into single file or defer. |
| numpy not available in Pyodide (minesweeper) | Medium | Low | Pyodide includes numpy. Declare in pyscript.toml. Test import early. |
| Mouse events don't translate correctly to Pygame | Medium | Low | PyScript pygame-ce handles this natively. Test early with Paint-board. |
| Game runs too slow (low FPS) in browser | Medium | Medium | Optimize game loop, reduce sprite counts, or defer complex projects. |
| PyGame-CE support in PyScript is marked "experimental" (see [PyScript pygame-ce guide](https://docs.pyscript.net/2025.2.1/user-guide/pygame-ce/)) | High | Medium | Pin to PyScript CDN 2024.1.1. Test early. If a simulation fails due to pygame-ce browser limitations, mark as "coming soon" rather than spending excessive time debugging. |

---

## Open Questions

All pre-implementation questions have been resolved. Answers recorded for reference:

- [x] Does PyScript pygame-ce support `pygame.mixer` audio in browser? — **No.** Audio was disabled in First Game via no-op stubs (`_NoSound` class). `pygame.mixer.music` and `pygame.mixer.Sound` calls are commented out. Game runs without audio.
- [x] Can PyScript load 42 image assets efficiently for First Game? — **Yes.** All 42 assets listed individually in `pyscript.toml` under `[files]`. Confirmed working in browser.
- [x] Does PyScript support multi-file Python imports for Minesweeper? — **Not reliably** (no `__init__.py`, namespace package issues in Pyodide). Resolved by merging all 5 source files into a single `main.py`.
- [x] What FPS can pygame-ce achieve in browser? — **Sufficient.** All sims run at their original frame rates without browser tab freezing.
- [x] Should we add touch controls for mobile? — **Deferred.** Future enhancement, not in scope for this phase.

---

## Project Inventory Reference

### All 11 Pygame Scripts (from 9 repos)

| # | Repo | Script | Complexity | Key Adaptations Needed |
|---|------|--------|------------|----------------------|
| 1 | `Moving-Square` | `1. Moving square.py` | Low | Add async sleep, remove `pygame.quit()`, remove `print()` |
| 2 | `Paint-board` | `2. Drawing.py` | Low | Moves a red rectangle with arrow keys leaving a trail, press C to clear. Remove `get_pos([x,y])` — this is both a **bug** (incorrect API usage — `get_pos()` takes no arguments) and dead code (result is never used). Add async sleep |
| 3 | `Jumping-Square-` | `3. Jumping square.py` | Low | Add async sleep, remove `pygame.quit()` |
| 4 | `Python-Game` | `4 First game.py` | Very High | Bundle 42 image assets, disable audio, replace SysFont, test classes |
| 5 | `Sierpinski-s-Triangle` | `5. Sierpinski's Triangle.py` | Low | Music already commented out, add async sleep |
| 6 | `Pendulum` | `6. Simple Pendulum.py` | Low | Replace `delay(50)` with `await sleep(0.05)` |
| 7 | `Sine-Wave` | `7.Sine Wave.py` | Low | Replace `delay(25)` with `await sleep(0.025)` |
| 8 | `Paint-Canvas` | `8a.Paint screen with random color.py` | Low | Replace `delay(8)` with `await sleep(0.008)` |
| 9 | `Paint-Canvas` | `8b.Paint with random color.py` | Low | Test mouse `get_pressed()` and `get_pos()`, add async sleep |
| 10 | `Paint-Canvas` | `8c.Strips of RGB.py` | Low | Replace `delay(5)` with `await sleep(0.005)` |
| 11 | `python-minesweeper` | Multi-file project | Very High | Merge 5 production files (no `__init__.py` — merge preferred), copy images from `ui/assets/` to `assets/`, declare numpy |

---

## Important: Frame Rate Conversion Rule

When replacing `pygame.time.delay(ms)` or `clock.tick(fps)` with `await asyncio.sleep()`, **match the original frame rate** to preserve game feel:
- `delay(100)` = 10 FPS → `await asyncio.sleep(0.1)` (NOT `1/60`)
- `delay(50)` = 20 FPS → `await asyncio.sleep(0.05)`
- `delay(25)` = 40 FPS → `await asyncio.sleep(0.025)`
- `delay(8)` = 125 FPS → `await asyncio.sleep(0.008)`
- `clock.tick(N)` = N FPS → `await asyncio.sleep(1/N)`

Changing the frame rate without adjusting velocity/physics values will alter game behavior. If you want smoother animation at higher FPS, you must also scale all per-frame movement values by `(original_delay / new_delay)`.

---

## Conversion Notes Per Project

### 1. Moving Square (`1. Moving square.py`)

**Original behavior:** Red square moves with arrow keys. Has `print()` call. Uses `pygame.quit()` at end.

**Adaptations:**
- Add `import asyncio` at top
- Replace `pygame.time.delay(100)` with `await asyncio.sleep(0.1)` — preserves original 10 FPS feel. (If you want smoother 60 FPS, also divide all velocity values by 6 to compensate.)
- Remove `pygame.quit()` and `sys.exit()`
- Remove `print()` call
- Folder: `pygame/moving-square/`

**Code changes:**
```python
# Original repo: dev-arctik/Moving-Square
import pygame
import asyncio

# ... setup code ...

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ... movement logic ...

    pygame.display.update()
    await asyncio.sleep(0.1)  # Matches original delay(100) = 10 FPS

# Removed: pygame.quit()
```

---

### 2. Paint-board (`2. Drawing.py`)

**Original behavior:** Moves a red rectangle with arrow keys, leaving a trail on screen. Press C to clear. The `pygame.mouse.get_pos([x,y])` call is dead code (mouse position is never used) — remove it entirely.

**Adaptations:**
- Remove `pygame.mouse.get_pos([x,y])` call entirely — this is both a **bug** (incorrect API usage — `get_pos()` takes no arguments) and dead code (result is never used)
- Add `import asyncio`
- Replace `pygame.time.delay(100)` with `await asyncio.sleep(0.1)` — preserves original 10 FPS feel
- Remove `pygame.quit()`
- Folder: `pygame/paint-board/`

**Code changes:**
```python
# Original repo: dev-arctik/Paint-board
import pygame
import asyncio

# ... setup code ...

while running:
    for event in pygame.event.get():
        # ...

    # Removed: pygame.mouse.get_pos([x,y])  # Dead code — mouse position was never used

    pygame.display.update()
    await asyncio.sleep(0.1)  # Matches original delay(100) = 10 FPS
```

---

### 3. Jumping Square (`3. Jumping square.py`)

**Original behavior:** Square with arrow key movement and jump physics using velocity wrapping. Uses `pygame.time.delay(100)`. **Note:** display caption says "First Game" — fix to "Jumping Square" during conversion.

**Adaptations:**
- Add `import asyncio`
- Replace `pygame.time.delay(100)` with `await asyncio.sleep(0.1)` — preserves original 10 FPS feel. (If you want smoother 60 FPS, also divide all velocity values by 6 to compensate.)
- Remove `pygame.quit()`
- Fix `pygame.display.set_caption("First Game")` → `pygame.display.set_caption("Jumping Square")`
- **Preserve velocity wrapping behavior:** The original intentionally modifies `vel` on screen wrap (halves on left/top, doubles on right/bottom). This creates accelerating/decelerating movement — it is NOT a bug. Do not "fix" this.
- Folder: `pygame/jumping-square/`

**Code changes:**
```python
# Original repo: dev-arctik/Jumping-Square-
import pygame
import asyncio

# ... setup code ...

while running:
    # ... jump physics logic ...
    pygame.display.update()
    await asyncio.sleep(0.1)  # Matches original delay(100) = 10 FPS
```

---

### 4. First Game (`4 First game.py`) — **COMPLEX**

**Original behavior:** Side-scrolling shooter with player character, enemy, bullets, score system. Loads 42 image assets — PNG and JPG (9 left + 9 right + 11 left-enemy + 11 right-enemy + 1 background + 1 standing) and 3 audio files. Uses classes (player, enemy, projectile).

**Adaptations:**
- Create `assets/` folder and bundle ALL 42 image files (PNG and JPG)
- **Update ALL `pygame.image.load()` calls** to add `assets/` prefix — the original loads images from the same directory as the script (e.g., `pygame.image.load('R1.png')`). After relocating to `assets/`, every call must become `pygame.image.load('assets/R1.png')`. There are ~42 such calls across the player, enemy, and background loading code.
- Create `pyscript.toml` to map asset directory into Pyodide's virtual filesystem:
  ```toml
  # No packages needed for First Game (unlike Minesweeper which needs numpy)

  [files]
  # Format: "source_to_fetch" = "destination_in_vfs"
  # (verified against PyScript docs — LEFT is source, RIGHT is destination)
  "./assets" = "./assets"
  ```
  > **Alternative if directory mapping fails:** List each file individually: `"./assets/R1.png" = "./assets/R1.png"` etc. for all 42 images. This is verbose but guaranteed to work.
- Replace **both** `pygame.font.SysFont()` calls:
  1. In `player.hit()` method: `pygame.font.SysFont('comicsans', 100)` → `pygame.font.Font(None, 100)`
  2. In main loop setup: `pygame.font.SysFont('comicsans', 30, True)` → `pygame.font.Font(None, 30)`
- Disable or comment out ALL `pygame.mixer` audio (likely won't work in browser):
  - Background music: `pygame.mixer.music.load('music.mp3')` and `pygame.mixer.music.play(-1)`
  - Sound effects: `bulletSound = pygame.mixer.Sound('bullet.wav')` and `hitSound = pygame.mixer.Sound('hit.wav')`
  - Their `.play()` calls: `bulletSound.play()` (on spacebar/shoot) and `hitSound.play()` (on enemy hit)
  - Create no-op stubs to avoid NameError: `class _NoSound:` with `def play(self): pass`
- Add `import asyncio`
- Replace `clock.tick(27)` with `await asyncio.sleep(1/27)` — match original 27 FPS
- Remove `pygame.quit()` (including the one inside the `hit()` method's event loop)
- Test class-based structure works in PyScript
- Folder: `pygame/first-game/`

**Additional conversion needed in `hit()` method:**
- The `hit()` method contains a blocking delay loop: `while i < 200: pygame.time.delay(10)` (2 seconds total). This must be converted to async: `for i in range(200): await asyncio.sleep(0.01)`. This requires `hit()` to become an `async def` method, which affects how it's called from the game loop.
- Remove `pygame.quit()` from inside `hit()`'s event loop as well.

**Risk:** If asset loading is too slow or complex, mark as "coming soon".

**Code changes:**
```python
# Original repo: dev-arctik/Python-Game
import pygame
import asyncio

# ... class definitions ...
# Note: hit() method must become async — convert its blocking
# delay loop (200 x delay(10)) to: for i in range(200): await asyncio.sleep(0.01)

# Replaced 2 SysFont calls:
# hit() method:  SysFont('comicsans', 100) → Font(None, 100)
# main setup:    SysFont('comicsans', 30, True) → Font(None, 30)

# Audio disabled — no-op stubs to avoid NameError:
class _NoSound:
    def play(self): pass
bulletSound = _NoSound()
hitSound = _NoSound()
# Commented out:
# pygame.mixer.music.load('music.mp3')
# pygame.mixer.music.play(-1)

while run:
    await asyncio.sleep(1/27)  # Match original clock.tick(27) = 27 FPS
    # ... game logic ...
```

---

### 5. Sierpinski Triangle (pygame) (`5. Sierpinski's Triangle.py`)

**Original behavior:** Chaos game fractal. Music loading already commented out. Clean script. The original has **no delay or clock.tick()** — the loop draws one point per iteration with no yielding. **Note:** The original repo contains an `Illuminati.mp3` file — skip it during conversion (the music code is already commented out in the source).

**Adaptations:**
- Add `import asyncio`
- **Batch multiple points per frame** to avoid slow one-point-per-frame rendering. At 60 FPS, drawing one point per frame would take ~167 seconds for 10,000 points. Instead, draw 100-500 points per frame, then yield.
- No iteration cap needed — the continuous drawing is intentional for this visualization. The user controls when to stop by closing the tab or navigating away.
- Remove `pygame.quit()`
- Folder: `pygame/sierpinski-triangle/`

**Code changes:**
```python
# Original repo: dev-arctik/Sierpinski-s-Triangle
import pygame
import random
import asyncio

# ... setup code ...

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw multiple points per frame for performance
    for _ in range(200):  # Batch 200 points per frame
        # ... chaos game point logic ...
        pass

    pygame.display.update()
    await asyncio.sleep(1/60)
```

---

### 6. Pendulum (`6. Simple Pendulum.py`)

**Original behavior:** Physics-based pendulum simulation with angular acceleration and velocity. Uses `pygame.time.delay(50)`.

**Adaptations:**
- Add `import asyncio`
- Replace `pygame.time.delay(50)` with `await asyncio.sleep(0.05)`
- Remove `pygame.quit()`
- Folder: `pygame/pendulum/`

**Code changes:**
```python
# Original repo: dev-arctik/Pendulum
import pygame
import math
import asyncio

# ... setup code ...

while running:
    # ... physics calculations ...
    pygame.display.update()
    # Replaced: pygame.time.delay(50)
    await asyncio.sleep(0.05)
```

---

### 7. Sine Wave (`7.Sine Wave.py`)

**Original behavior:** Animated sine wave visualization. Uses `pygame.time.delay(25)`.

**Performance warning:** The original `delay(25)` is inside `for x in range(50)`, meaning 50 async yields per frame. Instead, remove the per-point delay entirely, draw all 50 points in a batch, then yield once with `await asyncio.sleep(0.025)` after `pygame.display.update()`.

**Behavior change:** The original displays each point individually with a 25ms delay, creating a visible "drawing" animation. The proposed conversion renders all 50 points at once per frame, eliminating this effect. This is an intentional tradeoff for browser performance. To partially preserve the animation, batch 10 points per yield: draw 10 points, call `display.update()`, yield, repeat 5 times per frame.

**Adaptations:**
- Add `import asyncio`
- Remove per-point `pygame.time.delay(25)` from inside the loop — draw all 50 points in a batch, then yield once after display update
- Remove `pygame.quit()`
- Folder: `pygame/sine-wave/`

**Code changes:**
```python
# Original repo: dev-arctik/Sine-Wave
import pygame
import math
import asyncio

# ... setup code ...

while running:
    for x in range(50):
        # ... draw sine wave point (no delay per point) ...
        pass
    pygame.display.update()
    await asyncio.sleep(0.025)  # Yield once per frame, not per point
```

---

### 8a. Paint Random Screen (`8a.Paint screen with random color.py`)

**Original behavior:** Fills screen with random colored rectangles. Uses `pygame.time.delay(8)` **inside nested loops** (28 rows x 40 cols = 1,120 delay calls per screen fill).

**Performance warning:** Converting each `delay(8)` to `await asyncio.sleep(0.008)` would cause 1,120 async context switches per screen fill, which is dramatically slower in the browser than native Python. Instead, yield once per row (every 40 rectangles) to balance visual feedback with performance.

**Behavior change:** The original displays each rectangle individually with an 8ms delay, creating a visible "painting" animation. The proposed conversion draws all rectangles in a row before yielding, then calls `display.update()` per row — this preserves the row-by-row painting effect (28 visible updates per fill) while reducing async yields from 1,120 to 28.

**Adaptations:**
- Add `import asyncio`
- Replace per-rectangle `pygame.time.delay(8)` with per-row `await asyncio.sleep(0)` — yield once per row instead of per rectangle
- Call `pygame.display.update()` after each row to preserve the progressive painting effect
- Remove `pygame.quit()`
- Folder: `pygame/paint-random-screen/`

**Code changes:**
```python
# Original repo: dev-arctik/Paint-Canvas
import pygame
import random
import asyncio

# ... setup code ...

while running:
    for y in range(0, 560, 20):
        for x in range(0, 800, 20):
            # ... draw random colored rectangle ...
            pass
        pygame.display.update()  # Update per row to preserve progressive painting
        await asyncio.sleep(0)  # Yield once per row, not per rectangle
```

---

### 8b. Paint Random Color (`8b.Paint with random color.py`)

**Original behavior:** Mouse painting with random colored circles. Uses `pygame.mouse.get_pressed()` and `get_pos()`. The original has **no delay or clock.tick()** — the game loop runs as fast as possible.

**Adaptations:**
- Add `import asyncio`
- Add `await asyncio.sleep(1/60)` at the end of the game loop — the original has no frame rate limiter, so this is a new addition to yield to the browser and prevent 100% CPU usage
- Remove `pygame.quit()`
- Folder: `pygame/paint-random-color/`

**Code changes:**
```python
# Original repo: dev-arctik/Paint-Canvas
import pygame
import random
import asyncio

# ... setup code ...

while running:
    # ... mouse input logic ...
    # Mouse functions should work natively in pygame-ce
    pygame.display.update()
    await asyncio.sleep(1/60)  # Added — original has no delay
```

---

### 8c. RGB Strips (`8c.Strips of RGB.py`)

**Original behavior:** Animated RGB color strips. Uses `pygame.time.delay(5)`.

**Performance warning:** The original has `delay(5)` inside 3 loops (red: `range(0, 226)`, green: `range(225, -1, -1)` **reversed**, blue: `range(0, 226)`) — 678 async yields per cycle. Instead, yield once per strip (after each loop completes) with `await asyncio.sleep(0)`, then do a final `pygame.display.update()`. Preserve the reversed green loop direction for visual fidelity.

**Adaptations:**
- Add `import asyncio`
- Remove per-rectangle `pygame.time.delay(5)` from inside loops — yield once per strip with `await asyncio.sleep(0)` instead of per rectangle
- Remove `pygame.quit()`
- Folder: `pygame/rgb-strips/`

**Behavior change:** The original displays each rectangle individually with a 5ms delay. The proposed conversion draws an entire strip at once, then updates the display per strip — this preserves the per-strip progressive animation (3 visible updates per cycle) while reducing async yields from 678 to 3.

**Code changes:**
```python
# Original repo: dev-arctik/Paint-Canvas
import pygame
import asyncio

# ... setup code ...

while running:
    # Red strip
    for x in range(0, 226):
        # ... draw red rectangle (no delay per rectangle) ...
        pass
    pygame.display.update()  # Update per strip to preserve progressive animation
    await asyncio.sleep(0)   # Yield once per strip

    # Green strip (reversed direction in original)
    for x in range(225, -1, -1):
        # ... draw green rectangle ...
        pass
    pygame.display.update()
    await asyncio.sleep(0)

    # Blue strip
    for x in range(0, 226):
        # ... draw blue rectangle ...
        pass
    pygame.display.update()
    await asyncio.sleep(0)
```

---

### 9. Minesweeper (Multi-file project) — **COMPLEX**

**Original behavior:** Full minesweeper game with UI, flags, chording, timer. 5 production Python files (main.py, game.py, board.py, cell.py, ui/renderer.py) + 1 test file (tests/test_board.py, skip during conversion) + 2 image assets at **`ui/assets/bomb.png`** and **`ui/assets/flag.png`** (NOT `assets/`). Uses `numpy`. **Note:** `ui/renderer.py` contains 3 `pygame.font.SysFont()` calls and image loading logic (`pygame.image.load()`) that also need conversion. The `ui/` directory has **no `__init__.py`** — the import `from ui.renderer import GameRenderer` relies on implicit namespace packages, which will likely break in Pyodide.

**Adaptations:**
- **Option A (strongly preferred):** Merge all 5 production files into single `main.py`. This avoids the missing `__init__.py` problem and PyScript import issues. Merge in dependency order: Cell → Board → GameRenderer → MinesweeperGame → main loop.
- **Option B:** Test PyScript's multi-file import mechanism (risky due to missing `__init__.py`)
- Copy images from `ui/assets/` to `pygame/minesweeper/assets/` and update load paths from `os.path.join('ui', 'assets', 'bomb.png')` to `os.path.join('assets', 'bomb.png')`
- Create `pyscript.toml`:
  ```toml
  # Root-level package declaration (NOT inside [files])
  packages = ["numpy"]

  [files]
  # Format: "source_to_fetch" = "destination_in_vfs"
  # (verified against PyScript docs — LEFT is source, RIGHT is destination)
  # Individual file mappings (primary approach — guaranteed to work)
  "./assets/bomb.png" = "./assets/bomb.png"
  "./assets/flag.png" = "./assets/flag.png"
  ```
  > **Note:** `packages` MUST be at the TOML root level, above the `[files]` table — never inside it. Use explicit destination paths (NOT empty strings — `""` places files at the virtual filesystem root, breaking `os.path.join('assets', 'bomb.png')`). Individual file mappings are the primary approach. Directory-level mapping (`"./assets" = "./assets"`) is a convenient shorthand but may not work for all PyScript versions — test before relying on it. File paths are relative to the TOML file's directory (`pygame/minesweeper/`).
- Replace ALL 3 `pygame.font.SysFont('Arial', ...)` calls in `renderer.py` with `pygame.font.Font(None, size)`:
  1. `GameRenderer.__init__()`: `self.font = pygame.font.SysFont('Arial', cell_size // 2)` → `pygame.font.Font(None, cell_size // 2)`
  2. `GameRenderer.__init__()`: `self.stats_font = pygame.font.SysFont('Arial', 18)` → `pygame.font.Font(None, 18)`
  3. `GameRenderer.draw_board()`: inline `pygame.font.SysFont('Arial', 32)` → `pygame.font.Font(None, 32)`
- Add `import asyncio`
- Replace `pygame.time.Clock().tick(30)` with `await asyncio.sleep(1/30)` — the original creates a **new Clock() every frame** (a minor performance bug). Replace the entire line, no Clock object needed.
- Remove `pygame.quit()` and `sys.exit()` (browser manages lifecycle). Also remove `import sys`.
- **Canvas size:** The SIMS config uses `[400, 440]` assuming a default 10x10 board with 40px cells + 40px stats bar. After merging, grep for `set_mode` in the merged `main.py` and verify the computed dimensions match `[400, 440]`. If they differ (e.g., different grid size or cell size), update the SIMS config in `pygame/index.html` to match.
- Folder: `pygame/minesweeper/`

**Additional notes:**
- The original code uses `os.path.join('ui', 'assets', 'bomb.png')` for asset paths. After merging and copying assets, update these to `os.path.join('assets', 'bomb.png')`. **Test path resolution in Pyodide early.**
- The original code uses `time.time()` for the game timer — verify `time` module works in Pyodide (it should, but confirm timer accuracy).

**Risk:** If merging files is too complex or imports don't work, mark as "coming soon".

**Code changes:**
```python
# Original repo: dev-arctik/python-minesweeper
import pygame
import numpy as np
import time
import asyncio

# ... merged code from all 5 production files ...
# Merge order: Cell → Board → GameRenderer → MinesweeperGame → main loop
# Update asset paths: 'ui/assets/bomb.png' → 'assets/bomb.png'

# Replaced: pygame.font.SysFont(...)
# With:     pygame.font.Font(None, size)

# Replaced: pygame.time.Clock().tick(30)  # Created new Clock every frame
# With:     await asyncio.sleep(1/30)     # No Clock object needed

while running:
    # ... minesweeper logic ...
    pygame.display.update()
    await asyncio.sleep(1/30)  # 30 FPS — sufficient for turn-based game
```

---

## Shared Player Page + main.py Template

### Shared Player Page (`pygame/index.html`)

A single HTML file serves all 11 pygame simulations. It reads the `?sim=` URL parameter and dynamically injects the correct `<script type="py-game">` tag before PyScript's `core.js` loads.

**Notes:**
- Simulation pages use a **light theme** (white background, dark text) per project convention — distinct from the dark-themed landing page.
- If no `?sim=` parameter is provided or an invalid sim name is given, the player page shows a "Simulation not found" message with clickable links to all available simulations.
- `core.css` styles PyScript editor components. **It does NOT provide a loading spinner.** `core.js` may inject its own loading state via JavaScript — test during Phase 1. If no loading indicator appears during the ~15-20 MB Pyodide WASM download, add a custom one (see `<div id="loading">` in the HTML template below and the `py:ready` event listener to hide it).
- For interactive simulations, `tabindex="0"` on `<canvas>` ensures keyboard focus without requiring a click first.
- For sims that need `pyscript.toml` (First Game, Minesweeper), the player dynamically adds `config="<sim>/pyscript.toml"` to the script tag.
- The regular `<script>` runs synchronously during DOM parsing, creating the `<script type="py-game">` element. Since `core.js` is loaded as `type="module"` (always deferred), it runs after parsing — so the dynamic tag is already in the DOM when PyScript initializes.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading... | Py-Playground</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">
    <script>
        // Sim metadata — title, description, canvas size, and whether it needs pyscript.toml
        // size: [width, height] from each original's pygame.display.set_mode()
        const SIMS = {
            'moving-square':       { title: 'Moving Square',         desc: 'Move a red square with arrow keys',              size: [500, 500] },
            'jumping-square':      { title: 'Jumping Square',        desc: 'Arrow keys to move, jump physics with velocity wrapping', size: [500, 500] },
            'pendulum':            { title: 'Pendulum',              desc: 'Physics-based pendulum simulation',              size: [500, 500] },
            'sine-wave':           { title: 'Sine Wave',             desc: 'Animated sine wave visualization',               size: [500, 500] },
            'sierpinski-triangle': { title: 'Sierpinski Triangle',   desc: 'Chaos game fractal (Pygame version)',            size: [500, 500] },
            'paint-board':         { title: 'Paint-board',           desc: 'Arrow keys to draw, press C to clear',           size: [500, 500] },
            'paint-random-screen': { title: 'Paint Random Screen',   desc: 'Screen fills with random colored rectangles',    size: [800, 560] },
            'paint-random-color':  { title: 'Paint Random Color',    desc: 'Click and drag to paint with random colors',     size: [800, 550] },
            'rgb-strips':          { title: 'RGB Strips',            desc: 'Animated RGB color strips',                      size: [675, 600] },
            'first-game':          { title: 'First Game',            desc: 'Side-scrolling shooter', config: true,           size: [500, 480] },
            'minesweeper':         { title: 'Minesweeper',           desc: 'Classic minesweeper game', config: true,         size: [400, 440] },
        };

        const sim = new URLSearchParams(location.search).get('sim');
        const meta = SIMS[sim];
        if (meta) {
            document.title = `${meta.title} | Py-Playground`;
        }
    </script>
    <script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            text-align: center;
        }
        h1 { color: #0d1117; }
        canvas {
            display: block;
            margin: 20px auto;
            border: 1px solid #333;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #0969da;
            text-decoration: none;
        }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1 id="sim-title">Loading...</h1>
    <p id="sim-desc"></p>
    <div id="loading" style="text-align:center; padding:40px; color:#555;">Loading simulation...</div>

    <canvas id="canvas" tabindex="0"></canvas>

    <script>
        // Hide loading message once PyScript is ready
        // Note: py:ready fires when the interpreter bootstraps, before main() finishes.
        // For long-running sims, users will see the canvas populate incrementally after this.
        document.addEventListener('py:ready', () => {
            const el = document.getElementById('loading');
            if (el) el.style.display = 'none';
        });

        // Inject the PyScript tag for the selected sim before core.js loads
        const sim = new URLSearchParams(location.search).get('sim');
        const meta = SIMS[sim];
        if (meta) {
            document.getElementById('sim-title').textContent = meta.title;
            document.getElementById('sim-desc').textContent = meta.desc;
            // Set canvas dimensions to match original pygame.display.set_mode()
            if (meta.size) {
                const canvas = document.getElementById('canvas');
                canvas.width = meta.size[0];
                canvas.height = meta.size[1];
            }
            const tag = document.createElement('script');
            tag.type = 'py-game';
            tag.src = `${sim}/main.py`;
            // Add pyscript.toml config for sims that need assets/packages
            if (meta.config) {
                tag.setAttribute('config', `${sim}/pyscript.toml`);
            }
            document.body.appendChild(tag);
        } else {
            document.getElementById('sim-title').textContent = 'Simulation not found';
            document.getElementById('loading').style.display = 'none';
            // Show available sims as clickable links
            const desc = document.getElementById('sim-desc');
            desc.textContent = 'Available: ';
            Object.entries(SIMS).forEach(([k, v], i) => {
                if (i > 0) desc.appendChild(document.createTextNode(' · '));
                const a = document.createElement('a');
                a.href = `?sim=${k}`;
                a.textContent = v.title;
                desc.appendChild(a);
            });
        }
    </script>

    <a href="../index.html" class="back-link">← Back to Gallery</a>
</body>
</html>
```

### main.py Template (Dual-Mode)

Every pygame `main.py` uses `async def main()` so it works in both browser and locally. The key challenge is that **PyScript does NOT auto-call `main()`** — the file's top-level code runs, but `async def main()` only defines the function. We must explicitly invoke it.

**Pattern:** Use `asyncio.get_running_loop()` to detect the environment — Pyodide (browser) has a running event loop; local Python does not.

```python
# Original repo: dev-arctik/<repo-name>
import pygame
import asyncio
# import other modules as needed (random, math, numpy, etc.)

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # Important: set_mode() dimensions MUST match the SIMS config in the player page.
    # If they disagree, pygame-ce may resize the canvas or render at the wrong resolution.
    # Note: clock.tick() replaced by await asyncio.sleep() — no Clock needed

    # ... setup code ...

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ... game logic ...

        pygame.display.update()
        await asyncio.sleep(1/60)  # Match original frame rate (see FPS conversion rule)

# Detect environment and run main()
try:
    # Browser: Pyodide has a running event loop — schedule main() as a task
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    # Local: no running event loop — use asyncio.run()
    asyncio.run(main())
    pygame.quit()
```

> **Note:** This pattern MUST be tested with a minimal script during Phase 1. If `create_task()` doesn't work as expected in Pyodide, use this concrete fallback — change the player page's JS to fetch the script content and inject it as inline code:
> ```javascript
> // Fallback: fetch script content and inject inline instead of using src=
> fetch(`${sim}/main.py`).then(r => r.text()).then(code => {
>     const tag = document.createElement('script');
>     tag.type = 'py-game';
>     tag.textContent = code;
>     if (meta.config) tag.setAttribute('config', `${sim}/pyscript.toml`);
>     document.body.appendChild(tag);
> });
> ```
> This avoids Python import path issues (folder names use hyphens, not valid Python identifiers) by injecting the script content directly.

**pyscript.toml (only for First Game and Minesweeper):**

```toml
# Root-level package declaration (NOT inside [files])
packages = ["numpy"]  # Only if needed (minesweeper)

[files]
# Format: "source_to_fetch" = "destination_in_vfs"
# (verified against PyScript docs — LEFT is source, RIGHT is destination)
# Use individual file mappings as the primary approach:
"./assets/bomb.png" = "./assets/bomb.png"
"./assets/flag.png" = "./assets/flag.png"
# Or directory shorthand (test first): "./assets" = "./assets"
```

> **Note:** `packages` MUST be at the TOML root level, ABOVE the `[files]` table — never inside it. File paths are relative to the TOML file's directory. Individual file mappings are the guaranteed-to-work approach; directory mapping is convenient but may not be supported in all PyScript versions. See [PyScript config docs](https://docs.pyscript.net/).

---

## References

- Original source repositories: `https://github.com/dev-arctik/<repo-name>` (9 repos listed in inventory)
- PyScript documentation: `https://docs.pyscript.net/`
- PyScript pygame-ce guide: `https://docs.pyscript.net/2025.2.1/user-guide/pygame-ce/`
- **PyScript CDN (actual version used):** `https://pyscript.net/releases/2025.3.1/core.js`
- PyScript CDN (originally planned): `https://pyscript.net/releases/2024.1.1/core.js`
- Pyodide documentation: `https://pyodide.org/en/stable/`
- pygame-ce documentation: `https://pyga.me/docs/`
- numpy in Pyodide: `https://pyodide.org/en/stable/usage/packages-in-pyodide.html`
- Project CLAUDE.md: `../../CLAUDE.md`
