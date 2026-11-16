class Solution:
    def mySqrt(self, x: int) -> int:
        result = 0
        if x == 1:
            result = 1
        
        left,right = 1,x

        while left <= right:
            mid = (left + right) // 2
            sq = mid * mid
            if sq == x:
                result = mid
                break
            elif sq < x:
                left = mid + 1
                result = mid
            elif sq > x:
                right = mid - 1
        
        return result
