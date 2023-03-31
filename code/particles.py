import pygame
from support import import_folder


class Effect(pygame.sprite.Sprite):
    def __init__(self, pos, type, animation_speed=0.4):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = animation_speed
        if type == 'jump':
            self.frames = import_folder("../graphics/character/dust_particles/jump")
        elif type == 'land':
            self.frames = import_folder("../graphics/character/dust_particles/land")
        elif type == 'enemy_die':
            self.frames = import_folder("../graphics/enemy/DeadHit")
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift
