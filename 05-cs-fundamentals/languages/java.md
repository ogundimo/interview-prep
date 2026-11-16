# Java interview cheat sheet

[Language notes](README.md) · [Python](python.md) · [C++](cpp.md) · [Home](../../README.md)

| Need | Java | Notes |
|---|---|---|
| Dynamic array | `List<Integer> a = new ArrayList<>();` `a.add(x)`, `a.get(i)`, `a.remove(a.size() - 1)` | `remove(int)` vs `remove(Object)`: careful with `Integer` |
| Hash map / set | `Map<K, V> m = new HashMap<>();` `m.getOrDefault(k, 0)`, `m.merge(k, 1, Integer::sum)` | `computeIfAbsent(k, x -> new ArrayList<>()).add(v)` |
| Queue / deque | `Deque<Integer> q = new ArrayDeque<>();` `offer`, `poll`, `peek`, `push`, `pop` | Prefer `ArrayDeque` over `Stack` / `LinkedList` |
| Heap | `PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> x[0] - y[0]);` | Max-heap: `Collections.reverseOrder()`; avoid `a - b` when it can overflow, use `Integer.compare` |
| Sorted map / set | `TreeMap`, `TreeSet`: `floorKey`, `ceilingKey`, `headMap` | O(log n) |
| Sort | `Arrays.sort(arr)`, `list.sort(Comparator.comparingInt(x -> x[1]))` | Primitive arrays: dual-pivot quicksort (not stable) |
| Strings | `StringBuilder sb`; `s.charAt(i)`, `s.toCharArray()`, `String.valueOf(chars)` | Compare with `.equals`, never `==` |
| Infinity | `Integer.MAX_VALUE`, `Long.MAX_VALUE` | `MAX_VALUE + 1` overflows to negative |
| 2D grid | `int[][] g = new int[rows][cols];` | Defaults to 0 |

## Gotchas

- `Integer` caching: `==` works for -128..127 only. Use `.equals` or unbox.
- Integer overflow: `mid = lo + (hi - lo) / 2`; use `long` for sums and products.
- `HashMap` iteration order is undefined; use `LinkedHashMap` to keep insertion order.
- Recursion depth around 10k frames by default: go iterative for deep DFS.
