# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def minDepth(self, root: Optional[TreeNode]) -> int:
        def helper(node):
            if node is None:
                return 0
            if node.left is None and node.right is None:
                return 1
            
            left = helper(node.left) + 1
            right = helper(node.right) + 1
            
            if node.left is None:
                return right
            if node.right is None: 
                return left

            return min(left,right)
        
        return helper(root)
