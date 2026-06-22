from __future__ import annotations
import os
import pygame


class AssetError(Exception):
    pass


class AssetManager:
    """Loads and caches images, fonts and sounds from a single asset root.

    Every path passed in is relative to the root, so the rest of the engine
    never hard-codes an absolute location and the game stays portable.
    """

    def __init__(self, root: str) -> None:
        self._root = root
        self._images: dict[str, pygame.Surface] = {}
        self._fonts: dict[tuple[str, int], pygame.font.Font] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}

    def ResolvePath(self, relative: str) -> str:
        return os.path.join(self._root, relative)

    def LoadImage(self, relative: str) -> pygame.Surface:
        if relative in self._images:
            return self._images[relative]

        path = self.ResolvePath(relative)

        try:
            surface = pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError) as error:
            raise AssetError(f"failed to load image '{relative}': {error}") from error

        self._images[relative] = surface
        return surface

    def LoadFont(self, relative: str, size: int) -> pygame.font.Font:
        key = (relative, size)

        if key in self._fonts:
            return self._fonts[key]

        path = self.ResolvePath(relative)

        try:
            font = pygame.font.Font(path, size)
        except (pygame.error, FileNotFoundError) as error:
            raise AssetError(f"failed to load font '{relative}': {error}") from error

        self._fonts[key] = font
        return font

    def LoadSound(self, relative: str) -> pygame.mixer.Sound | None:
        if relative in self._sounds:
            return self._sounds[relative]

        mixer = getattr(pygame, "mixer", None)
        if mixer is None or not mixer.get_init():
            return None

        path = self.ResolvePath(relative)

        try:
            sound = pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError):
            return None

        self._sounds[relative] = sound
        return sound

    def HasImage(self, relative: str) -> bool:
        return os.path.exists(self.ResolvePath(relative))
