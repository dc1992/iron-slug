import math
import random
import pygame
from .settings import GRAVITY, GROUND_Y, NATIVE_W, ORANGE, YELLOW, MELEE_RANGE
from .bullet import Bullet
from .sprites import draw_enemy
import game.draw as draw


class Enemy:
    W, H   = 30, 45
    MAX_HP = 40

    def __init__(self, x: float,
                 speed: float = 1.8,
                 bullet_damage: int = 10,
                 melee_damage: int = 25) -> None:
        self.x             = x
        self.y             = float(GROUND_Y - self.H)
        self.vy            = 0.0
        self.on_ground     = False
        self.hp            = self.MAX_HP
        self.shoot_cd      = random.randint(60, 180)
        self.facing        = 1
        self.dead          = False
        self.death_timer   = 0
        self.anim_frame    = 0
        self.anim_timer    = 0
        self.speed         = speed
        self.bullet_damage = bullet_damage
        self.melee_damage  = melee_damage

    STOP_DIST   = 80   # min distance (px) from player center
    SPREAD_DIST = 40   # min distance (px) between enemies

    def update(self, player_cx: float, others: list = []) -> None:
        self._player_cx = player_cx   # stored for try_ranged / try_melee
        if self.dead:
            self.death_timer += 1
            return

        my_cx = self.x + self.W / 2
        dist  = player_cx - my_cx

        if abs(dist) > self.STOP_DIST:
            if dist > 0:
                self.x += self.speed; self.facing = 1
            else:
                self.x -= self.speed; self.facing = -1

        # push away from other enemies so they don't stack
        for other in others:
            if other is self or other.dead:
                continue
            gap = (self.x + self.W / 2) - (other.x + other.W / 2)
            if abs(gap) < self.SPREAD_DIST:
                push = (self.SPREAD_DIST - abs(gap)) / 2
                self.x += push if gap >= 0 else -push

        self.vy += GRAVITY
        self.y  += self.vy
        if self.y + self.H >= GROUND_Y:
            self.y         = GROUND_Y - self.H
            self.vy        = 0
            self.on_ground = True

        self.x = max(0, min(NATIVE_W - self.W, self.x))

        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

    def _dist_to_player(self) -> float:
        return abs((self.x + self.W / 2) - self._player_cx)

    def try_ranged(self) -> Bullet | None:
        """Shoot a bullet only when outside melee range."""
        if self.shoot_cd != 0 or self.dead or self._dist_to_player() <= MELEE_RANGE:
            return None
        self.shoot_cd = 130
        bx = (self.x + self.W) if self.facing == 1 else (self.x - Bullet.W)
        by = self.y + 17
        return Bullet(bx, by, self.facing * 7, 0, 'enemy', damage=self.bullet_damage)

    def try_melee(self) -> bool:
        """Strike with knife when close. Returns True if attack fires."""
        if self.shoot_cd != 0 or self.dead or self._dist_to_player() > MELEE_RANGE:
            return False
        self.shoot_cd = 70   # slightly faster rhythm than ranged
        return True

    def hit(self, dmg: int) -> None:
        self.hp -= dmg
        if self.hp <= 0:
            self.hp   = 0
            self.dead = True

    def draw(self, surface: pygame.Surface) -> None:
        if self.dead:
            self._draw_explosion(surface)
            return

        draw_enemy(surface, int(self.x), int(self.y), self.facing)
        self._draw_health_bar(surface)

    def _draw_explosion(self, surface) -> None:
        if self.death_timer >= 25:
            return
        r = self.death_timer * 1.8
        for i in range(6):
            a  = math.radians(i * 60 + self.death_timer * 18)
            ex = self.x + self.W / 2 + math.cos(a) * r
            ey = self.y + self.H / 2 + math.sin(a) * r
            draw.circle(surface, ORANGE, (ex, ey), max(1, 7 - self.death_timer // 4))
        draw.circle(surface, YELLOW,
                    (self.x + self.W / 2, self.y + self.H / 2),
                    max(1, 18 - self.death_timer))

    def _draw_health_bar(self, surface) -> None:
        bw = 30
        bx, by = self.x, self.y - 8
        draw.rect(surface, (100,   0, 0), (bx, by, bw, 4))
        draw.rect(surface, (255, 100, 0), (bx, by, bw * self.hp / self.MAX_HP, 4))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)
