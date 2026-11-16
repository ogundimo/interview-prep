# AGENTS.md

Instructions for any coding agent (Claude, Codex, etc.) working in this repo. Read before changing anything.

## What this repo is

A personal interview-prep workspace for a new-grad SWE candidate (any track: backend, infra, frontend, full stack). Everything is driven by the `prep` CLI (`scripts/prep.py`, package `scripts/prepkit/`). Python 3.12+, PyYAML is the only dependency. Host is Windows; CI is Linux. Both must work.

## Owner's settled preferences (do not re-ask, do not change without being told)

- Languages: Python (default), Java, C++.
- Problem list: NeetCode 150 (`data/problem-lists/neetcode150.csv`).
- Target times: Easy 15, Medium 25, Hard 40 min. OAs use their real limit. System design = 45 min, phases 5/5/10/15/10.
- Review intervals: 1/3/7/14/30/60 days; grades Again/Hard/Good/Easy; mastered after 2 in-target reviews in a row.
- Budget: 48 h/week (split in `data/config.json` → `hours_per_week`). No interview date yet.
- Reminders: README dashboard + daily "Reviews due" GitHub issue.
- LeetHub syncs to the separate PRIVATE repo `ogundimo/LEETCODE-PROBLEMS`; pull it in with `prep import --sync`. Never make that repo public or copy its secrets anywhere.

## Rules

1. Use the CLI, don't hand-edit what it owns:
   - Create entries with `prep new <type> <id>`; record time with `prep start/stop` or `prep log`.
   - Never edit `data/attempts.csv` rows by hand unless fixing a typo the owner points out.
   - Never edit text between `<!-- prep:...:start -->` and `<!-- prep:...:end -->` markers; it is regenerated.
   - Never edit `assets/` charts or `data/items.json`; `prep build` regenerates them.
2. Data model: `data/attempts.csv` is the single attempt log. Entry frontmatter holds static facts (link, difficulty, tags, pattern). Review state is recomputed on every build; do not store it in frontmatter.
3. After any change: run `python scripts/prep.py build` then `python scripts/prep.py check` (must report 0 broken links). Rebuilding twice must produce no diff.
4. New entries follow the files in `templates/`. Keep the section folder layout (01-07, templates, scripts, data).
5. Entries tagged `sample: true` are demo data; `prep samples remove` deletes them. Don't add new samples.
6. Keep scripts cross-platform: `pathlib`, UTF-8 I/O, `newline=""` for CSV, no shell-specific calls. Test on Windows (`.\prep ...` or `python scripts\prep.py ...`).
7. Dependencies: stdlib + PyYAML only. Ask before adding any.

## Git

- Never commit or push without the owner's explicit instruction.
- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`...).
- Commit email must be the GitHub noreply address (already set in this repo's local git config; GitHub rejects the private email).
- The `Dashboard` Action commits rebuilt files to `main` on push and daily. Run `git pull --rebase` before starting work.
- CI needs the repo secret `LEETHUB_TOKEN` (fine-grained, Contents read-only on `LEETCODE-PROBLEMS`) for the LeetHub sync; without it the step is skipped.

## Useful commands

```
prep due | next | plan | status        # what to do
prep new lc 217 | sd <name> | ood <name> | concept <name> | note <area> <name>
prep new oa <platform> <name> | star <slug> | mock <platform> [format]
prep start lc 217 ; prep pause ; prep resume ; prep phase ; prep stop
prep log lc 217 20 --outcome solved      # manual entry: ref + minutes
prep find <query> [--text]
prep import --sync [--dry-run]
prep build ; prep check
```

Details: `scripts/README.md`, `07-study-plan/spaced-repetition.md`, `07-study-plan/roadmap.md`.
