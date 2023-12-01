import pygame.sprite

from data.support import create_masks_list, import_folder
from levels.tiles import AnimatedTile


class AnimatedTreasureTile(AnimatedTile):
	def __init__(self, size, x, y, path, effects_path, anim_speed=0.10, scale=2):
		super().__init__(size, x, y, path, anim_speed, scale)
		center_x = x + (size // 2)
		center_y = y + (size // 2)
		self.rect = self.image.get_rect(center=(center_x, center_y))
		self.masks = []
		create_masks_list(self.frames, self.masks)
		self.mask = self.masks[0]
		# collection animation
		effects = import_folder(effects_path)
		self.effect_frames = []
		for frame in effects:
			self.effect_frames.append(pygame.transform.scale_by(frame, scale))
		self.collected = False

	def animate(self):
		self.frame_index += self.anim_speed
		if not self.collected:
			if self.frame_index >= len(self.frames):
				self.frame_index = 0
			self.image = self.frames[int(self.frame_index)]
			self.mask = self.masks[int(self.frame_index)]
		else:
			if self.frame_index >= len(self.effect_frames):
				self.kill()
			else:
				self.image = self.effect_frames[int(self.frame_index)]

	def collect(self):
		self.collected = True
		self.frame_index = 0
		self.mask.clear()


class Coin(AnimatedTreasureTile):
	def __init__(self, size, x, y, path, value):
		super().__init__(size, x, y, path, './graphics/treasure/coin_effect', anim_speed=0.10)
		self.value = value
		self.name = 'Coin'


class RedPotion(AnimatedTreasureTile):
	def __init__(self, size, x, y, change_health):
		super().__init__(size, x, y, './graphics/treasure/red_potion',
		                 './graphics/treasure/potion_effect')
		self.change_cur_health = change_health
		self.name = 'Potion'

	def consume(self):
		self.change_cur_health(50)
