# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def leafSimilar(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool:
        list1 =  []
        self._leaf_to_list(root1, list1)
        list2 = []
        self._leaf_to_list(root2, list2)

        return list1 == list2
    
    def _leaf_to_list(self, node, result =[]) -> list:
        if node.left is None and node.right is None:
            result.append(node.val)

        if node.left is not None:
            self._leaf_to_list(node.left,result)
            
        if node.right is not None:
            self._leaf_to_list(node.right,result)
        
             
    
