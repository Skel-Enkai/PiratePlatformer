import pygame.sprite

from data.support import import_character_assets, flipx_dictionary
from levels.particles import Effect, CannonBall


class StaticTraps(pygame.sprite.Sprite):
	def __init__(self, x, y, path, particles, health=100):
		super().__init__()
		self.particle_effects_sprites = particles
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
		self.destroyed = False

	def update_position(self, world_shift):
		self.rect.center += world_shift

	def update(self, world_shift):
		self.animate()
		self.update_position(world_shift)


class Cannon(StaticTraps):
	def __init__(self, x, y, projectiles, particles, facing_right=False, health=120):
		super().__init__(x, y, './graphics/traps/Cannon/', particles, health=health)
		self.rect.center += pygame.Vector2(-10, 12)
		self.firing = False
		self.effect = None
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
		index = int(self.frame_index)
		if index == 3 and self.firing:
			self.fire()
		self.mask = self.masks[self.status][index]
		self.image = self.animations[self.status][index]
		self.frame_index += self.anim_speed
		if self.frame_index > len(self.animations[self.status]):
			self.frame_index = 0
			self.check_status()

	def check_status(self):
		if self.status == '02-Hit' and self.destroyed:
			self.status = 'Destroyed'
			self.image = self.animations['03-Destroyed'][2]
			self.rect.center += pygame.Vector2(6, 20)
			self.mask.clear()
		elif self.status in ['04-Fire', '02-Hit']:
			self.status = '01-Idle'

	def prepare_fire(self):
		if self.status == '01-Idle':
			self.status = '04-Fire'
			self.firing = True

	def damage(self, amount):
		if self.status != '02-Hit':
			self.health += amount
			self.frame_index = 0
			if self.health <= 0:
				self.status = '02-Hit'
				self.destroyed = True
			else:
				self.status = '02-Hit'

	def fire(self):
		self.projectiles.add(CannonBall(self.cannon_ball_animations, self.cannon_ball_masks, self.rect.center,
		                                self.facing_right))
		if self.facing_right:
			pos = self.rect.center + pygame.Vector2(50, -4)
		else:
			pos = self.rect.center + pygame.Vector2(-50, -4)
		self.particle_effects_sprites.add(Effect(pos, self.animations['05-FireEffect']))
		self.firing = False

	def update(self, world_shift):
		if not self.status == 'Destroyed':
			self.animate()
		self.update_position(world_shift)
