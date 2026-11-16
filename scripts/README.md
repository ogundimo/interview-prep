# Scripts: the `prep` CLI

[Home](../README.md) · [Templates](../templates/README.md) · [Data](../data/README.md)

Pure Python 3.12+ with one dependency (PyYAML). Works in PowerShell, cmd and Git Bash.

## Setup (once)

```powershell
cd C:\Users\Ogund\Projects\interview-prep
python -m pip install -e .     # puts `prep` on your PATH
prep --help
```

Without installing, use the wrappers from the repo root: `.\prep <command>` (cmd/PowerShell, runs `prep.cmd`) or `./prep <command>` (Git Bash).

## Commands

| Command | What it does |
|---|---|
| `prep new lc 146 ["LRU Cache"] [--lang java]` | Note + solution file from the template; title, difficulty, pattern folder and tags come from NeetCode 150 or the LeetCode API |
| `prep new sd url-shortener` · `ood` · `concept` · `note <area>` · `oa <platform>` · `star` · `mock` | Same, for the other entry types |
| `prep start lc 146` | Start the timer (`prep start sd url-shortener` for a phased design mock) |
| `prep pause` · `prep resume` · `prep status` · `prep cancel` | Timer control |
| `prep phase` | System design: close the current phase and print its time vs target |
| `prep stop [-o solved -g good -y]` | Stop, ask for outcome and grade (suggested from time vs target), append to `data/attempts.csv`, reschedule, rebuild |
| `prep log lc 146 23 -o hints [--date 2026-11-14]` | Add a time by hand |
| `prep due [--days 7]` | Today's and overdue reviews, with the command to start each one |
| `prep find <tag or name or number> [--text]` | Search across all sections |
| `prep next` · `prep plan` | Today's tasks · the 7-day plan |
| `prep build` | Regenerate frontmatter, indexes, charts, dashboard, plan |
| `prep import [--sync] [--remote]` | Pull solutions from the LeetHub repo and link them to timed attempts |
| `prep master lc 1 [--undo]` | Stop reviewing something you know cold |
| `prep interview add 2027-01-20 "Company" [--type mock]` | Schedule an interview or mock (drives *Next mock* and the taper) |
| `prep check` | Verify every relative link and anchor in the repo |
| `prep samples remove` | Delete the sample entries once you have your own |

## Layout

| File | Role |
|---|---|
| [prep.py](prep.py) | Entry point |
| [prepkit/core.py](prepkit/core.py) | Paths, config, frontmatter I/O, item registry, attempt log |
| [prepkit/srs.py](prepkit/srs.py) | Interval ladder, grades, mastery, legacy spreading |
| [prepkit/metrics.py](prepkit/metrics.py) | Speed stats, weekly trend, weakness score |
| [prepkit/plan.py](prepkit/plan.py) | 7-day plan, new/review mix, interleaving |
| [prepkit/charts.py](prepkit/charts.py) | SVG charts (light and dark mode) |
| [prepkit/build.py](prepkit/build.py) | Dashboard, indexes, entry refresh |
| [prepkit/timer.py](prepkit/timer.py) | Timer and attempt logging |
| [prepkit/entries.py](prepkit/entries.py) | Templates, LeetCode lookup, reference resolution |
| [prepkit/importer.py](prepkit/importer.py) | LeetHub import and sync |
| [prepkit/cli.py](prepkit/cli.py) | Argument parsing |

**CI sync of a private LeetHub repo:** create a fine-grained token with *Contents: read-only* on `LEETCODE-PROBLEMS` and save it as the repository secret `LEETHUB_TOKEN`. Without it, the Action skips the sync and `prep import --sync` works locally.

Set `PREP_TODAY=2026-12-01` to see the dashboard as it will look on another date.
