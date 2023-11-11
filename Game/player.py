import pygame.sprite

from particles import AttackEffect
from settings import controllers
from support import import_folder, import_loop, create_masks, find_files


# noinspection PyAttributeOutsideInit
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles, mute, create_overworld):
        super().__init__()
        self.animations = {}
        self.sword_effects = {}
        self.import_character_assets()
        self.frame_index = 0
        self.image = self.animations['09-Idle Sword'][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.collide_rect = self.rect.inflate(-94, -34)

        # dust particles
        self.import_dust_run_particles()
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
        self.status = '09-Idle Sword'
        self.facing_right = True
        self.on_ground = True
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.rebound = False
        self.knockback = False
        self.can_move = True
        self.dead = False

        # timers
        self.can_attack = True
        self.attack_timer = pygame.event.custom_type()
        self.create_overworld = create_overworld

        # surfaces and masks
        self.display_surface = surface
        self.attack = pygame.sprite.GroupSingle()
        self.mask_dict = {'09-Idle Sword': '01-Idle', '10-Run Sword': '02-Run', '11-Jump Sword': '03-Jump',
                          '12-Fall Sword': '04-Fall', '13-Ground Sword': '05-Ground', '14-Hit Sword': '06-Hit'}
        self.mask = self.mask_animations_right[self.mask_dict[self.status]][0]
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
        self.attack_data = {'15-Attack 1': ['24-Attack 1', False, 1300, pygame.Vector2(72, 2)],
                            '16-Attack 2': ['25-Attack 2', False, 1300, pygame.Vector2(50, 0)],
                            '17-Attack 3': ['26-Attack 3', False, 1300, pygame.Vector2(50, -10)],
                            '18-Air Attack 1': ['27-Air Attack 1', True, 500, pygame.Vector2(24, 48)],
                            '19-Air Attack 2': ['28-Air Attack 2', True, 500, pygame.Vector2(40, 30)]}

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

    def import_dust_run_particles(self):
        self.dust_run_particles = import_folder("./graphics/character/dust_particles/run")

    def animate(self):
        self.set_animation_speed()
        self.frame_index += self.animations_speed
        animation = self.animations[self.status]
        if self.frame_index >= len(animation):
            self.frame_index = 0
            self.reset_status()
            animation = self.animations[self.status]
        index = int(self.frame_index)
        self.image = animation[index]
        try:
            key = self.mask_dict[self.status]
        except KeyError:
            key = self.status
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            self.mask = self.mask_animations_left[key][index]
        else:
            self.mask = self.mask_animations_right[key][index]

    def set_animation_speed(self):
        if self.status == '10-Run Sword':
            self.animations_speed = 0.15
        else:
            self.animations_speed = 0.10

    def reset_status(self):
        if self.status == '07-Dead Hit':
            self.status = '08-Dead Ground'
        elif self.status == '08-Dead Ground':
            self.create_overworld()
        elif self.should_reset_status():
            self.knockback = False
            self.status = 'None'
            self.get_status()

    def should_reset_status(self):
        should_reset = ['14-Hit Sword', '15-Attack 1', '16-Attack 2', '17-Attack 3', '18-Air Attack 1',
                        '19-Air Attack 2', '07-Dead Hit', '08-Dead Ground']
        if self.status in should_reset:
            return True
        return False

    def get_status(self):
        if not self.should_reset_status():
            current = self.status
            if self.direction.y < 0:
                self.status = '11-Jump Sword'
            elif self.direction.y > 1:
                self.status = '12-Fall Sword'
            else:
                if self.direction.x == 0:
                    self.status = '09-Idle Sword'
                else:
                    self.status = '10-Run Sword'
            if self.status != current:
                self.can_move = True

    def knockback_init(self):
        self.frame_index = 0
        self.can_move = self.jump = self.rebound = False
        self.knockback = True
        self.status = '14-Hit Sword'

    def die(self):
        if not self.dead:
            self.frame_index = 0
            self.status = '07-Dead Hit'
            self.can_move = self.jump = False
            self.dead = True

    def dust_animate(self):
        if self.status == '10-Run Sword' and self.on_ground:
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
            if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.direction.y == 0:
                self.jump = True
                self.create_jump_particles(self.collide_rect.midbottom)
                self.channel.play(self.jump_sound)
            elif not (keys[pygame.K_SPACE] or keys[pygame.K_w]):
                if self.direction.y < -4 and not self.rebound:
                    self.direction.y = -4
                    self.jump = False
            # attacks
            if self.can_attack:
                if keys[pygame.K_q] and self.on_ground:
                    self.initiate_attack('15-Attack 1')
                elif keys[pygame.K_q] and not self.on_ground:
                    self.initiate_attack('18-Air Attack 1')
                elif keys[pygame.K_e] and self.on_ground:
                    self.initiate_attack('16-Attack 2')
                elif keys[pygame.K_e] and not self.on_ground:
                    self.initiate_attack('19-Air Attack 2')
                elif keys[pygame.K_r] and self.on_ground:
                    self.initiate_attack('17-Attack 3')

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
                    self.direction.y == 0):
                self.jump = True
                self.create_jump_particles(self.collide_rect.midbottom)
                self.channel.play(self.jump_sound)
            elif not (joystick.get_button(controller['cross']) or joystick.get_button(controller['up_pad'])):
                if self.direction.y < -4 and not self.rebound:
                    self.direction.y = -4
                    self.jump = False
            # attacks
            if self.can_attack:
                if joystick.get_button(controller['square']) and self.on_ground:
                    self.initiate_attack('15-Attack 1')
                if joystick.get_button(controller['square']) and not self.on_ground:
                    self.initiate_attack('18-Air Attack 1')
                elif joystick.get_button(controller['triangle']) and self.on_ground:
                    self.initiate_attack('16-Attack 2')
                elif joystick.get_button(controller['triangle']) and not self.on_ground:
                    self.initiate_attack('19-Air Attack 2')
                elif joystick.get_button(controller['circle']) and self.on_ground:
                    self.initiate_attack('17-Attack 3')

    def initiate_attack(self, status):
        self.status = status
        attack = self.attack_data[status]
        self.can_attack = False
        self.can_move = attack[1]
        self.frame_index = 0
        pygame.time.set_timer(self.attack_timer, attack[2])
        self.attack.add(AttackEffect(self, self.sword_effects[attack[0]], should_flip=not self.facing_right,
                                     facing=self.facing_right,
                                     right_mask=self.mask_sword_effects_right[attack[0]],
                                     left_mask=self.mask_sword_effects_left[attack[0]],
                                     offset=attack[3], type=attack[0]))

    def apply_gravity(self):
        if self.jump:
            self.direction.y += self.jump_speed
            if self.direction.y <= -7 and not self.rebound:
                self.jump = False
            elif self.direction.y <= -9:
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
            self.attack.draw(self.display_surface)
        self.animate()
        self.dust_animate()
