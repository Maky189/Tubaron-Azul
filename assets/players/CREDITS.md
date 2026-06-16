# Player Sprite Credits

The three base poses (`outfield_idle`, `outfield_kick`, `keeper`) are derived
from author-provided pixel-art renders of a Cape Verde player and goalkeeper
(`player.png`, `player_kick.png`, `vozinha.png` in the repository root).

`tools/process_players.py` turns each raw render into a game-ready sprite:
keying out the white background with an inward flood-fill (so the white socks,
laces and ball survive), trimming to the silhouette, and saving at a workable
size. Every other nation is produced at load time by recolouring the kit — see
`game/visual/soccer_art.py`.

These are personal-project assets; rights remain with the author. Replace before
any public or commercial distribution.
