from __future__ import annotations
from game.data.teams import WORLD_CUP_PATH, StageCount

"""The persistent run: Cabo Verde's progress along the World Cup road.

A run advances one stage per win. The state serialises itself so a tournament
can be saved and continued, and exposes the numbers the high-score book reads.
"""


class GameState:
    def __init__(self) -> None:
        self.coach = "Treinador"
        self.stage_index = 0
        self.wins = 0
        self.goals_for = 0
        self.goals_against = 0
        self.finished = False
        self.champion = False

    def CurrentOpponentId(self) -> str:
        if self.stage_index >= len(WORLD_CUP_PATH):
            return WORLD_CUP_PATH[-1]

        return WORLD_CUP_PATH[self.stage_index]

    def IsFinalStage(self) -> bool:
        return self.stage_index == StageCount() - 1

    def RecordMatch(self, goals_for: int, goals_against: int, won: bool) -> None:
        self.goals_for += goals_for
        self.goals_against += goals_against

        if won:
            self.wins += 1
            self.stage_index += 1

            if self.stage_index >= StageCount():
                self.finished = True
                self.champion = True
        else:
            self.finished = True

    def Score(self) -> int:
        return self.wins * 200 + self.goals_for * 25 - self.goals_against * 10

    def StageReached(self) -> int:
        return self.stage_index + 1

    def CaptureSnapshot(self) -> dict:
        return {
            "coach": self.coach,
            "stage_index": self.stage_index,
            "wins": self.wins,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "finished": self.finished,
            "champion": self.champion,
        }

    def ApplySnapshot(self, data: dict) -> None:
        self.coach = data.get("coach", "Treinador")
        self.stage_index = int(data.get("stage_index", 0))
        self.wins = int(data.get("wins", 0))
        self.goals_for = int(data.get("goals_for", 0))
        self.goals_against = int(data.get("goals_against", 0))
        self.finished = bool(data.get("finished", False))
        self.champion = bool(data.get("champion", False))
