import pygame.sprite

from Game.code.support import import_folder


class Effect(pygame.sprite.Sprite):
    def __init__(self, pos, type, animation_speed=0.4, enemy_speed=-1):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.enemy_speed = enemy_speed
        if type == 'jump':
            self.frames = import_folder("./graphics/character/dust_particles/jump")
        elif type == 'land':
            self.frames = import_folder("./graphics/character/dust_particles/land")
        elif type == 'enemy_die':
            self.frames = import_folder("./graphics/enemies/fierce_tooth/dead_hit")
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=pos)

    def animate(self, should_flip=None):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
            if should_flip > 0:
                self.image = pygame.transform.flip(self.image, True, False)

    def update(self, x_shift):
        self.animate(should_flip=self.enemy_speed)
        self.rect.x += x_shift
