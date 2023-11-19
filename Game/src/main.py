import asyncio
import sys

import pygame

from data.settings import *
from data.support import find_files
from game.game import Game

# initialise only needed
pygame.font.init()
pygame.mixer.init(channels=0)

# screen setup
# pygame.FULLSCREEN | pygame.SCALED (flags for fullscreen) # (vsync sets fps max to 60)
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height), flags=pygame.SCALED, vsync=1)
screen_surface = pygame.Surface((screen_width, screen_height))

# sets title as well as loads icon
pygame.display.set_caption("Treasure Hunters", "Treasure Hunters")
pygame_icon = pygame.image.load(find_files("./graphics/ui/icon.png"))
pygame.display.set_icon(pygame_icon)

# pygame setup
clock = pygame.time.Clock()
game = Game(screen_surface)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED,
                          pygame.JOYBUTTONDOWN])


async def main():
    # debug
    counter_1 = 0
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

            elif event.type == game.menu_wait:
                game.input_wait = False

            elif game.level and event.type == game.level.player.sprite.attack_timer:
                game.level.player.sprite.can_attack = True

            elif event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
                number_joys = pygame.joystick.get_count()
                current_controller = 0
                if number_joys > 0:
                    joysticks = [pygame.joystick.Joystick(x) for x in range(number_joys)]
                    for x in joysticks:
                        if x.get_name() not in controllers.keys():
                            joysticks.remove(x)
                            print(x.get_name() + ' is not a currently supported controller.')
                    if not joysticks:
                        joysticks = [None]
                else:
                    joysticks = [None]

            elif event.type == pygame.JOYBUTTONDOWN:
                game.controller = True
                current_controller = event.joy

        game.run(joysticks[current_controller])

        screen.blit(screen_surface, (0, 0))
        pygame.display.update()

        # DEBUGGING
        # if joysticks != [None]:
        #     counter_1 += 1
        #     if counter_1 >= 100:
        #         counter_1 = 0
        #         for x in range(joysticks[current_controller].get_numhats()):
        #             print('Hat ' + str(x))
        #             print(joysticks[current_controller].get_hat(x))
        #
        #         for x in range(joysticks[current_controller].get_numaxes()):
        #             print('Axis ' + str(x))
        #             print(joysticks[current_controller].get_axis(x))

        clock.tick(60)
        # fps = clock.get_fps()
        # if fps:
        #     print(fps)
        await asyncio.sleep(0)

asyncio.run(main())
# Setup Scalable Resolutions
