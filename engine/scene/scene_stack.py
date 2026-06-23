from __future__ import annotations
from engine.scene.scene import Scene


class SceneStack:

    def __init__(self) -> None:
        self._scenes: list[Scene] = []
        self._pending: list[tuple[str, Scene | None]] = []

    def IsEmpty(self) -> bool:
        return not self._scenes

    def GetActive(self) -> Scene | None:
        if not self._scenes:
            return None

        return self._scenes[-1]

    def RequestPush(self, scene: Scene) -> None:
        self._pending.append(("push", scene))

    def RequestPop(self) -> None:
        self._pending.append(("pop", None))

    def RequestReplace(self, scene: Scene) -> None:
        self._pending.append(("replace", scene))

    def RequestClearTo(self, scene: Scene) -> None:
        self._pending.append(("clear", scene))

    def ApplyPending(self) -> None:
        for action, scene in self._pending:
            self._ApplyOne(action, scene)

        self._pending.clear()

    def _ApplyOne(self, action: str, scene: Scene | None) -> None:
        if action == "push":
            self._scenes.append(scene) 
            scene.OnEnter() 
            return

        if action == "pop":
            self._PopTop()
            active = self.GetActive()

            if active is not None:
                active.OnResume()

            return

        if action == "replace":
            self._PopTop()
            self._scenes.append(scene) 
            scene.OnEnter() 
            return

        if action == "clear":
            while self._scenes:
                self._PopTop()

            self._scenes.append(scene)  
            scene.OnEnter()  

    def _PopTop(self) -> None:
        if self._scenes:
            self._scenes.pop().OnExit()

    def IterVisible(self) -> list[Scene]:
        first_visible = 0

        for index in range(len(self._scenes) - 1, -1, -1):
            first_visible = index

            if self._scenes[index].IsOpaque():
                break

        return self._scenes[first_visible:]
