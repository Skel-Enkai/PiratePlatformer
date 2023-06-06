import pygame

from decoration import Sky
from tiles import AnimatedTile
from game_data import levels


class Node(AnimatedTile):
    def __init__(self, size, x, y, status, icon_speed, path, anim_speed=0.10):
        super().__init__(size, x, y, path, anim_speed)
        self.rect = self.image.get_rect(center=(x, y))
        if status == 'available':
            self.status = 'available'
        else:
            self.status = 'locked'

        self.detection_zone = pygame.Rect(self.rect.centerx - icon_speed * 1.5, self.rect.centery - icon_speed * 1.5,
                                          icon_speed * 3, icon_speed * 3)

    def update(self, **kwargs):
        if self.status == 'available':
            self.animate()
        else:
            tint_surf = self.image.copy()
            tint_surf.fill('black', None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surf, (0, 0))


class Icon(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load('../graphics/overworld/hat.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.center = self.pos


class Overworld:
    def __init__(self, surface, create_level, start_level=0, max_level=0):
        # setup
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level
        self.wait = True

        # movement logic
        self.moving = False
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 4

        # sprites
        self.icon = None
        self.nodes = None
        self.setup_nodes()
        self.setup_icon()
        self.sky = Sky(7, 'overworld')

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()

        for index, node_data in enumerate(levels.values()):
            pos = node_data['node_pos']
            if index <= self.max_level:
                node_sprite = Node(200, pos[0], pos[1], 'available', self.speed, node_data['node_graphics'])
            else:
                node_sprite = Node(200, pos[0], pos[1], 'locked', self.speed, node_data['node_graphics'])
            self.nodes.add(node_sprite)

    def setup_icon(self):
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)
        self.icon.add(icon_sprite)

    def draw_paths(self):
        points = [node['node_pos'] for index, node in enumerate(levels.values()) if index <= self.max_level]
        if len(points) > 1:
            pygame.draw.lines(self.display_surface, '#a04f45', False, points, 6)

    def input(self, joystick, controller):
        if controller and joystick:
            self.controller_input(joystick)
        else:
            self.keyboard_input()

    def controller_input(self, joystick):
        if joystick.get_name() == "PS5 Controller" and not self.moving and not self.wait:
            if joystick.get_button(14) and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data(True)
                self.current_level += 1
                self.moving = True
            elif joystick.get_button(13) and self.current_level > 0:
                self.move_direction = self.get_movement_data(False)
                self.current_level -= 1
                self.moving = True
            elif joystick.get_button(0):
                self.create_level(self.current_level)

    def keyboard_input(self):
        keys = pygame.key.get_pressed()

        if not self.moving and not self.wait:
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data(True)
                self.current_level += 1
                self.moving = True
            elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.current_level > 0:
                self.move_direction = self.get_movement_data(False)
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                self.create_level(self.current_level)

    def get_movement_data(self, direction_forward=True):
        start = pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)
        if direction_forward:
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level - 1].rect.center)

        return (end - start).normalize()

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            self.icon.update()
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0, 0)
                pygame.time.wait(60)

    def draw(self):
        self.nodes.update()
        self.sky.draw(self.display_surface)
        self.draw_paths()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)

    def run(self, joystick, controller):
        self.input(joystick, controller)
        self.update_icon_pos()
        self.draw()
