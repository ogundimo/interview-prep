class Solution:
    def maximum69Number (self, num: int) -> int:
        s = str(num)
        temp = ""
        done = 0
        for i in range(len(s)):
            if s[i] == '6' and done == 0:
                temp += '9'
                done = 1
            else:
                temp += s[i]


        return int(temp)
