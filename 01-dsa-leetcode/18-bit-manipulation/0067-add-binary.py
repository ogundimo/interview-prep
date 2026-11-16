class Solution:
    def addBinary(self, a: str, b: str) -> str:
        n_a = len(a) - 1
        n_b = len(b) - 1
        carry = 0
        final = ""

        while n_a >= 0 and n_b >= 0:
            sum = int(a[n_a]) + int(b[n_b]) + carry
            carry, res = self.modulo(sum, 2)
            final = str(res) + final
            n_a -= 1
            n_b -= 1
        
        while n_a >= 0:
            sum = int(a[n_a]) + carry
            carry,res = self.modulo(sum, 2)
            final = str(res) + final
            n_a -= 1
        
        while n_b >= 0:
            sum = int(b[n_b]) + carry
            carry,res = self.modulo(sum, 2)
            final = str(res) + final
            n_b -= 1
        if carry > 0:
            final = str(carry) + final

        return final
        
    def modulo(self, num: int, denom: int) :
        quotient = num // denom
        remainder =  num % denom
        return quotient,remainder


        
