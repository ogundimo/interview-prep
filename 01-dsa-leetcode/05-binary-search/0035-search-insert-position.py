class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        left = 0
        right = len(nums) - 1
        mid = (left + right) // 2
        found = -1
        while left < right:
            mid = ( right + left ) //  2
            if nums[mid] > target:
                right = mid - 1
            elif nums[mid] < target:
                left =  mid + 1
            else:
                found = mid
                break
        
        if found == -1 and left >= right:
            if nums[left] < target:
                found = left + 1
            else:
                found = left
        
        return found




        
