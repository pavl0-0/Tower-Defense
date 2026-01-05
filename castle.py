import pygame as pg

class Castle(pg.sprite.Sprite):
    def __init__(self, image_path, x, y, max_lives):
        pg.sprite.Sprite.__init__(self)
        
        self.sprite_sheet = pg.image.load(image_path).convert_alpha()
        self.frame_width = self.sprite_sheet.get_width() // 4
        self.frame_height = self.sprite_sheet.get_height()
        
        self.frames = []
        for i in range(4):
            frame = self.sprite_sheet.subsurface(i * self.frame_width, 0, self.frame_width, self.frame_height)
            self.frames.append(frame)
            
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.max_lives = max_lives

    def update(self, current_lives):
        if current_lives <= 0:
            self.image = self.frames[3]
        else:
            percent = current_lives / self.max_lives
            if percent > 0.75:
                self.image = self.frames[0]
            elif percent > 0.50:
                self.image = self.frames[1]
            elif percent > 0.25:
                self.image = self.frames[2]
            else:
                self.image = self.frames[3]

    def draw(self, surface):
        surface.blit(self.image, self.rect)