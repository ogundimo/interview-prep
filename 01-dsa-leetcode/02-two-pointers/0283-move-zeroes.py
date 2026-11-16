class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        lastZero = 0
        nextInt = 0
        n = len(nums)

        while nextInt < n:
            if nums[lastZero] == 0 and nums[nextInt] != 0:
                nums[lastZero] = nums[nextInt]
                nums[nextInt] = 0
                lastZero += 1
            else:
                if (nums[lastZero] != 0):
                    lastZero+=1
                
                
            nextInt += 1

        
