class Solution {
public:
    int maxArea(vector<int>& height) {
        int left = 0;
        int right = height.size() - 1;
        int maxarea = -1;

        while( left < right ){
            int length = min(height[left], height[right]);
            int width = right - left;

            maxarea = max(maxarea, ( length * width ));
            
            if(height[left] >= height[right]){
                right --;
            }else{
                left ++;
            }
        }

        return maxarea;
    }
};
