# Feature: Python Turtle Projects — Browser Conversion

**Version:** v1.0
**Status:** Complete
**Author:** global-doc-master
**Created:** 2026-02-16
**Last Modified:** 2026-02-17

---

## Problem Statement

The dev-arctik GitHub account contains 7 Python turtle graphics scripts in the `Python-Turtle` repository that showcase various algorithmic visualizations (fractals, chaos theory, geometry). These scripts currently require a local Python environment with `tkinter` to run, limiting their accessibility and shareability.

The goal is to convert all 7 turtle scripts to run natively in the browser using PyScript (Pyodide), making them instantly accessible to anyone with a web browser, without requiring Python installation or environment setup. These conversions will form part of the py-playground portfolio website deployed on GitHub Pages.

**Who is affected:** Developers, students, and educators who want to view and share Python turtle graphics without local setup.

**Why now:** The py-playground project aims to consolidate all dev-arctik visualization projects into a single, publicly accessible web portfolio.

---

## Goals & Success Criteria

### Primary Goals
- Convert all 7 Python turtle scripts to browser-runnable HTML pages using PyScript
- Maintain the original visual output and algorithmic logic of each simulation
- Ensure smooth browser performance with no freezing or crashing
- Provide a consistent user experience across all turtle simulations

### Success Metrics
- 100% of turtle projects successfully ported (7/7)
- Each simulation loads and runs in under 5 seconds
- No browser tab freezing during execution
- All simulations render correctly in Chrome, Firefox, and Safari
- Original repository attribution preserved in code comments

### Definition of Done
- All 7 `main.py` files created in `turtle/<name>/` folders
- Shared player page (`turtle/index.html`) loads each sim via `?sim=` parameter
- Each `main.py` runs locally via `poetry run python turtle/<name>/main.py`
- All simulations tested and verified working in browser AND locally
- Landing page gallery cards created for all 7 turtle projects
- Code comments reference original repository

---

## Requirements

### Functional Requirements

**FR-001:** Each turtle script must be converted to a `main.py` file in `turtle/<name>/`, loaded by the shared player page (`turtle/index.html?sim=<name>`) via PyScript `<script type="py" src="<name>/main.py">`

**FR-002:** All original visual outputs must be preserved (shapes, colors, patterns, animations)

**FR-003:** Infinite loops must be capped to prevent browser freezing

**FR-004:** Large iteration counts must be reduced to browser-safe values (10k-20k max)

**FR-005:** Each HTML page must include:
- Page title matching the simulation name
- Short description of what the visualization shows
- "Back to Gallery" navigation link
- Original repository attribution in code comments

**FR-006:** All `exitonclick()` and `mainloop()` calls must be removed (browser manages lifecycle)

**FR-007:** `print()` calls should be removed for cleanliness (optional, as they're harmless)

### Non-Functional Requirements

- **Performance:** Simulations must complete rendering within 30 seconds or provide incremental updates
- **Compatibility:** Must work in modern browsers (Chrome 120+, Firefox 120+, Safari 17+)
- **Accessibility:** Each simulation page must have semantic HTML structure
- **Maintainability:** Code must retain original structure and comments from source repos

### Assumptions

- Pyodide's turtle module API is **largely** compatible with Python's standard `turtle` module (exception: `clone()` and advanced features need testing)
- Pyodide includes `random` and `math` stdlib modules by default
- GitHub Pages hosting supports static HTML files that load external Python scripts via PyScript

---

## User Stories

| Priority | Story | Acceptance Criteria |
|----------|-------|---------------------|
| Must | As a visitor, I want to click a turtle project card on the landing page and see the simulation run immediately in my browser | Clicking any turtle card navigates to `turtle/?sim=<name>` and the simulation begins rendering within 3 seconds |
| Must | As a developer, I want to view the Python source code to understand how the algorithm works | Python code is viewable by navigating to `turtle/<name>/main.py` directly, or runnable locally via `poetry run python turtle/<name>/main.py` |
| Must | As a student, I want to see smooth fractal tree generation without my browser tab freezing | Fractal tree (most complex turtle script) completes without blocking the browser event loop |
| Should | As a mobile user, I want turtle simulations to render correctly on my phone screen | Turtle canvas scales appropriately on mobile viewports |
| Could | As an educator, I want to easily share individual simulation URLs with students | Each sim has a clean URL like `/turtle/?sim=fractal-tree` |

---

## Technical Design

### Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                     Browser Environment                        │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  turtle/index.html (shared player page)                   │ │
│  │  URL: turtle/?sim=<name>                                  │ │
│  │                                                           │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  JS reads ?sim= param, injects:                    │  │ │
│  │  │  <script type="py" src="<name>/main.py">           │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                           ↓                               │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  <name>/main.py                                    │  │ │
│  │  │  async def main():                                 │  │ │
│  │  │      import turtle, asyncio                        │  │ │
│  │  │      # Adapted code (capped loops, async yields)   │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                           ↓                               │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  PyScript CDN (2024.1.1) → Pyodide (CPython WASM) │  │ │
│  │  │  - turtle, random, math, asyncio (stdlib)          │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  │                           ↓                               │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │  HTML5 Canvas or SVG (auto-created by Pyodide's    │  │ │
│  │  │  turtle module — verify target during Phase 1)     │  │ │
│  │  └────────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  Also runnable locally: poetry run python turtle/<name>/main.py│
│  (try/except detects env → create_task or asyncio.run + exitonclick)│
└───────────────────────────────────────────────────────────────┘
```

### Component Breakdown

| Component | File | Purpose |
|-----------|------|---------|
| Polygon | `turtle/polygon/main.py` | Draws polygons with increasing number of sides (3 to 50) |
| Sierpinski's Triangle | `turtle/sierpinski-triangle/main.py` | Chaos game fractal using random midpoint method. **Note:** a pygame version also exists — landing page should distinguish them (e.g., "Sierpinski Triangle (Turtle)" vs "Sierpinski Triangle (Pygame)") |
| Curved Graph | `turtle/curved-graph/main.py` | Curved line art pattern in 4 quadrants |
| Barnsley Fern | `turtle/barnsley-fern/main.py` | IFS fractal fern using affine transformations |
| Fractal Tree | `turtle/fractal-tree/main.py` | Recursive tree using turtle cloning and generators |
| Flower | `turtle/flower/main.py` | Rotating filled triangles forming a flower pattern |
| Chaos with PI and E | `turtle/chaos-pi-e/main.py` | Spiral pattern using sqrt, pi, and e constants |

### Data Models / Schema Changes

**N/A** — No database or persistent data storage. All simulations are ephemeral visualizations.

### API Contracts

**N/A** — No HTTP APIs. All code runs client-side in the browser.

### Integration Points

**PyScript CDN:**
- URL: `https://pyscript.net/releases/2024.1.1/core.js`
- Provides Pyodide runtime and PyScript framework
- Automatically loads Python standard library modules (turtle, random, math)

**Pyodide Runtime:**
- CPython 3.11+ compiled to WebAssembly
- Executes Python code in browser sandbox
- Turtle module renders to an auto-created canvas or SVG element (verify rendering target during Phase 1)
- `turtle.Screen()` methods (`bgcolor()`, `screensize()`, `title()`) are expected to work in Pyodide — no adaptation needed

**Landing Page:**
- Each turtle sim is linked from a gallery card on `index.html`
- Navigation: User clicks card → navigates to `turtle/?sim=<name>` (shared player page loads `<name>/main.py`)

---

## Implementation Plan

### Phases

| Phase | Tasks | Dependencies |
|-------|-------|-------------|
| 1. Simple Conversions | Convert Flower, Curved Graph, Polygon | PyScript CDN available |
| 2. Medium Conversions | Convert Chaos PI+E, Sierpinski's Triangle, Barnsley Fern | Phase 1 complete, async patterns tested |
| 3. Complex Conversion | Convert Fractal Tree (uses clone() and generators) | Phase 2 complete |
| 4. Integration | Add all 7 cards to landing page gallery | All conversions complete |

### Suggested Build Order

**1. Flower (simplest)** — Clean script with `begin_fill()` and `end_fill()`. Short loop (36 iterations) — no capping needed. Wrap in async template.

**2. Curved Graph** — Clean script, no issues. Tests basic turtle drawing in browser.

**3. Polygon** — Cap outer loop from 1999 to 50 sides for browser performance. Remove `print()` calls.

**4. Chaos with PI and E** — Cap infinite `while True` loop to ~5000 iterations. Add `await asyncio.sleep(0)` periodically.

**5. Sierpinski's Triangle** — Cap loop from 2e21 to 10,000 iterations. Remove stray `v` character at end of file. Add async yield.

**6. Barnsley Fern** — Reduce iterations from 100k to 20k. Remove `print()` calls. Add async yield every 1000 iterations.

**7. Fractal Tree (hardest)** — Test `turtle.clone()` in Pyodide (may require workaround). Uses generators (`yield`). Remove `exitonclick()`. Most complex, save for last.

---

## Testing Strategy

### Unit Tests
**N/A** — These are visual simulations without testable logic. Manual visual verification required.

### Integration Tests

- [ ] All 7 sims load via shared player (`turtle/?sim=<name>`) without JavaScript errors
- [ ] PyScript CDN loads successfully (check Network tab)
- [ ] Python code executes without Pyodide errors
- [ ] Turtle canvas renders and displays expected visual output
- [ ] "Back to Gallery" link navigates correctly to `index.html`
- [ ] Player page with no `?sim=` parameter shows list of available simulations

### Edge Cases

| Edge Case | Expected Behavior |
|-----------|------------------|
| User refreshes page mid-simulation | Simulation restarts from beginning |
| User opens multiple turtle sims in different tabs | Each tab runs independently without interference |
| User resizes browser window during rendering | Canvas maintains aspect ratio, may clip on small screens |
| `turtle.clone()` not supported in Pyodide | Fractal Tree: rewrite to avoid clone() or mark "coming soon" |
| Iteration count too high (forgot to cap loop) | Browser tab freezes — MUST test and fix before deployment |
| Pyodide first-load WASM download (~15-20 MB) takes several seconds on slow connections | Show a loading indicator or informational message; subsequent visits use browser cache |
| Random seed not set (non-deterministic output) | Acceptable — randomness is intentional in chaos game sims |

### Browser Compatibility Testing

Test all 7 simulations in:
- [ ] Chrome 120+ (macOS, Windows)
- [ ] Firefox 120+ (macOS, Windows)
- [ ] Safari 17+ (macOS)
- [ ] Chrome mobile (Android)
- [ ] Safari mobile (iOS)

---

## Rollout & Deployment

### Deployment Steps

1. Create `pyproject.toml` in project root (Python 3.12+, pygame-ce, numpy) and run `poetry install`
2. Create shared player page `turtle/index.html`
3. Convert all 7 turtle scripts to `main.py` files in `turtle/<name>/` folders
4. Test each simulation locally (`poetry run python turtle/<name>/main.py`) and in browser (`turtle/?sim=<name>`)
5. Add 7 gallery cards to `index.html` with category badge "Turtle" (green)
6. Commit all files to git
7. Push to `dev-arctik/py-playground` repository on GitHub
8. GitHub Pages automatically deploys from main branch
9. Verify all turtle sims work at `https://dev-arctik.github.io/py-playground/turtle/?sim=<name>`

### Feature Flag Strategy

**N/A** — Static site, no feature flags. If a simulation is broken, mark card as "Coming Soon" on landing page until fixed.

### Rollback Plan

If a turtle simulation is broken in production:
1. Add `<span class="badge coming-soon">Coming Soon</span>` to the card on landing page
2. Remove the broken sim's entry from the player page's SIMS config or remove its `main.py`
3. Commit and push fix
4. GitHub Pages redeploys automatically within 1-2 minutes

---

## Risks & Mitigations

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| `turtle.clone()` not supported in Pyodide | High | Medium | Test early with Fractal Tree. If broken, rewrite without clone() or defer to "coming soon" |
| Infinite loop freezes browser tab | Critical | High | Cap ALL loops to max 10k-20k iterations. Add `await asyncio.sleep(0)` in long loops to yield to event loop |
| Large iteration count causes 30+ second load time | Medium | Medium | Reduce iteration counts (Barnsley Fern: 100k→20k, Sierpinski: 2e21→10k) |
| `tracer()` optimization doesn't work in Pyodide | Medium | Medium | Test early — tracer() is used by Polygon, Sierpinski's Triangle, Barnsley Fern, and Chaos PI+E. If broken, remove `tracer()` calls and reduce iteration counts further to compensate |
| Turtle canvas too small on mobile devices | Low | Medium | Acceptable — turtle graphics are best viewed on desktop. Future: add responsive canvas scaling |
| Original `.py` files have syntax errors (e.g., stray `v` in Sierpinski) | High | Known (Sierpinski file) | Manually review and fix syntax errors during conversion |
| `print()` calls clutter browser console | Low | High | Remove all `print()` calls during conversion (harmless but unnecessary) |

---

## Open Questions

- [ ] Does Pyodide's turtle module support `turtle.clone()`? — Test with Fractal Tree. If not, research workaround or rewrite.
- [ ] What is the optimal iteration count for Barnsley Fern to balance detail vs speed? — Test 10k, 15k, 20k and choose best.
- [ ] Does PyScript correctly call `async def main()` from an external `.py` file loaded via `<script type="py" src="...">`? — Test with a minimal script before building all 7 sims. If it doesn't auto-run, the shared player may need to add an inline `from <module> import main; await main()` call.
- [ ] Should we add a "Speed" slider to let users control `tracer()` value? — Defer to future enhancement, not in MVP.

---

## Project Inventory Reference

### All 7 Turtle Scripts (from `dev-arctik/Python-Turtle`)

| # | Script | Complexity | Key Adaptations Needed |
|---|--------|------------|----------------------|
| 1 | `1.Polygon.py` | Low | Cap outer loop to 50, remove `print()` |
| 2 | `2.Sierpinski's Triangle.py` | Medium | Cap loop to 10k, remove stray `v`, add async yield |
| 3 | `3.Curved graph.py` | Low | Wrap in async template (no algorithmic changes) |
| 4 | `4.Barnsley fern.py` | Medium | Reduce to 20k iterations, remove `print()`, add async yield |
| 5 | `5.Factral Tree.py` | High | Test `clone()`, remove `exitonclick()`, keep generators. **Note:** original filename misspells "Fractal" as "Factral" |
| 6 | `6.Flower.py` | Low | Wrap in async template (no algorithmic changes) |
| 7 | `7.Chaos with PI and E.py` | Medium | Cap infinite loop to 5k, add async yield |

---

## Conversion Notes Per Project

### 1. Polygon (`1.Polygon.py`)

**Original behavior:** Draws polygons with sides from 3 to 1999 (`range(3, 2000)`), uses `tracer(100,0)` for speed, includes `print()` calls.

**Adaptations:**
- Cap outer loop to 50 sides instead of 1999 (browser performance)
- Remove `print()` calls
- **Move** `tracer(100,0)` from inside the loop to setup (before the loop starts) — the original places it inside the inner loop body, which is redundant. Assumed working in Pyodide, test early (see Risks)
- Folder: `turtle/polygon/`

**Code changes:**
```python
# Original repo: dev-arctik/Python-Turtle
import turtle

# ... setup code ...

for i in range(3, 51):  # Changed from range(3, 2000)
    # ... drawing logic ...
    # Removed: print(i)
```

---

### 2. Sierpinski's Triangle (`2.Sierpinski's Triangle.py`)

**Original behavior:** Chaos game method with absurdly large loop count (2e21 iterations), stray `v` character at end of file (syntax error).

**Adaptations:**
- Cap loop to 10,000 iterations
- Remove stray `v` at EOF
- **Move** `pen.getscreen().tracer(100,0)` from inside the loop to setup (before the loop starts) — the original places it at the end of the main loop body, which is redundant. Assumed working in Pyodide, test early (see Risks)
- Add `import asyncio` and `await asyncio.sleep(0)` every 500 iterations
- Remove `print()` calls
- Folder: `turtle/sierpinski-triangle/`

**Code changes:**
```python
# Original repo: dev-arctik/Python-Turtle
import turtle
import random
import asyncio

# ... setup code ...

for i in range(10000):  # Changed from range(2000000000000000000000)
    # ... drawing logic ...
    if i % 500 == 0:
        await asyncio.sleep(0)  # Yield to browser
# Removed: stray 'v' character
```

---

### 3. Curved Graph (`3.Curved graph.py`)

**Original behavior:** Clean script, draws curved line art in 4 quadrants.

**Adaptations:**
- No algorithmic changes needed — wrap in `async def main()` and add dual-mode boilerplate per template
- No async yields needed — only 84 draw calls (4 loops of 21), completes near-instantly
- Folder: `turtle/curved-graph/`

**Code changes:**
```python
# Original repo: dev-arctik/Python-Turtle
import turtle
import asyncio

async def main():
    # ... all original drawing code (unchanged logic) ...
    pass

try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    turtle.exitonclick()
```

---

### 4. Barnsley Fern (`4.Barnsley fern.py`)

**Original behavior:** 100,000 iterations using IFS transformations, uses `tracer(1000,0)`, includes `print()` calls.

**WARNING — Sequential Update Bug:** The original script has a bug in its IFS transformations: `y` is computed using the already-updated `x` instead of the old `x`. Standard Barnsley Fern IFS requires simultaneous updates (both computed from old values). This produces a subtly distorted fern. **Decision for this project:** Preserve original behavior to maintain fidelity with the source repo. Add a code comment noting the mathematical imprecision:
```python
# Note: original code has a sequential update — y uses new x, not old x.
# Standard IFS requires simultaneous update. Preserving original behavior.
# To fix: old_x = x; x = 0.85*old_x + 0.04*y; y = -0.04*old_x + 0.85*y + 1.6
```

**Adaptations:**
- Reduce to 20,000 iterations
- Remove `print()` calls
- **Move** `tracer(1000,0)` from inside the loop to setup (before the loop starts) — the original places it inside the `for n` loop body, which is redundant. Assumed working in Pyodide, test early (see Risks)
- Add `await asyncio.sleep(0)` every 1000 iterations
- Folder: `turtle/barnsley-fern/`

**Code changes:**
```python
# Original repo: dev-arctik/Python-Turtle
import turtle
import random
import asyncio

# ... setup code ...

for i in range(20000):  # Changed from range(100000)
    # ... transformation logic ...
    if i % 1000 == 0:
        await asyncio.sleep(0)
    # Removed: print(i)
```

---

### 5. Fractal Tree (`5.Factral Tree.py`)

**Original behavior:** Most complex turtle script. Uses `turtle.clone()`, generators with `yield`, recursive tree drawing, `exitonclick()`.

**Adaptations:**
- Wrap in `async def main()` and add dual-mode boilerplate per template
- Test `turtle.clone()` in Pyodide — may need workaround
- Remove `exitonclick()` from browser code path (keep in local `except RuntimeError` block)
- Remove `mainloop` from imports (imported but unused in the original script)
- Keep generators (should work in Pyodide)
- Yield to browser during tree generation (see async strategy below)
- Folder: `turtle/fractal-tree/`

**Async generator conversion:** The original `tree()` function is a regular generator (`def tree()` with `yield None`). Since `await` cannot be used inside a regular generator, choose one of:
- **Option A (use this unless it causes issues):** Keep `tree()` as a regular generator. In the caller loop inside `main()`, add `await asyncio.sleep(0)` every N iterations: `for i, x in enumerate(t): if i % 50 == 0: await asyncio.sleep(0)`
- **Option B (fallback only):** Convert `tree()` to an async generator: `async def tree(...)` and replace `yield None` with `await asyncio.sleep(0); yield`. The caller changes from `for x in t:` to `async for x in t:`. Only use this if Option A doesn't yield to the browser correctly.

**Risk:** If `clone()` doesn't work, rewrite using turtle state saving: store position and heading before branching, draw left subtree, restore state, draw right subtree. This eliminates clone() at the cost of losing simultaneous branch drawing. If still too complex, mark as "coming soon".

**Code changes:**
```python
# Original repo: dev-arctik/Python-Turtle
import turtle
import random
import asyncio

async def main():
    # ... setup code ...

    # tree() stays as a regular generator, caller yields to browser
    t = tree([p], length, angle, depth)
    for i, x in enumerate(t):
        if i % 50 == 0:
            await asyncio.sleep(0)  # Yield to browser every 50 steps
    # Removed: turtle.exitonclick() (handled in local block below)

try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    turtle.exitonclick()
```

---

### 6. Flower (`6.Flower.py`)

**Original behavior:** Simplest script. Draws rotating filled triangles.

**Adaptations:**
- No algorithmic changes needed — wrap in `async def main()` and add dual-mode boilerplate per template
- Uses `begin_fill()` and `end_fill()` — works in Pyodide
- Folder: `turtle/flower/`

**Code changes:**
```python
# Original repo: dev-arctik/Python-Turtle
import turtle
import asyncio

async def main():
    # ... all original drawing code (unchanged logic) ...
    # begin_fill() / end_fill() work in Pyodide
    pass

try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    turtle.exitonclick()
```

---

### 7. Chaos with PI and E (`7.Chaos with PI and E.py`)

**Original behavior:** Infinite `while True` loop drawing spiral using `math.sqrt`, `math.pi`, `math.e`. Uses `tracer(100,0)`.

**Adaptations:**
- Cap infinite loop to 5000 iterations
- Add `await asyncio.sleep(0)` every 500 iterations
- Keep `tracer(100,0)` in setup — it's already before the loop in the original (unlike Polygon/Sierpinski/Barnsley which need it moved). Assumed working in Pyodide, test early (see Risks)
- Folder: `turtle/chaos-pi-e/`

**Code changes:**
```python
# Original repo: dev-arctik/Python-Turtle
import turtle
import math
import asyncio

# ... setup code ...

# Changed from: while True:
for i in range(5000):
    # ... spiral logic ...
    if i % 500 == 0:
        await asyncio.sleep(0)
```

---

## Shared Player Page + main.py Template

### Shared Player Page (`turtle/index.html`)

A single HTML file serves all 7 turtle simulations. It reads the `?sim=` URL parameter and dynamically injects the correct `<script type="py">` tag before PyScript's `core.js` loads.

**Notes:**
- Simulation pages use a **light theme** (white background, dark text) per project convention — distinct from the dark-themed landing page.
- If no `?sim=` parameter is provided or an invalid sim name is given, the player page shows a "Simulation not found" message with clickable links to all available simulations.
- `core.css` exists at the CDN URL below and styles PyScript editor components. **It does NOT provide a loading spinner.** `core.js` may inject its own loading state via JavaScript — test during Phase 1. If no loading indicator appears during the Pyodide WASM download, add a custom one (see `<div id="loading">` in the HTML template below and the `py:ready` event listener to hide it).
- The regular `<script>` runs synchronously during DOM parsing, creating the `<script type="py">` element. Since `core.js` is loaded as `type="module"` (always deferred), it runs after parsing — so the dynamic tag is already in the DOM when PyScript initializes.
- The `src` path in `<script type="py" src="flower/main.py">` is relative to `turtle/index.html`, so `flower/main.py` resolves to `turtle/flower/main.py` on disk.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading... | Py-Playground</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">
    <script>
        // Sim metadata — title and description for each turtle simulation
        const SIMS = {
            'flower':              { title: 'Flower',              desc: 'Rotating filled triangles forming a flower pattern' },
            'polygon':             { title: 'Polygon',             desc: 'Polygons with increasing sides (3 to 50)' },
            'curved-graph':        { title: 'Curved Graph',        desc: 'Curved line art pattern in 4 quadrants' },
            'chaos-pi-e':          { title: 'Chaos with PI and E', desc: 'Spiral pattern using sqrt, pi, and e constants' },
            'sierpinski-triangle': { title: 'Sierpinski Triangle', desc: 'Chaos game fractal using random midpoint method' },
            'barnsley-fern':       { title: 'Barnsley Fern',       desc: 'IFS fractal fern using affine transformations' },
            'fractal-tree':        { title: 'Fractal Tree',        desc: 'Recursive tree using turtle cloning and generators' },
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
        }
        h1 { color: #0d1117; }
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
            const tag = document.createElement('script');
            tag.type = 'py';
            tag.src = `${sim}/main.py`;
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

Every turtle `main.py` uses `async def main()` so it works in both browser and locally. The key challenge is that **PyScript does NOT auto-call `main()`** — the file's top-level code runs, but `async def main()` only defines the function. We must explicitly invoke it.

**Pattern:** Use `asyncio.get_running_loop()` to detect the environment — Pyodide (browser) has a running event loop; local Python does not.

```python
# Original repo: dev-arctik/Python-Turtle
import turtle
import asyncio
# import random  # if needed
# import math    # if needed

async def main():
    t = turtle.Turtle()
    # ... setup code (tracer() calls go here, before loops) ...

    # Adapted Python code here
    # (capped loops, removed exitonclick, etc.)

    for i in range(5000):  # example: capped loop
        # ... drawing logic ...
        if i % 500 == 0:
            await asyncio.sleep(0)  # yields in browser, no-op locally

# Detect environment and run main()
try:
    # Browser: Pyodide has a running event loop — schedule main() as a task
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    # Local: no running event loop — use asyncio.run()
    asyncio.run(main())
    turtle.exitonclick()
```

> **Note:** This pattern MUST be tested with a minimal script during Phase 1. If `create_task()` doesn't work as expected in Pyodide, use this concrete fallback — change the player page's JS to fetch the script content and inject it as inline code:
> ```javascript
> // Fallback: fetch script content and inject inline instead of using src=
> fetch(`${sim}/main.py`).then(r => r.text()).then(code => {
>     const tag = document.createElement('script');
>     tag.type = 'py';
>     tag.textContent = code;
>     document.body.appendChild(tag);
> });
> ```
> This avoids Python import path issues (folder names use hyphens, not valid Python identifiers) by injecting the script content directly.

---

## References

- Original source repository: `https://github.com/dev-arctik/Python-Turtle`
- PyScript documentation: `https://docs.pyscript.net/`
- PyScript CDN (stable): `https://pyscript.net/releases/2024.1.1/core.js`
- Pyodide documentation: `https://pyodide.org/en/stable/`
- Python turtle module docs: `https://docs.python.org/3/library/turtle.html`
- Project CLAUDE.md: `../../CLAUDE.md`
