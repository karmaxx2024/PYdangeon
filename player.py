import os

import pygame
from settings import *

KNIGHT_IMAGE = os.path.join("assets", "images", "player", "knight.jpg")


def _load_sprite(path, max_side):
    if not path or not os.path.exists(path):
        return None
    img = pygame.image.load(path).convert()
    # JPG без альфа-канала: чёрный фон спрайта делаем прозрачным
    img.set_colorkey((0, 0, 0), pygame.RLEACCEL)
    w, h = img.get_size()
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
    return img


class Player:
    def __init__(self, x, y, char_data):
        self.x = float(x)
        self.y = float(y)
        self.speed = char_data["speed"]
        self.max_hp = char_data["hp"]
        self.hp = char_data["hp"]
        self.attack = char_data["attack"]
        self.color = char_data["color"]
        self.name = char_data["name"]

        image_path = char_data.get("image")
        self.image = _load_sprite(image_path, 96) if image_path else None
        self.size = 16
        if self.image:
            self.size = max(self.image.get_width(), self.image.get_height()) // 2
        elif image_path:
            print("Нет картинки:", image_path)

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

        half = self.size
        self.x = max(half, min(screen_w - half, self.x))
        self.y = max(half, min(screen_h - half, self.y))

    def draw(self, screen):
        cx = int(self.x)
        cy = int(self.y)
        half = self.size

        if self.image:
            rect = self.image.get_rect(center=(cx, cy))
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, self.color, (cx, cy), half)

        bar_w = 50
        bar_h = 7
        bar_x = cx - bar_w // 2
        bar_y = cy - half - 16

        pygame.draw.rect(screen, (80, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        hp_fill = int(bar_w * self.hp / self.max_hp)
        pygame.draw.rect(screen, (220, 50, 50), (bar_x, bar_y, hp_fill, bar_h), border_radius=3)
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

    def draw_hud(self, screen, font):
        hp_text = font.render(f"{self.name}   HP: {self.hp} / {self.max_hp}", True, WHITE)
        screen.blit(hp_text, (16, 16))
