class Solution:
    def plusOne(self, digits: List[int]) -> List[int]:
        n = len(digits)
        if digits[n - 1] != 9:
            digits[n - 1] += 1
        else:
            idx = n-1 
            while idx >= 0 and digits[idx] == 9:
                digits[idx] = 0
                idx -= 1
            
            if idx == -1:
                digits.insert(0, 1)
            else:
                digits[idx] += 1
        return digits
            
