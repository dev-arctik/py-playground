# Flow: Turtle Simulations

**Last Updated:** 2026-02-18
**Status:** Active

---

## Overview

A unified system for running Python turtle graphics simulations in the browser using Pyodide (CPython compiled to WebAssembly) with a custom progressive animation system. Seven turtle simulations are served by a single shared player page that loads simulation code dynamically based on URL parameters.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         Browser Environment                               │
│                                                                           │
│  User visits:                                                             │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ Landing Page (index.html)                          │                  │
│  │ - Dark theme gallery of simulation cards           │                  │
│  │ - Links: turtle/?sim=flower, turtle/?sim=polygon   │                  │
│  └────────────────┬───────────────────────────────────┘                  │
│                   │ Click sim card                                       │
│                   ↓                                                       │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ Player Page (turtle/index.html?sim=<name>)         │                  │
│  │ - Reads ?sim= param from URL                       │                  │
│  │ - Loads Pyodide + registers fake basthon module    │                  │
│  │ - Loads RPi turtle wheel (SVG-based turtle)        │                  │
│  │ - Monkey-patches asyncio.sleep for progressive SVG │                  │
│  │ - Fetches <name>/main.py and runs main()           │                  │
│  └────────────────┬───────────────────────────────────┘                  │
│                   │ fetch("<name>/main.py")                              │
│                   ↓                                                       │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ Simulation Code (turtle/<name>/main.py)            │                  │
│  │ - Dual-mode pattern (browser vs local detection)   │                  │
│  │ - async def main() with drawing logic               │                  │
│  │ - Calls await asyncio.sleep(0) for animation frames│                  │
│  └────────────────┬───────────────────────────────────┘                  │
│                   │ asyncio.sleep(0) triggers render                     │
│                   ↓                                                       │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ Progressive Animation System                        │                  │
│  │ - Monkey-patched asyncio.sleep calls turtle.show_scene()│             │
│  │ - Renders current state as SVG dict                 │                  │
│  │ - Triggers basthon.kernel.display_event()           │                  │
│  └────────────────┬───────────────────────────────────┘                  │
│                   │ display_event({content: svg_dict})                   │
│                   ↓                                                       │
│  ┌────────────────────────────────────────────────────┐                  │
│  │ SVG Rendering Pipeline                              │                  │
│  │ - elementFromProps(svg_dict) → createElementNS      │                  │
│  │ - SVG namespace handling for all SVG tags           │                  │
│  │ - Safe DOM construction (no innerHTML)              │                  │
│  │ - Replaces canvas-frame contents with new SVG       │                  │
│  └────────────────┬───────────────────────────────────┘                  │
│                   ↓                                                       │
│              White lightbox frame displays live SVG                      │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

Alternative flow — No sim selected:
  turtle/index.html (no ?sim=) → Shows listing of all 7 sims as clickable cards
```

---

## User Flow

1. User visits landing page at `index.html`
2. User scrolls to "Turtle Graphics" section (7 simulation cards)
3. User clicks a simulation card (e.g., "Flower")
4. Browser navigates to `turtle/?sim=flower`
5. Player page shows loading spinner while Pyodide downloads (~15 MB on first visit)
6. Loading text updates: "Loading Python runtime..." → "Running simulation..."
7. Canvas frame shows progressive rendering — SVG updates every `await asyncio.sleep(0)` call
8. When simulation completes, final SVG remains displayed
9. User clicks "Back to Gallery" to return to landing page

**Edge case:** User navigates to `turtle/` with no `?sim=` parameter → Player shows grid of 7 clickable simulation cards (internal navigation)

---

## Technical Flow

### Frontend

| Component | File | Line(s) | Purpose |
|-----------|------|---------|---------|
| Landing page gallery | `index.html` | 38-73 | Turtle section with 7 cards linking to `turtle/?sim=<name>` |
| Shared player page | `turtle/index.html` | 1-503 | Single-page player for all turtle sims, loads Pyodide + RPi turtle |
| Sim metadata config | `turtle/index.html` | 13-21 | SIMS object mapping sim names to titles and descriptions |
| URL param parsing | `turtle/index.html` | 23-27 | Reads `?sim=` param and updates page title |
| SVG namespace constants | `turtle/index.html` | 366-372 | SVG_NS and SVG_TAGS set for proper SVG element creation |
| SVG rendering function | `turtle/index.html` | 375-386 | `elementFromProps()` recursively builds DOM from SVG dict |
| Pyodide initialization | `turtle/index.html` | 392-395 | `loadPyodide()` from CDN at line 10 |
| Basthon module registration | `turtle/index.html` | 398-409 | Fake module with `kernel.display_event()` and `kernel.locals()` |
| RPi turtle wheel load | `turtle/index.html` | 412 | `pyodide.loadPackage("./turtle-0.0.1-py3-none-any.whl")` |
| Animation mode setup | `turtle/index.html` | 418 | `turtle.Screen().animation('off')` disables SMIL animations |
| Progressive animation patch | `turtle/index.html` | 420-434 | Monkey-patches `asyncio.sleep` to call `turtle.show_scene()` and `display_event()` |
| Sim code fetch and run | `turtle/index.html` | 437-444 | `fetch("${sim}/main.py")` → `runPythonAsync(code)` → `await main()` |
| Final SVG render | `turtle/index.html` | 447-453 | Calls `show_scene()` and `display_event()` after main() completes |
| Error handling | `turtle/index.html` | 455-464 | Catches errors, displays in error-state div with error message |
| Sim listing fallback | `turtle/index.html` | 466-500 | When no ?sim= param, shows grid of all sims with clickable cards |

### Simulation Scripts

| Component | File | Line(s) | Purpose |
|-----------|------|---------|---------|
| Flower simulation | `turtle/flower/main.py` | 1-30 | Draws 36 rotating filled triangles; simplest sim with 36 iterations |
| Curved Graph simulation | `turtle/curved-graph/main.py` | N/A | Curved line art pattern in 4 quadrants (not examined in detail) |
| Polygon simulation | `turtle/polygon/main.py` | N/A | Draws polygons with increasing sides (3 to 50) |
| Chaos PI+E simulation | `turtle/chaos-pi-e/main.py` | N/A | Spiral pattern using sqrt, pi, and e constants |
| Sierpinski Triangle simulation | `turtle/sierpinski-triangle/main.py` | N/A | Chaos game fractal using random midpoint method |
| Barnsley Fern simulation | `turtle/barnsley-fern/main.py` | N/A | IFS fractal fern using affine transformations |
| Fractal Tree simulation | `turtle/fractal-tree/main.py` | 1-47 | Recursive tree using turtle.clone() and generators — most complex |
| Dual-mode detection (all sims) | `turtle/*/main.py` | varies (22-29 in flower, 39-46 in fractal-tree) | `asyncio.get_running_loop()` detects browser vs local environment |
| Async main definition (all sims) | `turtle/*/main.py` | varies (6-19 in flower, 22-36 in fractal-tree) | `async def main()` with drawing logic and `await asyncio.sleep(0)` calls |
| Browser execution path (all sims) | `turtle/*/main.py` | varies | `try: asyncio.get_running_loop()` → exits silently (main() called by player) |
| Local execution path (all sims) | `turtle/*/main.py` | varies | `except RuntimeError:` → `asyncio.run(main())` + `turtle.exitonclick()` |

### API Routes

**N/A** — No backend API. All code runs client-side in the browser.

### Controllers / Business Logic

**N/A** — Pure frontend static site. Logic implemented in JavaScript (player page) and Python (simulation scripts).

### Database

**N/A** — No database. All simulations are ephemeral visualizations.

### Real-time Events

**Progressive SVG Rendering:**

| Event | Direction | Payload | Purpose |
|-------|-----------|---------|---------|
| `basthon.kernel.display_event()` | Python → JavaScript | `{ display_type: "turtle", content: <svg_dict> }` | Triggered by monkey-patched `asyncio.sleep()` and final render; sends SVG dict to JS for rendering |

**Flow:**
1. Simulation code calls `await asyncio.sleep(0)` (line 19 in `flower/main.py`)
2. Patched `_render_sleep()` calls `turtle.Screen().show_scene()` (line 429 in `turtle/index.html`)
3. `show_scene()` returns a Python dict representing current SVG state
4. `basthon.kernel.display_event()` sends dict to registered JS callback (line 430)
5. JS callback (`display_event` function at line 402) receives dict
6. `elementFromProps()` converts dict to DOM tree using `createElementNS` for SVG namespace (line 375-386)
7. `frame.replaceChildren(svgEl)` updates canvas frame with new SVG (line 405)

### State Management

**N/A** — No global state management library. State is managed via:
- URL parameters (`?sim=<name>`) for simulation selection
- Pyodide runtime globals for turtle state (managed by RPi turtle library)
- DOM state for SVG rendering (canvas-frame contents)

---

## Authentication & Authorization

**N/A** — Publicly accessible static site. No authentication or authorization.

---

## Error Handling

**Pyodide/Python Errors:**
- All errors during Pyodide load or Python execution are caught at `turtle/index.html:455-464`
- Loading spinner is hidden, error-state div is shown with `<code>` element containing `err.message`
- Errors are also logged to browser console via `console.error(err)` at line 463

**Error States:**
- Pyodide CDN unreachable → Loading hangs with "Loading Python runtime..." message
- Simulation script syntax error → Error shown: "SyntaxError: ..." with line number
- Simulation script runtime error → Error shown: "PythonError: ..." with traceback
- Turtle API not available → Error shown: "ModuleNotFoundError: No module named 'turtle'"
- Invalid `?sim=` parameter → Player shows "Choose a simulation to explore" with listing

**User-Facing Error Messages:**
- Technical errors display Python traceback/JavaScript error message in monospace font
- No friendly error messages implemented — assumes developer audience

---

## Edge Cases

**No `?sim=` Parameter:**
- Player page shows internal sim listing (lines 467-499)
- Canvas frame background becomes transparent, border removed
- Grid of 7 clickable sim cards displayed (same card style as landing page)
- User can navigate to any sim directly from player page

**Invalid `?sim=` Parameter:**
- Same as no parameter — listing is shown
- No explicit "invalid sim" error message

**Simulation Code Without `asyncio.sleep(0)` Calls:**
- Progressive animation doesn't occur — user sees loading spinner until completion
- Final SVG is still rendered after `main()` completes (lines 447-453)
- Acceptable behavior — instant rendering for fast simulations

**User Refreshes During Simulation:**
- Simulation restarts from beginning
- Pyodide runtime reloads (uses browser cache after first visit)
- No state persistence — expected behavior

**Multiple Tabs Running Different Sims:**
- Each tab runs independently with its own Pyodide instance
- No interference between tabs
- Each tab uses ~50-100 MB memory for Pyodide runtime

**Mobile/Small Viewport:**
- SVG scales to fit canvas-frame (max-width: 100%, height: auto at line 156-157)
- Player page uses responsive padding and font scaling (lines 320-327)
- Turtle graphics may be hard to see on very small screens — acceptable (desktop-optimized)

**Slow Network Connection:**
- Pyodide download (~15 MB) takes longer — loading spinner shows "Downloading Pyodide (~15 MB on first visit)" message (line 349)
- Subsequent visits use browser cache — loading is much faster
- Simulation code fetch is small (~1-5 KB per script) — negligible delay

---

## Key Code Snippets

### SVG Namespace Handling (Proper SVG Element Creation)

**File:** `turtle/index.html:366-386`

```javascript
const SVG_NS = 'http://www.w3.org/2000/svg';
// SVG tags that must be created with the SVG namespace
const SVG_TAGS = new Set([
    'svg', 'g', 'line', 'circle', 'rect', 'polygon', 'polyline',
    'path', 'text', 'tspan', 'animate', 'animateTransform', 'use',
    'defs', 'clipPath', 'image', 'ellipse',
]);

// Build a DOM element from the SVG dict returned by RPi turtle lib
function elementFromProps(map) {
    const tag = map.get("tag");
    if (!tag) return document.createTextNode(map.get("text"));

    // SVG elements need createElementNS to render correctly
    const node = SVG_TAGS.has(tag)
        ? document.createElementNS(SVG_NS, tag)
        : document.createElement(tag);
    for (const [key, value] of map.get("props")) node.setAttribute(key, value);
    for (const childProps of map.get("children")) node.appendChild(elementFromProps(childProps));
    return node;
}
```

**Why this matters:** SVG elements created with `createElement()` (HTML namespace) don't render in browsers. Must use `createElementNS(SVG_NS, tag)` for proper SVG rendering. This function recursively builds the entire SVG tree from the Python dict returned by `turtle.Screen().show_scene()`.

---

### Basthon Module Registration (Fake Module Interface)

**File:** `turtle/index.html:398-409`

```javascript
// Register fake basthon module (required by RPi turtle lib)
const visual = document.getElementById('visual');
const frame = document.getElementById('canvas-frame');
pyodide.registerJsModule("basthon", {
    kernel: {
        display_event: (e) => {
            // Safe DOM construction — no innerHTML
            const svgEl = elementFromProps(e.toJs().get("content"));
            frame.replaceChildren(svgEl);
        },
        locals: () => pyodide.runPython("globals()"),
    },
});
```

**Why this matters:** The RPi turtle library expects a `basthon` module to be available (designed for basthon.fr IDE). `display_event()` is called whenever the turtle scene needs to be rendered. We register a fake module that captures the SVG dict and renders it to the DOM. `e.toJs()` converts the Python dict to JavaScript Map, then `get("content")` extracts the SVG dict.

---

### Progressive Animation System (Monkey-Patched asyncio.sleep)

**File:** `turtle/index.html:420-434`

```javascript
// Monkey-patch asyncio.sleep to render progressive frames
pyodide.runPython(`
import asyncio
import turtle
import basthon

_orig_sleep = asyncio.sleep

async def _render_sleep(delay):
    svg_dict = turtle.Screen().show_scene()
    basthon.kernel.display_event({"display_type": "turtle", "content": svg_dict})
    await _orig_sleep(0.05)

asyncio.sleep = _render_sleep
`);
```

**Why this matters:** Standard RPi turtle renders only at the end. This patch intercepts every `await asyncio.sleep(0)` call in simulation code, renders the current turtle state as SVG, and then actually sleeps for 0.05 seconds (50ms) to create a visible animation frame. Without this, users would see only a loading spinner followed by the final result.

**Key detail:** `await _orig_sleep(0.05)` ensures a minimum delay between frames — even if simulation code calls `sleep(0)`, we render at ~20 FPS. This prevents frame flooding and keeps animations smooth.

---

### Dual-Mode Pattern (Browser vs Local Execution)

**File:** `turtle/flower/main.py:6-29` (example — all sims use this pattern)

```python
async def main():
    pen = turtle.Turtle()
    pen.color("red")
    pen.speed(0)
    pen.up()
    pen.backward(100)
    pen.down()

    for i in range(36):
        pen.begin_fill()
        pen.forward(200)
        pen.left(170)
        pen.end_fill()
        await asyncio.sleep(0)  # Yield for animation frame


# Detect environment: browser vs local
try:
    asyncio.get_running_loop()
    # Browser (Pyodide): main() will be called by the player page
except RuntimeError:
    # Local: run with standard turtle + tkinter
    asyncio.run(main())
    turtle.exitonclick()
```

**Why this matters:** The same `main.py` files work both in the browser AND locally via `poetry run python turtle/flower/main.py`. In the browser, Pyodide already has a running event loop (provided by the JavaScript environment), so `get_running_loop()` succeeds and we do nothing — the player page explicitly calls `await main()` at line 444. Locally, there's no running loop, so `get_running_loop()` raises `RuntimeError`, and we run main() with `asyncio.run()` then show the tkinter window with `exitonclick()`.

**Key detail:** The `await asyncio.sleep(0)` calls inside `main()` do nothing when running locally (just yield control instantly) but trigger progressive SVG rendering in the browser due to the monkey-patch. This makes the animation system transparent to simulation code.

---

### Simulation Loading and Execution

**File:** `turtle/index.html:437-453`

```javascript
// Fetch the sim's Python code
const code = await fetch(`${sim}/main.py`).then(r => r.text());

// Run the code — defines main() but doesn't call it in browser
// (the try/except detects the running loop and skips execution)
await pyodide.runPythonAsync(code);

// Call main() and wait for it to complete
await pyodide.runPythonAsync("await main()");

// Render the turtle scene as SVG
pyodide.runPython(`
import turtle
import basthon

svg_dict = turtle.Screen().show_scene()
basthon.kernel.display_event({ "display_type": "turtle", "content": svg_dict })
`);
```

**Why this matters:** This is the execution sequence for every simulation:
1. Fetch the `main.py` code as text
2. Run the code with `runPythonAsync()` — this executes the top-level code (imports, function definitions, and the try/except block)
3. The try/except detects the running loop and exits silently (the `try:` branch does nothing)
4. Explicitly call `await main()` to actually run the simulation
5. After `main()` completes, do a final SVG render to ensure the last state is displayed

**Key detail:** We must explicitly call `await main()` because the dual-mode pattern doesn't auto-call it in the browser. The `runPythonAsync(code)` only defines the function.

---

### Simulation Listing Fallback (No ?sim= Parameter)

**File:** `turtle/index.html:466-500`

```javascript
} else {
    // No sim selected — show listing of all available simulations
    document.getElementById('sim-title').textContent = 'Turtle Simulations';
    document.getElementById('sim-desc').textContent = 'Choose a simulation to explore';
    document.getElementById('loading').style.display = 'none';

    const frame = document.getElementById('canvas-frame');
    frame.style.background = 'transparent';
    frame.style.border = 'none';
    frame.style.boxShadow = 'none';
    frame.style.minHeight = 'auto';
    frame.style.display = 'block';

    const listing = document.createElement('div');
    listing.className = 'sim-listing';
    Object.entries(SIMS).forEach(([k, v], i) => {
        const a = document.createElement('a');
        a.href = `?sim=${k}`;
        a.className = 'sim-card';
        a.style.setProperty('--i', i);

        const title = document.createElement('div');
        title.className = 'sim-card-title';
        title.textContent = v.title;

        const desc = document.createElement('div');
        desc.className = 'sim-card-desc';
        desc.textContent = v.desc;

        a.appendChild(title);
        a.appendChild(desc);
        listing.appendChild(a);
    });
    frame.appendChild(listing);
}
```

**Why this matters:** This provides an internal navigation system within the player page. If a user navigates to `turtle/` or `turtle/index.html` without a `?sim=` parameter, they see a grid of all 7 simulations. This is a fallback/discovery mechanism — the primary flow is through the landing page gallery, but this ensures the player page is self-contained and doesn't show a blank page or error.

**Key detail:** Styles are dynamically removed from the canvas frame (`background: transparent`, `border: none`) to make it blend with the page background. Each card uses the same `sim-card` CSS class defined in the player page's styles (lines 217-266).

---

## Related Flows

**Landing Page Gallery:**
- Flow: User visits `index.html` → Sees turtle section with 7 cards → Clicks card → Navigates to `turtle/?sim=<name>`
- File: `index.html:30-74`
- Styling: `assets/style.css:1-366` (dark theme with teal accent for turtle cards)

**Pygame Simulations (11/11 Live):**
- All 11 pygame sims are live using PyScript 2025.3.1 + pygame-ce + HTML5 canvas
- Shared player page: `pygame/index.html` (same `?sim=` URL param pattern as turtle)
- First Game and Minesweeper are fully deployed; no "Coming Soon" cards remain on the landing page
- Planning doc: `docs/planning/pygame-projects.md`

**Local Development/Testing:**
- Flow: Developer runs `poetry run python turtle/<name>/main.py` → tkinter window opens → Standard turtle graphics with exitonclick()
- Same `main.py` files work in both browser and locally via dual-mode pattern
- No server required for local testing — just Python + tkinter
