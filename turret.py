import pygame as pg
import math
import constants as c
from projectile import Projectile

class Turret(pg.sprite.Sprite):
    def __init__(self, image, tile_x, tile_y, shot_image, turret_type, shot_sound):
        pg.sprite.Sprite.__init__(self)
        self.upgrade_level = 1
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.turret_type = turret_type
        
        data = c.TURRET_DATA[self.turret_type]
        self.range = data["range"]
        self.cooldown = data["cooldown"]
        self.damage = data["damage"]
        
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE

        self.shot_sound = shot_sound
        
        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        self.shot_image = shot_image
        self.last_shot = pg.time.get_ticks()
        self.target = None

    def update(self, projectile_group, enemy_group):
        self.pick_target(enemy_group)
        if self.target:
            if pg.time.get_ticks() - self.last_shot > self.cooldown:
                self.shoot(projectile_group)

    def pick_target(self, enemy_group):
        for enemy in enemy_group:
            if enemy.health > 0:
                dist = math.sqrt((enemy.pos.x - self.x)**2 + (enemy.pos.y - self.y)**2)
                if dist < self.range:
                    self.target = enemy
                    return 
        self.target = None

    def shoot(self, projectile_group):
        proj = Projectile(self.shot_image, self.rect.center, self.target, self.damage, self.turret_type)
        projectile_group.add(proj)
        self.last_shot = pg.time.get_ticks()
        if self.shot_sound:
            self.shot_sound.play()

    def draw_range(self, surface):
        range_surf = pg.Surface((self.range * 2, self.range * 2), pg.SRCALPHA)
        
        pg.draw.circle(range_surf, (255, 255, 255, 50), (self.range, self.range), self.range)
        
        pg.draw.circle(range_surf, (255, 255, 255, 100), (self.range, self.range), self.range, 2)
        
        surface.blit(range_surf, (self.rect.centerx - self.range, self.rect.centery - self.range))

    def upgrade(self):
        if self.upgrade_level < 3:
            self.upgrade_level += 1
            self.range *= 1.1
            self.cooldown /= 1.15
            self.damage *= 1.2
            
            self.image = self.original_image.copy()
            
            if self.upgrade_level == 2:
                tint = pg.Surface(self.image.get_size(), pg.SRCALPHA)
                tint.fill((50, 50, 50, 0)) 
                self.image.blit(tint, (0, 0), special_flags=pg.BLEND_RGBA_ADD)
                
            elif self.upgrade_level == 3:
                tint = pg.Surface(self.image.get_size(), pg.SRCALPHA)
                tint.fill((100, 50, 0, 0)) 
                self.image.blit(tint, (0, 0), special_flags=pg.BLEND_RGBA_ADD)