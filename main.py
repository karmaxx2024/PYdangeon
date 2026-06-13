import pygame
import sys
from settings import *
from menu import show_menu, show_settings
from settings import GameSettings
from character_selection import show_character_select
from player import Player
from tilemap import load_floor_tile, load_wall_tile, draw_floor, generate_floor_layout, FLOOR_IMAGE, FLOOR_MOSS_IMAGE
from world_map import DungeonGenerator
#from pause_menu import PauseMenu  # НОВЫЙ ИМПОРТ


def game_loop(screen, settings, char_data):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    hint_font = pygame.font.Font(None, 24)

    sw = screen.get_width()
    sh = screen.get_height()
    
    # ===== ГЕНЕРИРУЕМ ПОДЗЕМЕЛЬЕ (каждый раз разное!) =====
    WORLD_WIDTH_TILES = 50   # ширина в тайлах
    WORLD_HEIGHT_TILES = 40  # высота в тайлах
    
    # Каждый запуск - новое подземелье!
    dungeon = DungeonGenerator(WORLD_WIDTH_TILES, WORLD_HEIGHT_TILES)
    
    # Получаем размер карты в пикселях
    map_width_px, map_height_px = dungeon.get_map_size_pixels()
    
    # Стартовая позиция игрока
    start_x, start_y = dungeon.get_player_start_position()
    player = Player(start_x, start_y, char_data)
    
    # Загружаем текстуры
    floor_tile = load_floor_tile(FLOOR_IMAGE)
    floor_moss_tile = load_floor_tile(FLOOR_MOSS_IMAGE)
    floor_layout = generate_floor_layout(sw, sh, TILE_SIZE, moss_chance=0.20)
    wall_tile = load_wall_tile()
    
    # Камера
    camera_x = 0
    camera_y = 0
    
    # Режим отладки
    debug_mode = False
    
    # НОВОЕ: Меню паузы
    pause_menu = PauseMenu(screen)
    
    print("=== ПОДЗЕМЕЛЬЕ СОЗДАНО ===")
    print(f"Комнат: {len(dungeon.rooms)}")
    print(f"Стен: {len(dungeon.collision_rects)}")
    print("Нажми F3 для отладки, ESC — пауза")
    
    while True:
        dt = clock.tick(settings.fps_limit) / 1000.0
        if dt > 0.1:
            dt = 0.1
        
        # --- ОБРАБОТКА СОБЫТИЙ ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu.toggle()  # Переключаем паузу
                elif event.key == pygame.K_F3:
                    debug_mode = not debug_mode
        
        # --- ЛОГИКА ПАУЗЫ ---
        if pause_menu.is_paused:
            # Собираем события заново для меню паузы
            pause_events = []
            for event in pygame.event.get():
                pause_events.append(event)
                if event.type == pygame.QUIT:
                    return False
            
            # Обрабатываем ввод в меню паузы
            pause_action = pause_menu.handle_input(pause_events)
            
            if pause_action == "resume":
                pause_menu.toggle()
            elif pause_action == "settings":
                # Возвращаемся в настройки (выйдет из игрового цикла)
                return True
            elif pause_action == "menu":
                return True  # Выход в главное меню
            elif pause_action == "quit":
                return False  # Выход из игры
            
            # ---- ОТРИСОВКА (игра заморожена) ----
            screen.fill((20, 20, 30))
            
            # Рисуем пол
            draw_floor(screen, floor_tile, floor_moss_tile, floor_layout)
            
            # Рисуем подземелье
            dungeon.draw(screen, camera_x, camera_y, wall_tile)
            
            # Отладка
            if debug_mode:
                dungeon.draw_debug(screen, camera_x, camera_y)
                
                debug_font = pygame.font.Font(None, 20)
                info = [
                    f"FPS: {int(clock.get_fps())}",
                    f"Комнат: {len(dungeon.rooms)}",
                    f"Стен: {len(dungeon.collision_rects)}",
                    f"Позиция: ({player.rect.x}, {player.rect.y})"
                ]
                for i, line in enumerate(info):
                    text = debug_font.render(line, True, (255, 255, 0))
                    screen.blit(text, (10, 100 + i * 20))
            
            # Рисуем игрока
            player.draw_with_camera(screen, camera_x, camera_y)
            
            # HUD
            player.draw_hud(screen, font)
            
            # Подсказка
            hint = hint_font.render("ESC — продолжить", True, (150, 150, 150))
            screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 30))
            
            # Рисуем меню паузы поверх всего
            pause_menu.draw()
            
            pygame.display.flip()
            continue  # Пропускаем обновление игрока
        
        # --- ОБНОВЛЕНИЕ ИГРЫ (если не на паузе) ---
        keys = pygame.key.get_pressed()
        
        # Обновляем игрока
        player.update_with_collision(dt, keys, dungeon)
        
        # Камера следует за игроком
        camera_x = player.rect.centerx - sw // 2
        camera_y = player.rect.centery - sh // 2
        
        # Ограничиваем камеру
        camera_x = max(0, min(camera_x, map_width_px - sw))
        camera_y = max(0, min(camera_y, map_height_px - sh))
        
        # --- ОТРИСОВКА ---
        screen.fill((20, 20, 30))
        
        # Рисуем пол
        draw_floor(screen, floor_tile, floor_moss_tile, floor_layout)
        
        # Рисуем подземелье
        dungeon.draw(screen, camera_x, camera_y, wall_tile)
        
        # Отладка
        if debug_mode:
            dungeon.draw_debug(screen, camera_x, camera_y)
            
            # Показываем информацию
            debug_font = pygame.font.Font(None, 20)
            info = [
                f"FPS: {int(clock.get_fps())}",
                f"Комнат: {len(dungeon.rooms)}",
                f"Стен: {len(dungeon.collision_rects)}",
                f"Позиция: ({player.rect.x}, {player.rect.y})"
            ]
            for i, line in enumerate(info):
                text = debug_font.render(line, True, (255, 255, 0))
                screen.blit(text, (10, 100 + i * 20))
        
        # Рисуем игрока
        player.draw_with_camera(screen, camera_x, camera_y)
        
        # HUD
        player.draw_hud(screen, font)
        
        # Подсказки
        hint = hint_font.render("WASD / стрелки — движение    ESC — пауза    F3 — отладка", True, (150, 150, 150))
        screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 30))
        
        pygame.display.flip()
    
    return True


def main():
    pygame.init()
    
    game_settings = GameSettings("config.json")
    
    flags = pygame.FULLSCREEN if game_settings.fullscreen else 0
    screen = pygame.display.set_mode((game_settings.screen_width, game_settings.screen_height), flags)
    pygame.display.set_caption("PYdangeon - Procedural Dungeon")
    
    while True:
        choice = show_menu(screen, game_settings)
        
        if choice == "start":
            char_data = show_character_select(screen, game_settings)
            if char_data is not None:
                if not game_loop(screen, game_settings, char_data):
                    break
        elif choice == "settings":
            show_settings(screen, game_settings)
            screen = pygame.display.get_surface()
        elif choice == "load":
            print("Загрузка игры...")
            pygame.time.wait(500)
        elif choice == "exit":
            break
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
