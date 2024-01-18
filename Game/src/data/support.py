import os
import sys
from csv import reader
from os import walk

import pygame.surface

from data.settings import tile_size


# noinspection PyProtectedMember
def find_files(path):
    if getattr(sys, 'frozen', False):
        wd = sys._MEIPASS
        new_path = ''
        for element in path:
            if element == '/':
                new_path += '\\'
            else:
                new_path += element
        return os.path.join(wd, new_path[2:])
    else:
        return path


def import_folder(path):
    surfaces = []
    path_list = []
    path = find_files(path)
    for _, __, img_file in walk(path):
        for image in img_file:
            full_path = (path + '/' + image)
            path_list.append(full_path)
    path_list.sort()
    for pathL in path_list:
        surface = pygame.image.load(pathL).convert_alpha()
        surfaces.append(surface)
    return surfaces


def import_loop(path, dict):
    path = find_files(path)
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


def create_masks_list(animation_list, mask_list):
    for frame in animation_list:
        mask_list.append(pygame.mask.from_surface(frame))


def import_character_assets(path, animations_dict, masks_left, masks_right):
    character_path = path
    import_loop(character_path, animations_dict)
    create_masks(animations_dict, masks_right, masks_left)


def flipx_dictionary(dictionary):
    for key in dictionary.keys():
        for index, frame in enumerate(dictionary[key]):
            dictionary[key][index] = pygame.transform.flip(frame, True, False)
    return dictionary


def import_csv_layout(path):
    terrain_map = []
    with open(find_files(path)) as map:
        level = reader(map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map


def import_cut_graphic(path):
    surface = pygame.image.load(find_files(path)).convert_alpha()
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


# PHYSICS
# Direction A->B
def find_vector_from_two_points(point_a, point_b, magnitude):
    x_diff = point_b[0] - point_a[0]
    y_diff = point_b[1] - point_a[1]
    rect_vector = pygame.Vector2(x_diff, y_diff)
    return rect_vector.normalize() * magnitude
