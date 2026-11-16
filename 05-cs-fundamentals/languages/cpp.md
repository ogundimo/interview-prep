# C++ interview cheat sheet

[Language notes](README.md) · [Python](python.md) · [Java](java.md) · [Home](../../README.md)

| Need | C++ (STL) | Notes |
|---|---|---|
| Dynamic array | `vector<int> a; a.push_back(x); a.pop_back();` | `a.reserve(n)` avoids reallocations |
| Hash map / set | `unordered_map<int,int> m; m[k]++;` `m.count(k)`, `m.find(k) != m.end()` | `m[k]` **inserts** a default if missing |
| Queue / deque | `queue<int>`, `deque<int>`: `push_back`, `pop_front`, `front` | |
| Heap | `priority_queue<int> pq;` (max-heap) / `priority_queue<int, vector<int>, greater<int>>` (min) | Custom: lambda comparator plus `decltype` |
| Sorted map / set | `map`, `set`, `multiset`: `lower_bound`, `upper_bound`, `prev(it)` | O(log n); `multiset::erase(value)` removes **all** copies, so erase an iterator |
| Sort | `sort(a.begin(), a.end(), [](auto& x, auto& y){ return x[1] < y[1]; });` | Comparator must be a strict weak ordering (`<`, not `<=`) |
| Binary search | `lower_bound(a.begin(), a.end(), x) - a.begin()` | First index with value >= x |
| Strings | `string s; s += c; s.substr(pos, len); to_string(n); stoi(s)` | `substr` takes a **length**, not an end index |
| Infinity | `INT_MAX`, `LLONG_MAX`, `1e9` | Use `long long` for sums |
| 2D grid | `vector<vector<int>> g(rows, vector<int>(cols, 0));` | |
| Linked list with O(1) move | `list<T>` + `splice` | See LRU Cache in [Linked List](../../01-dsa-leetcode/06-linked-list/README.md) |

## Gotchas

- `size()` is unsigned: `a.size() - 1` underflows when the vector is empty. Cast with `(int)a.size()`.
- Pass big containers by reference (`const vector<int>&`) or every call copies them.
- Iterators are invalidated by `vector` reallocation and by erasing from `unordered_map` while iterating (use `it = m.erase(it)`).
- Local arrays are uninitialized: `int cnt[26] = {};` zero-fills.
