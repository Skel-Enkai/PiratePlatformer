import pygame.sprite

from support import import_folder


# noinspection PyAttributeOutsideInit
class Enemy(pygame.sprite.Sprite):
    def __init__(self, anim_speed=0.10):
        super().__init__()
        # attributes
        self.collide_rect = None
        self.speed = 1
        self.previous_speed = 0
        self.health = 100
        self.knockback = False
        self.dying = False

        self.frame_index = 0
        self.anim_speed = anim_speed

        # empty attributes
        self.rect = None
        self.death_frames = None
        self.knockback_frames = None
        self.run_frames = None

    def move(self):
        self.rect.x += self.speed

    def reverse(self):
        self.speed *= -1

    def damage(self, amount):
        if not self.knockback and not self.dying:
            self.health += amount
            self.frame_index = 0
            self.previous_speed = self.speed
            self.speed = 0
            if self.health <= 0:
                self.frames = self.death_frames
                self.rect.y -= 8
                self.dying = True
            else:
                self.frames = self.knockback_frames
                self.knockback = True

    def animate(self):
        self.frame_index += self.anim_speed
        if self.frame_index > len(self.frames):
            self.frame_index = 0
            if self.knockback:
                self.frames = self.run_frames
                self.speed = self.previous_speed
                self.previous_speed = 0
                self.knockback = False
            elif self.dying:
                self.kill()
        self.image = self.frames[int(self.frame_index)]
        if self.speed > 0 or self.previous_speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, x_shift):
        self.move()
        self.rect.x += x_shift
        self.collide_rect.centerx = self.rect.centerx
        self.animate()


class FierceTooth(Enemy):
    def __init__(self, size, x, y):
        super().__init__(anim_speed=0.10)
        self.run_frames = import_folder('../graphics/enemies/fierce_tooth/run')
        self.knockback_frames = import_folder('../graphics/enemies/fierce_tooth/hit')
        self.death_frames = import_folder('../graphics/enemies/fierce_tooth/dead_hit')
        self.death_frames += import_folder('../graphics/enemies/fierce_tooth/dead_ground')
        self.frames = self.run_frames

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect.x -= 40
        self.rect.y += 6

        self.collide_rect = pygame.Rect(x, y, 34, 42)
        self.collide_rect.bottom = self.rect.bottom
        self.collide_rect.y -= 4
