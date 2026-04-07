import pygame
from .settings import (
    SKY_BLUE, GROUND_CLR, GRASS_CLR,
    DARK_GREEN, BROWN, GRAY,
    NATIVE_W, NATIVE_H, GROUND_Y,
)


def draw_bg(surface: pygame.Surface) -> None:
    surface.fill(SKY_BLUE)

    # far mountains
    m1 = [
        (0, 310), (80, 230), (180, 270), (300, 190), (420, 260),
        (540, 180), (660, 240), (800, 200), (800, 410), (0, 410),
    ]
    pygame.draw.polygon(surface, (100, 120, 100), m1)

    # near mountains
    m2 = [
        (0, 360), (100, 290), (220, 330), (350, 265), (470, 320),
        (600, 260), (730, 305), (800, 280), (800, 410), (0, 410),
    ]
    pygame.draw.polygon(surface, (70, 95, 70), m2)

    # ground strip
    pygame.draw.rect(surface, GRASS_CLR,  (0, GROUND_Y,      NATIVE_W, 18))
    pygame.draw.rect(surface, GROUND_CLR, (0, GROUND_Y + 18, NATIVE_W, NATIVE_H))

    # trees
    for tx in [50, 160, 560, 700]:
        pygame.draw.rect(surface, BROWN,       (tx - 5, GROUND_Y - 45, 10, 45))
        pygame.draw.circle(surface, DARK_GREEN, (tx, GROUND_Y - 55), 28)

    # rocks
    for rx in [270, 460, 650]:
        pygame.draw.ellipse(surface, GRAY, (rx - 18, GROUND_Y - 12, 36, 16))
