import math
import game.draw as draw


class Slash:
    DURATION = 10

    def __init__(self, cx: float, cy: float, facing: int) -> None:
        self.cx     = cx
        self.cy     = cy
        self.facing = facing
        self.timer  = self.DURATION

    def update(self) -> None:
        self.timer -= 1

    @property
    def alive(self) -> bool:
        return self.timer > 0

    def draw(self, surface) -> None:
        t      = self.timer / self.DURATION
        color  = (255, 255, 120) if t > 0.5 else (255, 140, 30)
        length = 40 * t + 8
        sweep  = (1 - t) * 80 * self.facing
        width  = max(1, int(3 * t))
        for a in (-45, -22, 0, 22, 45):
            rad = math.radians(a + sweep)
            ex  = self.cx + math.cos(rad) * length * self.facing
            ey  = self.cy + math.sin(rad) * length
            draw.line(surface, color, (self.cx, self.cy), (ex, ey), width)
