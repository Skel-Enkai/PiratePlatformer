import math

import pygame.sprite

from support import import_folder


# noinspection PyAttributeOutsideInit
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles, mute):
        super().__init__()
        self.import_character_assets()
        self.frame_index = 0
        self.animations_speed = 0.10
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
        self.speed = 1
        self.gravity = 0.32
        self.jump_speed = -2
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

        # timers
        self.can_attack = True
        self.attack_timer = pygame.event.custom_type()

        # surfaces
        self.display_surface = surface
        self.attack_hitbox = None

        # audio
        self.channel = pygame.mixer.Channel(3)
        if mute:
            self.channel.set_volume(0.0)
        else:
            self.channel.set_volume(0.2)
        self.jump_sound = pygame.mixer.Sound('./audio/effects/jump.wav')
        self.hit_sound = pygame.mixer.Sound('./audio/effects/hit.wav')

    def import_character_assets(self):
        character_path = './graphics/character/Captain Clown Nose with Sword/'
        self.animations = {'09-Idle Sword': [], '10-Run Sword': [], '11-Jump Sword': [], '12-Fall Sword': [],
                           '14-Hit Sword': [], '15-Attack 1': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)
            for index, frame in enumerate(self.animations[animation]):
                self.animations[animation][index] = pygame.transform.scale_by(frame, 2)

    def import_dust_run_particles(self):
        self.dust_run_particles = import_folder("./graphics/character/dust_particles/run")

    def animate(self):
        self.frame_index += self.animations_speed
        animation = self.animations[self.status]
        if self.frame_index >= len(animation):
            self.frame_index = 0
            self.reset_status()
            animation = self.animations[self.status]
        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image

    def reset_status(self):
        if not self.should_reset_status():
            self.knockback = False
            self.status = 'None'
            self.get_status()

    def should_reset_status(self):
        should_reset = ['14-Hit Sword', '15-Attack 1']
        for anim in should_reset:
            if self.status == anim:
                return False
        return True

    def knockback_init(self):
        self.frame_index = 0
        self.can_move = self.jump = False
        self.knockback = True
        self.status = '14-Hit Sword'

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
        if self.knockback and self.frame_index >= 2:
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
                elif self.direction.y < -6 and self.rebound:
                    self.direction.y = -6
                    self.jump = False
            # attacks
            if keys[pygame.K_q] and self.on_ground:
                self.stab()

    def joystick_input(self, joystick):
        if joystick.get_name() == "PS5 Controller" and self.can_move:
            # movement
            if joystick.get_button(14) and self.direction.x <= 3:
                self.direction.x += 0.2
                self.facing_right = True
            elif joystick.get_button(13) and self.direction.x >= -3:
                self.direction.x -= 0.2
                self.facing_right = False
            # jump
            if (joystick.get_button(0) or joystick.get_button(11)) and self.direction.y == 0:
                self.jump = True
                self.create_jump_particles(self.collide_rect.midbottom)
                self.channel.play(self.jump_sound)
            elif not (joystick.get_button(0) or joystick.get_button(11)):
                if self.direction.y < -4 and not self.rebound:
                    self.direction.y = -4
                    self.jump = False
                elif self.direction.y < -6 and self.rebound:
                    self.direction.y = -6
                    self.jump = False
            # attacks
            if joystick.get_button(2) and self.on_ground:
                self.stab()

    def stab(self):
        if self.can_attack:
            self.status = '15-Attack 1'
            self.can_move = self.can_attack = False
            self.frame_index = 0
            self.animations_speed = 0.10
            pygame.time.set_timer(self.attack_timer, 1000)
            self.attack_hitbox = pygame.Rect

    # update to function that can take multiple attack types
    def update_hitbox_stab(self):
        height, width, offset = 28, 40, 15
        if int(self.frame_index) == 1:
            width = 70
        if int(self.frame_index) == 2:
            width, offset = 30, 60
        self.attack_hitbox = pygame.Rect(self.rect.midbottom, (width, height))
        self.attack_hitbox.x += offset
        self.attack_hitbox.y -= (height + 1)
        if not self.facing_right:
            self.attack_hitbox.x -= (width + (offset * 2))

        if self.status != '15-Attack 1':
            self.attack_hitbox = None

    def get_status(self):
        if self.should_reset_status():
            current = self.status
            self.animations_speed = 0.10
            if self.direction.y < 0:
                self.status = '11-Jump Sword'
            elif self.direction.y > 1:
                self.status = '12-Fall Sword'
                self.rebound = False
            else:
                if self.direction.x == 0:
                    self.status = '09-Idle Sword'
                else:
                    self.status = '10-Run Sword'
                    self.animations_speed = 0.15
            if self.status != current:
                self.frame_index = 0
                self.can_move = True

    def apply_gravity(self):
        if self.jump:
            self.direction.y += self.jump_speed
            if self.direction.y <= -7:
                self.jump = False
        else:
            self.direction.y += self.gravity
        self.collide_rect.y += self.direction.y

    def reset_x(self):
        if self.direction.x >= 0.2:
            self.direction.x -= 0.1
        elif self.direction.x <= -0.2:
            self.direction.x += 0.1
        else:
            self.direction.x = 0

    def bounce(self, enemy):
        self.jump = True
        self.direction.y = 0
        self.collide_rect.bottom = enemy.collide_rect.top

    def head_collision(self):
        self.collide_rect.y += -self.direction.y
        self.direction.y = -(self.direction.y // 4)
        self.direction.x = -self.direction.x

    def slow_fall_collision(self, enemy_speed):
        self.rebound = True
        self.collide_rect.y += -10
        self.direction.y = -abs(self.direction.y)
        self.direction.x = enemy_speed

    def standard_collision(self, enemy):
        if math.copysign(1, enemy.speed) != math.copysign(1, self.direction.x) \
                or self.direction.x == 0:
            force = (-self.direction.x / 1.5) + enemy.speed
            enemy.speed *= -1
        else:
            force = (-self.direction.x / 1.5)
        self.direction.x = force
        self.collide_rect.x += force
        self.direction.y = -1 * abs(force)

    def update(self, joystick, controller):
        self.control_player(joystick, controller)
        self.reset_x()
        self.get_status()
        if self.attack_hitbox:
            self.update_hitbox_stab()
        self.animate()
        self.dust_animate()
