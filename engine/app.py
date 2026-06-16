from __future__ import annotations
from dataclasses import dataclass
import pygame
from engine.resources.asset_manager import AssetManager
from engine.input.input_manager import InputManager
from engine.audio.audio_manager import AudioManager, MUSIC_END_EVENT
from engine.scene.scene_stack import SceneStack
from engine.scene.scene import Scene


@dataclass(frozen=True)
class AppConfig:
    title: str
    width: int
    height: int
    asset_root: str
    target_fps: int = 60


class Application:
    """Owns the window, the main loop and the shared subsystems.

    Scenes reach the asset manager, input and audio through this object, so the
    game layer never touches pygame's global state directly.
    """

    def __init__(self, config: AppConfig) -> None:
        pygame.init()
        self._InitMixer()
        self._config = config
        self._screen = pygame.display.set_mode((config.width, config.height))
        pygame.display.set_caption(config.title)
        self._clock = pygame.time.Clock()
        self._running = False
        self._assets = AssetManager(config.asset_root)
        self._input = InputManager()
        self._audio = AudioManager(self._assets)
        self._scenes = SceneStack()

    def _InitMixer(self) -> None:
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

    def GetAssets(self) -> AssetManager:
        return self._assets

    def GetInput(self) -> InputManager:
        return self._input

    def GetAudio(self) -> AudioManager:
        return self._audio

    def GetScenes(self) -> SceneStack:
        return self._scenes

    def GetScreenSize(self) -> tuple[int, int]:
        return (self._config.width, self._config.height)

    def StartWith(self, scene: Scene) -> None:
        self._scenes.RequestClearTo(scene)

    def RequestQuit(self) -> None:
        self._running = False

    def Run(self) -> None:
        self._running = True
        self._scenes.ApplyPending()

        while self._running:
            dt = self._clock.tick(self._config.target_fps) / 1000.0
            self._PumpEvents()
            self._UpdateActive(dt)
            self._RenderVisible()
            pygame.display.flip()
            self._scenes.ApplyPending()

            if self._scenes.IsEmpty():
                self._running = False

        pygame.quit()

    def _PumpEvents(self) -> None:
        self._input.BeginFrame()
        active = self._scenes.GetActive()

        for event in pygame.event.get():
            self._input.HandleEvent(event)

            if event.type == MUSIC_END_EVENT:
                self._audio.HandleMusicEndEvent()

            if active is not None:
                active.HandleEvent(event)

        if self._input.IsQuitRequested():
            self._running = False

    def _UpdateActive(self, dt: float) -> None:
        active = self._scenes.GetActive()

        if active is not None:
            active.Update(dt)

    def _RenderVisible(self) -> None:
        self._screen.fill((0, 0, 0))

        for scene in self._scenes.IterVisible():
            scene.Render(self._screen)
