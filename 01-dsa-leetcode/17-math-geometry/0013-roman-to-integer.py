class Solution:
    def romanToInt(self, s: str) -> int:
        rom_int_dict ={
            'I' : 1,
            'V' : 5,
            'X' : 10,
            'L' : 50,
            'C' : 100,
            'D' : 500,
            'M' : 1000
        }

        sum = 0
        for idx in range(0,len(s)):
            num = rom_int_dict[s[idx]]
            if (idx + 1) < len(s):
                if s[idx] == 'I' and (s[idx + 1] == 'V' or s[idx + 1] == 'X'):
                    # minus one (I)
                    num *= (-1)
                    pass
                elif s[idx] == 'X' and (s[idx + 1] == 'L' or s[idx + 1] == 'C'):
                    # minus ten (X)
                    num *= (-1)
                    pass 
                elif s[idx] == 'C' and (s[idx + 1] == 'D' or s[idx + 1] == 'M'):
                    # minus hundred (C)
                    num *= (-1)
                    pass 
            sum += num
            
        return sum
