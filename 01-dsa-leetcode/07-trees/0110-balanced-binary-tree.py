# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isBalanced(self, root: Optional[TreeNode]) -> bool:
        b = [True]
        def helper(node) -> int:
            if node is None:
                return 0
            left = helper(node.left) + 1
            right = helper(node.right) + 1
            diff = abs(right-left)
            print(diff)
            if diff > 1:
                b[0] = False
            return max(left,right)

        if root is None:
            return True
        h = helper(root)
        return b[0]
