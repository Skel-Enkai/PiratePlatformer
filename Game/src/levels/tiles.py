import pygame.sprite

from data.support import import_folder, find_files


class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.offset = 0

    def update(self, world_shift):
        self.rect.center += world_shift


class StaticTile(Tile):
    def __init__(self, size, x, y, surface):
        super().__init__(size, x, y)
        self.image = surface


class AnimatedTile(Tile):
    def __init__(self, size, x, y, path, anim_speed=0.10, scale=1):
        super().__init__(size, x, y)
        frames = import_folder(path)
        self.frames = []
        for frame in frames:
            self.frames.append(pygame.transform.scale_by(frame, scale))
        self.frame_index = 0
        self.anim_speed = anim_speed
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += self.anim_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, world_shift):
        self.animate()
        self.rect.center += world_shift


class Crate(StaticTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, pygame.image.load(find_files('./graphics/terrain/crate.png')).convert_alpha())
        offset_y = y + size
        self.rect = self.image.get_rect(bottomleft=(x, offset_y))
        self.hitbox_rect = self.rect.inflate(-20, 0)

    def update(self, world_shift):
        self.rect.center += world_shift
        self.hitbox_rect.center += world_shift


class Palm(AnimatedTile):
    def __init__(self, size, x, y, path, offset):
        super().__init__(size, x, y, path)
        offset_y = y - offset
        self.rect.topleft = (x, offset_y)
