# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if head == None:
            return head
        curr = head
        lastSeen = head

        while curr != None:
            if lastSeen.val != curr.val:
                lastSeen.next = curr
                lastSeen = curr
            curr = curr.next

        lastSeen.next = None

        return head
