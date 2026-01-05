import pygame as pg
import constants as c

class UIManager:
    def __init__(self, gui_sheet, turret_images, speed_imgs, system_pause_img):
        self.font = pg.font.SysFont("Arial", 16, bold=True)
        self.font_price = pg.font.SysFont("Arial", 12, bold=True)
        self.font_tiny = pg.font.SysFont("Arial", 11, bold=True)
        
        self.turret_images = turret_images
        self.speed_imgs = speed_imgs
        self.system_pause_img = system_pause_img
        
        self.heart_images = []
        if gui_sheet:
            for i in range(4):
                rect = pg.Rect(16 + (i*16), 16, 16, 16)
                try:
                    img = gui_sheet.subsurface(rect)
                except ValueError:
                    img = pg.Surface((16,16)); img.fill("red")
                self.heart_images.append(pg.transform.scale(img, (28, 28)))
            
            try:
                self.orb_full = gui_sheet.subsurface(pg.Rect(96, 16, 16, 16))
                self.orb_empty = gui_sheet.subsurface(pg.Rect(144, 16, 16, 16))
            except ValueError:
                self.orb_full = pg.Surface((16,16)); self.orb_full.fill("orange")
                self.orb_empty = pg.Surface((16,16)); self.orb_empty.fill("grey")
        else:
            self.heart_images = [pg.Surface((28,28)) for _ in range(4)]
            self.orb_full = pg.Surface((16,16))
            self.orb_empty = pg.Surface((16,16))

        self.shop_rects = {}
        self.speed_rects = {}
        
        btn_size = 40
        padding = 10
        total_screen_width = c.SCREEN_WIDTH + c.SIDE_PANEL
        self.sys_pause_rect = pg.Rect(total_screen_width - btn_size - padding, padding, btn_size, btn_size)

    def draw(self, screen, game_data):
        pg.draw.rect(screen, (40, 40, 40), (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
        
        self.draw_wave(screen, game_data["wave"])
        self.draw_stats(screen, game_data["lives"], game_data["money"])
        
        self.draw_speed_controls(screen, game_data["game_speed"])
        self.draw_shop(screen, game_data["money"], game_data["selected_turret"])
        self.draw_charges(screen, game_data["charges"])
        
        self.draw_system_pause(screen)
    
    def draw_system_pause(self, screen):
        if self.system_pause_img:
            scaled_img = pg.transform.scale(self.system_pause_img, (self.sys_pause_rect.width, self.sys_pause_rect.height))
            screen.blit(scaled_img, self.sys_pause_rect)
            
            if self.sys_pause_rect.collidepoint(pg.mouse.get_pos()):
                pg.draw.rect(screen, (255, 255, 255), self.sys_pause_rect, 2, border_radius=5)
    
    def check_system_pause_click(self, mouse_pos):
        if self.sys_pause_rect.collidepoint(mouse_pos):
            return True
        return False

    def draw_wave(self, screen, wave):
        pg.draw.rect(screen, (50, 50, 50), (10, 10, 100, 40), border_radius=10)
        pg.draw.rect(screen, "white", (10, 10, 100, 40), 2, border_radius=10)
        
        txt = self.font.render(f"Wave: {wave}", True, "cyan")
        txt_rect = txt.get_rect(center=(60, 30))
        screen.blit(txt, txt_rect)

    def draw_stats(self, screen, lives, money):
        panel_x = c.SCREEN_WIDTH
        panel_center = panel_x + (c.SIDE_PANEL // 2)
        
        # 1. Серця
        pg.draw.rect(screen, (60, 60, 60), (panel_x + 10, 10, 180, 50), border_radius=8)
        pg.draw.rect(screen, "white", (panel_x + 10, 10, 180, 50), 2, border_radius=8)
        
        total_hearts = 5
        hp_per_heart = 3
        start_heart_x = panel_x + 22 
        
        for i in range(total_hearts):
            heart_hp = lives - (i * hp_per_heart)
            if heart_hp >= 3:   idx = 0
            elif heart_hp >= 2: idx = 1
            elif heart_hp >= 1: idx = 2
            else:               idx = 3
            screen.blit(self.heart_images[idx], (start_heart_x + (i * 32), 21))

        # 2. Гроші
        pg.draw.rect(screen, (60, 60, 60), (panel_x + 10, 70, 180, 40), border_radius=8)
        pg.draw.rect(screen, "white", (panel_x + 10, 70, 180, 40), 2, border_radius=8)
        
        pg.draw.circle(screen, "gold", (panel_x + 35, 90), 12)
        pg.draw.circle(screen, (200, 150, 0), (panel_x + 35, 90), 12, 2)
        
        txt = self.font.render(f"{money}", True, "gold")
        screen.blit(txt, (panel_x + 55, 82))

    def draw_speed_controls(self, screen, game_speed):
        panel_x = c.SCREEN_WIDTH
        panel_center = panel_x + (c.SIDE_PANEL // 2)
        y_pos = 125 
        
        btn_size = 32
        gap = 15
        total_w = (3 * btn_size) + (2 * gap)
        start_x = panel_center - (total_w // 2)
        
        buttons = ["pause", "play", "fast"]
        
        self.speed_rects = {}
        
        for i, name in enumerate(buttons):
            x = start_x + (i * (btn_size + gap))
            rect = pg.Rect(x, y_pos, btn_size, btn_size)
            self.speed_rects[name] = rect
            
            current_val = i 
            is_active = (game_speed == current_val)
            
            if name in self.speed_imgs:
                img = self.speed_imgs[name]
                img_scaled = pg.transform.scale(img, (btn_size, btn_size))
                
                if not is_active:
                    img_scaled.set_alpha(150)
                else:
                    img_scaled.set_alpha(255)
                
                screen.blit(img_scaled, rect)
                if is_active:
                    pg.draw.rect(screen, "gold", rect, 2, border_radius=4)
            else:
                color = (0, 255, 0) if is_active else (100, 100, 100)
                pg.draw.rect(screen, color, rect)

    def draw_shop(self, screen, money, selected):
        panel_x = c.SCREEN_WIDTH
        panel_center = panel_x + (c.SIDE_PANEL // 2)
        
        towers = ["archer", "crossbow", "cannon", "ice", "poison", "lightning"]
        
        title = self.font.render("SHOP", True, (200, 200, 200))
        title_rect = title.get_rect(center=(panel_center, 175))
        screen.blit(title, title_rect)
        
        line_start = (panel_x + 5, 185)
        line_end = (panel_x + c.SIDE_PANEL - 5, 185)
        pg.draw.line(screen, (100, 100, 100), line_start, line_end, 2)

        START_Y = 195
        COLUMNS = 2
        SLOT_W = 86
        SLOT_H = 80 
        GAP = 8
        
        total_width = (SLOT_W * COLUMNS) + (GAP * (COLUMNS - 1))
        start_x = panel_center - (total_width // 2)
        
        self.shop_rects = {} 
        
        for i, name in enumerate(towers):
            col = i % COLUMNS
            row = i // COLUMNS
            
            x_pos = start_x + (col * (SLOT_W + GAP))
            y_pos = START_Y + (row * (SLOT_H + GAP))
            
            slot_rect = pg.Rect(x_pos, y_pos, SLOT_W, SLOT_H)
            self.shop_rects[name] = slot_rect
            
            bg_color = (80, 80, 80) if selected == name else (60, 60, 60)
            pg.draw.rect(screen, bg_color, slot_rect, border_radius=8)
            
            border_col = "red" if selected == name else (100, 100, 100)
            pg.draw.rect(screen, border_col, slot_rect, 2 if selected == name else 1, border_radius=8)
            
            if name in self.turret_images:
                orig = self.turret_images[name]
                max_h = 38 
                ratio = max_h / orig.get_height()
                target_w = int(orig.get_width() * ratio)
                
                if target_w > SLOT_W - 10:
                    target_w = SLOT_W - 10
                    ratio = target_w / orig.get_width()
                    max_h = int(orig.get_height() * ratio)

                icon = pg.transform.scale(orig, (target_w, max_h))
            else:
                icon = pg.Surface((30, 40)); icon.fill("purple")

            icon_rect = icon.get_rect(center=(slot_rect.centerx, slot_rect.top + 28))
            screen.blit(icon, icon_rect)
            
            d_name = name.capitalize()
            if name == "lightning": d_name = "Tesla"
            
            name_surf = self.font_tiny.render(d_name, True, (220, 220, 220))
            name_rect = name_surf.get_rect(midtop=(slot_rect.centerx, icon_rect.bottom + 2))
            screen.blit(name_surf, name_rect)
            
            cost = c.TURRET_DATA[name]["cost"]
            p_col = (100, 255, 100) if money >= cost else (255, 80, 80)
            
            cost_surf = self.font_price.render(f"{cost}", True, p_col)
            cost_rect = cost_surf.get_rect(midbottom=(slot_rect.centerx, slot_rect.bottom - 5))
            screen.blit(cost_surf, cost_rect)

    def draw_charges(self, screen, charges):
        panel_x = c.SCREEN_WIDTH
        panel_center = panel_x + (c.SIDE_PANEL // 2)
        bottom_y = c.SCREEN_HEIGHT - 30
        
        total_w = (4 * 20) + (3 * 5)
        start_x = panel_center - (total_w // 2)
        
        txt = self.font_tiny.render("UPGRADES", True, "grey")
        txt_rect = txt.get_rect(center=(panel_center, bottom_y - 25))
        screen.blit(txt, txt_rect)
        
        for i in range(c.MAX_UPGRADES):
            x = start_x + (i * 25)
            if i < charges:
                scaled = pg.transform.scale(self.orb_full, (20, 20))
                screen.blit(scaled, (x, bottom_y - 10))
            else:
                scaled = pg.transform.scale(self.orb_empty, (20, 20))
                screen.blit(scaled, (x, bottom_y - 10))

    def check_shop_click(self, mouse_pos):
        if not hasattr(self, 'shop_rects'): return None
        for name, rect in self.shop_rects.items():
            if rect.collidepoint(mouse_pos):
                return name
        return None

    def check_speed_click(self, mouse_pos):
        if not hasattr(self, 'speed_rects'): return None
        for name, rect in self.speed_rects.items():
            if rect.collidepoint(mouse_pos):
                if name == "pause": return 0
                if name == "play": return 1
                if name == "fast": return 2
        return None