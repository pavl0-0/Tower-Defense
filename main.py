import pygame as pg
import json
import math
import random
import constants as c
import cv2
from world import World
from turret import Turret
from enemy import Bat, Big_slime, NormalSlime, Goblin, Skeleton, Zombie, Ghost, Demon, KingSlime
from projectile import Projectile
from upgrade_drop import UpgradeDrop
from floating_text import FloatingText
from interface import UIManager 
from menu import MainMenu, GamePauseMenu, TextInput, VideoBackground, LevelSelectMenu, SettingsMenu
from audio import AudioManager
from castle import Castle
from database import DatabaseManager
from map_generator import MapGenerator

pg.init()
db = DatabaseManager()
clock = pg.time.Clock()
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defense")

font = pg.font.SysFont("Arial", 16, bold=True)
font_small = pg.font.SysFont("Arial", 12, bold=True)
font_large = pg.font.SysFont("Arial", 24, bold=True)

WAVE_DELAY = 5000 
audio_manager = AudioManager()

in_stats = False
stats_data = {"campaign": None, "survival": None}

level_menu = LevelSelectMenu(font_large, font_small, c.SCREEN_WIDTH, c.SCREEN_HEIGHT, max_level=5)

video_bg = VideoBackground("assets/menu_bg.mp4")

end_overlay = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.SRCALPHA)
end_overlay.fill((0, 0, 0, 210))

player_name = ""
player_id = None
input_box = TextInput(font_large, c.SCREEN_WIDTH // 2 - 100, c.SCREEN_HEIGHT // 2, 200, 50, "Введіть ваше ім'я:")

login_run = True
audio_manager.play_music("menu")
while login_run:
    clock.tick(60)
    
    video_bg.draw(screen)
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            login_run = False
            pg.quit()
            exit()
        input_box.handle_event(event)

    input_box.draw(screen)
    pg.display.flip()
    
    if input_box.done:
        player_name = input_box.text
        player_id = db.get_player_id(player_name)
        audio_manager.play_sfx("click")
        login_run = False

try:
    grass_imgs = [
        pg.image.load('assets/Simple Tower Defense/Environment/Grass/spr_grass_01.png').convert_alpha(),
        pg.image.load('assets/Simple Tower Defense/Environment/Grass/spr_grass_02.png').convert_alpha(),
        pg.image.load('assets/Simple Tower Defense/Environment/Grass/spr_grass_03.png').convert_alpha()
    ]

    grass_imgs = [pg.transform.scale(img, (c.TILE_SIZE, c.TILE_SIZE)) for img in grass_imgs]

    ground_set = pg.image.load('assets/Simple Tower Defense/Environment/Tile Set/spr_tile_set_ground.png').convert_alpha()
    ts_w = ground_set.get_width() // 3
    ts_h = ground_set.get_height() // 3
    
    road_tiles = []
    for y in range(3):
        for x in range(3):
            rect = (x * ts_w, y * ts_h, ts_w, ts_h)
            img = ground_set.subsurface(rect)
            img = pg.transform.scale(img, (c.TILE_SIZE, c.TILE_SIZE))
            road_tiles.append(img)

    rock_img = pg.image.load('assets/Simple Tower Defense/Environment/Decoration/spr_rock_01.png').convert_alpha()
    rock_img = pg.transform.scale(rock_img, (c.TILE_SIZE, c.TILE_SIZE))
    
    mushroom_img = pg.image.load('assets/Simple Tower Defense/Environment/Decoration/spr_mushroom_01.png').convert_alpha()
    mushroom_img = pg.transform.scale(mushroom_img, (c.TILE_SIZE, c.TILE_SIZE))

    player_castle = pg.image.load("assets/Simple Tower Defense/Towers/Castle/spr_castle_blue.png").convert_alpha()
    player_castle = pg.transform.scale(player_castle, (c.TILE_SIZE, c.TILE_SIZE))

    tile_imgs = [
        grass_imgs[0], 
        road_tiles,
        rock_img,
        mushroom_img,
        rock_img,
        player_castle
    ]

    map_image = pg.image.load('levels/level1.png').convert_alpha()
    gui_sheet = pg.image.load("assets/CrimsonFantasyGUI/GUISprite.png").convert_alpha()
    upgrade_arrow = pg.image.load("assets/Upgrade Arrows/200+ Arrow Cursors - Pack (32x32) - Free/Static/Direction/orange/24_90.png").convert_alpha()

    stone_buttons_sheet = pg.image.load("assets/AncientUIpack/UI_stone_buttons_2.png").convert_alpha()
    
    sheet_w = stone_buttons_sheet.get_width()
    sheet_h = stone_buttons_sheet.get_height()
    tile_w = sheet_w // 5
    tile_h = sheet_h // 6
    
    sys_pause_rect = pg.Rect(tile_w, tile_h, tile_w, tile_h)
    system_pause_img = stone_buttons_sheet.subsurface(sys_pause_rect)

    bat_img = pg.image.load('assets/Simple Tower Defense/Enemies/spr_bat.png').convert_alpha()
    big_slime_img = pg.image.load('assets/Simple Tower Defense/Enemies/spr_big_slime.png').convert_alpha()
    normal_slime_img = pg.image.load('assets/Simple Tower Defense/Enemies/spr_normal_slime.png').convert_alpha()
    goblin_img = pg.image.load('assets/Simple Tower Defense/Enemies/spr_goblin.png').convert_alpha()
    skeleton_img = pg.image.load('assets/Simple Tower Defense/Enemies/spr_skeleton.png').convert_alpha()
    zombie_img = pg.image.load('assets/Simple Tower Defense/Enemies/spr_zombie.png').convert_alpha()
    ghost_img = pg.image.load('assets/Simple Tower Defense/Enemies/spr_ghost.png').convert_alpha()
    demon_img = pg.image.load('assets/Simple Tower Defense/Enemies/spr_demon.png').convert_alpha()
    king_slime_img = pg.image.load('assets/Simple Tower Defense/Enemies/spr_king_slime.png').convert_alpha()

    speed_imgs = {
        "pause": pg.image.load('assets/AncientUIpack/ancientPause.png').convert_alpha(),
        "play":  pg.image.load('assets/AncientUIpack/ancientPlay.png').convert_alpha(),
        "fast":  pg.image.load('assets/AncientUIpack/ancientFaster.png').convert_alpha()
    }

    turret_imgs = {
        "archer":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_archer.png').convert_alpha(),
        "crossbow":  pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_crossbow.png').convert_alpha(), 
        "cannon":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_cannon.png').convert_alpha(),
        "ice":       pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_ice_wizard.png').convert_alpha(),
        "poison":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_poison_wizard.png').convert_alpha(),
        "lightning": pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers/spr_tower_lightning_tower.png').convert_alpha()
    }

    proj_imgs = {
        "archer":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_archer_projectile.png').convert_alpha(),
        "crossbow":  pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_crossbow_projectile.png').convert_alpha(),
        "cannon":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_cannon_projectile.png').convert_alpha(),
        "ice":       pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_ice_wizard_projectile.png').convert_alpha(),
        "poison":    pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_poison_wizard_projectile.png').convert_alpha(),
        "lightning": pg.image.load('assets/Simple Tower Defense/Towers/Combat Towers Projectiles/spr_tower_lightning_tower_projectile.png').convert_alpha()
    }
except pg.error as e:
    print(f"ПОМИЛКА ЗАВАНТАЖЕННЯ: {e}")

map_gen = MapGenerator(c.TILE_SIZE, c.ROWS, c.COLS)
menu_map_data = map_gen.get_level_data(1)

world = World(menu_map_data, None, tile_imgs=tile_imgs)
world.process_data()

if world.waypoints:
    last_pos = world.waypoints[-1]
else:
    last_pos = (0, 0)

player_castle = Castle("assets/Simple Tower Defense/Towers/Castle/spr_castle_blue.png", last_pos[0], last_pos[1], c.START_LIVES)

ui = UIManager(gui_sheet, turret_imgs, speed_imgs, system_pause_img)
main_menu = MainMenu()
pause_menu = GamePauseMenu()

enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()
projectile_group = pg.sprite.Group()
drop_group = pg.sprite.Group()
text_group = pg.sprite.Group()

game_state = {
    "money": c.START_MONEY,
    "lives": c.START_LIVES,
    "wave": 1,
    "charges": 0,
    "selected_turret": None,
    "game_speed": 0
}

waves_data = []

in_menu = True
in_level_select = False
game_over = False
level_complete = False
game_paused = False

active_turret = None
last_spawn = pg.time.get_ticks()
last_wave_complete = pg.time.get_ticks()
game_start_time = 0

current_campaign_level = 1

def start_game(mode):
    global world, player_castle, waves_data, game_state, game_start_time, current_game_mode, last_pos, current_campaign_level
    current_game_mode = mode
    
    if mode == "campaign":
        pass 
        
        map_json = map_gen.get_level_data(current_campaign_level)
    else:
        map_json = map_gen.generate_new_map(difficulty=5)

    world = World(map_json, None, tile_imgs)
    world.process_data()
    
    if world.waypoints:
        last_pos = world.waypoints[-1]
        player_castle.rect.center = last_pos
    
    reset_game_logic()

def reset_game_logic():
    global enemy_group, turret_group, projectile_group, drop_group, text_group, waves_data, game_state, active_turret, game_start_time, game_over, level_complete
    game_over = False
    level_complete = False
    enemy_group.empty()
    turret_group.empty()
    projectile_group.empty()
    drop_group.empty()
    text_group.empty()
    
    game_state["money"] = c.START_MONEY
    game_state["lives"] = c.START_LIVES
    game_state["wave"] = 1
    game_state["charges"] = 0
    game_state["selected_turret"] = None
    game_state["game_speed"] = 0

    player_castle.update(c.START_LIVES)
    
    active_turret = None
    
    if current_game_mode == "campaign":
        waves_data = generate_wave(current_campaign_level, 1)
    else:
        waves_data = generate_wave(100, 1) 
        
    game_start_time = pg.time.get_ticks()
    audio_manager.play_music("game")

def generate_wave(level, wave_number):
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
        if wave_number > level + 2:
             return []
        
        count = 10 + (wave_number * 2)
        types = ["bat", "normal_slime", "goblin", "skeleton", "zombie", "ghost", "big_slime", "demon"]
        enemies = random.choices(types, k=count)

    return enemies

def create_turret(pos, type_name):
    mx, my = pos[0] // c.TILE_SIZE, pos[1] // c.TILE_SIZE
    if mx < 0 or mx >= c.COLS or my < 0 or my >= c.ROWS: return False
    idx = (my * c.COLS) + mx
    if world.tile_map[idx] != 0: return False 
    for t in turret_group:
        if t.tile_x == mx and t.tile_y == my: return False
    for t in turret_group:
        dist_x = abs(t.tile_x - mx); dist_y = abs(t.tile_y - my)
        if dist_x <= 1 and dist_y <= 1: return False 
    is_near_path = False
    for y in range(-1, 2):
        for x in range(-1, 2):
            neighbor_x = mx + x; neighbor_y = my + y
            if 0 <= neighbor_x < c.COLS and 0 <= neighbor_y < c.ROWS:
                neighbor_idx = (neighbor_y * c.COLS) + neighbor_x
                if 10 <= world.tile_map[neighbor_idx] <= 18: is_near_path = True; break
        if is_near_path: break
    if is_near_path: return False

    sound = audio_manager.get_sound(type_name)
    turret_group.add(Turret(turret_imgs[type_name], mx, my, proj_imgs[type_name], type_name, sound))
    audio_manager.play_sfx("build")
    return True

def draw_end_screen(screen, title, subtitle, font_large, font_small, buttons):
    screen.blit(end_overlay, (0, 0))

    t = font_large.render(title, True, "white")
    screen.blit(t, t.get_rect(center=(c.SCREEN_WIDTH//2, 160)))

    s = font_small.render(subtitle, True, "white")
    screen.blit(s, s.get_rect(center=(c.SCREEN_WIDTH//2, 195)))

    btn_w, btn_h = 260, 60
    gap = 18
    total_h = len(buttons) * btn_h + (len(buttons) - 1) * gap
    start_y = c.SCREEN_HEIGHT//2 - total_h//2 + 40

    mx, my = pg.mouse.get_pos()
    clicked = False
    for e in pg.event.get(pg.MOUSEBUTTONDOWN):
        if e.button == 1:
            clicked = True

    for i, (bid, text) in enumerate(buttons):
        rect = pg.Rect(c.SCREEN_WIDTH//2 - btn_w//2, start_y + i*(btn_h+gap), btn_w, btn_h)
        hover = rect.collidepoint(mx, my)
        color = "grey50" if hover else "grey25"

        pg.draw.rect(screen, color, rect, border_radius=14)
        pg.draw.rect(screen, "white", rect, 2, border_radius=14)

        txt = font_small.render(text, True, "white")
        screen.blit(txt, txt.get_rect(center=rect.center))

        if clicked and hover:
            return bid

    return None

def draw_stats_window(surface, data):
    overlay = pg.Surface((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 200)) 
    surface.blit(overlay, (0, 0))
    
    panel_w, panel_h = 500, 400
    panel_rect = pg.Rect((c.SCREEN_WIDTH + c.SIDE_PANEL) // 2 - panel_w // 2, 
                         c.SCREEN_HEIGHT // 2 - panel_h // 2, 
                         panel_w, panel_h)
    
    pg.draw.rect(surface, (45, 45, 50), panel_rect, border_radius=15)
    pg.draw.rect(surface, "gold", panel_rect, 3, border_radius=15)

    title = font_large.render("STATISTICS", True, "gold")
    surface.blit(title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 30))

    camp = data.get("campaign")
    c_title = font.render("CAMPAIGN", True, "cyan")
    surface.blit(c_title, (panel_rect.x + 50, panel_rect.y + 100))
    
    lvl_val = camp[0] if camp else 1
    time_val = int(camp[1]) if camp else 0
    
    txt_lvl = font.render(f"Max Level: {lvl_val}", True, "white")
    txt_time = font.render(f"Time Played: {time_val}s", True, "white")
    surface.blit(txt_lvl, (panel_rect.x + 70, panel_rect.y + 130))
    surface.blit(txt_time, (panel_rect.x + 70, panel_rect.y + 160))

    surv = data.get("survival")
    s_title = font.render("SURVIVAL", True, "orange")
    surface.blit(s_title, (panel_rect.x + 50, panel_rect.y + 220))
    
    wave_val = surv[0] if surv else 0
    s_time_val = int(surv[1]) if surv else 0
    
    txt_wave = font.render(f"Best Wave: {wave_val}", True, "white")
    txt_s_time = font.render(f"Best Time: {s_time_val}s", True, "white")
    surface.blit(txt_wave, (panel_rect.x + 70, panel_rect.y + 250))
    surface.blit(txt_s_time, (panel_rect.x + 70, panel_rect.y + 280))

    hint = font_small.render("Press ESC to Back", True, "grey")
    surface.blit(hint, (panel_rect.centerx - hint.get_width() // 2, panel_rect.bottom - 40))

in_settings = False
settings_menu = SettingsMenu(font_large, c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT, audio_manager)

run = True
while run:
    clock.tick(c.FPS)
    screen.fill("grey100")
    
    if in_menu:
        audio_manager.play_music("menu")
        video_bg.draw(screen)

        if in_stats:
            draw_stats_window(screen, stats_data)
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        audio_manager.play_sfx("click")
                        in_stats = False
        elif in_settings:
            action = settings_menu.draw(screen)
            
            if action == "back":
                audio_manager.play_sfx("click")
                in_settings = False
                
            for event in pg.event.get():
                if event.type == pg.QUIT: run = False
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    audio_manager.play_sfx("click")
                    in_settings = False
                settings_menu.handle_event(event)
        else:
            action = main_menu.draw(screen)

            if action == "campaign":
                audio_manager.play_sfx("click")
                in_menu = False   
                in_level_select = True

            elif action == "survival":
                audio_manager.play_sfx("click")
                in_menu = False
                start_game("survival")
            
            elif action == "stats":
                audio_manager.play_sfx("click")
                in_stats = True

                if player_id:
                    try:
                        stats_data["campaign"] = db.get_campaign_stats(player_id)
                        stats_data["survival"] = db.get_survival_stats(player_id)
                    except AttributeError:
                        print("Методи статистики ще не додані в DatabaseManager")

            elif action == "settings":
                audio_manager.play_sfx("click")
                in_settings = True

            elif action == "exit":
                audio_manager.play_sfx("click")
                run = False

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False

    elif in_level_select:
        audio_manager.play_music("menu")
        video_bg.draw(screen)

        choice = level_menu.draw(screen)

        if choice == "back":
            audio_manager.play_sfx("click")
            in_level_select = False
            in_menu = True

        elif isinstance(choice, int):
            audio_manager.play_sfx("click")
            current_campaign_level = choice
            in_level_select = False
            in_menu = False
            start_game("campaign")

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

    else:
        world.draw(screen)
        player_castle.draw(screen)
        
        if level_complete:
            btn = draw_end_screen(
                screen,
                "LEVEL COMPLETE!",
                f"Level {current_campaign_level} finished",
                font_large,
                font_small,
                buttons=[("next", "NEXT LEVEL"), ("retry", "RETRY"), ("menu", "MAIN MENU")]
            )
            if btn == "next":
                audio_manager.play_sfx("click")
                level_complete = False
                current_campaign_level += 1
                start_game("campaign")
            elif btn == "retry":
                audio_manager.play_sfx("click")
                level_complete = False
                start_game("campaign")
            elif btn == "menu":
                audio_manager.play_sfx("click")
                level_complete = False
                game_over = False
                in_level_select = False
                in_menu = True

        elif game_over:
            btn = draw_end_screen(
                screen,
                "GAME OVER",
                "Try again?",
                font_large,
                font_small,
                buttons=[("retry", "RETRY"), ("menu", "MAIN MENU")]
            )
            if btn == "retry":
                audio_manager.play_sfx("click")
                game_over = False
                start_game(current_game_mode)
            elif btn == "menu":
                audio_manager.play_sfx("click")
                level_complete = False
                game_over = False
                in_level_select = False
                in_menu = True

        
        if game_paused:
            for enemy in enemy_group: screen.blit(enemy.image, enemy.rect)
            for t in turret_group: screen.blit(t.image, t.rect)
            projectile_group.draw(screen)
            drop_group.draw(screen)
            text_group.draw(screen)
            ui.draw(screen, game_state)
            
            action = pause_menu.draw(screen)
            if action != 0: audio_manager.play_sfx("click")
            if action == 1: game_paused = False 
            elif action == 2: in_menu = True; game_paused = False 
            elif action == -1: run = False 
                
            for event in pg.event.get():
                if event.type == pg.QUIT: run = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE: game_paused = False

        else:
            if game_state["game_speed"] == 2: clock.tick(c.FPS * 2)

            if game_state["game_speed"] > 0:
                if not waves_data and len(enemy_group) == 0:
                    if pg.time.get_ticks() - last_wave_complete > WAVE_DELAY:
                        
                        game_state["wave"] += 1
                        
                        if current_game_mode == "campaign":
                            new_wave = generate_wave(current_campaign_level, game_state["wave"])
                        else:
                            new_wave = generate_wave(100, game_state["wave"])
                        
                        if new_wave:
                            waves_data = new_wave
                            last_spawn = pg.time.get_ticks()
                        else:
                            if current_game_mode == "campaign":
                                audio_manager.play_sfx("level_complete")
                                level_complete = True
                                game_state["game_speed"] = 0 
                            else:
                                pass

                else:
                    last_wave_complete = pg.time.get_ticks()

                if waves_data:
                    current_speed = game_state["game_speed"] if game_state["game_speed"] > 0 else 1
                    effective_cooldown = c.SPAWN_COOLDOWN / current_speed
                    if pg.time.get_ticks() - last_spawn > effective_cooldown:
                        enemy_type = waves_data.pop(0)
                        new_enemy = None
                        if enemy_type == "bat": new_enemy = Bat(world.waypoints, bat_img)
                        elif enemy_type == "big_slime": new_enemy = Big_slime(world.waypoints, big_slime_img)
                        elif enemy_type == "normal_slime": new_enemy = NormalSlime(world.waypoints, normal_slime_img)
                        elif enemy_type == "goblin": new_enemy = Goblin(world.waypoints, goblin_img)
                        elif enemy_type == "skeleton": new_enemy = Skeleton(world.waypoints, skeleton_img)
                        elif enemy_type == "zombie": new_enemy = Zombie(world.waypoints, zombie_img)
                        elif enemy_type == "ghost": new_enemy = Ghost(world.waypoints, ghost_img)
                        elif enemy_type == "demon": new_enemy = Demon(world.waypoints, demon_img)
                        elif enemy_type == "king_slime": new_enemy = KingSlime(world.waypoints, king_slime_img)
                        if new_enemy: enemy_group.add(new_enemy)
                        last_spawn = pg.time.get_ticks()

            loops = 0
            if game_state["game_speed"] == 1: loops = 1
            elif game_state["game_speed"] == 2: loops = 2
            if not game_over and not level_complete:
                for _ in range(loops):
                    enemy_group.update()
                    turret_group.update(projectile_group, enemy_group)
                    projectile_group.update()
                    drop_group.update()

                    hits = pg.sprite.groupcollide(enemy_group, projectile_group, False, True)
                    for enemy, projs in hits.items():
                        for proj in projs:
                            audio_manager.play_sfx("enemy_hit")
                            if proj.turret_type == "cannon":
                                enemy.health -= proj.damage
                                for other in enemy_group:
                                    if other != enemy and other.pos.distance_to(enemy.pos) < 60:
                                        other.health -= proj.damage * 0.5
                                        text_group.add(FloatingText("BOOM", other.rect.centerx, other.rect.centery, "orange"))
                            elif proj.turret_type == "ice":
                                enemy.health -= proj.damage
                                enemy.slow_down(0.5, 60)
                                text_group.add(FloatingText("SLOW", enemy.rect.centerx, enemy.rect.centery, "cyan"))
                            elif proj.turret_type == "poison":
                                enemy.health -= proj.damage
                                enemy.poison(2, 300)
                                text_group.add(FloatingText("POISON", enemy.rect.centerx, enemy.rect.centery, "green"))
                            else:
                                enemy.health -= proj.damage

                            if enemy.health <= 0:
                                audio_manager.play_sfx("enemy_death")
                                enemy.kill()
                                reward = enemy.reward
                                game_state["money"] += reward
                                text_group.add(FloatingText(f"+{reward}", enemy.rect.centerx, enemy.rect.centery, "gold"))
                                if random.random() < 0.1:
                                    drop_group.add(UpgradeDrop(upgrade_arrow, enemy.pos.x, enemy.pos.y))

                    for enemy in enemy_group:
                        if enemy.health == -100:
                            enemy.kill()
                            game_state["lives"] -= 1
                            audio_manager.play_sfx("base_hit")
                            player_castle.update(game_state["lives"])
                            text_group.add(FloatingText("-1 HP", c.SCREEN_WIDTH - 50, 50, "red"))
                            if game_state["lives"] <= 0: 
                                audio_manager.play_sfx("game_over")
                        
                                if player_id:
                                    time_played = (pg.time.get_ticks() - game_start_time) / 1000.0
                                    if current_game_mode == "survival":
                                        db.save_survival_score(player_id, game_state["wave"], time_played)
                                    else:
                                        db.save_campaign_progress(player_id, game_state["wave"], time_played)
                                
                                game_over = True
                                game_state["game_speed"] = 0

            for enemy in enemy_group:
                screen.blit(enemy.image, enemy.rect)
                if enemy.health < enemy.max_health:
                    ratio = max(0, enemy.health / enemy.max_health)
                    pg.draw.rect(screen, "red", (enemy.rect.centerx - 15, enemy.rect.top - 5, 30, 4))
                    pg.draw.rect(screen, "lime", (enemy.rect.centerx - 15, enemy.rect.top - 5, 30 * ratio, 4))
            
            for t in turret_group: 
                screen.blit(t.image, t.rect)
                lvl_text = font_small.render(f"Lv{t.upgrade_level}", True, "white")
                lvl_shadow = font_small.render(f"Lv{t.upgrade_level}", True, "black")
                text_pos = (t.rect.centerx - 10, t.rect.top - 15)
                screen.blit(lvl_shadow, (text_pos[0]+1, text_pos[1]+1))
                screen.blit(lvl_text, text_pos)
            
            text_group.update()
            projectile_group.draw(screen)
            drop_group.draw(screen)
            text_group.draw(screen)
            
            if active_turret: active_turret.draw_range(screen)
            ui.draw(screen, game_state)
            
            if game_state["selected_turret"]:
                mx, my = pg.mouse.get_pos()
                if mx < c.SCREEN_WIDTH:
                    pg.mouse.set_visible(False)
                    r = c.TURRET_DATA[game_state["selected_turret"]]["range"]
                    range_surf = pg.Surface((r * 2, r * 2), pg.SRCALPHA)
                    pg.draw.circle(range_surf, (255, 255, 255, 100), (r, r), r)
                    pg.draw.circle(range_surf, (255, 255, 255, 150), (r, r), r, 2)
                    screen.blit(range_surf, (mx - r, my - r))
                    img = turret_imgs[game_state["selected_turret"]]
                    screen.blit(img, img.get_rect(center=(mx, my)))
                else: pg.mouse.set_visible(True)
            else: pg.mouse.set_visible(True)

            upgrade_btn_rect = None
            sell_btn_rect = None
            
            if active_turret:
                btn_x = active_turret.rect.centerx - (c.BUTTON_WIDTH // 2)
                btn_y = active_turret.rect.centery + 35
                upgrade_btn_rect = pg.Rect(btn_x, btn_y, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
                if active_turret.upgrade_level >= 3:
                    btn_color = "grey40"; text_color = "white"; btn_text = "MAX"
                elif game_state["charges"] > 0:
                    btn_color = "darkgreen"; text_color = "white"; btn_text = "UPGRADE"
                else:
                    btn_color = "grey40"; text_color = "lightgrey"; btn_text = "UPGRADE"
                pg.draw.rect(screen, btn_color, upgrade_btn_rect, border_radius=5)
                pg.draw.rect(screen, "white", upgrade_btn_rect, 2, border_radius=5)
                text_surf = font_small.render(btn_text, True, text_color)
                screen.blit(text_surf, text_surf.get_rect(center=upgrade_btn_rect.center))
                
                base_cost = c.TURRET_DATA[active_turret.turret_type]["cost"]
                refund_amount = 0
                if active_turret.upgrade_level == 1: refund_amount = int(base_cost * 0.5)
                elif active_turret.upgrade_level == 2: refund_amount = int(base_cost * 0.75)
                elif active_turret.upgrade_level == 3: refund_amount = int(base_cost * 1.0)
                sell_btn_rect = pg.Rect(btn_x, btn_y + 35, c.BUTTON_WIDTH, c.BUTTON_HEIGHT)
                pg.draw.rect(screen, "darkred", sell_btn_rect, border_radius=5)
                pg.draw.rect(screen, "white", sell_btn_rect, 2, border_radius=5)
                sell_text = font_small.render(f"SELL {refund_amount}", True, "white")
                screen.blit(sell_text, sell_text.get_rect(center=sell_btn_rect.center))

            for event in pg.event.get():
                if event.type == pg.QUIT: run = False
                
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        game_paused = True

                if event.type == pg.MOUSEBUTTONDOWN:
                    mx, my = pg.mouse.get_pos()
                    if event.button == 1:
                        if ui.check_system_pause_click((mx, my)):
                            audio_manager.play_sfx("click")
                            game_paused = True
                            continue

                        new_speed = ui.check_speed_click((mx, my))
                        if new_speed is not None:
                            audio_manager.play_sfx("click")
                            game_state["game_speed"] = new_speed
                            continue

                        shop_item = ui.check_shop_click((mx, my))
                        if shop_item:
                            audio_manager.play_sfx("click")
                            if game_state["selected_turret"] == shop_item:
                                game_state["selected_turret"] = None
                                pg.mouse.set_visible(True)
                            else:
                                game_state["selected_turret"] = shop_item
                                active_turret = None
                                pg.mouse.set_visible(False)
                            continue 

                        if active_turret and upgrade_btn_rect and upgrade_btn_rect.collidepoint(mx, my):
                            if game_state["charges"] > 0 and active_turret.upgrade_level < 3:
                                audio_manager.play_sfx("build")
                                game_state["charges"] -= 1
                                active_turret.upgrade()
                                text_group.add(FloatingText("UPGRADED!", mx, my, "gold"))
                            else:
                                audio_manager.play_sfx("click")
                            continue
                        
                        if active_turret and sell_btn_rect and sell_btn_rect.collidepoint(mx, my):
                            audio_manager.play_sfx("destroy")
                            base_cost = c.TURRET_DATA[active_turret.turret_type]["cost"]
                            refund = 0
                            if active_turret.upgrade_level == 1: refund = int(base_cost * 0.5)
                            elif active_turret.upgrade_level == 2: refund = int(base_cost * 0.75)
                            elif active_turret.upgrade_level == 3: refund = int(base_cost * 1.0)
                            game_state["money"] += refund
                            text_group.add(FloatingText(f"+{refund}", mx, my, "gold"))
                            active_turret.kill()
                            active_turret = None
                            continue

                        if mx < c.SCREEN_WIDTH:
                            is_busy = (game_state["selected_turret"] is not None) or (active_turret is not None)
                            clicked_drop = False
                            if not is_busy:
                                for drop in drop_group:
                                    if drop.rect.collidepoint(mx, my):
                                        audio_manager.play_sfx("click")
                                        if game_state["charges"] < c.MAX_UPGRADES:
                                            game_state["charges"] += 1
                                            drop.kill()
                                            text_group.add(FloatingText("+1 CHARGE", mx, my, "lime"))
                                        else:
                                            text_group.add(FloatingText("FULL!", mx, my, "red"))
                                        clicked_drop = True
                            
                            if not clicked_drop:
                                if game_state["selected_turret"]:
                                    cost = c.TURRET_DATA[game_state["selected_turret"]]["cost"]
                                    if game_state["money"] >= cost:
                                        if create_turret((mx, my), game_state["selected_turret"]):
                                            game_state["money"] -= cost
                                            text_group.add(FloatingText(f"-{cost}", mx, my, "red"))
                                        else:
                                            audio_manager.play_sfx("click")
                                            text_group.add(FloatingText("Invalid!", mx, my, "red"))
                                    else:
                                        audio_manager.play_sfx("click")
                                        text_group.add(FloatingText("No Money", mx, my, "red"))
                                else:
                                    active_turret = None
                                    for t in turret_group:
                                        if t.rect.collidepoint(mx, my):
                                            audio_manager.play_sfx("click")
                                            active_turret = t
                                            break
                    
                    if event.button == 3:
                        if game_state["selected_turret"]:
                            game_state["selected_turret"] = None
                            pg.mouse.set_visible(True)
                        elif active_turret:
                            active_turret = None

    pg.display.flip()

pg.quit()