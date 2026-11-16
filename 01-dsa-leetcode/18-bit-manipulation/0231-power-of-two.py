class Solution:
    def isPowerOfTwo(self, n: int) -> bool:
        if n == 1: 
            return True

        if n%2 != 0 or n < 1:
            return False

        rem = n % 2
        while n > 1 and rem == 0:
            n = n // 2
            rem = n % 2
        
        if rem == 1 and n > 1 :
            return False
        
        return True
