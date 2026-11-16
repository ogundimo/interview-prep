class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        length = len(nums)           
        i= 0

        while i < length:
            if nums[i] == val:
                del nums[i]
                length = len(nums)
            else:
                i += 1
        
        return length
        
