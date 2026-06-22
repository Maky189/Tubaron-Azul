from __future__ import annotations

"""Tiny bridge to the browser when running under pygbag, inert on desktop.

pygbag augments the stdlib `platform` module with live browser handles
(`platform.window`, `platform.document`, ...). On native CPython those
attributes simply do not exist, so every helper here degrades to a safe
"not on the web" answer and the desktop build behaves exactly as before.
"""


def IsWeb() -> bool:
    try:
        import platform
        return hasattr(platform, "window")
    except Exception:
        return False


def DeviceViewport() -> tuple[int, int] | None:
    """The browser viewport in CSS pixels, or None when not on the web."""
    try:
        import platform
        w = int(platform.window.innerWidth)
        h = int(platform.window.innerHeight)
        if w > 0 and h > 0:
            return w, h
    except Exception:
        return None
    return None


def LandscapeLogicalSize(base_width: int, base_height: int) -> tuple[int, int]:
    """Pick the game's internal resolution for the current device.

    Height is pinned to the reference (`base_height`) so fonts, sprites and the
    touch buttons keep their tuned sizes; width is stretched to the device's
    *landscape* aspect ratio (long side over short side) so the framebuffer
    matches the screen and scales up with no letterbox and no distortion. The
    aspect is taken orientation-independently, so we still get the right
    landscape shape even when the page first loads in portrait, before the
    fullscreen/orientation lock kicks in. Off the web, the base size is kept.
    """
    viewport = DeviceViewport()
    if viewport is None:
        return base_width, base_height

    long_side = max(viewport)
    short_side = min(viewport)
    if short_side <= 0:
        return base_width, base_height

    aspect = long_side / short_side
    # Clamp to a sane range so a freak viewport can't make a 4000px-wide
    # surface or a narrower-than-base one.
    aspect = max(base_width / base_height, min(aspect, 2.4))
    width = int(round(base_height * aspect))
    return width, base_height
