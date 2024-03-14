import pygame.sprite

from data.settings import controllers
from data.support import import_folder, import_loop, create_masks, find_files
from levels.particles import AttackEffect, SwordProjectile


# TO DO: Fix can_move flag to be a dictionary lookup based on current status
# noinspection PyAttributeOutsideInit
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles, mute, create_overworld, swords, projectiles):
        super().__init__()
        self.animations = {}
        self.sword_effects = {}
        self.import_character_assets()
        self.frame_index = 0
        self.image = self.animations['09-Idle Sword'][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.collide_rect = self.rect.inflate(-94, -34)

        # dust particles
        self.dust_run_particles = import_folder("./graphics/character/dust_particles/run")
        self.dust_frame_index = 0
        self.dust_animations_speed = 0.15
        self.create_jump_particles = create_jump_particles

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = pygame.Vector2(1, 1)
        self.gravity = 0.28
        self.jump_speed = -1
        self.jump = False

        # player status
        self.status = 'Idle'
        self.prev_status = 'Idle'
        self.sword_dict = {'Idle': '09-Idle Sword', 'Run': '10-Run Sword', 'Jump': '11-Jump Sword',
                           'Fall': '12-Fall Sword', 'Ground': '13-Ground Sword', 'Hit': '14-Hit Sword'}
        self.nosword_dict = {'Idle': '01-Idle', 'Run': '02-Run', 'Jump': '03-Jump', 'Fall': '04-Fall',
                             'Ground': '05-Ground', 'Hit': '06-Hit'}
        # flags
        self.facing_right = True
        self.on_ground = True
        self.rebound = False
        self.knockback = False
        self.can_move = True
        self.dead = False
        self.ground_impact = False

        # timers
        self.can_attack = True
        self.can_air_attack = True
        self.attack_timer = pygame.event.custom_type()
        self.create_overworld = create_overworld

        # surfaces and masks
        self.display_surface = surface
        self.attack = pygame.sprite.GroupSingle()
        self.mask = self.mask_animations_right[self.nosword_dict['Idle']][0]
        self.mask.clear()

        # audio
        self.channel = pygame.mixer.Channel(3)
        if mute:
            self.channel.set_volume(0.0)
        else:
            self.channel.set_volume(0.2)
        self.jump_sound = pygame.mixer.Sound(find_files('./audio/effects/jump.wav'))
        self.hit_sound = pygame.mixer.Sound(find_files('./audio/effects/hit.wav'))

        # attack data
        self.attack_data = {'15-Attack 1': ['24-Attack 1', False, 1200, pygame.Vector2(72, 2), -40],
                            '16-Attack 2': ['25-Attack 2', False, 1200, pygame.Vector2(50, 0), -50],
                            '17-Attack 3': ['26-Attack 3', False, 1200, pygame.Vector2(50, -10), -50],
                            '18-Air Attack 1': ['27-Air Attack 1', True, None, pygame.Vector2(24, 48), -40],
                            '19-Air Attack 2': ['28-Air Attack 2', True, None, pygame.Vector2(40, 30), -70],
                            '20-Throw Sword': ['', False, 1200, pygame.Vector2(32, -8), -100]}
        self.swords = swords
        self.projectiles = projectiles

    def import_character_assets(self):
        sword_effects_path = './graphics/character/Sword Effects/'
        import_loop(sword_effects_path, self.sword_effects)

        character_no_sword_path = './graphics/character/Captain Clown Nose without Sword/'
        import_loop(character_no_sword_path, self.animations)

        character_path = './graphics/character/Captain Clown Nose with Sword/'
        import_loop(character_path, self.animations)

        self.mask_sword_effects_right = {}
        self.mask_sword_effects_left = {}
        create_masks(self.sword_effects, self.mask_sword_effects_right, self.mask_sword_effects_left)

        self.mask_animations_right = {}
        self.mask_animations_left = {}
        create_masks(self.animations, self.mask_animations_right, self.mask_animations_left,
                     exclude_masks=['09-Idle Sword', '10-Run Sword', '11-Jump Sword', '12-Fall Sword',
                                    '13-Ground Sword', '14-Hit Sword'])

    def animate(self):
        self.set_animation_speed()
        self.frame_index += self.animations_speed
        key = self.get_animation_key()
        animation = self.animations[key]
        if self.frame_index >= len(animation):
            self.frame_index = 0
            self.reset_status()
            key = self.get_animation_key()
            animation = self.animations[key]
        index = int(self.frame_index)
        self.image = animation[index]
        try:
            key = self.nosword_dict[self.status]
        except KeyError:
            key = self.status
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            self.mask = self.mask_animations_left[key][index]
        else:
            self.mask = self.mask_animations_right[key][index]

    def get_animation_key(self):
        if self.swords > 0:
            try:
                key = self.sword_dict[self.status]
            except KeyError:
                key = self.status
        else:
            try:
                key = self.nosword_dict[self.status]
            except KeyError:
                key = self.status
        return key

    def set_animation_speed(self):
        if self.status == 'Run':
            self.animations_speed = 0.15
        else:
            self.animations_speed = 0.10

    def reset_frame_index(self):
        if self.status != self.prev_status:
            self.frame_index = 0
        self.prev_status = self.status

    def reset_status(self):
        if self.status == '07-Dead Hit':
            self.status = '08-Dead Ground'
        elif self.status == '08-Dead Ground':
            self.dead_wait_counter = 0
            self.status = 'DEAD-WAIT'
        elif self.status == 'DEAD-WAIT':
            self.dead_wait_counter += 1
            if self.dead_wait_counter > 10:
                self.create_overworld()
        elif self.is_status_sticky():
            self.knockback = False
            self.status = 'None'
            self.get_status()

    def is_status_sticky(self):
        should_reset = ['Hit', 'Ground', '15-Attack 1', '16-Attack 2', '17-Attack 3', '18-Air Attack 1',
                        '19-Air Attack 2', '07-Dead Hit', '08-Dead Ground', 'DEAD-WAIT', '20-Throw Sword']
        if self.status in ['18-Air Attack 1', '19-Air Attack 2'] and self.on_ground:
            return False
        elif self.status in should_reset:
            return True
        return False

    def get_status(self):
        if not self.is_status_sticky():
            current = self.status
            if self.direction.y < 0:
                self.status = 'Jump'
            elif self.direction.y > 1:
                self.status = 'Fall'
            elif self.direction.x == 0:
                self.status = 'Idle'
            else:
                self.status = 'Run'
            if self.status != current:
                self.can_move = True

    def knockback_init(self, vector_push=None, rebound=False):
        self.can_move = self.jump = self.rebound = False
        self.knockback = True
        self.status = 'Hit'
        if rebound:
            self.rebound = True
        if vector_push:
            self.direction += vector_push

    def die(self):
        if not self.dead:
            self.frame_index = 0
            self.status = '07-Dead Hit'
            self.can_move = self.jump = False
            self.dead = True

    def dust_animate(self):
        if self.status == 'Run' and self.on_ground:
            self.dust_frame_index += self.dust_animations_speed
            if self.dust_frame_index >= len(self.dust_run_particles):
                self.dust_frame_index = 0

            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

            if self.facing_right:
                pos = self.collide_rect.bottomleft - pygame.math.Vector2(15, 10)
                self.display_surface.blit(dust_particle, pos)
            else:
                pos = self.collide_rect.bottomright - pygame.math.Vector2(0, 10)
                self.display_surface.blit(pygame.transform.flip(dust_particle, True, False), pos)

    def control_player(self, joystick, controller):
        if self.knockback and self.frame_index >= 2 and not self.dead:
            self.can_move = True
        if controller and joystick:
            self.joystick_input(joystick)
        else:
            self.keyboard_input()

    def keyboard_input(self):
        if self.can_move:
            keys = pygame.key.get_pressed()
            # movement
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.direction.x <= 3:
                self.direction.x += 0.2
                self.facing_right = True
            elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.direction.x >= -3:
                self.direction.x -= 0.2
                self.facing_right = False
            # jump
            if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
                self.jump = True
                self.create_jump_particles(self.collide_rect.midbottom)
                self.channel.play(self.jump_sound)
            elif not (keys[pygame.K_SPACE] or keys[pygame.K_w]):
                if self.direction.y < -4 and not self.rebound:
                    self.direction.y = -4
                    self.jump = False
            # attacks
            if self.swords > 0:
                if self.can_attack and self.on_ground:
                    if keys[pygame.K_q]:
                        self.initiate_attack('15-Attack 1')
                    elif keys[pygame.K_e]:
                        self.initiate_attack('16-Attack 2')
                    elif keys[pygame.K_r]:
                        self.initiate_attack('17-Attack 3')
                    elif keys[pygame.K_g]:
                        self.initiate_attack('20-Throw Sword')

                elif self.can_air_attack and not self.on_ground:
                    if keys[pygame.K_q]:
                        self.initiate_attack('18-Air Attack 1', True)
                    elif keys[pygame.K_e]:
                        self.initiate_attack('19-Air Attack 2', True)

    def joystick_input(self, joystick):
        controller = controllers[joystick.get_name()]
        if joystick.get_name() in controllers.keys() and self.can_move:
            # movement
            if joystick.get_button(controller['right_pad']) and self.direction.x <= 3:
                self.direction.x += 0.2
                self.facing_right = True
            elif joystick.get_button(controller['left_pad']) and self.direction.x >= -3:
                self.direction.x -= 0.2
                self.facing_right = False
            # jump
            if ((joystick.get_button(controller['cross']) or joystick.get_button(controller['up_pad'])) and
                    self.on_ground):
                self.jump = True
                self.create_jump_particles(self.collide_rect.midbottom)
                self.channel.play(self.jump_sound)
            elif not (joystick.get_button(controller['cross']) or joystick.get_button(controller['up_pad'])):
                if self.direction.y < -4 and not self.rebound:
                    self.direction.y = -4
                    self.jump = False
            # attacks
            if self.swords > 0:
                if self.can_attack and self.on_ground:
                    if joystick.get_button(controller['square']):
                        self.initiate_attack('15-Attack 1')
                    elif joystick.get_button(controller['triangle']):
                        self.initiate_attack('16-Attack 2')
                    elif joystick.get_button(controller['circle']):
                        self.initiate_attack('17-Attack 3')
                    elif joystick.get_button(controller['R1']):
                        self.initiate_attack('20-Throw Sword')

                elif self.can_air_attack and not self.on_ground:
                    if joystick.get_button(controller['square']):
                        self.initiate_attack('18-Air Attack 1', True)
                    elif joystick.get_button(controller['triangle']):
                        self.initiate_attack('19-Air Attack 2', True)

    def initiate_attack(self, status, air=False):
        self.status = status
        attack = self.attack_data[status]
        self.can_move = attack[1]
        if not air:
            self.can_attack = False
            pygame.time.set_timer(self.attack_timer, attack[2])
        else:
            self.can_air_attack = False

        if status != '20-Throw Sword':
            self.attack.add(AttackEffect(self, self.sword_effects[attack[0]], should_flip=not self.facing_right,
                                         facing=self.facing_right,
                                         right_mask=self.mask_sword_effects_right[attack[0]],
                                         left_mask=self.mask_sword_effects_left[attack[0]],
                                         offset=attack[3], type=attack[0], damage=attack[4]))
        else:
            self.swords -= 1
            self.projectiles.add(SwordProjectile(self.rect, facing=self.facing_right, offset=attack[3],
                                                 damage=attack[4]))

    def apply_gravity(self):
        if self.jump:
            self.direction.y += self.jump_speed
            if self.direction.y <= -7:
                self.jump = self.rebound = False
        else:
            self.direction.y += self.gravity
        self.collide_rect.y += (self.speed.y * self.direction.y)

    def reset_x(self):
        if self.direction.x >= 0.2:
            self.direction.x -= 0.1
        elif self.direction.x <= -0.2:
            self.direction.x += 0.1
        else:
            self.direction.x = 0

    def bounce(self):
        if self.can_move:
            self.jump = True
            self.rebound = True

    def head_collision(self):
        self.collide_rect.y += -self.direction.y
        self.direction.y = -(self.direction.y // 4)
        self.direction.x = -self.direction.x

    def fall_collision(self, enemy_x):
        self.direction.x = self.find_direction_collision(enemy_x)
        self.direction.y = -5

    def standard_collision(self, enemy_x):
        self.direction.x = self.find_direction_collision(enemy_x)
        self.direction.y = -4

    def find_direction_collision(self, enemy_x):
        if self.collide_rect.centerx >= enemy_x:
            return 2.8
        else:
            return -2.8

    def update(self, joystick, controller, world_shift):
        self.control_player(joystick, controller)
        self.reset_x()
        self.get_status()
        if self.attack:
            self.attack.update()
        self.reset_frame_index()
        self.animate()
