class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        n = len(prices)
        output = 0
        min_price = float("inf")
        
        for p in prices:
            if p < min_price:
                min_price = p
            elif p >= min_price:
                diff = p - min_price
                output = max(output, diff)
        return output
        
