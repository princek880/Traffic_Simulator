import pygame
import random
import sys
import math
from traffic_sim import Road, Vehicle, Junction, Source, Sink
from traffic_sim import CentralizedRouting


class GUIBuilder:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        
        self.nodes = {}      
        self.node_types = {} 
        self.node_rates = {} 
        self.roads_data = [] 
        
        self.simulating = False
        self.mode = "NODE" 
        self.selected_node = None
        
        self.current_capacity = 10
        self.current_rate = 2

        self.elements = {}
        self.roads = []
        self.sources = []
        self.sinks = []
        self.dest_colors = {}
        self.router = None

    def get_offset_points(self, p1, p2, offset):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length == 0: 
            return p1, p2
        
        nx = -dy / length
        ny = dx / length
        
        op1 = (p1[0] + nx * offset, p1[1] + ny * offset)
        op2 = (p2[0] + nx * offset, p2[1] + ny * offset)
        return op1, op2

    def draw_triangle(self, surface, color, pos, size):
        points = [
            (pos[0], pos[1] - size),
            (pos[0] - size, pos[1] + size * 0.75),
            (pos[0] + size, pos[1] + size * 0.75)
        ]
        pygame.draw.polygon(surface, color, points)

    def draw_square(self, surface, color, pos, size):
        rect = pygame.Rect(pos[0] - size, pos[1] - size, size * 2, size * 2)
        pygame.draw.rect(surface, color, rect)

    def get_clicked_node(self, pos):
        for nid, npos in self.nodes.items():
            if math.hypot(pos[0]-npos[0], pos[1]-npos[1]) < 15:
                return nid
        return None

    def run(self):
        running = True
        while running:
            self.screen.fill((240, 240, 240))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if not self.simulating:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:
                            self.init_simulation()
                            self.simulating = True
                        elif event.key == pygame.K_SPACE:
                            self.mode = "ROAD" if self.mode == "NODE" else "NODE"
                            self.selected_node = None
                        elif event.key == pygame.K_UP:
                            self.current_rate += 1
                        elif event.key == pygame.K_DOWN:
                            self.current_rate = max(1, self.current_rate - 1)
                        elif event.key == pygame.K_RIGHT:
                            self.current_capacity += 1
                        elif event.key == pygame.K_LEFT:
                            self.current_capacity = max(1, self.current_capacity - 1)

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        clicked = self.get_clicked_node(pos)
                        
                        if event.button == 1: 
                            if self.mode == "NODE":
                                if clicked is None:
                                    nid = len(self.nodes)
                                    self.nodes[nid] = pos
                                    self.node_types[nid] = "Junction"
                                    self.node_rates[nid] = self.current_rate
                            elif self.mode == "ROAD":
                                if clicked is not None:
                                    if self.selected_node is None:
                                        self.selected_node = clicked
                                    else:
                                        if self.selected_node != clicked:
                                            self.roads_data.append((self.selected_node, clicked, self.current_capacity))
                                            self.roads_data.append((clicked, self.selected_node, self.current_capacity))
                                        self.selected_node = None
                        
                        if event.button == 3 and clicked is not None: 
                            types = ["Source", "Junction", "Sink"]
                            curr = self.node_types[clicked]
                            self.node_types[clicked] = types[(types.index(curr)+1)%3]
                            if self.node_types[clicked] == "Source":
                                self.node_rates[clicked] = self.current_rate

            if self.simulating:
                self.update_sim()
                self.draw_sim()
            else:
                self.draw_builder()

            pygame.display.flip()
            self.clock.tick(60)

    def init_simulation(self):
        self.router = CentralizedRouting(self.nodes, [(u, v) for u, v, _ in self.roads_data])
        self.router.update_weights()

        for nid, ntype in self.node_types.items():
            if ntype == "Sink":
                self.elements[nid] = Sink(self.nodes[nid])
                self.sinks.append(nid)
                self.dest_colors[nid] = (random.randint(50,200), random.randint(50,200), random.randint(50,200))

        for nid, ntype in self.node_types.items():
            if ntype == "Source":
                obj = Source(rate=self.node_rates[nid], sink_list=self.sinks, coords=self.nodes[nid], color_map=self.dest_colors)
                self.elements[nid] = obj
                self.sources.append(obj)
            elif ntype == "Junction":
                self.elements[nid] = Junction(self.nodes[nid], node_id=nid, router=self.router)

        for s in self.sources:
            s.sink_list = self.sinks

        for u, v, cap in self.roads_data:
            dist = math.hypot(self.nodes[u][0]-self.nodes[v][0], self.nodes[u][1]-self.nodes[v][1])
            road = Road(capacity=cap, e1=u, e2=v, length=max(1, dist/5))
            road.next_element = self.elements[v]
            self.roads.append(road)
            
            if isinstance(self.elements[u], Junction):
                self.elements[u].out_roads[v] = road 
            elif isinstance(self.elements[u], Source):
                self.elements[u].next_element = road 

    def update_sim(self):
        for s in self.sources:
            s.step() 
        for r in self.roads:
            r.step() 
        for eid, elem in self.elements.items():
            if isinstance(elem, Junction):
                elem.step()

    def draw_builder(self):
        hud_text = [
            f"Mode (SPACE): {self.mode}",
            f"Spawn Rate (UP/DOWN): {self.current_rate}",
            f"Road Capacity (LEFT/RIGHT): {self.current_capacity}",
            "Left Click: Place Node / Select Node (ROAD Mode)",
            "Right Click on Node: Change Type",
            "S: Start Simulation"
        ]
        for i, text in enumerate(hud_text):
            label = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(label, (10, 10 + (i * 20)))

        for u, v, cap in self.roads_data:
            p1, p2 = self.get_offset_points(self.nodes[u], self.nodes[v], 6)
            pygame.draw.line(self.screen, (180, 180, 180), p1, p2, 2)
            mid_x = (p1[0] + p2[0]) / 2
            mid_y = (p1[1] + p2[1]) / 2
            cap_label = self.font.render(f"C:{cap}", True, (100, 100, 100))
            self.screen.blit(cap_label, (mid_x, mid_y))

        for nid, pos in self.nodes.items():
            type_str = self.node_types[nid]
            
            if self.mode == "ROAD" and self.selected_node == nid:
                pygame.draw.circle(self.screen, (231, 76, 60), pos, 18, 2)

            if type_str == "Source":
                self.draw_triangle(self.screen, (52, 152, 219), pos, 12)
            elif type_str == "Sink":
                self.draw_square(self.screen, (46, 204, 113), pos, 10)
            else:
                pygame.draw.circle(self.screen, (100, 100, 100), pos, 12)
            
            rate_str = f" (R:{self.node_rates.get(nid, 0)})" if type_str == "Source" else ""
            label = self.font.render(f"{nid}:{type_str}{rate_str}", True, (0, 0, 0))
            self.screen.blit(label, (pos[0]+15, pos[1]-10))

    def draw_sim(self):
        for r in self.roads:
            p1, p2 = self.get_offset_points(self.nodes[r.e1], self.nodes[r.e2], 6)
            pygame.draw.line(self.screen, (200, 200, 200), p1, p2, 8)
            
            # Draw moving vehicles
            for v, progress in r.veh_on_road:
                ratio = progress / r.length
                x = p1[0] + (p2[0]-p1[0])*ratio
                y = p1[1] + (p2[1]-p1[1])*ratio
                pygame.draw.circle(self.screen, v.color, (int(x), int(y)), 5)
            
            for i, v in enumerate(r.vqueue):
                offset_distance = 10 + (i * 10)
                dx = p1[0] - p2[0]
                dy = p1[1] - p2[1]
                dist = math.hypot(dx, dy)
                if dist > 0:
                    nx, ny = dx/dist, dy/dist
                    x = p2[0] + nx * offset_distance
                    y = p2[1] + ny * offset_distance
                    pygame.draw.circle(self.screen, v.color, (int(x), int(y)), 5)
                    pygame.draw.circle(self.screen, (0, 0, 0), (int(x), int(y)), 5, 1) 

                
        for nid, pos in self.nodes.items():
            type_str = self.node_types[nid]
            
            if type_str == "Source":
                self.draw_triangle(self.screen, (52, 152, 219), pos, 12)
            elif type_str == "Sink":
                color = self.dest_colors.get(nid, (46, 204, 113))
                self.draw_square(self.screen, color, pos, 12)
            else:
                pygame.draw.circle(self.screen, (60, 60, 60), pos, 10)

if __name__ == "__main__":
    builder = GUIBuilder()
    builder.run()