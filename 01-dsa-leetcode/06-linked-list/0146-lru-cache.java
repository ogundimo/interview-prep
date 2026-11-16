import java.util.*;

class LRUCache {
    private static class Node {
        int key, val;
        Node prev, next;

        Node(int k, int v) {
            key = k;
            val = v;
        }
    }

    private final int cap;
    private final Map<Integer, Node> map = new HashMap<>();
    private final Node head = new Node(0, 0), tail = new Node(0, 0);

    public LRUCache(int capacity) {
        cap = capacity;
        head.next = tail;
        tail.prev = head;
    }

    private void remove(Node n) {
        n.prev.next = n.next;
        n.next.prev = n.prev;
    }

    private void append(Node n) { // most recently used sits right before tail
        n.prev = tail.prev;
        n.next = tail;
        tail.prev.next = n;
        tail.prev = n;
    }

    public int get(int key) {
        Node n = map.get(key);
        if (n == null) return -1;
        remove(n);
        append(n);
        return n.val;
    }

    public void put(int key, int value) {
        Node n = map.get(key);
        if (n != null) {
            n.val = value;
            remove(n);
            append(n);
            return;
        }
        n = new Node(key, value);
        map.put(key, n);
        append(n);
        if (map.size() > cap) {
            Node lru = head.next;
            remove(lru);
            map.remove(lru.key);
        }
    }
}
