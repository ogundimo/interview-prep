# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def preorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        def pre(node, vals):
            if not node:
                return 
            vals.append(node.val)
            pre(node.left, vals)
            pre(node.right, vals)
        
        vals = []
        pre(root, vals)
        return vals
        
