import random
from collections import deque

class Road:
    def __init__(self, capacity, e1, e2, length):
        self.capacity = capacity
        self.e1 = e1
        self.e2 = e2
        self.length = max(1, int(length))
        self.veh_on_road = []
        self.vqueue = deque()
        self.next_element = None

    def receive(self, vehicle):
        if len(self.vqueue) + len(self.veh_on_road) < self.capacity:
            self.veh_on_road.append([vehicle, 0])
            return True
        return False

    def step(self):
        still_moving = []
        for v_data in self.veh_on_road:
            v_data[1] += 1
            if v_data[1] >= self.length:
                self.vqueue.append(v_data[0])
            else:
                still_moving.append(v_data)
        self.veh_on_road = still_moving

        if self.vqueue and self.next_element:
            if self.next_element.receive(self.vqueue[0]):
                self.vqueue.popleft()


class Junction:
    def __init__(self, coords, node_id=None, router=None):
        self.coords = coords
        self.out_roads = {}
        self.node_id = node_id
        self.router = router
        self.process_interval = 30
        self.cooldown = 0

    def step(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def receive(self, vehicle):
        if self.cooldown > 0:
            return False
            
        if self.router is None or self.node_id is None:
            return False
            
        next_hop = self.router.get_next_step(self.node_id, vehicle.dest)
        
        if next_hop is None:
            return False
            
        target_road = self.out_roads.get(next_hop)
        if target_road:
            success = target_road.receive(vehicle)
            if success:
                self.cooldown = self.process_interval
            return success
        return False

class Vehicle:
    def __init__(self, dest, color):
        self.dest = dest
        self.color = color
        self.current_path = []


class Source:
    def __init__(self, rate, sink_list, coords, color_map=None):
        self.rate = rate
        self.sink_list = sink_list
        self.coords = coords
        self.next_element = None
        self.spawn_timer = 0
        self.interval = max(1, 60 // rate) if rate > 0 else float('inf')
        self.color_map = color_map 

    def step(self):
        if not self.next_element or self.rate <= 0: 
            return
            
        self.spawn_timer += 1
        if self.spawn_timer >= self.interval:
            dest = random.choice(self.sink_list)
            color = self.color_map.get(dest, (100, 100, 100)) if self.color_map else (100, 100, 100)
            new_veh = Vehicle(dest, color)
            self.next_element.receive(new_veh)
            self.spawn_timer = 0

class Sink:
    def __init__(self, coords):
        self.received_count = 0
        self.coords = coords

    def receive(self, vehicle):
        self.received_count += 1
        del vehicle
        return True