import random
import pygame
from .settings import GRAVITY, JUMP_FORCE, GROUND_Y, NATIVE_W, RED, GREEN
from .bullet import Bullet
from .sprites import draw_player
from .weapon import WEAPONS
import game.draw as draw


class Player:
    W, H = 30, 50

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.x          = 100.0
        self.y          = float(GROUND_Y - self.H)
        self.vx         = 0.0
        self.vy         = 0.0
        self.on_ground  = False
        self.facing     = 1
        self.health     = 100
        self.shoot_cd   = 0
        self.invincible = 0
        self.anim_frame = 0
        self.anim_timer = 0
        self.moving     = False
        self.weapon     = 'pistol'
        self.ammo       = -1          # -1 = unlimited

    def equip(self, weapon_name: str) -> None:
        self.weapon   = weapon_name
        self.ammo     = WEAPONS[weapon_name]['ammo']
        self.shoot_cd = 0             # ready to fire immediately

    def update(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.vx     = 0.0
        self.moving = False

        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.vx = -5; self.facing = -1; self.moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx =  5; self.facing =  1; self.moving = True
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vy        = JUMP_FORCE
            self.on_ground = False

        self.vy += GRAVITY
        self.x  += self.vx
        self.y  += self.vy

        if self.y + self.H >= GROUND_Y:
            self.y         = GROUND_Y - self.H
            self.vy        = 0
            self.on_ground = True

        self.x = max(0, min(NATIVE_W - self.W, self.x))

        if self.shoot_cd   > 0: self.shoot_cd   -= 1
        if self.invincible > 0: self.invincible -= 1

        if self.moving and self.on_ground:
            self.anim_timer += 1
            if self.anim_timer >= 8:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4
        else:
            self.anim_frame = 0

    def try_melee(self) -> bool:
        """Instant knife strike. Returns True if attack fires (caller applies damage)."""
        if self.shoot_cd > 0:
            return False
        self.shoot_cd = 22
        return True

    def try_shoot(self) -> list[Bullet]:
        """Returns a list of bullets (flamethrower can produce spread shots)."""
        if self.shoot_cd > 0:
            return []

        w = WEAPONS[self.weapon]
        self.shoot_cd = w['cooldown']

        # consume ammo
        if self.ammo > 0:
            self.ammo -= 1
            if self.ammo == 0:
                self.weapon = 'pistol'
                self.ammo   = -1

        bx     = (self.x + self.W) if self.facing == 1 else (self.x - Bullet.W)
        by     = self.y + 20
        speed  = w['speed'] * self.facing
        spread = w['spread']

        if spread > 0:
            # flamethrower: 3-bullet spray
            return [
                Bullet(bx, by + random.uniform(-spread, spread),
                       speed, random.uniform(-spread * 0.5, spread * 0.5),
                       'player', w['damage'], w['color'], w['max_range'])
                for _ in range(3)
            ]
        return [Bullet(bx, by, speed, 0, 'player', w['damage'], w['color'], w['max_range'])]

    def take_damage(self, amt: int) -> bool:
        if self.invincible > 0:
            return False
        self.health    -= amt
        self.invincible = 90
        return True

    def draw(self, surface) -> None:
        draw_player(surface, int(self.x), int(self.y),
                    self.facing, self.anim_frame, self.invincible)
        self._draw_health_bar(surface)

    def _draw_health_bar(self, surface) -> None:
        bw = 40
        bx, by = self.x - 5, self.y - 10
        draw.rect(surface, RED,   (bx, by, bw, 5))
        draw.rect(surface, GREEN, (bx, by, bw * self.health / 100, 5))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)
