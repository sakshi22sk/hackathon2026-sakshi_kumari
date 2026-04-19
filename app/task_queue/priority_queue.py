import heapq

class PriorityQueue:
    def __init__(self):
        self.queue = []

    def push(self, priority, ticket):
        heapq.heappush(self.queue, (priority, ticket))

    def pop(self):
        return heapq.heappop(self.queue)[1]

    def is_empty(self):
        return len(self.queue) == 0