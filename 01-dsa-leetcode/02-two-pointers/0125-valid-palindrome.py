class Solution:
    def isPalindrome(self, s: str) -> bool:
        def clean(s) -> str:
            lowered = s.lower().replace(" ", "")
            res = ""
            for c in lowered:
                if c.isalnum():
                    res += c
            return res
        
        news = clean(s)
        l = 0
        r = len(news) - 1
        while l < r:
            if news[l] != news[r]:
                return False
            l+=1
            r-=1
        return True
