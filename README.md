# Py-Playground

Python turtle and pygame simulations running entirely in your browser — no installs, no backend.

**Live demo:** [dev-arctik.github.io/py-playground](https://dev-arctik.github.io/py-playground/)

## What is this?

This repo consolidates several standalone Python simulation repos into a single portfolio site deployed on GitHub Pages. Instead of maintaining 7+ separate repos that each require a local Python install to run, everything is now compiled to WebAssembly via [Pyodide](https://pyodide.org/) and runs directly in the browser.

### Original repos (now replaced by this one)

These repos contained the original Python source code. Each has been ported to run in-browser and merged here:

| Original Repo | Type | Simulations |
|---|---|---|
| `dev-arctik/Python-Turtle` | Turtle | Flower, Polygon, Curved Graph, Chaos PI+E, Sierpinski Triangle, Barnsley Fern, Fractal Tree |
| `dev-arctik/Moving-Square` | Pygame | Moving Square |
| `dev-arctik/Jumping-Square-` | Pygame | Jumping Square |
| `dev-arctik/Pendulum` | Pygame | Pendulum |
| `dev-arctik/Sine-Wave` | Pygame | Sine Wave |
| `dev-arctik/Sierpinski-s-Triangle` | Pygame | Sierpinski's Triangle |
| `dev-arctik/Paint-board` | Pygame | Paint Board |
| `dev-arctik/Paint-Canvas` | Pygame | Paint Random Screen, Paint Random Color, RGB Strips |
| `dev-arctik/Python-Game` | Pygame | First Game |
| `dev-arctik/python-minesweeper` | Pygame | Minesweeper |

## How does Python run in a browser?

Browsers only execute JavaScript natively. To run Python, we need a bridge — that's where **Pyodide** and **PyScript** come in.

### Pyodide — CPython compiled to WebAssembly

[Pyodide](https://pyodide.org/) takes the entire CPython interpreter (the same one you run with `python3` on your machine) and compiles it to [WebAssembly (WASM)](https://webassembly.org/) — a binary instruction format that browsers can execute at near-native speed.

When you open a simulation on this site, here's what happens:

1. The browser downloads the Pyodide runtime (~15 MB on first visit, cached after that)
2. Pyodide boots a full CPython interpreter inside the browser tab
3. Your Python code runs in that interpreter — `import math`, `for` loops, `async/await` — all real Python
4. The results (SVG graphics, canvas pixels) get passed back to JavaScript for rendering

Pyodide supports most of the Python standard library and can install pure-Python packages. However, modules that depend on system libraries (like `tkinter` for GUI windows) are stripped out since there's no operating system underneath — just the browser sandbox.

### PyScript — the HTML-friendly wrapper

[PyScript](https://pyscript.net/) is built on top of Pyodide and makes it easier to embed Python directly in HTML pages. Instead of writing JavaScript glue code to load Pyodide, you just write:

```html
<script type="py">
    import math
    print(f"Pi is {math.pi}")
</script>
```

PyScript handles loading Pyodide, managing packages, and connecting Python to the DOM. It also provides a special `<script type="py-game">` tag that sets up a pygame-compatible canvas automatically — which is how the pygame simulations will work.

### How this project uses them

**Turtle simulations** use Pyodide directly (not PyScript) because the standard `turtle` module is removed from Pyodide (it depends on tkinter, which needs a display server). Instead, we use the [RPi Foundation's turtle library](https://github.com/RaspberryPiFoundation/turtle) — a drop-in replacement that renders to SVG instead of a tkinter window.

The flow for a turtle simulation:

```
Browser loads Pyodide → loads RPi turtle wheel → runs your Python code
→ turtle draws to an internal SVG → SVG gets inserted into the page
```

Each simulation draws progressively — you can watch the turtle animate line by line, just like running it locally.

**Pygame simulations** (coming soon) will use PyScript with `<script type="py-game">` to run [pygame-ce](https://pyga.me/) via Pyodide, rendering to an HTML `<canvas>` element.

## Running locally

The simulation scripts also work as standard Python turtle/pygame programs:

```bash
# Install dependencies
poetry install

# Run any turtle simulation
poetry run python turtle/flower/main.py
poetry run python turtle/fractal-tree/main.py

# Run any pygame simulation (once converted)
poetry run python pygame/moving-square/main.py
```

Requires Python 3.12+ and `python-tk` for turtle (install via `brew install python-tk@3.12` on macOS).

## Project structure

```
py-playground/
├── index.html                    # Landing page gallery
├── assets/style.css              # Shared landing page styles
├── turtle/
│   ├── index.html                # Shared turtle player (Pyodide + RPi turtle)
│   ├── turtle-0.0.1-py3-none-any.whl
│   ├── flower/main.py
│   ├── polygon/main.py
│   ├── curved-graph/main.py
│   ├── chaos-pi-e/main.py
│   ├── sierpinski-triangle/main.py
│   ├── barnsley-fern/main.py
│   └── fractal-tree/main.py
├── pygame/                       # Coming soon
│   └── ...
├── pyproject.toml
└── docs/planning/                # Conversion planning docs
```

## Tech stack

- **Runtime:** Pyodide (CPython → WebAssembly)
- **Turtle rendering:** RPi Foundation SVG turtle wheel
- **Pygame rendering:** PyScript + pygame-ce (planned)
- **Hosting:** GitHub Pages
- **Package manager:** Poetry (local development)
- **Design:** Instrument Serif + IBM Plex Mono, dark theme

## Status

- [x] 7 turtle simulations — all working
- [ ] 11 pygame simulations — coming soon
