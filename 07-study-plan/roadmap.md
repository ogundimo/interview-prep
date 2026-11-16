# Roadmap

[Home](../README.md) · [Study plan](README.md) · [Spaced repetition](spaced-repetition.md) · [Weekly plan](weekly-plan.md)

**Profile:** new-grad SWE, open to backend, infrastructure, frontend and full stack. Python first, Java and C++ as well. 48 h/week. No interview date yet, so the plan aims to keep me **ready at all times**: build coverage fast, then stay sharp.

**Starting point (2026-11-15):** 61 problems solved via LeetHub, mostly Easy. Strong on arrays, two pointers, strings and basic trees/lists; little or no graphs, DP, heaps, backtracking, intervals or tries. System design: one course, no timed practice.

## Weekly hours

| Area | h/week | Typical week |
|---|---:|---|
| DSA: new + review | 22 | 15 to 20 new problems + every due review |
| Online assessments | 4 | 1 timed OA set (CodeSignal GCA / HackerRank) |
| System + OO design | 6 | 1 timed 45-min design + 1 to 2 concept notes |
| CS fundamentals | 6 | 2 to 3 notes with flashcards |
| Behavioral | 3 | write or rehearse 1 to 2 STAR stories |
| Mock interviews | 3 | 1 mock (2 from week 7) |
| Buffer | 4 | catch up on overdue reviews / weak patterns |

Change these in [`data/config.json`](../data/config.json); the weekly plan follows.

## Phase 1 · Foundation (weeks 1 to 6): every pattern, Easy + core Medium

Goal: about 100 of the NeetCode 150, every pattern touched, the time-target habit established.

| Week | DSA patterns (interleaved) | System design | Fundamentals | Behavioral / OA / mocks |
|---|---|---|---|---|
| 1 | [Arrays & Hashing](../01-dsa-leetcode/01-arrays-hashing/README.md) · [Two Pointers](../01-dsa-leetcode/02-two-pointers/README.md) · [Stack](../01-dsa-leetcode/04-stack/README.md) | Caching · load balancing | Language sheets · processes vs threads | List 8 story ideas; **baseline OA** (untimed is fine) |
| 2 | [Sliding Window](../01-dsa-leetcode/03-sliding-window/README.md) · [Binary Search](../01-dsa-leetcode/05-binary-search/README.md) · [Linked List](../01-dsa-leetcode/06-linked-list/README.md) | Consistent hashing · sharding | Virtual memory, paging | Write 2 STAR stories; OA #1 |
| 3 | [Trees](../01-dsa-leetcode/07-trees/README.md) · [Tries](../01-dsa-leetcode/08-tries/README.md) | Replication · CAP | TCP/UDP, HTTP, DNS | Write 2 stories; first mock |
| 4 | [Heap](../01-dsa-leetcode/09-heap-priority-queue/README.md) · [Backtracking](../01-dsa-leetcode/10-backtracking/README.md) · [Intervals](../01-dsa-leetcode/16-intervals/README.md) | Queues · rate limiting · **Q: URL shortener** | TLS, "type a URL" walkthrough | Write 2 stories (6 total); OA; mock |
| 5 | [Graphs](../01-dsa-leetcode/11-graphs/README.md) · [Greedy](../01-dsa-leetcode/15-greedy/README.md) · [Bit Manipulation](../01-dsa-leetcode/18-bit-manipulation/README.md) | CDN · indexes · **Q: rate limiter** | Indexes, transactions, isolation | Rehearse all stories; OA; mock |
| 6 | [Advanced Graphs](../01-dsa-leetcode/12-advanced-graphs/README.md) (Mediums) · [1-D DP](../01-dsa-leetcode/13-1-d-dp/README.md) · [Math & Geometry](../01-dsa-leetcode/17-math-geometry/README.md) | **Q: chat app** | SQL vs NoSQL, replication | 2 more stories (8); OA; mock |

## Phase 2 · Depth (weeks 7 to 12): Hards, design, mocks

Goal: finish the NeetCode 150, hit Medium in 25 minutes reliably, and run 2 mocks a week.

| Week | DSA | System design | Fundamentals | OA / mocks |
|---|---|---|---|---|
| 7 | [2-D DP](../01-dsa-leetcode/14-2-d-dp/README.md) · Hards: 42, 76, 239, 84, 4 | OOD: parking lot · **Q: news feed** | Locks, deadlock, producer-consumer | OA; 2 mocks |
| 8 | 2-D DP (rest) · Hards: 23, 25, 124, 297, 212, 295 | OOD: LRU / elevator · **Q: notifications** | Event loop, async vs threads | OA; 2 mocks |
| 9 | Hards: 51, 127, 332, 778, 269, 329, 115, 312, 10 | **Q: web crawler** | Browser rendering, REST vs GraphQL, CORS | OA; 2 mocks |
| 10 | Grind 169 extras for weak patterns; timed sets of 4 | **Q: key-value store** | Weakest area from the dashboard | OA marathon (2 back to back); 2 mocks |
| 11 | Review-heavy week (50/50); redo every *(slower)* problem | **Q: file storage** | Flashcard sweep | 2 mocks (1 behavioral) |
| 12 | Mixed timed sets; company-tagged lists if a target appears | Redo the weakest design from memory | Flashcard sweep | OA; 2 mocks |

## Phase 3 · Maintenance (week 13 onward)

- About **50% new / 50% review**: company-tagged problems, Grind 169 extras, contest problems.
- 1 timed design and 1 OA every week; 1 to 2 mocks.
- Keep **Overdue at zero**; anything that regresses goes back on the ladder.

## When an interview is booked

```powershell
prep interview add 2027-02-10 "Company X"     # real interview
prep interview add 2027-02-03 "Pramp" --type mock
```

| Days out | What changes |
|---|---|
| 28 | Weekly plan drops to **50% new**; start the company's tagged problems |
| 14 | **30% new / 70% review**: weak patterns and *(slower)* problems; 3 mocks/week incl. 1 behavioral; research the company |
| 3 | No new problems. Light reviews of mastered favourites, rehearse the top 4 stories, sleep |

## Checkpoints

| By the end of | Target |
|---|---|
| Week 2 | Every attempt timed; Easy median at or under 15 min |
| Week 6 | 100 / 150 NeetCode; every pattern attempted; 6+ STAR stories; 3 timed designs |
| Week 9 | 150 / 150; Medium within target 60%+ of the time |
| Week 12 | Medium within target 75%+; no pattern with weakness above 0.45; 10+ mocks logged |
