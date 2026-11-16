class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        if len(haystack) < len(needle):
            return -1
        idx = 0
        found = -1
        for i in range(0,len(haystack)):
            temp = i
            # print(temp,idx)
            while idx < len(needle) and temp < len(haystack):
                if haystack[temp] == needle[idx]:
                    if idx == 0:
                        found = temp
                    # print(temp,idx,found)
                    idx += 1
                    temp += 1
                else:
                    found = -1
                    idx = 0
                    break
            if idx != len(needle):
                found = -1
                
            if found != -1:
                break
        
        return found
        
