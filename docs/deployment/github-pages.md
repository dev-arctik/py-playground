# Deployment: GitHub Pages

**Last Updated:** 2026-02-17
**Status:** Active
**Environment(s):** Production
**Live URL:** https://dev-arctik.github.io/py-playground/

---

## Overview

py-playground is a fully static site — pure HTML, CSS, and JavaScript, with no build step. Python simulations run entirely in the browser via Pyodide (turtle) and PyScript (pygame). The site is deployed to GitHub Pages on every push to `main` via a 3-job GitHub Actions pipeline defined in `.github/workflows/deploy.yml`.

There is no server, no backend, and no build tool. The entire repository root is uploaded as the Pages artifact and served directly.

**Related planning doc:** `docs/planning/github-pages-cicd.md` — covers the design rationale for the CI/CD pipeline. This document covers day-to-day operation.

---

## Prerequisites

- [ ] Push access to the `main` branch of `github.com/dev-arctik/py-playground`
- [ ] GitHub Pages is configured: Settings → Pages → Source = "GitHub Actions"
- [ ] The workflow file `.github/workflows/deploy.yml` exists in the repo

No local tools are required to trigger a deployment — pushing to `main` is sufficient.

---

## Environment Setup

### Environment Variables

N/A — py-playground is a static site with no secrets or server-side configuration. All external resources are loaded from public CDNs at runtime by the browser.

| Resource | Where Used | CDN URL |
|----------|-----------|---------|
| Pyodide v0.26.4 | `turtle/index.html:10` | `https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js` |
| PyScript 2025.3.1 JS | `pygame/index.html:34` | `https://pyscript.net/releases/2025.3.1/core.js` |
| PyScript 2025.3.1 CSS | `pygame/index.html:10` | `https://pyscript.net/releases/2025.3.1/core.css` |
| RPi turtle wheel | `turtle/index.html:412` | `turtle/turtle-0.0.1-py3-none-any.whl` (served from repo) |

> **Note:** The turtle wheel is served from the repository itself, not a CDN. It must remain at `turtle/turtle-0.0.1-py3-none-any.whl` — the turtle player fetches it via relative path at runtime.

### Dependencies

None — the GitHub Actions runner installs Python 3.12 from the `actions/setup-python@v5` action during the `check` job. No `npm install`, no `pip install`, no `poetry install` happens during CI.

The `pyproject.toml` and `poetry.lock` at the repo root are for **local development only** (running sims locally via `poetry run python`). They play no role in the deployment pipeline.

---

## How Deployment Works

The pipeline is defined entirely in `.github/workflows/deploy.yml` (109 lines). It uses a **3-job structure** that separates quality checking from deployment:

```
┌───────────────────────────────────────────────────────────────┐
│  Trigger                                                       │
│    push → main        runs all 3 jobs (check → build → deploy)│
│    pull_request → main  runs check job only (no deploy)        │
│    workflow_dispatch   runs all 3 jobs (manual trigger)        │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────────┐
│  Job 1: check  (all triggers)                                 │
│    • actions/checkout@v4                                       │
│    • actions/setup-python@v5  (Python 3.12)                   │
│    • py_compile every .py in turtle/ and pygame/              │
│    • verify each sim folder contains main.py                   │
└──────────────────────┬────────────────────────────────────────┘
                       │  needs: check
                       │  if: push or workflow_dispatch
                       ▼
┌───────────────────────────────────────────────────────────────┐
│  Job 2: build  (push to main / manual only)                   │
│    • actions/checkout@v4                                       │
│    • actions/configure-pages@v4                               │
│    • actions/upload-pages-artifact@v3  (path: . — entire root)│
└──────────────────────┬────────────────────────────────────────┘
                       │  needs: build
                       │  if: push or workflow_dispatch
                       ▼
┌───────────────────────────────────────────────────────────────┐
│  Job 3: deploy  (push to main / manual only)                  │
│    • actions/deploy-pages@v4                                   │
│    • outputs deployed URL via steps.deployment.outputs.page_url│
└───────────────────────────────────────────────────────────────┘
```

### Job Details

| Job | Runs on | Depends on | Purpose |
|-----|---------|-----------|---------|
| `check` | All pushes and PRs | — | Python syntax validation + sim structure verification |
| `build` | Push to `main` or `workflow_dispatch` | `check` | Package the entire repo root as a Pages artifact |
| `deploy` | Push to `main` or `workflow_dispatch` | `build` | Publish the artifact to GitHub Pages |

**Concurrency control** (`.github/workflows/deploy.yml:20-22`): Only one deployment runs at a time. If a new push arrives while a deployment is in progress, the in-progress run is cancelled and the new one takes over.

```yaml
concurrency:
  group: pages
  cancel-in-progress: true
```

**Permissions** (`.github/workflows/deploy.yml:14-17`): The workflow requests the minimum permissions required for OIDC-based Pages deployment.

```yaml
permissions:
  contents: read   # read repo files
  pages: write     # deploy to GitHub Pages
  id-token: write  # OIDC token for secure deployment
```

---

## How to Deploy

### Standard Deployment (push to main)

```bash
git push origin main
```

That is the entire deployment process. The workflow triggers automatically, runs `check → build → deploy`, and the live site updates at `https://dev-arctik.github.io/py-playground/` within ~1-2 minutes.

### Manual Deployment (workflow_dispatch)

To trigger a deployment without pushing new code:

1. Go to https://github.com/dev-arctik/py-playground/actions
2. Select the "CI / Deploy" workflow in the left sidebar
3. Click "Run workflow"
4. Leave branch as `main`, click the green "Run workflow" button

This runs the full `check → build → deploy` chain, identical to a push.

---

## PR Workflow

Pull requests against `main` run the `check` job only. The `build` and `deploy` jobs are skipped — enforced by the `if` condition on those jobs:

```yaml
# .github/workflows/deploy.yml:82
if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
```

**What `check` validates on every PR:**

1. **Python syntax** (`.github/workflows/deploy.yml:39-51`): Runs `python -m py_compile` on every `.py` file found under `turtle/` and `pygame/`. A single syntax error fails the entire job.

2. **Sim structure** (`.github/workflows/deploy.yml:54-77`): Iterates every subdirectory in `turtle/*/` and `pygame/*/` and verifies that `main.py` exists. Fails if any sim folder is missing its entry point.

PRs that fail `check` cannot be merged (assuming branch protection is enabled). No code with broken Python syntax or a missing `main.py` can reach `main`.

---

## Monitoring

### Check Workflow Status

Live workflow runs: https://github.com/dev-arctik/py-playground/actions

Each run shows the 3 jobs as a visual pipeline. Click any job to expand its step logs.

### Check Deployment History

All deployments (with commit hash and timestamp): https://github.com/dev-arctik/py-playground/deployments

### Check the Deployed URL

The `deploy` job outputs the URL after each successful run. It appears in the Actions log under the "Deploy to GitHub Pages" step and is also visible in the GitHub Pages settings:
https://github.com/dev-arctik/py-playground/settings/pages

---

## Infrastructure

### Architecture Diagram

```
Developer workstation
        │
        │  git push origin main
        ▼
GitHub (git host + CI runner)
        │
        ├── Job: check
        │       Python 3.12 runner
        │       py_compile all .py files
        │       verify main.py presence
        │
        ├── Job: build
        │       actions/configure-pages
        │       upload-pages-artifact (entire repo root)
        │
        └── Job: deploy
                actions/deploy-pages
                        │
                        ▼
              GitHub Pages CDN
              https://dev-arctik.github.io/py-playground/
                        │
                        │  browser requests
                        ▼
              End user's browser
              Pyodide / PyScript loads Python runtime
              Simulations run 100% client-side (WebAssembly)
```

### Static File Inventory

The following files are served directly from the Pages CDN — every file committed to `main` is deployed:

| Path | Purpose |
|------|---------|
| `index.html` | Landing page gallery |
| `assets/style.css` | Landing page shared styles |
| `turtle/index.html` | Turtle simulation player (Pyodide) |
| `turtle/turtle-0.0.1-py3-none-any.whl` | RPi Foundation SVG turtle wheel |
| `turtle/<name>/main.py` | Individual turtle simulation (7 sims) |
| `pygame/index.html` | Pygame simulation player (PyScript) |
| `pygame/<name>/main.py` | Individual pygame simulation (9 sims) |

### GitHub Actions Used

| Action | Version | Job | Purpose |
|--------|---------|-----|---------|
| `actions/checkout` | v4 | check, build | Clone the repository |
| `actions/setup-python` | v5 | check | Install Python 3.12 |
| `actions/configure-pages` | v4 | build | Configure GitHub Pages deployment |
| `actions/upload-pages-artifact` | v3 | build | Package repo root as artifact |
| `actions/deploy-pages` | v4 | deploy | Publish artifact to GitHub Pages |

---

## Configuration

### GitHub Pages Settings

Navigate to: https://github.com/dev-arctik/py-playground/settings/pages

```
Build and deployment
┌─────────────────────────────┐
│ Source: GitHub Actions      │  ← Must be set to "GitHub Actions", NOT "Deploy from a branch"
└─────────────────────────────┘

Custom domain: (none)

✓ Enforce HTTPS
```

**Source must be "GitHub Actions"** — if set to "Deploy from a branch", the `actions/deploy-pages@v4` action will not work and deployments will fail.

### No Base Path Required

Because `index.html` lives at the repository root and the site is served at `https://dev-arctik.github.io/py-playground/`, all relative paths in HTML files (`turtle/?sim=flower`, `assets/style.css`, etc.) resolve correctly without any framework base path configuration. There is no Vite, no webpack, no `base` setting to manage.

---

## Rollback Plan

GitHub Pages does not support instant rollback via a UI toggle. To revert to a previous version:

1. Identify the last good commit hash from the deployments page or `git log`
2. Revert on `main`:

```bash
# Revert a specific commit (creates a new revert commit — safe for shared history)
git revert <bad-commit-hash>
git push origin main
```

Or to hard-revert to a known-good state:

```bash
# Only do this if you are certain — this rewrites history
git reset --hard <last-good-commit-hash>
git push --force-with-lease origin main
```

The push triggers the workflow, which re-deploys the reverted state. Propagation typically takes under 2 minutes, though CDN edge caches may take an additional 1-2 minutes to clear.

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Site shows 404 after deployment | Pages source is set to "Deploy from a branch" instead of "GitHub Actions" | Settings → Pages → Source → select "GitHub Actions" |
| Workflow does not trigger on push | Workflow file is not on the `main` branch, or YAML is malformed | Check `.github/workflows/deploy.yml` exists and parses without errors |
| `deploy` job fails: "Resource not accessible by integration" | `pages: write` or `id-token: write` permission missing | Verify `permissions` block at `.github/workflows/deploy.yml:14-17` |
| `check` job fails: syntax error in a `.py` file | Python file has a syntax error | Run `python -m py_compile <file>` locally to identify the line |
| `check` job fails: "Missing main.py" | A new sim folder was added without a `main.py` | Add `main.py` to the flagged folder before pushing |
| Site shows stale content after successful deployment | Browser cache or CDN propagation delay | Hard-refresh (`Cmd+Shift+R` on Mac, `Ctrl+Shift+R` on Windows/Linux); wait 1-2 minutes |
| Turtle sim shows blank page / white frame | Pyodide CDN unreachable or wheel fetch failed | Open browser DevTools → Network tab; check if `pyodide.js` or `turtle-0.0.1-py3-none-any.whl` returned an error |
| Pygame sim stays on loading spinner indefinitely | PyScript CDN unreachable, or `main.py` has a runtime error | Open browser DevTools → Console tab; check for PyScript error messages |

---

## Related

- Workflow file: `.github/workflows/deploy.yml`
- Turtle player: `turtle/index.html`
- Pygame player: `pygame/index.html`
- Planning doc (CI/CD design): `docs/planning/github-pages-cicd.md`
- Feature flow (turtle): `docs/feature-flow/turtle-simulations-flow.md`
