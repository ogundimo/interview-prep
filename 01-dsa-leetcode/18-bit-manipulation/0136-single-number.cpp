class Solution {
public:
    int singleNumber(vector<int>& nums) {
        int output = 0;
        for (int x: nums){
            output = x ^ output;
        }
        return output;
    }
};
