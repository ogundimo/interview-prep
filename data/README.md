# Data

[Home](../README.md) · [CLI](../scripts/README.md) · [Templates](../templates/README.md)

**Single source of truth:** `attempts.csv` holds every attempt; each entry's frontmatter holds its static facts. Everything else (review dates, status, dashboards, charts, `items.json`) is **derived** by `prep build`, so nothing can drift.

| File | Edited by | Contents |
|---|---|---|
| [attempts.csv](attempts.csv) | `prep stop` / `prep log` / `prep import` | `id, date, minutes, outcome, grade, lang, source, phases, note`. `source` is `timer`, `manual`, `leethub` or `legacy`; only `timer` and `manual` count toward speed stats |
| [config.json](config.json) | you | Targets, intervals, mastery rule, weekly hours, new/review ratio, LeetHub location |
| [interviews.csv](interviews.csv) | `prep interview` | Scheduled mocks and real interviews |
| [problem-lists/neetcode150.csv](problem-lists/neetcode150.csv) | rarely | NeetCode 150: number, slug, title, difficulty, pattern, premium |
| [behavioral-themes.json](behavioral-themes.json) | you | Behavioral themes and their common questions |
| [lc-cache.json](lc-cache.json) | `prep` | Cached LeetCode metadata (public number, difficulty, topics) |
| [items.json](items.json) | `prep build` | Snapshot of every entry with status and next review, for other tools |
| `.timer.json` | `prep start` | Running timer (git-ignored) |

Editing the CSV by hand is fine; run `prep build` afterwards.
