from __future__ import annotations
import pygame
from engine.app import Application
from engine.resources.asset_manager import AssetManager
from game.persistence.save_manager import SaveManager
from game.persistence.records import RecordBook
from game.domain.game_state import GameState
from game.data import theme


class FontBank:
    """Lazily loads and caches the four project fonts at any requested size."""

    def __init__(self, assets: AssetManager) -> None:
        self._assets = assets

    def GetDisplay(self, size: int) -> pygame.font.Font:
        return self._assets.LoadFont(theme.FONT_DISPLAY, size)

    def GetBold(self, size: int) -> pygame.font.Font:
        return self._assets.LoadFont(theme.FONT_BOLD, size)

    def GetSemi(self, size: int) -> pygame.font.Font:
        return self._assets.LoadFont(theme.FONT_SEMI, size)

    def GetBody(self, size: int) -> pygame.font.Font:
        return self._assets.LoadFont(theme.FONT_BODY, size)


class GameContext:
    """Bundles the engine application with the game-wide services and the run.

    Scenes read engine subsystems through 'app' and game services here, and
    create the next scene with the same context, so there is one shared spine.
    """

    def __init__(self, app: Application, save_manager: SaveManager, records: RecordBook) -> None:
        self.app = app
        self.fonts = FontBank(app.GetAssets())
        self.cursor = app.GetAssets().LoadImage("ui/cursor.png")
        self.save_manager = save_manager
        self.records = records
        self.state: GameState | None = None

    def GetState(self) -> GameState:
        if self.state is None:
            raise RuntimeError("no active game state")

        return self.state
