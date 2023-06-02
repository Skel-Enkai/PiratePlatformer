import pygame
import sys
from settings import *
from game import Game

# pygame.FULLSCREEN | pygame.SCALED (flags for fullscreen) # (vsync sets fps max to 60)
# Pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height), flags=pygame.SCALED, vsync=1)
screen_surface = pygame.Surface((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game(screen_surface)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == game.switch_overworld:
            game.overworld.wait = False

    game.run()
    screen.blit(screen_surface, (0, 0))
    pygame.display.update()
    clock.tick(60)

# Setup Scalable Resolutions
