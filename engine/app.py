from __future__ import annotations
import asyncio
import os
from dataclasses import dataclass
import pygame
from engine.resources.asset_manager import AssetManager
from engine.input.input_manager import InputManager
from engine.audio.audio_manager import AudioManager
from engine.scene.scene_stack import SceneStack
from engine.scene.scene import Scene
from engine.input.touch_overlay import TouchOverlay


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
        self._InitMixer()
        pygame.init()
        self._config = config
        self._screen = pygame.display.set_mode((config.width, config.height))
        pygame.display.set_caption(config.title)
        self._clock = pygame.time.Clock()
        self._running = False
        self._assets = AssetManager(config.asset_root)
        self._input = InputManager()
        self._audio = AudioManager(self._assets)
        self._scenes = SceneStack()
        self._touch = TouchOverlay(config.width, config.height)

    def _InitMixer(self) -> None:
        # Must run before pygame.init(): that call brings the mixer up and opens
        # the output device, and once it is initialised these settings (and the
        # PulseAudio env var below) are read too late to take effect.
        #
        # On WSL, sound leaves the Linux side through a PulseAudio/PipeWire
        # bridge to the Windows host. That client connection has its own buffer,
        # separate from pygame's mixer buffer, and its default is small enough
        # that it underruns on the bridge -- not at once, but as timing slowly
        # slips, which is why the music plays for a while and then crackles and
        # cuts. PULSE_LATENCY_MSEC tells libpulse to hold a larger cushion, which
        # is the standard cure for WSL audio dropout. setdefault keeps it
        # overridable from the environment for tuning. It is harmless off WSL
        # (libpulse only honours it when the PulseAudio backend is in use).
        os.environ.setdefault("PULSE_LATENCY_MSEC", "90")

        # The audible fault is the music stuttering/skipping after a minute or so
        # while the game keeps animating perfectly smoothly. Audio that breaks up
        # on its own, independent of the visuals, is the output device buffer
        # underrunning: the SDL audio callback now and then arrives late and the
        # device has nothing fresh to play, so it repeats or skips. The size of
        # that buffer is the only thing that governs it -- a bigger buffer is
        # filled in fewer, larger callbacks, so a late one still has a long
        # cushion of already-queued audio to coast on. 4096 frames (~85 ms) was
        # not enough to cover the late spikes; 16384 (~340 ms) is. The only cost
        # is start-up latency on a sound, which is irrelevant for looping music
        # and there are no latency-sensitive effects.
        #
        # 48000 Hz matches the output device so nothing resamples on the way out.
        # pygame.mixer is not always present at this point: the pygbag/web build
        # does not expose it (nor even pygame.error) before pygame.init(), so the
        # original `except pygame.error` raised its own AttributeError and killed
        # the app before the window was created. This tuning is a desktop/WSL
        # audio fix, so skip it cleanly when pre_init is unavailable.
        pre_init = getattr(getattr(pygame, "mixer", None), "pre_init", None)
        if pre_init is None:
            return

        try:
            pre_init(frequency=48000, size=-16, channels=2, buffer=16384)
        except Exception:
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
        """Synchronous entry point for desktop and tests.

        Wraps the async loop so native runs and the test suite call exactly as
        before; on the web the pygbag entry awaits RunAsync directly.
        """
        asyncio.run(self.RunAsync())

    async def RunAsync(self) -> None:
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

            # Hand control back to the browser's event loop so it can paint the
            # canvas and pump input. Harmless on desktop (a zero-delay yield);
            # required under Emscripten/pygbag, which has no background thread to
            # drive the frame and would otherwise hang the page.
            await asyncio.sleep(0)

        pygame.quit()

    def _PumpEvents(self) -> None:
        self._input.BeginFrame()
        active = self._scenes.GetActive()

        if active is not None:
            self._touch.SetScheme(active.TouchControls())

        for event in pygame.event.get():
            self._UpdateTouchVisibility(event)
            self._touch.HandleEvent(event)
            self._input.HandleEvent(event)

            if active is not None:
                active.HandleEvent(event)

        if self._input.IsQuitRequested():
            self._running = False

    def _UpdateTouchVisibility(self, event: pygame.event.Event) -> None:
        # Auto-detect the input method: first finger reveals the on-screen pad,
        # a real key press hides it again. Synthetic keys posted by the overlay
        # itself carry `synthetic` and must not count as the player reaching for
        # a keyboard.
        if event.type == pygame.FINGERDOWN:
            self._touch.SetVisible(True)
        elif event.type == pygame.KEYDOWN and not getattr(event, "synthetic", False):
            self._touch.SetVisible(False)

    def _UpdateActive(self, dt: float) -> None:
        active = self._scenes.GetActive()

        if active is not None:
            active.Update(dt)

    def _RenderVisible(self) -> None:
        self._screen.fill((0, 0, 0))

        for scene in self._scenes.IterVisible():
            scene.Render(self._screen)

        self._touch.Render(self._screen)
