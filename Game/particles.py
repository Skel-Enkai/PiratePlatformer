import pygame.sprite

from support import import_folder


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

    def update(self, world_shift):
        self.animate(should_flip=self.enemy_speed)
        self.rect.center += world_shift


class AttackEffect(pygame.sprite.Sprite):
    def __init__(self, parent, animation, should_flip=True, facing=True, right_mask=None, left_mask=None,
                 offset=pygame.Vector2(0, 0), animation_speed=0.1):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.frames = animation
        self.image = animation[0]
        self.rect = self.image.get_rect()
        self.offset = offset

        self.parent = parent
        self.should_flip = should_flip
        self.facing = facing
        self.right_mask = right_mask
        self.left_mask = left_mask
        self.mask = right_mask[0]
        self.mask.clear()

    def animate(self):
        self.frame_index += self.animation_speed
        index = int(self.frame_index)
        if index >= len(self.frames):
            self.kill()
        else:
            image = self.frames[index]
            if not self.should_flip:
                self.image = image
                self.mask = self.right_mask[index]
            else:
                self.image = pygame.transform.flip(image, True, False)
                self.mask = self.left_mask[index]

    def update(self):
        self.animate()
        self.rect.center = self.parent.collide_rect.center
        if self.facing:
            self.rect.x += self.offset.x
        else:
            self.rect.x -= self.offset.x
        self.rect.y += self.offset.y
