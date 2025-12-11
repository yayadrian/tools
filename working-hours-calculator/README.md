# Working Hours Calculator

Vanilla JS single-page app for designing and comparing 2-week working patterns. Data persists in `localStorage`; no build step required.

## Usage
- Open `index.html` in a modern browser (or serve the folder with any static server).
- Configure contract settings: hours per week, target fortnight hours (auto-updates from weekly × 2 unless overridden), and default break minutes.
- Add, rename, duplicate, or delete patterns. Each pattern has 10 weekdays across two weeks with start/end/break inputs; daily hours, weekly totals, fortnight total, and gap recalc instantly.
- Comparison table highlights the pattern closest to zero gap among valid patterns.

## Validation
- End must be after start; break must be non-negative and less than shift duration.
- Invalid days show an inline message and are excluded from totals. A pattern with any invalid day is marked invalid and excluded from comparison highlighting.

## Checks
- Inline sanity checks run on load:
  - 37.5h/week default pattern → 75h fortnight.
  - Week-2 Friday off (others default) → 67.5h fortnight.
- Manual QA suggestions:
  - Edit start/end/break and confirm live totals and gap update.
  - Override target fortnight hours and verify gap changes.
  - Add, duplicate, rename, and delete patterns without reload.
  - Reload the page and confirm settings and patterns persist.
  - Enter invalid times/breaks to see errors and exclusion from totals.
