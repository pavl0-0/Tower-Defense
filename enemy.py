import pygame as pg
from pygame.math import Vector2
import constants as c

class Enemy(pg.sprite.Sprite):
    def __init__(self, waypoints, sprite_sheet, original_health, speed, reward):
        pg.sprite.Sprite.__init__(self)
        self.waypoints = waypoints
        self.pos = Vector2(self.waypoints[0])
        self.target_waypoint = 1
        
        self.health = original_health
        self.max_health = original_health
        self.speed = speed
        self.original_speed = speed
        self.reward = reward
        
        self.slow_timer = 0
        self.poison_timer = 0
        self.poison_damage = 0

        self.animation_frames = []
        self.current_frame_index = 0
        self.animation_speed_ms = 100
        self.last_animation_update = pg.time.get_ticks()
        self.flip = False
        
        FRAME_COUNT = 4
        sheet_width = sprite_sheet.get_width()
        sheet_height = sprite_sheet.get_height()
        frame_width = sheet_width // FRAME_COUNT
        
        self.load_animation_frames(sprite_sheet, frame_width, sheet_height, FRAME_COUNT)
        
        self.image = self.animation_frames[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.movement = Vector2(0, 0)

    def load_animation_frames(self, sprite_sheet, width, height, frames):
        self.animation_frames = []
        for i in range(frames):
            x = i * width
            frame_rect = pg.Rect(x, 0, width, height)
            try:
                frame = sprite_sheet.subsurface(frame_rect)
                self.animation_frames.append(frame)
            except ValueError:
                pass

    def update(self):
        self.move()
        self.animate()
        self.check_alive()
        self.handle_status_effects()

    def handle_status_effects(self):
        if self.slow_timer > 0:
            self.slow_timer -= 1
        else:
            self.speed = self.original_speed
            
        if self.poison_timer > 0:
            self.poison_timer -= 1
            if self.poison_timer % 60 == 0:
                self.health -= self.poison_damage

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.last_animation_update > self.animation_speed_ms:
            self.last_animation_update = now
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
            base_image = self.animation_frames[self.current_frame_index]
            if self.flip:
                self.image = pg.transform.flip(base_image, True, False)
            else:
                self.image = base_image
            self.rect = self.image.get_rect(center=self.pos)

    def move(self):
        if self.target_waypoint >= len(self.waypoints):
            self.health = -100
            return

        self.target = Vector2(self.waypoints[self.target_waypoint])
        self.movement = self.target - self.pos
        dist = self.movement.length()

        if self.movement.x < 0: self.flip = True
        elif self.movement.x > 0: self.flip = False

        if dist >= self.speed:
            self.pos += self.movement.normalize() * self.speed
        else:
            if dist != 0: self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1
        
        self.rect.center = self.pos

    def check_alive(self):
        if self.health <= 0 and self.health != -100:
            self.kill()

    def slow_down(self, factor, duration):
        self.speed = self.original_speed * (1 - factor)
        self.slow_timer = duration

    def poison(self, damage, duration):
        self.poison_damage = damage
        self.poison_timer = duration


class NormalSlime(Enemy):
    def __init__(self, waypoints, sheet):
        super().__init__(waypoints, sheet, original_health=10, speed=1.5, reward=5)

class Bat(Enemy):
    def __init__(self, waypoints, sheet):
        super().__init__(waypoints, sheet, original_health=15, speed=3, reward=10)

class Goblin(Enemy):
    def __init__(self, waypoints, sheet):
        super().__init__(waypoints, sheet, original_health=20, speed=2.5, reward=15)

class Skeleton(Enemy):
    def __init__(self, waypoints, sheet):
        super().__init__(waypoints, sheet, original_health=30, speed=2.0, reward=20)

class Ghost(Enemy):
    def __init__(self, waypoints, sheet):
        super().__init__(waypoints, sheet, original_health=25, speed=3.5, reward=30)

class Big_slime(Enemy):
    def __init__(self, waypoints, sheet):
        super().__init__(waypoints, sheet, original_health=35, speed=1.5, reward=25)

class Zombie(Enemy):
    def __init__(self, waypoints, sheet):
        super().__init__(waypoints, sheet, original_health=50, speed=1.0, reward=35)

class Demon(Enemy):
    def __init__(self, waypoints, sheet):
        super().__init__(waypoints, sheet, original_health=100, speed=1.8, reward=100)

class KingSlime(Enemy):
    def __init__(self, waypoints, sheet):
        super().__init__(waypoints, sheet, original_health=400, speed=0.7, reward=400)