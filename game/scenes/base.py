from __future__ import annotations
from engine.scene.scene import Scene
from game.scenes.services import GameContext


class GameScene(Scene):
    """Base for every game scene: carries the shared context to the next scene."""

    def __init__(self, ctx: GameContext) -> None:
        super().__init__(ctx.app)
        self.ctx = ctx
