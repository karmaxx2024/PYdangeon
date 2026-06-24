import random


class MazeGenerator:
    """Генератор лабиринта методом DFS (backtracking)."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[True for _ in range(width)] for _ in range(height)]

    def generate(self):
        self.maze = [[True for _ in range(self.width)] for _ in range(self.height)]
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = False

        stack = [(start_x, start_y)]
        visited = {(start_x, start_y)}

        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, dx, dy))

            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                wall_x = x + dx // 2
                wall_y = y + dy // 2
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
