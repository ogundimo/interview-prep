# Python interview cheat sheet

[Language notes](README.md) · [Java](java.md) · [C++](cpp.md) · [Home](../../README.md)

| Need | Python | Notes |
|---|---|---|
| Dynamic array | `a = []`, `a.append(x)`, `a.pop()` | `pop(0)` is O(n): use `deque` |
| Hash map / set | `d = {}`, `defaultdict(list)`, `Counter(s)`, `set()` | `Counter.most_common(k)` |
| Queue / deque | `from collections import deque`; `q.append`, `q.popleft()` | O(1) at both ends |
| Min-heap | `heapq.heappush(h, x)`, `heapq.heappop(h)`, `heapq.heapify(a)` | Max-heap: push `-x`; tuples compare element-wise |
| Sorted container | `bisect.bisect_left(a, x)`, `insort(a, x)` | No built-in balanced BST |
| Sort | `a.sort(key=lambda x: (x[1], -x[0]))`, `sorted(a, reverse=True)` | Timsort, stable, O(n log n) |
| Memoize | `@functools.cache` | Recursion limit 1000: `sys.setrecursionlimit(10**6)` or go iterative |
| Infinity | `float("inf")`, `math.inf` | Ints are arbitrary precision: no overflow |
| Char math | `ord(c) - ord("a")`, `chr(97 + i)` | |
| 2D grid | `[[0] * cols for _ in range(rows)]` | **Not** `[[0] * cols] * rows` (shared rows) |
| Iteration | `enumerate`, `zip`, `itertools.accumulate`, `pairwise` | `accumulate` gives prefix sums |

## Gotchas

- Mutable default arguments (`def f(a=[])`) are shared between calls.
- `//` floors toward negative infinity: `-7 // 2 == -4`. Use `int(a / b)` to truncate toward zero.
- String concatenation in a loop is O(n^2): build a list and `"".join(parts)`.
- The GIL: threads do not speed up CPU-bound code; use `multiprocessing`.
