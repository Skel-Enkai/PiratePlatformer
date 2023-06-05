import pygame
import math
from support import import_folder


# noinspection PyAttributeOutsideInit
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles):
        super().__init__()
        self.import_character_assets()
        self.frame_index = 0
        self.animations_speed = 0.10
        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect(topleft=pos)
        self.rect = self.rect.inflate(-55, 0)

        # dust particles
        self.import_dust_run_particles()
        self.dust_frame_index = 0
        self.dust_animations_speed = 0.15
        self.display_surface = surface
        self.create_jump_particles = create_jump_particles

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 1.8
        self.gravity = 0.4
        self.jump_speed = -2
        self.jump = False

        # player status
        self.status = 'idle'
        self.facing_right = True
        self.on_ground = True
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.rebound = False
        self.knockback = False
        self.can_move = True

    def import_character_assets(self):
        character_path = '../graphics/character/'
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'hit': [], 'attack1': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def import_dust_run_particles(self):
        self.dust_run_particles = import_folder("../graphics/character/dust_particles/run")

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animations_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
            self.reset_status()
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
        should_reset = ['hit', 'attack1']
        for anim in should_reset:
            if self.status == anim:
                return False
        return True

    def knockback_init(self):
        self.frame_index = 0
        self.can_move = False
        self.jump = False
        self.knockback = True
        self.status = 'hit'

    def dust_animate(self):
        if self.status == 'run' and self.on_ground:
            self.dust_frame_index += self.dust_animations_speed
            if self.dust_frame_index >= len(self.dust_run_particles):
                self.dust_frame_index = 0

            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

            if self.facing_right:
                pos = self.rect.bottomleft - pygame.math.Vector2(15, 12)
                self.display_surface.blit(dust_particle, pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(-3, 12)
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
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.direction.x <= 2:
                self.direction.x += 0.4
                self.facing_right = True
            elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.direction.x >= -2:
                self.direction.x -= 0.4
                self.facing_right = False

            if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.direction.y == 0:
                self.jump = True
                self.create_jump_particles(self.rect.midbottom)
            elif not (keys[pygame.K_SPACE] or keys[pygame.K_w]):
                if self.direction.y < -4 and not self.rebound:
                    self.direction.y = -4
                    self.jump = False
                elif self.direction.y < -6 and self.rebound:
                    self.direction.y = -6
                    self.jump = False

    def joystick_input(self, joystick):
        if joystick.get_name() == "PS5 Controller" and self.can_move:
            if joystick.get_button(14) and self.direction.x <= 2:
                self.direction.x += 0.4
                self.facing_right = True
            elif joystick.get_button(13) and self.direction.x >= -2:
                self.direction.x -= 0.4
                self.facing_right = False

            if (joystick.get_button(0) or joystick.get_button(11)) and self.direction.y == 0:
                self.jump = True
                self.create_jump_particles(self.rect.midbottom)
            elif not (joystick.get_button(0) or joystick.get_button(11)):
                if self.direction.y < -4 and not self.rebound:
                    self.direction.y = -4
                    self.jump = False
                elif self.direction.y < -6 and self.rebound:
                    self.direction.y = -6
                    self.jump = False

    def get_status(self):
        current = self.status
        self.animations_speed = 0.10
        if self.should_reset_status():
            if self.direction.y < 0:
                self.status = 'jump'
            elif self.direction.y > 1:
                self.status = 'fall'
                self.rebound = False
            else:
                if self.direction.x == 0:
                    self.status = 'idle'
                else:
                    self.status = 'run'
                    self.animations_speed = 0.15
        if self.status != current:
            self.frame_index = 0

    def apply_gravity(self):
        if self.jump:
            self.direction.y += self.jump_speed
            if self.direction.y <= -12:
                self.jump = False
        else:
            self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def reset_x(self):
        if self.direction.x >= 0.4:
            self.direction.x -= 0.3
        elif self.direction.x <= -0.4:
            self.direction.x += 0.3
        else:
            self.direction.x = 0

    def bounce(self, enemy):
        self.jump = True
        self.direction.y = 0
        self.rect.bottom = enemy.rect.top

    def head_collision(self):
        self.rect.y += -self.direction.y
        self.direction.y = -(self.direction.y // 4)
        self.direction.x = -self.direction.x

    def slow_fall_collision(self, enemy_speed):
        self.rebound = True
        self.rect.y += -10
        self.direction.y = -7
        self.direction.x = enemy_speed

    def standard_collision(self, enemy):
        if math.copysign(1, enemy.speed) != math.copysign(1, self.direction.x) \
                or self.direction.x == 0:
            force = (-self.direction.x + enemy.speed) / 2 + math.copysign(2, enemy.speed)
            enemy.speed *= -1
        else:
            force = (-self.direction.x) - math.copysign(2, enemy.speed)
        self.direction.x = force
        self.rect.x += force
        self.direction.y = -1 * abs(force)

    def draw(self):
        pygame.Surface.blit(self.display_surface, self.image, self.rect.move(-28, 0))
        self.dust_animate()
        # pygame.draw.rect(self.display_surface, 'Red', self.rect)

    def update(self, joystick, controller):
        self.control_player(joystick, controller)
        self.reset_x()
        self.get_status()
        self.animate()
