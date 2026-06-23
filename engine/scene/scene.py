from __future__ import annotations
import abc
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from engine.app import Application


class Scene(abc.ABC):

    def __init__(self, app: Application) -> None:
        self.app = app

    def OnEnter(self) -> None:
        pass

    def OnExit(self) -> None:
        pass

    def OnResume(self) -> None:
        pass

    def HandleEvent(self, event: pygame.event.Event) -> None:
        pass

    def Update(self, dt: float) -> None:
        pass

    @abc.abstractmethod
    def Render(self, surface: pygame.Surface) -> None:
        """Draw the scene. Concrete scenes must implement this."""
        raise NotImplementedError

    def IsOpaque(self) -> bool:
        """When False the scene below keeps drawing, used for overlay menus."""
        return True

    def TouchControls(self) -> str:
        from engine.input.touch_overlay import SCHEME_MENU
        return SCHEME_MENU
