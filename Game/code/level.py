import pygame.sprite

from Game.code.decoration import *
from Game.code.enemy import FierceTooth
from Game.code.game_data import *
from Game.code.particles import Effect
from Game.code.player import Player
from Game.code.settings import screen_height, screen_width
from Game.code.support import import_csv_layout, import_cut_graphic
from Game.code.tiles import *


# noinspection PyAttributeOutsideInit,PyTypeChecker,PyUnboundLocalVariable
class Level:
    def __init__(self, level_number, surface, create_overworld, change_coins, change_cur_health):
        # attributes
        self.create_overworld = create_overworld
        self.level_number = level_number
        level_data = levels[level_number]
        self.new_max_level = level_data['unlock']

        self.world_shift = -2
        self.world_offset = 0
        self.current_x = 0

        # surface
        self.display_surface = surface

        # audio
        self.effects_channel = pygame.mixer.Channel(2)
        self.effects_channel.set_volume(0.2)
        self.coin_sound = pygame.mixer.Sound('./audio/effects/coin.wav')
        self.stomp_sound = pygame.mixer.Sound('./audio/effects/stomp.wav')

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)
        self.player_speed = self.player.sprite.speed

        # user interface
        self.change_coins = change_coins
        self.change_cur_health = change_cur_health

        # terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.world_length = len(terrain_layout[0]) * tile_size
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')
        self.terrain_collidable = self.create_tile_group(terrain_layout, 'terrain_collidable')

        # grass setup
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        # crates
        crate_layout = import_csv_layout(level_data['crates'])
        self.crate_sprites = self.create_tile_group(crate_layout, 'crates')

        # coins
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')

        # foreground palms
        fg_palm_layout = import_csv_layout(level_data['fg palms'])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout, 'fg palms')

        # background palms
        bg_palm_layout = import_csv_layout(level_data['bg palms'])
        self.bg_palm_sprites = self.create_tile_group(bg_palm_layout, 'bg palms')

        # enemies
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

        # constraint
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraint')

        # decoration
        self.sky = Sky(7)
        self.water = Water(screen_height - 40, self.world_length, 0.06)
        self.cloud = Clouds(7, self.world_length, randint(2, 14))

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = True

    @staticmethod
    def create_tile_group(layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            y = tile_size * row_index
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = tile_size * col_index

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphic('./graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'terrain_collidable':
                        collide_list = ('0', '1', '2', '3', '12', '13', '14', '15')
                        for ident in collide_list:
                            if val == ident:
                                terrain_tile_list = import_cut_graphic('./graphics/terrain/terrain_tiles.png')
                                tile_surface = terrain_tile_list[int(val)]
                                sprite = StaticTile(tile_size, x, y, tile_surface)

                    elif type == 'grass':
                        grass_tile_list = import_cut_graphic('./graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    elif type == 'crates':
                        sprite = Crate(tile_size, x, y)

                    elif type == 'coins':
                        if val == '0':
                            sprite = Coin(tile_size, x, y, './graphics/coins/gold', 5)
                        elif val == '1':
                            sprite = Coin(tile_size, x, y, './graphics/coins/silver', 1)

                    elif type == 'fg palms':
                        if val == '0':
                            sprite = Palm(tile_size, x, y, './graphics/terrain/palm_small', 38)
                        elif val == '1':
                            sprite = Palm(tile_size, x, y, './graphics/terrain/palm_large', 72)

                    elif type == 'bg palms':
                        sprite = Palm(tile_size, x, y, './graphics/terrain/palm_bg', 64)

                    elif type == 'enemies':
                        sprite = FierceTooth(tile_size, x, y)

                    elif type == 'constraint':
                        sprite = Tile(tile_size, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            y = tile_size * row_index
            for col_index, val in enumerate(row):
                x = tile_size * col_index
                if val == '0':
                    sprite = Player((x, y + 10), self.display_surface, self.create_jump_particles)
                    self.player.add(sprite)
                elif val == '1':
                    hat_surface = pygame.image.load('./graphics/character/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y + 38, hat_surface)
                    self.goal.add(sprite)

    def create_jump_particles(self, pos):
        jump_particle_sprite = Effect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            pos = self.player.sprite.rect.midbottom
            fall_dust_particle = Effect(pos, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x
        speed = round(player.direction.x * self.player_speed)

        if player_x < (screen_width // 3) and direction_x < 0 and self.world_offset < 0:
            player.speed = 0
            self.world_shift = -speed
            self.world_offset -= speed

        elif player_x > (screen_width - screen_width // 3) and direction_x > 0 and \
                self.world_length >= -self.world_offset + screen_width + 10:
            self.world_shift = -speed
            self.world_offset -= speed
            player.speed = 0

        else:
            self.world_shift = 0
            player.speed = self.player_speed

    def horizontal_movement_collision(self):
        player = self.player.sprite
        if (player.rect.left > 0 and not player.direction.x > 0) or \
                (player.rect.right < screen_width and not player.direction.x < 0):
            # print('player speed=' + str(player.speed))
            # print('player.direction.x =' + str(player.direction.x))
            player.rect.x += round(player.direction.x * player.speed)
            # print(round(player.direction.x * player.speed))

        for sprite in self.crate_sprites.sprites():
            if sprite.hitbox_rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.hitbox_rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.hitbox_rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        self.get_player_on_ground()

        for sprite in self.crate_sprites.sprites():
            if sprite.hitbox_rect.colliderect(player.rect):
                if player.direction.y < 0:
                    player.rect.top = sprite.hitbox_rect.bottom
                    player.direction.y = 0.4
                    player.on_ceiling = True
                elif player.direction.y > 0 and player.rect.bottom <= sprite.rect.top + 10 + player.direction.y:
                    player.rect.bottom = sprite.hitbox_rect.top
                    player.direction.y = 0
                    player.on_ground = True

        for sprite in self.terrain_collidable.sprites():
            if sprite.rect.inflate(-18, 0).colliderect(player.rect):
                if player.direction.y > 0.4 and player.rect.bottom <= sprite.rect.top + 10 + player.direction.y:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True

        for sprite in self.fg_palm_sprites.sprites():
            if sprite.rect.inflate(-22, 0).move(10, 0).colliderect(player.rect):
                if player.direction.y > 0.4 and player.rect.bottom <= sprite.rect.top + 10 + player.direction.y:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True

        self.create_landing_dust()

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0 or player.direction.y < 1:
            player.on_ceiling = False

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False,
                                           collided=pygame.sprite.collide_rect_ratio(0.5)):
                enemy.rect.x -= enemy.speed
                enemy.reverse()

    def check_death(self):
        if self.player.sprite.rect.top > screen_height + 400:
            self.change_cur_health(-100)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False, pygame.sprite.collide_rect_ratio(0.6)):
            self.create_overworld(self.new_max_level)

    def check_coin_collisions(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True,
                                                     pygame.sprite.collide_rect_ratio(0.6))
        if collided_coins:
            self.effects_channel.play(self.coin_sound)
            for coin in collided_coins:
                self.change_coins(coin.value)

    def player_enemy_collision(self, player, enemy, joystick):
        if (player.rect.bottom <= enemy.rect.top + 28 and player.direction.y > 5) or player.direction.y > 8:
            if player.direction.y > 9:
                enemy.damage(-35)
                self.effects_channel.play(self.stomp_sound)
            player.rebound = True
            player.bounce(enemy)
        elif not player.knockback:
            self.change_cur_health(-20)
            player.knockback_init()
            if player.direction.y < -2 and (enemy.rect.top <= player.rect.top):
                player.head_collision()
            elif player.direction.y > 1:
                player.slow_fall_collision(enemy.speed)
            else:
                player.standard_collision(enemy)
            # joystick rumble
            if joystick:
                joystick.rumble(1, 1, 300)

    @staticmethod
    def check_player_attack_hits(player, enemy):
        if player.attack_hitbox:
            if player.attack_hitbox.colliderect(enemy.collide_rect):
                enemy.damage(-70)

    def check_enemy_collisions(self, joystick):
        player = self.player.sprite
        for enemy in self.enemy_sprites:
            if not enemy.dying:
                if pygame.Rect.colliderect(enemy.collide_rect, player.rect):
                    self.player_enemy_collision(player, enemy, joystick)
                elif not enemy.knockback:
                    self.check_player_attack_hits(player, enemy)

    def draw(self):
        self.sky.draw(self.display_surface)
        self.cloud.draw(self.display_surface, self.world_shift)
        self.bg_palm_sprites.draw(self.display_surface)
        self.terrain_sprites.draw(self.display_surface)
        self.grass_sprites.draw(self.display_surface)
        self.crate_sprites.draw(self.display_surface)
        self.coin_sprites.draw(self.display_surface)
        self.enemy_sprites.draw(self.display_surface)
        self.dust_sprite.draw(self.display_surface)
        self.player.sprite.draw()
        self.fg_palm_sprites.draw(self.display_surface)
        self.goal.draw(self.display_surface)

        # updates and draws together, could split for threading
        self.water.draw(self.display_surface, self.world_shift)

        # for enemy in self.enemy_sprites:
        #     pygame.draw.rect(self.display_surface, 'red', enemy.collide_rect)

    def update(self, joystick, controller):
        self.scroll_x()
        self.bg_palm_sprites.update(self.world_shift)
        self.terrain_sprites.update(self.world_shift)
        self.terrain_collidable.update(self.world_shift)
        self.grass_sprites.update(self.world_shift)
        self.crate_sprites.update(self.world_shift)
        self.coin_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.fg_palm_sprites.update(self.world_shift)
        self.goal.update(self.world_shift)
        self.dust_sprite.update(self.world_shift)
        self.player.update(joystick, controller)
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        # checks
        self.check_death()
        self.check_win()
        self.check_enemy_collisions(joystick)
        self.check_coin_collisions()

    def run(self, joystick, controller):
        self.draw()
        self.update(joystick, controller)