import pygame.surface

from support import find_files


class UI:
    def __init__(self, surface):
        # setup
        self.display_surface = surface
        # health
        self.health_bar = pygame.image.load(find_files('./graphics/ui/health_bar.png'))
        self.health_bar_width = self.health_bar.get_width() - 40
        # coins
        self.coin = pygame.image.load(find_files('./graphics/ui/coin.png'))
        self.coin_rect = self.coin.get_rect(topleft=(50, 61))
        self.font = pygame.font.Font(find_files('./graphics/ui/ARCADEPI.TTF'), 24)

    def show_health(self, current, full):
        current_health_ratio = current / full
        bar_rect = pygame.Rect(54, 39, self.health_bar_width * current_health_ratio, 4)
        self.display_surface.blit(self.health_bar, (20, 10))
        pygame.draw.rect(self.display_surface, '#dc4949', bar_rect)

    def show_coins(self, amount):
        self.display_surface.blit(self.coin, self.coin_rect)
        coin_amount_surf = self.font.render(str(amount), False, '#8f4300')
        coin_amount_rect = coin_amount_surf.get_rect(midleft=self.coin_rect.midright)
        self.display_surface.blit(coin_amount_surf, coin_amount_rect)
# Other Font Colour #bf5900 #8f4300
