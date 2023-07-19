from random import choice, randint

import pygame.sprite

from settings import *
from support import import_folder
from tiles import AnimatedTile, StaticTile


class Sky:
    def __init__(self, horizon, style='level'):
        self.top = pygame.image.load('./graphics/decoration/sky/sky_top.png').convert()
        self.bottom = pygame.image.load('./graphics/decoration/sky/sky_bottom.png').convert()
        self.middle = pygame.image.load('./graphics/decoration/sky/sky_middle.png').convert()
        self.horizon = horizon

        # stretch
        self.top = pygame.transform.scale(self.top, (screen_width, tile_size))
        self.bottom = pygame.transform.scale(self.bottom, (screen_width, tile_size))
        self.middle = pygame.transform.scale(self.middle, (screen_width, tile_size))

        self.style = style
        if self.style == 'overworld':
            palm_surfaces = import_folder('./graphics/overworld/palms')
            self.palms = []

            for surface in [choice(palm_surfaces) for __ in range(10)]:
                x = randint(0, screen_width)
                y = randint((self.horizon * tile_size) + randint(40, 60), screen_height)
                rect = surface.get_rect(midbottom=(x, y))
                self.palms.append((surface, rect))

            cloud_surfaces = import_folder('./graphics/overworld/clouds')
            self.clouds = []

            for surface in [choice(cloud_surfaces) for __ in range(randint(3, 7))]:
                x = randint(0, screen_width)
                y = randint(0, (self.horizon * tile_size - 80))
                rect = surface.get_rect(midtop=(x, y))
                self.clouds.append((surface, rect))

    def draw(self, surface):
        for row in range(vertical_tile_number):
            y = row * tile_size
            if row < self.horizon:
                surface.blit(self.top, (0, y))
            elif row == self.horizon:
                surface.blit(self.middle, (0, y))
            else:
                surface.blit(self.bottom, (0, y))

        if self.style == 'overworld':
            for palm in self.palms:
                surface.blit(palm[0], palm[1])
            for cloud in self.clouds:
                surface.blit(cloud[0], cloud[1])


class Water:
    def __init__(self, top, level_width, anim_speed):
        water_start = -screen_width
        water_tile_width = 192
        tile_x_amount = (2 * level_width + screen_width) // water_tile_width
        self.water_sprites = pygame.sprite.Group()

        for tile in range(tile_x_amount):
            x = tile * water_tile_width + water_start
            y = top
            sprite = AnimatedTile(water_tile_width, x, y, './graphics/decoration/water', anim_speed)
            self.water_sprites.add(sprite)

    def draw(self, surface, x_shift):
        self.water_sprites.update(x_shift)
        self.water_sprites.draw(surface)


# noinspection PyTypeChecker
class Clouds:
    def __init__(self, horizon, level_width, cloud_number):
        cloud_surface_list = import_folder('./graphics/decoration/clouds')
        min_x = -50
        max_x = level_width + 50
        min_y = 0
        max_y = (horizon - 2) * tile_size
        self.cloud_sprites = pygame.sprite.Group()

        for cloud in range(cloud_number):
            cloud = choice(cloud_surface_list)
            x = randint(min_x, max_x)
            y = randint(min_y, max_y)
            sprite = StaticTile(0, x, y, cloud)
            self.cloud_sprites.add(sprite)

    def draw(self, surface, x_shift):
        self.cloud_sprites.update(x_shift)
        self.cloud_sprites.draw(surface)
