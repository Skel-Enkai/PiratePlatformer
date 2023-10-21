import pygame.time

from level import Level
from overworld import Overworld
from ui import UI


class Game:
    def __init__(self, surface):
        # game attributes
        self.input_wait = False
        self.level = None
        self.current_level = 0
        self.max_level = 5
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0

        # surfaces
        self.screen_surface = surface

        # ui
        self.ui = UI(self.screen_surface)

        # controller
        self.controller = False

        # audio
        self.music = pygame.mixer.Channel(0)
        self.music.set_volume(0.1)
        self.overworld_music = pygame.mixer.Sound('./audio/overworld_music.wav')
        self.level_music = pygame.mixer.Sound('./audio/level_music.wav')

        self.channel_effects = pygame.mixer.Channel(1)
        self.channel_effects.set_volume(0.3)
        self.hit_sound = pygame.mixer.Sound('./audio/effects/hit.wav')

        self.mute_flag = False
        self.menu_wait = pygame.event.custom_type()

        # overworld creation
        self.overworld = Overworld(self.screen_surface, self.create_level, 0, self.max_level)
        self.status = 'overworld'
        self.switch_overworld = pygame.event.custom_type()
        pygame.time.set_timer(self.switch_overworld, 600)
        self.music.play(self.overworld_music, loops=-1)

    def create_level(self, current_level):
        self.current_level = current_level
        self.level = Level(current_level, self.screen_surface, self.create_overworld,
                           self.change_coins, self.change_cur_health, self.mute_flag)
        self.status = 'level'
        self.music.play(self.level_music, loops=-1)
        if self.mute_flag:
            pygame.mixer.pause()

    def create_overworld(self, new_max_level=0):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(self.screen_surface, self.create_level, self.current_level, self.max_level)
        self.status = 'overworld'
        pygame.time.set_timer(self.switch_overworld, 1200)
        self.music.play(self.overworld_music, loops=-1)
        if self.mute_flag:
            pygame.mixer.pause()

    def change_coins(self, amount):
        self.coins += amount

    def change_cur_health(self, amount):
        self.cur_health += amount
        self.channel_effects.play(self.hit_sound)

    def check_game_over(self):
        if self.cur_health <= 0:
            self.cur_health = 100
            self.coins = 0
            # self.max_level = 0 // uncomment for perma death
            # self.current_level 0 // uncomment for perma death
            self.create_overworld()

    def check_menu(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_m] and not self.input_wait:
            pygame.time.set_timer(self.menu_wait, 600)
            self.input_wait = True
            if not self.mute_flag:
                pygame.mixer.pause()
                self.mute_flag = True
                if self.level:
                    self.level.effects_channel.set_volume(0.0)
                    self.level.player.sprite.channel.set_volume(0.0)
            else:
                self.mute_flag = False
                pygame.mixer.unpause()
                if self.level:
                    self.level.effects_channel.set_volume(0.2)
                    self.level.player.sprite.channel.set_volume(0.2)

    def check_menu(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_m] and not self.input_wait:
            pygame.time.set_timer(self.menu_wait, 600)
            self.input_wait = True
            if not self.mute_flag:
                pygame.mixer.pause()
                self.mute_flag = True
                if self.level:
                    self.level.effects_channel.set_volume(0.0)
                    self.level.player.sprite.channel.set_volume(0.0)
            else:
                self.mute_flag = False
                pygame.mixer.unpause()
                if self.level:
                    self.level.effects_channel.set_volume(0.2)
                    self.level.player.sprite.channel.set_volume(0.2)

    def run(self, joystick=None):
        self.check_menu()
        if self.status == 'overworld':
            self.overworld.run(joystick, self.controller)
        elif self.status == 'level':
            self.level.run(joystick, self.controller)
            self.ui.show_health(self.cur_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()
