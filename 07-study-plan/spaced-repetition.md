# Spaced repetition

[Home](../README.md) · [Study plan](README.md) · [Roadmap](roadmap.md) · [Weekly plan](weekly-plan.md)

Solving a problem once proves very little. Being able to solve it again, **cold and on time**, a month later is what counts in an interview. This repo schedules every item for review on a fixed interval ladder, and a script does all the bookkeeping.

## The method

### Interval ladder

| Step | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Next review after | 1 day | 3 days | 7 days | 14 days | 30 days | 60 days |

- A **first attempt** puts the item on step 1 (review tomorrow). If the first attempt is graded *Easy* it starts on step 2.
- Every **review** is graded, and the grade moves the item along the ladder:

| Grade | When to use it | Effect |
|---|---|---|
| **Again** | Failed, or could not start without the answer | Back to step 1 (1 day) |
| **Hard** | Solved with hints, or solved but over the target time | Repeat the same interval |
| **Good** | Solved alone within target | Move forward 1 step |
| **Easy** | Solved in under half the target, no hesitation | Move forward 2 steps |

`prep stop` suggests a grade from your outcome and time (failed → Again, hints → Hard, over target → Hard, more than 25% slower than your best → Hard, under half the target → Easy, otherwise Good). Press Enter to accept it, or type a different one.

### Mastery

An item is **mastered** after **2 reviews in a row solved within the target time**. A mastered item drops to a maintenance review every 60 days. `prep master <id>` skips the wait for things you know cold, such as old Easies.

### Regressions

A review is flagged as a **regression** when its outcome is worse than an earlier attempt, or when it is more than 25% slower than your best time *and* over target. Regressions:

- show as *(slower)* in the entry's attempts table,
- usually earn a *Hard* or *Again* grade, which shortens the interval,
- raise the pattern's **weakness score**, which pulls more new problems and extra reviews into that pattern in the [weekly plan](weekly-plan.md).

So a topic that felt easy the first time but slipped on review gets more attention automatically.

## What gets reviewed

| Item | Review means | Target |
|---|---|---|
| LeetCode problem | Re-solve from a blank file, timed | Easy 15 · Medium 25 · Hard 40 min |
| System design question | Redraw it from memory with the note closed: requirements, numbers, API, diagram, 2 deep dives. Then compare | 45 min (phases logged) |
| Concept note (system design or CS fundamentals) | Answer every flashcard out loud before opening it | 10 min |
| STAR story | Tell it out loud without notes | 3 min |
| OA, mock interview | Not reviewed: these are logs. Their mistakes become action items and new problems | n/a |

## Daily routine

1. `prep due` or open the dashboard: **Overdue first**, then **Due today**.
2. `prep start lc 146` → solve → `prep stop` → accept or change the grade.
3. Then the new problems from `prep next`.

Reminders: the root README shows *Due today* and *Overdue*, and a GitHub issue titled **Reviews due** is opened or updated every morning and closed once nothing is due.

## Imported history

The 61 problems imported from LeetHub have a solve date but no time. They are tagged `legacy` and are **spread at 3 per day** across the queue (NeetCode 150 problems first, then Hard → Medium → Easy) so day 1 is not a wall of reviews. Their first timed review puts them on the normal ladder.

## Why a fixed ladder and not SM-2 or FSRS

| Algorithm | Good at | Why not here |
|---|---|---|
| SM-2 (classic Anki) | Simple, per-card ease factor | Ease factors drift and hide what happened; a fixed ladder is easier to read in a repo |
| FSRS (modern Anki) | Best recall prediction | Needs hundreds of reviews per user to fit its parameters; a few hundred problems is too little data |
| **Fixed ladder + 4 grades + time-based mastery** | Transparent, explainable, computed from a CSV in a few lines | Less precise, but the time-vs-target signal makes up for most of that |

All state is **recomputed from [`data/attempts.csv`](../data/attempts.csv)** on every build. Change the intervals or the mastery rule in [`data/config.json`](../data/config.json) and the whole schedule updates.

## Mixing new work and reviews

- **Starts at 70% new / 30% review**, and shifts toward review when the backlog grows, when regressions pile up, and as a booked interview gets close (50/50 at 4 weeks, 30/70 at 2 weeks).
- **Interleave** patterns: never two problems from the same pattern back to back. Mixed practice is harder in the moment, but it trains the skill interviews actually test: *recognizing* which pattern applies.
- Details: [weekly-plan.md](weekly-plan.md#how-the-mix-is-chosen).
