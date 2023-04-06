import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld
from ui import UI


class Game:
    def __init__(self):
        # game attributes
        self.level = None
        self.max_level = 5
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0

        # overworld creation
        self.overworld = Overworld(screen_surface, self.create_level, 0, self.max_level)
        self.status = 'overworld'
        self.switch_overworld = pygame.event.custom_type()
        self.wait = False

        # ui
        self.ui = UI(screen_surface)

    def create_level(self, current_level):
        self.level = Level(current_level, screen_surface, self.create_overworld,
                           self.change_coins, self.change_cur_health)
        self.status = 'level'

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(screen_surface, self.create_level, current_level, self.max_level)
        self.status = 'overworld'
        self.wait = True
        pygame.time.set_timer(self.switch_overworld, 600)

    def change_coins(self, amount):
        self.coins += amount

    def change_cur_health(self, amount):
        self.cur_health += amount

    def check_game_over(self):
        if self.cur_health <= 0:
            self.cur_health = 100
            self.coins = 0
            self.max_level = 0
            self.overworld = Overworld(screen_surface, self.create_level, 0, self.max_level)
            self.status = 'overworld'

    def run(self):
        if self.status == 'overworld' and not self.wait:
            self.overworld.run()
        elif self.status == 'level':
            self.level.run()
            self.ui.show_health(self.cur_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()
        else:
            self.overworld.draw()


# pygame.FULLSCREEN | pygame.SCALED (flags for fullscreen)
# Pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height), flags=pygame.FULLSCREEN | pygame.SCALED, vsync=1)
screen_surface = pygame.Surface((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()

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
            game.wait = False

    game.run()
    screen.blit(screen_surface, (0, 0))

    pygame.display.update()
    clock.tick(60)

# Setup Scalable Resolutions
