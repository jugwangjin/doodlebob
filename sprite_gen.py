"""Generate placeholder DoodleBob sprites using PIL.

These are meant to be replaced with proper pixel-art sprites created in
Aseprite or similar tools.  The generated sprites are intentionally rough
and "sketchy" to match DoodleBob's hand-drawn aesthetic.
"""

import os
import math
import random as _rng
from PIL import Image, ImageDraw

from config import SPRITES_DIR, CHAR_BASE_W, CHAR_BASE_H

# Deterministic seed so regeneration produces identical sprites
_rng.seed(42)

# Palette
BLACK = (0, 0, 0, 255)
WHITE = (245, 240, 230, 255)
CREAM = (250, 245, 235, 255)
PUPIL = (10, 10, 10, 255)
MOUTH = (30, 30, 30, 255)
PENCIL_YELLOW = (240, 200, 50, 255)
PENCIL_TIP = (60, 60, 60, 255)
PENCIL_METAL = (180, 180, 180, 255)
PENCIL_ERASER = (230, 130, 130, 255)
TRANSPARENT = (0, 0, 0, 0)


def _sketchy_rect(draw: ImageDraw.Draw, bbox, outline=BLACK, fill=None, width=2):
    """Draw a slightly wobbly rectangle for a hand-drawn look."""
    x0, y0, x1, y1 = bbox
    if fill:
        draw.rectangle(bbox, fill=fill)
    pts = [
        (x0 + _rng.randint(-1, 1), y0 + _rng.randint(-1, 1)),
        (x1 + _rng.randint(-1, 1), y0 + _rng.randint(-1, 1)),
        (x1 + _rng.randint(-1, 1), y1 + _rng.randint(-1, 1)),
        (x0 + _rng.randint(-1, 1), y1 + _rng.randint(-1, 1)),
        (x0 + _rng.randint(-1, 1), y0 + _rng.randint(-1, 1)),
    ]
    draw.line(pts, fill=outline, width=width)


def _sketchy_circle(draw: ImageDraw.Draw, center, radius, outline=BLACK, fill=None, width=2):
    """Draw a slightly wobbly circle."""
    cx, cy = center
    bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
    if fill:
        draw.ellipse(bbox, fill=fill)
    draw.ellipse(bbox, outline=outline, width=width)


def _draw_body(draw: ImageDraw.Draw, offset_y=0):
    """Draw DoodleBob's rectangular body."""
    body_x0, body_y0 = 14, 8 + offset_y
    body_x1, body_y1 = 50, 52 + offset_y
    _sketchy_rect(draw, (body_x0, body_y0, body_x1, body_y1), fill=WHITE, width=2)
    return body_x0, body_y0, body_x1, body_y1


def _draw_face(draw: ImageDraw.Draw, offset_y=0, expression="normal"):
    """Draw DoodleBob's face (eyes, pupils, mouth)."""
    # Left eye (slightly bigger)
    _sketchy_circle(draw, (26, 22 + offset_y), 7, fill=WHITE, width=2)
    # Right eye
    _sketchy_circle(draw, (40, 20 + offset_y), 6, fill=WHITE, width=2)

    if expression == "normal":
        # Pupils
        draw.ellipse((24, 21 + offset_y, 28, 25 + offset_y), fill=PUPIL)
        draw.ellipse((39, 19 + offset_y, 42, 22 + offset_y), fill=PUPIL)
        # Mouth - wide grin
        draw.arc((20, 30 + offset_y, 44, 44 + offset_y), 0, 180, fill=MOUTH, width=2)
        draw.line([(20, 37 + offset_y), (44, 37 + offset_y)], fill=MOUTH, width=1)
    elif expression == "angry":
        # Angry pupils (centered, looking forward)
        draw.ellipse((25, 20 + offset_y, 29, 24 + offset_y), fill=PUPIL)
        draw.ellipse((38, 18 + offset_y, 42, 22 + offset_y), fill=PUPIL)
        # Angry eyebrows
        draw.line([(19, 14 + offset_y), (28, 17 + offset_y)], fill=BLACK, width=2)
        draw.line([(45, 12 + offset_y), (37, 16 + offset_y)], fill=BLACK, width=2)
        # Angry mouth
        draw.arc((22, 34 + offset_y, 42, 44 + offset_y), 180, 360, fill=MOUTH, width=2)
    elif expression == "surprised":
        draw.ellipse((23, 19 + offset_y, 29, 25 + offset_y), fill=PUPIL)
        draw.ellipse((37, 17 + offset_y, 43, 23 + offset_y), fill=PUPIL)
        # O-shaped mouth
        _sketchy_circle(draw, (32, 40 + offset_y), 5, fill=MOUTH, width=2)

    # Tie
    pts = [(30, 48 + offset_y), (27, 52 + offset_y), (33, 52 + offset_y)]
    draw.polygon(pts, fill=BLACK, outline=BLACK)


def _draw_legs(draw: ImageDraw.Draw, frame=0, offset_y=0):
    """Draw stick legs. frame 0-3 for walk cycle."""
    base_y = 52 + offset_y
    foot_y = 70 + offset_y
    if frame == 0:
        draw.line([(26, base_y), (20, foot_y)], fill=BLACK, width=2)
        draw.line([(38, base_y), (44, foot_y)], fill=BLACK, width=2)
    elif frame == 1:
        draw.line([(26, base_y), (24, foot_y)], fill=BLACK, width=2)
        draw.line([(38, base_y), (40, foot_y)], fill=BLACK, width=2)
    elif frame == 2:
        draw.line([(26, base_y), (32, foot_y)], fill=BLACK, width=2)
        draw.line([(38, base_y), (32, foot_y)], fill=BLACK, width=2)
    else:
        draw.line([(26, base_y), (22, foot_y)], fill=BLACK, width=2)
        draw.line([(38, base_y), (42, foot_y)], fill=BLACK, width=2)
    # Feet (small ovals)
    if frame == 0:
        draw.ellipse((16, foot_y - 2, 24, foot_y + 4), fill=BLACK)
        draw.ellipse((40, foot_y - 2, 48, foot_y + 4), fill=BLACK)
    elif frame == 1:
        draw.ellipse((20, foot_y - 2, 28, foot_y + 4), fill=BLACK)
        draw.ellipse((36, foot_y - 2, 44, foot_y + 4), fill=BLACK)
    elif frame == 2:
        draw.ellipse((28, foot_y - 2, 36, foot_y + 4), fill=BLACK)
        draw.ellipse((28, foot_y - 2, 36, foot_y + 4), fill=BLACK)
    else:
        draw.ellipse((18, foot_y - 2, 26, foot_y + 4), fill=BLACK)
        draw.ellipse((38, foot_y - 2, 46, foot_y + 4), fill=BLACK)


def _draw_arms(draw: ImageDraw.Draw, frame=0, offset_y=0, holding=None):
    """Draw stick arms. holding can be None, 'pencil', or 'eraser'."""
    body_left = 14
    body_right = 50
    arm_y = 32 + offset_y

    if holding:
        # Right arm extended holding item
        draw.line([(body_right, arm_y), (58, 20 + offset_y)], fill=BLACK, width=2)
        # Left arm relaxed
        if frame % 2 == 0:
            draw.line([(body_left, arm_y), (6, 40 + offset_y)], fill=BLACK, width=2)
        else:
            draw.line([(body_left, arm_y), (8, 36 + offset_y)], fill=BLACK, width=2)
        # Hand blobs
        draw.ellipse((4, 38 + offset_y, 10, 44 + offset_y) if frame % 2 == 0
                      else (6, 34 + offset_y, 12, 40 + offset_y), fill=BLACK)
    else:
        # Normal swinging arms
        if frame == 0:
            draw.line([(body_left, arm_y), (4, 26 + offset_y)], fill=BLACK, width=2)
            draw.line([(body_right, arm_y), (58, 40 + offset_y)], fill=BLACK, width=2)
        elif frame == 1:
            draw.line([(body_left, arm_y), (6, 34 + offset_y)], fill=BLACK, width=2)
            draw.line([(body_right, arm_y), (56, 34 + offset_y)], fill=BLACK, width=2)
        elif frame == 2:
            draw.line([(body_left, arm_y), (4, 40 + offset_y)], fill=BLACK, width=2)
            draw.line([(body_right, arm_y), (58, 26 + offset_y)], fill=BLACK, width=2)
        else:
            draw.line([(body_left, arm_y), (6, 34 + offset_y)], fill=BLACK, width=2)
            draw.line([(body_right, arm_y), (56, 34 + offset_y)], fill=BLACK, width=2)
        # Hand blobs
        for pos in _arm_endpoints(frame, offset_y):
            draw.ellipse((pos[0] - 3, pos[1] - 3, pos[0] + 3, pos[1] + 3), fill=BLACK)


def _arm_endpoints(frame, offset_y):
    if frame == 0:
        return [(4, 26 + offset_y), (58, 40 + offset_y)]
    elif frame == 1:
        return [(6, 34 + offset_y), (56, 34 + offset_y)]
    elif frame == 2:
        return [(4, 40 + offset_y), (58, 26 + offset_y)]
    else:
        return [(6, 34 + offset_y), (56, 34 + offset_y)]


def _add_sketch_dots(draw: ImageDraw.Draw):
    """Add random dots for a sketchy, hand-drawn feel."""
    for _ in range(6):
        x = _rng.randint(16, 48)
        y = _rng.randint(10, 50)
        draw.point((x, y), fill=(0, 0, 0, 80))


def _new_frame() -> tuple[Image.Image, ImageDraw.Draw]:
    img = Image.new("RGBA", (CHAR_BASE_W, CHAR_BASE_H), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    return img, draw


# ---------------------------------------------------------------------------
# Sprite set generators
# ---------------------------------------------------------------------------

def generate_idle_frames() -> list[Image.Image]:
    """Two frames: slight bobbing."""
    frames = []
    for i in range(2):
        img, draw = _new_frame()
        oy = -1 if i == 0 else 1
        _draw_body(draw, oy)
        _draw_face(draw, oy)
        _draw_arms(draw, frame=1, offset_y=oy)
        _draw_legs(draw, frame=1, offset_y=oy)
        _add_sketch_dots(draw)
        frames.append(img)
    return frames


def generate_walk_frames() -> list[Image.Image]:
    """Four frames of walking animation."""
    frames = []
    for i in range(4):
        img, draw = _new_frame()
        bob = -1 if i % 2 == 0 else 1
        _draw_body(draw, bob)
        _draw_face(draw, bob)
        _draw_arms(draw, frame=i, offset_y=bob)
        _draw_legs(draw, frame=i, offset_y=bob)
        _add_sketch_dots(draw)
        frames.append(img)
    return frames


def generate_chase_frames() -> list[Image.Image]:
    """Four frames of chasing (angry expression, leaning forward)."""
    frames = []
    for i in range(4):
        img, draw = _new_frame()
        bob = -2 if i % 2 == 0 else 0
        _draw_body(draw, bob)
        _draw_face(draw, bob, expression="angry")
        _draw_arms(draw, frame=i, offset_y=bob)
        _draw_legs(draw, frame=i, offset_y=bob)
        _add_sketch_dots(draw)
        frames.append(img)
    return frames


def generate_erase_frames() -> list[Image.Image]:
    """Frames of DoodleBob erasing with the magic pencil eraser end."""
    frames = []
    for i in range(4):
        img, draw = _new_frame()
        _draw_body(draw)
        _draw_face(draw, expression="angry")
        _draw_arms(draw, frame=i, holding="eraser")
        _draw_legs(draw, frame=1)

        # Draw eraser in hand
        ex = 56 + (i % 2) * 3
        ey = 14 + (i % 2) * 2
        draw.rectangle((ex, ey, ex + 10, ey + 6), fill=PENCIL_ERASER, outline=BLACK)

        _add_sketch_dots(draw)
        frames.append(img)
    return frames


def generate_draw_frames() -> list[Image.Image]:
    """Frames of DoodleBob drawing with the magic pencil tip."""
    frames = []
    for i in range(4):
        img, draw = _new_frame()
        _draw_body(draw)
        _draw_face(draw, expression="surprised")
        _draw_arms(draw, frame=i, holding="pencil")
        _draw_legs(draw, frame=1)

        # Draw pencil in hand
        px = 56
        py = 12 + (i % 2) * 2
        # Pencil body
        draw.rectangle((px, py, px + 18, py + 5), fill=PENCIL_YELLOW, outline=BLACK)
        # Pencil tip
        draw.polygon([(px + 18, py), (px + 23, py + 2), (px + 18, py + 5)],
                     fill=PENCIL_TIP)
        # Eraser end
        draw.rectangle((px - 3, py, px, py + 5), fill=PENCIL_ERASER, outline=BLACK)
        # Metal band
        draw.rectangle((px, py, px + 3, py + 5), fill=PENCIL_METAL, outline=BLACK)

        _add_sketch_dots(draw)
        frames.append(img)
    return frames


def generate_approach_frames() -> list[Image.Image]:
    """Walking toward a window X button - mischievous expression."""
    frames = []
    for i in range(4):
        img, draw = _new_frame()
        bob = -1 if i % 2 == 0 else 1
        _draw_body(draw, bob)
        _draw_face(draw, bob, expression="angry")
        _draw_arms(draw, frame=i, offset_y=bob)
        _draw_legs(draw, frame=i, offset_y=bob)
        _add_sketch_dots(draw)
        frames.append(img)
    return frames


def generate_cursor_sprite() -> Image.Image:
    """Generate a simple arrow cursor sprite."""
    size = 24
    img = Image.new("RGBA", (size, size), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    # Standard arrow cursor shape
    points = [
        (2, 2), (2, 18), (7, 14), (11, 20), (14, 18), (10, 12), (16, 12), (2, 2)
    ]
    draw.polygon(points, fill=WHITE, outline=BLACK)
    return img


# ---------------------------------------------------------------------------
# Save / Load
# ---------------------------------------------------------------------------

_SPRITE_SETS = {
    "idle": generate_idle_frames,
    "walk": generate_walk_frames,
    "chase": generate_chase_frames,
    "erase": generate_erase_frames,
    "draw": generate_draw_frames,
    "approach": generate_approach_frames,
}


def ensure_sprites_exist() -> None:
    """Generate placeholder sprites if they don't already exist."""
    os.makedirs(SPRITES_DIR, exist_ok=True)

    for name, gen_func in _SPRITE_SETS.items():
        first_file = os.path.join(SPRITES_DIR, f"{name}_0.png")
        gif_file = os.path.join(SPRITES_DIR, f"{name}.gif")
        if os.path.exists(first_file) or os.path.exists(gif_file):
            continue
        frames = gen_func()
        for i, frame in enumerate(frames):
            path = os.path.join(SPRITES_DIR, f"{name}_{i}.png")
            frame.save(path)

    cursor_path = os.path.join(SPRITES_DIR, "cursor.png")
    if not os.path.exists(cursor_path):
        generate_cursor_sprite().save(cursor_path)


def load_sprite_set(name: str, scale: int = 1) -> list[Image.Image]:
    """Load a named sprite set from disk.

    Checks for:
      1. An animated GIF  (e.g. walk.gif)
      2. Numbered PNGs     (e.g. walk_0.png, walk_1.png, ...)

    Returns a list of RGBA PIL Images, scaled by *scale*.
    """
    gif_path = os.path.join(SPRITES_DIR, f"{name}.gif")
    if os.path.exists(gif_path):
        gif = Image.open(gif_path)
        frames = []
        try:
            while True:
                frame = gif.copy().convert("RGBA")
                if scale != 1:
                    frame = frame.resize(
                        (frame.width * scale, frame.height * scale),
                        Image.NEAREST,
                    )
                frames.append(frame)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        if frames:
            return frames

    frames = []
    i = 0
    while True:
        path = os.path.join(SPRITES_DIR, f"{name}_{i}.png")
        if not os.path.exists(path):
            break
        img = Image.open(path).convert("RGBA")
        if scale != 1:
            img = img.resize(
                (img.width * scale, img.height * scale), Image.NEAREST
            )
        frames.append(img)
        i += 1

    return frames


def load_single_sprite(name: str, scale: int = 1) -> Image.Image | None:
    """Load a single sprite image."""
    path = os.path.join(SPRITES_DIR, f"{name}.png")
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGBA")
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    return img
