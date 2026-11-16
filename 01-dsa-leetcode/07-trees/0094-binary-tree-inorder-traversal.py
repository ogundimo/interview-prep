# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def inorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        result = []
        self.inorder(root,result)
        return result

    def inorder(self, node, lis) -> None:
        if node == None:
            return
        self.inorder(node.left,lis)
        lis.append(node.val)
        self.inorder(node.right,lis)
        
