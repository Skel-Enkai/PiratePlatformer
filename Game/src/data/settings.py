vertical_tiles_on_screen = 11
horizontal_tiles_on_screen = 18
tile_size: int = 64
screen_width = tile_size * horizontal_tiles_on_screen
screen_height = tile_size * vertical_tiles_on_screen

controllers = {'PS5 Controller': {'left_pad': 13, 'right_pad': 14, 'up_pad': 11, 'down_pad': 12, 'cross': 0,
                                  'square': 2, 'triangle': 3, 'circle': 1, 'L1': 9, 'R1': 10, 'L3': 7, 'R3': 8,
                                  'menu': 6},
               'DualSense Wireless Controller': {'left_pad': 13, 'right_pad': 14, 'up_pad': 11, 'down_pad': 12,
                                                 'cross': 0, 'square': 2, 'triangle': 3, 'circle': 1, 'L1': 9, 'R1': 10,
                                                 'L3': 7, 'R3': 8, 'menu': 6},
               'Xbox 360 Controller': {'L1': 4, 'R1': 5, 'L3': 8, 'triangle': 2, 'circle': 3, 'cross': 1, 'square': 0,
                                       'R3': 9, 'menu': 7, 'playstation': 6}}


class saveState:
    def __init__(self, current_level=0, max_level=0, max_health=100, cur_health=100, coins=0, swords=0):
        self.current_level = current_level
        self.max_level = max_level
        self.max_health = max_health
        self.cur_health = cur_health
        self.coins = coins
        self.swords = swords

    def __reduce__(self):
        return self.__class__, (self.current_level, self.max_level, self.max_health, self.cur_health, self.coins,
                                self.swords)
