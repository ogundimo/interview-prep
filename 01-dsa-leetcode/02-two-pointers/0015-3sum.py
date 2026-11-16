class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        seen = []
        triplets = [] 
        nums.sort()

        for index in range(0, len(nums)):
            if nums[index] in seen:
                continue
            if nums[index] > 0:
                break
            seen.append(nums[index])
            low = index + 1 
            high = len(nums) - 1 
            while low < high:
                sum = nums[index] + nums[low] + nums[high]
                if sum == 0:
                    temp = [nums[index],nums[low],nums[high]]
                    triplets.append(temp)
                    
                    low += 1
                    high -= 1

                    while low < high and nums[low] == nums[low-1]:
                        low += 1
                    
                    while low < high and nums[high] == nums[high+1]:
                        high -= 1
                elif sum > 0:
                    high -= 1 
                else:
                    low += 1
        return triplets

        
