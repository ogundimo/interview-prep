class Solution {
    public String removeStars(String s) {
        Stack stack = new Stack();
        int n = s.length();
        String result = "";

        for(int i = 0; i < n; i++){
            char c = s.charAt(i);
            if (c == '*') {
                stack.pop();
            } else {
                stack.push(c);
            }
        }

        while(!stack.empty()){
            char c = (char) stack.pop();
            result = c + result;
        }

        return result;
    }
}
