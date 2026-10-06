import pygame
from game.game_engine import GameEngine

pygame.init()

WIDTH, HEIGHT = 700, 500
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reaction Time Tester - Lab 4")

clock = pygame.time.Clock()
FPS = 60


def main():
    engine = GameEngine(WIDTH, HEIGHT)
    running = True

    while running:
        for event in pygame.event.get():
            action = engine.handle_event(event)
            if action == "quit":
                running = False

        engine.update()
        engine.render(SCREEN)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
