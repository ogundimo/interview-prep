class Solution:
    def getRow(self, rowIndex: int) -> List[int]:
        if rowIndex == 0:
            return [1]

        if rowIndex == 1:
            return [1,1]

        currIndex = 1
        row = [1,1]

        while currIndex < rowIndex:
            nextRow = []

            nextRow.append(1)
            for i in range(len(row) - 1):
                num = row[i] + row[i+1]
                nextRow.append(num)
            nextRow.append(1)

            row = nextRow
            currIndex += 1
        
        return row
