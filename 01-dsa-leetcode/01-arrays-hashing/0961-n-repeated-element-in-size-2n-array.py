class Solution:
    def repeatedNTimes(self, nums: List[int]) -> int:
        N = len(nums) // 2
        f = collections.Counter(nums)

        for k,v in f.items():
            if v == N:
                return k
