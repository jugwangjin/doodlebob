# DoodleBob 🖊️

A Desktop Goose-inspired desktop pet featuring **DoodleBob** from SpongeBob SquarePants.
DoodleBob walks around your screen, randomly closes windows, and steals your cursor with his magic pencil eraser.

![DoodleBob Concept](https://upload.wikimedia.org/wikipedia/en/f/f7/DoodleBob.png)

## Features

1. **Random Window Closing** — DoodleBob walks to a random window's X button and closes it. Happens at random intervals (30–90 seconds apart, never predictable).

2. **Cursor Stealing** — DoodleBob periodically chases your cursor, "erases" it with the magic pencil's eraser end, hides it briefly, then "redraws" it at a random screen position. While the cursor is hidden, it truly disappears.

3. **Autonomous Walking** — DoodleBob wanders around the screen, bouncing off edges, occasionally pausing to idle.

## Requirements

- **Python 3.10+**
- **Windows 10/11** (for full functionality — overlay, window closing, cursor hiding)
- Linux/macOS supported in windowed/testing mode

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate placeholder sprites (first time)
python main.py --generate

# Run in full-screen overlay mode (Windows)
python main.py

# Run in windowed mode (for testing / development)
python main.py --windowed
```

## Building a Standalone .exe (Windows)

```bash
pip install pyinstaller
build.bat
# Find DoodleBob.exe in dist/
```

## Custom Sprites

Placeholder sprites are auto-generated on first run in `assets/sprites/`.
Replace them with your own pixel art (Aseprite, Piskel, etc.):

### Supported formats

| Format | Example |
|--------|---------|
| Animated GIF | `walk.gif` — each GIF frame = one animation frame |
| Numbered PNGs | `walk_0.png`, `walk_1.png`, `walk_2.png`, ... |

### Sprite sets

| Name | Purpose | Frames |
|------|---------|--------|
| `idle` | Standing still / bobbing | 2 |
| `walk` | Normal walking | 4 |
| `chase` | Chasing the cursor (angry) | 4 |
| `approach` | Walking toward window X button | 4 |
| `erase` | Erasing cursor with pencil eraser | 4 |
| `draw` | Redrawing cursor with pencil tip | 4 |
| `cursor.png` | Fake cursor sprite | 1 |

Base sprite size: **64×80 pixels** (scaled 2× for display = 128×160).
Use `NEAREST` neighbor scaling for crisp pixel art.

## Configuration

Edit `config.py` to tweak behavior timing, movement speed, animation FPS, etc.

Key settings:
- `WINDOW_CLOSE_MIN_DELAY_S` / `MAX` — Window close interval range (seconds)
- `CURSOR_STEAL_MIN_DELAY_S` / `MAX` — Cursor steal interval range (seconds)
- `WANDER_SPEED` — How fast DoodleBob walks
- `CURSOR_CHASE_SPEED` — How fast DoodleBob chases the cursor
- `SPRITE_SCALE` — Display scale multiplier

## Architecture

```
main.py           Entry point (CLI argument parsing)
app.py            Application class (tkinter overlay, main loop, tray icon)
character.py      DoodleBob state machine, movement, animation, rendering
behaviors.py      WindowCloseBehavior, CursorStealBehavior
win_api.py        Windows API wrappers (cursor, window management) + Linux stubs
sprite_gen.py     Placeholder sprite generator (PIL-based)
config.py         All tunable constants
build.bat         PyInstaller build script (Windows)
assets/sprites/   Sprite files (auto-generated or user-provided)
```

## System Tray

When `pystray` is available, DoodleBob adds a system tray icon with:
- **Pause / Resume** — Temporarily freeze DoodleBob
- **Quit** — Exit gracefully

## License

MIT
