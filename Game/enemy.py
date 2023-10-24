import pygame.sprite

from support import import_folder


# noinspection PyAttributeOutsideInit
class Enemy(pygame.sprite.Sprite):
    def __init__(self, anim_speed=0.10):
        super().__init__()
        # attributes
        self.collide_rect = None
        self.speed = 1
        self.health = 100
        self.knockback = False
        self.dying = False
        self.facing_right = True

        self.frame_index = 0
        self.anim_speed = anim_speed

        # empty attributes
        self.rect = None
        self.death_frames = None
        self.knockback_frames = None
        self.run_frames = None

    def move(self):
        self.rect.x += self.speed

    def reverse(self):
        self.speed *= -1

    def check_facing(self):
        if self.speed > 0:
            self.facing_right = False
        elif self.speed < 0:
            self.facing_right = True

    def restart_move(self):
        if self.facing_right:
            self.speed = -1
        else:
            self.speed = 1

    def damage(self, amount):
        if not self.knockback and not self.dying:
            self.health += amount
            self.frame_index = 0
            self.speed = 0
            if self.health <= 0:
                self.frames = self.death_frames
                self.dying = True
            else:
                self.frames = self.knockback_frames
                self.knockback = True

    def update(self, x_shift):
        self.rect.x += x_shift
        self.collide_rect.centerx = self.rect.centerx
        self.check_facing()


class FierceTooth(Enemy):
    def __init__(self, size, x, y):
        super().__init__(anim_speed=0.10)
        # flags
        self.anticipation = False
        self.attack = False

        # animation frames
        self.run_frames = import_folder('./graphics/enemies/fierce_tooth/run')
        self.knockback_frames = import_folder('./graphics/enemies/fierce_tooth/hit')
        self.death_frames = import_folder('./graphics/enemies/fierce_tooth/dead_hit')
        self.death_frames += import_folder('./graphics/enemies/fierce_tooth/dead_ground')
        self.anticipation_frames = import_folder('./graphics/enemies/fierce_tooth/anticipation')
        self.attack_frames = import_folder('./graphics/enemies/fierce_tooth/attack')

        self.frames = self.run_frames

        # animation rect
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect.x -= 40
        self.rect.y += 6

        # collision detection rect
        self.collide_rect = pygame.Rect(x, y, 34, 42)
        self.collide_rect.bottom = self.rect.bottom
        self.collide_rect.y -= 4

        # attack hitbox
        self.counter = 0
        self.attack_masks = import_folder('./graphics/enemies/fierce_tooth/attack_mask')
        self.attack_masks_right = []
        self.attack_masks_left = []
        for frame in self.attack_masks:
            self.attack_masks_right.append(pygame.mask.from_surface(frame))
            self.attack_masks_left.append(pygame.mask.from_surface(pygame.transform.flip(frame, True, False)))
        self.mask = self.attack_masks_right[0]
        self.mask.clear()

    def animate(self):
        self.frame_index += self.anim_speed
        if self.frame_index > len(self.frames):
            self.frame_index = 0
            if self.knockback:
                self.frames = self.run_frames
                self.restart_move()
                self.knockback = False
            elif self.dying:
                self.kill()
            elif self.anticipation:
                self.frames = self.attack_frames
                self.anticipation = False
                self.attack = True
            elif self.attack:
                self.frames = self.run_frames
                self.attack = False
                self.restart_move()
        self.image = self.frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def anticipate_attack(self):
        if not self.knockback and not self.dying:
            self.anticipation = True
            self.frames = self.anticipation_frames
            self.speed = 0

    def update_attack(self):
        index = int(self.frame_index)
        if index < 3:
            if self.facing_right:
                self.mask = self.attack_masks_right[index]
            else:
                self.mask = self.attack_masks_left[index]
        else:
            self.mask.clear()

    def update(self, x_shift):
        self.counter += 1
        if self.counter == 200:
            self.anticipate_attack()
            self.counter = 0
        if self.attack:
            self.update_attack()
        self.move()
        self.rect.x += x_shift
        self.collide_rect.centerx = self.rect.centerx
        self.check_facing()
        self.animate()
