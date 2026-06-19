import pygame
import sys
from settings import *
from menu import show_menu, show_settings
from settings import GameSettings
from character_selection import show_character_select
from player import Player
from tilemap import load_floor_tile, load_wall_tile, draw_floor_with_camera, generate_floor_layout, FLOOR_IMAGE, FLOOR_MOSS_IMAGE
from world_map import DungeonGenerator
from objects import Torch, Door
from pause_menu import PauseMenu



def game_loop(screen, settings, char_data):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    hint_font = pygame.font.Font(None, 24)

    sw = screen.get_width()
    sh = screen.get_height()

    # ===== ГЕНЕРИРУЕМ ПОДЗЕМЕЛЬЕ (каждый раз разное!) =====
    WORLD_WIDTH_TILES = 50  # ширина в тайлах
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
    floor_layout = generate_floor_layout(map_width_px, map_height_px, TILE_SIZE, moss_chance=0.20)
    wall_tile = load_wall_tile()
    
    # ПРОВЕРКА: загрузилась ли текстура стены?
    if wall_tile is None:
        print("⚠️ ВНИМАНИЕ: Текстура стены не загружена! Будет использован серый цвет.")
        # Создаём заглушку
        wall_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        wall_tile.fill((100, 100, 100))

    # Камера
    camera_x = 0
    camera_y = 0

    # Режим отладки
    debug_mode = False

    # НОВОЕ: Меню паузы
    pause_menu = PauseMenu(screen)

    # ===== НОВОЕ: СОЗДАЁМ ОБЪЕКТЫ (ФАКЕЛЫ И ДВЕРИ) =====
    objects_group = pygame.sprite.Group()
    
    # Добавляем факелы на стены
    torch_positions = dungeon.get_torch_positions()
    for pos in torch_positions:
        # Определяем направление факела (смотрит в центр комнаты)
        x, y, room_center_x, room_center_y = pos
        # Если факел слева от центра комнаты - смотрит вправо, и наоборот
        if x < room_center_x:
            direction = 'right'
        else:
            direction = 'left'
        torch = Torch(x, y, direction)
        objects_group.add(torch)
    
    # Добавляем двери между комнатами
    door_positions = dungeon.get_door_positions()
    doors = []  # Сохраняем ссылки на двери для проверки коллизий
    for door_data in door_positions:
        x, y, width, height = door_data
        door = Door(x, y, width, height, is_open=False)
        objects_group.add(door)
        doors.append(door)

    print("=== ПОДЗЕМЕЛЬЕ СОЗДАНО ===")
    print(f"Комнат: {len(dungeon.rooms)}")
    print(f"Стен: {len(dungeon.collision_rects)}")
    print(f"Факелов: {len(torch_positions)}")
    print(f"Дверей: {len(door_positions)}")
    print(f"Текстура стены: {'загружена' if wall_tile else 'НЕ ЗАГРУЖЕНА'}")
    print("Нажми F3 для отладки, ESC — пауза, E — открыть/закрыть дверь")

    while True:
        dt = clock.tick(settings.fps_limit) / 1000.0
        if dt > 0.1:
            dt = 0.1

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                return False

        if pause_menu.is_paused:
            pause_action = pause_menu.handle_input(events)

            if pause_action == "resume":
                pause_menu.toggle()
            elif pause_action == "settings":
                show_settings(screen, settings)
                screen = pygame.display.get_surface()
                pause_menu.toggle()
            elif pause_action == "menu":
                return True
            elif pause_action == "quit":
                return False

            screen.fill((20, 20, 30))
            draw_floor_with_camera(screen, floor_tile, floor_moss_tile, floor_layout, camera_x, camera_y)
            dungeon.draw(screen, camera_x, camera_y, wall_tile)
            
            # Рисуем объекты
            objects_group.draw(screen)

            if debug_mode:
                dungeon.draw_debug(screen, camera_x, camera_y)

            player.draw_with_camera(screen, camera_x, camera_y)
            player.draw_hud(screen, font)
            pause_menu.draw()
            pygame.display.flip()
            continue

        # ===== НОВОЕ: ОБРАБОТКА ВЗАИМОДЕЙСТВИЯ С ДВЕРЯМИ =====
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu.toggle()
                elif event.key == pygame.K_F3:
                    debug_mode = not debug_mode
                elif event.key == pygame.K_e:
                    # Проверяем, стоит ли игрок рядом с дверью
                    for door in doors:
                        # Создаём зону взаимодействия (чуть больше двери)
                        interaction_rect = door.rect.inflate(30, 30)
                        if interaction_rect.colliderect(player.rect):
                            door.toggle()
                            print(f"Дверь {'открыта' if door.is_open else 'закрыта'}")
                            break

        # --- ОБНОВЛЕНИЕ ИГРЫ (если не на паузе) ---
        keys = pygame.key.get_pressed()

        # Обновляем игрока (передаём двери для коллизий)
        player.update_with_collision(dt, keys, dungeon, doors)

        # Обновляем объекты (анимация факелов и дверей)
        objects_group.update(dt)

        # Камера следует за игроком
        camera_x = player.rect.centerx - sw // 2
        camera_y = player.rect.centery - sh // 2

        # Ограничиваем камеру
        camera_x = max(0, min(camera_x, map_width_px - sw))
        camera_y = max(0, min(camera_y, map_height_px - sh))

        # --- ОТРИСОВКА ---
        screen.fill((20, 20, 30))

        # Рисуем пол с камерой
        draw_floor_with_camera(screen, floor_tile, floor_moss_tile, floor_layout, camera_x, camera_y)

        # Рисуем подземелье (стены)
        dungeon.draw(screen, camera_x, camera_y, wall_tile)

        # Рисуем объекты (факелы и двери)
        objects_group.draw(screen)

        # Отладка
        if debug_mode:
            dungeon.draw_debug(screen, camera_x, camera_y)

            # Показываем информацию
            debug_font = pygame.font.Font(None, 20)
            info = [
                f"FPS: {int(clock.get_fps())}",
                f"Комнат: {len(dungeon.rooms)}",
                f"Стен: {len(dungeon.collision_rects)}",
                f"Позиция: ({player.rect.x}, {player.rect.y})",
                f"Камера: ({camera_x}, {camera_y})",
                f"Дверей: {len(doors)}",
                f"Факелов: {len(torch_positions)}"
            ]
            for i, line in enumerate(info):
                text = debug_font.render(line, True, (255, 255, 0))
                screen.blit(text, (10, 100 + i * 20))
            
            # Показываем зоны взаимодействия с дверями (зелёные рамки)
            for door in doors:
                interaction_rect = door.rect.inflate(30, 30)
                pygame.draw.rect(screen, (0, 255, 0), 
                               (interaction_rect.x - camera_x, 
                                interaction_rect.y - camera_y, 
                                interaction_rect.width, 
                                interaction_rect.height), 1)

        # Рисуем игрока
        player.draw_with_camera(screen, camera_x, camera_y)

        # HUD
        player.draw_hud(screen, font)

        # Подсказки
        hint_text = "WASD / стрелки — движение    ESC — пауза    F3 — отладка    E — открыть/закрыть дверь"
        hint = hint_font.render(hint_text, True, (150, 150, 150))
        screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 30))

        # Подсказка о двери рядом (жёлтая)
        near_door = False
        for door in doors:
            interaction_rect = door.rect.inflate(30, 30)
            if interaction_rect.colliderect(player.rect) and not door.is_open:
                near_door = True
                break
        
        if near_door:
            door_hint = hint_font.render("Нажми E, чтобы открыть дверь", True, (255, 255, 100))
            screen.blit(door_hint, (sw // 2 - door_hint.get_width() // 2, sh - 60))

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
