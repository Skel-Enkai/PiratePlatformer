import pygame.sprite

from particles import AttackEffect
from support import import_loop, create_masks


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
        self.facing_right = False

        self.frame_index = 0
        self.anim_speed = anim_speed

        # empty attributes
        self.rect = None

    def move(self):
        self.rect.x += self.speed

    def reverse(self):
        self.speed *= -1

    def check_facing(self):
        if self.speed > 0:
            self.facing_right = True
        elif self.speed < 0:
            self.facing_right = False

    def restart_move(self):
        if self.facing_right:
            self.speed = 1
        else:
            self.speed = -1

    def update(self, x_shift):
        self.rect.x += x_shift
        self.collide_rect.centerx = self.rect.centerx
        self.check_facing()


# noinspection PyAttributeOutsideInit
class FierceTooth(Enemy):
    def __init__(self, size, x, y, display_surface):
        super().__init__(anim_speed=0.10)
        # flags
        self.status = '02-Run'

        # animation frames
        self.display_surface = display_surface
        self.animations = {}
        self.import_character_assets()

        # animation rect
        self.image = self.animations['02-Run'][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.rect.x += 10
        self.rect.y += 10

        # collision detection rect
        self.collide_rect = pygame.Rect(x, y, 34, 42)
        self.collide_rect.bottom = self.rect.bottom
        self.collide_rect.y -= 4

        # attacks
        self.counter = 0
        self.attack_effects = pygame.sprite.GroupSingle()
        self.mask = self.masks_left['01-Idle'][0]
        self.mask.clear()

    def import_character_assets(self):
        character_path = './graphics/enemies/fierce_tooth/'
        import_loop(character_path, self.animations)
        self.masks_left = {}
        self.masks_right = {}
        create_masks(self.animations, self.masks_left, self.masks_right)

    def animate(self):
        self.frame_index += self.anim_speed
        if self.frame_index > len(self.animations[self.status]):
            self.frame_index = 0
            if self.knockback:
                self.status = '02-Run'
                self.restart_move()
                self.knockback = False
            elif self.status == '09-Dead Hit':
                self.status = '10-Dead Ground'
            elif self.status == '10-Dead Ground':
                self.kill()
            elif self.status == '06-Anticipation':
                self.status = '07-Attack'
            elif self.status == '07-Attack':
                self.status = '02-Run'
                self.restart_move()
        index = int(self.frame_index)
        self.image = self.animations[self.status][index]
        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            self.mask = self.masks_right[self.status][index]
        else:
            self.mask = self.masks_left[self.status][index]

    def anticipate_attack(self):
        if not self.knockback and not self.dying:
            self.speed = 0
            self.status = '06-Anticipation'
            self.attack_effects.add(AttackEffect(self, self.animations['11-Attack Effect'],
                                    should_flip=self.facing_right, facing=self.facing_right,
                                    right_mask=self.masks_right['11-Attack Effect'],
                                    left_mask=self.masks_left['11-Attack Effect'],
                                    offset=pygame.Vector2(60, -12)))

    def damage(self, amount):
        if not self.knockback and not self.dying:
            self.health += amount
            self.frame_index = 0
            self.speed = 0
            if self.health <= 0:
                self.status = '09-Dead Hit'
                self.dying = True
            else:
                self.status = '08-Hit'
                self.knockback = True

    def update(self, x_shift):
        self.counter += 1
        if self.counter == 200:
            self.anticipate_attack()
            self.counter = 0
        self.move()
        self.rect.x += x_shift
        self.collide_rect.centerx = self.rect.centerx
        self.check_facing()
        self.animate()
        if self.status == '07-Attack':
            self.attack_effects.update()
            self.attack_effects.draw(self.display_surface)
