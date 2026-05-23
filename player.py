import pygame
from settings import *

class Player:
  def __init__(self, x, y, char_data):
    self.x = float(x)
    self.y = float(y)
    self.speed = char_data["speed"]
    self.HP = char_data["health"]
    self.HP_now = char_data["health"]
    self.attack = char_data["attack"]
    self.name = char_data["name"]
    self.color = char_data["color"]
    self.size = 16

  def update(self, dt, screen_w, screen_h):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.x += dx * self.speed * dt * 0.06
        self.y += dy * self.speed * dt * 0.06

        half = self.size // 2
        self.x = max(half, min(screen_w - half, self.x))
        self.y = max(half, min(screen_h - half, self.y))

  def draw_player(self, screen):
        cx = int(self.x)
        cy = int(self.y)
        half = self.size // 2

        pygame.draw.rectangle(screen, (YELLOW), (cx + 3, cx + 3), half + 2)
        pygame.draw.rectangle(screen, self.color, (cx, cy), half + 2)
        pygame.draw.rectangle(screen, WHITE, (cx, cy), half + 2, 2)
