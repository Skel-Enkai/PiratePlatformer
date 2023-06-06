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
joysticks = []
current_controller = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            game.controller = False
        elif event.type == game.switch_overworld:
            game.overworld.wait = False
        elif game.level:
            if event.type == game.level.player.sprite.attack_timer:
                game.level.player.sprite.can_attack = True
        elif event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
            joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        elif event.type == pygame.JOYBUTTONDOWN:
            game.controller = True
            current_controller = event.joy
            print(event)

    if joysticks:
        game.run(joysticks[current_controller])
    else:
        game.run()
    screen.blit(screen_surface, (0, 0))
    pygame.display.update()
    clock.tick(60)
    fps = clock.get_fps()
    if fps < 58:
        pass
        print(fps)

# Setup Scalable Resolutions
