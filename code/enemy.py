import pygame
from tiles import AnimatedTile
from support import import_folder


# noinspection PyAttributeOutsideInit
class Enemy(AnimatedTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, '../graphics/enemy/run')
        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect.y += size - self.image.get_height()
        self.speed = 1
        self.previous_speed = 0
        self.health = 100
        self.knockback = False
        self.dying = False
        self.run_frames = self.frames
        self.knockback_frames = import_folder('../graphics/enemy/Hit')
        self.death_frames = import_folder('../graphics/enemy/DeadHit')

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
        self.animate()
