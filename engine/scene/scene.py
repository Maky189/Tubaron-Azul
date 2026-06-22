from __future__ import annotations
import abc
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from engine.app import Application


class Scene(abc.ABC):
    """A self-contained screen of the game: a menu, exploration, a battle.

    This is the engine's abstract base class. It cannot be instantiated on its
    own: every concrete screen subclasses it and must at least supply its own
    `Render`. The lifecycle hooks below have harmless defaults so a subclass only
    overrides the moments it actually cares about. Scenes never create each other
    directly — they ask the application to push, pop or replace, which keeps the
    transition policy in one place.
    """

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
        """Which on-screen control scheme the touch overlay should show.

        Defaults to the menu scheme (D-pad + confirm + back), which every
        navigable screen uses. Scenes with their own controls (the live match)
        override this. Imported lazily to keep the engine input layer optional.
        """
        from engine.input.touch_overlay import SCHEME_MENU
        return SCHEME_MENU
