from __future__ import annotations
import pygame


class SpriteSheet:
    """Slices a single image into a grid of equally sized frames."""

    def __init__(self, sheet: pygame.Surface, frame_width: int, frame_height: int) -> None:
        self._sheet = sheet
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._columns = sheet.get_width() // frame_width

    def GetFrame(self, index: int) -> pygame.Surface:
        column = index % self._columns
        row = index // self._columns
        region = pygame.Rect(
            column * self._frame_width,
            row * self._frame_height,
            self._frame_width,
            self._frame_height,
        )
        return self._sheet.subsurface(region).copy()


class Animation:
    """Advances through a list of frames at a fixed rate and loops."""

    def __init__(self, frames: list[pygame.Surface], frame_duration: float) -> None:
        self._frames = frames
        self._frame_duration = frame_duration
        self._elapsed = 0.0
        self._index = 0

    def Reset(self) -> None:
        self._elapsed = 0.0
        self._index = 0

    def Advance(self, dt: float) -> None:
        if len(self._frames) <= 1:
            return

        self._elapsed += dt

        while self._elapsed >= self._frame_duration:
            self._elapsed -= self._frame_duration
            self._index = (self._index + 1) % len(self._frames)

    def GetCurrentFrame(self) -> pygame.Surface:
        return self._frames[self._index]
