from collections import Counter
from typing import List


class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        buckets = [[] for _ in range(len(nums) + 1)]
        for num, freq in Counter(nums).items():
            buckets[freq].append(num)
        out = []
        for freq in range(len(buckets) - 1, 0, -1):
            for num in buckets[freq]:
                out.append(num)
                if len(out) == k:
                    return out
        return out
