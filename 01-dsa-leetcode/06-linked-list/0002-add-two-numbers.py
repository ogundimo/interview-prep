# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        head = None
        carry = 0
        node1 = l1
        node2 = l2
        while node1 is not None and node2 is not None:
            total = node1.val + node2.val + carry
            if total >= 10:
                value = total - 10
                carry = 1
                node = ListNode(val = value, next = None)
                head = self.insert(node,head)
            else:
                carry=0
                node = ListNode(val = total, next = None)
                head = self.insert(node,head)
            node1 = node1.next
            node2 = node2.next

        while node1 is not None:
            total = node1.val + carry
            if total >= 10:
                value = total - 10
                carry = 1
                node = ListNode(val = value, next = None)
                head = self.insert(node,head)
            else:
                carry = 0
                node = ListNode(val = total, next = None)
                head = self.insert(node,head)
            node1 = node1.next

        while node2 is not None:
            total = node2.val + carry
            if total >= 10:
                value = total - 10
                carry = 1
                node = ListNode(val = value, next = None)
                head = self.insert(node,head)
            else:
                carry = 0
                node = ListNode(val = total, next = None)
                head = self.insert(node,head)
            node2 = node2.next

        if carry > 0:
            head = self.insert(ListNode(val=carry, next = None),head)
        
        return head

    def insert(self, node, headNode):
        if headNode is None:
            print("head is none")
            print(node.val)
            headNode = node
        else:
            curr = headNode
            while curr.next is not None:
                curr = curr.next
            curr.next = node
        
        return headNode
