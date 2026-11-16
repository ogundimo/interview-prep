# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def hasPathSum(self, root: Optional[TreeNode], targetSum: int) -> bool:
        exists = [False]

        def helper(node, currSum):
            if node.left is None and node.right is None:
                currSum += node.val
                if currSum == targetSum:
                    exists[0] = True
                return
            else:
                currSum += node.val
                if node.left is not None:
                    helper(node.left, currSum)
                if node.right is not None:
                    helper(node.right, currSum)
        if root is None:
            return False 
        helper(root, 0)
        return exists[0]
