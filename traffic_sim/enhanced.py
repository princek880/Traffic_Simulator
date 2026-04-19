import pygame
import random
from traffic_sim import Road, Junction, Vehicle, Source, Sink
from traffic_sim import CentralizedRouting

class VisualRoad(Road):
    def __init__(self, capacity, e1, e2, length):
        super().__init__(capacity, e1, e2)
        self.length = max(1, int(length)) # Capacity/Steps to cross
        self.vehicles_in_transit = [] # List of [vehicle, progress]

    def receive(self, vehicle):
        if len(self.vqueue) + len(self.vehicles_in_transit) < self.capacity:
            self.vehicles_in_transit.append([vehicle, 0])
            return True
        return False

    def step(self):
        # Progress vehicles through the road length
        still_moving = []
        for v_data in self.vehicles_in_transit:
            v_data[1] += 1
            if v_data[1] >= self.length:
                self.vqueue.append(v_data[0])
            else:
                still_moving.append(v_data)
        self.vehicles_in_transit = still_moving

        # Move from queue to next element (Junction/Sink)
        if self.vqueue and self.next_element:
            if self.next_element.receive(self.vqueue[0]):
                self.vqueue.popleft()

class VisualVehicle(Vehicle):
    def __init__(self, destination, color):
        super().__init__(destination)
        self.color = color
        self.current_path = []