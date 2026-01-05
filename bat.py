import pygame as pg
from enemy import Enemy

class Bat(Enemy):
    def __init__(self, waypoints, sprite_sheet):
        super().__init__(waypoints, health=5)
        
        self.speed = 2.5
        self.animation_speed_ms = 100
        
        self.load_animation_frames(
            sprite_sheet_image=sprite_sheet,
            frame_width=10,
            frame_height=7,
            num_frames=4
        )
        
        self.image = self.animation_frames[self.current_frame_index]
        self.rect = self.image.get_rect(center=self.pos)