import pygame as pg
from pygame.math import Vector2
import math

class UpgradeDrop(pg.sprite.Sprite):
    def __init__(self, image, x, y):
        pg.sprite.Sprite.__init__(self)

        SCALE_FACTOR = 1.5  
        new_width = int(image.get_width() * SCALE_FACTOR)
        new_height = int(image.get_height() * SCALE_FACTOR)
        self.image = pg.transform.scale(image, (new_width, new_height))
        
        self.original_image = self.image.copy()

        self.rect = self.image.get_rect(center=(x, y))

        self.initial_y = y   
        self.lifetime = 0        
        self.floating_amplitude = 8 
        self.floating_speed = 0.08 

        self.spawn_time = pg.time.get_ticks() 
        self.total_life = 5000  
        self.blink_start = 2000 

    def update(self):
        self.lifetime += 1
        offset = math.sin(self.lifetime * self.floating_speed) * self.floating_amplitude
        self.rect.centery = self.initial_y + offset

        now = pg.time.get_ticks()
        age = now - self.spawn_time

        if age > self.total_life:
            self.kill()
            return

        if age > self.blink_start:
            if (now // 200) % 2 == 0:
                self.image.set_alpha(100) 
            else:
                self.image.set_alpha(255) 
        else:
            self.image.set_alpha(255)