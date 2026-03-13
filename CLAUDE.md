# chub-leaderboard

## Dev Server
```
python -m http.server 8000
```
Open `http://localhost:8000`. Use a local server (not `file://`) when testing Wikipedia API fetches.

## Architecture
Two standalone single-file HTML apps — no build step, no dependencies, no package manager:

- **`index.html`** — SVG chart leaderboard. Tracks celebrity weights with progress markers and Wikipedia thumbnails.
- **`punch-out.html`** — Retro arcade UI with CSS-only pixel art fighter sprites and circuit-based opponent groupings.

## Stack
Vanilla HTML/CSS/JS only. No frameworks, no bundler, no npm.

## Key Data Structures
- `CELEBRITIES` — uppercase array constant holding all celebrity entries
- `CIRCUITS` — groupings of celebrities for the punch-out opponent ladder
- `photoCache` — object caching Wikipedia REST API thumbnail responses

## Patterns
- **DOM rendering**: imperative full-rebuild on each update (no virtual DOM, no diffing)
- **Photos**: Wikipedia REST API (`/page/summary/{title}`) with fallback to initials avatar
- **Sprites**: CSS-only pixel art in `punch-out.html` — no image assets

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
- Progress direction correct for start/current/goal edge cases
- Wikipedia thumbnails load; fallback initials UI works when they don't
- Layout usable on desktop and mobile widths

## Commit Style
Short imperative summaries: `Add punch-out circuit UI`, `Fix Wikipedia fallback avatar`.
