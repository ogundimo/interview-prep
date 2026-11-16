class Solution:
    def maxArea(self,height: list[int]) -> int:
        left_idx = 0
        right_idx = len(height) - 1
        currArea = abs(left_idx - right_idx) * min(height[right_idx], height[left_idx])

        while left_idx < right_idx:
            if height[left_idx] <= height[right_idx]:
                left_idx += 1

            elif height[left_idx] > height[right_idx]:
                right_idx -= 1
            
            #recalculate the area
            temp_area = abs(left_idx - right_idx) * min(height[right_idx], height[left_idx])

            if temp_area > currArea:
                currArea = temp_area
        
        return currArea
        
