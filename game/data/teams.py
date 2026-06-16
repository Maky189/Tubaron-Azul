from __future__ import annotations
from dataclasses import dataclass

"""Teams, kits and the World Cup road for Cabo Verde.

A match is always Cabo Verde (the player) against one rival nation. The rivals
form a ladder of rising difficulty — the same six-stage road the old RPG walked,
now played out on the pitch. Kit colours drive the per-team sprite recolouring;
the goalkeeper sprite keeps its own keeper colour.
"""

Color = tuple[int, int, int]


@dataclass(frozen=True)
class TeamDef:
    team_id: str
    name: str
    short: str
    shirt: Color
    shorts: Color
    keeper: Color
    ai_skill: float
    round_label: str


CAPE_VERDE = TeamDef(
    "capeverde", "Cabo Verde", "CPV",
    (34, 96, 210), (244, 247, 252), (255, 196, 0),
    0.62, "Os Tubarões Azuis",
)

_RIVALS = {
    "spain": TeamDef("spain", "Espanha", "ESP", (200, 32, 44), (24, 40, 110), (40, 200, 120), 0.34, "Estreia — Fase de Grupos"),
    "belgium": TeamDef("belgium", "Bélgica", "BEL", (150, 28, 40), (18, 18, 22), (220, 180, 40), 0.45, "Fase de Grupos"),
    "netherlands": TeamDef("netherlands", "Países Baixos", "NED", (236, 120, 24), (244, 247, 252), (40, 60, 160), 0.56, "Oitavos de Final"),
    "england": TeamDef("england", "Inglaterra", "ENG", (232, 236, 246), (24, 36, 96), (60, 200, 90), 0.66, "Quartos de Final"),
    "france": TeamDef("france", "França", "FRA", (18, 28, 92), (236, 240, 248), (200, 40, 60), 0.76, "Meias-Finais"),
    "brazil": TeamDef("brazil", "Brasil", "BRA", (246, 206, 32), (24, 64, 170), (60, 210, 110), 0.86, "A GRANDE FINAL"),
}

WORLD_CUP_PATH = ["spain", "belgium", "netherlands", "england", "france", "brazil"]


def GetCapeVerde() -> TeamDef:
    return CAPE_VERDE


def GetRival(team_id: str) -> TeamDef:
    if team_id not in _RIVALS:
        raise KeyError(f"unknown rival '{team_id}'")

    return _RIVALS[team_id]


def IsFinalStage(stage_index: int) -> bool:
    return stage_index == len(WORLD_CUP_PATH) - 1


def StageCount() -> int:
    return len(WORLD_CUP_PATH)


# Formation for a team attacking to the right, normalised to the pitch:
# x in [0,1] from own goal line to the opponent's, y in [0,1] top to bottom.
# Goalkeeper first, then defenders, midfield, attack. Six players a side.
FORMATION = [
    ("GK", 0.05, 0.50),
    ("DEF", 0.26, 0.27),
    ("DEF", 0.26, 0.73),
    ("MID", 0.48, 0.50),
    ("ATT", 0.70, 0.30),
    ("ATT", 0.70, 0.70),
]


def SquadSize() -> int:
    return len(FORMATION)
