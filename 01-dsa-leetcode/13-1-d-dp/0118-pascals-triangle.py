class Solution:
    def generate(self, numRows: int) -> List[List[int]]:
        result = []
        result.append([1])
        
        if numRows >= 2:
            result.append([1,1])
        
        if numRows > 2:
            idx = 2
            while idx < numRows:
                prev = result[idx - 1]
                temp = []
                temp.append(1)
                for i in range(len(prev) - 1):
                    num = prev[i] + prev[i+1]
                    temp.append(num)
                temp.append(1)
                result.append(temp)
                idx += 1
            
        return result 
        
