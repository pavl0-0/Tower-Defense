import pygame as pg
import random
import json
import os
import constants as c

class MapGenerator:
    def __init__(self, tile_size, rows, cols):
        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols
        
    def get_level_data(self, level_num, difficulty=1):
        if not os.path.exists("levels_data"):
            os.makedirs("levels_data")
            
        filename = f"levels_data/campaign_level_{level_num}.json"
        
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        
        else:
            map_data = self.generate_new_map(difficulty)
            
            with open(filename, 'w') as f:
                json.dump(map_data, f)
            return map_data

    def generate_new_map(self, difficulty=1):
        grid = [[c.GRID_GRASS for _ in range(self.cols)] for _ in range(self.rows)]
        waypoints = []
        
        current_x = 0
        current_y = random.randint(2, self.rows - 3)
        
        waypoints.append(self.get_center(current_x, current_y))
        grid[current_y][current_x] = c.GRID_ROAD

        start_length = 3
        for _ in range(start_length):
            if current_x < self.cols - 1:
                current_x += 1
                grid[current_y][current_x] = c.GRID_ROAD
        
        last_turn_x = current_x

        while current_x < self.cols - 1:
            current_x += 1
            grid[current_y][current_x] = c.GRID_ROAD
            
            if current_x >= self.cols - 2: continue
            if current_x - last_turn_x < 3: continue
            
            if random.random() < 0.3:
                direction = 0
                if current_y < self.rows // 3: 
                    direction = 1 if random.random() < 0.8 else -1
                elif current_y > (self.rows * 2) // 3:
                    direction = -1 if random.random() < 0.8 else 1
                else:
                    direction = random.choice([-1, 1])

                space_available = 0
                if direction == 1: space_available = (self.rows - 2) - current_y
                else: space_available = current_y - 2
                
                if space_available < 3: continue

                max_len = int(space_available * 0.8)
                if max_len < 3: max_len = 3
                
                vert_len = random.randint(3, max_len)

                waypoints.append(self.get_center(current_x, current_y))
                for _ in range(vert_len):
                    current_y += direction
                    grid[current_y][current_x] = c.GRID_ROAD
                waypoints.append(self.get_center(current_x, current_y))
                last_turn_x = current_x

        grid[current_y][current_x] = c.GRID_BASE
        waypoints.append(self.get_center(current_x, current_y))

        map_area = self.rows * self.cols
        targets = [
            (c.GRID_ROCK, int(map_area * 0.015)), 
            (c.GRID_MUSHROOM, int(map_area * 0.015))
        ]

        for item_type, amount in targets:
            for _ in range(amount):
                for attempt in range(20):
                    rx = random.randint(0, self.cols - 1)
                    ry = random.randint(0, self.rows - 1)

                    if grid[ry][rx] != c.GRID_GRASS:
                        continue

                    has_road_neighbor = False
                    
                    for dy in range(-1, 2):  
                        for dx in range(-1, 2):  
                            if dy == 0 and dx == 0: continue

                            ny, nx = ry + dy, rx + dx
                            
                            if 0 <= ny < self.rows and 0 <= nx < self.cols:
                                if grid[ny][nx] == c.GRID_ROAD or grid[ny][nx] == c.GRID_BASE:
                                    has_road_neighbor = True
                                    break 
                        
                        if has_road_neighbor: 
                            break

                    if not has_road_neighbor:
                        grid[ry][rx] = item_type
                        break

        map_json = {
            "tile_map": grid,
            "waypoints": waypoints,
            "width": self.cols,
            "height": self.rows
        }
        return map_json

    def get_center(self, x, y):
        return (x * self.tile_size + self.tile_size // 2, 
                y * self.tile_size + self.tile_size // 2)