# import pygame as pg

# pg.init()

# try:
#     info = pg.display.Info()
#     SCREEN_WIDTH = info.current_w
#     SCREEN_HEIGHT = info.current_h
# except pg.error:
#     SCREEN_WIDTH = 1280
#     SCREEN_HEIGHT = 720
ROWS = 32
COLS = 32
TILE_SIZE = 16
SIDE_PANEL = 300
SCREEN_WIDTH = TILE_SIZE * COLS
SCREEN_HEIGHT = TILE_SIZE * ROWS
FPS = 60
MAX_UPGRADES = 4
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 30

START_MONEY = 1000
START_LIVES = 15

SPAWN_COOLDOWN = 1200

TURRET_DATA = {
    "archer": {
        "cost": 200,   
        "range": 100,   
        "cooldown": 700, 
        "damage": 3,
        "slow_factor": 0
    },
    "crossbow": {
        "cost": 500,    
        "range": 180,  
        "cooldown": 1500, 
        "damage": 15, 
        "slow_factor": 0
    },
    "cannon": { 
        "cost": 800,
        "range": 130,
        "cooldown": 2000, 
        "damage": 30,  
        "slow_factor": 0
    },
    "ice": {
        "cost": 600,
        "range": 110,
        "cooldown": 1200,
        "damage": 3,
        "slow_factor": 1
    },
    "poison": {
        "cost": 700,
        "range": 110,
        "cooldown": 1000,
        "damage": 2,
        "slow_factor": 0.5
    },
    "lightning": {
        "cost": 1200,
        "range": 140,
        "cooldown": 200,
        "damage": 1,
        "slow_factor": 0
    }
}