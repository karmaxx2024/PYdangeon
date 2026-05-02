# tilemap.py

import pygame

class TileMap:
    def __init__(self):
        self.tile_size = 32
        
    def draw(self, screen):
        # Просто заполняем экран чёрным цветом для теста
        screen.fill((0, 0, 0))