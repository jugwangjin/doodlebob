# DoodleBob Desktop Pet

## Cursor Cloud specific instructions

### Overview
DoodleBob is a Python (tkinter) desktop pet that runs as a transparent always-on-top overlay on Windows. On Linux/macOS it runs in `--windowed` mode for development/testing.

### Running
- `python main.py --windowed` for development (shows dark background window)
- `python main.py --generate` to regenerate placeholder sprites only
- `python main.py --sheet` to generate a sprite sheet PNG from current sprites
- `python main.py --split-sheet PATH` to split an improved sprite sheet back into individual PNGs
- `python main.py` for full overlay mode (Windows only — transparent click-through overlay)

### Dependencies
- `pip install -r requirements.txt` (Pillow, pystray; pywin32 auto-included on Windows only)
- `python3-tk` system package is required (not included in some minimal Python installs)

### Keyboard Controls (in-app)
- `C` — Force cursor steal (with lurking)
- `D` — Force screen doodle
- `S` — Stop current action (return to wandering)
- `B` — Toggle behaviors on/off (off = only wander)
- `Space` — Pause / Resume

### Key caveats
- The transparent overlay (`-transparentcolor`) only works on Windows. On Linux, use `--windowed`.
- System tray icon requires GTK on Linux — expect a warning if GTK is unavailable; the app still runs fine without it.
- Window closing and cursor hiding are no-ops on non-Windows platforms. The character still walks and animates.
- Sprites are auto-generated on first run. To force regeneration, delete `assets/sprites/` and run again.
- The sprite loading order is: animated GIF → numbered PNGs → sprite sheet fallback → auto-generated placeholder.
- Pencil particle effects are only visible in windowed mode.
- The ActionScheduler randomly picks between behaviors; timing is per-behavior (see `config.py`).

### Testing
- Run `python main.py --windowed` and verify the character appears and walks around.
- Press keyboard shortcuts to test each behavior: C for cursor steal (with lurking), S to stop.
- On Windows, verify overlay transparency, window closing, and cursor stealing behaviors.
- No automated test suite exists yet; testing is manual/visual.
