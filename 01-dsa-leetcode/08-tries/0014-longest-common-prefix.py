class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if len(strs) == 0:
            return ""
        elif len(strs) == 1:
            return strs[0]
        
        base_str = strs[0]
        result = ""
        done = False
        idx = 0
        while not done:
            for i in range(1,len(strs)):
                if (idx >= len(strs[i])) or (idx >= len(base_str)):
                    done = True
                    break
                if strs[i][idx] != base_str[idx]:
                    done = True
                    break
            if not done:
                result+=base_str[idx]
                idx+=1
        return result
        
