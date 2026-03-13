# Repository Guidelines

## Project Structure & Module Organization
This repository is a single-file static web app. [`index.html`](/C:/claude-code/code/chub-leaderboard/index.html) contains the HTML markup, embedded CSS, and all JavaScript logic for rendering the weight-progress chart and fetching celebrity photos from Wikipedia. Local notes live under [`.claude/`](/C:/claude-code/code/chub-leaderboard/.claude), but application behavior should remain centered in `index.html` unless the project is intentionally restructured.

## Build, Test, and Development Commands
There is no build step or package manager setup.

- `python -m http.server 8000` runs a local static server from the repo root.
- Open `http://localhost:8000` to test the app in a browser.
- `start index.html` is acceptable for a quick manual check, but use a local server when validating API fetch behavior.
- `git status` reviews your working tree before committing.

## Coding Style & Naming Conventions
Use vanilla HTML, CSS, and JavaScript only; keep the app dependency-free unless there is a clear reason to change architecture. Follow the existing style in `index.html`: two-space indentation, semicolons, `const`/`let` over `var`, and descriptive camelCase names such as `renderChart`, `photoCache`, and `nextCeleb`. Keep data constants uppercase, for example `CELEBRITIES`. Prefer small helper functions for display logic and keep comments short and purposeful.

## Testing Guidelines
Testing is currently manual. Verify:

- weight inputs update stats and chart markers correctly
- progress direction behaves for start/current/goal edge cases
- Wikipedia thumbnails load without breaking the fallback initials UI
- layout remains usable on desktop and mobile widths

When adding logic, include clear reproduction steps in the PR if no automated tests are added.

## Commit & Pull Request Guidelines
The current Git history uses short, imperative summaries, for example: `Initial commit: Celebrity weight scale leaderboard`. Continue with concise subject lines that describe the change directly. Pull requests should include a brief summary, note any UI or behavior changes, list manual test steps, and attach screenshots or a short screen recording for visual updates.

## Security & Content Notes
Celebrity weights are approximate motivational markers, not medical data. Keep copy neutral, avoid sensitive claims, and preserve graceful handling when the Wikipedia API does not return a thumbnail.
