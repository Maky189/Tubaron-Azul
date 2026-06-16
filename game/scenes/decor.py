from __future__ import annotations
import math
import pygame
from engine.rendering.draw import FillVerticalGradient, DrawTextWithOutline, DrawSlantedPanel
from game.scenes.services import FontBank
from game.data import theme

"""Shared menu chrome, all in Cape Verde blue and white."""


def DrawMenuBackground(surface: pygame.Surface, elapsed: float) -> None:
    FillVerticalGradient(surface, theme.CV_BLUE, theme.CV_BLUE_DEEP)
    band = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    drift = (elapsed * 36.0) % 150.0

    for index in range(-2, 9):
        offset = index * 150 + int(drift)
        points = [
            (offset, surface.get_height()),
            (offset + 90, surface.get_height()),
            (offset + 90 + 220, 0),
            (offset + 220, 0),
        ]
        pygame.draw.polygon(band, (255, 255, 255, 10), points)

    surface.blit(band, (0, 0))
    pulse = int(40 + 18 * math.sin(elapsed * 2.0))
    glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 255, 255, pulse), pygame.Rect(-200, -260, surface.get_width() + 400, 440))
    surface.blit(glow, (0, 0))


def DrawHeaderBanner(surface: pygame.Surface, fonts: FontBank, title: str, subtitle: str) -> None:
    banner = pygame.Rect(-20, 24, 540, 58)
    DrawSlantedPanel(surface, banner, (*theme.CV_WHITE, 240), theme.CV_BLUE, 18, 0)
    DrawTextWithOutline(surface, fonts.GetDisplay(40), title, (40, 28), theme.CV_BLUE, theme.CV_BLUE, 0)

    if subtitle:
        DrawTextWithOutline(surface, fonts.GetBold(20), subtitle, (44, 90), theme.CV_WHITE, theme.INK, 2)
