import asyncio
import sys

import pygame

from game import Game
from settings import *

# initialise only needed
pygame.font.init()
pygame.mixer.init(channels=0)

# screen setup
# pygame.FULLSCREEN | pygame.SCALED (flags for fullscreen) # (vsync sets fps max to 60)
screen = pygame.display.set_mode((screen_width, screen_height))
screen_surface = pygame.Surface((screen_width, screen_height))

# sets title as well as loads icon
pygame.display.set_caption("Treasure Hunters", "Treasure Hunters")
pygame_icon = pygame.image.load("./graphics/ui/icon.png")
pygame.display.set_icon(pygame_icon)

# pygame setup
clock = pygame.time.Clock()
game = Game(screen_surface)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.JOYDEVICEADDED,
                         pygame.JOYDEVICEREMOVED, pygame.JOYBUTTONDOWN])


async def main():
    joysticks = [None]
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

        game.run(joysticks[current_controller])

        screen.blit(screen_surface, (0, 0))
        pygame.display.update()

        # fps = clock.get_fps()
        # if fps:
        #     print(fps)

        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())
# Setup Scalable Resolutions
