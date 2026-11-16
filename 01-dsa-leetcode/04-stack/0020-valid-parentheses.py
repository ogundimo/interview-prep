class Solution:
    def isValid(self, s: str) -> bool:

        matching_pair = {'{':'}', '[' : ']', '(' : ')'}

        stack_brac =  []

        for i in range(len(s)):
            if s[i] in matching_pair.keys():
                stack_brac.append(s[i])
            else:
                n = len(stack_brac)
                if len(stack_brac) == 0 and s[i] in matching_pair.values():
                    return False
                if matching_pair[stack_brac[n-1]] == s[i]:
                    stack_brac.pop()
                else:
                    return False

        if len(stack_brac) == 0:
            return True
        else:
            return False      

                

        
        
