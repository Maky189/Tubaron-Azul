from __future__ import annotations
import pygame


class InputManager:
    """Tracks key state for the current frame.

    Distinguishes a held key from a freshly pressed one so menus can react to
    a single press while movement can react to a continuous hold.
    """

    def __init__(self) -> None:
        self._down: set[int] = set()
        self._pressed_this_frame: set[int] = set()
        self._released_this_frame: set[int] = set()
        self._quit_requested: bool = False

    def BeginFrame(self) -> None:
        self._pressed_this_frame.clear()
        self._released_this_frame.clear()

    def HandleEvent(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self._quit_requested = True
            return

        if event.type == pygame.KEYDOWN:
            self._down.add(event.key)
            self._pressed_this_frame.add(event.key)
            return

        if event.type == pygame.KEYUP:
            self._down.discard(event.key)
            self._released_this_frame.add(event.key)

    def IsHeld(self, key: int) -> bool:
        return key in self._down

    def WasPressed(self, key: int) -> bool:
        return key in self._pressed_this_frame

    def WasReleased(self, key: int) -> bool:
        return key in self._released_this_frame

    def IsQuitRequested(self) -> bool:
        return self._quit_requested
