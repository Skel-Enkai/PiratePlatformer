import pygame.sprite

from particles import AttackEffect
from support import import_loop, create_masks


# noinspection PyAttributeOutsideInit
class Enemy(pygame.sprite.Sprite):
    def __init__(self, path, identifier, anim_speed=0.10):
        super().__init__()
        # attributes
        self.speed = 1
        self.true_speed = 1
        self.health = 100
        self.frame_index = 0
        self.anim_speed = anim_speed
        self.direction = pygame.Vector2(0, 0)

        # flags
        self.knockback = False
        self.dying = False
        self.facing_right = False
        self.status = None
        self.should_reset = []
        self.identifier = identifier

        # empty attributes
        self.rect = None
        self.collide_rect = None

        self.animations = {}
        self.import_character_assets(path)

    def import_character_assets(self, path):
        character_path = path
        import_loop(character_path, self.animations)
        self.masks_left = {}
        self.masks_right = {}
        create_masks(self.animations, self.masks_right, self.masks_left)

    def should_reset_status(self):
        if self.status in self.should_reset:
            return False
        return True

    def reset_status(self):
        if not self.should_reset_status():
            self.knockback = False
            self.status = 'None'
            self.speed = self.true_speed
            self.get_status()

    def get_status(self):
        if self.should_reset_status():
            current = self.status
            if self.status != current:
                self.frame_index = 0

    def check_facing(self):
        if self.direction.x > 0:
            self.facing_right = True
        elif self.direction.x < 0:
            self.facing_right = False

    def move(self, x_shift):
        self.rect.x += int(self.direction.x * self.speed)
        self.rect.x += x_shift
        self.collide_rect.centerx = self.rect.centerx


# noinspection PyAttributeOutsideInit
class FierceTooth(Enemy):
    def __init__(self, x, y, display_surface, player, identifier):
        super().__init__('./graphics/enemies/fierce_tooth/', identifier, anim_speed=0.10)
        # flags and essentials
        self.status = '01-Idle'
        self.should_reset = ['06-Anticipation', '07-Attack', '08-Hit', '09-Dead Hit', '10-Dead Ground']
        self.display_surface = display_surface
        self.constraints = []
        self.player = player

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
        self.attack_effect = pygame.sprite.GroupSingle()
        self.mask = self.masks_left['01-Idle'][0]
        self.mask.clear()

    def animate(self):
        self.frame_index += self.anim_speed
        if self.frame_index > len(self.animations[self.status]):
            self.frame_index = 0
            if self.knockback:
                self.reset_status()
            elif self.status == '09-Dead Hit':
                self.status = '10-Dead Ground'
            elif self.status == '10-Dead Ground':
                self.kill()
            elif self.status == '06-Anticipation':
                self.status = '07-Attack'
            elif self.status == '07-Attack':
                self.reset_status()
        index = int(self.frame_index)
        self.image = self.animations[self.status][index]
        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
            self.mask = self.masks_right[self.status][index]
        else:
            self.mask = self.masks_left[self.status][index]

    def get_status(self):
        if self.should_reset_status():
            current = self.status
            if self.direction.y < 0:
                self.status = '03-Jump'
            elif self.direction.y > 1:
                self.status = '04-Fall'
            else:
                if self.direction.x == 0:
                    self.status = '01-Idle'
                else:
                    self.status = '02-Run'
            if self.status != current:
                self.frame_index = 0

    def decision(self):
        if self.speed > 0:
            rect_xdifference = self.rect.centerx - self.player.sprite.rect.centerx
            rect_ydifference = self.rect.centery - self.player.sprite.rect.centery
            if abs(rect_ydifference) <= 60:
                if abs(rect_xdifference) >= 300:
                    self.direction.x = 0
                elif abs(rect_xdifference) <= 90 and ((self.facing_right and rect_xdifference < 0) or
                                                      (not self.facing_right and rect_xdifference > 0)):
                    self.anticipate_attack()
                elif rect_xdifference < 0:
                    self.direction.x = 1
                else:
                    self.direction.x = -1
            else:
                self.direction.x = 0

    def boundry_detection(self):
        if self.constraints is not []:
            for constraint in self.constraints:
                if self.collide_rect.centerx <= constraint.rect.centerx:
                    if self.direction.x > 0:
                        self.direction.x = 0
                else:
                    if self.direction.x < 0:
                        self.direction.x = 0

    def anticipate_attack(self):
        if not self.knockback and not self.dying:
            self.speed = 0
            self.status = '06-Anticipation'
            self.attack_effect.add(AttackEffect(self, self.animations['11-Attack Effect'],
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
        self.decision()
        self.boundry_detection()
        self.get_status()
        self.move(x_shift)

        self.check_facing()
        self.animate()
        if self.status == '07-Attack':
            self.attack_effect.update()
            self.attack_effect.draw(self.display_surface)
