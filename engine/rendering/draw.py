from __future__ import annotations
import pygame

Color = tuple[int, int, int]
ColorA = tuple[int, int, int, int]


def DrawTextWithOutline(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    position: tuple[int, int],
    fill: Color,
    outline: Color,
    thickness: int = 2,
) -> pygame.Rect:
    base = font.render(text, True, fill)
    edge = font.render(text, True, outline)
    x, y = position

    for offset_x in range(-thickness, thickness + 1):
        for offset_y in range(-thickness, thickness + 1):
            if offset_x != 0 or offset_y != 0:
                surface.blit(edge, (x + offset_x, y + offset_y))

    return surface.blit(base, (x, y))


def MeasureText(font: pygame.font.Font, text: str) -> tuple[int, int]:
    return font.size(text)


def DrawSlantedPanel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill: ColorA,
    border: Color,
    slant: int = 14,
    border_width: int = 3,
) -> None:
    """Draws the angular parallelogram panel that defines the menu look."""
    points = [
        (rect.left + slant, rect.top),
        (rect.right, rect.top),
        (rect.right - slant, rect.bottom),
        (rect.left, rect.bottom),
    ]
    panel = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(panel, fill, points)
    surface.blit(panel, (0, 0))

    if border_width > 0:
        pygame.draw.polygon(surface, border, points, border_width)


def DrawBar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    ratio: float,
    fill: Color,
    background: Color,
    border: Color,
) -> None:
    clamped = min(max(ratio, 0.0), 1.0)
    pygame.draw.rect(surface, background, rect)
    inner = pygame.Rect(rect.left, rect.top, int(rect.width * clamped), rect.height)
    pygame.draw.rect(surface, fill, inner)
    pygame.draw.rect(surface, border, rect, 2)


def FillVerticalGradient(surface: pygame.Surface, top: Color, bottom: Color) -> None:
    height = surface.get_height()
    width = surface.get_width()

    for y in range(height):
        blend = y / max(height - 1, 1)
        red = int(top[0] + (bottom[0] - top[0]) * blend)
        green = int(top[1] + (bottom[1] - top[1]) * blend)
        blue = int(top[2] + (bottom[2] - top[2]) * blend)
        pygame.draw.line(surface, (red, green, blue), (0, y), (width, y))
