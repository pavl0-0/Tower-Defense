import pygame as pg
import cv2
import constants as c

class VideoBackground:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        self.success = False
        if self.cap.isOpened():
            self.success = True
        else:
            print(f"ПОМИЛКА: Не вдалося відкрити відео {video_path}")
        
        self.ZOOM_FACTOR = 1.5

    def draw(self, screen):
        if not self.success:
            full_w = c.SCREEN_WIDTH + c.SIDE_PANEL
            screen.fill((20, 20, 30))
            return

        ret, frame = self.cap.read()
        
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        if ret:
            target_w = c.SCREEN_WIDTH + c.SIDE_PANEL
            target_h = c.SCREEN_HEIGHT
            
            video_h, video_w = frame.shape[:2]
            
            scale_w = target_w / video_w
            scale_h = target_h / video_h
            
            scale = max(scale_w, scale_h) * self.ZOOM_FACTOR
            
            new_w = int(video_w * scale)
            new_h = int(video_h * scale)
            
            frame = cv2.resize(frame, (new_w, new_h))
            
            start_x = (new_w - target_w) // 2
            start_y = (new_h - target_h) // 2
            
            frame = frame[start_y:start_y+target_h, start_x:start_x+target_w]
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame.swapaxes(0, 1)
            surf = pg.surfarray.make_surface(frame)
            
            screen.blit(surf, (0, 0))
            
            overlay = pg.Surface((target_w, target_h), pg.SRCALPHA)
            pg.draw.rect(overlay, (0, 0, 0, 100), overlay.get_rect())
            screen.blit(overlay, (0, 0))

class Button():
    def __init__(self, x, y, width, height, text, text_col, color, hover_color):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.text_col = text_col
        self.color = color
        self.hover_color = hover_color
        self.font = pg.font.SysFont("Arial", 24, bold=True)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pg.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            pg.draw.rect(surface, self.hover_color, self.rect, border_radius=10)
            if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        else:
            pg.draw.rect(surface, self.color, self.rect, border_radius=10)

        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        pg.draw.rect(surface, "white", self.rect, 2, border_radius=10)

        text_img = self.font.render(self.text, True, self.text_col)
        text_rect = text_img.get_rect(center=self.rect.center)
        surface.blit(text_img, text_rect)

        return action

class MainMenu:
    def __init__(self):
        self.title_font = pg.font.SysFont("Arial", 40, bold=True)
        
        full_w = c.SCREEN_WIDTH + c.SIDE_PANEL
        center_x = full_w // 2
        
        btn_w = 220
        btn_h = 60
        gap = 20
        buttons_count = 5
        
        total_h = (buttons_count * btn_h) + ((buttons_count - 1) * gap)
        start_y = (c.SCREEN_HEIGHT - total_h) // 2 + 40

        btn_x = center_x - (btn_w // 2)

        self.btn_campaign = Button(btn_x, start_y, btn_w, btn_h, 
                                   "CAMPAIGN", "white", "gray30", "gray50")
        
        self.btn_survival = Button(btn_x, start_y + 1 * (btn_h + gap), btn_w, btn_h, 
                                   "SURVIVAL", "white", "gray30", "gray50")
        
        self.btn_stats = Button(btn_x, start_y + 2 * (btn_h + gap), btn_w, btn_h, 
                                "STATISTICS", "white", "gray30", "gray50")

        self.btn_settings = Button(btn_x, start_y + 3 * (btn_h + gap), btn_w, btn_h, 
                                   "SETTINGS", "white", "gray30", "gray50")

        self.btn_exit = Button(btn_x, start_y + 4 * (btn_h + gap), btn_w, btn_h, 
                               "EXIT", "white", "gray30", "gray50")
        
        self.title_pos = (center_x, start_y - 60)

    def draw(self, surface):
        action = None
        
        title = self.title_font.render("TOWER DEFENSE", True, "white")
        title_shadow = self.title_font.render("TOWER DEFENSE", True, "black")
        t_rect = title.get_rect(center=self.title_pos)
        surface.blit(title_shadow, (t_rect.x + 3, t_rect.y + 3))
        surface.blit(title, t_rect)

        if self.btn_campaign.draw(surface): action = "campaign"
        if self.btn_survival.draw(surface): action = "survival"
        if self.btn_stats.draw(surface): action = "stats"
        if self.btn_settings.draw(surface): action = "settings"
        if self.btn_exit.draw(surface): action = "exit"
            
        return action

class GamePauseMenu:
    def __init__(self):
        self.font = pg.font.SysFont("Arial", 30, bold=True)
        
        self.resume_btn = Button(0, 0, 220, 50, "RESUME", "white", "orange", "darkorange")
        self.menu_btn = Button(0, 0, 220, 50, "MENU", "white", "dodgerblue", "deepskyblue")
        self.quit_btn = Button(0, 0, 220, 50, "EXIT GAME", "white", "crimson", "darkred")
    
    def draw(self, screen):
        full_w = c.SCREEN_WIDTH + c.SIDE_PANEL
        center_x = full_w // 2
        center_y = c.SCREEN_HEIGHT // 2
        
        overlay = pg.Surface((full_w, c.SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0,0,0,150))
        screen.blit(overlay, (0,0))
        
        gap = 20
        btn_h = 50
        
        self.resume_btn.rect.center = (center_x, center_y - (btn_h + gap))
        self.menu_btn.rect.center   = (center_x, center_y)
        self.quit_btn.rect.center   = (center_x, center_y + (btn_h + gap))
        
        title = self.font.render("PAUSED", True, "white")
        screen.blit(title, title.get_rect(center=(center_x, center_y - 130)))
        
        action = 0
        if self.resume_btn.draw(screen):
            action = 1 
        if self.menu_btn.draw(screen):
            action = 2 
        if self.quit_btn.draw(screen):
            action = -1
            
        return action

class TextInput:
    def __init__(self, font, x, y, width, height, prompt="Enter Name:"):
        self.font = font
        full_w = c.SCREEN_WIDTH + c.SIDE_PANEL
        self.center_x = full_w // 2
        self.rect = pg.Rect(0, 0, width, height)
        self.rect.center = (self.center_x, c.SCREEN_HEIGHT // 2)
        
        self.text = ""
        self.prompt = prompt
        self.active = True
        self.done = False
        self.color_inactive = pg.Color('lightskyblue3')
        self.color_active = pg.Color('dodgerblue2')
        self.color = self.color_active

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    if len(self.text) > 0: self.done = True
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 12: self.text += event.unicode

    def draw(self, screen):
        box_w = self.rect.w + 120
        box_h = self.rect.h + 150 
        
        bg_rect = pg.Rect(0, 0, box_w, box_h)
        bg_rect.center = self.rect.center
        
        overlay = pg.Surface((bg_rect.w, bg_rect.h), pg.SRCALPHA)
        pg.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect(), border_radius=20)
        screen.blit(overlay, bg_rect.topleft)
        
        pg.draw.rect(screen, "white", bg_rect, 3, border_radius=20)

        prompt_surf = self.font.render(self.prompt, True, "white")
        prompt_rect = prompt_surf.get_rect(center=(self.rect.centerx, self.rect.top - 45))
        screen.blit(prompt_surf, prompt_rect)
        
        txt_surface = self.font.render(self.text, True, "white")
        
        width = max(200, txt_surface.get_width() + 20)
        self.rect.w = width
        self.rect.centerx = self.center_x
        
        text_y = self.rect.centery - txt_surface.get_height() // 2
        
        screen.blit(txt_surface, (self.rect.x + 10, text_y))
        
        pg.draw.rect(screen, self.color, self.rect, 2, border_radius=5)

class LevelSelectMenu:
    def __init__(self, font, font_small, screen_w, screen_h, max_level=5):
        self.font = font
        self.font_small = font_small
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.max_level = max_level

        self.btn_w = 120
        self.btn_h = 60
        self.gap = 20

        self.back_rect = pg.Rect(20, 20, 120, 50)

    def draw(self, screen):
        overlay = pg.Surface((self.screen_w, self.screen_h), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        title = self.font.render("Оберіть рівень", True, "white")
        screen.blit(title, title.get_rect(center=(self.screen_w // 2, 120)))

        pg.draw.rect(screen, "grey30", self.back_rect, border_radius=10)
        pg.draw.rect(screen, "white", self.back_rect, 2, border_radius=10)
        back_txt = self.font_small.render("BACK", True, "white")
        screen.blit(back_txt, back_txt.get_rect(center=self.back_rect.center))

        mx, my = pg.mouse.get_pos()
        clicked = False
        for e in pg.event.get(pg.MOUSEBUTTONDOWN):
            if e.button == 1:
                clicked = True

        cols = 3
        start_x = self.screen_w // 2 - (cols * self.btn_w + (cols - 1) * self.gap) // 2
        start_y = 200

        for i in range(1, self.max_level + 1):
            row = (i - 1) // cols
            col = (i - 1) % cols
            x = start_x + col * (self.btn_w + self.gap)
            y = start_y + row * (self.btn_h + self.gap)
            rect = pg.Rect(x, y, self.btn_w, self.btn_h)

            hover = rect.collidepoint(mx, my)
            color = "grey50" if hover else "grey25"
            pg.draw.rect(screen, color, rect, border_radius=12)
            pg.draw.rect(screen, "white", rect, 2, border_radius=12)

            txt = self.font.render(str(i), True, "white")
            screen.blit(txt, txt.get_rect(center=rect.center))

            if clicked and hover:
                return i

        if clicked and self.back_rect.collidepoint(mx, my):
            return "back"

        return None

class Slider:
    def __init__(self, x, y, w, h, initial_val=0.5):
        self.rect = pg.Rect(x, y, w, h)
        self.val = initial_val
        self.grabbed = False
        
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.grabbed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.grabbed = False
            
        if self.grabbed:
            mx, my = pg.mouse.get_pos()
            relative_x = mx - self.rect.x
            self.val = relative_x / self.rect.w
            self.val = max(0.0, min(1.0, self.val)) 
            return True
        return False

    def draw(self, surface):
        pg.draw.rect(surface, "grey40", self.rect, border_radius=5)
        
        fill_rect = pg.Rect(self.rect.x, self.rect.y, self.rect.w * self.val, self.rect.h)
        pg.draw.rect(surface, "dodgerblue", fill_rect, border_radius=5)
        pg.draw.rect(surface, "white", self.rect, 2, border_radius=5)
        
        handle_x = self.rect.x + (self.rect.w * self.val)
        pg.draw.circle(surface, "white", (int(handle_x), self.rect.centery), self.rect.h // 2 + 4)

class SettingsMenu:
    def __init__(self, font, width, height, audio_manager):
        self.font = font
        self.width = width
        self.height = height
        self.audio = audio_manager
        
        cx = width // 2
        cy = height // 2
        
        self.music_slider = Slider(cx - 100, cy - 50, 200, 20, self.audio.music_volume)
        self.sfx_slider = Slider(cx - 100, cy + 50, 200, 20, self.audio.sfx_volume)
        
        self.back_btn = Button(cx - 60, cy + 120, 120, 50, "BACK", "white", "grey30", "grey50")

    def draw(self, surface):
        overlay = pg.Surface((self.width, self.height), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        panel = pg.Rect(self.width//2 - 200, self.height//2 - 150, 400, 350)
        pg.draw.rect(surface, (50, 50, 55), panel, border_radius=15)
        pg.draw.rect(surface, "gold", panel, 3, border_radius=15)
        
        title = self.font.render("SETTINGS", True, "gold")
        surface.blit(title, title.get_rect(center=(self.width//2, self.height//2 - 120)))
        
        m_txt = self.font.render(f"Music Volume: {int(self.music_slider.val * 100)}%", True, "white")
        surface.blit(m_txt, (self.width//2 - 100, self.height//2 - 80))
        self.music_slider.draw(surface)
        
        s_txt = self.font.render(f"SFX Volume: {int(self.sfx_slider.val * 100)}%", True, "white")
        surface.blit(s_txt, (self.width//2 - 100, self.height//2 + 20))
        self.sfx_slider.draw(surface)
        
        if self.back_btn.draw(surface):
            return "back"
            
        return None

    def handle_event(self, event):
        if self.music_slider.handle_event(event):
            self.audio.set_music_volume(self.music_slider.val)
            
        if self.sfx_slider.handle_event(event):
            self.audio.set_sfx_volume(self.sfx_slider.val)