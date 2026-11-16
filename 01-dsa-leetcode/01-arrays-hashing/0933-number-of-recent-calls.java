class RecentCounter {
    private Deque<Integer> pings;

    public RecentCounter() {
        this.pings = new ArrayDeque<>();
    }
    
    public int ping(int t) {
        this.pings.addLast(t);
        while (pings.peekFirst() < t - 3000) {
            this.pings.removeFirst();
        }
        return this.pings.size();
    }
}

/**
 * Your RecentCounter object will be instantiated and called as such:
 * RecentCounter obj = new RecentCounter();
 * int param_1 = obj.ping(t);
 */
