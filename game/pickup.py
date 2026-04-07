import math
import random
import pygame
from .settings import GROUND_Y, WHITE, BLACK

# Visual palette per weapon
_COLORS = {
    'ak47':         (100, 180, 255),
    'flamethrower': (255, 110,  20),
}
_LABELS = {
    'ak47':         'AK-47',
    'flamethrower': 'FLAMER',
}

_font: pygame.font.Font | None = None

def _get_font() -> pygame.font.Font:
    global _font
    if _font is None:
        _font = pygame.font.Font(None, 16)
    return _font


class Pickup:
    W, H = 22, 18

    def __init__(self, x: float, weapon: str) -> None:
        self.x      = x
        self.y      = float(GROUND_Y - self.H)
        self.weapon = weapon
        self.alive  = True
        self._timer = random.uniform(0, math.pi * 2)  # phase offset for bob

    def update(self) -> None:
        self._timer += 0.08

    def draw(self, surface: pygame.Surface) -> None:
        bob    = int(math.sin(self._timer) * 3)
        color  = _COLORS[self.weapon]
        bx, by = int(self.x), int(self.y) + bob - 4

        # crate body
        pygame.draw.rect(surface, color,        (bx,     by,     self.W,     self.H))
        pygame.draw.rect(surface, WHITE,        (bx + 1, by + 1, self.W - 2, 4))      # stripe
        pygame.draw.rect(surface, (0, 0, 0, 0), (bx,     by,     self.W,     self.H), 2)  # border

        # label above
        font = _get_font()
        txt  = font.render(_LABELS[self.weapon], True, WHITE)
        surface.blit(txt, (bx + self.W // 2 - txt.get_width() // 2, by - 12))

        # glow outline
        pygame.draw.rect(surface, color, (bx - 1, by - 1, self.W + 2, self.H + 2), 1)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y) - 4, self.W, self.H + 4)
