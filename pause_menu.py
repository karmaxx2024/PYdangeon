import pygame
from settings import *

class PauseMenu:
    """Меню паузы с остановкой игрового процесса"""
    
    def __init__(self, screen):
        self.screen = screen
        self.is_paused = False
        self.font_title = None
        self.font_normal = None
        self.selected_option = 0
        self.options = ["Продолжить", "Настройки", "В главное меню", "Выход"]
        
        # Шрифты
        try:
            self.font_title = pygame.font.Font(None, 72)
            self.font_normal = pygame.font.Font(None, 48)
        except:
            self.font_title = pygame.font.SysFont("Arial", 72)
            self.font_normal = pygame.font.SysFont("Arial", 48)
        
        # Полупрозрачная поверхность
        self.overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        self.overlay.set_alpha(180)
        self.overlay.fill((0, 0, 0))
        
        print("✓ PauseMenu готов")
    
    def toggle(self):
        """Переключает состояние паузы"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            print("⏸ Игра на паузе")
        else:
            print("▶ Игра продолжена")
        return self.is_paused
    
    def handle_input(self, events):
        """
        Обрабатывает ввод в меню паузы
        Returns: действие (None, "resume", "settings", "menu", "quit")
        """
        if not self.is_paused:
            return None
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected_option == 0:
                        return "resume"
                    elif self.selected_option == 1:
                        return "settings"
                    elif self.selected_option == 2:
                        return "menu"
                    elif self.selected_option == 3:
                        return "quit"
        
        return None
    
    def draw(self):
        """Рисует меню паузы"""
        if not self.is_paused:
            return
        
        sw, sh = self.screen.get_width(), self.screen.get_height()
        
        # Затемнённый фон
        self.screen.blit(self.overlay, (0, 0))
        
        # Заголовок "ПАУЗА"
        title_text = self.font_title.render("ПАУЗА", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(sw // 2, sh // 4))
        self.screen.blit(title_text, title_rect)
        
        # Пункты меню
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = self.font_normal.render(option, True, color)
            rect = text.get_rect(center=(sw // 2, sh // 2 + i * 60))
            self.screen.blit(text, rect)
        
        # Подсказка
        hint_font = pygame.font.Font(None, 24)
        hint = hint_font.render("↑/↓ — выбор    Enter — выбрать    ESC — продолжить", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(sw // 2, sh - 50))
        self.screen.blit(hint, hint_rect)
