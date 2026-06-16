from __future__ import annotations
import pygame
from engine.resources.asset_manager import AssetManager

MUSIC_END_EVENT = pygame.USEREVENT + 7


class AudioManager:
    """Thin wrapper over the mixer that fails quietly when no audio device exists.

    Headless machines and CI have no output device, so every call degrades to a
    no-op rather than crashing the game. The manager remembers the intended
    track, so if playback ever stops unexpectedly it can be brought back: a scene
    re-requesting its own track restarts it when it is no longer playing, and an
    end-of-track event restarts looping music that was cut short.
    """

    def __init__(self, assets: AssetManager) -> None:
        self._assets = assets
        self._enabled = pygame.mixer.get_init() is not None
        self._track: str | None = None
        self._volume = 0.5
        self._loop = True

        if self._enabled:
            pygame.mixer.music.set_endevent(MUSIC_END_EVENT)

    def IsEnabled(self) -> bool:
        return self._enabled

    def PlaySound(self, relative: str, volume: float = 1.0) -> None:
        if not self._enabled:
            return

        sound = self._assets.LoadSound(relative)

        if sound is None:
            return

        sound.set_volume(volume)
        sound.play()

    def PlayMusic(self, relative: str, volume: float = 0.5, loop: bool = True) -> None:
        if not self._enabled:
            return

        if relative == self._track and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(volume)
            self._volume = volume
            return

        self._track = relative
        self._volume = volume
        self._loop = loop
        self._StartTrack()

    def _StartTrack(self) -> None:
        if not self._enabled or self._track is None:
            return

        path = self._assets.ResolvePath(self._track)

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._volume)
        except pygame.error:
            self._track = None
            return

        loops = 0
        if self._loop:
            loops = -1

        try:
            pygame.mixer.music.play(loops)
        except pygame.error:
            self._track = None

    def HandleMusicEndEvent(self) -> None:
        if not self._enabled or self._track is None or not self._loop:
            return

        if pygame.mixer.music.get_busy():
            return

        self._StartTrack()

    def StopMusic(self) -> None:
        if not self._enabled:
            return

        pygame.mixer.music.stop()
        self._track = None
