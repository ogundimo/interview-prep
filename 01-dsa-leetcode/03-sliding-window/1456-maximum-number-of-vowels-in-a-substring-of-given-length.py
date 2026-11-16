class Solution:
    def maxVowels(self, s: str, k: int) -> int:
        vowels = ['a', 'e', 'i', 'o', 'u']
        n = len(s)
        maxv = 0
        count = 0

        i = 0
        j = 0

        while j < n:
            if s[j] in vowels:
                count += 1
            if j >= k-1:
                maxv = max( count, maxv)
                if s[i] in vowels:
                    count -= 1
                i+=1
            j+=1

        return maxv
        
