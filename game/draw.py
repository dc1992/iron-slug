"""
Scaled drawing helpers.
Call setup(scale) once at startup; then use these instead of pygame.draw.*
All coordinates are passed in NATIVE (800x500) space and scaled automatically.
"""
import pygame

_scale: float = 1.0


def setup(scale: float) -> None:
    global _scale
    _scale = scale


def s(v: float) -> int:
    """Scale a single value."""
    return int(v * _scale)


def p(x: float, y: float) -> tuple[int, int]:
    """Scale a point."""
    return (int(x * _scale), int(y * _scale))


def font_size(native_size: int) -> int:
    return max(8, int(native_size * _scale))


# ── shape wrappers ────────────────────────────────────────────────────────────

def rect(surface: pygame.Surface, color, r, width: int = 0) -> None:
    x, y, w, h = r
    pygame.draw.rect(surface, color, (*p(x, y), s(w), s(h)), s(width) if width else 0)


def circle(surface: pygame.Surface, color, center, radius: float, width: int = 0) -> None:
    pygame.draw.circle(surface, color, p(*center), max(1, s(radius)),
                       s(width) if width else 0)


def ellipse(surface: pygame.Surface, color, r, width: int = 0) -> None:
    x, y, w, h = r
    pygame.draw.ellipse(surface, color, (*p(x, y), s(w), s(h)), s(width) if width else 0)


def line(surface: pygame.Surface, color, start, end, width: int = 1) -> None:
    pygame.draw.line(surface, color, p(*start), p(*end), max(1, s(width)))


def polygon(surface: pygame.Surface, color, points, width: int = 0) -> None:
    pygame.draw.polygon(surface, color, [p(x, y) for x, y in points],
                        s(width) if width else 0)


def blit(surface: pygame.Surface, src: pygame.Surface, native_pos) -> None:
    """Blit a surface whose pixel size is already in display space (e.g. rendered text)."""
    x, y = native_pos
    surface.blit(src, p(x, y))
