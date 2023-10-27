from csv import reader
from os import walk

import pygame.surface

from settings import tile_size


def import_folder(path):
    surfaces = []
    path_list = []
    for _, __, img_file in walk(path):
        for image in img_file:
            full_path = path + '/' + image
            path_list.append(full_path)
    path_list.sort()
    for path in path_list:
        surface = pygame.image.load(path).convert_alpha()
        surfaces.append(surface)
    return surfaces


def import_loop(path, dict):
    for _, dir, ___ in walk(path):
        for folder in dir:
            full_path = path + folder
            dict[folder] = import_folder(full_path)
            for index, frame in enumerate(dict[folder]):
                dict[folder][index] = pygame.transform.scale_by(frame, 2)


def create_masks(animation_dict, mask_dict_right, mask_dict_left, exclude_masks=None):
    if exclude_masks is None:
        exclude_masks = [None]
    for animation in animation_dict.keys():
        if animation not in exclude_masks:
            mask_dict_right[animation] = []
            mask_dict_left[animation] = []
            for frame in animation_dict[animation]:
                mask_dict_right[animation].append(pygame.mask.from_surface(frame))
                mask_dict_left[animation].append(pygame.mask.from_surface(pygame.transform.flip(
                    frame, True, False)))


def import_csv_layout(path):
    terrain_map = []
    with open(path) as map:
        level = reader(map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map


def import_cut_graphic(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_width() / tile_size)
    tile_num_y = int(surface.get_height() / tile_size)

    cut_tiles = []
    for row in range(tile_num_y):
        y = row * tile_size
        for col in range(tile_num_x):
            x = col * tile_size
            new_surf = pygame.Surface((tile_size, tile_size), flags=pygame.SRCALPHA)
            new_surf.blit(surface, (0, 0), pygame.Rect(x, y, tile_size, tile_size))
            cut_tiles.append(new_surf)

    return cut_tiles
