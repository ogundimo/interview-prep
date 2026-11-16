class Solution {
    public List<Boolean> kidsWithCandies(int[] candies, int extraCandies) {
        int maximum = 0;
        int n = candies.length;
        ArrayList<Boolean> result =  new ArrayList<Boolean>();

        for(int i = 0; i < n; i++){
            maximum = Math.max(candies[i], maximum);
        }

        for (int i = 0; i < n; i ++){
            int count = candies[i] + extraCandies; 
            if(count >= maximum){
                result.add(true);
            }else{
                result.add(false);
            }
        }

        return result;
        
    }
}
