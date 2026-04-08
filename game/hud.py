import pygame
import game.draw as draw
from .settings import (
    NATIVE_W, NATIVE_H,
    BLACK, WHITE, RED, GREEN, YELLOW,
)
from .weapon import WEAPONS

_font_hud:   pygame.font.Font | None = None
_font_big:   pygame.font.Font | None = None
_font_small: pygame.font.Font | None = None


def init_fonts(scale: float = 1.0) -> None:
    global _font_hud, _font_big, _font_small
    _font_hud   = pygame.font.Font(None, draw.font_size(28))
    _font_big   = pygame.font.Font(None, draw.font_size(74))
    _font_small = pygame.font.Font(None, draw.font_size(20))


HUD_H = 46   # height of the HUD bar (two rows)

def draw_hud(surface, player, score: int, lives: int,
             wave: int, enemies_left: int) -> None:
    draw.rect(surface, BLACK, (0, 0, NATIVE_W, HUD_H))

    # ── row 1: score / lives / wave / enemies ────────────────────────────────
    draw.blit(surface, _font_hud.render(f"SCORE: {score:06d}", True, WHITE),       ( 10, 5))
    draw.blit(surface, _font_hud.render(f"LIVES: {lives}",     True, WHITE),       (200, 5))
    draw.blit(surface, _font_hud.render(f"WAVE: {wave}",       True, YELLOW),      (330, 5))
    draw.blit(surface, _font_hud.render(f"ENEMIES: {enemies_left}", True, (255, 160, 0)), (450, 5))

    # ── row 2: weapon + ammo (left) | HP bar (right) ─────────────────────────
    w_def    = WEAPONS[player.weapon]
    ammo_str = 'inf.' if player.ammo == -1 else str(player.ammo)
    draw.blit(surface, _font_hud.render(f"{w_def['label']}  {ammo_str}", True, w_def['color']), (10, 27))

    hpx = NATIVE_W - 145
    draw.blit(surface, _font_hud.render("HP", True, WHITE), (hpx - 525, 27))
    draw.rect(surface, RED,   (hpx - 490, 30, 100, 12))
    draw.rect(surface, GREEN, (hpx - 490, 30, player.health, 12))

    tip = _font_small.render(
        "A/D or arrows keys: Move   W/Up Arrow/Space: Jump   K: Shoot   L: Dash   P: Pause   ESC: Quit",
        True, (180, 180, 180),
    )
    surface.blit(tip, (draw.s(NATIVE_W) // 2 - tip.get_width() // 2, draw.s(NATIVE_H) - tip.get_height() - 4))


def draw_game_over(surface, score: int) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    t1 = _font_big.render("GAME OVER", True, RED)
    t2 = _font_hud.render(f"Final Score: {score:06d}", True, WHITE)
    t3 = _font_hud.render("Press R to Restart   Q to Quit", True, YELLOW)
    cx = draw.s(NATIVE_W) // 2
    surface.blit(t1, (cx - t1.get_width() // 2, draw.s(140)))
    surface.blit(t2, (cx - t2.get_width() // 2, draw.s(250)))
    surface.blit(t3, (cx - t3.get_width() // 2, draw.s(310)))


def _render_banner(surface, text: str, color: tuple, timer: int, cy_native: int) -> None:
    t  = _font_big.render(text, True, color)
    s  = pygame.Surface((t.get_width(), t.get_height()), pygame.SRCALPHA)
    s.blit(t, (0, 0))
    s.set_alpha(min(255, timer * 8))
    cx = draw.s(NATIVE_W) // 2
    surface.blit(s, (cx - t.get_width() // 2, draw.s(cy_native)))


def draw_wave_banner(surface, wave: int, timer: int) -> None:
    if timer > 0:
        _render_banner(surface, f"WAVE  {wave}", YELLOW, timer, NATIVE_H // 2 - 40)


def draw_paused(surface) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))
    t = _font_big.render("PAUSED", True, WHITE)
    cx = draw.s(NATIVE_W) // 2
    cy = draw.s(NATIVE_H) // 2
    surface.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))
