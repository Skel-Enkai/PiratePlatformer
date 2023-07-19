import pygame.sprite

from support import import_folder


class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.offset = 0

    def update(self, x_shift):
        self.rect.x += x_shift


class StaticTile(Tile):
    def __init__(self, size, x, y, surface):
        super().__init__(size, x, y)
        self.image = surface


class Crate(StaticTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, pygame.image.load('./graphics/terrain/crate.png').convert_alpha())
        offset_y = y + size
        self.rect = self.image.get_rect(bottomleft=(x, offset_y))
        self.hitbox_rect = self.rect.inflate(-20, 0)

    def update(self, x_shift):
        self.rect.x += x_shift
        self.hitbox_rect.x += x_shift


class AnimatedTile(Tile):
    def __init__(self, size, x, y, path, anim_speed=0.10):
        super().__init__(size, x, y)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.anim_speed = anim_speed
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += self.anim_speed
        if self.frame_index > len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift


class Coin(AnimatedTile):
    def __init__(self, size, x, y, path, value):
        super().__init__(size, x, y, path)
        center_x = x + (size // 2)
        center_y = y + (size // 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))
        self.value = value


class Palm(AnimatedTile):
    def __init__(self, size, x, y, path, offset):
        super().__init__(size, x, y, path)
        offset_y = y - offset
        self.rect.topleft = (x, offset_y)
