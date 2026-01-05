import pygame as pg
import constants as c

class World():
    def __init__(self, data, map_image, tile_imgs=None):
        self.tile_map = []
        self.waypoints = []
        self.level_data = data
        self.image = map_image
        self.tile_imgs = tile_imgs

    def process_data(self):
        # Обробка даних рівня
        if "waypoints" in self.level_data:
            self.waypoints = self.level_data["waypoints"]
            self.tile_map = self.level_data["layers"][0]["data"]

    def draw(self, surface):
        if self.tile_imgs and self.tile_map:
            # 1. Малюємо фон (траву)
            grass_img = self.tile_imgs[0]
            if isinstance(grass_img, list): grass_img = grass_img[0]
            
            for y in range(c.ROWS):
                for x in range(c.COLS):
                    surface.blit(grass_img, (x * c.TILE_SIZE, y * c.TILE_SIZE))

            # 2. Малюємо дорогу
            road_tiles = self.tile_imgs[1] 
            
            for y in range(c.ROWS):
                for x in range(c.COLS):
                    tile_id = self.tile_map[y * c.COLS + x]
                    pos = (x * c.TILE_SIZE, y * c.TILE_SIZE)
                    
                    if tile_id == 1 or tile_id == 5:
                        # Функція перевірки сусідів
                        def is_road(nx, ny):
                            if 0 <= nx < c.COLS and 0 <= ny < c.ROWS:
                                nid = self.tile_map[ny * c.COLS + nx]
                                return nid == 1 or nid == 5
                            return False

                        top = is_road(x, y - 1)
                        bot = is_road(x, y + 1)
                        left = is_road(x - 1, y)
                        right = is_road(x + 1, y)
                        
                        idx = 4 # Центр (якщо нічого не підійшло - просто квадрат землі)

                        # --- 1. СПОЧАТКУ ПЕРЕВІРЯЄМО ПОВОРОТИ (Пріоритет!) ---
                        if right and bot: idx = 0   # Поворот Вниз-Вправо 
                        elif left and bot: idx = 2  # Поворот Вниз-Вліво
                        elif right and top: idx = 6 # Поворот Вверх-Вправо
                        elif left and top: idx = 8  # Поворот Вверх-Вліво
                        
                        # --- 2. ПОТІМ ПРЯМІ ЛІНІЇ ---
                        elif left and right: idx = 1 # Горизонталь (верхній бордюр)
                        elif top and bot: idx = 3    # Вертикаль (лівий бордюр)

                        # --- 3. ПОТІМ ТУПИКИ (Кінці дороги) ---
                        # Тут ми підбираємо ті шматки, які візуально продовжують лінію
                        elif bot: idx = 3   # Початок зверху (малюємо як вертикаль)
                        elif top: idx = 3   # Кінець знизу (малюємо як вертикаль)
                        elif right: idx = 1 # Початок зліва (малюємо як горизонталь)
                        elif left: idx = 1  # Кінець справа (малюємо як горизонталь)
                        
                        # Безпечне малювання
                        if isinstance(road_tiles, list) and idx < len(road_tiles):
                            surface.blit(road_tiles[idx], pos)
                        else:
                            surface.blit(road_tiles, pos)
                        
                        # Замок
                        if tile_id == 5 and len(self.tile_imgs) > 5:
                             castle_img = self.tile_imgs[5]
                             if castle_img:
                                 offset_x = (c.TILE_SIZE - castle_img.get_width()) // 2
                                 offset_y = (c.TILE_SIZE - castle_img.get_height()) // 2
                                 surface.blit(castle_img, (pos[0] + offset_x, pos[1] + offset_y))

                    # Декорації
                    elif tile_id == 2:
                        surface.blit(self.tile_imgs[2], pos)
                    elif tile_id == 3:
                        surface.blit(self.tile_imgs[3], pos)
                    elif tile_id == 4 and len(self.tile_imgs) > 4:
                         surface.blit(self.tile_imgs[4], pos)
        else:
            if self.image:
                surface.blit(self.image, (0, 0))