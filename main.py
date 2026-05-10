# main.py
import pygame
import sys
from settings import *
from menu import show_menu, show_settings
from settings import GameSettings

def game_loop(screen, settings):
    """Основной игровой цикл (заглушка)"""
    clock = pygame.time.Clock()
    running = True
    while running:
        # Ограничение FPS из настроек
        dt = clock.tick(settings.fps_limit)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        
        # Отрисовка временного экрана игры
        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        text = font.render("Игра запущена! Нажми ESC для возврата", True, WHITE)
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    return True

def main():
    pygame.init()
    
    # Загружаем настройки из config.json
    game_settings = GameSettings("config.json")
    
    # Создаём окно с учётом сохранённых настроек
    flags = pygame.FULLSCREEN if game_settings.fullscreen else 0
    screen = pygame.display.set_mode((game_settings.screen_width, game_settings.screen_height), flags)
    pygame.display.set_caption("PYdangeon - Overgrown Labyrinth")
    
    # Главный цикл приложения
    while True:
        # Показываем главное меню, получаем выбор пользователя
        choice = show_menu(screen, game_settings)
        
        if choice == "start":
            if not game_loop(screen, game_settings):
                break
        elif choice == "settings":
            # Открываем меню настроек
            show_settings(screen, game_settings)
            # Обновляем экран (разрешение могло измениться)
            screen = pygame.display.get_surface()
            # Настройки уже сохранены внутри меню настроек
        elif choice == "load":
            # Заглушка для загрузки сохранений
            print("Загрузка игры... (функция в разработке)")
            pygame.time.wait(500)
        elif choice == "exit":
            break
        else:
            # На случай неизвестного выбора
            print(f"Выбрано: {choice}")
            pygame.time.wait(500)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
