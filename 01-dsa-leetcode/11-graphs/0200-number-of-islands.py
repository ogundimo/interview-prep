from typing import List


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        rows, cols = len(grid), len(grid[0])

        def sink(r: int, c: int) -> None:
            grid[r][c] = "0"
            stack = [(r, c)]
            while stack:
                r, c = stack.pop()
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                        grid[nr][nc] = "0"  # mark on push, not on pop
                        stack.append((nr, nc))

        count = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == "1":
                    count += 1
                    sink(r, c)
        return count
