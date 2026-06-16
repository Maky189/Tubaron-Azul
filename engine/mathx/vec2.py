from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scale: float) -> Vec2:
        return Vec2(self.x * scale, self.y * scale)

    def __str__(self) -> str:
        return f"({self.x:.1f}, {self.y:.1f})"

    def GetLength(self) -> float:
        return math.hypot(self.x, self.y)

    def GetNormalized(self) -> Vec2:
        length = self.GetLength()

        if length == 0.0:
            return Vec2(0.0, 0.0)

        return Vec2(self.x / length, self.y / length)

    def GetDistanceTo(self, other: Vec2) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def AsTuple(self) -> tuple[int, int]:
        return (int(self.x), int(self.y))
