/** 
 * Forward declaration of guess API.
 * @param  num   your guess
 * @return 	     -1 if num is higher than the picked number
 *			      1 if num is lower than the picked number
 *               otherwise return 0
 * int guess(int num);
 */

class Solution {
public:
    int guessNumber(int n) {
        long long left = 1;
        long long right = n;
        long long num = -1;
        bool found = false;

        while(left <= right && !found){
            long long mid = (left + right)/2;
            cout << mid << endl;
            int result = guess(mid);

            if(result == 0){
                num = mid;
                found = true;
            }else if(result <= 0){
                right = mid - 1;
            }else{
                left = mid + 1;
            }
        }

        return num;
        
    }
};
