class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        li = s.split()
        n = len(li)
        return len(li[n-1])
        
