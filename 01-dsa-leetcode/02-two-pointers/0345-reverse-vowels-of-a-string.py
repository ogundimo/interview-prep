class Solution:
    def reverseVowels(self, s: str) -> str:
        vowels = ['A','E','I','O','U', 'a','i','e','o','u' ]
        found = []
        result = ""
        n = len(s)
        for i in range(n-1,-1,-1):
            if s[i] in vowels:
                found.append(s[i])
        
        idx = 0
        for i in range(n):
            if s[i] in vowels:
                result += found[idx]
                idx += 1
            else:
                result += s[i]
        

        return result
        
