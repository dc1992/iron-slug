import pygame
import game.draw as draw
from .settings import YELLOW, NATIVE_W, NATIVE_H


class Bullet:
    W, H = 10, 4

    def __init__(
        self, x: float, y: float, vx: float, vy: float,
        owner: str,
        damage: int = 10,
        color: tuple = YELLOW,
        max_range: int = 0,
    ) -> None:
        self.x         = x
        self.y         = y
        self._prev_x   = x
        self._start_x  = x
        self.vx        = vx
        self.vy        = vy
        self.owner     = owner
        self.damage    = damage
        self.color     = color
        self.max_range = max_range
        self.alive     = True

    def update(self) -> None:
        self._prev_x = self.x
        self.x += self.vx
        self.y += self.vy
        if self.max_range > 0 and abs(self.x - self._start_x) > self.max_range:
            self.alive = False
        if not (-20 < self.x < NATIVE_W + 20 and -20 < self.y < NATIVE_H + 20):
            self.alive = False

    def draw(self, surface) -> None:
        w = self.W + 4 if self.max_range > 0 else self.W
        draw.ellipse(surface, self.color, (self.x, self.y, w, self.H + 2))

    def rect(self) -> pygame.Rect:
        extra = abs(self.vx)
        if self.vx >= 0:
            x1 = int(self._prev_x - extra)
            x2 = int(self.x) + self.W
        else:
            x1 = int(self.x)
            x2 = int(self._prev_x) + self.W + int(extra)
        return pygame.Rect(x1, int(self.y), x2 - x1, self.H)
