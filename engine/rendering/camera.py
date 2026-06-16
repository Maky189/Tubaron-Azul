from __future__ import annotations
from engine.mathx.vec2 import Vec2


class Camera:
    """Maps world coordinates to screen coordinates and follows a target smoothly.

    The camera clamps to the level bounds so the view never shows past the edge
    of the map.
    """

    def __init__(self, view_width: int, view_height: int) -> None:
        self._view_width = view_width
        self._view_height = view_height
        self._position = Vec2(0.0, 0.0)
        self._map_width = view_width
        self._map_height = view_height

    def SetBounds(self, width: int, height: int) -> None:
        self._map_width = width
        self._map_height = height

    def GetPosition(self) -> Vec2:
        return self._position

    def FollowTarget(self, target: Vec2, dt: float) -> None:
        desired = Vec2(
            target.x - self._view_width * 0.5,
            target.y - self._view_height * 0.5,
        )
        smoothing = min(1.0, dt * 8.0)
        moved = self._position + (desired - self._position) * smoothing
        self._position = self._ClampToBounds(moved)

    def CenterOn(self, target: Vec2) -> None:
        desired = Vec2(
            target.x - self._view_width * 0.5,
            target.y - self._view_height * 0.5,
        )
        self._position = self._ClampToBounds(desired)

    def _ClampToBounds(self, position: Vec2) -> Vec2:
        return Vec2(
            self._ClampAxis(position.x, self._map_width, self._view_width),
            self._ClampAxis(position.y, self._map_height, self._view_height),
        )

    def _ClampAxis(self, value: float, map_size: int, view_size: int) -> float:
        if map_size <= view_size:
            return (map_size - view_size) / 2.0

        return min(max(value, 0.0), float(map_size - view_size))

    def WorldToScreen(self, world: Vec2) -> Vec2:
        return world - self._position
