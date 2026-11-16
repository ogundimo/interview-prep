class Solution:
    def isPowerOfThree(self, n: int) -> bool:

        rem = n % 3
        if n == 1:
            return True 
        
        if rem != 0 or n <= 0:
            return False

        while  n > 1 and rem == 0:
            n = n // 3
            rem = n % 3
        
        if rem != 0 and n > 1:
            return False
        
        return True
        
