import pygame
import random

# Константы
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
BLOCK_SIZE = 64
MAZE_WIDTH = 29
MAZE_HEIGHT = 15

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[True for _ in range(width)] for _ in range(height)]
    
    def generate(self):
        self.maze = [[True for _ in range(self.width)] for _ in range(self.height)]
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = False
        
        stack = [(start_x, start_y)]
        visited = set([(start_x, start_y)])
        
        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.width and 0 < ny < self.height:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, dx, dy))
            
            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                wall_x, wall_y = x + dx // 2, y + dy // 2
                self.maze[wall_y][wall_x] = False
                self.maze[ny][nx] = False
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        
        for i in range(self.height):
            self.maze[i][0] = True
            self.maze[i][self.width - 1] = True
        for j in range(self.width):
            self.maze[0][j] = True
            self.maze[self.height - 1][j] = True
    
    def draw(self, screen, wall_texture, floor_texture, offset_x, offset_y):
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(
                    offset_x + x * BLOCK_SIZE,
                    offset_y + y * BLOCK_SIZE,
                    BLOCK_SIZE, BLOCK_SIZE
                )
                if self.maze[y][x]:
                    screen.blit(wall_texture, rect)
                else:
                    screen.blit(floor_texture, rect)

# ============ ЗАГРУЗКА ТЕКСТУР ============
pygame.init()

# Получаем размеры экрана для полноэкранного режима
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

# Создаем окно в полноэкранном режиме
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Лабиринт - Fullscreen")

# ЗАГРУЖАЕМ СВОИ ИЗОБРАЖЕНИЯ
wall_texture = pygame.image.load('wall.png')
floor_texture = pygame.image.load('floor.png')

# Масштабируем до 64x64
wall_texture = pygame.transform.scale(wall_texture, (BLOCK_SIZE, BLOCK_SIZE))
floor_texture = pygame.transform.scale(floor_texture, (BLOCK_SIZE, BLOCK_SIZE))

# Вычисляем отступы для центрирования лабиринта
offset_x = (screen_width - MAZE_WIDTH * BLOCK_SIZE) // 2
offset_y = (screen_height - MAZE_HEIGHT * BLOCK_SIZE) // 2

maze = MazeGenerator(MAZE_WIDTH, MAZE_HEIGHT)
maze.generate()

running = True
clock = pygame.time.Clock()
fullscreen = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                maze.generate()
            # Переключение полноэкранного режима по F11
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                # Пересчитываем отступы при смене режима
                if fullscreen:
                    offset_x = (screen_width - MAZE_WIDTH * BLOCK_SIZE) // 2
                    offset_y = (screen_height - MAZE_HEIGHT * BLOCK_SIZE) // 2
                else:
                    offset_x = (SCREEN_WIDTH - MAZE_WIDTH * BLOCK_SIZE) // 2
                    offset_y = (SCREEN_HEIGHT - MAZE_HEIGHT * BLOCK_SIZE) // 2
            # Выход по ESC
            if event.key == pygame.K_ESCAPE:
                running = False
    
    screen.fill((0, 0, 0))
    maze.draw(screen, wall_texture, floor_texture, offset_x, offset_y)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()