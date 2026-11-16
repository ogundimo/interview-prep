class Solution {
    public int largestAltitude(int[] gain) {
        int[] trip = new int[gain.length + 1];
        trip[0] = 0;
        int currMax = 0;

        for(int i = 1; i < gain.length + 1; i++){
            trip[i] = trip[i - 1] + gain[i - 1];
            currMax = Math.max(currMax, trip[i]);
        }

        return currMax;

    }
}
