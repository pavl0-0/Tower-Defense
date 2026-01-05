import pygame as pg
import random
import json
import os

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
            print(f"Завантаження рівня {level_num} з файлу...")
            with open(filename, 'r') as f:
                return json.load(f)
        
        else:
            print(f"Генерація нового рівня {level_num}...")
            map_data = self.generate_new_map(difficulty)
            
            with open(filename, 'w') as f:
                json.dump(map_data, f)
            return map_data

    def generate_new_map(self, difficulty=1):
        grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        waypoints = []
        
        current_x = 0
        current_y = random.randint(2, self.rows - 3)
        
        waypoints.append(self.get_center(current_x, current_y))
        grid[current_y][current_x] = 1

        start_length = 3
        for _ in range(start_length):
            if current_x < self.cols - 1:
                current_x += 1
                grid[current_y][current_x] = 1
        
        last_turn_x = current_x

        while current_x < self.cols - 1:
            current_x += 1
            grid[current_y][current_x] = 1
            
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
                    grid[current_y][current_x] = 1
                waypoints.append(self.get_center(current_x, current_y))
                last_turn_x = current_x

        grid[current_y][current_x] = 5
        waypoints.append(self.get_center(current_x, current_y))

        for y in range(self.rows):
            for x in range(self.cols):
                if grid[y][x] == 0: 
                    is_near_road = False
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            ny, nx = y+dy, x+dx
                            if 0 <= ny < self.rows and 0 <= nx < self.cols:
                                if grid[ny][nx] == 1 or grid[ny][nx] == 5:
                                    is_near_road = True
                                    break
                        if is_near_road: break
                    
                    if not is_near_road:
                        rnd = random.random()
                        if rnd < 0.015: grid[y][x] = 2 
                        elif rnd < 0.030: grid[y][x] = 3

        flat_data = [item for sublist in grid for item in sublist]
        map_json = {
            "layers": [{"data": flat_data}],
            "waypoints": waypoints,
            "width": self.cols,
            "height": self.rows
        }
        return map_json

    def get_center(self, x, y):
        return (x * self.tile_size + self.tile_size // 2, 
                y * self.tile_size + self.tile_size // 2)