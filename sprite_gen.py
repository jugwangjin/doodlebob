"""Generate placeholder DoodleBob sprites using PIL.

These are meant to be replaced with proper pixel-art sprites created in
Aseprite or similar tools.  The generated sprites are intentionally rough
and "sketchy" to match DoodleBob's hand-drawn aesthetic.

The magic pencil is DoodleBob's defining item and appears in every sprite.
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

# The character body is drawn on a 64x80 canvas, then composited onto the
# wider CHAR_BASE_W canvas with an X offset so the body is centered and the
# pencil has room to extend to the right (and to the left when mirrored).
_CHAR_DRAW_W = 64
_BODY_X_OFFSET = (CHAR_BASE_W - _CHAR_DRAW_W) // 2  # 12 for 88-wide canvas


# ---------------------------------------------------------------------------
# Character body drawing (all on 64-wide internal canvas, unchanged)
# ---------------------------------------------------------------------------

def _sketchy_rect(draw: ImageDraw.Draw, bbox, outline=BLACK, fill=None, width=2):
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


def _sketchy_circle(draw: ImageDraw.Draw, center, radius, outline=BLACK,
                    fill=None, width=2):
    cx, cy = center
    bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
    if fill:
        draw.ellipse(bbox, fill=fill)
    draw.ellipse(bbox, outline=outline, width=width)


def _draw_body(draw: ImageDraw.Draw, offset_y=0):
    body_x0, body_y0 = 14, 8 + offset_y
    body_x1, body_y1 = 50, 52 + offset_y
    _sketchy_rect(draw, (body_x0, body_y0, body_x1, body_y1), fill=WHITE, width=2)
    return body_x0, body_y0, body_x1, body_y1


def _draw_face(draw: ImageDraw.Draw, offset_y=0, expression="normal"):
    _sketchy_circle(draw, (26, 22 + offset_y), 7, fill=WHITE, width=2)
    _sketchy_circle(draw, (40, 20 + offset_y), 6, fill=WHITE, width=2)

    if expression == "normal":
        draw.ellipse((24, 21 + offset_y, 28, 25 + offset_y), fill=PUPIL)
        draw.ellipse((39, 19 + offset_y, 42, 22 + offset_y), fill=PUPIL)
        draw.arc((20, 30 + offset_y, 44, 44 + offset_y), 0, 180, fill=MOUTH, width=2)
        draw.line([(20, 37 + offset_y), (44, 37 + offset_y)], fill=MOUTH, width=1)
    elif expression == "angry":
        draw.ellipse((25, 20 + offset_y, 29, 24 + offset_y), fill=PUPIL)
        draw.ellipse((38, 18 + offset_y, 42, 22 + offset_y), fill=PUPIL)
        draw.line([(19, 14 + offset_y), (28, 17 + offset_y)], fill=BLACK, width=2)
        draw.line([(45, 12 + offset_y), (37, 16 + offset_y)], fill=BLACK, width=2)
        draw.arc((22, 34 + offset_y, 42, 44 + offset_y), 180, 360, fill=MOUTH, width=2)
    elif expression == "surprised":
        draw.ellipse((23, 19 + offset_y, 29, 25 + offset_y), fill=PUPIL)
        draw.ellipse((37, 17 + offset_y, 43, 23 + offset_y), fill=PUPIL)
        _sketchy_circle(draw, (32, 40 + offset_y), 5, fill=MOUTH, width=2)

    pts = [(30, 48 + offset_y), (27, 52 + offset_y), (33, 52 + offset_y)]
    draw.polygon(pts, fill=BLACK, outline=BLACK)


def _draw_legs(draw: ImageDraw.Draw, frame=0, offset_y=0):
    base_y = 52 + offset_y
    foot_y = 70 + offset_y
    leg_positions = {
        0: [(26, 20), (38, 44)],
        1: [(26, 24), (38, 40)],
        2: [(26, 32), (38, 32)],
        3: [(26, 22), (38, 42)],
    }
    lx, rx = leg_positions.get(frame, leg_positions[1])
    draw.line([(26, base_y), (lx[1], foot_y)], fill=BLACK, width=2)
    draw.line([(38, base_y), (rx[1], foot_y)], fill=BLACK, width=2)
    draw.ellipse((lx[1] - 4, foot_y - 2, lx[1] + 4, foot_y + 4), fill=BLACK)
    draw.ellipse((rx[1] - 4, foot_y - 2, rx[1] + 4, foot_y + 4), fill=BLACK)


def _draw_arms(draw: ImageDraw.Draw, frame=0, offset_y=0, holding=False):
    """Draw stick arms. Returns (right_hand_x, right_hand_y) on 64-wide canvas."""
    body_left = 14
    body_right = 50
    arm_y = 32 + offset_y

    if holding:
        rh = (58, 20 + offset_y)
        draw.line([(body_right, arm_y), rh], fill=BLACK, width=2)
        lh = (6, 40 + offset_y) if frame % 2 == 0 else (8, 36 + offset_y)
        draw.line([(body_left, arm_y), lh], fill=BLACK, width=2)
        draw.ellipse((lh[0] - 3, lh[1] - 3, lh[0] + 3, lh[1] + 3), fill=BLACK)
        draw.ellipse((rh[0] - 3, rh[1] - 3, rh[0] + 3, rh[1] + 3), fill=BLACK)
        return rh

    right_positions = {0: (58, 40), 1: (56, 34), 2: (58, 26), 3: (56, 34)}
    left_positions = {0: (4, 26), 1: (6, 34), 2: (4, 40), 3: (6, 34)}

    rh = (right_positions[frame][0], right_positions[frame][1] + offset_y)
    lh = (left_positions[frame][0], left_positions[frame][1] + offset_y)

    draw.line([(body_right, arm_y), rh], fill=BLACK, width=2)
    draw.line([(body_left, arm_y), lh], fill=BLACK, width=2)
    draw.ellipse((rh[0] - 3, rh[1] - 3, rh[0] + 3, rh[1] + 3), fill=BLACK)
    draw.ellipse((lh[0] - 3, lh[1] - 3, lh[0] + 3, lh[1] + 3), fill=BLACK)
    return rh


def _add_sketch_dots(draw: ImageDraw.Draw):
    for _ in range(6):
        x = _rng.randint(16, 48)
        y = _rng.randint(10, 50)
        draw.point((x, y), fill=(0, 0, 0, 80))


# ---------------------------------------------------------------------------
# Magic Pencil
# ---------------------------------------------------------------------------

def _draw_magic_pencil(draw: ImageDraw.Draw, hx, hy, angle_deg,
                       flip=False, length=18):
    """Draw the magic pencil extending from hand position.

    hx, hy:     grip position (hand coordinates on the FINAL canvas)
    angle_deg:  direction the pencil extends (0=right, negative=up)
    flip:       if True, eraser end is at the far end (for erasing action)
    length:     pencil length in pixels
    """
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    w = 2.5
    nx, ny = -dy * w, dx * w

    def _rect(s, e, color):
        pts = [
            (hx + dx * s + nx, hy + dy * s + ny),
            (hx + dx * e + nx, hy + dy * e + ny),
            (hx + dx * e - nx, hy + dy * e - ny),
            (hx + dx * s - nx, hy + dy * s - ny),
        ]
        draw.polygon(pts, fill=color, outline=BLACK)

    if not flip:
        # Normal: eraser near hand → metal → body → tip
        _rect(0, 3, PENCIL_ERASER)
        _rect(3, 5, PENCIL_METAL)
        _rect(5, length - 3, PENCIL_YELLOW)
        # Pointed tip (triangle)
        tip_s = length - 3
        tip_pts = [
            (hx + dx * tip_s + nx, hy + dy * tip_s + ny),
            (hx + dx * tip_s - nx, hy + dy * tip_s - ny),
            (hx + dx * (length + 2), hy + dy * (length + 2)),
        ]
        draw.polygon(tip_pts, fill=PENCIL_TIP, outline=BLACK)
    else:
        # Flipped: tip near hand → body → metal → eraser far
        _rect(0, 3, PENCIL_TIP)
        _rect(3, length - 5, PENCIL_YELLOW)
        _rect(length - 5, length - 3, PENCIL_METAL)
        _rect(length - 3, length, PENCIL_ERASER)
        # Rounded eraser end
        ex = hx + dx * length
        ey = hy + dy * length
        draw.ellipse((ex - 3, ey - 3, ex + 3, ey + 3),
                     fill=PENCIL_ERASER, outline=BLACK)


# ---------------------------------------------------------------------------
# Composition: character body + magic pencil on the wider canvas
# ---------------------------------------------------------------------------

def _draw_character(offset_y=0, frame=0, expression="normal", holding=False):
    """Draw the character body on a 64-wide canvas.
    Returns (char_image, right_hand_x, right_hand_y).
    """
    img = Image.new("RGBA", (_CHAR_DRAW_W, CHAR_BASE_H), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    _draw_body(draw, offset_y)
    _draw_face(draw, offset_y, expression)
    rh = _draw_arms(draw, frame, offset_y, holding)
    _draw_legs(draw, frame, offset_y)
    _add_sketch_dots(draw)
    return img, rh[0], rh[1]


def _compose(char_img, hand_x, hand_y, pencil_angle, pencil_flip=False):
    """Compose character + magic pencil on the full-width canvas."""
    final = Image.new("RGBA", (CHAR_BASE_W, CHAR_BASE_H), TRANSPARENT)
    final.paste(char_img, (_BODY_X_OFFSET, 0), char_img)
    final_draw = ImageDraw.Draw(final)
    _draw_magic_pencil(
        final_draw,
        hand_x + _BODY_X_OFFSET,
        hand_y,
        pencil_angle,
        flip=pencil_flip,
    )
    return final


# ---------------------------------------------------------------------------
# Sprite set generators
# ---------------------------------------------------------------------------

def generate_idle_frames() -> list[Image.Image]:
    """Two frames: slight bobbing, pencil held casually."""
    frames = []
    for i in range(2):
        oy = -1 if i == 0 else 1
        char_img, hx, hy = _draw_character(oy, frame=1, expression="normal")
        frames.append(_compose(char_img, hx, hy, pencil_angle=-50))
    return frames


def generate_walk_frames() -> list[Image.Image]:
    """Four frames of walking, pencil carried at a jaunty angle."""
    angles = [-55, -45, -35, -45]
    frames = []
    for i in range(4):
        bob = -1 if i % 2 == 0 else 1
        char_img, hx, hy = _draw_character(bob, frame=i, expression="normal")
        frames.append(_compose(char_img, hx, hy, pencil_angle=angles[i]))
    return frames


def generate_chase_frames() -> list[Image.Image]:
    """Four frames: angry, pencil pointed forward aggressively."""
    frames = []
    for i in range(4):
        bob = -2 if i % 2 == 0 else 0
        char_img, hx, hy = _draw_character(bob, frame=i, expression="angry")
        frames.append(_compose(char_img, hx, hy, pencil_angle=-15))
    return frames


def generate_erase_frames() -> list[Image.Image]:
    """DoodleBob erasing with the pencil's eraser end forward."""
    angles = [-5, 0, 5, 0]
    frames = []
    for i in range(4):
        char_img, hx, hy = _draw_character(
            offset_y=0, frame=i, expression="angry", holding=True
        )
        frames.append(
            _compose(char_img, hx, hy, pencil_angle=angles[i], pencil_flip=True)
        )
    return frames


def generate_draw_frames() -> list[Image.Image]:
    """DoodleBob drawing with the pencil tip forward."""
    angles = [15, 10, 20, 10]
    frames = []
    for i in range(4):
        char_img, hx, hy = _draw_character(
            offset_y=0, frame=i, expression="surprised", holding=True
        )
        frames.append(
            _compose(char_img, hx, hy, pencil_angle=angles[i], pencil_flip=False)
        )
    return frames


def generate_approach_frames() -> list[Image.Image]:
    """Walking toward a window X button, pencil forward menacingly."""
    frames = []
    for i in range(4):
        bob = -1 if i % 2 == 0 else 1
        char_img, hx, hy = _draw_character(bob, frame=i, expression="angry")
        frames.append(_compose(char_img, hx, hy, pencil_angle=-20))
    return frames


def generate_pencil_sprite() -> Image.Image:
    """Generate a standalone magic pencil sprite (horizontal, larger)."""
    w, h = 52, 14
    img = Image.new("RGBA", (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    cy = h // 2
    # Eraser
    draw.rectangle((1, 2, 7, 11), fill=PENCIL_ERASER, outline=BLACK)
    # Metal band
    draw.rectangle((7, 2, 12, 11), fill=PENCIL_METAL, outline=BLACK)
    # Body
    draw.rectangle((12, 2, 40, 11), fill=PENCIL_YELLOW, outline=BLACK)
    # Tip (triangle)
    draw.polygon([(40, 2), (40, 11), (50, cy)], fill=PENCIL_TIP, outline=BLACK)
    return img


def generate_cursor_sprite() -> Image.Image:
    """Generate a simple arrow cursor sprite."""
    size = 24
    img = Image.new("RGBA", (size, size), TRANSPARENT)
    draw = ImageDraw.Draw(img)
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


def ensure_sprites_exist(force: bool = False) -> None:
    """Generate placeholder sprites if they don't already exist.

    Pass force=True to regenerate even if files exist.
    """
    os.makedirs(SPRITES_DIR, exist_ok=True)

    for name, gen_func in _SPRITE_SETS.items():
        first_file = os.path.join(SPRITES_DIR, f"{name}_0.png")
        gif_file = os.path.join(SPRITES_DIR, f"{name}.gif")
        if not force and (os.path.exists(first_file) or os.path.exists(gif_file)):
            continue
        frames = gen_func()
        for i, frame in enumerate(frames):
            path = os.path.join(SPRITES_DIR, f"{name}_{i}.png")
            frame.save(path)

    cursor_path = os.path.join(SPRITES_DIR, "cursor.png")
    if force or not os.path.exists(cursor_path):
        generate_cursor_sprite().save(cursor_path)

    pencil_path = os.path.join(SPRITES_DIR, "pencil.png")
    if force or not os.path.exists(pencil_path):
        generate_pencil_sprite().save(pencil_path)


def load_sprite_set(name: str, scale: int = 1) -> list[Image.Image]:
    """Load a named sprite set from disk.

    Checks for:
      1. An animated GIF  (e.g. walk.gif)
      2. Numbered PNGs     (e.g. walk_0.png, walk_1.png, ...)
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
