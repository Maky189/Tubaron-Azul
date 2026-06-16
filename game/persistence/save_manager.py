from __future__ import annotations
import json
import os
from game.domain.game_state import GameState


class SaveError(Exception):
    pass


class SaveManager:
    """Reads and writes a single run to a JSON file.

    The domain object knows its own snapshot shape, so this class only owns the
    file: where it lives, how to write it atomically and how to fail loudly.
    """

    def __init__(self, path: str) -> None:
        self._path = path

    def HasSave(self) -> bool:
        return os.path.exists(self._path)

    def Save(self, state: GameState) -> None:
        snapshot = state.CaptureSnapshot()
        directory = os.path.dirname(self._path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        temp_path = self._path + ".tmp"

        try:
            with open(temp_path, "w", encoding="utf-8") as handle:
                json.dump(snapshot, handle, indent=2)

            os.replace(temp_path, self._path)
        except OSError as error:
            raise SaveError(f"failed to write save '{self._path}': {error}") from error

    def Load(self) -> GameState:
        try:
            with open(self._path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as error:
            raise SaveError(f"failed to read save '{self._path}': {error}") from error

        state = GameState()
        state.ApplySnapshot(data)
        return state

    def Delete(self) -> None:
        if os.path.exists(self._path):
            os.remove(self._path)
