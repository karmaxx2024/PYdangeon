import pygame
import sys
from settings import *
from menu import show_menu, show_settings
from settings import GameSettings
from character_selection import show_character_select
from player import Player
from tilemap import *


def game_loop(screen, settings, char_data):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    hint_font = pygame.font.Font(None, 24)

    sw = screen.get_width()
    sh = screen.get_height()

    player = Player(sw // 2, sh // 2, char_data)
    floor_tile = load_floor_tile()# пол  # один тайл 32×32 из листа
    wall_tile = load_wall_tile()# стены  # один тайл 32×32 из листа

    while True:
        dt = clock.tick(settings.fps_limit)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True

        player.update(dt, sw, sh)

        draw_floor(screen, floor_tile)

        player.draw(screen)
        player.draw_hud(screen, font)

        hint = hint_font.render("WASD / стрелки — движение    ESC — в меню", True, (90, 90, 90))
        screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 30))

        pygame.display.flip()

    return True


def main():
    pygame.init()

    game_settings = GameSettings("config.json")

    flags = pygame.FULLSCREEN if game_settings.fullscreen else 0
    screen = pygame.display.set_mode((game_settings.screen_width, game_settings.screen_height), flags)
    pygame.display.set_caption("PYdangeon - Overgrown Labyrinth")

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
            print("Загрузка игры... (функция в разработке)")
            pygame.time.wait(500)
        elif choice == "exit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
