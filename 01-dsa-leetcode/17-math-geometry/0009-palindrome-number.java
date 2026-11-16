class Solution {
    public boolean isPalindrome(int x) {
        if(x < 0)
            return false;
        String num = x + "";
        boolean result = true;
        for(int i = 0; i <= num.length()/2; i++){
            String s1 = num.charAt(i) + "";
            String s2 = num.charAt(num.length() - 1 - i) + ""; 
            int i1 = Integer.parseInt(s1);
            int i2 = Integer.parseInt(s2);

            if(i1 != i2)
            {
                return false;
            }
        }

        return true;
    }
}
