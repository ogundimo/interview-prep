class Solution {
    public int climbStairs(int n) {
        if (n < 2){
            return 1;
        }
        int steps[] = new int[n+1];
        steps[n] = 1;
        steps[n-1] = 1;

        for (int i = n-2; i >= 0; i --)
        {
            steps[i] = steps[i+1] + steps[i+2];
        }
        return steps[0];
    }
}
