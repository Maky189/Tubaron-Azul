from __future__ import annotations

"""The single source of truth for the game's look: colours, fonts, layout, music.

The whole game is skinned in Cape Verde's colours — deep blue and clean white —
so every scene reads from here and never invents an ad-hoc colour.
"""

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540

# Cape Verde identity.
CV_BLUE = (0, 56, 147)
CV_BLUE_DEEP = (0, 38, 104)
CV_BLUE_BRIGHT = (38, 104, 220)
CV_WHITE = (244, 247, 252)
CV_RED = (207, 26, 46)
CV_YELLOW = (255, 205, 0)

# Neutral UI tones, all kept in the blue/white family.
WHITE = (244, 247, 252)
OFF_WHITE = (214, 224, 240)
GREY = (150, 166, 196)
DARK = (10, 22, 52)
PANEL = (12, 40, 92)
PANEL_LIGHT = (22, 64, 140)
INK = (6, 16, 38)

# Pitch tones.
GRASS_LIGHT = (62, 150, 70)
GRASS_DARK = (52, 134, 62)
LINE_WHITE = (236, 244, 250)

# Status colours (used sparingly, e.g. stamina).
GREEN = (86, 214, 122)
RED = (226, 54, 78)
GOLD = (255, 205, 0)

FONT_DISPLAY = "fonts/Anton-Regular.ttf"
FONT_BOLD = "fonts/BarlowCondensed-Bold.ttf"
FONT_SEMI = "fonts/BarlowCondensed-SemiBold.ttf"
FONT_BODY = "fonts/BarlowCondensed-Medium.ttf"

# Soundtrack: IShowSpeed's "World Cup (Champions)" over the opening cinematic,
# "We Are One" on every menu, and "LA MC Malcriado" during live matches.
MUSIC_OPENING = "audio/opening.ogg"
MUSIC_ANTHEM = "audio/anthem.ogg"
MUSIC_MATCH = "audio/match.ogg"

MUSIC_OPENING_VOLUME = 0.55
MUSIC_ANTHEM_VOLUME = 0.5
MUSIC_MATCH_VOLUME = 0.5
