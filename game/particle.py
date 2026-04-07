import random
import game.draw as draw


class Particle:
    def __init__(self, x: float, y: float, color: tuple) -> None:
        self.x        = x
        self.y        = y
        self.vx       = random.uniform(-4, 4)
        self.vy       = random.uniform(-6, -1)
        self.color    = color
        self.life     = random.randint(12, 28)
        self.max_life = self.life

    def update(self) -> None:
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.3
        self.life -= 1

    def draw(self, surface) -> None:
        size = max(0.5, 5 * self.life / self.max_life)
        draw.circle(surface, self.color, (self.x, self.y), size)
