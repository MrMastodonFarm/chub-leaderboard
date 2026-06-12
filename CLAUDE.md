# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# chub-leaderboard

## Dev Server
```
python -m http.server 8000
```
Open `http://localhost:8000`. Use a local server (not `file://`) when testing Wikipedia API fetches.

## Architecture
Two standalone single-file HTML apps — no build step, no dependencies, no package manager:

- **`index.html`** — SVG chart leaderboard. Tracks celebrity weights with progress markers and Wikipedia thumbnails. Links to punch-out view.
- **`punch-out.html`** — Retro arcade UI with circuit-based opponent groupings and pixel-art fighter portraits.
- **`assets/fighters/`** — AI-generated NES Punch-Out-style portrait PNGs for the fighter cards. Reproducible: `comfy_gen.py` + `prompts.json` in that folder hold the exact ComfyUI workflow, prompt, and seed per fighter (server: ComfyUI on the local network; see the repo memory notes). To add a fighter, add a job to `prompts.json` following the existing prompt formula and re-run.

## Stack
Vanilla HTML/CSS/JS only. No frameworks, no bundler, no npm.

## Key Data Structures
- `CELEBRITIES` — **duplicated independently in each HTML file, and the lists differ.** `index.html` sorts ascending by weight with a `wiki` field for photo lookup; `punch-out.html` sorts descending with sprite color fields (`hair`, `shirt`, `skin`). The rosters are not identical (e.g. only `index.html` has Gabriel Iglesias; only `punch-out.html` has Chris Farley). Adding or changing a celebrity means editing both files deliberately — there is no shared source of truth.
- `CIRCUITS` (`punch-out.html`) — groups fighters by **index ranges** (`start`/`end`) into `CELEBRITIES`, so circuit membership silently breaks if the array order changes.
- `photoCache` (`index.html`) — in-memory cache of Wikipedia REST API thumbnail responses.

## Patterns
- **DOM rendering**: imperative full-rebuild on each update (no virtual DOM, no diffing). `renderPage()` in punch-out, `renderChart()`/`renderStats()` in index.
- **State**: read directly from the three weight `<input>`s on each render; defaults live in the HTML `value` attributes. No localStorage — the two pages do not share state.
- **Photos (`index.html`)**: Wikipedia REST API (`/page/summary/{title}`) with fallback to initials avatar.
- **Portraits (`punch-out.html`)**: image-first with CSS fallback. Filename is `<fighterSlug(name)>.png` (kebab-case), with explicit overrides possible in `PORTRAIT_FILES`. On image load, `has-art` class hides the fallback; on error the `<img>` removes itself and CSS-only pixel-art divs (colored by `--hair`/`--skin`/`--shirt` custom properties from celebrity data) show instead.

## Coding Style
- Two-space indentation, semicolons
- `const`/`let` over `var`
- Descriptive camelCase: `renderChart`, `photoCache`, `nextCeleb`
- Uppercase data constants: `CELEBRITIES`, `CIRCUITS`
- Small helper functions for display logic
- Short, purposeful comments

## Testing
Manual only. Verify:
- Weight inputs update stats and chart markers
- Progress direction correct for start/current/goal edge cases (both pages support gain and loss goals via `isLosing`)
- Wikipedia thumbnails load; fallback initials UI works when they don't
- Punch-out portraits load; CSS pixel-art fallback renders for fighters without art
- Layout usable on desktop and mobile widths

## Commit Style
Short imperative summaries: `Add punch-out circuit UI`, `Fix Wikipedia fallback avatar`.

## Content Notes
Celebrity weights are approximate motivational markers, not medical data. Keep copy neutral and avoid sensitive claims.
