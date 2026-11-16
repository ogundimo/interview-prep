class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """
        idx_1 = 0
        idx_2 = 0
        nums = []
        while idx_1 < m and idx_2 < n:
            if nums1[idx_1] <= nums2[idx_2]:
                nums.append(nums1[idx_1])
                idx_1+=1
            else:
                nums.append(nums2[idx_2])
                idx_2+=1
        
        while idx_1 < m:
            nums.append(nums1[idx_1])
            idx_1+=1
        
        while idx_2 < n:
            nums.append(nums2[idx_2])
            idx_2+=1

        i = 0
        while i < len(nums):
            nums1[i] = nums[i]
            i += 1
        
