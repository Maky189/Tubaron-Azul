from __future__ import annotations
import os
import sys
import math
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

ASSET_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
OUTLINE = (16, 12, 26)

CV_BLUE = (0, 56, 147)
CV_WHITE = (244, 246, 252)
CV_RED = (207, 20, 43)
CV_YELLOW = (255, 205, 0)


def _Clamp(value: int) -> int:
    return max(0, min(255, value))


def _Star(surface: pygame.Surface, cx: float, cy: float, outer: float, inner: float, color) -> None:
    points = []

    for index in range(10):
        radius = inner

        if index % 2 == 0:
            radius = outer

        angle = -math.pi / 2 + index * math.pi / 5
        points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))

    pygame.draw.polygon(surface, color, points)


def _BuildCursor() -> pygame.Surface:
    cursor = pygame.Surface((22, 22), pygame.SRCALPHA)
    points = [(2, 2), (20, 11), (2, 20), (8, 11)]
    pygame.draw.polygon(cursor, CV_YELLOW, points)
    pygame.draw.polygon(cursor, OUTLINE, points, 2)
    return cursor


def _BuildPitchFloor() -> pygame.Surface:
    size = 48
    surface = pygame.Surface((size, size))
    light = (56, 150, 66)
    dark = (46, 130, 56)
    surface.fill(light)
    pygame.draw.rect(surface, dark, pygame.Rect(size // 2, 0, size // 2, size))

    for _ in range(150):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        base = surface.get_at((x, y))
        delta = random.randint(-10, 10)
        surface.set_at((x, y), (_Clamp(base[0] + delta), _Clamp(base[1] + delta), _Clamp(base[2] + delta)))

    return surface


def _BuildPitchWall() -> pygame.Surface:
    size = 48
    surface = pygame.Surface((size, size))
    surface.fill((22, 30, 78))
    pygame.draw.rect(surface, (14, 20, 54), pygame.Rect(0, 0, size, 26))
    crowd = [(200, 210, 230), (230, 200, 120), (220, 120, 120), (120, 160, 230)]

    for _ in range(70):
        x = random.randint(0, size - 1)
        y = random.randint(0, 24)
        surface.set_at((x, y), random.choice(crowd))

    pygame.draw.rect(surface, (36, 52, 140), pygame.Rect(0, 26, size, 16))
    pygame.draw.line(surface, CV_WHITE, (0, 30), (size, 30), 2)
    pygame.draw.line(surface, CV_YELLOW, (0, 40), (size, 40), 2)
    pygame.draw.rect(surface, (46, 130, 56), pygame.Rect(0, 42, size, 6))
    return surface


def _BuildFloodlight() -> pygame.Surface:
    width = 24
    height = 60
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, (80, 86, 102), pygame.Rect(width // 2 - 2, 16, 4, height - 18))
    pygame.draw.rect(surface, (60, 66, 80), pygame.Rect(width // 2 - 5, height - 6, 10, 6))
    head = pygame.Rect(3, 2, width - 6, 14)
    pygame.draw.rect(surface, (70, 76, 92), head, border_radius=3)
    pygame.draw.rect(surface, (150, 160, 185), head, 1, border_radius=3)

    for col in range(3):
        for row in range(2):
            pygame.draw.rect(surface, (235, 242, 255), pygame.Rect(6 + col * 5, 4 + row * 5, 4, 4))

    return surface


def _BuildBall() -> pygame.Surface:
    size = 40
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)
    radius = 17
    pygame.draw.circle(surface, (245, 247, 252), center, radius)
    pygame.draw.circle(surface, (20, 22, 30), center, radius, 2)
    pentagon = []

    for index in range(5):
        angle = -math.pi / 2 + index * 2 * math.pi / 5
        pentagon.append((center[0] + math.cos(angle) * 7, center[1] + math.sin(angle) * 7))

    pygame.draw.polygon(surface, (20, 22, 30), pentagon)

    for index in range(5):
        angle = -math.pi / 2 + index * 2 * math.pi / 5 + math.pi / 5
        inner = (center[0] + math.cos(angle) * 7, center[1] + math.sin(angle) * 7)
        outer = (center[0] + math.cos(angle) * radius, center[1] + math.sin(angle) * radius)
        pygame.draw.line(surface, (20, 22, 30), inner, outer, 2)

    return surface


def _BuildCone() -> pygame.Surface:
    width = 28
    height = 30
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, (180, 90, 20), pygame.Rect(2, height - 8, width - 4, 8))
    pygame.draw.polygon(surface, (240, 120, 30), [(width // 2, 3), (6, height - 4), (width - 6, height - 4)])
    pygame.draw.polygon(surface, (245, 245, 250), [(9, height - 13), (width - 9, height - 13), (width - 11, height - 19), (11, height - 19)])
    return surface


def _BuildFlag() -> pygame.Surface:
    width = 168
    height = 100
    surface = pygame.Surface((width, height))
    surface.fill(CV_BLUE)
    band = height // 9
    top = int(height * 0.5)
    pygame.draw.rect(surface, CV_WHITE, pygame.Rect(0, top, width, band))
    pygame.draw.rect(surface, CV_RED, pygame.Rect(0, top + band, width, band))
    pygame.draw.rect(surface, CV_WHITE, pygame.Rect(0, top + 2 * band, width, band))
    ring_x = int(width * 0.375)
    ring_y = top + band + band // 2
    ring_r = int(band * 2.2)

    for index in range(10):
        angle = -math.pi / 2 + index * 2 * math.pi / 10
        star_x = ring_x + math.cos(angle) * ring_r
        star_y = ring_y + math.sin(angle) * ring_r
        _Star(surface, star_x, star_y, 5.0, 2.0, CV_YELLOW)

    pygame.draw.rect(surface, OUTLINE, pygame.Rect(0, 0, width, height), 2)
    return surface


def _BuildCrest() -> pygame.Surface:
    width = 110
    height = 124
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    shield = [(8, 6), (width - 8, 6), (width - 8, int(height * 0.55)), (width // 2, height - 6), (8, int(height * 0.55))]
    pygame.draw.polygon(surface, CV_BLUE, shield)
    pygame.draw.polygon(surface, CV_WHITE, shield, 4)
    fin = [(width // 2 - 22, int(height * 0.64)), (width // 2 + 22, int(height * 0.64)), (width // 2 + 6, int(height * 0.32))]
    pygame.draw.polygon(surface, CV_WHITE, fin)
    pygame.draw.line(surface, CV_WHITE, (width // 2 - 26, int(height * 0.70)), (width // 2 + 26, int(height * 0.70)), 3)

    for fraction in (0.32, 0.5, 0.68):
        _Star(surface, width * fraction, height * 0.17, 6.0, 2.5, CV_YELLOW)

    return surface


def _Save(surface: pygame.Surface, *parts: str) -> None:
    folder = os.path.join(ASSET_ROOT, *parts[:-1])
    os.makedirs(folder, exist_ok=True)
    pygame.image.save(surface, os.path.join(folder, parts[-1]))


def GenerateAll() -> None:
    """Builds the procedural art: the menu cursor, the football pitch tiles and
    props, and the Cabo Verde / Tubarões motifs.

    The player and rival sprites are real downloaded pixel art under
    assets/external/, palette-tinted into the blue-and-white kit; ambient
    lighting and particles are generated at runtime.
    """
    pygame.init()
    _Save(_BuildCursor(), "ui", "cursor.png")
    _Save(_BuildPitchFloor(), "pitch", "floor.png")
    _Save(_BuildPitchWall(), "pitch", "wall.png")
    _Save(_BuildFloodlight(), "pitch", "floodlight.png")
    _Save(_BuildBall(), "pitch", "ball.png")
    _Save(_BuildCone(), "pitch", "cone.png")
    _Save(_BuildFlag(), "capeverde", "flag.png")
    _Save(_BuildCrest(), "capeverde", "crest.png")
    pygame.quit()
    print("generated cursor, pitch tiles/props and Cabo Verde motifs")


if __name__ == "__main__":
    GenerateAll()
