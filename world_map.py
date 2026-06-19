import pygame
import random
from settings import TILE_SIZE

class Room:
    """Комната в подземелье"""
    def __init__(self, x, y, w, h):
        self.x = x  # позиция в тайлах
        self.y = y
        self.w = w  # ширина в тайлах
        self.h = h  # высота в тайлах
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, w * TILE_SIZE, h * TILE_SIZE)
        self.center = (x + w // 2, y + h // 2)
    
    def is_big(self, threshold=10):
        """Проверяет, является ли комната большой"""
        return self.w >= threshold or self.h >= threshold

    def get_size_category(self):    
        """Возвращает категорию размера комнаты"""
        if self.w >= 10 or self.h >= 10:
            return "big"
        elif self.w <= 6 or self.h <= 6:
            return "small"
        else:
            return "medium"

    def intersects(self, other, margin=2):
        """Проверяет пересечение с другой комнатой"""
        return not (self.x + self.w + margin < other.x or
                    other.x + other.w + margin < self.x or
                    self.y + self.h + margin < other.y or
                    other.y + other.h + margin < self.y)


class DungeonGenerator:
    """Генератор подземелий с комнатами и коридорами"""
    
    def __init__(self, width_tiles, height_tiles):
        self.width = width_tiles
        self.height = height_tiles
        self.tile_size = TILE_SIZE
        self.rooms = []
        self.corridors = []
        self.walls = []  # стены для коллизий
        self.collision_rects = []
        self.door_positions = []  # для хранения позиций дверей
        
        # Генерируем подземелье
        self.generate_dungeon()
    
    def generate_dungeon(self, max_rooms=15):
        """Генерирует подземелье с комнатами разных размеров"""
        print("🏰 Генерируем подземелье с комнатами разных размеров...")
        
        # Настройки размеров комнат
        SMALL_MIN, SMALL_MAX = 4, 6    # маленькие комнаты
        MEDIUM_MIN, MEDIUM_MAX = 7, 10  # средние комнаты
        BIG_MIN, BIG_MAX = 11, 15       # большие комнаты
        
        # Создаём границы карты (внешние стены)
        self.fill_map_with_walls()
        
        # Генерируем комнаты разных размеров
        room_types = ["small", "medium", "big"]
        room_weights = [0.3, 0.5, 0.2]  # 30% маленьких, 50% средних, 20% больших
        
        attempts = 0
        for _ in range(max_rooms * 4):
            if len(self.rooms) >= max_rooms:
                break
            
            # Выбираем размер комнаты
            room_type = random.choices(room_types, weights=room_weights)[0]
            
            if room_type == "small":
                room_w = random.randint(SMALL_MIN, SMALL_MAX)
                room_h = random.randint(SMALL_MIN, SMALL_MAX)
            elif room_type == "medium":
                room_w = random.randint(MEDIUM_MIN, MEDIUM_MAX)
                room_h = random.randint(MEDIUM_MIN, MEDIUM_MAX)
            else:  # big
                room_w = random.randint(BIG_MIN, BIG_MAX)
                room_h = random.randint(BIG_MIN, BIG_MAX)
            
            # Случайная позиция (не у краёв)
            x = random.randint(2, self.width - room_w - 2)
            y = random.randint(2, self.height - room_h - 2)
            
            new_room = Room(x, y, room_w, room_h)
            
            # Проверяем, не пересекается ли с другими комнатами
            intersects = False
            for room in self.rooms:
                if new_room.intersects(room):
                    intersects = True
                    break
            
            if not intersects:
                self.rooms.append(new_room)
                # Прорезаем комнату (убираем стены внутри)
                self.carve_room(new_room)
                print(f"  → Добавлена {room_type} комната: {room_w}x{room_h}")
            
            attempts += 1
            if attempts > max_rooms * 6:
                break
        
        print(f"✓ Создано {len(self.rooms)} комнат (маленьких: {self.count_rooms_by_size('small')}, "
            f"средних: {self.count_rooms_by_size('medium')}, больших: {self.count_rooms_by_size('big')})")
        
        # Соединяем комнаты коридорами
        self.connect_rooms()
        
        # Добавляем декоративные стены (колонны)
        self.add_decorative_walls()
        
        print(f"✓ Стены для коллизий: {len(self.collision_rects)}")

    def count_rooms_by_size(self, size_category):
        """Подсчитывает количество комнат определённого размера"""
        count = 0
        for room in self.rooms:
            if size_category == "small" and (room.w <= 6 or room.h <= 6):
                count += 1
            elif size_category == "big" and (room.w >= 10 or room.h >= 10):
                count += 1
            elif size_category == "medium" and (6 < room.w < 10 and 6 < room.h < 10):
                count += 1
        return count
    
    def create_border_walls(self):
        """Создаёт внешние стены по границе карты"""
        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.add_wall(x, y)

    def fill_map_with_walls(self):
        for x in range(self.width):
            for y in range(self.height):
                self.add_wall(x, y)
    
    def carve_room(self, room):
        """Прорезает комнату (убирает стены внутри)"""
        for x in range(room.x, room.x + room.w):
            for y in range(room.y, room.y + room.h):
                self.remove_wall(x, y)
    
    def add_wall(self, x, y):
        """Добавляет стену"""
        rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
        self.walls.append((x, y, rect))
        self.collision_rects.append(rect)
    
    def remove_wall(self, x, y):
        """Удаляет стену"""
        for i, (wx, wy, rect) in enumerate(self.walls):
            if wx == x and wy == y:
                self.walls.pop(i)
                if rect in self.collision_rects:
                    self.collision_rects.remove(rect)
                return True
        return False
    
    def is_wall(self, x, y):
        """Проверяет, есть ли стена на позиции"""
        for wx, wy, _ in self.walls:
            if wx == x and wy == y:
                return True
        return False

    def is_in_room(self, x, y):
        """Проверяет, находится ли позиция внутри какой-либо комнаты"""
        for room in self.rooms:
            if room.x <= x < room.x + room.w and room.y <= y < room.y + room.h:
                return True
        return False
    
    def connect_rooms(self):
        """Соединяет комнаты коридорами (алгоритм минимального остовного дерева)"""
        if len(self.rooms) < 2:
            return
        for i in range(1, len(self.rooms)):
            self.create_corridor(self.rooms[i - 1], self.rooms[i])
        
        # Находим ближайших соседей для каждой комнаты
        connections = []
        for i, room1 in enumerate(self.rooms):
            for j, room2 in enumerate(self.rooms):
                if i < j:
                    dist = abs(room1.center[0] - room2.center[0]) + abs(room1.center[1] - room2.center[1])
                    connections.append((dist, i, j))
        
        # Сортируем по расстоянию
        connections.sort()
        
        # Простые соединения (первые N-1)
        connected = set()
        for dist, i, j in connections:
            if len(connected) >= len(self.rooms) - 1:
                break
            if i not in connected or j not in connected:
                self.create_corridor(self.rooms[i], self.rooms[j])
                connected.add(i)
                connected.add(j)
        
        # Добавляем случайные дополнительные коридоры (для цикличности)
        for _ in range(len(self.rooms) // 3):
            if connections:
                dist, i, j = random.choice(connections)
                self.create_corridor(self.rooms[i], self.rooms[j])
    
    def create_corridor(self, room1, room2):
        """Создаёт коридор между двумя комнатами"""
        x1, y1 = room1.center
        x2, y2 = room2.center
        
        # Выбираем случайно направление
        if random.choice([True, False]):
            # Сначала горизонтальный, потом вертикальный
            self.create_horizontal_tunnel(x1, x2, y1)
            self.create_vertical_tunnel(y1, y2, x2)
        else:
            # Сначала вертикальный, потом горизонтальный
            self.create_vertical_tunnel(y1, y2, x1)
            self.create_horizontal_tunnel(x1, x2, y2)
    
    def create_horizontal_tunnel(self, x1, x2, y):
        """Создаёт горизонтальный коридор"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            # Прорезаем стены
            self.remove_wall(x, y)
            self.remove_wall(x, y - 1)
            self.remove_wall(x, y + 1)
    
    def create_vertical_tunnel(self, y1, y2, x):
        """Создаёт вертикальный коридор"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            # Прорезаем стены
            self.remove_wall(x, y)
            self.remove_wall(x - 1, y)
            self.remove_wall(x + 1, y)
    
    def add_decorative_walls(self):
        """Добавляет декоративные стены внутри коридоров для интереса"""
        # С вероятностью 20% добавляем колонны в коридорах
        for _ in range(len(self.rooms) * 2):
            x = random.randint(3, self.width - 4)
            y = random.randint(3, self.height - 4)
            
            # Проверяем, что это не комната и не проход
            if not self.is_wall(x, y):
                # Проверяем, что вокруг есть проходы
                neighbors = 0
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    if not self.is_wall(x+dx, y+dy):
                        neighbors += 1
                
                if neighbors >= 2 and random.random() < 0.3:
                    self.add_wall(x, y)
    
    # ===== НОВЫЕ МЕТОДЫ ДЛЯ ФАКЕЛОВ И ДВЕРЕЙ =====
    
    def get_torch_positions(self):
        """Возвращает список позиций для факелов на стенах"""
        torch_positions = []
        
        for room in self.rooms:
            room_center_x = room.x + room.w // 2
            room_center_y = room.y + room.h // 2
            
            # Добавляем факелы на стены каждой комнаты (по 2-4 факела на комнату)
            num_torches = random.randint(2, 4)
            
            for _ in range(num_torches):
                # Выбираем случайную стену
                wall = random.choice(['left', 'right', 'top', 'bottom'])
                
                if wall == 'left':
                    x = room.x
                    y = random.randint(room.y + 3, room.y + room.h - 4)
                elif wall == 'right':
                    x = room.x + room.w - 1
                    y = random.randint(room.y + 3, room.y + room.h - 4)
                elif wall == 'top':
                    x = random.randint(room.x + 3, room.x + room.w - 4)
                    y = room.y
                else:  # bottom
                    x = random.randint(room.x + 3, room.x + room.w - 4)
                    y = room.y + room.h - 1
                
                # Проверяем, что факел не попал в дверной проём
                is_valid = True
                for door in self.door_positions:
                    door_rect = pygame.Rect(door[0] - 2, door[1] - 2, door[2] + 4, door[3] + 4)
                    if door_rect.collidepoint(x, y):
                        is_valid = False
                        break
                
                if is_valid:
                    # Переводим в пиксели
                    pixel_x = x * TILE_SIZE + TILE_SIZE // 2
                    pixel_y = y * TILE_SIZE + TILE_SIZE // 2
                    torch_positions.append((pixel_x, pixel_y, room_center_x * TILE_SIZE, room_center_y * TILE_SIZE))
        
        return torch_positions

    def get_door_positions(self):
        """Возвращает список позиций для дверей между комнатами"""
        door_positions = []
        self.door_positions = []  # Сохраняем для проверок
        
        # Находим комнаты, которые соприкасаются
        for i, room1 in enumerate(self.rooms):
            for j, room2 in enumerate(self.rooms):
                if i >= j:
                    continue
                
                # Проверяем, соприкасаются ли комнаты
                # Проверяем, есть ли общая стена
                
                # Горизонтальное соединение (комнаты рядом по горизонтали)
                if (room1.x + room1.w == room2.x or room2.x + room2.w == room1.x):
                    # Проверяем, что они перекрываются по вертикали
                    if (room1.y < room2.y + room2.h and room2.y < room1.y + room1.h):
                        # Определяем, какая комната слева
                        if room1.x + room1.w == room2.x:  # room1 слева от room2
                            left_room = room1
                            right_room = room2
                        else:  # room2 слева от room1
                            left_room = room2
                            right_room = room1
                        
                        # Находим общую область по вертикали
                        top = max(left_room.y, right_room.y)
                        bottom = min(left_room.y + left_room.h, right_room.y + right_room.h)
                        
                        if bottom - top > 4:  # Если общая стена достаточно длинная
                            door_y = random.randint(top + 1, bottom - 2)
                            door_x = left_room.x + left_room.w
                            
                            door_data = (door_x, door_y, 1, 3)
                            self.door_positions.append(door_data)
                            door_positions.append((
                                door_x * TILE_SIZE + TILE_SIZE // 2,
                                door_y * TILE_SIZE + TILE_SIZE // 2,
                                10,  # ширина двери в пикселях
                                40   # высота двери в пикселях
                            ))
                
                # Вертикальное соединение (комнаты друг над другом)
                if (room1.y + room1.h == room2.y or room2.y + room2.h == room1.y):
                    # Проверяем, что они перекрываются по горизонтали
                    if (room1.x < room2.x + room2.w and room2.x < room1.x + room1.w):
                        # Определяем, какая комната сверху
                        if room1.y + room1.h == room2.y:  # room1 над room2
                            top_room = room1
                            bottom_room = room2
                        else:  # room2 над room1
                            top_room = room2
                            bottom_room = room1
                        
                        # Находим общую область по горизонтали
                        left = max(top_room.x, bottom_room.x)
                        right = min(top_room.x + top_room.w, bottom_room.x + bottom_room.w)
                        
                        if right - left > 4:  # Если общая стена достаточно длинная
                            door_x = random.randint(left + 1, right - 2)
                            door_y = top_room.y + top_room.h
                            
                            door_data = (door_x, door_y, 3, 1)
                            self.door_positions.append(door_data)
                            door_positions.append((
                                door_x * TILE_SIZE + TILE_SIZE // 2,
                                door_y * TILE_SIZE + TILE_SIZE // 2,
                                40,  # ширина двери в пикселях
                                10   # высота двери в пикселях
                            ))
        
        return door_positions
    
    def check_collision(self, rect, dx, dy):
        """Проверяет столкновение при движении"""
        if not self.collision_rects:
            return False
        
        new_rect = rect.move(dx, dy)
        
        for wall_rect in self.collision_rects:
            if new_rect.colliderect(wall_rect):
                return True
        return False
    
    def draw(self, screen, camera_x, camera_y, wall_tile):
        """Рисует подземелье"""
        for x, y, rect in self.walls:
            screen_x = rect.x - camera_x
            screen_y = rect.y - camera_y
            
            # Оптимизация: не рисуем за пределами экрана
            if (screen_x + self.tile_size < 0 or screen_x > screen.get_width() or
                screen_y + self.tile_size < 0 or screen_y > screen.get_height()):
                continue
            
            if wall_tile:
                screen.blit(wall_tile, (screen_x, screen_y))
            else:
                pygame.draw.rect(screen, (80, 80, 80), (screen_x, screen_y, self.tile_size, self.tile_size))
    
    def draw_debug(self, screen, camera_x, camera_y):
        """Рисует отладку (красные рамки коллизий)"""
        for rect in self.collision_rects:
            screen_x = rect.x - camera_x
            screen_y = rect.y - camera_y
            pygame.draw.rect(screen, (255, 0, 0), (screen_x, screen_y, rect.width, rect.height), 2)
        
        # Рисуем комнаты синими рамками
        for room in self.rooms:
            screen_x = room.rect.x - camera_x
            screen_y = room.rect.y - camera_y
            pygame.draw.rect(screen, (0, 100, 255), (screen_x, screen_y, room.rect.width, room.rect.height), 2)
        
        # Рисуем позиции дверей (зелёные точки)
        for door in self.door_positions:
            door_x = door[0] * TILE_SIZE - camera_x
            door_y = door[1] * TILE_SIZE - camera_y
            pygame.draw.circle(screen, (0, 255, 0), (int(door_x), int(door_y)), 5)
    
    def get_map_size_pixels(self):
        """Возвращает размер карты в пикселях"""
        return (self.width * self.tile_size, self.height * self.tile_size)
    
    def get_player_start_position(self):
        """Возвращает стартовую позицию игрока в первой комнате"""
        if self.rooms:
            room = self.rooms[0]
            x = (room.x + room.w // 2) * self.tile_size
            y = (room.y + room.h // 2) * self.tile_size
            return (x, y)
        return (self.width * self.tile_size // 2, self.height * self.tile_size // 2)
