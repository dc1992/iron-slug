"""
Pixel-art drawing routines for player and enemy.
All coordinates are in native (800x500) space; game.draw handles scaling.
"""
import math
import game.draw as draw
from .settings import BLACK, DARK_GRAY


def draw_player(
    surface,
    x: int, y: int,
    facing: int,
    anim_frame: int,
    invincible: int,
) -> None:
    if invincible > 0 and (invincible // 5) % 2 == 0:
        return

    skin    = (255, 200, 150)
    uniform = ( 30, 110,  30)
    pants   = ( 40,  80,  40)
    boot    = ( 60,  30,  10)
    helmet  = (120,  80,  20)
    belt    = ( 80,  60,  10)

    draw.rect(surface, boot,    (x +  3, y + 41, 11, 9))
    draw.rect(surface, boot,    (x + 16, y + 41, 11, 9))
    draw.rect(surface, pants,   (x +  5, y + 28,  9, 14))
    draw.rect(surface, pants,   (x + 16, y + 28,  9, 14))
    draw.rect(surface, uniform, (x +  3, y + 14, 24, 16))
    draw.rect(surface, belt,    (x +  3, y + 27, 24,  3))
    draw.rect(surface, skin,    (x +  7, y +  3, 16, 13))
    draw.rect(surface, helmet,  (x +  5, y,      20,  9))
    draw.rect(surface, helmet,  (x +  3, y +  7, 24,  4))
    eye_x = (x + 14) if facing == 1 else (x + 8)
    draw.rect(surface, BLACK, (eye_x, y + 7, 3, 3))
    if facing == 1:
        draw.rect(surface, DARK_GRAY, (x + 27, y + 18, 14, 5))
        draw.rect(surface, DARK_GRAY, (x + 39, y + 16,  3, 9))
    else:
        draw.rect(surface, DARK_GRAY, (x - 14, y + 18, 14, 5))
        draw.rect(surface, DARK_GRAY, (x - 14, y + 16,  3, 9))


def draw_enemy(surface, x: int, y: int, facing: int) -> None:
    skin    = (255, 200, 150)
    uniform = (160,  20,  20)
    pants   = (120,  10,  10)
    boot    = ( 30,  30,  30)
    helmet  = ( 90,   0,   0)

    draw.rect(surface, boot,    (x +  3, y + 37, 10,  8))
    draw.rect(surface, boot,    (x + 17, y + 37, 10,  8))
    draw.rect(surface, pants,   (x +  5, y + 24,  9, 14))
    draw.rect(surface, pants,   (x + 16, y + 24,  9, 14))
    draw.rect(surface, uniform, (x +  3, y + 12, 24, 14))
    draw.rect(surface, skin,    (x +  6, y +  2, 18, 12))
    draw.rect(surface, helmet,  (x +  4, y -  2, 22,  9))
    eye_x = (x + 15) if facing == 1 else (x + 8)
    draw.rect(surface, BLACK, (eye_x, y + 5, 3, 3))
    if facing == 1:
        draw.rect(surface, DARK_GRAY, (x + 27, y + 15, 12, 5))
    else:
        draw.rect(surface, DARK_GRAY, (x - 12, y + 15, 12, 5))
