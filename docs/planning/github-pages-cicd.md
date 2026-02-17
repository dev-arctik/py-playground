# Deployment: GitHub Pages CI/CD with GitHub Actions

**Last Updated:** 2026-02-17
**Status:** Complete
**Live URL:** https://dev-arctik.github.io/py-playground/
**Environment(s):** Production (GitHub Pages)
**Source Reference:** [dev-arctik/digital-bouquet](https://github.com/dev-arctik/digital-bouquet) workflow

---

## Overview

This guide explains how to set up automated CI/CD deployment for static sites to GitHub Pages using GitHub Actions. The workflow is based on the digital-bouquet repository's deployment pipeline, adapted for the py-playground project.

The pipeline automatically deploys every push to the `main` branch, while running quality checks on pull requests without deploying.

## Prerequisites

- [ ] GitHub repository with static site content (HTML/CSS/JS)
- [ ] Write access to the repository (to configure settings and push workflows)
- [ ] Basic understanding of YAML syntax and GitHub Actions

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Trigger: Push to main / PR / Manual workflow_dispatch          │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Job 1: Check (runs on PRs and pushes)                          │
│  • Checkout code                                                 │
│  • Setup environment (Node/Python/etc.)                          │
│  • Run linters, type checkers, tests                             │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼ (only on push to main)
┌─────────────────────────────────────────────────────────────────┐
│  Job 2: Build (depends on check passing)                        │
│  • Checkout code                                                 │
│  • Setup environment                                             │
│  • Install dependencies                                          │
│  • Run build command (if applicable)                             │
│  • Upload build artifacts for GitHub Pages                       │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Job 3: Deploy (depends on build passing)                       │
│  • Deploy artifact to GitHub Pages                               │
│  • Returns deployed URL                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Structure

The CI/CD pipeline uses a **3-job structure** with conditional execution:

| Job | Runs On | Purpose | Dependencies |
|-----|---------|---------|--------------|
| **check** | All events (push, PR) | Quality checks (lint, test, typecheck) | None |
| **build** | Push to main only | Build static assets, prepare for deployment | `check` must pass |
| **deploy** | Push to main only | Deploy to GitHub Pages | `build` must pass |

This ensures:
- PRs are validated but not deployed
- Deployments only happen after all checks pass
- Build artifacts are created only when needed

## Step-by-Step Setup

### Step 1: Create Workflow Directory

```bash
mkdir -p .github/workflows
```

### Step 2: Create Workflow File

Create `.github/workflows/deploy.yml` with the following content:

#### For Static Python Sites (py-playground style)

This is the actual workflow used by py-playground — `.github/workflows/deploy.yml`:

```yaml
# CI/CD pipeline: validate Python sims on PRs, full deploy on push to main.
# Uses a 3-job structure: check → build → deploy.
name: CI / Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

  # allow manual trigger from Actions tab
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

# only one deployment at a time — cancel in-progress if a new push arrives
concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  # ── Check: validate Python scripts and project structure ─────────────
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      # syntax-check every .py file in turtle/ and pygame/
      - name: Check Python syntax
        run: |
          echo "Checking Python syntax..."
          errors=0
          while IFS= read -r f; do
            if ! python -m py_compile "$f"; then
              errors=$((errors + 1))
            fi
          done < <(find turtle pygame -name '*.py')
          if [ "$errors" -gt 0 ]; then
            echo "::error::$errors Python file(s) have syntax errors"
            exit 1
          fi
          echo "All Python files pass syntax check"

      # every sim directory should have a main.py
      - name: Verify sim structure
        run: |
          echo "Verifying each sim folder has main.py..."
          errors=0
          for dir in turtle/*/; do
            # skip non-directories and the .whl file
            [ -d "$dir" ] || continue
            if [ ! -f "${dir}main.py" ]; then
              echo "::error::Missing main.py in $dir"
              errors=$((errors + 1))
            fi
          done
          for dir in pygame/*/; do
            [ -d "$dir" ] || continue
            if [ ! -f "${dir}main.py" ]; then
              echo "::error::Missing main.py in $dir"
              errors=$((errors + 1))
            fi
          done
          if [ "$errors" -gt 0 ]; then
            echo "::error::$errors sim folder(s) missing main.py"
            exit 1
          fi
          echo "All sim folders have main.py"

  # ── Build: prepare static files for deployment (gated by check) ──────
  build:
    needs: check
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Pages
        uses: actions/configure-pages@v4

      # no build step — static HTML/CSS/JS site with Pyodide and PyScript
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: .

  # ── Deploy: publish to GitHub Pages (gated by build) ─────────────────
  deploy:
    needs: build
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

#### For Build-Required Sites (Vite/React/etc.)

```yaml
# CI/CD pipeline: lint + typecheck + test on PRs, full deploy on push to main.
# Uses a 3-job structure: check → build → deploy.

name: CI / Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  # ── Check: lint, typecheck, and test (runs on PRs and pushes) ────────
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Typecheck
        run: tsc -b

      - name: Test
        run: npm run test:ci

  # ── Build: only on push/dispatch to main (gated by check) ───────────
  build:
    needs: check
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: dist  # Vite builds to dist/ by default

  # ── Deploy: publish to GitHub Pages (gated by build) ─────────────────
  deploy:
    needs: build
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Step 3: Configure Repository Settings

1. Go to repository settings: `https://github.com/<username>/<repo>/settings/pages`
2. Under "Build and deployment":
   - **Source:** Select "GitHub Actions" (NOT "Deploy from a branch")
   - This tells GitHub to use the workflow file instead of auto-deploying from a branch

**Screenshot reference:**
```
┌─────────────────────────────────────────┐
│ Build and deployment                    │
├─────────────────────────────────────────┤
│ Source                                  │
│ ┌─────────────────────────────────────┐ │
│ │ GitHub Actions                  [▼] │ │  ← Select this
│ └─────────────────────────────────────┘ │
│                                         │
│ ✓ Enforce HTTPS                         │
└─────────────────────────────────────────┘
```

### Step 4: Configure Build Settings (If Applicable)

If your site requires a build step with a framework like Vite, configure the base path:

**For Vite (`vite.config.ts`):**
```typescript
import { defineConfig } from 'vite';

export default defineConfig({
  // Base path must match GitHub repo name
  base: '/py-playground/',  // Replace with your repo name

  // ... other config
});
```

**For Next.js (`next.config.js`):**
```javascript
module.exports = {
  basePath: '/py-playground',
  output: 'export',
};
```

**For Create React App (`package.json`):**
```json
{
  "homepage": "https://<username>.github.io/<repo-name>/"
}
```

### Step 5: Commit and Push Workflow

```bash
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Pages CI/CD workflow"
git push origin main
```

### Step 6: Verify Deployment

1. Go to the "Actions" tab in your repository
2. You should see the workflow running (triggered by the push)
3. Wait for all jobs to complete (check → build → deploy)
4. Visit your site at `https://<username>.github.io/<repo-name>/`

## Workflow Components Explained

### Triggers (`on`)

```yaml
on:
  push:
    branches: [main]      # Deploy on push to main
  pull_request:
    branches: [main]      # Validate PRs (check only)
  workflow_dispatch:      # Allow manual trigger from UI
```

### Permissions

```yaml
permissions:
  contents: read          # Read repo contents
  pages: write            # Deploy to GitHub Pages
  id-token: write         # OIDC token for secure deployment
```

### Concurrency Control

```yaml
concurrency:
  group: pages
  cancel-in-progress: true  # Cancel old deployments if new push arrives
```

Prevents multiple deployments from running simultaneously — newer pushes cancel older in-progress deployments.

### Job Dependencies

```yaml
jobs:
  check:
    # Runs on all events

  build:
    needs: check                # Wait for check to pass
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    # Only runs on push to main or manual trigger

  deploy:
    needs: build                # Wait for build to pass
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    # Only runs after successful build
```

### Key Actions Used

| Action | Version | Purpose |
|--------|---------|---------|
| `actions/checkout@v4` | v4 | Clone the repository |
| `actions/setup-node@v4` | v4 | Install Node.js (for build-required sites) |
| `actions/configure-pages@v4` | v4 | Configure GitHub Pages deployment |
| `actions/upload-pages-artifact@v3` | v3 | Upload static files as deployment artifact |
| `actions/deploy-pages@v4` | v4 | Deploy artifact to GitHub Pages |

## Environment Variables (If Needed)

If your build requires environment variables (API keys, feature flags), add them as **GitHub Secrets**:

1. Go to `Settings → Secrets and variables → Actions`
2. Click "New repository secret"
3. Add your secret (e.g., `VITE_API_KEY`)
4. Reference in workflow:

```yaml
- name: Build
  run: npm run build
  env:
    VITE_API_KEY: ${{ secrets.VITE_API_KEY }}
```

> **SECURITY:** Never commit secrets to the repository. Always use GitHub Secrets.

## Troubleshooting

### Problem: 404 Error After Deployment

**Likely Cause:** Base path mismatch

**Solution:**
- For subpath deployments (`username.github.io/repo-name/`), ensure `base` in Vite config matches the repo name
- For custom domains or root deployments, set `base: '/'`

### Problem: Workflow Doesn't Trigger

**Likely Cause:** Incorrect trigger configuration

**Solution:**
- Check branch name matches (`main` vs `master`)
- Ensure workflow file is in `.github/workflows/` directory
- Verify YAML syntax (no tabs, correct indentation)

### Problem: Deploy Job Fails with "Resource not accessible by integration"

**Likely Cause:** Missing Pages write permission

**Solution:**
- Add `permissions` block to workflow (see template above)
- Verify repository settings allow GitHub Actions to deploy to Pages

### Problem: Build Job Fails with "Cannot find module"

**Likely Cause:** Dependencies not cached correctly or wrong Node version

**Solution:**
- Use `npm ci` instead of `npm install` (installs from package-lock.json)
- Specify Node version explicitly in `actions/setup-node@v4`
- Check that `package-lock.json` is committed

### Problem: Deployment Succeeds but Site Shows Old Content

**Likely Cause:** Browser cache or CDN propagation delay

**Solution:**
- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Wait 1-2 minutes for GitHub's CDN to update
- Check Actions tab to confirm latest deployment completed successfully

## Deployment Checklist

Before deploying to production, verify:

- [ ] Workflow file is in `.github/workflows/` directory
- [ ] Repository settings → Pages → Source is set to "GitHub Actions"
- [ ] Base path configured correctly (if using a build tool)
- [ ] No secrets or credentials committed to repository
- [ ] Workflow runs successfully on a test branch first
- [ ] All links and assets use relative paths or include base path
- [ ] 404 page configured (optional: create `404.html` in root)

## Advanced: Custom Domain Setup

To use a custom domain (e.g., `www.example.com`):

1. Create a `CNAME` file in the root of your site:
   ```
   www.example.com
   ```

2. Add the CNAME file to the artifact upload:
   ```yaml
   - name: Upload artifact
     uses: actions/upload-pages-artifact@v3
     with:
       path: dist
   ```

3. Configure DNS records with your domain provider:
   ```
   Type: CNAME
   Name: www
   Value: <username>.github.io
   ```

4. Go to repository settings → Pages → Custom domain
5. Enter your domain and click "Save"
6. Enable "Enforce HTTPS" after DNS propagates (24-48 hours)

## Monitoring Deployments

### View Deployment History
- Go to: `https://github.com/<username>/<repo>/deployments`
- Shows all deployments, timestamps, and commit hashes

### View Workflow Runs
- Go to: `https://github.com/<username>/<repo>/actions`
- Shows all workflow runs with logs for each job

### Check Deployment URL
The deploy job outputs the URL:
```yaml
environment:
  name: github-pages
  url: ${{ steps.deployment.outputs.page_url }}
```

Access it in the Actions tab after deployment completes.

## py-playground Specific Notes

For the py-playground project:

1. **No build step required** — the site is pure HTML/CSS/JS with Pyodide (turtle) and PyScript (pygame)
2. **Deploy entire repo root** — `path: .` in `upload-pages-artifact` serves all HTML, CSS, JS, `.py`, and `.whl` files directly
3. **Check job validates Python** — uses `python -m py_compile` on every `.py` file in `turtle/` and `pygame/`, and verifies every sim directory contains a `main.py`
4. **check runs on PRs** — PRs are validated but never deployed; `build` and `deploy` are gated to `push` and `workflow_dispatch` only
5. **Pages enabled via API** — GitHub Pages was configured with `build_type=workflow` (not "Deploy from a branch") so that the Actions workflow controls all deployments
6. **Live URL:** `https://dev-arctik.github.io/py-playground/`

### Check Job Details

The `check` job performs two validations:

| Step | Tool | What it checks |
|------|------|----------------|
| Check Python syntax | `python -m py_compile` | Every `.py` in `turtle/` and `pygame/` — fails if any file has a syntax error |
| Verify sim structure | bash `for dir` loop | Every `turtle/*/` and `pygame/*/` subdirectory must contain a `main.py` |

Python version used: **3.12** (via `actions/setup-python@v5`).

### Workflow Trigger Matrix

| Event | check | build | deploy |
|-------|-------|-------|--------|
| Push to `main` | Yes | Yes (needs check) | Yes (needs build) |
| Pull request to `main` | Yes | No | No |
| `workflow_dispatch` | Yes | Yes (needs check) | Yes (needs build) |

### Actual Workflow File

The deployed workflow is at `.github/workflows/deploy.yml` — see the "For Static Python Sites" template above for the exact content. The workflow name is `CI / Deploy`.

## References

- **Source workflow:** [dev-arctik/digital-bouquet/.github/workflows/deploy.yml](https://github.com/dev-arctik/digital-bouquet/blob/main/.github/workflows/deploy.yml)
- **GitHub Actions docs:** https://docs.github.com/en/actions
- **GitHub Pages docs:** https://docs.github.com/en/pages
- **actions/deploy-pages:** https://github.com/actions/deploy-pages
- **actions/upload-pages-artifact:** https://github.com/actions/upload-pages-artifact
- **actions/configure-pages:** https://github.com/actions/configure-pages

---

## Revision History

| Date | Change |
|------|--------|
| 2026-02-17 | Initial version — adapted from digital-bouquet workflow |
| 2026-02-17 | Updated to reflect actual 3-job pipeline: check (Python syntax + sim structure validation) → build → deploy; added PR trigger, workflow_dispatch, trigger matrix, check job detail table; replaced single-job "recommended workflow" with real deploy.yml content; added live URL |
