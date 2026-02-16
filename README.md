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

## How it works

### Turtle simulations

Turtle graphics can't run in the browser natively (no tkinter in WebAssembly). The solution:

1. **Pyodide** (v0.26.4) — CPython compiled to WebAssembly
2. **RPi Foundation's turtle library** — a drop-in SVG-based turtle module designed for Pyodide
3. A shared player page (`turtle/index.html`) loads Pyodide, runs the Python simulation, and renders the result as an SVG

Each simulation draws progressively — you can watch the turtle animate, just like running it locally.

### Pygame simulations (coming soon)

Pygame sims will use **PyScript** with `<script type="py-game">` to run pygame-ce via Pyodide with a `<canvas>` element.

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
