from collections import Counter


class Solution:
    def minWindow(self, s: str, t: str) -> str:
        need = Counter(t)
        missing = len(t)
        best = (0, float("inf"))
        left = 0
        for right, c in enumerate(s):
            if need[c] > 0:
                missing -= 1
            need[c] -= 1
            while missing == 0:
                if right - left < best[1] - best[0]:
                    best = (left, right)
                need[s[left]] += 1
                if need[s[left]] > 0:
                    missing += 1
                left += 1
        return "" if best[1] == float("inf") else s[best[0]:best[1] + 1]
