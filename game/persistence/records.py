from __future__ import annotations
import json
import os

"""The high-score book: the best World Cup runs, highest score first."""

_STAGE_NAMES = ["Grupos", "Grupos", "Oitavos", "Quartos", "Meias", "Final", "Campeão"]


class RecordEntry:
    def __init__(self, name: str, score: int, stage_reached: int, outcome: str) -> None:
        self.name = name
        self.score = score
        self.stage_reached = stage_reached
        self.outcome = outcome

    def StageLabel(self) -> str:
        index = min(max(self.stage_reached, 0), len(_STAGE_NAMES) - 1)
        return _STAGE_NAMES[index]

    def ToDict(self) -> dict:
        return {
            "name": self.name,
            "score": self.score,
            "stage_reached": self.stage_reached,
            "outcome": self.outcome,
        }

    @staticmethod
    def FromDict(data: dict) -> "RecordEntry":
        return RecordEntry(
            data.get("name", "????"),
            int(data.get("score", 0)),
            int(data.get("stage_reached", 1)),
            data.get("outcome", "eliminado"),
        )

    def __str__(self) -> str:
        return f"{self.name:<8} {self.score:>6}  {self.StageLabel()} ({self.outcome})"


class RecordBook:
    """Keeps the top scores on disk, highest first.

    A missing or corrupt file is treated as an empty book rather than an error,
    so a fresh install or a hand-edited file never blocks the title screen.
    """

    def __init__(self, path: str, capacity: int = 8) -> None:
        self._path = path
        self._capacity = capacity
        self._entries: list[RecordEntry] = []
        self._Load()

    def _Load(self) -> None:
        if not os.path.exists(self._path):
            return

        try:
            with open(self._path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)

            self._entries = [RecordEntry.FromDict(item) for item in raw]
        except (OSError, json.JSONDecodeError, TypeError):
            self._entries = []

    def GetEntries(self) -> list[RecordEntry]:
        return list(self._entries)

    def QualifiesForRecord(self, score: int) -> bool:
        if len(self._entries) < self._capacity:
            return True

        return score > self._entries[-1].score

    def AddRecord(self, entry: RecordEntry) -> int:
        self._entries.append(entry)
        self._entries.sort(key=lambda item: item.score, reverse=True)
        self._entries = self._entries[: self._capacity]
        self._Save()
        return self._entries.index(entry) + 1

    def _Save(self) -> None:
        directory = os.path.dirname(self._path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        try:
            with open(self._path, "w", encoding="utf-8") as handle:
                json.dump([entry.ToDict() for entry in self._entries], handle, indent=2)
        except OSError:
            pass
