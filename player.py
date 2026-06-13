import os
import pygame
from settings import *

KNIGHT_IMAGE = os.path.join("assets", "images", "player", "knight.jpg")


def _load_sprite(path, max_side):
    """Загружает и масштабирует спрайт"""
    if not path or not os.path.exists(path):
        return None
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
    return img


class Player:
    def __init__(self, x, y, char_data):
        """
        Создаёт игрока
        
        Args:
            x, y: начальная позиция в пикселях
            char_data: словарь с данными персонажа (speed, hp, attack, color, name, image)
        """
        self.x = float(x)
        self.y = float(y)
        self.speed = char_data["speed"]
        self.max_hp = char_data["hp"]
        self.hp = char_data["hp"]
        self.attack = char_data["attack"]
        self.color = char_data["color"]
        self.name = char_data["name"]

        # Загружаем спрайт
        image_path = char_data.get("image")
        self.image = _load_sprite(image_path, 96) if image_path else None
        self.size = 16  # радиус/половина размера игрока
        
        if self.image:
            self.size = max(self.image.get_width(), self.image.get_height()) // 2
        elif image_path:
            print("Нет картинки:", image_path)
        
        # Создаём прямоугольник для коллизий
        self.rect = pygame.Rect(0, 0, self.size * 2, self.size * 2)
        self.rect.center = (int(self.x), int(self.y))
        
        print(f"✓ Игрок {self.name} создан. Скорость: {self.speed}, Размер: {self.rect.size}")

    def update(self, dt, screen_w, screen_h):
        """
        Старый метод - только для границ экрана (оставлен для совместимости)
        Используется только в меню и других местах, где нет карты мира
        """
        keys = pygame.key.get_pressed()  # <-- ЭТО СТРОКА БЫЛА ПРОПУЩЕНА!

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

        # Нормализация диагонального движения
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        # Движение
        self.x += dx * self.speed * dt * 0.06
        self.y += dy * self.speed * dt * 0.06

        # Границы экрана
        half = self.size
        self.x = max(half, min(screen_w - half, self.x))
        self.y = max(half, min(screen_h - half, self.y))
        
        # Обновляем прямоугольник
        self.rect.center = (int(self.x), int(self.y))

    def update_with_collision(self, dt, keys, world_map, is_paused=False):
        """Движение с коллизиями (с поддержкой паузы)"""
        if is_paused:
            return  # Не двигаемся на паузе
        """Новый метод - движение с коллизиями на карте мира
        Используется в основной игре"""
        # Вычисляем направление
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

        # Нормализуем диагональное движение
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        # Скорость в пикселях в секунду
        move_distance = self.speed * dt
        
        # Пробуем движение по X
        test_rect = self.rect.move(dx * move_distance, 0)
        if not world_map.check_collision(test_rect, 0, 0):
            self.rect.x += dx * move_distance
        
        # Пробуем движение по Y
        test_rect = self.rect.move(0, dy * move_distance)
        if not world_map.check_collision(test_rect, 0, 0):
            self.rect.y += dy * move_distance
        
        # Обновляем float координаты для совместимости со старыми методами
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)

    def draw(self, screen):
        """
        Отрисовка игрока без камеры (старый метод)
        Используется в меню и других местах
        """
        cx = int(self.x)
        cy = int(self.y)
        half = self.size

        if self.image:
            rect = self.image.get_rect(center=(cx, cy))
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, self.color, (cx, cy), half)

        # Полоска HP
        bar_w = 50
        bar_h = 7
        bar_x = cx - bar_w // 2
        bar_y = cy - half - 16

        pygame.draw.rect(screen, (80, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        hp_fill = int(bar_w * self.hp / self.max_hp)
        pygame.draw.rect(screen, (220, 50, 50), (bar_x, bar_y, hp_fill, bar_h), border_radius=3)
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
    
    def draw_with_camera(self, screen, camera_x, camera_y):
        """
        Отрисовка игрока с учётом камеры
        Используется в основной игре
        """
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        if self.image:
            rect = self.image.get_rect(center=(screen_x + self.size, screen_y + self.size))
            screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, self.color, (screen_x + self.size, screen_y + self.size), self.size)
        
        # Полоска HP (относительно камеры)
        bar_w = 50
        bar_h = 7
        bar_x = screen_x + self.size - bar_w // 2
        bar_y = screen_y - 16

        pygame.draw.rect(screen, (80, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        hp_fill = int(bar_w * self.hp / self.max_hp)
        pygame.draw.rect(screen, (220, 50, 50), (bar_x, bar_y, hp_fill, bar_h), border_radius=3)
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

    def draw_hud(self, screen, font):
        """Рисует HUD (интерфейс) с информацией о игроке"""
        hp_text = font.render(f"{self.name}   HP: {self.hp} / {self.max_hp}", True, WHITE)
        screen.blit(hp_text, (16, 16))
    
    def take_damage(self, damage):
        """Наносит урон игроку"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"{self.name} получил {damage} урона! HP: {self.hp}/{self.max_hp}")
        return self.hp <= 0  # Возвращает True если игрок умер
    
    def heal(self, amount):
        """Лечит игрока"""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        print(f"{self.name} вылечился на {amount}. HP: {self.hp}/{self.max_hp}")
    
    def get_rect(self):
        """Возвращает прямоугольник игрока для коллизий"""
        return self.rect
    
    def is_alive(self):
        """Проверяет, жив ли игрок"""
        return self.hp > 0
