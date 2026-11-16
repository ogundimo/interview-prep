class Solution:
    def isPowerOfFour(self, n: int) -> bool:
        rem = n % 4

        if n == 1:
            return True

        if rem != 0 or n <= 0:
            return False

        while n > 1 and rem == 0:
            n = n // 4
            rem = n % 4

        if rem != 0 and n > 1:
            return False

        return True 
