import pygame.time

from data.settings import controllers, saveState
from data.support import find_files
from game.overworld import Overworld
from game.ui import UI
from levels.level import Level


class Game:
    def __init__(self, surface):
        self.input_wait = False
        self.level = None
        self.state = saveState()

        # misc
        self.screen_surface = surface
        self.ui = UI(self.screen_surface)
        self.controller = False

        # audio
        self.music = pygame.mixer.Channel(0)
        self.music.set_volume(0.1)
        self.overworld_music = pygame.mixer.Sound(find_files('./audio/overworld_music.wav'))
        self.level_music = pygame.mixer.Sound(find_files('./audio/level_music.wav'))

        self.channel_effects = pygame.mixer.Channel(1)
        self.channel_effects.set_volume(0.3)
        self.hit_sound = pygame.mixer.Sound(find_files('./audio/effects/hit.wav'))

        self.mute_flag = False
        self.menu_wait = pygame.event.custom_type()

        # overworld creation
        self.overworld = Overworld(self.screen_surface, self.create_level, self.state)
        self.status = 'overworld'
        self.switch_overworld = pygame.event.custom_type()
        pygame.time.set_timer(self.switch_overworld, 600)
        self.music.play(self.overworld_music, loops=-1)

    def create_level(self):
        self.level = Level(self.state.current_level, self.screen_surface, self.create_overworld,
                           self.change_coins, self.change_cur_health, self.state, self.mute_flag)
        self.pickle_state()
        self.status = 'level'
        self.music.play(self.level_music, loops=-1)
        if self.mute_flag:
            pygame.mixer.pause()

    def create_overworld(self, new_max_level=0):
        self.check_death()
        if new_max_level > self.state.max_level:
            self.state.max_level = new_max_level

        # create overworld and store game state in pickle
        self.overworld = Overworld(self.screen_surface, self.create_level, self.state)
        self.pickle_state()

        self.status = 'overworld'
        pygame.time.set_timer(self.switch_overworld, 1200)
        self.music.play(self.overworld_music, loops=-1)
        if self.mute_flag:
            pygame.mixer.pause()

    def pickle_state(self):
        pass

    def check_death(self):
        if self.state.cur_health <= 0:
            self.state.cur_health = 100
            self.state.coins = 0
            # self.max_level = 0 // uncomment for perma death
            # self.current_level = 0 // uncomment for perma death

    def change_coins(self, amount):
        self.state.coins += abs(amount)

    def change_cur_health(self, amount):
        self.state.cur_health += amount
        if amount < 0:
            self.channel_effects.play(self.hit_sound)
        elif self.state.cur_health > 100:
            self.state.cur_health = 100

    def check_game_over(self):
        if self.state.cur_health <= 0:
            self.level.player.sprite.die()

    def check_menu(self, joystick):
        keys = pygame.key.get_pressed()
        menu = False
        if joystick:
            controller = controllers[joystick.get_name()]
            menu = joystick.get_button(controller['menu'])

        if (keys[pygame.K_m] or menu) and not self.input_wait:
            pygame.time.set_timer(self.menu_wait, 600)
            self.input_wait = True
            if not self.mute_flag:
                pygame.mixer.pause()
                self.mute_flag = True
                self.channel_effects.set_volume(0.0)
                if self.level:
                    self.level.effects_channel.set_volume(0.0)
                    self.level.player.sprite.channel.set_volume(0.0)
            else:
                self.mute_flag = False
                pygame.mixer.unpause()
                self.channel_effects.set_volume(0.2)
                if self.level:
                    self.level.effects_channel.set_volume(0.2)
                    self.level.player.sprite.channel.set_volume(0.2)

        # debugging command
        if (keys[pygame.K_PERIOD] and keys[pygame.K_1]) and not self.input_wait:
            pygame.time.set_timer(self.menu_wait, 600)
            self.input_wait = True
            self.state.max_level = 5
            self.overworld = Overworld(self.screen_surface, self.create_level, self.state)

    def run(self, joystick=None):
        self.check_menu(joystick)
        if self.status == 'overworld':
            self.overworld.run(joystick, self.controller)
        elif self.status == 'level':
            self.level.run(joystick, self.controller)
            self.ui.show_health(self.state.cur_health, self.state.max_health)
            self.ui.show_coins(self.state.coins)
            self.ui.show_swords(self.level.player.sprite.swords)
            self.check_game_over()
