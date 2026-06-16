from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.ecs.world import World


class System:
    """Base for all ECS systems. A system holds behaviour, never persistent state."""

    def Update(self, world: World, dt: float) -> None:
        raise NotImplementedError(f"{type(self).__name__} must implement Update")


class RenderSystem:
    """Base for systems that draw. Kept separate so update and draw passes stay ordered."""

    def Render(self, world: World, surface) -> None:
        raise NotImplementedError(f"{type(self).__name__} must implement Render")
