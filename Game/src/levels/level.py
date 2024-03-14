import pygame.sprite

from data.enums import Projectile
from data.game_data import *
from data.support import import_csv_layout, import_cut_graphic, find_vector_from_two_points
from game.player import Player
from levels.decoration import *
from levels.enemy import FierceTooth, Crabby
from levels.particles import Effect
from levels.tiles import *
from levels.traps import Cannon
from levels.treasure import *


# noinspection PyAttributeOutsideInit,PyTypeChecker,PyUnboundLocalVariable
class Level:
    def __init__(self, level_number, surface, create_overworld, change_coins, change_cur_health, state, mute):
        self.state = state
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

        # user interface
        self.change_coins = change_coins
        self.change_cur_health = change_cur_health

        # dust
        self.particle_effects = pygame.sprite.Group()

        # level dict
        self.projectiles = pygame.sprite.Group()
        self.level_sprites = {'terrain': pygame.sprite.Group(), 'terrain_collidable': pygame.sprite.Group(),
                              'grass': pygame.sprite.Group(), 'crates': pygame.sprite.Group(),
                              'treasure': pygame.sprite.Group(), 'fg palms': pygame.sprite.Group(),
                              'bg palms': pygame.sprite.Group(), 'enemies': pygame.sprite.Group(),
                              'constraints': pygame.sprite.Group(), 'traps': pygame.sprite.Group()}

        # "camera"
        self.world_shift = pygame.Vector2(0, 0)
        self.world_offset = pygame.Vector2(0, 0)

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, mute, create_overworld)
        self.player_speed = self.player.sprite.speed.copy()
        self.player_current_x = 0

        # world size
        self.world_size = (tile_size * len(player_layout), tile_size * len(player_layout[0]))

        # leveldata
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
        self.water = Water(self.world_size[0] - tile_size + 10 + self.initial_offset.y, self.world_length, 0.06)
        self.cloud = Clouds(7, self.world_length, randint(2, 14))

        # traps
        self.traps_timer = pygame.event.custom_type()
        if self.level_sprites['traps']:
            pygame.time.set_timer(self.traps_timer, 3000, loops=0)

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
                    match type:
                        case 'terrain':
                            terrain_tile_list = import_cut_graphic('./graphics/terrain/terrain_tiles.png')
                            tile_surface = terrain_tile_list[int(val)]
                            sprite = StaticTile(tile_size, x, y, tile_surface)

                        case 'terrain_collidable':
                            collide_list = ('0', '1', '2', '3', '12', '13', '14', '15')
                            for ident in collide_list:
                                if val == ident:
                                    terrain_tile_list = import_cut_graphic('./graphics/terrain/terrain_tiles.png')
                                    tile_surface = terrain_tile_list[int(val)]
                                    sprite = StaticTile(tile_size, x, y, tile_surface)

                        case 'grass':
                            grass_tile_list = import_cut_graphic('./graphics/decoration/grass/grass.png')
                            tile_surface = grass_tile_list[int(val)]
                            sprite = StaticTile(tile_size, x, y, tile_surface)

                        case 'crates':
                            sprite = Crate(tile_size, x, y)

                        case 'treasure':
                            if val == '0':
                                sprite = Coin(tile_size, x, y, './graphics/treasure/gold_coin', 5)
                            elif val == '1':
                                sprite = Coin(tile_size, x, y, './graphics/treasure/silver_coin', 1)
                            elif val == '2':
                                sprite = RedPotion(tile_size, x, y, self.change_cur_health)
                            elif val == '3':
                                sprite = Sword(tile_size, x, y + 10)

                        case 'fg palms':
                            if val == '0':
                                sprite = Palm(tile_size, x, y, './graphics/terrain/palm_small', 38)
                            elif val == '1':
                                sprite = Palm(tile_size, x, y, './graphics/terrain/palm_large', 72)

                        case 'bg palms':
                            sprite = Palm(tile_size, x, y, './graphics/terrain/palm_bg', 64)

                        case 'enemies':
                            if val == '0':
                                sprite = FierceTooth(x, y, self.display_surface, self.player, identifier)
                            elif val == '1':
                                sprite = Crabby(x, y, self.display_surface, self.player, identifier)
                            identifier += 1

                        case 'constraints':
                            sprite = Tile(tile_size, x, y)

                        case 'traps':
                            if val == '0':
                                sprite = Cannon(x, y, self.projectiles, self.particle_effects, False)
                            elif val == '1':
                                sprite = Cannon(x, y, self.projectiles, self.particle_effects, True)

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
                                    create_overworld, self.state.swords, self.projectiles)
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
        end_pos = (200, screen_height - 3 * tile_size)
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
        jump_particle_sprite = Effect(pos, "./graphics/character/dust_particles/jump", player_effect=True)
        self.particle_effects.add(jump_particle_sprite)

    def create_landing_dust(self):
        if self.player.sprite.ground_impact:
            pos = self.player.sprite.collide_rect.midbottom
            fall_dust_particle = Effect(pos, "./graphics/character/dust_particles/land", player_effect=True)
            self.particle_effects.add(fall_dust_particle)
            self.player.sprite.ground_impact = False

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

        if player_y < (screen_height // 3) and direction_y < 0:
            player.speed.y = 0
            self.world_shift.y = -speed
            self.world_offset.y -= speed

        elif (player_y > (screen_height // (3 / 2)) and direction_y > 0
              and -self.world_offset.y + screen_height + speed < self.world_size[0]):
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

                if player.direction.x > 0 and player.collide_rect.centerx < sprite.hitbox_rect.centerx:
                    player.collide_rect.right = sprite.hitbox_rect.left
                    self.player_current_x = player.collide_rect.right

                elif player.direction.x < 0 and player.collide_rect.centerx > sprite.hitbox_rect.centerx:
                    player.collide_rect.left = sprite.hitbox_rect.right
                    self.player_current_x = player.collide_rect.left

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.level_sprites['crates'].sprites():
            if sprite.hitbox_rect.inflate(-20, 0).colliderect(player.collide_rect):
                if self.check_upwards(player, sprite):
                    self.upwards_collision(player, sprite.hitbox_rect)
                elif self.check_downwards(player, sprite):
                    self.downwards_collision(player, sprite.hitbox_rect)

        for sprite in self.level_sprites['terrain_collidable'].sprites():
            if sprite.rect.inflate(-20, 0).colliderect(player.collide_rect) and self.check_downwards(player, sprite):
                self.downwards_collision(player, sprite.rect)

        for sprite in self.level_sprites['fg palms'].sprites():
            if (sprite.rect.inflate(-30, 0).move(10, 0).colliderect(player.collide_rect)
                    and self.check_downwards(player, sprite)):
                self.downwards_collision(player, sprite.rect)

        self.create_landing_dust()
        self.check_player_on_ground(player)

    @staticmethod
    def check_downwards(player, sprite):
        return player.direction.y > 0 and player.collide_rect.bottom < sprite.rect.top + 10 + player.direction.y

    @staticmethod
    def downwards_collision(player, hitbox):
        if player.direction.y > 7 and player.status == 'Fall':
            player.ground_impact = True
            player.status = 'Ground'
            player.can_move = False
        player.collide_rect.bottom = hitbox.top
        player.direction.y = 0
        player.on_ground = True
        player.can_air_attack = True

    @staticmethod
    def check_upwards(player, sprite):
        return player.direction.y < 0 and player.collide_rect.top > sprite.rect.bottom - 10 + player.direction.y

    @staticmethod
    def upwards_collision(player, hitbox):
        player.collide_rect.top = hitbox.bottom
        player.direction.y = 1.0

    @staticmethod
    def check_player_on_ground(player):
        if player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

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

    def check_outofbounds_death(self):
        if self.player.sprite.rect.y > screen_height + 400:
            self.change_cur_health(-100)
            self.create_overworld()

    def check_win(self):
        if self.goal.sprite.rect.colliderect(self.player.sprite.collide_rect):
            if self.player.sprite.swords < 5:
                self.state.swords = self.player.sprite.swords
            else:
                self.state.swords = 5
            self.create_overworld(self.new_max_level)

    def check_treasure_collide(self):
        player = self.player.sprite
        collided_treasure = pygame.sprite.spritecollide(player, self.level_sprites['treasure'], False,
                                                        pygame.sprite.collide_mask)
        if collided_treasure:
            for treasure in collided_treasure:
                treasure.collect()
                if treasure.type == Treasure.Coin:
                    self.effects_channel.play(self.coin_sound)
                    self.change_coins(treasure.value)
                elif treasure.type == Treasure.Potion:
                    self.effects_channel.play(self.coin_sound)
                    treasure.consume()
                elif treasure.type == Treasure.Sword:
                    self.effects_channel.play(self.coin_sound)
                    player.swords += 1

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
            if joystick:
                joystick.rumble(1, 1, 300)

    def check_player_attack_hits(self, player, enemy):
        attack = player.attack.sprite
        if attack is not None:
            if pygame.sprite.collide_mask(attack, enemy):
                enemy.damage(attack.damage)
                if player.attack.sprite.type in ('27-Air Attack 1', '28-Air Attack 2'):
                    player.bounce()
                    self.effects_channel.play(self.stomp_sound)

    def check_enemy_attack_hits(self, enemy, player):
        if enemy.attack_effect.sprite is not None:
            if pygame.sprite.collide_mask(player, enemy.attack_effect.sprite):
                # add more flair to this interaction
                self.change_cur_health(enemy.attack_effect.sprite.damage)
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
        for enemy in self.level_sprites['traps']:
            if not enemy.destroyed:
                self.check_player_attack_hits(player, enemy)

    def check_projectile_collisions(self):
        collided_player = pygame.sprite.spritecollide(self.player.sprite, self.projectiles, False,
                                                      collided=pygame.sprite.collide_mask)
        for projectile in collided_player:
            if projectile.type == Projectile.CannonBall:
                if not projectile.exploded:
                    self.change_cur_health(-80)
                    vector = find_vector_from_two_points(projectile.rect.center, self.player.sprite.rect.center,
                                                         5)
                    self.player.sprite.direction = pygame.Vector2(0, 0)
                    self.player.sprite.knockback_init(vector, rebound=True)
                    projectile.explode()

        collided_enemy = pygame.sprite.groupcollide(self.level_sprites['enemies'], self.projectiles, False,
                                                    False, collided=pygame.sprite.collide_mask)
        for enemy in collided_enemy.keys():
            for projectile in collided_enemy[enemy]:
                if projectile.type == Projectile.Sword:
                    enemy.damage(projectile.damage)
                elif projectile.type == Projectile.CannonBall:
                    if not projectile.exploded:
                        enemy.damage(-80)
                        # vector = find_vector_from_two_points(projectile.rect.center, enemy.rect.center, 5)
                        # self.player.sprite.direction = pygame.Vector2(0, 0)
                        # self.player.sprite.knockback_init(vector, rebound=True)
                        projectile.explode()

        collided_traps = pygame.sprite.groupcollide(self.level_sprites['traps'], self.projectiles, False,
                                                    False, collided=pygame.sprite.collide_mask)
        for enemy in collided_traps.keys():
            for projectile in collided_traps[enemy]:
                if projectile.type == Projectile.Sword:
                    enemy.damage(projectile.damage)

    def draw(self):
        self.sky.draw(self.display_surface)
        self.cloud.draw(self.display_surface, self.world_shift)
        self.level_sprites['bg palms'].draw(self.display_surface)
        self.level_sprites['terrain'].draw(self.display_surface)
        self.level_sprites['grass'].draw(self.display_surface)
        self.level_sprites['crates'].draw(self.display_surface)
        self.level_sprites['treasure'].draw(self.display_surface)
        self.level_sprites['traps'].draw(self.display_surface)
        self.level_sprites['enemies'].draw(self.display_surface)
        self.particle_effects.draw(self.display_surface)
        # draws the player and it's elements {
        self.player.draw(self.display_surface)
        if self.player.sprite.attack:
            self.player.sprite.attack.draw(self.display_surface)
        self.player.sprite.dust_animate()
        # }
        self.projectiles.draw(self.display_surface)
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

    def update_scene(self):
        self.update_world_shift()
        self.level_sprites['bg palms'].update(self.world_shift)
        self.level_sprites['terrain'].update(self.world_shift)
        self.level_sprites['terrain_collidable'].update(self.world_shift)
        self.level_sprites['grass'].update(self.world_shift)
        self.level_sprites['crates'].update(self.world_shift)
        self.level_sprites['treasure'].update(self.world_shift)
        self.level_sprites['constraints'].update(self.world_shift)
        self.level_sprites['enemies'].update(self.world_shift)
        self.level_sprites['traps'].update(self.world_shift)
        self.projectiles.update(self.world_shift)
        self.enemy_collision_boundary()
        self.level_sprites['fg palms'].update(self.world_shift)
        self.goal.update(self.world_shift)
        self.particle_effects.update(self.world_shift)

    def update(self, joystick, controller):
        self.update_scene()
        # player and movement
        self.player.update(joystick, controller, self.world_shift)
        self.vertical_movement_collision()
        self.horizontal_movement_collision()
        self.player.sprite.rect.center = self.player.sprite.collide_rect.center
        # checks
        self.check_outofbounds_death()
        self.check_win()
        if not self.player.sprite.dead:
            self.check_enemy_collisions(joystick)
            self.check_projectile_collisions()
            self.check_treasure_collide()

    def run(self, joystick, controller):
        self.draw()
        self.update(joystick, controller)
