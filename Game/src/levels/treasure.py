from levels.tiles import AnimatedCenteredTile


class Coin(AnimatedCenteredTile):
	def __init__(self, size, x, y, path, value):
		super().__init__(size, x, y, path)
		self.value = value
