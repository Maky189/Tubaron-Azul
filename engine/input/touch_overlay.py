from __future__ import annotations
from dataclasses import dataclass, field
import pygame
from engine.mathx.vec2 import Vec2

"""On-screen touch controls for the web build.

The whole game already routes input through two channels: most scenes read
KEYDOWN/KEYUP from `HandleEvent`, while the live match polls `InputManager`.
Both are fed from the single event loop in `Application._PumpEvents`. So rather
than teach every scene about touch, an on-screen button simply *posts the same
pygame key events* a keyboard would. A finger press posts KEYDOWN, a lift posts
KEYUP, and from there nothing downstream can tell touch from a real key.

Movement during a match is the exception: the gameplay scheme shows a floating
**analog stick** instead of a D-pad, and exposes a continuous direction vector
through `GetMoveVector()` that `MatchScene` reads directly. Menus, which only
need discrete up/down/left/right, keep the digital D-pad and the key-posting
path. The overlay stays hidden until the first touch arrives (see Application),
so desktop browsers never show it.
"""

SCHEME_MENU = "menu"
SCHEME_GAMEPLAY = "gameplay"

_MOUSE_FINGER = "mouse"

# Analog stick geometry (reference height is 540; width flexes per device).
_STICK_BASE_R = 80     # outer ring radius
_STICK_KNOB_R = 42     # inner knob radius
_STICK_TRAVEL = 72     # max knob travel from the ring centre


def _IsTouchMouse(event: pygame.event.Event) -> bool:
    """True when a mouse event is just SDL's touch-to-mouse emulation.

    Touch devices emit both FINGER* and a mirrored MOUSE* event for the same
    contact; we handle the FINGER one and drop the emulated mouse twin so a
    single tap isn't counted twice.
    """
    return bool(getattr(event, "touch", False))


@dataclass(frozen=True)
class TouchButton:
    keys: tuple[int, ...]
    label: str
    rect: pygame.Rect
    arrow: str | None = None  # "up"/"down"/"left"/"right" for the D-pad, else None
    radius: int = 0           # >0 draws a circle, else a rounded rectangle


@dataclass
class _Layout:
    buttons: list[TouchButton]
    has_stick: bool = False
    base: pygame.Surface | None = field(default=None)


def _DPad(cx: int, cy: int, unit: int) -> list[TouchButton]:
    half = unit // 2
    return [
        TouchButton((pygame.K_UP,), "", pygame.Rect(cx - half, cy - unit - half, unit, unit), arrow="up"),
        TouchButton((pygame.K_DOWN,), "", pygame.Rect(cx - half, cy + half, unit, unit), arrow="down"),
        TouchButton((pygame.K_LEFT,), "", pygame.Rect(cx - unit - half, cy - half, unit, unit), arrow="left"),
        TouchButton((pygame.K_RIGHT,), "", pygame.Rect(cx + half, cy - half, unit, unit), arrow="right"),
    ]


def _BuildLayouts(width: int, height: int) -> dict[str, _Layout]:
    pad_cx, pad_cy, unit = 120, int(height * 0.70), 72

    # Gameplay: analog stick on the left (handled separately), actions on the
    # right. No D-pad buttons -- movement comes from GetMoveVector().
    gameplay = [
        _Circle(width - 120, int(height * 0.70), 46, (pygame.K_SPACE,), "CHUTE"),
        _Circle(width - 220, int(height * 0.80), 38, (pygame.K_z,), "PASSE"),
        _Circle(width - 220, int(height * 0.60), 38, (pygame.K_x,), "TROCA"),
        _Circle(width - 50, int(height * 0.56), 34, (pygame.K_LSHIFT,), "CORRE"),
        TouchButton((pygame.K_ESCAPE,), "II", pygame.Rect(width - 52, 14, 38, 34)),
    ]

    menu = _DPad(pad_cx, pad_cy, unit) + [
        _Circle(width - 120, int(height * 0.70), 46, (pygame.K_RETURN,), "OK"),
        TouchButton((pygame.K_ESCAPE,), "VOLTAR", pygame.Rect(width - 84, 14, 70, 34)),
    ]

    return {
        SCHEME_MENU: _Layout(menu),
        SCHEME_GAMEPLAY: _Layout(gameplay, has_stick=True),
    }


def _Circle(cx: int, cy: int, r: int, keys: tuple[int, ...], label: str) -> TouchButton:
    return TouchButton(keys, label, pygame.Rect(cx - r, cy - r, r * 2, r * 2), radius=r)


class TouchOverlay:
    """Maps touches onto on-screen buttons and an analog stick."""

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._layouts = _BuildLayouts(width, height)
        self._scheme = SCHEME_MENU
        self._font: pygame.font.Font | None = None
        # Which button each active finger is currently resting on.
        self._finger_button: dict[object, TouchButton] = {}
        self._visible = False

        # Floating analog stick (gameplay only).
        self._stick_home = (int(width * 0.13), int(height * 0.66))
        self._stick_finger: object | None = None
        self._stick_anchor: tuple[int, int] = self._stick_home
        self._stick_offset = Vec2(0.0, 0.0)  # pixels, clamped to _STICK_TRAVEL
        # Reused scratch surface for the stick, sized to its largest extent, so
        # drawing it never allocates a fresh (full-screen) surface each frame.
        self._stick_pad = _STICK_BASE_R + _STICK_TRAVEL + _STICK_KNOB_R + 4
        self._stick_scratch = pygame.Surface((self._stick_pad * 2, self._stick_pad * 2), pygame.SRCALPHA)

    def SetVisible(self, visible: bool) -> None:
        if self._visible and not visible:
            self._ReleaseAll()
        self._visible = visible

    def IsVisible(self) -> bool:
        return self._visible

    def SetScheme(self, scheme: str) -> None:
        if scheme == self._scheme:
            return
        # Drop any held buttons from the old scheme so a key can't get stuck
        # down across a scene change.
        self._ReleaseAll()
        self._scheme = scheme

    def GetMoveVector(self) -> Vec2:
        """Analog move direction from the stick, magnitude 0..1.

        Zero unless the gameplay stick is being held; MatchScene prefers this
        over the keyboard when it is non-zero. Screen axes (x right, y down)
        already match the match's input convention.
        """
        if not self._visible or self._scheme != SCHEME_GAMEPLAY:
            return Vec2(0.0, 0.0)
        return Vec2(self._stick_offset.x / _STICK_TRAVEL, self._stick_offset.y / _STICK_TRAVEL)

    # -- input -----------------------------------------------------------

    def HandleEvent(self, event: pygame.event.Event) -> None:
        if not self._visible:
            return

        if event.type == pygame.FINGERDOWN:
            self._Press(event.finger_id, self._FingerPoint(event))
        elif event.type == pygame.FINGERMOTION:
            self._Move(event.finger_id, self._FingerPoint(event))
        elif event.type == pygame.FINGERUP:
            self._Release(event.finger_id)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not _IsTouchMouse(event):
            self._Press(_MOUSE_FINGER, event.pos)
        elif event.type == pygame.MOUSEMOTION and event.buttons[0] and not _IsTouchMouse(event):
            self._Move(_MOUSE_FINGER, event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not _IsTouchMouse(event):
            self._Release(_MOUSE_FINGER)

    def _FingerPoint(self, event: pygame.event.Event) -> tuple[int, int]:
        return (int(event.x * self._width), int(event.y * self._height))

    def _InStickZone(self, point: tuple[int, int]) -> bool:
        # Left ~45% of the screen grabs the stick; the action buttons live on
        # the right, so the two never fight over the same finger.
        return self._HasStick() and point[0] < self._width * 0.45

    def _HasStick(self) -> bool:
        return self._layouts[self._scheme].has_stick

    def _Press(self, finger: object, point: tuple[int, int]) -> None:
        if self._stick_finger is None and self._InStickZone(point):
            self._stick_finger = finger
            self._stick_anchor = point
            self._stick_offset = Vec2(0.0, 0.0)
            return

        button = self._ButtonAt(point)
        if button is None:
            return
        self._finger_button[finger] = button
        self._PostKeys(button, down=True)

    def _Move(self, finger: object, point: tuple[int, int]) -> None:
        if finger == self._stick_finger:
            self._UpdateStick(point)
            return

        current = self._finger_button.get(finger)
        target = self._ButtonAt(point)
        if target is current:
            return
        # Sliding off a button releases it; sliding onto a new one presses it.
        if current is not None:
            self._PostKeys(current, down=False)
            del self._finger_button[finger]
        if target is not None:
            self._finger_button[finger] = target
            self._PostKeys(target, down=True)

    def _Release(self, finger: object) -> None:
        if finger == self._stick_finger:
            self._stick_finger = None
            self._stick_offset = Vec2(0.0, 0.0)
            return

        button = self._finger_button.pop(finger, None)
        if button is not None:
            self._PostKeys(button, down=False)

    def _UpdateStick(self, point: tuple[int, int]) -> None:
        raw = Vec2(point[0] - self._stick_anchor[0], point[1] - self._stick_anchor[1])
        length = raw.GetLength()
        if length > _STICK_TRAVEL:
            raw = raw.GetNormalized() * _STICK_TRAVEL
        self._stick_offset = raw

    def _ReleaseAll(self) -> None:
        for button in self._finger_button.values():
            self._PostKeys(button, down=False)
        self._finger_button.clear()
        self._stick_finger = None
        self._stick_offset = Vec2(0.0, 0.0)

    def _ButtonAt(self, point: tuple[int, int]) -> TouchButton | None:
        for button in self._layouts[self._scheme].buttons:
            if button.rect.collidepoint(point):
                return button
        return None

    def _PostKeys(self, button: TouchButton, *, down: bool) -> None:
        kind = pygame.KEYDOWN if down else pygame.KEYUP
        for key in button.keys:
            # `synthetic` lets Application tell these apart from real keyboard
            # input, so a touch-posted KEYDOWN doesn't get read as "the player
            # switched to the keyboard" and hide the overlay.
            pygame.event.post(pygame.event.Event(kind, key=key, mod=0, unicode="", scancode=0, synthetic=True))

    # -- rendering -------------------------------------------------------

    def Render(self, surface: pygame.Surface) -> None:
        if not self._visible:
            return

        layout = self._layouts[self._scheme]
        if layout.base is None:
            layout.base = self._RenderBase(layout)
        surface.blit(layout.base, (0, 0))

        for button in self._finger_button.values():
            self._DrawButton(surface, button, fill=(255, 255, 255, 95))

        if layout.has_stick:
            self._DrawStick(surface)

    def _RenderBase(self, layout: _Layout) -> pygame.Surface:
        if self._font is None:
            self._font = pygame.font.Font(None, 22)
        base = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        for button in layout.buttons:
            self._DrawButton(base, button, fill=(255, 255, 255, 38))
        return base

    def _DrawStick(self, surface: pygame.Surface) -> None:
        active = self._stick_finger is not None
        center = self._stick_anchor if active else self._stick_home

        ring_fill = (255, 255, 255, 30 if not active else 46)
        ring_line = (255, 255, 255, 110 if not active else 150)
        knob_fill = (255, 255, 255, 70 if not active else 120)
        knob_line = (255, 255, 255, 150 if not active else 210)

        # Draw into the reused scratch surface in local coordinates (its centre
        # is the stick centre), then blit it once at the stick position.
        pad = self._stick_pad
        local = (pad, pad)
        knob = (int(pad + self._stick_offset.x), int(pad + self._stick_offset.y))
        layer = self._stick_scratch
        layer.fill((0, 0, 0, 0))
        pygame.draw.circle(layer, ring_fill, local, _STICK_BASE_R)
        pygame.draw.circle(layer, ring_line, local, _STICK_BASE_R, 3)
        pygame.draw.circle(layer, knob_fill, knob, _STICK_KNOB_R)
        pygame.draw.circle(layer, knob_line, knob, _STICK_KNOB_R, 3)
        surface.blit(layer, (center[0] - pad, center[1] - pad))

    def _DrawButton(self, surface: pygame.Surface, button: TouchButton, *, fill: tuple[int, int, int, int]) -> None:
        outline = (255, 255, 255, 120)
        if button.radius > 0:
            center = button.rect.center
            pygame.draw.circle(surface, fill, center, button.radius)
            pygame.draw.circle(surface, outline, center, button.radius, 2)
        else:
            pygame.draw.rect(surface, fill, button.rect, border_radius=10)
            pygame.draw.rect(surface, outline, button.rect, 2, border_radius=10)

        if button.arrow is not None:
            self._DrawArrow(surface, button)
        elif button.label:
            self._DrawLabel(surface, button)

    def _DrawArrow(self, surface: pygame.Surface, button: TouchButton) -> None:
        cx, cy = button.rect.center
        s = button.rect.width // 5
        points = {
            "up": [(cx, cy - s), (cx - s, cy + s), (cx + s, cy + s)],
            "down": [(cx, cy + s), (cx - s, cy - s), (cx + s, cy - s)],
            "left": [(cx - s, cy), (cx + s, cy - s), (cx + s, cy + s)],
            "right": [(cx + s, cy), (cx - s, cy - s), (cx - s, cy + s)],
        }[button.arrow]
        pygame.draw.polygon(surface, (255, 255, 255, 200), points)

    def _DrawLabel(self, surface: pygame.Surface, button: TouchButton) -> None:
        if self._font is None:
            self._font = pygame.font.Font(None, 22)
        text = self._font.render(button.label, True, (255, 255, 255))
        text.set_alpha(210)
        surface.blit(text, text.get_rect(center=button.rect.center))
