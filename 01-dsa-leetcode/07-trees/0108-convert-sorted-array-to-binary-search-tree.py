# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:
        def helper(elements, left, right) -> Optional[TreeNode]:
            if left > right:
                return None
            
            mid = left + (right -left) // 2
            node = TreeNode(elements[mid])
            node.left = helper(elements, left, mid - 1)
            node.right = helper(elements, mid + 1, right)
            return node
        return helper(nums, 0, len(nums) - 1)
