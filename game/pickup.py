import math
import random
import pygame
import game.draw as draw
from .settings import GROUND_Y, WHITE

_WEAPON_COLORS = {
    'ak47':         (100, 180, 255),
    'flamethrower': (255, 110,  20),
}
_WEAPON_LABELS = {
    'ak47':         'AK-47',
    'flamethrower': 'FLAMER',
}

_font: pygame.font.Font | None = None

def _get_font() -> pygame.font.Font:
    global _font
    if _font is None:
        _font = pygame.font.Font(None, draw.font_size(16))
    return _font


class Pickup:
    W, H = 22, 18

    def __init__(self, x: float, kind: str, weapon: str = '') -> None:
        self.x      = x
        self.y      = float(GROUND_Y - self.H)
        self.kind   = kind    # 'weapon' | 'medkit' | 'life'
        self.weapon = weapon
        self.alive  = True
        self._timer = random.uniform(0, math.pi * 2)

    def update(self) -> None:
        self._timer += 0.08

    def draw(self, surface) -> None:
        bob = math.sin(self._timer) * 3
        bx  = self.x
        by  = self.y + bob - 4

        if self.kind == 'weapon':
            self._draw_weapon(surface, bx, by)
        elif self.kind == 'medkit':
            self._draw_medkit(surface, bx, by)
        elif self.kind == 'life':
            self._draw_life(surface, bx, by)

    def _draw_weapon(self, surface, bx, by) -> None:
        color = _WEAPON_COLORS[self.weapon]
        draw.rect(surface, color,           (bx,     by,     self.W,     self.H))
        draw.rect(surface, WHITE,           (bx + 1, by + 1, self.W - 2, 4))
        draw.rect(surface, (200, 200, 200), (bx,     by,     self.W,     self.H), 1)
        draw.rect(surface, color,           (bx - 1, by - 1, self.W + 2, self.H + 2), 1)
        txt = _get_font().render(_WEAPON_LABELS[self.weapon], True, WHITE)
        surface.blit(txt, (draw.s(bx + self.W // 2) - txt.get_width() // 2,
                           draw.s(by) - txt.get_height() - draw.s(2)))

    def _draw_medkit(self, surface, bx, by) -> None:
        RED_CROSS = (210, 30, 30)
        draw.rect(surface, WHITE,     (bx, by, self.W, self.H))
        draw.rect(surface, RED_CROSS, (bx, by, self.W, self.H), 1)
        # cross
        draw.rect(surface, RED_CROSS, (bx + self.W // 2 - 2, by + 2, 4, self.H - 4))
        draw.rect(surface, RED_CROSS, (bx + 3, by + self.H // 2 - 2, self.W - 6, 4))
        txt = _get_font().render("MED", True, RED_CROSS)
        surface.blit(txt, (draw.s(bx + self.W // 2) - txt.get_width() // 2,
                           draw.s(by) - txt.get_height() - draw.s(2)))

    def _draw_life(self, surface, bx, by) -> None:
        PURPLE = (170, 70, 220)
        DARK_P = (110, 30, 160)
        CORK   = (139, 90,  43)
        # bottle body
        draw.rect(surface, PURPLE, (bx + 4, by + 6, self.W - 8, self.H - 6))
        # bottle neck
        draw.rect(surface, PURPLE, (bx + 8, by + 2, self.W - 16, 5))
        # cork
        draw.rect(surface, CORK,   (bx + 8, by,     self.W - 16, 3))
        # shine
        draw.rect(surface, (220, 170, 255), (bx + 6, by + 8, 3, 4))
        # border
        draw.rect(surface, DARK_P, (bx + 4, by + 6, self.W - 8, self.H - 6), 1)
        txt = _get_font().render("1UP", True, PURPLE)
        surface.blit(txt, (draw.s(bx + self.W // 2) - txt.get_width() // 2,
                           draw.s(by) - txt.get_height() - draw.s(2)))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y) - 4, self.W, self.H + 4)
