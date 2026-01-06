import pygame as pg
import constants as c
from interface import UIManager 
from menu import MainMenu, GamePauseMenu, TextInput, VideoBackground, LevelSelectMenu, SettingsMenu
from audio import AudioManager
from database import DatabaseManager
from map_generator import MapGenerator
from gameplay import Gameplay
from world import World
from castle import Castle

class Game:
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
        pg.display.set_caption("Tower Defense")

        self.font_large = pg.font.SysFont("Arial", 24, bold=True)
        self.font_small = pg.font.SysFont("Arial", 12, bold=True)
        self.font = pg.font.SysFont("Arial", 16, bold=True)
        
        self.WAVE_DELAY = 5000 
        self.running = True
        
        self.in_menu = True
        self.in_level_select = False
        self.in_stats = False
        self.in_settings = False
        self.game_paused = False
        self.game_over = False
        self.level_complete = False
        
        self.current_campaign_level = 1
        self.current_game_mode = "survival"
        self.player_id = None
        self.player_name = ""
        
        self.game_state = { "money": 0, "lives": 0, "wave": 0, "charges": 0, "selected_turret": None, "game_speed": 0 }
        self.stats_data = {"campaign": None, "survival": None}
        
        self.db = DatabaseManager()
        self.audio_manager = AudioManager()
        self.map_gen = MapGenerator(c.TILE_SIZE, c.ROWS, c.COLS)
        
        self.load_assets()
        
        self.ui = UIManager(self.gui_sheet, self.turret_imgs, self.speed_imgs, self.system_pause_img)
        self.main_menu = MainMenu()
        self.settings_menu = SettingsMenu(self.font_large, c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT, self.audio_manager)
        self.level_menu = LevelSelectMenu(self.font_large, self.font_small, c.SCREEN_WIDTH, c.SCREEN_HEIGHT, 5)
        self.pause_menu = GamePauseMenu()
        self.video_bg = VideoBackground("assets/menu_bg.mp4")
        
        self.end_overlay = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.SRCALPHA)
        self.end_overlay.fill((0, 0, 0, 210))
        
        menu_map = self.map_gen.get_level_data(1)
        self.menu_world = World(menu_map, None, self.tile_imgs)
        self.menu_world.process_data()
        lp = self.menu_world.waypoints[-1] if self.menu_world.waypoints else (0,0)
        self.menu_castle = Castle("assets/Simple Tower Defense/Towers/Castle/spr_castle_blue.png", lp[0], lp[1], 1)

        self.gameplay = Gameplay(self, self.map_gen, self.ui, self.audio_manager, self.tile_imgs, self.proj_imgs)

    def load_assets(self):
        try:
            grass_imgs = [pg.image.load(f'assets/Simple Tower Defense/Environment/Grass/spr_grass_0{i}.png').convert_alpha() for i in range(1,4)]
            self.grass_imgs = [pg.transform.scale(img, (c.TILE_SIZE, c.TILE_SIZE)) for img in grass_imgs]

            ground_set = pg.image.load('assets/Simple Tower Defense/Environment/Tile Set/spr_tile_set_ground.png').convert_alpha()
            ts_w, ts_h = ground_set.get_width() // 3, ground_set.get_height() // 3
            self.road_tiles = []
            for y in range(3):
                for x in range(3):
                    img = pg.transform.scale(ground_set.subsurface((x * ts_w, y * ts_h, ts_w, ts_h)), (c.TILE_SIZE, c.TILE_SIZE))
                    self.road_tiles.append(img)

            rock = pg.image.load('assets/Simple Tower Defense/Environment/Decoration/spr_rock_01.png').convert_alpha()
            self.rock_img = pg.transform.scale(rock, (c.TILE_SIZE, c.TILE_SIZE))
            shroom = pg.image.load('assets/Simple Tower Defense/Environment/Decoration/spr_mushroom_01.png').convert_alpha()
            self.mushroom_img = pg.transform.scale(shroom, (c.TILE_SIZE, c.TILE_SIZE))
            castle = pg.image.load("assets/Simple Tower Defense/Towers/Castle/spr_castle_blue.png").convert_alpha()
            self.player_castle_img = pg.transform.scale(castle, (c.TILE_SIZE, c.TILE_SIZE))

            self.tile_imgs = [self.grass_imgs[0], self.road_tiles, self.rock_img, self.mushroom_img, self.player_castle_img]

            self.gui_sheet = pg.image.load("assets/CrimsonFantasyGUI/GUISprite.png").convert_alpha()
            self.upgrade_arrow = pg.image.load("assets/Upgrade Arrows/200+ Arrow Cursors - Pack (32x32) - Free/Static/Direction/orange/24_90.png").convert_alpha()
            stone_btns = pg.image.load("assets/AncientUIpack/UI_stone_buttons_2.png").convert_alpha()
            sb_w, sb_h = stone_btns.get_width() // 5, stone_btns.get_height() // 6
            self.system_pause_img = stone_btns.subsurface(pg.Rect(sb_w, sb_h, sb_w, sb_h))

            self.enemy_imgs = {name: pg.image.load(f'assets/Simple Tower Defense/Enemies/spr_{name}.png').convert_alpha() 
                               for name in ["bat", "big_slime", "normal_slime", "goblin", "skeleton", "zombie", "ghost", "demon", "king_slime"]}
            
            self.turret_imgs = {
                "archer":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_archer.png').convert_alpha(),
                "crossbow":  pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_crossbow.png').convert_alpha(), 
                "cannon":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_cannon.png').convert_alpha(),
                "ice":       pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_ice_wizard.png').convert_alpha(),
                "poison":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_poison_wizard.png').convert_alpha(),
                "lightning": pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_lightning_tower.png').convert_alpha()
            }

            self.proj_imgs = {
                "archer":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_archer_projectile.png').convert_alpha(),
                "crossbow":  pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_crossbow_projectile.png').convert_alpha(),
                "cannon":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_cannon_projectile.png').convert_alpha(),
                "ice":       pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_ice_wizard_projectile.png').convert_alpha(),
                "poison":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_poison_wizard_projectile.png').convert_alpha(),
                "lightning": pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_lightning_tower_projectile.png').convert_alpha()
            }
            
            self.speed_imgs = {
                "pause": pg.image.load('assets/AncientUIpack/ancientPause.png').convert_alpha(),
                "play":  pg.image.load('assets/AncientUIpack/ancientPlay.png').convert_alpha(),
                "fast":  pg.image.load('assets/AncientUIpack/ancientFaster.png').convert_alpha()
            }

        except pg.error as e:
            print(f"ПОМИЛКА ЗАВАНТАЖЕННЯ: {e}")

    def start_game(self, mode):
        self.current_game_mode = mode
        self.gameplay.start_new_game(mode, self.current_campaign_level)

    def run_login(self):
        input_box = TextInput(self.font_large, c.SCREEN_WIDTH // 2 - 100, c.SCREEN_HEIGHT // 2, 200, 50, "Введіть ваше ім'я:")
        login_run = True
        self.audio_manager.play_music("menu")
        while login_run:
            self.clock.tick(60)
            self.video_bg.draw(self.screen)
            for event in pg.event.get():
                if event.type == pg.QUIT: pg.quit(); exit()
                input_box.handle_event(event)
            input_box.draw(self.screen)
            pg.display.flip()
            if input_box.done:
                self.player_name = input_box.text
                self.player_id = self.db.get_player_id(self.player_name)
                self.audio_manager.play_sfx("click")
                login_run = False

    def draw_end_screen(self, title, subtitle, buttons):
        self.screen.blit(self.end_overlay, (0, 0))
        t = self.font_large.render(title, True, "white")
        self.screen.blit(t, t.get_rect(center=(c.SCREEN_WIDTH//2, 160)))
        s = self.font_small.render(subtitle, True, "white")
        self.screen.blit(s, s.get_rect(center=(c.SCREEN_WIDTH//2, 195)))

        btn_w, btn_h = 260, 60
        gap = 18
        total_h = len(buttons) * btn_h + (len(buttons) - 1) * gap
        start_y = c.SCREEN_HEIGHT//2 - total_h//2 + 40
        mx, my = pg.mouse.get_pos()
        clicked = False
        for e in pg.event.get(pg.MOUSEBUTTONDOWN):
            if e.button == 1: clicked = True

        for i, (bid, text) in enumerate(buttons):
            rect = pg.Rect(c.SCREEN_WIDTH//2 - btn_w//2, start_y + i*(btn_h+gap), btn_w, btn_h)
            hover = rect.collidepoint(mx, my)
            color = "grey50" if hover else "grey25"
            pg.draw.rect(self.screen, color, rect, border_radius=14)
            pg.draw.rect(self.screen, "white", rect, 2, border_radius=14)
            txt = self.font_small.render(text, True, "white")
            self.screen.blit(txt, txt.get_rect(center=rect.center))
            if clicked and hover: return bid
        return None

    def draw_stats_window(self, data):
        overlay = pg.Surface((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) 
        self.screen.blit(overlay, (0, 0))
        
        panel_w, panel_h = 500, 400
        panel_rect = pg.Rect((c.SCREEN_WIDTH + c.SIDE_PANEL) // 2 - panel_w // 2, c.SCREEN_HEIGHT // 2 - panel_h // 2, panel_w, panel_h)
        pg.draw.rect(self.screen, (45, 45, 50), panel_rect, border_radius=15)
        pg.draw.rect(self.screen, "gold", panel_rect, 3, border_radius=15)

        title = self.font_large.render("STATISTICS", True, "gold")
        self.screen.blit(title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 30))

        camp = data.get("campaign")
        c_title = self.font.render("CAMPAIGN", True, "cyan")
        self.screen.blit(c_title, (panel_rect.x + 50, panel_rect.y + 100))
        lvl_val = camp[0] if camp else 1
        time_val = int(camp[1]) if camp else 0
        self.screen.blit(self.font.render(f"Max Level: {lvl_val}", True, "white"), (panel_rect.x + 70, panel_rect.y + 130))
        self.screen.blit(self.font.render(f"Time Played: {time_val}s", True, "white"), (panel_rect.x + 70, panel_rect.y + 160))

        surv = data.get("survival")
        s_title = self.font.render("SURVIVAL", True, "orange")
        self.screen.blit(s_title, (panel_rect.x + 50, panel_rect.y + 220))
        wave_val = surv[0] if surv else 0
        s_time_val = int(surv[1]) if surv else 0
        self.screen.blit(self.font.render(f"Best Wave: {wave_val}", True, "white"), (panel_rect.x + 70, panel_rect.y + 250))
        self.screen.blit(self.font.render(f"Best Time: {s_time_val}s", True, "white"), (panel_rect.x + 70, panel_rect.y + 280))

        hint = self.font_small.render("Press ESC to Back", True, "grey")
        self.screen.blit(hint, (panel_rect.centerx - hint.get_width() // 2, panel_rect.bottom - 40))

    def run(self):
        self.run_login()
        while self.running:
            self.clock.tick(c.FPS)
            self.screen.fill("grey100")

            if self.in_menu:
                self.audio_manager.play_music("menu")
                self.video_bg.draw(self.screen)
                if self.in_stats:
                    self.draw_stats_window(self.stats_data)
                    for event in pg.event.get():
                        if event.type == pg.QUIT: self.running = False
                        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: 
                            self.audio_manager.play_sfx("click"); self.in_stats = False
                elif self.in_settings:
                    action = self.settings_menu.draw(self.screen)
                    if action == "back": self.audio_manager.play_sfx("click"); self.in_settings = False
                    for event in pg.event.get():
                        if event.type == pg.QUIT: self.running = False
                        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.in_settings = False
                        self.settings_menu.handle_event(event)
                else:
                    action = self.main_menu.draw(self.screen)
                    if action == "campaign": self.audio_manager.play_sfx("click"); self.in_menu = False; self.in_level_select = True
                    elif action == "survival": self.audio_manager.play_sfx("click"); self.in_menu = False; self.start_game("survival")
                    elif action == "stats":
                        self.audio_manager.play_sfx("click"); self.in_stats = True
                        if self.player_id:
                            try:
                                self.stats_data["campaign"] = self.db.get_campaign_stats(self.player_id)
                                self.stats_data["survival"] = self.db.get_survival_stats(self.player_id)
                            except: print("DB Stats Error")
                    elif action == "settings": self.audio_manager.play_sfx("click"); self.in_settings = True
                    elif action == "exit": self.audio_manager.play_sfx("click"); self.running = False
                    for event in pg.event.get(): 
                        if event.type == pg.QUIT: self.running = False
            
            elif self.in_level_select:
                self.video_bg.draw(self.screen)
                choice = self.level_menu.draw(self.screen)
                if choice == "back": self.audio_manager.play_sfx("click"); self.in_level_select = False; self.in_menu = True
                elif isinstance(choice, int):
                    self.audio_manager.play_sfx("click"); self.current_campaign_level = choice
                    self.in_level_select = False; self.in_menu = False; self.start_game("campaign")
                for event in pg.event.get(): 
                    if event.type == pg.QUIT: self.running = False
            
            else:
                if not self.game_paused and not self.game_over and not self.level_complete:
                    self.gameplay.update()
                
                self.gameplay.draw(self.screen)
                
                if self.level_complete:
                    btn = self.draw_end_screen("LEVEL COMPLETE!", f"Level {self.current_campaign_level} finished", [("next", "NEXT LEVEL"), ("retry", "RETRY"), ("menu", "MAIN MENU")])
                    if btn == "next": self.audio_manager.play_sfx("click"); self.level_complete = False; self.current_campaign_level += 1; self.start_game("campaign")
                    elif btn == "retry": self.audio_manager.play_sfx("click"); self.level_complete = False; self.start_game("campaign")
                    elif btn == "menu": self.audio_manager.play_sfx("click"); self.level_complete = False; self.game_over = False; self.in_level_select = False; self.in_menu = True
                
                elif self.game_over:
                    btn = self.draw_end_screen("GAME OVER", "Try again?", [("retry", "RETRY"), ("menu", "MAIN MENU")])
                    if btn == "retry": self.audio_manager.play_sfx("click"); self.game_over = False; self.start_game(self.current_game_mode)
                    elif btn == "menu": self.audio_manager.play_sfx("click"); self.level_complete = False; self.game_over = False; self.in_level_select = False; self.in_menu = True

                elif self.game_paused:
                    action = self.pause_menu.draw(self.screen)
                    if action == 1: self.audio_manager.play_sfx("click"); self.game_paused = False
                    elif action == 2: self.audio_manager.play_sfx("click"); self.in_menu = True; self.game_paused = False
                    elif action == -1: self.running = False

                for event in pg.event.get():
                    if event.type == pg.QUIT: self.running = False
                    if not self.game_paused and not self.game_over and not self.level_complete:
                        self.gameplay.handle_input(event)
                    else:
                        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: self.game_paused = False

            pg.display.flip()
        pg.quit()