import pygame as pg
import math
import constants as c

class Projectile(pg.sprite.Sprite):
    def __init__(self, image, position, target, damage, turret_type):
        pg.sprite.Sprite.__init__(self)
        self.image_original = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        self.pos = pg.math.Vector2(position)
        
        self.target = target
        self.damage = damage
        self.turret_type = turret_type
        self.speed = 10 

    def update(self):
        if self.target.health <= 0:
            self.kill()
            return

        target_center = pg.math.Vector2(self.target.rect.center)
        direction = target_center - self.pos
        
        dist = direction.length()

        if dist <= self.speed:
            self.pos = target_center
            self.rect.center = self.pos
        else:
            direction.normalize_ip()
            self.pos += direction * self.speed
            self.rect.center = self.pos

            angle = math.degrees(math.atan2(-direction.y, direction.x))
            
            self.image = pg.transform.rotate(self.image_original, angle - 90)
            
            self.rect = self.image.get_rect(center=self.rect.center)

        if self.rect.right < 0 or self.rect.left > c.SCREEN_WIDTH or \
           self.rect.bottom < 0 or self.rect.top > c.SCREEN_HEIGHT:
            self.kill()