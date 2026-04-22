import heapq
import math

class CentralizedRouting:
    def __init__(self, coords, edges):
        self.coords = coords
        self.edges = edges
        self.adj = {n: {} for n in coords}
        self.next_hop = {}
        self.dirty = True

    def update_weights(self, weight_map=None):
        self.next_hop.clear()
        for u, v in self.edges:
            if weight_map and (u, v) in weight_map:
                w = weight_map[(u, v)]
            else:
                x1, y1 = self.coords[u]
                x2, y2 = self.coords[v]
                w = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            self.adj[u][v] = self.adj[v][u] = w
        self.dirty = False
        
    

    def _compute_source(self, src):
        distances = {n: float('inf') for n in self.adj}
        predecessors = {n: None for n in self.adj}
        distances[src] = 0
        pq = [(0, src)]

        while pq:
            d, u = heapq.heappop(pq)
            if d > distances[u]: continue
            for v, weight in self.adj[u].items():
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u
                    heapq.heappush(pq, (distances[v], v))
        
       
        self.next_hop[src] = {}
        for target in self.adj:
            if target == src or predecessors[target] is None:
                continue
            
            curr = target
            while predecessors[curr] != src:
                curr = predecessors[curr]
            self.next_hop[src][target] = curr

    def get_next_step(self, current, destination):
        if current == destination:
            return current
        if current not in self.next_hop:
            self._compute_source(current)
        
        return self.next_hop[current].get(destination)

    def get_full_route(self, src, dest):
        path = [src]
        curr = src
        while curr != dest:
            curr = self.get_next_step(curr, dest)
            if curr is None: return [] 
            path.append(curr)
        return path