import pygame.sprite

from data.support import import_character_assets, flipx_dictionary


class StaticTraps(pygame.sprite.Sprite):
	def __init__(self, x, y, path, display_surface, health=100):
		super().__init__()
		self.display_surface = display_surface
		self.health = health
		self.animations = {}
		self.masks_left = {}
		self.masks_right = {}
		import_character_assets(path, self.animations, self.masks_left, self.masks_right)

		self.status = '01-Idle'
		self.mask = self.masks_left['01-Idle'][0]
		self.image = self.animations['01-Idle'][0]
		self.rect = self.image.get_rect(topleft=(x, y))

		self.frame_index = 0
		self.anim_speed = 0.10
		self.facing_right = False

	def update_position(self, world_shift):
		self.rect.center += world_shift

	def update(self, world_shift):
		self.animate()
		self.update_position(world_shift)


class Cannon(StaticTraps):
	def __init__(self, x, y, display_surface, projectiles, facing_right=False):
		super().__init__(x, y, './graphics/traps/Cannon/', display_surface)
		self.rect.center += pygame.Vector2(-10, 12)
		self.firing = False
		self.facing_right = facing_right
		self.projectiles = projectiles
		if facing_right:
			self.animations = flipx_dictionary(self.animations)
			self.masks = self.masks_right
		else:
			self.masks = self.masks_left

		keys_to_extract = ['06-IdleBall', '07-BallExplosion', '08-BallDestroyed']
		self.cannon_ball_animations = dict(filter(lambda item: item[0] in keys_to_extract, self.animations.items()))
		self.cannon_ball_masks = dict(filter(lambda item: item[0] in keys_to_extract, self.masks.items()))

	def animate(self):
		self.frame_index += self.anim_speed
		if self.frame_index > len(self.animations[self.status]):
			self.frame_index = 0
			self.check_status()
		index = int(self.frame_index)
		if index == 3 and self.firing:
			self.projectiles.add(CannonBall(self.cannon_ball_animations, self.cannon_ball_masks, self.rect.center,
			                                self.facing_right))
			self.firing = False
		self.mask = self.masks[self.status][index]
		self.image = self.animations[self.status][index]

	def check_status(self):
		if self.status in ['04-Fire']:
			self.status = '01-Idle'

	def fire(self):
		self.status = '04-Fire'
		self.firing = True


class CannonBall(pygame.sprite.Sprite):
	def __init__(self, animations, masks, pos, facing_right):
		super().__init__()
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