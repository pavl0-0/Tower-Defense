import pygame as pg
import os

class AudioManager:
    def __init__(self):
        self.music_volume = 0.5
        self.sfx_volume = 0.5

        if not pg.mixer.get_init():
            pg.mixer.pre_init(44100, -16, 2, 512)
            pg.mixer.init()
            pg.mixer.set_num_channels(64)

        self.sounds = {}     
        self.base_volumes = {} 
        
        self.music_files = {}
        self.current_music = None
        
        self.load_assets()

    def load_assets(self):
        sfx_data = {
            "click":     ("assets/audio/button_click.wav", 0.5),
            "build":     ("assets/audio/tower_build.mp3", 0.6),
            "destroy":   ("assets/audio/tower_destroy.mp3", 0.6),
            "victory":   ("assets/audio/victory.mp3", 0.6),
            "game_over": ("assets/audio/game_over.mp3", 0.6),
            "base_hit":    ("assets/audio/myself_hit.mp3", 0.8),
            "enemy_hit":   ("assets/audio/enemy_hit.mp3", 0.6), 
            "enemy_death": ("assets/audio/enemy_death.mp3", 0.6),
            "level_complete": ("assets/audio/victory.mp3", 0.6),

            "archer":    ("assets/audio/shot_archer.mp3", 0.2),
            "crossbow":  ("assets/audio/shot_crossbow.mp3", 0.3),
            "cannon":    ("assets/audio/shot_cannon.mp3", 0.4),
            "ice":       ("assets/audio/shot_ice.mp3", 0.4),
            "poison":    ("assets/audio/shot_poison.mp3", 0.4),
            "lightning": ("assets/audio/shot_lightning.mp3", 0.4),
        }

        print("--- ЗАВАНТАЖЕННЯ АУДІО ---")
        for name, (path, base_vol) in sfx_data.items():
            if os.path.exists(path):
                try:
                    sound = pg.mixer.Sound(path)
                    sound.set_volume(base_vol * self.sfx_volume)
                    
                    self.sounds[name] = sound
                    self.base_volumes[name] = base_vol 
                    print(f"✅ Завантажено: {name}")
                except Exception as e:
                    print(f"⚠️ Помилка файлу {path}: {e}")
                    self.sounds[name] = None
            else:
                print(f"⚠️ Не знайдено файл: {path}")
                self.sounds[name] = None 

        self.music_files = {
            "menu": "assets/audio/menu.mp3",
            "game": "assets/audio/game_music.mp3"
        }

    def set_music_volume(self, volume):
        """Оновлює гучність музики"""
        self.music_volume = volume
        pg.mixer.music.set_volume(volume)

    def set_sfx_volume(self, volume):
        """Оновлює гучність ефектів, зберігаючи баланс"""
        self.sfx_volume = volume
        
        for name, sound in self.sounds.items():
            if sound:
                base = self.base_volumes.get(name, 1.0)
                new_vol = base * self.sfx_volume
                sound.set_volume(new_vol)

    def play_sfx(self, name):
        """Програти звук"""
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()

    def get_sound(self, name):
        """Отримати об'єкт звуку"""
        return self.sounds.get(name, None)

    def play_music(self, track_name):
        """Запустити музику"""
        if self.current_music == track_name:
            return
        
        path = self.music_files.get(track_name)
        if path and os.path.exists(path):
            try:
                pg.mixer.music.load(path)
                pg.mixer.music.set_volume(self.music_volume)
                pg.mixer.music.play(-1)
                self.current_music = track_name
            except Exception as e:
                print(f"Помилка музики: {e}")
        else:
            print(f"Музику не знайдено: {track_name}")