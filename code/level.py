import pygame.sprite
import math
from decoration import *
from enemy import Enemy
from game_data import *
from particles import Effect
from player import Player
from settings import screen_height, screen_width
from support import import_csv_layout, import_cut_graphic
from tiles import *


# noinspection PyAttributeOutsideInit,PyTypeChecker,PyUnboundLocalVariable
class Level:
    def __init__(self, level_number, surface, create_overworld, change_coins, change_cur_health):
        self.create_overworld = create_overworld
        self.display_surface = surface
        self.level_number = level_number
        level_data = levels[level_number]
        self.new_max_level = level_data['unlock']

        self.world_shift = -2
        self.world_offset = 0
        self.current_x = 0

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

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

        # enemy
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')
        self.enemy_effects = pygame.sprite.GroupSingle()

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
                        terrain_tile_list = import_cut_graphic('../graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'terrain_collidable':
                        collide_list = ('0', '1', '2', '3', '12', '13', '14', '15')
                        for ident in collide_list:
                            if val == ident:
                                terrain_tile_list = import_cut_graphic('../graphics/terrain/terrain_tiles.png')
                                tile_surface = terrain_tile_list[int(val)]
                                sprite = StaticTile(tile_size, x, y, tile_surface)

                    elif type == 'grass':
                        grass_tile_list = import_cut_graphic('../graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    elif type == 'crates':
                        sprite = Crate(tile_size, x, y)

                    elif type == 'coins':
                        if val == '0':
                            sprite = Coin(tile_size, x, y, '../graphics/coins/gold', 5)
                        elif val == '1':
                            sprite = Coin(tile_size, x, y, '../graphics/coins/silver', 1)

                    elif type == 'fg palms':
                        if val == '0':
                            sprite = Palm(tile_size, x, y, '../graphics/terrain/palm_small', 38)
                        elif val == '1':
                            sprite = Palm(tile_size, x, y, '../graphics/terrain/palm_large', 72)

                    elif type == 'bg palms':
                        sprite = Palm(tile_size, x, y, '../graphics/terrain/palm_bg', 64)

                    elif type == 'enemies':
                        sprite = Enemy(tile_size, x, y)

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
                    hat_surface = pygame.image.load('../graphics/character/hat.png').convert_alpha()
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
        speed = 2

        if player_x < (screen_width // 3) and direction_x < 0 and self.world_offset < 0:
            player.speed = 0
            self.world_shift = -round(player.direction.x * speed)
            self.world_offset -= round(player.direction.x * speed)

        elif player_x > (screen_width - screen_width // 3) and direction_x > 0 and \
                self.world_length >= -self.world_offset + screen_width + 10:
            self.world_shift = -round(player.direction.x * speed)
            self.world_offset -= round(player.direction.x * speed)
            player.speed = 0

        else:
            self.world_shift = 0
            player.speed = 2

    def horizontal_movement_collision(self):
        player = self.player.sprite
        if (player.rect.left > 0 and not player.direction.x > 0) or \
                (player.rect.right < screen_width and not player.direction.x < 0):
            # print('player speed=' + str(player.speed))
            # print('player.direction.x =' + str(player.direction.x))
            player.rect.x += round(player.direction.x * player.speed)

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
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def check_death(self):
        if self.player.sprite.rect.top > screen_height + 400:
            self.change_cur_health(-100)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False, pygame.sprite.collide_rect_ratio(0.6)):
            self.create_overworld(self.level_number, self.new_max_level)

    def check_coin_collisions(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True,
                                                     pygame.sprite.collide_rect_ratio(0.6))
        if collided_coins:
            for coin in collided_coins:
                self.change_coins(coin.value)

    def check_enemy_collisions(self):
        player = self.player.sprite
        for enemy in self.enemy_sprites:
            if pygame.sprite.spritecollide(enemy, self.player, False, collided=pygame.sprite.collide_rect_ratio(0.6)):
                if (player.rect.bottom <= enemy.rect.top + 28 and player.direction.y > 6) or player.direction.y > 8:
                    death_effect = Effect((enemy.rect.midbottom[0], enemy.rect.midbottom[1] - 12),
                                          'enemy_die', 0.1, enemy.speed)
                    self.enemy_effects.add(death_effect)
                    player.rebound = True
                    player.direction.y = -player.direction.y
                    enemy.kill()
                elif not player.knockback:
                    self.change_cur_health(-25)
                    if player.direction.y < -2:
                        player.rect.y += -player.direction.y
                        player.direction.y = -(player.direction.y//4)
                        player.direction.x = -player.direction.x
                        player.knockback = True
                    else:
                        # if you collide with enemy while it's walking away it will deal double damage, needs fix
                        force = (-player.direction.x + enemy.speed) + math.copysign(1, enemy.speed)
                        player.rect.x += force
                        player.direction.x = force
                        player.direction.y = -6
                        player.knockback = True
                        enemy.speed *= -1

    def run(self):
        self.scroll_x()

        # decoration
        self.sky.draw(self.display_surface)
        self.cloud.draw(self.display_surface, self.world_shift)

        # background palms
        self.bg_palm_sprites.update(self.world_shift)
        self.bg_palm_sprites.draw(self.display_surface)

        # level tiles
        self.terrain_sprites.update(self.world_shift)
        self.terrain_collidable.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        # grass
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)

        # crate
        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)

        # coins
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

        # enemy
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)
        self.enemy_effects.update(self.world_shift)
        self.enemy_effects.draw(self.display_surface)

        # dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # player
        self.player.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        self.player.sprite.draw()

        # foreground palms
        self.fg_palm_sprites.update(self.world_shift)
        self.fg_palm_sprites.draw(self.display_surface)

        # goal
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        # water
        self.water.draw(self.display_surface, self.world_shift)

        # checks
        self.check_death()
        self.check_win()
        self.check_enemy_collisions()
        self.check_coin_collisions()
