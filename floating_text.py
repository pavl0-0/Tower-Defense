import pygame as pg

class FloatingText(pg.sprite.Sprite):
    def __init__(self, text, x, y, color="white", size=20):
        pg.sprite.Sprite.__init__(self)
        
        self.font = pg.font.SysFont("Arial", size, bold=True)
        
        self.image_text = self.font.render(text, True, color)
        self.image_shadow = self.font.render(text, True, "black")
        
        width = self.image_text.get_width() + 2
        height = self.image_text.get_height() + 2
        self.image = pg.Surface((width, height), pg.SRCALPHA)
        
        self.image.blit(self.image_shadow, (2, 2)) 
        self.image.blit(self.image_text, (0, 0))   
        
        self.rect = self.image.get_rect(center=(x, y))
        
        self.timer = 0
        self.max_time = 60 
        self.speed_y = -1  

    def update(self):
        self.rect.y += self.speed_y 
        self.timer += 1
        
        if self.timer > 30:
            alpha = 255 - ((self.timer - 30) * (255 // 30))
            if alpha < 0: alpha = 0
            self.image.set_alpha(alpha)

        if self.timer >= self.max_time:
            self.kill()