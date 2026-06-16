from __future__ import annotations
import pygame
from engine.mathx.vec2 import Vec2
from game.match import pitch
from game.data import theme

"""Draws the pitch: a baked grass-and-lines surface plus the goals on top.

The static field (mowing stripes, markings) is rendered once into a surface the
size of the playing area and scrolled under the camera. Goals are drawn each
frame in world space so their nets can spill past the touchline at the screen
edge.
"""

_STRIPE = 95
_LINE = 4
_pitch_surface: pygame.Surface | None = None


def BuildPitchSurface() -> pygame.Surface:
    global _pitch_surface

    if _pitch_surface is not None:
        return _pitch_surface

    surface = pygame.Surface((pitch.WIDTH, pitch.HEIGHT))
    _DrawGrass(surface)
    _DrawMarkings(surface)
    _pitch_surface = surface
    return surface


def _DrawGrass(surface: pygame.Surface) -> None:
    columns = pitch.WIDTH // _STRIPE + 1

    for index in range(columns):
        color = theme.GRASS_DARK
        if index % 2 == 0:
            color = theme.GRASS_LIGHT

        rect = pygame.Rect(index * _STRIPE, 0, _STRIPE, pitch.HEIGHT)
        pygame.draw.rect(surface, color, rect)


def _DrawMarkings(surface: pygame.Surface) -> None:
    white = theme.LINE_WHITE
    inset = 14
    field = pygame.Rect(inset, inset, pitch.WIDTH - inset * 2, pitch.HEIGHT - inset * 2)
    pygame.draw.rect(surface, white, field, _LINE)

    mid_x = pitch.WIDTH // 2
    pygame.draw.line(surface, white, (mid_x, inset), (mid_x, pitch.HEIGHT - inset), _LINE)
    center = (mid_x, pitch.HEIGHT // 2)
    pygame.draw.circle(surface, white, center, 120, _LINE)
    pygame.draw.circle(surface, white, center, 7)

    _DrawBox(surface, white, 0)
    _DrawBox(surface, white, 1)


def _DrawBox(surface: pygame.Surface, white, team_index: int) -> None:
    left, top, right, bottom = pitch.PenaltyBox(team_index)
    rect = pygame.Rect(int(left), int(top), int(right - left), int(bottom - top))
    pygame.draw.rect(surface, white, rect, _LINE)

    # Six-yard box and penalty spot.
    small_w = 130
    small_h = 260
    spot_x = right - 200
    if team_index == 0:
        small = pygame.Rect(0, int(pitch.HEIGHT / 2 - small_h / 2), small_w, small_h)
        spot_x = left + 200
    else:
        small = pygame.Rect(pitch.WIDTH - small_w, int(pitch.HEIGHT / 2 - small_h / 2), small_w, small_h)
        spot_x = right - 200

    pygame.draw.rect(surface, white, small, _LINE)
    pygame.draw.circle(surface, white, (int(spot_x), pitch.HEIGHT // 2), 6)


def DrawGoals(surface: pygame.Surface, cam: Vec2) -> None:
    _DrawGoal(surface, cam, 0)
    _DrawGoal(surface, cam, 1)


def _DrawGoal(surface: pygame.Surface, cam: Vec2, side: int) -> None:
    top = pitch.GoalMouthTop()
    bottom = pitch.GoalMouthBottom()
    depth = pitch.GOAL_DEPTH

    if side == 0:
        line_x = 0.0
        net_x = -depth
    else:
        line_x = pitch.WIDTH
        net_x = pitch.WIDTH

    sx = int(line_x - cam.x)
    nx = int(net_x - cam.x)
    sy_top = int(top - cam.y)
    sy_bottom = int(bottom - cam.y)

    net_rect = pygame.Rect(min(sx, nx), sy_top, depth, sy_bottom - sy_top)
    net = pygame.Surface((depth, sy_bottom - sy_top), pygame.SRCALPHA)
    net.fill((250, 252, 255, 60))
    _HatchNet(net)
    surface.blit(net, net_rect.topleft)

    pygame.draw.rect(surface, theme.WHITE, net_rect, 5)
    pygame.draw.line(surface, theme.WHITE, (sx, sy_top - 4), (sx, sy_bottom + 4), 7)


def _HatchNet(net: pygame.Surface) -> None:
    width = net.get_width()
    height = net.get_height()
    mesh = (255, 255, 255, 45)

    for x in range(0, width, 9):
        pygame.draw.line(net, mesh, (x, 0), (x, height), 1)

    for y in range(0, height, 9):
        pygame.draw.line(net, mesh, (0, y), (width, y), 1)
