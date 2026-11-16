---
id: mock-2026-11-07-pramp-coding
type: mock
title: Pramp coding mock
date: 2026-11-07
platform: pramp
format: coding
interviewer: peer (Pramp)
result: lean hire
tags: [mock, coding, graphs, communication]
sample: true
---

# Pramp coding mock (2026-11-07)

[Mock log](README.md) · [Home](../README.md)

| Platform | Format | Interviewer | Result |
|---|---|---|---|
| Pramp | 45-min coding | peer | **lean hire** |

## Questions

1. **Shortest path in a binary grid** (BFS, Medium): solved in 28 min after first reaching for DFS. Related: [Number of Islands](../01-dsa-leetcode/11-graphs/0200-number-of-islands.md).
2. Follow-up: return the path, not just its length. Described the parent-pointer approach, no time to code it.

## Scores

| Area | 1 to 4 | Notes |
|---|:---:|---|
| Communication | 3 | Explained the approach before coding; went quiet while debugging |
| Problem solving | 3 | DFS first, then BFS once prompted on "shortest" |
| Coding | 3 | Clean helper for neighbours; off-by-one on the bounds check |
| Testing | 2 | Did not walk through an edge case until asked (start cell blocked) |

## Feedback

- "Say 'shortest path in an unweighted graph means BFS' out loud. You got there, but it took a nudge."
- "Narrate while you debug; silence reads as being stuck."
- "Test the degenerate cases first: blocked start, 1×1 grid."

## Action items

- [ ] Do 5 BFS grid problems from [Graphs](../01-dsa-leetcode/11-graphs/README.md) this week (Rotting Oranges, Walls and Gates, ...)
- [ ] Practise thinking aloud while debugging in the next 2 mocks
- [x] Add an edge-case checklist to the [LeetCode template](../templates/lc.md)
