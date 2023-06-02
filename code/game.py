import pygame
from ui import UI
from level import Level
from overworld import Overworld
class Game:
    def __init__(self, surface):
        # game attributes
        self.level = None
        self.current_level = 0
        self.max_level = 5
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0
        self.screen_surface = surface

        # overworld creation
        self.overworld = Overworld(self.screen_surface, self.create_level, 0, self.max_level)
        self.status = 'overworld'
        self.switch_overworld = pygame.event.custom_type()
        pygame.time.set_timer(self.switch_overworld, 500)

        # ui
        self.ui = UI(self.screen_surface)

    def create_level(self, current_level):
        self.current_level = current_level
        self.level = Level(current_level, self.screen_surface, self.create_overworld,
                           self.change_coins, self.change_cur_health)
        self.status = 'level'

    def create_overworld(self, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(self.screen_surface, self.create_level, self.current_level, self.max_level)
        self.status = 'overworld'
        pygame.time.set_timer(self.switch_overworld, 1000)

    def change_coins(self, amount):
        self.coins += amount

    def change_cur_health(self, amount):
        self.cur_health += amount

    def check_game_over(self):
        if self.cur_health <= 0:
            self.cur_health = 100
            self.coins = 0
            # self.max_level = 0 // uncomment for perma death
            # self.current_level 0 // uncomment for perma death
            self.overworld = Overworld(self.screen_surface, self.create_level, self.current_level, self.max_level)
            self.status = 'overworld'

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        elif self.status == 'level':
            self.level.run()
            self.ui.show_health(self.cur_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()
