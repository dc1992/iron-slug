import pygame
from .settings import (
    NATIVE_W, NATIVE_H,
    BLACK, WHITE, RED, GREEN, YELLOW,
)
from .weapon import WEAPONS

_font_hud:   pygame.font.Font | None = None
_font_big:   pygame.font.Font | None = None
_font_small: pygame.font.Font | None = None


def init_fonts() -> None:
    global _font_hud, _font_big, _font_small
    _font_hud   = pygame.font.Font(None, 28)
    _font_big   = pygame.font.Font(None, 74)
    _font_small = pygame.font.Font(None, 20)


def draw_hud(surface: pygame.Surface, player, score: int, lives: int,
             wave: int, enemies_left: int) -> None:
    pygame.draw.rect(surface, BLACK, (0, 0, NATIVE_W, 38))
    surface.blit(_font_hud.render(f"SCORE: {score:06d}", True, WHITE),  (10,  7))
    surface.blit(_font_hud.render(f"LIVES: {lives}",     True, WHITE),  (210, 7))
    surface.blit(_font_hud.render(f"WAVE: {wave}",       True, YELLOW), (350, 7))
    surface.blit(_font_hud.render(f"ENEMIES: {enemies_left}", True, (255, 160, 0)), (460, 7))

    # weapon + ammo
    w_def   = WEAPONS[player.weapon]
    w_color = w_def['color']
    w_label = w_def['label']
    ammo_str = '∞' if player.ammo == -1 else str(player.ammo)
    surface.blit(_font_hud.render(f"{w_label}  {ammo_str}", True, w_color), (600, 7))

    # HP bar
    hpx = NATIVE_W - 155
    pygame.draw.rect(surface, RED,   (hpx, 11, 100, 14))
    pygame.draw.rect(surface, GREEN, (hpx, 11, player.health, 14))
    surface.blit(_font_hud.render("HP", True, WHITE), (hpx - 30, 7))

    tip = _font_small.render(
        "A/D or ←/→: Move   W/↑/Space: Jump   Shift: Shoot   ESC: Quit",
        True, (180, 180, 180),
    )
    surface.blit(tip, (NATIVE_W // 2 - tip.get_width() // 2, NATIVE_H - 22))


def draw_game_over(surface: pygame.Surface, score: int) -> None:
    overlay = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    t1 = _font_big.render("GAME OVER", True, RED)
    t2 = _font_hud.render(f"Final Score: {score:06d}", True, WHITE)
    t3 = _font_hud.render("Press R to Restart   Q to Quit", True, YELLOW)
    surface.blit(t1, (NATIVE_W // 2 - t1.get_width() // 2, 140))
    surface.blit(t2, (NATIVE_W // 2 - t2.get_width() // 2, 250))
    surface.blit(t3, (NATIVE_W // 2 - t3.get_width() // 2, 310))


def draw_wave_banner(surface: pygame.Surface, wave: int, timer: int) -> None:
    if timer <= 0:
        return
    t = _font_big.render(f"WAVE  {wave}", True, YELLOW)
    s = pygame.Surface((t.get_width(), t.get_height()), pygame.SRCALPHA)
    s.blit(t, (0, 0))
    s.set_alpha(min(255, timer * 8))
    surface.blit(s, (NATIVE_W // 2 - t.get_width() // 2, NATIVE_H // 2 - 40))
