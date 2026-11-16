/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */
class Solution {
public:
    ListNode *getIntersectionNode(ListNode *headA, ListNode *headB) {
        ListNode* pointa = headA;
        ListNode* pointb = headB;

        if( pointa == nullptr || pointb == nullptr){
            return nullptr;
        }

        while(pointa != pointb){
        
            if(pointa == nullptr){
                pointa = headB;
            }else{
                pointa = pointa -> next;
            }

            if(pointb == nullptr){
                pointb = headA;
            }else{
                pointb = pointb -> next;
            }
        }

        return pointa;
    }
};
