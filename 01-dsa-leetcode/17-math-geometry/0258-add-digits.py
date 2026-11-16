class Solution:
    def addDigits(self, num: int) -> int:
        s = str(num)
        length = len(s)

        if length <= 1:
            return num
        
        while length > 1:
            sum = 0
            for i in range(len(s)):
                sum += int(s[i])
            s = str(sum)
            length = len(s)
        
        return int(s)
        
