from __future__ import annotations
from engine.mathx.vec2 import Vec2

"""Pitch geometry in world pixels.

The playing field is a plain rectangle from (0,0) to (WIDTH, HEIGHT). The home
team always attacks to the right and defends the left goal; the away team
mirrors. The ball bounces off the four touchlines except inside the goal mouths
at each end, where it can pass through to score — an arcade rule that avoids
throw-ins and corners while still feeling like football.
"""

WIDTH = 1520
HEIGHT = 940
MARGIN = 90

GOAL_WIDTH = 250
GOAL_DEPTH = 64
CENTER = Vec2(WIDTH / 2.0, HEIGHT / 2.0)

BOX_WIDTH = 320
BOX_HEIGHT = 520


def GoalMouthTop() -> float:
    return HEIGHT / 2.0 - GOAL_WIDTH / 2.0


def GoalMouthBottom() -> float:
    return HEIGHT / 2.0 + GOAL_WIDTH / 2.0


def IsWithinMouth(y: float) -> bool:
    return GoalMouthTop() <= y <= GoalMouthBottom()


def LeftGoalCenter() -> Vec2:
    return Vec2(0.0, HEIGHT / 2.0)


def RightGoalCenter() -> Vec2:
    return Vec2(WIDTH, HEIGHT / 2.0)


def AttackingGoalCenter(team_index: int) -> Vec2:
    """The goal a team is trying to score in."""
    if team_index == 0:
        return RightGoalCenter()

    return LeftGoalCenter()


def OwnGoalCenter(team_index: int) -> Vec2:
    if team_index == 0:
        return LeftGoalCenter()

    return RightGoalCenter()


def PlaceFromFormation(nx: float, ny: float, team_index: int) -> Vec2:
    """Maps a normalised formation slot to world coordinates for a team.

    Home (index 0) attacks right, so normalised x runs straight; away mirrors.
    """
    if team_index == 0:
        x = nx * WIDTH
    else:
        x = (1.0 - nx) * WIDTH

    return Vec2(x, ny * HEIGHT)


def PenaltyBox(team_index: int) -> tuple[float, float, float, float]:
    """Returns (left, top, right, bottom) of a team's own penalty box."""
    top = HEIGHT / 2.0 - BOX_HEIGHT / 2.0
    bottom = HEIGHT / 2.0 + BOX_HEIGHT / 2.0

    if team_index == 0:
        return (0.0, top, BOX_WIDTH, bottom)

    return (WIDTH - BOX_WIDTH, top, WIDTH, bottom)
