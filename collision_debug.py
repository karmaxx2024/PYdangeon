import pygame

def draw_collision_debug(screen, world_map, camera_x=0, camera_y=0, show_grid=True):
    """
    Рисует отладочную информацию о коллизиях
    
    Args:
        screen: поверхность pygame для отрисовки
        world_map: объект WorldMap с коллизиями
        camera_x: смещение камеры по X
        camera_y: смещение камеры по Y
        show_grid: показывать ли сетку тайлов
    """
    if not world_map:
        return
    
    # Рисуем красные рамки всех коллизий
    for rect in world_map.collision_rects:
        screen_x = rect.x - camera_x
        screen_y = rect.y - camera_y
        pygame.draw.rect(screen, (255, 0, 0), (screen_x, screen_y, rect.width, rect.height), 2)
    
    # Рисуем зелёные рамки для стен, которые НЕ являются коллизиями (если есть)
    if hasattr(world_map, 'non_collision_walls'):
        for rect in world_map.non_collision_walls:
            screen_x = rect.x - camera_x
            screen_y = rect.y - camera_y
            pygame.draw.rect(screen, (0, 255, 0), (screen_x, screen_y, rect.width, rect.height), 2)
    
    # Показываем сетку тайлов (опционально)
    if show_grid and hasattr(world_map, 'tile_size'):
        tile_size = world_map.tile_size
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Вертикальные линии сетки
        start_x = (camera_x // tile_size) * tile_size - camera_x
        for x in range(start_x, screen_width, tile_size):
            pygame.draw.line(screen, (100, 100, 100, 50), (x, 0), (x, screen_height), 1)
        
        # Горизонтальные линии сетки
        start_y = (camera_y // tile_size) * tile_size - camera_y
        for y in range(start_y, screen_height, tile_size):
            pygame.draw.line(screen, (100, 100, 100, 50), (0, y), (screen_width, y), 1)


class CollisionDebugger:
    """Класс для удобной отладки коллизий"""
    
    def __init__(self, world_map):
        self.world_map = world_map
        self.enabled = False
        self.show_grid = True
        self.show_collision_rects = True
        self.show_distance_to_nearest_wall = False
        self.font = None
        
    def toggle(self):
        """Включает/выключает режим отладки"""
        self.enabled = not self.enabled
        print(f"🔧 Режим отладки коллизий: {'ВКЛЮЧЁН' if self.enabled else 'ВЫКЛЮЧЁН'}")
        return self.enabled
    
    def toggle_grid(self):
        """Включает/выключает сетку"""
        self.show_grid = not self.show_grid
        print(f"📐 Сетка: {'показана' if self.show_grid else 'скрыта'}")
    
    def draw(self, screen, camera_x=0, camera_y=0, player_rect=None):
        """
        Рисует отладочную информацию
        
        Args:
            screen: поверхность pygame
            camera_x: смещение камеры по X
            camera_y: смещение камеры по Y
            player_rect: прямоугольник игрока (для дополнительной информации)
        """
        if not self.enabled or not self.world_map:
            return
        
        # Инициализируем шрифт если нужно
        if self.font is None:
            self.font = pygame.font.Font(None, 24)
        
        # Рисуем коллизии
        if self.show_collision_rects:
            for rect in self.world_map.collision_rects:
                screen_x = rect.x - camera_x
                screen_y = rect.y - camera_y
                pygame.draw.rect(screen, (255, 0, 0), (screen_x, screen_y, rect.width, rect.height), 2)
        
        # Рисуем сетку
        if self.show_grid:
            self._draw_grid(screen, camera_x, camera_y)
        
        # Показываем дополнительную информацию
        info_y = 100
        info_lines = []
        
        info_lines.append(f"Коллизий: {len(self.world_map.collision_rects)}")
        info_lines.append(f"Размер карты: {self.world_map.width_tiles}x{self.world_map.height_tiles} тайлов")
        
        if player_rect:
            # Находим ближайшую стену
            min_distance = float('inf')
            for wall_rect in self.world_map.collision_rects:
                # Расстояние между центрами
                dx = wall_rect.centerx - player_rect.centerx
                dy = wall_rect.centery - player_rect.centery
                distance = (dx*dx + dy*dy) ** 0.5
                if distance < min_distance:
                    min_distance = distance
            
            info_lines.append(f"Игрок: ({player_rect.centerx}, {player_rect.centery})")
            info_lines.append(f"Ближайшая стена: {min_distance:.1f} пикселей")
            
            # Проверяем, есть ли коллизия прямо сейчас
            collision_now = False
            for wall_rect in self.world_map.collision_rects:
                if player_rect.colliderect(wall_rect):
                    collision_now = True
                    break
            info_lines.append(f"В стене прямо сейчас: {'ДА!!!' if collision_now else 'Нет'}")
        
        # Рисуем информацию на экране
        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, (255, 255, 0))
            screen.blit(text, (10, info_y + i * 25))
    
    def _draw_grid(self, screen, camera_x, camera_y):
        """Рисует сетку тайлов"""
        if not hasattr(self.world_map, 'tile_size'):
            return
        
        tile_size = self.world_map.tile_size
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Определяем начальные координаты сетки
        start_x = (camera_x // tile_size) * tile_size - camera_x
        start_y = (camera_y // tile_size) * tile_size - camera_y
        
        # Рисуем вертикальные линии
        for x in range(start_x, screen_width, tile_size):
            pygame.draw.line(screen, (80, 80, 80), (x, 0), (x, screen_height), 1)
            # Подписываем координаты X
            tile_x = (x + camera_x) // tile_size
            if self.font:
                text = self.font.render(str(tile_x), True, (100, 100, 100))
                screen.blit(text, (x + 2, 2))
        
        # Рисуем горизонтальные линии
        for y in range(start_y, screen_height, tile_size):
            pygame.draw.line(screen, (80, 80, 80), (0, y), (screen_width, y), 1)
            # Подписываем координаты Y
            tile_y = (y + camera_y) // tile_size
            if self.font:
                text = self.font.render(str(tile_y), True, (100, 100, 100))
                screen.blit(text, (2, y + 2))


def create_debug_panel(screen, world_map, player_rect=None):
    """
    Простая функция для быстрой отладки
    
    Использование:
        в основном цикле: create_debug_panel(screen, world_map, player.rect)
    
    Args:
        screen: поверхность pygame
        world_map: объект WorldMap
        player_rect: прямоугольник игрока (опционально)
    """
    if not world_map:
        return
    
    font = pygame.font.Font(None, 20)
    y_offset = 10
    
    # Полупрозрачный фон для панели
    panel_rect = pygame.Rect(10, 10, 250, 150)
    s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, panel_rect)
    
    # Текст информации
    info = [
        f"Стен: {len(world_map.collision_rects)}",
        f"Размер карты: {world_map.width_tiles}x{world_map.height_tiles}",
    ]
    
    if player_rect:
        info.append(f"Игрок: ({player_rect.centerx}, {player_rect.centery})")
        info.append(f"Размер игрока: {player_rect.width}x{player_rect.height}")
    
    for i, text in enumerate(info):
        rendered = font.render(text, True, (255, 255, 255))
        screen.blit(rendered, (20, y_offset + i * 22))
