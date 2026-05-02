import pygame
import sys
from settings import *
from menu import show_menu

def game_loop(screen):
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        
        screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        text = font.render("Игра запущена! Нажми ESC для возврата", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_W//2, SCREEN_H//2))
        screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    return True

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("PYdangeon - Overgrown Labyrinth")
    
    while True:
        choice = show_menu(screen)
        
        if choice == "start":
            if not game_loop(screen):
                break
        elif choice == "exit":
            break
        else:
            print(f"Выбрано: {choice}")
            pygame.time.wait(500)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
