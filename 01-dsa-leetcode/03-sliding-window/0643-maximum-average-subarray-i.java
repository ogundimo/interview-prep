class Solution {
    public double findMaxAverage(int[] nums, int k) {
        double average = Double.NEGATIVE_INFINITY ;
        int pointer = 0;
        double curr_sum = 0;

        for(int i = 0 ; i < nums.length; i++){
            curr_sum += nums[i];
            if(i >= k - 1){
                average = Math.max(average, (curr_sum/k));
                curr_sum -= nums[i-(k-1)];
            }
        }
        
        return average;
    }
}
