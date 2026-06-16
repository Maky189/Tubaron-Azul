from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from engine.app import Application, AppConfig
from engine.mathx.vec2 import Vec2
from game.scenes.services import GameContext
from game.scenes.cinematic_scene import CinematicScene
from game.persistence.save_manager import SaveManager
from game.persistence.records import RecordBook, RecordEntry
from game.domain.game_state import GameState
from game.data.teams import GetCapeVerde, GetRival, WORLD_CUP_PATH, SquadSize
from game.match import pitch
from game.match.match import Match, MatchInput

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_ROOT = os.path.join(PROJECT_ROOT, "assets")


def CheckSimulation() -> None:
    match = Match(GetCapeVerde(), GetRival("spain"), duration=30.0)
    assert len(match.players) == SquadSize() * 2

    guard = 0
    while not match.IsOver() and guard < 60 * 200:
        guard += 1
        human = MatchInput.Idle()
        active = match.controlled

        if active is not None:
            human.move = (match.ball.pos - active.pos).GetNormalized()
            if match.ball.owner is active:
                human.shoot = True

        match.Update(1.0 / 60.0, human)

        for player in match.players:
            assert 0 <= player.pos.x <= pitch.WIDTH
            assert 0 <= player.pos.y <= pitch.HEIGHT

    assert match.IsOver()
    print("  match reached full time, score =", match.score, "minute =", match.DisplayMinute())


def CheckBalance() -> None:
    # An engaged attacker should be able to score against the easiest side.
    match = Match(GetCapeVerde(), GetRival("spain"), duration=90.0)
    guard = 0
    while not match.IsOver() and guard < 60 * 400:
        guard += 1
        human = MatchInput.Idle()
        active = match.controlled

        if active is not None:
            goal_x = pitch.WIDTH
            if abs(active.pos.x - goal_x) < 300 and match.ball.owner is active:
                human.move = (Vec2(goal_x, 500.0) - active.pos).GetNormalized()
                human.shoot = True
            else:
                human.move = (match.ball.pos - active.pos).GetNormalized()
                human.sprint = True

        match.Update(1.0 / 60.0, human)

    assert match.score[0] > 0, "an active attacker scored nothing against Spain"
    print("  attacker scored, final =", match.score)


def CheckPersistence() -> None:
    save_path = os.path.join(PROJECT_ROOT, "saves", "_test_save.json")
    manager = SaveManager(save_path)
    state = GameState()
    state.RecordMatch(3, 1, True)
    state.RecordMatch(2, 0, True)
    manager.Save(state)
    loaded = manager.Load()
    assert loaded.stage_index == 2
    assert loaded.wins == 2
    assert loaded.goals_for == 5
    manager.Delete()

    records = RecordBook(os.path.join(PROJECT_ROOT, "saves", "_test_records.json"))
    assert records.QualifiesForRecord(loaded.Score())
    rank = records.AddRecord(RecordEntry("TST", loaded.Score(), loaded.StageReached(), "campeão"))
    assert rank >= 1
    os.remove(os.path.join(PROJECT_ROOT, "saves", "_test_records.json"))
    print("  persistence roundtrip ok, stage =", loaded.stage_index, "score =", loaded.Score())


def _MakeKeyEvent(key: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode="")


def DriveScenes() -> None:
    config = AppConfig("Test", 960, 540, ASSET_ROOT, 60)
    app = Application(config)
    records = RecordBook(os.path.join(PROJECT_ROOT, "saves", "_test_records2.json"))
    manager = SaveManager(os.path.join(PROJECT_ROOT, "saves", "_test_run.json"))
    ctx = GameContext(app, manager, records)
    app.StartWith(CinematicScene(ctx))
    scenes = app.GetScenes()
    scenes.ApplyPending()
    surface = pygame.Surface((960, 540))
    held = app.GetInput()

    assert type(scenes.GetActive()).__name__ == "CinematicScene"
    _Step(scenes, held, surface, [])
    _Step(scenes, held, surface, [_MakeKeyEvent(pygame.K_SPACE)])
    scenes.ApplyPending()
    assert type(scenes.GetActive()).__name__ == "TitleScene", "cinematic did not hand off to title"
    print("  cinematic skipped to title")

    _Step(scenes, held, surface, [_MakeKeyEvent(pygame.K_RETURN)])
    scenes.ApplyPending()
    assert type(scenes.GetActive()).__name__ == "TournamentScene", "new game did not open the road"
    print("  new tournament opened")

    _Step(scenes, held, surface, [_MakeKeyEvent(pygame.K_RETURN)])
    scenes.ApplyPending()
    match_scene = scenes.GetActive()
    assert type(match_scene).__name__ == "MatchScene", "did not kick off"

    # Pause overlay open/close.
    _Step(scenes, held, surface, [_MakeKeyEvent(pygame.K_ESCAPE)])
    scenes.ApplyPending()
    assert type(scenes.GetActive()).__name__ == "PauseScene"
    _Step(scenes, held, surface, [_MakeKeyEvent(pygame.K_ESCAPE)])
    scenes.ApplyPending()
    assert type(scenes.GetActive()).__name__ == "MatchScene"
    print("  pause overlay open/close ok")

    # Force full time and roll into the result.
    match_scene.match.state = "playing"
    match_scene.match.elapsed = match_scene.match.duration
    _Step(scenes, held, surface, [])
    _Step(scenes, held, surface, [])
    scenes.ApplyPending()
    assert type(scenes.GetActive()).__name__ == "ResultsScene", "match did not resolve into a result"
    print("  match resolved into a result")

    # Continue from the result back to the road or end screen.
    _Step(scenes, held, surface, [_MakeKeyEvent(pygame.K_RETURN)])
    scenes.ApplyPending()
    assert type(scenes.GetActive()).__name__ in ("TournamentScene", "TournamentEndScene")
    print("  result advanced the run:", type(scenes.GetActive()).__name__)

    manager.Delete()
    if os.path.exists(os.path.join(PROJECT_ROOT, "saves", "_test_records2.json")):
        os.remove(os.path.join(PROJECT_ROOT, "saves", "_test_records2.json"))
    pygame.quit()


def _Step(scenes, held, surface, events) -> None:
    held.BeginFrame()

    for event in events:
        held.HandleEvent(event)
        active = scenes.GetActive()

        if active is not None:
            active.HandleEvent(event)

    active = scenes.GetActive()

    if active is not None:
        active.Update(1.0 / 60.0)

    for scene in scenes.IterVisible():
        scene.Render(surface)


if __name__ == "__main__":
    pygame.init()
    print("checking simulation...")
    CheckSimulation()
    print("checking balance...")
    CheckBalance()
    print("checking persistence...")
    CheckPersistence()
    print("driving scenes...")
    DriveScenes()
    print("ALL SMOKE TESTS PASSED")
