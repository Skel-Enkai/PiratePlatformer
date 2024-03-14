import pygame.surface

from data.support import find_files


class UI:
    def __init__(self, surface):
        # setup
        self.display_surface = surface
        self.font = pygame.font.Font(find_files('./graphics/ui/ARCADEPI.TTF'), 24)
        # health
        self.health_bar = pygame.image.load(find_files('./graphics/ui/health_bar.png'))
        self.health_bar_width = self.health_bar.get_width() - 40
        # coins
        self.coin = pygame.image.load(find_files('./graphics/ui/coin.png'))
        self.coin_rect = self.coin.get_rect(topleft=(50, 61))
        # swords
        self.sword = pygame.image.load(find_files('./graphics/ui/sword.png'))
        self.sword = pygame.transform.scale_by(self.sword, 3)
        self.sword_rect = self.sword.get_rect(topleft=(220, 10))

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

    def show_swords(self, amount):
        self.display_surface.blit(self.sword, self.sword_rect)
        sword_amount_surf = self.font.render(str(amount), False, '#8f4300')
        sword_amount_rect = sword_amount_surf.get_rect(midleft=(self.sword_rect.midright[0] + 10,
                                                                self.sword_rect.midleft[1]))
        self.display_surface.blit(sword_amount_surf, sword_amount_rect)

# Other Font Colour #bf5900 #8f4300
