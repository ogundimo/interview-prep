class Solution:
    def asteroidCollision(self, asteroids: List[int]) -> List[int]:
        stack = []
        n = len(asteroids)
        rocks = len(asteroids)
        i = 0

        while i < rocks:
            x = asteroids[i]
            if len(stack) == 0:
                stack.append(x)
            else:
                top = stack.pop()
                if (top > 0 and x > 0) or (top < 0 and x < 0) or (top < 0 and x > 0):
                    stack.append(top)
                    stack.append(x)
                else:
                    if(top > 0 and x < 0):
                        if(top > abs(x)):
                            stack.append(top)
                            pass
                        elif(top < abs(x)):
                            i -= 1
                            pass
                        else:
                            #they are equal
                            pass
                        pass
            i += 1
        
        return stack
