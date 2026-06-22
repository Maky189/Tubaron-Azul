from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path

"""Re-encode the music tracks to a small, web-friendly size.

The three .ogg tracks dominate the web download (~12.5 MB of a ~15 MB bundle).
They are full ~5-minute songs at 128 kbps stereo, so size is driven mostly by
length: bitrate compression alone has a floor. Two knobs:

  --bitrate N    Vorbis bitrate in kbps (default 96).
  --seconds S    Trim each track to S seconds with a short fade-out, then the
                 game loops it. This is the big lever -- a 75 s loop is ~4x
                 smaller than the full song and barely noticeable in play.

Ogg Vorbis is kept (pygbag's mixer decodes it reliably; MP3/Opus support in the
WASM build is not guaranteed). Originals stay recoverable from git history.

Run once as a dev step (not part of the build); commit the smaller files:

    python tools/compress_audio.py --bitrate 96
    python tools/compress_audio.py --bitrate 96 --seconds 75
"""

TRACKS = ["opening", "anthem", "match"]
AUDIO_DIR = Path("assets/audio")


def find_ffmpeg() -> str | None:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    # winget installs under WinGet/Packages or Links; probe common spots.
    home = Path.home()
    for pat in [
        home / "AppData/Local/Microsoft/WinGet/Links/ffmpeg.exe",
        home / "AppData/Local/Microsoft/WinGet/Packages",
    ]:
        if pat.is_file():
            return str(pat)
        if pat.is_dir():
            hits = list(pat.glob("**/ffmpeg.exe"))
            if hits:
                return str(hits[0])
    return None


def transcode(ffmpeg: str, src: Path, dst: Path, bitrate_k: int, seconds: float | None) -> None:
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src)]
    if seconds:
        # The tracks loop (loops=-1), so a long fade would dip to silence every
        # cycle. A short 0.4 s out-fade just kills the end-of-clip click while
        # staying effectively continuous.
        fade = max(0.0, seconds - 0.4)
        cmd += ["-t", str(seconds), "-af", f"afade=t=out:st={fade}:d=0.4"]
    cmd += ["-c:a", "libvorbis", "-b:a", f"{bitrate_k}k", str(dst)]
    subprocess.run(cmd, check=True)


def main(argv: list[str]) -> int:
    bitrate = 96
    seconds: float | None = None
    if "--bitrate" in argv:
        bitrate = int(argv[argv.index("--bitrate") + 1])
    if "--seconds" in argv:
        seconds = float(argv[argv.index("--seconds") + 1])

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("ffmpeg not found. Install it (winget install Gyan.FFmpeg) and retry.", file=sys.stderr)
        return 1
    print(f"using ffmpeg: {ffmpeg}")
    print(f"bitrate={bitrate}k  trim={seconds or 'none'}")

    total_before = total_after = 0
    for name in TRACKS:
        src = AUDIO_DIR / f"{name}.ogg"
        if not src.exists():
            print(f"  skip {name}: not found")
            continue
        tmp = AUDIO_DIR / f"{name}.compressed.ogg"
        before = src.stat().st_size
        transcode(ffmpeg, src, tmp, bitrate, seconds)
        after = tmp.stat().st_size
        tmp.replace(src)
        total_before += before
        total_after += after
        print(f"  {name:8} {before/1e6:5.2f} MB -> {after/1e6:5.2f} MB")

    if total_before:
        print(f"  TOTAL    {total_before/1e6:5.2f} MB -> {total_after/1e6:5.2f} MB "
              f"({100 * total_after / total_before:.0f}% of original)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
