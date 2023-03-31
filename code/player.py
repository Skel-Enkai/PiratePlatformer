import pygame
from support import import_folder


# noinspection PyAttributeOutsideInit
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles):
        super().__init__()
        self.import_character_assets()
        self.frame_index = 0
        self.animations_speed = 0.15
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
        self.speed = 4
        self.gravity = 0.4
        self.jump_speed = -14

        # player status
        self.status = 'idle'
        self.facing_right = True
        self.on_ground = True
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.rebound = False

    def import_character_assets(self):
        character_path = '../graphics/character/'
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def import_dust_run_particles(self):
        self.dust_run_particles = import_folder("../graphics/character/dust_particles/run")

    def animate(self):
        animation = self.animations[self.status]

        # loop over frame index
        self.frame_index += self.animations_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image

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

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.direction.y == 0:
            self.jump()
            self.create_jump_particles(self.rect.midbottom)
        elif not (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.direction.y < -4 and not self.rebound:
            self.direction.y = -4
        elif not (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.direction.y < -8 and self.rebound:
            self.direction.y = -8

    def get_status(self):
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

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    def draw(self):
        pygame.Surface.blit(self.display_surface, self.image, self.rect.move(-28, 0))
        self.dust_animate()
        #  pygame.draw.rect(self.display_surface, 'Red', self.rect)

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
