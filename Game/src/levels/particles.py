import pygame.sprite

from data.support import import_folder


class Effect(pygame.sprite.Sprite):
    def __init__(self, pos, frames_object, animation_speed=0.4, player_effect=False):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = animation_speed
        if isinstance(frames_object, str):
            self.frames = import_folder(frames_object)
        else:
            self.frames = frames_object
        self.image = self.frames[self.frame_index]
        if player_effect:
            self.rect = self.image.get_rect(midbottom=pos)
        else:
            self.rect = self.image.get_rect(center=pos)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, world_shift):
        self.animate()
        self.rect.center += world_shift


class AttackEffect(pygame.sprite.Sprite):
    def __init__(self, parent, animation, should_flip=True, facing=True, right_mask=None, left_mask=None,
                 offset=pygame.Vector2(0, 0), animation_speed=0.1, type=None, damage=None):
        super().__init__()
        # animation
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.frames = animation
        self.image = animation[0]
        # misc
        self.rect = self.image.get_rect()
        self.offset = offset
        self.parent = parent
        self.type = type
        self.damage = damage
        # flags and masks
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
