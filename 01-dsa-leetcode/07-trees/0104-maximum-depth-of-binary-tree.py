# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        def maxDepth(node):
            if not node:
                return 0
            return max(maxDepth(node.left), maxDepth(node.right)) + 1
        
        return maxDepth(root)
