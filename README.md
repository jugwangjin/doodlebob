# DoodleBob 🖊️

A Python (tkinter) desktop pet that runs as a transparent always-on-top overlay on Windows. On Linux/macOS it runs in `--windowed` mode for development/testing.

DoodleBob walks around your screen, randomly closes windows, and steals your cursor with his magic pencil eraser.

## Features

1. **Random Window Closing** — DoodleBob walks to a random window's X button and closes it. Happens at random intervals.

2. **Cursor Stealing** — DoodleBob periodically chases your cursor, "erases" it with the magic pencil's eraser end, hides it briefly, then "redraws" it at a random screen position. While the cursor is hidden, it truly disappears.

3. **Autonomous Walking & Lurking** — DoodleBob wanders around the screen or "lurks" near your cursor before attacking.

4. **Screen Doodling** — DoodleBob can draw random shapes/doodles on your screen.

## Requirements

- **Python 3.10+**
- **Windows 10/11** (for full functionality — overlay, window closing, cursor hiding)
- `pip install -r requirements.txt` (Pillow, pystray; pywin32 auto-included on Windows only)
- `python3-tk` system package is required

## Keyboard Controls (in-app)

- `C` — Force cursor steal (with lurking)
- `W` — Force window close (walk to random window X button)
- `D` — Force screen doodle
- `S` — Stop current action (return to wandering)
- `B` — Toggle behaviors on/off (off = only wander)
- `Space` — Pause / Resume
- `Escape` or `Q` — Close app (quit)

## Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Generate placeholder sprites (first time)
python main.py --generate

# Run in full-screen overlay mode (Windows)
python main.py

# Run in windowed mode (for testing / development)
python main.py --windowed

# Generate a sprite sheet PNG from current sprites
python main.py --sheet

# Split an improved sprite sheet back into individual PNGs
python main.py --split-sheet path/to/sheet.png
```

## Custom Sprites

The sprite loading order is: **animated GIF → numbered PNGs → sprite sheet fallback → auto-generated placeholder**.

### Sprite sets

| Name | Purpose | Frames |
|------|---------|--------|
| `idle` | Standing still / bobbing | 2 |
| `walk` | Normal walking | 4 |
| `chase` | Chasing the cursor (angry) | 4 |
| `approach` | Walking toward window X button | 4 |
| `erase` | Erasing cursor with pencil eraser | 4 |
| `draw` | Redrawing cursor with pencil tip | 4 |
| `lurk` | Lurking near cursor | 2 |
| `doodle` | Drawing random shapes | 4 |
| `pencil_press` | Pencil contact animation | 4 |

Base sprite size: **64×80 pixels**.

## Configuration

Edit `config.py` to tweak behavior timing, movement speed, animation FPS, etc.

## Key Caveats

- The transparent overlay (`-transparentcolor`) only works on Windows. On Linux, use `--windowed`.
- System tray icon requires GTK on Linux.
- Window closing and cursor hiding are no-ops on non-Windows platforms.
- Pencil particle effects are only visible in windowed mode.

## License

MIT
