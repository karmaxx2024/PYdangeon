import os
import pygame
import random
from settings import *

TILE_WALL = 0
TILE_FLOOR = 1
TILE_DOOR = 2
TILE_STAIRS = 3
TILE_TRAP = 4

WALL_IMAGE = os.path.join("assets", "images", "decorations", "wall.jpg")
FLOOR_IMAGE_CANDIDATES = [
    os.path.join("assets", "images", "decorations", "floor.jpg"),
    os.path.join("assets", "images", "decorations", "floor2.jpg"),  # второй вариант пола
]


def _resolve_floor_path(path=None):
    if path and os.path.exists(path):
        return path
    for candidate in FLOOR_IMAGE_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    return path or FLOOR_IMAGE_CANDIDATES[0]


def load_wall_tile(tile_size=TILE_SIZE):
    """Загружает текстуру стены"""
    if not os.path.exists(WALL_IMAGE):
        print("Нет стены:", WALL_IMAGE)
        return None
    
    wall_img = pygame.image.load(WALL_IMAGE).convert()
    return pygame.transform.scale(wall_img, (tile_size, tile_size))


def load_floor_tile(path=None, tile_size=TILE_SIZE, col=0, row=0):
    """
    Один маленький тайл для замощения экрана.
    - Большая картинка без сетки → ужимаем целиком до tile_size.
    - Лист с сеткой (ширина и высота кратны tile_size) → вырезаем клетку (col, row).
    """
    path = _resolve_floor_path(path)
    if not os.path.exists(path):
        print("Нет пола:", path)
        return None

    sheet = pygame.image.load(path).convert()
    sheet_w, sheet_h = sheet.get_size()

    is_tileset = (
        sheet_w >= tile_size * 2
        and sheet_h >= tile_size * 2
        and sheet_w % tile_size == 0
        and sheet_h % tile_size == 0
    )

    if is_tileset:
        x = col * tile_size
        y = row * tile_size
        tile = sheet.subsurface((x, y, tile_size, tile_size)).copy()
    else:
        tile = pygame.transform.scale(sheet, (tile_size, tile_size))

    print(f"✓ Пол: {path} → тайл {tile.get_size()}")
    return tile


def draw_floor(screen, floor_tile):
    """Рисует пол (только пол, без стен)"""
    if not floor_tile:
        screen.fill((20, 12, 30))
        return
    sw, sh = screen.get_size()
    tw, th = floor_tile.get_size()
    for y in range(0, sh, th):
        for x in range(0, sw, tw):
            screen.blit(floor_tile, (x, y))


def draw_walls(screen, wall_tile, map_width, map_height, camera_x=0, camera_y=0):
    """
    Рисует стены по периметру карты.
    map_width, map_height - размеры карты в тайлах
    camera_x, camera_y - смещение камеры
    """
    if not wall_tile:
        # Если нет текстуры стены, рисуем серые прямоугольники
        wall_color = (80, 80, 80)
        for x in range(map_width):
            for y in range(map_height):
                if x == 0 or x == map_width-1 or y == 0 or y == map_height-1:
                    screen_x = x * TILE_SIZE - camera_x
                    screen_y = y * TILE_SIZE - camera_y
                    pygame.draw.rect(screen, wall_color, 
                                   (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
        return
    
    # Рисуем стены по периметру
    for x in range(map_width):
        for y in range(map_height):
            # Если клетка на границе карты - это стена
            if x == 0 or x == map_width-1 or y == 0 or y == map_height-1:
                screen_x = x * TILE_SIZE - camera_x
                screen_y = y * TILE_SIZE - camera_y
                screen.blit(wall_tile, (screen_x, screen_y))


def draw_tilemap(screen, floor_tile, wall_tile, map_width, map_height, camera_x=0, camera_y=0):
    """
    Рисует пол и стены на карте.
    Используйте эту функцию для отрисовки всего уровня.
    """
    # Сначала рисуем пол
    draw_floor(screen, floor_tile)
    # Затем рисуем стены поверх
    draw_walls(screen, wall_tile, map_width, map_height, camera_x, camera_y)


class Room:

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

    def interpects(self, other):
        return (
                self.x <= other.x2 + 1 and
                self.x2 >= other.x - 1 and
                self.y <= other.y2 + 1 and
                self.y2 >= other.y - 1
        )

    def random_floor_point(self):
        rx = random.randint(self.x + 1, self.x2 - 2)
        ry = random.randint(self.y + 1, self.y2 - 2)
        return rx, ry


class BSPLeaf:
    MIN_SIZE = 7

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.left = None
        self.right = None
        self.room = None

    def split(self):
        if self.left is not None:
            return False

        if self.w > self.h * 1.25:
            split_horizontal = False
        elif self.h > self.w * 1.25:
            split_horizontal = True
        else:
            split_horizontal = random.choice([True, False])

        if split_horizontal:
            max_split = self.h - self.MIN_SIZE
            if max_split <= self.MIN_SIZE:
                return False
            split_at = random.randint(self.MIN_SIZE, max_split)

            self.left = BSPLeaf(self.x, self.y, self.w, split_at)
            self.right = BSPLeaf(self.x, self.y + split_at, self.w, self.h - split_at)

        else:
            max_split = self.w - self.MIN_SIZE
            if max_split <= self.MIN_SIZE:
                return False
            split_at = random.randint(self.MIN_SIZE, max_split)

            self.left = BSPLeaf(self.x, self.y, split_at, self.h)
            self.right = BSPLeaf(self.x + split_at, self.y, self.w - split_at, self.h)

        return True
