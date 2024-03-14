import pygame.sprite

from data.enums import Projectile
from data.support import import_folder, import_assets_lists


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


# PROJECTILES

class CannonBall(pygame.sprite.Sprite):
    def __init__(self, animations, masks, pos, facing_right):
        super().__init__()
        self.type = Projectile.CannonBall
        self.animations = animations
        self.masks = masks
        self.image = self.animations['06-IdleBall'][0]
        self.mask = self.masks['06-IdleBall'][0]

        if facing_right:
            self.speed = 4
            starting_pos = pos + pygame.Vector2(32, 0)
        else:
            self.speed = -4
            starting_pos = pos + pygame.Vector2(-32, 0)

        self.rect = self.image.get_rect(center=starting_pos)
        self.exploded = False
        self.frame_index = 0

    def check_out_of_bound(self):
        if (self.rect.x < -200 or self.rect.x > 1352) or (self.rect.y < -200 or self.rect.y > 904):
            # print('projectile deleted')
            self.kill()

    def explode(self):
        self.image = self.animations['07-BallExplosion'][0]
        self.rect = self.image.get_rect(center=self.rect.center)
        self.speed = 0
        self.exploded = True

    def explosion_animate(self):
        anim_speed = 0.10
        self.frame_index += anim_speed
        index = int(self.frame_index)
        if index >= len(self.animations['07-BallExplosion']):
            self.kill()
        else:
            self.image = self.animations['07-BallExplosion'][index]

    def update_position(self, world_shift):
        self.rect.center += world_shift
        self.rect.x += self.speed

    def update(self, world_shift):
        self.update_position(world_shift)
        if not self.exploded:
            self.check_out_of_bound()
        else:
            self.explosion_animate()


class SwordProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, facing=True, offset=pygame.Vector2(0, 0), damage=0, scale=2):
        super().__init__()
        self.type = Projectile.Sword
        path = './graphics/character/Sword/22-Sword Spinning'
        self.animations_right = []
        self.animations_left = []
        self.masks_right = []
        self.masks_left = []
        import_assets_lists(path, self.animations_right, self.animations_left, self.masks_right, self.masks_left, scale)
        self.image = self.animations_right[0]
        self.mask = self.masks_right[0]

        if facing:
            self.speed = 5
            pos.x += offset.x
        else:
            self.speed = -5
            pos.x -= offset.x

        pos.y += offset.y
        self.rect = self.image.get_rect(center=pos.center)
        clear_image = self.animations_right[0].copy()
        clear_image.set_alpha(0)
        self.image = clear_image

        self.damage = damage
        self.facing_right = facing
        # using frame index as a hacky way of delaying the sword by a frame
        self.frame_index = -1
        self.animation_speed = 0.10

    def animate(self):
        self.frame_index += self.animation_speed
        # print(int(self.frame_index), ' ', self.frame_index)
        if self.frame_index >= 0:
            if self.frame_index >= len(self.animations_right):
                self.frame_index = 0
            if self.facing_right:
                self.image = self.animations_right[int(self.frame_index)]
                self.mask = self.masks_right[int(self.frame_index)]
            else:
                self.image = self.animations_left[int(self.frame_index)]
                self.mask = self.masks_left[int(self.frame_index)]

    def check_out_of_bound(self):
        if (self.rect.x < -200 or self.rect.x > 1352) or (self.rect.y < -200 or self.rect.y > 904):
            # print('projectile deleted')
            self.kill()

    def update_position(self, world_shift):
        self.rect.center += world_shift
        if self.frame_index >= 0:
            self.rect.x += self.speed

    def update(self, world_shift):
        self.animate()
        self.update_position(world_shift)
        self.check_out_of_bound()
