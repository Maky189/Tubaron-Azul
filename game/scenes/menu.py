from __future__ import annotations
import pygame
from engine.rendering.draw import DrawSlantedPanel, DrawTextWithOutline
from game.scenes.services import FontBank
from game.data import theme


class MenuOption:
    def __init__(self, label: str, value: str, enabled: bool = True) -> None:
        self.label = label
        self.value = value
        self.enabled = enabled


class Menu:
    """A vertical list of options driven by the up/down keys.

    It owns only selection state and how to draw itself; what each option does
    is decided by the scene that reads GetSelectedValue.
    """

    def __init__(self, options: list[MenuOption]) -> None:
        self._options = options
        self._index = 0
        self._SkipToEnabled(1)

    def SetOptions(self, options: list[MenuOption]) -> None:
        self._options = options
        self._index = 0
        self._SkipToEnabled(1)

    def MoveUp(self) -> None:
        self._index = (self._index - 1) % len(self._options)
        self._SkipToEnabled(-1)

    def MoveDown(self) -> None:
        self._index = (self._index + 1) % len(self._options)
        self._SkipToEnabled(1)

    def _SkipToEnabled(self, step: int) -> None:
        for _ in range(len(self._options)):
            if self._options[self._index].enabled:
                return

            self._index = (self._index + step) % len(self._options)

    def GetSelectedValue(self) -> str:
        return self._options[self._index].value

    def GetIndex(self) -> int:
        return self._index

    def Draw(self, surface: pygame.Surface, fonts: FontBank, cursor: pygame.Surface, origin: tuple[int, int], width: int) -> None:
        font = fonts.GetBold(30)
        x, y = origin
        spacing = 46

        for index, option in enumerate(self._options):
            rect = pygame.Rect(x, y + index * spacing, width, 40)
            self._DrawOption(surface, font, cursor, option, rect, index == self._index)

    def _DrawOption(self, surface, font, cursor, option, rect, selected) -> None:
        if selected:
            DrawSlantedPanel(surface, rect, (*theme.CV_WHITE, 240), theme.CV_BLUE, 12, 0)
            text_color = theme.CV_BLUE
            surface.blit(cursor, (rect.left - 26, rect.top + 8))
        else:
            DrawSlantedPanel(surface, rect, (*theme.CV_BLUE_DEEP, 205), theme.CV_WHITE, 12, 2)
            text_color = theme.CV_WHITE

        if not option.enabled:
            text_color = theme.GREY

        DrawTextWithOutline(surface, font, option.label, (rect.left + 18, rect.top + 4), text_color, theme.INK, 1)
