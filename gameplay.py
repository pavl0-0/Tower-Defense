import pygame as pg
import random
import constants as c
from enemy import Bat, Big_slime, NormalSlime, Goblin, Skeleton, Zombie, Ghost, Demon, KingSlime
from turret import Turret
from projectile import Projectile
from upgrade_drop import UpgradeDrop
from floating_text import FloatingText
from castle import Castle
from world import World

class Gameplay:
    def __init__(self, game_instance, map_gen, ui, audio_manager, tile_imgs, proj_imgs):
        self.game = game_instance
        self.map_gen = map_gen
        self.ui = ui
        self.audio_manager = audio_manager
        self.tile_imgs = tile_imgs
        self.proj_imgs = proj_imgs
        
        self.font_small = pg.font.SysFont("Arial", 12, bold=True)

        self.enemy_group = pg.sprite.Group()
        self.turret_group = pg.sprite.Group()
        self.projectile_group = pg.sprite.Group()
        self.drop_group = pg.sprite.Group()
        self.text_group = pg.sprite.Group()
        
        self.world = None
        self.player_castle = None
        self.active_turret = None
        
        self.waves_data = []
        self.last_spawn = 0
        self.last_wave_complete = 0
        self.game_start_time = 0

    def start_new_game(self, mode, level):
        """Ініціалізація нової гри"""
        if mode == "campaign":
            map_json = self.map_gen.get_level_data(level)
        else:
            map_json = self.map_gen.generate_new_map(difficulty=5)

        self.world = World(map_json, None, self.tile_imgs)
        self.world.process_data()
        
        last_pos = self.world.waypoints[-1] if self.world.waypoints else (0,0)
        self.player_castle = Castle("assets/Simple Tower Defense/Towers/Castle/spr_castle_blue.png", last_pos[0], last_pos[1], c.START_LIVES)
        
        self.enemy_group.empty()
        self.turret_group.empty()
        self.projectile_group.empty()
        self.drop_group.empty()
        self.text_group.empty()
        self.active_turret = None
    
        self.game.game_state["money"] = c.START_MONEY
        self.game.game_state["lives"] = c.START_LIVES
        self.game.game_state["wave"] = 1
        self.game.game_state["charges"] = 0
        self.game.game_state["selected_turret"] = None
        self.game.game_state["game_speed"] = 0
        
        if mode == "campaign":
            self.waves_data = self.generate_wave(level, 1)
        else:
            self.waves_data = self.generate_wave(100, 1)

        self.game_start_time = pg.time.get_ticks()
        self.last_spawn = pg.time.get_ticks()
        self.audio_manager.play_music("game")

    def update(self):
        """Оновлення ігрової логіки"""
        state = self.game.game_state
        
        if state["game_speed"] > 0:
            if not self.waves_data and len(self.enemy_group) == 0:
                if pg.time.get_ticks() - self.last_wave_complete > self.game.WAVE_DELAY:
                    state["wave"] += 1
                    lvl = self.game.current_campaign_level if self.game.current_game_mode == "campaign" else 100
                    new_wave = self.generate_wave(lvl, state["wave"])
                    
                    if new_wave:
                        self.waves_data = new_wave
                        self.last_spawn = pg.time.get_ticks()
                    elif self.game.current_game_mode == "campaign":
                        self.audio_manager.play_sfx("level_complete")
                        self.game.level_complete = True
                        state["game_speed"] = 0
                else:
                    self.last_wave_complete = pg.time.get_ticks()

            if self.waves_data:
                current_speed = state["game_speed"]
                effective_cooldown = c.SPAWN_COOLDOWN / current_speed
                if pg.time.get_ticks() - self.last_spawn > effective_cooldown:
                    enemy_type = self.waves_data.pop(0)
                    self.spawn_enemy(enemy_type)
                    self.last_spawn = pg.time.get_ticks()

        loops = 2 if state["game_speed"] == 2 else 1
        if state["game_speed"] == 0: loops = 0
        
        for _ in range(loops):
            self.enemy_group.update()
            self.turret_group.update(self.projectile_group, self.enemy_group)
            self.projectile_group.update()
            self.drop_group.update()
            self.check_collisions()

        self.text_group.update()

    def check_collisions(self):
        hits = pg.sprite.groupcollide(self.enemy_group, self.projectile_group, False, True)
        for enemy, projs in hits.items():
            for proj in projs:
                self.audio_manager.play_sfx("enemy_hit")
                
                if proj.turret_type == "cannon":
                    enemy.health -= proj.damage
                    for other in self.enemy_group:
                        if other != enemy and other.pos.distance_to(enemy.pos) < 60:
                            other.health -= proj.damage * 0.5
                            self.text_group.add(FloatingText("BOOM", other.rect.centerx, other.rect.centery, "orange"))
                elif proj.turret_type == "ice":
                    enemy.health -= proj.damage
                    enemy.slow_down(0.5, 60)
                    self.text_group.add(FloatingText("SLOW", enemy.rect.centerx, enemy.rect.centery, "cyan"))
                elif proj.turret_type == "poison":
                    enemy.health -= proj.damage
                    enemy.poison(2, 300)
                    self.text_group.add(FloatingText("POISON", enemy.rect.centerx, enemy.rect.centery, "green"))
                else:
                    enemy.health -= proj.damage

                if enemy.health <= 0:
                    self.audio_manager.play_sfx("enemy_death")
                    enemy.kill()
                    self.game.game_state["money"] += enemy.reward
                    self.text_group.add(FloatingText(f"+{enemy.reward}", enemy.rect.centerx, enemy.rect.centery, "gold"))
                    if random.random() < 0.1:
                        self.drop_group.add(UpgradeDrop(self.game.upgrade_arrow, enemy.pos.x, enemy.pos.y))

        for enemy in self.enemy_group:
            if enemy.health == -100:
                enemy.kill()
                self.game.game_state["lives"] -= 1
                self.audio_manager.play_sfx("base_hit")
                self.player_castle.update(self.game.game_state["lives"])
                self.text_group.add(FloatingText("-1 HP", c.SCREEN_WIDTH - 50, 50, "red"))
                
                if self.game.game_state["lives"] <= 0:
                    self.handle_game_over()

    def handle_game_over(self):
        self.audio_manager.play_sfx("game_over")
        if self.game.player_id:
            time_played = (pg.time.get_ticks() - self.game_start_time) / 1000.0
            if self.game.current_game_mode == "survival":
                self.game.db.save_survival_score(self.game.player_id, self.game.game_state["wave"], time_played)
            else:
                self.game.db.save_campaign_progress(self.game.player_id, self.game.game_state["wave"], time_played)
        self.game.game_over = True
        self.game.game_state["game_speed"] = 0

    def handle_input(self, event):
        """Обробка кліків"""
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.game.game_paused = True

        if event.type == pg.MOUSEBUTTONDOWN:
            mx, my = pg.mouse.get_pos()
            
            if event.button == 1:
                if self.ui.check_system_pause_click((mx, my)):
                    self.audio_manager.play_sfx("click")
                    self.game.game_paused = True
                    return

                new_speed = self.ui.check_speed_click((mx, my))
                if new_speed is not None:
                    self.audio_manager.play_sfx("click")
                    self.game.game_state["game_speed"] = new_speed
                    return

                shop_item = self.ui.check_shop_click((mx, my))
                if shop_item:
                    self.process_shop_click(shop_item)
                    return

                self.process_field_click(mx, my)

            if event.button == 3:
                if self.game.game_state["selected_turret"]:
                    self.game.game_state["selected_turret"] = None
                    pg.mouse.set_visible(True)
                elif self.active_turret:
                    self.active_turret = None

    def process_field_click(self, mx, my):
        if self.active_turret:
            btn_x = self.active_turret.rect.centerx - (c.BUTTON_WIDTH // 2)
            btn_y = self.active_turret.rect.centery + 35
            
            upg_rect = pg.Rect(btn_x, btn_y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
            sell_rect = pg.Rect(btn_x, btn_y + 35, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
            
            if upg_rect.collidepoint(mx, my):
                if self.game.game_state["charges"] > 0 and self.active_turret.upgrade_level < 3:
                    self.audio_manager.play_sfx("build")
                    self.game.game_state["charges"] -= 1
                    self.active_turret.upgrade()
                    self.text_group.add(FloatingText("UPGRADED!", mx, my, "gold"))
                else: self.audio_manager.play_sfx("click")
                return

            if sell_rect.collidepoint(mx, my):
                self.audio_manager.play_sfx("destroy")
                base_cost = c.TURRET_DATA[self.active_turret.turret_type]["cost"]
                refund = 0
                if self.active_turret.upgrade_level == 1: refund = int(base_cost * 0.5)
                elif self.active_turret.upgrade_level == 2: refund = int(base_cost * 0.75)
                elif self.active_turret.upgrade_level == 3: refund = int(base_cost * 1.0)
                self.game.game_state["money"] += refund
                self.text_group.add(FloatingText(f"+{refund}", mx, my, "gold"))
                self.active_turret.kill()
                self.active_turret = None
                return

        if mx < c.SCREEN_WIDTH:
            is_busy = (self.game.game_state["selected_turret"] is not None) or (self.active_turret is not None)
            if not is_busy:
                for drop in self.drop_group:
                    if drop.rect.collidepoint(mx, my):
                        self.audio_manager.play_sfx("click")
                        if self.game.game_state["charges"] < c.MAX_UPGRADES:
                            self.game.game_state["charges"] += 1
                            drop.kill()
                            self.text_group.add(FloatingText("+1 CHARGE", mx, my, "lime"))
                        else:
                            self.text_group.add(FloatingText("FULL!", mx, my, "red"))
                        return

            if self.game.game_state["selected_turret"]:
                cost = c.TURRET_DATA[self.game.game_state["selected_turret"]]["cost"]
                if self.game.game_state["money"] >= cost:
                    if self.create_turret((mx, my), self.game.game_state["selected_turret"]):
                        self.game.game_state["money"] -= cost
                        self.text_group.add(FloatingText(f"-{cost}", mx, my, "red"))
                    else:
                        self.audio_manager.play_sfx("click")
                        self.text_group.add(FloatingText("Invalid!", mx, my, "red"))
                else:
                    self.audio_manager.play_sfx("click")
                    self.text_group.add(FloatingText("No Money", mx, my, "red"))
            else:
                self.active_turret = None
                for t in self.turret_group:
                    if t.rect.collidepoint(mx, my):
                        self.audio_manager.play_sfx("click")
                        self.active_turret = t
                        break

    def process_shop_click(self, item):
        self.audio_manager.play_sfx("click")
        if self.game.game_state["selected_turret"] == item:
            self.game.game_state["selected_turret"] = None
            pg.mouse.set_visible(True)
        else:
            self.game.game_state["selected_turret"] = item
            self.active_turret = None
            pg.mouse.set_visible(False)

    def draw(self, screen):
        self.world.draw(screen)
        self.player_castle.draw(screen)
        
        for enemy in self.enemy_group:
            screen.blit(enemy.image, enemy.rect)
            if enemy.health < enemy.max_health:
                ratio = max(0, enemy.health / enemy.max_health)
                pg.draw.rect(screen, "red", (enemy.rect.centerx - 15, enemy.rect.top - 5, 30, 4))
                pg.draw.rect(screen, "lime", (enemy.rect.centerx - 15, enemy.rect.top - 5, 30 * ratio, 4))

        for t in self.turret_group:
            screen.blit(t.image, t.rect)
            lvl_text = self.font_small.render(f"Lv{t.upgrade_level}", True, "white")
            lvl_shadow = self.font_small.render(f"Lv{t.upgrade_level}", True, "black")
            screen.blit(lvl_shadow, (t.rect.centerx-9, t.rect.top-14))
            screen.blit(lvl_text, (t.rect.centerx-10, t.rect.top-15))

        self.projectile_group.draw(screen)
        self.drop_group.draw(screen)
        self.text_group.draw(screen)

        if self.active_turret:
            self.active_turret.draw_range(screen)
            self.draw_upgrade_ui(screen)

        self.ui.draw(screen, self.game.game_state)
        
        if self.game.game_state["selected_turret"]:
            self.draw_placement_preview(screen)

    def draw_upgrade_ui(self, screen):
        btn_x = self.active_turret.rect.centerx - (c.BUTTON_WIDTH // 2)
        btn_y = self.active_turret.rect.centery + 35
        
        upg_rect = pg.Rect(btn_x, btn_y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        sell_rect = pg.Rect(btn_x, btn_y + 35, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
        
        if self.active_turret.upgrade_level >= 3:
            col, txt = "grey40", "MAX"
        elif self.game.game_state["charges"] > 0:
            col, txt = "darkgreen", "UPGRADE"
        else:
            col, txt = "grey40", "UPGRADE"
            
        pg.draw.rect(screen, col, upg_rect, border_radius=5)
        pg.draw.rect(screen, "white", upg_rect, 2, border_radius=5)
        t_surf = self.font_small.render(txt, True, "white")
        screen.blit(t_surf, t_surf.get_rect(center=upg_rect.center))
        
        # Sell Button
        base_cost = c.TURRET_DATA[self.active_turret.turret_type]["cost"]
        refund = int(base_cost * (0.25 + (0.25 * self.active_turret.upgrade_level)))
        pg.draw.rect(screen, "darkred", sell_rect, border_radius=5)
        pg.draw.rect(screen, "white", sell_rect, 2, border_radius=5)
        s_surf = self.font_small.render(f"SELL {refund}", True, "white")
        screen.blit(s_surf, s_surf.get_rect(center=sell_rect.center))

    def draw_placement_preview(self, screen):
        mx, my = pg.mouse.get_pos()
        if mx < c.SCREEN_WIDTH:
            pg.mouse.set_visible(False)
            r = c.TURRET_DATA[self.game.game_state["selected_turret"]]["range"]
            range_surf = pg.Surface((r * 2, r * 2), pg.SRCALPHA)
            pg.draw.circle(range_surf, (255, 255, 255, 100), (r, r), r)
            pg.draw.circle(range_surf, (255, 255, 255, 150), (r, r), r, 2)
            screen.blit(range_surf, (mx - r, my - r))
            img = self.game.turret_imgs[self.game.game_state["selected_turret"]]
            screen.blit(img, img.get_rect(center=(mx, my)))
        else:
            pg.mouse.set_visible(True)

    def spawn_enemy(self, enemy_type):
        img = self.game.enemy_imgs[enemy_type]
        new_enemy = None
        if enemy_type == "bat": new_enemy = Bat(self.world.waypoints, img)
        elif enemy_type == "normal_slime": new_enemy = NormalSlime(self.world.waypoints, img)
        elif enemy_type == "goblin": new_enemy = Goblin(self.world.waypoints, img)
        elif enemy_type == "skeleton": new_enemy = Skeleton(self.world.waypoints, img)
        elif enemy_type == "zombie": new_enemy = Zombie(self.world.waypoints, img)
        elif enemy_type == "ghost": new_enemy = Ghost(self.world.waypoints, img)
        elif enemy_type == "demon": new_enemy = Demon(self.world.waypoints, img)
        elif enemy_type == "big_slime": new_enemy = Big_slime(self.world.waypoints, img)
        elif enemy_type == "king_slime": new_enemy = KingSlime(self.world.waypoints, img)
        
        if new_enemy: self.enemy_group.add(new_enemy)

    def generate_wave(self, level, wave_number):
        enemies = []
        if level == 1:
            if wave_number == 1: enemies = ["normal_slime"] * 5
            elif wave_number == 2: enemies = ["normal_slime"] * 5 + ["bat"] * 3
            elif wave_number == 3: enemies = ["bat"] * 5 + ["goblin"] * 3
            else: return [] 
        elif level == 2:
            if wave_number == 1: enemies = ["goblin"] * 10
            elif wave_number == 2: enemies = ["skeleton"] * 5 + ["goblin"] * 5
            elif wave_number == 3: enemies = ["skeleton"] * 10
            elif wave_number == 4: enemies = ["zombie"] * 5 + ["skeleton"] * 5
            else: return []
        else:
            if wave_number > level + 2: return []
            count = 10 + (wave_number * 2)
            types = ["bat", "normal_slime", "goblin", "skeleton", "zombie", "ghost", "big_slime", "demon"]
            enemies = random.choices(types, k=count)
        return enemies

    def create_turret(self, pos, type_name):
        mx, my = pos[0] // c.TILE_SIZE, pos[1] // c.TILE_SIZE
        if mx < 0 or mx >= c.COLS or my < 0 or my >= c.ROWS: return False
        if self.world.tile_map[my][mx] != c.GRID_GRASS: return False 
        
        for t in self.turret_group:
            if t.tile_x == mx and t.tile_y == my: return False
            dist_x = abs(t.tile_x - mx); dist_y = abs(t.tile_y - my)
            if dist_x <= 1 and dist_y <= 1: return False 

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = mx + dx, my + dy
                if 0 <= nx < c.COLS and 0 <= ny < c.ROWS:
                    tile_val = self.world.tile_map[ny][nx]
                    if tile_val == c.GRID_ROAD or tile_val == c.GRID_BASE:
                        return False

        sound = self.audio_manager.get_sound(type_name)
        self.turret_group.add(Turret(self.game.turret_imgs[type_name], mx, my, self.game.proj_imgs[type_name], type_name, sound))
        self.audio_manager.play_sfx("build")
        return True