import pygame
import sys
import os
from settings import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Кнопки меню (на русском)
        self.menu_items = ["Начать игру", "Загрузить", "Настройки", "Выход"]
        self.selected = 0
        
        # Загружаем шрифты
        base_path = os.path.join("assets", "fonts")
        
        # Для заголовка
        title_font_path = os.path.join(base_path, "PlayfairDisplaySC-Bold.ttf")
        if os.path.exists(title_font_path):
            self.title_font = pygame.font.Font(title_font_path, 84)
        else:
            self.title_font = pygame.font.Font(None, 84)
        
        # Для кнопок
        button_font_path = os.path.join(base_path, "Philosopher-Bold.ttf")
        if os.path.exists(button_font_path):
            self.button_font = pygame.font.Font(button_font_path, 42)
        else:
            self.button_font = pygame.font.Font(None, 42)
        
        self.hint_font = pygame.font.Font(None, 24)
        
        # Загружаем видео
        self.frames = []
        video_path = os.path.join("assets", "videos", "menu_bg.mp4")
        
        try:
            import imageio
            if os.path.exists(video_path):
                print(f"Загрузка видео: {video_path}")
                video = imageio.get_reader(video_path)
                for i, frame in enumerate(video):
                    if i >= 300:
                        break
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    frame_surface = pygame.transform.scale(frame_surface, (SCREEN_W, SCREEN_H))
                    self.frames.append(frame_surface)
                self.current_frame = 0
                print(f"Загружено {len(self.frames)} кадров")
            else:
                print(f"Видео не найдено: {video_path}")
        except Exception as e:
            print(f"Ошибка видео: {e}")
    
    def draw_button(self, text, x, y, width, height, is_selected):
        if is_selected:
            color = GOLD
            glow_surface = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*GOLD, 50), (0, 0, width + 10, height + 10), border_radius=12)
            self.screen.blit(glow_surface, (x - 5, y - 5))
        else:
            color = (150, 150, 150)
        
        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        button_surface.fill((0, 0, 0, 180))
        pygame.draw.rect(button_surface, color, (0, 0, width, height), 3, border_radius=10)
        self.screen.blit(button_surface, (x, y))
        
        text_surface = self.button_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
        self.screen.blit(text_surface, text_rect)
    
    def run(self):
        while self.running:
            # Видео фон
            if self.frames:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.screen.blit(self.frames[self.current_frame], (0, 0))
            else:
                self.screen.fill(BLACK)
            
            # Затемнение
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))
            
            # Заголовок
            title = self.title_font.render("PYDANGEON", True, GOLD)
            title_rect = title.get_rect(center=(SCREEN_W//2, SCREEN_H//4))
            
            title_shadow = self.title_font.render("PYDANGEON", True, (0, 0, 0))
            shadow_rect = title_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            self.screen.blit(title_shadow, shadow_rect)
            self.screen.blit(title, title_rect)
            
            # Подзаголовок
            subtitle = self.hint_font.render("Overgrown Labyrinth", True, (180, 200, 150))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_W//2, SCREEN_H//4 + 70))
            self.screen.blit(subtitle, subtitle_rect)
            
            # Кнопки
            button_w = 250
            button_h = 60
            start_x = SCREEN_W//2 - button_w//2
            start_y = SCREEN_H//2 - 60
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for i in range(len(self.menu_items)):
                y = start_y + i * (button_h + 15)
                button_rect = pygame.Rect(start_x, y, button_w, button_h)
                if button_rect.collidepoint(mouse_x, mouse_y):
                    self.selected = i
            
            for i, item in enumerate(self.menu_items):
                y = start_y + i * (button_h + 15)
                self.draw_button(item, start_x, y, button_w, button_h, i == self.selected)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.menu_items)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        return self.get_action()
                    elif event.key == pygame.K_ESCAPE:
                        return "exit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i in range(len(self.menu_items)):
                            y = start_y + i * (button_h + 15)
                            button_rect = pygame.Rect(start_x, y, button_w, button_h)
                            if button_rect.collidepoint(event.pos):
                                return self.get_action(i)
            
            pygame.display.flip()
            self.clock.tick(30)
        
        return "exit"
    
    def get_action(self, index=None):
        if index is None:
            index = self.selected
        
        actions = {
            "Начать игру": "start",
            "Загрузить": "load",
            "Настройки": "settings",
            "Выход": "exit"
        }
        return actions.get(self.menu_items[index], "exit")

def show_menu(screen):
    menu = Menu(screen)
    return menu.run()