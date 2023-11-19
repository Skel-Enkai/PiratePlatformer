import pygame.sprite

from decoration import *
from enemy import FierceTooth, Crabby
from game_data import *
from particles import Effect
from player import Player
from settings import screen_height, screen_width
from support import import_csv_layout, import_cut_graphic
from tiles import *


# noinspection PyAttributeOutsideInit,PyTypeChecker,PyUnboundLocalVariable
class Level:
    def __init__(self, level_number, surface, create_overworld, change_coins, change_cur_health, mute):
        # attributes
        self.create_overworld = create_overworld
        self.level_number = level_number
        level_data = levels[level_number]
        self.new_max_level = level_data['unlock']
        self.display_surface = surface

        # audio
        self.effects_channel = pygame.mixer.Channel(2)
        if mute:
            self.effects_channel.set_volume(0.0)
        else:
            self.effects_channel.set_volume(0.2)
        self.coin_sound = pygame.mixer.Sound(find_files('./audio/effects/coin.wav'))
        self.stomp_sound = pygame.mixer.Sound(find_files('./audio/effects/stomp.wav'))

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, mute, create_overworld)
        self.player_speed = self.player.sprite.speed.copy()
        self.player_current_x = 0

        # user interface
        self.change_coins = change_coins
        self.change_cur_health = change_cur_health

        # "camera"
        self.world_shift = pygame.Vector2(0, 0)
        self.world_offset = pygame.Vector2(0, 0)

        # level dict
        self.level_sprites = {'terrain': pygame.sprite.Group(), 'terrain_collidable': pygame.sprite.Group(),
                              'grass': pygame.sprite.Group(), 'crates': pygame.sprite.Group(),
                              'coins': pygame.sprite.Group(), 'fg palms': pygame.sprite.Group(),
                              'bg palms': pygame.sprite.Group(), 'enemies': pygame.sprite.Group(),
                              'constraints': pygame.sprite.Group()}

        for key in level_data.keys():
            if key not in ('node_pos', 'unlock', 'node_graphics', 'player'):
                layout = import_csv_layout(level_data[key])
                self.level_sprites[key] = self.create_tile_group(layout, key)
                if key == 'terrain':
                    self.world_length = len(layout[0]) * tile_size
                    self.world_height = len(layout) * tile_size
                    self.level_sprites['terrain_collidable'] = self.create_tile_group(layout, 'terrain_collidable')

        # decoration
        self.sky = Sky(7)
        self.water = Water(screen_height - 40, self.world_length, 0.06)
        self.cloud = Clouds(7, self.world_length, randint(2, 14))

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = True

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()
        identifier = 0

        for row_index, row in enumerate(layout):
            y = tile_size * row_index
            y += self.initial_offset.y
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = tile_size * col_index
                    x += self.initial_offset.x

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
                        if val == '0':
                            sprite = FierceTooth(x, y, self.display_surface, self.player, identifier)
                        elif val == '1':
                            sprite = Crabby(x, y, self.display_surface, self.player, identifier)
                        identifier += 1

                    elif type == 'constraints':
                        sprite = Tile(tile_size, x, y)

                    try:
                        sprite_group.add(sprite)
                    except ValueError:
                        print('Tried to add object of type ' + type + ' with val ' + val + ' but no object found.')

        return sprite_group

    def player_setup(self, layout, mute, create_overworld):
        for row_index, row in enumerate(layout):
            y = tile_size * row_index
            for col_index, val in enumerate(row):
                x = tile_size * col_index
                if val == '0':
                    sprite = Player((x, y), self.display_surface, self.create_jump_particles, mute,
                                    create_overworld)
                    self.set_initial_world_offset(x, y)
                    sprite.collide_rect.center += self.initial_offset
                    sprite.collide_rect.centerx -= 32
                    self.player.add(sprite)
                elif val == '1':
                    hat_surface = pygame.image.load(find_files('./graphics/character/hat.png')).convert_alpha()
                    sprite = StaticTile(tile_size, x + 8, y + 38, hat_surface)
                    self.goal.add(sprite)
        self.goal.sprite.rect.center += self.initial_offset

    def set_initial_world_offset(self, x, y):
        start_pos = (x, y)
        end_pos = (200, 400)
        x = (end_pos[0] - start_pos[0])
        y = (end_pos[1] - start_pos[1])
        direction = pygame.Vector2(x, y)
        self.initial_offset = pygame.Vector2(0, 0)
        if start_pos[0] > screen_width:
            self.initial_offset.x = direction.x
        if start_pos[1] > screen_height:
            self.initial_offset.y = direction.y
        self.world_offset = self.initial_offset

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
            pos = self.player.sprite.collide_rect.midbottom
            fall_dust_particle = Effect(pos, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def update_world_shift(self):
        self.scroll_x()
        self.scroll_y()

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.collide_rect.centerx
        direction_x = player.direction.x
        speed = round(player.direction.x * self.player_speed.x)

        if player_x < (screen_width // 3) and direction_x < 0 and self.world_offset.x < 0:
            player.speed.x = 0
            self.world_shift.x = -speed
            self.world_offset.x -= speed

        elif player_x > (screen_width // (3 / 2)) and direction_x > 0 and \
                self.world_length >= -self.world_offset.x + screen_width:
            self.world_shift.x = -speed
            self.world_offset.x -= speed
            player.speed.x = 0

        else:
            self.world_shift.x = 0
            player.speed.x = self.player_speed.x

    def scroll_y(self):
        player = self.player.sprite
        player_y = player.collide_rect.centery

        direction_y = player.direction.y
        speed = round(player.direction.y * self.player_speed.y)

        if player_y < (screen_height // 3) and direction_y < 0 <= self.world_offset.y:
            player.speed.y = 0
            self.world_shift.y = -speed
            self.world_offset.y -= speed

        elif player_y > (screen_height // (3 / 2)) and direction_y > 0 and self.world_offset.y > 0:
            self.world_shift.y = -speed
            self.world_offset.y -= speed
            player.speed.y = 0

        else:
            self.world_shift.y = 0
            player.speed.y = self.player_speed.y

    def horizontal_movement_collision(self):
        player = self.player.sprite
        if (player.collide_rect.left > 0 and not player.direction.x > 0) or \
                (player.collide_rect.right < screen_width and not player.direction.x < 0):
            # print('player speed=' + str(player.speed))
            # print('player.direction.x =' + str(player.direction.x))
            player.collide_rect.x += round(player.direction.x * player.speed.x)
            # print(round(player.direction.x * player.speed))

        for sprite in self.level_sprites['crates'].sprites():
            if sprite.hitbox_rect.colliderect(player.collide_rect):
                if not ((player.collide_rect.bottom < sprite.rect.top - 10) or
                        (player.collide_rect.top > sprite.rect.bottom + 10)):
                    if player.direction.x < 0:
                        player.collide_rect.left = sprite.hitbox_rect.right
                        player.on_left = True
                        self.player_current_x = player.collide_rect.left
                    elif player.direction.x > 0:
                        player.collide_rect.right = sprite.hitbox_rect.left
                        player.on_right = True
                        self.player_current_x = player.collide_rect.right

        if player.on_left and (player.collide_rect.left < self.player_current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.collide_rect.right > self.player_current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        self.get_player_on_ground()

        for sprite in self.level_sprites['crates'].sprites():
            if sprite.hitbox_rect.colliderect(player.collide_rect):
                if player.direction.y < 0:
                    player.collide_rect.top = sprite.hitbox_rect.bottom
                    player.direction.y = 0.4
                    player.on_ceiling = True
                elif player.direction.y > 0 and player.collide_rect.bottom <= sprite.rect.top + 10 + player.direction.y:
                    player.collide_rect.bottom = sprite.hitbox_rect.top
                    player.direction.y = 0
                    player.on_ground = True

        for sprite in self.level_sprites['terrain_collidable'].sprites():
            if sprite.rect.inflate(-18, 0).colliderect(player.collide_rect):
                if player.direction.y > 0.4 and player.collide_rect.bottom <= sprite.rect.top + 10 + player.direction.y:
                    player.collide_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True

        for sprite in self.level_sprites['fg palms'].sprites():
            if sprite.rect.inflate(-22, 0).move(10, 0).colliderect(player.collide_rect):
                if player.direction.y > 0.4 and player.collide_rect.bottom <= sprite.rect.top + 10 + player.direction.y:
                    player.collide_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True

        self.create_landing_dust()

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0 or player.direction.y < 1:
            player.on_ceiling = False

    def enemy_collision_boundary(self):
        enemy_sprites = self.level_sprites['enemies']
        constraint_sprites = self.level_sprites['constraints']
        for enemy in enemy_sprites:
            enemy.constraints = []

        collisions = pygame.sprite.groupcollide(enemy_sprites, constraint_sprites, False, False,
                                                collided=pygame.sprite.collide_rect_ratio(0.8))
        for enemy in collisions.keys():
            enemy.constraints += collisions[enemy]

        collisions_self = pygame.sprite.groupcollide(enemy_sprites, enemy_sprites, False, False)

        for enemy in collisions_self.keys():
            for collided in collisions_self[enemy]:
                if collided.identifier != enemy.identifier:
                    enemy.constraints.append(collided)

    def check_death(self):
        if self.player.sprite.rect.y > screen_height + 400:
            self.change_cur_health(-100)
            self.create_overworld()

    def check_win(self):
        if self.goal.sprite.rect.colliderect(self.player.sprite.collide_rect):
            self.create_overworld(self.new_max_level)

    # add generate masks on load
    def check_coin_collisions(self):
        player = self.player.sprite
        collided_coins = pygame.sprite.spritecollide(player, self.level_sprites['coins'], True,
                                                     pygame.sprite.collide_mask)
        if collided_coins:
            self.effects_channel.play(self.coin_sound)
            for coin in collided_coins:
                self.change_coins(coin.value)

    def player_enemy_collision(self, player, enemy, joystick):
        if not player.knockback:
            self.change_cur_health(-25)
            player.knockback_init()
            if player.direction.y < -2 and (enemy.rect.top <= player.collide_rect.top):
                player.head_collision()
            elif player.direction.y > 1:
                player.fall_collision(enemy.collide_rect.centerx)
            else:
                player.standard_collision(enemy.collide_rect.centerx)
            # joystick rumble
            if joystick:
                joystick.rumble(1, 1, 300)

    def check_player_attack_hits(self, player, enemy):
        if player.attack.sprite is not None:
            if pygame.sprite.collide_mask(player.attack.sprite, enemy):
                if player.attack.sprite.type in ('27-Air Attack 1', '28-Air Attack 2'):
                    player.bounce()
                    enemy.damage(-60)
                    self.effects_channel.play(self.stomp_sound)
                else:
                    enemy.damage(-50)

    def check_enemy_attack_hits(self, enemy, player):
        if enemy.attack_effect.sprite is not None:
            if pygame.sprite.collide_mask(player, enemy.attack_effect.sprite):
                # add more flair to this interaction
                self.change_cur_health(-30)
                player.knockback_init()

    def check_enemy_collisions(self, joystick):
        player = self.player.sprite
        for enemy in self.level_sprites['enemies']:
            if not enemy.dying:
                if pygame.Rect.colliderect(enemy.collide_rect, player.collide_rect):
                    self.player_enemy_collision(player, enemy, joystick)
                if not enemy.knockback:
                    self.check_player_attack_hits(player, enemy)
                if not player.knockback:
                    self.check_enemy_attack_hits(enemy, player)

    def draw(self):
        self.sky.draw(self.display_surface)
        self.cloud.draw(self.display_surface, self.world_shift)
        self.level_sprites['bg palms'].draw(self.display_surface)
        self.level_sprites['terrain'].draw(self.display_surface)
        self.level_sprites['grass'].draw(self.display_surface)
        self.level_sprites['crates'].draw(self.display_surface)
        self.level_sprites['coins'].draw(self.display_surface)
        self.level_sprites['enemies'].draw(self.display_surface)
        self.dust_sprite.draw(self.display_surface)
        self.player.draw(self.display_surface)
        self.level_sprites['fg palms'].draw(self.display_surface)
        self.goal.draw(self.display_surface)
        # updates and draws together, could split for threading
        self.water.draw(self.display_surface, self.world_shift)

        # DEBUGGING

        # collide_rects debug
        # player = self.player.sprite
        # self.display_surface.blit(player.mask.to_surface(unsetcolor=None, setcolor='Red'), player.rect)
        # debug_collide_rect = pygame.Surface((player.collide_rect.width, player.collide_rect.height))
        # debug_collide_rect.fill(pygame.Color(255, 0, 0))
        # debug_collide_rect.set_alpha(150)
        # self.display_surface.blit(debug_collide_rect, player.collide_rect)

        # pygame.draw.rect(self.display_surface, 'red', self.player.sprite.rect)
        # pygame.draw.rect(self.display_surface, 'red', player.collide_rect)
        # for enemy in self.level_sprites['enemies']:
        #    self.display_surface.blit(enemy.mask.to_surface(unsetcolor=None, setcolor='Red'), enemy.rect)
        #    pygame.draw.rect(self.display_surface, 'red', enemy.collide_rect)

        # attack effects debug
        # player = self.player.sprite
        # if player.status == '15-Attack 1':
        #     self.display_surface.blit(player.attack.sprite.mask.to_surface(unsetcolor=None, setcolor='Red'),
        #                               player.attack.sprite.rect)
        # for enemy in self.enemy_sprites:
        #     if enemy.status == '07-Attack' and enemy.attack_effect.sprite is not None:
        #         self.display_surface.blit(enemy.attack_effect.sprite.mask.to_surface(unsetcolor=None, setcolor='Red'),
        #                                   enemy.attack_effect.sprite.rect)

    def update(self, joystick, controller):
        self.update_world_shift()
        self.level_sprites['bg palms'].update(self.world_shift)
        self.level_sprites['terrain'].update(self.world_shift)
        self.level_sprites['terrain_collidable'].update(self.world_shift)
        self.level_sprites['grass'].update(self.world_shift)
        self.level_sprites['crates'].update(self.world_shift)
        self.level_sprites['coins'].update(self.world_shift)
        self.level_sprites['constraints'].update(self.world_shift)
        self.level_sprites['enemies'].update(self.world_shift)
        self.enemy_collision_boundary()
        self.level_sprites['fg palms'].update(self.world_shift)
        self.goal.update(self.world_shift)
        self.dust_sprite.update(self.world_shift)
        # player and movement
        self.player.update(joystick, controller, self.world_shift)
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.player.sprite.rect.center = self.player.sprite.collide_rect.center
        # checks
        self.check_death()
        self.check_win()
        self.check_enemy_collisions(joystick)
        self.check_coin_collisions()

    def run(self, joystick, controller):
        self.draw()
        self.update(joystick, controller)
