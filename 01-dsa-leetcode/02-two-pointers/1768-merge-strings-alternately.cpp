class Solution {
public:
    string mergeAlternately(string word1, string word2) {
        int point1 = 0;
        int point2 = 0;
        int n1 = word1.length();
        int n2 = word2.length();
        string result = "";

        while(point1 < n1 && point2 < n2){
            result += word1[point1++];
            result += word2[point2++];
        }

        while(point1 < n1){
            result += word1[point1++];
        }


        while(point2 < n2){
            result += word2[point2++];
        }
        return result;
    }
};
