"""Generate placeholder DoodleBob sprites using PIL.

These are meant to be replaced with proper pixel-art sprites created in
Aseprite or similar tools.  The generated sprites are intentionally rough
and "sketchy" to match DoodleBob's hand-drawn aesthetic.

The magic pencil is DoodleBob's defining item — it's MASSIVE, bigger than
DoodleBob himself, held above his head with both hands.
"""

import os
import math
import random as _rng
from PIL import Image, ImageDraw

from config import SPRITES_DIR, CHAR_BASE_W, CHAR_BASE_H

_rng.seed(42)

# Palette
BLACK = (0, 0, 0, 255)
WHITE = (245, 240, 230, 255)
PUPIL = (10, 10, 10, 255)
MOUTH = (30, 30, 30, 255)
PENCIL_YELLOW = (230, 190, 50, 255)
PENCIL_YELLOW_SHADE = (210, 170, 40, 255)
PENCIL_TIP = (55, 55, 55, 255)
PENCIL_METAL = (175, 175, 180, 255)
PENCIL_METAL_DARK = (140, 140, 148, 255)
PENCIL_ERASER = (220, 110, 110, 255)
TRANSPARENT = (0, 0, 0, 0)

# The character body is drawn on a 64x80 canvas, then composited onto the
# wider final canvas. The body is centered so mirroring works correctly.
_CHAR_DRAW_W = 64
_BODY_X_OFFSET = (CHAR_BASE_W - _CHAR_DRAW_W) // 2  # 28 for 120-wide
_BODY_CENTER_X = _BODY_X_OFFSET + 32  # 60 — center of body on final canvas

# Pencil dimensions
_PENCIL_LEN = 80
_PENCIL_HALF = _PENCIL_LEN // 2
_PENCIL_THICKNESS = 4  # half-height


# ---------------------------------------------------------------------------
# Character body drawing (64-wide internal canvas)
# ---------------------------------------------------------------------------

def _sketchy_rect(draw, bbox, outline=BLACK, fill=None, width=2):
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


def _sketchy_circle(draw, center, radius, outline=BLACK, fill=None, width=2):
    cx, cy = center
    bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
    if fill:
        draw.ellipse(bbox, fill=fill)
    draw.ellipse(bbox, outline=outline, width=width)


def _draw_body(draw, offset_y=0):
    _sketchy_rect(draw, (14, 8 + offset_y, 50, 52 + offset_y), fill=WHITE, width=2)


def _draw_face(draw, offset_y=0, expression="normal"):
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

    # Tie
    pts = [(30, 48 + offset_y), (27, 52 + offset_y), (33, 52 + offset_y)]
    draw.polygon(pts, fill=BLACK, outline=BLACK)


def _draw_legs(draw, frame=0, offset_y=0):
    base_y = 52 + offset_y
    foot_y = 70 + offset_y
    leg_x = {
        0: [(20, 44)], 1: [(24, 40)], 2: [(32, 32)], 3: [(22, 42)],
    }
    lx, rx = leg_x.get(frame, leg_x[1])[0]
    draw.line([(26, base_y), (lx, foot_y)], fill=BLACK, width=2)
    draw.line([(38, base_y), (rx, foot_y)], fill=BLACK, width=2)
    draw.ellipse((lx - 4, foot_y - 2, lx + 4, foot_y + 4), fill=BLACK)
    draw.ellipse((rx - 4, foot_y - 2, rx + 4, foot_y + 4), fill=BLACK)


def _add_sketch_dots(draw):
    for _ in range(6):
        x = _rng.randint(16, 48)
        y = _rng.randint(10, 50)
        draw.point((x, y), fill=(0, 0, 0, 80))


def _draw_char_body(offset_y=0, frame=0, expression="normal"):
    """Draw character body WITHOUT arms on 64x80 canvas."""
    img = Image.new("RGBA", (_CHAR_DRAW_W, CHAR_BASE_H), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    _draw_body(draw, offset_y)
    _draw_face(draw, offset_y, expression)
    _draw_legs(draw, frame, offset_y)
    _add_sketch_dots(draw)
    return img


# ---------------------------------------------------------------------------
# Giant Magic Pencil — drawn on the final wide canvas
# ---------------------------------------------------------------------------

def _draw_big_pencil(draw, center_x, pencil_y, tilt=0, flip=False):
    """Draw the massive magic pencil horizontally above DoodleBob.

    center_x:  horizontal center (typically _BODY_CENTER_X)
    pencil_y:  vertical center of the pencil
    tilt:      right-end y-offset (positive = right end lower)
    flip:      if True, eraser is on the right (for erasing actions)
    """
    left_x = center_x - _PENCIL_HALF
    right_x = center_x + _PENCIL_HALF
    left_y = pencil_y - tilt
    right_y = pencil_y + tilt
    t = _PENCIL_THICKNESS

    def _lerp_y(frac):
        return left_y + (right_y - left_y) * frac

    def _section_rect(frac_start, frac_end, color):
        x0 = left_x + _PENCIL_LEN * frac_start
        x1 = left_x + _PENCIL_LEN * frac_end
        y0s = _lerp_y(frac_start) - t
        y1s = _lerp_y(frac_start) + t
        y0e = _lerp_y(frac_end) - t
        y1e = _lerp_y(frac_end) + t
        pts = [(x0, y0s), (x1, y0e), (x1, y1e), (x0, y1s)]
        draw.polygon(pts, fill=color, outline=BLACK)

    if not flip:
        # [tip ▸ body ▸ metal ▸ eraser]
        #  left                    right

        # Graphite tip (pointed triangle)
        tip_frac = 0.10
        tip_x = left_x
        tip_y = _lerp_y(0)
        body_x = left_x + _PENCIL_LEN * tip_frac
        body_y_top = _lerp_y(tip_frac) - t
        body_y_bot = _lerp_y(tip_frac) + t
        draw.polygon([(tip_x, tip_y), (body_x, body_y_top), (body_x, body_y_bot)],
                     fill=PENCIL_TIP, outline=BLACK)

        # Yellow body
        _section_rect(0.10, 0.75, PENCIL_YELLOW)
        # Shade line on body
        for frac in [0.30, 0.50, 0.65]:
            sx = left_x + _PENCIL_LEN * frac
            sy_top = _lerp_y(frac) - t + 1
            sy_bot = _lerp_y(frac) + t - 1
            draw.line([(sx, sy_top), (sx, sy_bot)], fill=PENCIL_YELLOW_SHADE, width=1)

        # Metal ferrule
        _section_rect(0.75, 0.85, PENCIL_METAL)
        # Ferrule ridge lines
        for frac in [0.77, 0.79, 0.81, 0.83]:
            sx = left_x + _PENCIL_LEN * frac
            sy_top = _lerp_y(frac) - t + 1
            sy_bot = _lerp_y(frac) + t - 1
            draw.line([(sx, sy_top), (sx, sy_bot)], fill=PENCIL_METAL_DARK, width=1)

        # Eraser
        _section_rect(0.85, 1.0, PENCIL_ERASER)

    else:
        # Flipped: [eraser ▸ metal ▸ body ▸ tip]
        _section_rect(0.0, 0.15, PENCIL_ERASER)

        _section_rect(0.15, 0.25, PENCIL_METAL)
        for frac in [0.17, 0.19, 0.21, 0.23]:
            sx = left_x + _PENCIL_LEN * frac
            sy_top = _lerp_y(frac) - t + 1
            sy_bot = _lerp_y(frac) + t - 1
            draw.line([(sx, sy_top), (sx, sy_bot)], fill=PENCIL_METAL_DARK, width=1)

        _section_rect(0.25, 0.90, PENCIL_YELLOW)
        for frac in [0.35, 0.55, 0.70]:
            sx = left_x + _PENCIL_LEN * frac
            sy_top = _lerp_y(frac) - t + 1
            sy_bot = _lerp_y(frac) + t - 1
            draw.line([(sx, sy_top), (sx, sy_bot)], fill=PENCIL_YELLOW_SHADE, width=1)

        # Pointed tip on right
        tip_frac = 0.90
        tip_x = right_x
        tip_y = _lerp_y(1.0)
        body_x = left_x + _PENCIL_LEN * tip_frac
        body_y_top = _lerp_y(tip_frac) - t
        body_y_bot = _lerp_y(tip_frac) + t
        draw.polygon([(tip_x, tip_y), (body_x, body_y_top), (body_x, body_y_bot)],
                     fill=PENCIL_TIP, outline=BLACK)


def _draw_pencil_arms(draw, offset_y, pencil_y, tilt=0, grip_spread=22):
    """Draw both arms reaching UP to hold the giant pencil."""
    body_left_x = _BODY_X_OFFSET + 14
    body_right_x = _BODY_X_OFFSET + 50
    arm_y = 32 + offset_y

    left_grip_x = _BODY_CENTER_X - grip_spread
    right_grip_x = _BODY_CENTER_X + grip_spread

    left_grip_y = pencil_y - tilt * (grip_spread / _PENCIL_HALF) + _PENCIL_THICKNESS + 1
    right_grip_y = pencil_y + tilt * (grip_spread / _PENCIL_HALF) + _PENCIL_THICKNESS + 1

    # Arms (lines from body sides up to pencil)
    draw.line([(body_left_x, arm_y), (left_grip_x, left_grip_y)],
              fill=BLACK, width=2)
    draw.line([(body_right_x, arm_y), (right_grip_x, right_grip_y)],
              fill=BLACK, width=2)

    # Hand blobs gripping pencil
    r = 3
    draw.ellipse((left_grip_x - r, left_grip_y - r,
                  left_grip_x + r, left_grip_y + r), fill=BLACK)
    draw.ellipse((right_grip_x - r, right_grip_y - r,
                  right_grip_x + r, right_grip_y + r), fill=BLACK)


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

def _compose(char_body_img, offset_y, pencil_y=5, tilt=0, flip=False,
             grip_spread=22):
    """Compose: character body + giant pencil + arms on final canvas."""
    final = Image.new("RGBA", (CHAR_BASE_W, CHAR_BASE_H), TRANSPARENT)
    draw = ImageDraw.Draw(final)

    # 1) Arms first (behind body)
    _draw_pencil_arms(draw, offset_y, pencil_y, tilt, grip_spread)

    # 2) Character body on top of arms
    final.paste(char_body_img, (_BODY_X_OFFSET, 0), char_body_img)

    # 3) Giant pencil on top of everything
    _draw_big_pencil(draw, _BODY_CENTER_X, pencil_y, tilt, flip)

    return final


# ---------------------------------------------------------------------------
# Sprite set generators
# ---------------------------------------------------------------------------

def generate_idle_frames() -> list[Image.Image]:
    """Slight bobbing, pencil held proudly overhead."""
    frames = []
    for i in range(2):
        oy = -1 if i == 0 else 1
        body = _draw_char_body(oy, frame=1, expression="normal")
        frames.append(_compose(body, oy, pencil_y=4 + (i % 2)))
    return frames


def generate_walk_frames() -> list[Image.Image]:
    """Walking with pencil bouncing above head."""
    frames = []
    for i in range(4):
        bob = -1 if i % 2 == 0 else 1
        body = _draw_char_body(bob, frame=i, expression="normal")
        py = 3 + (i % 2) * 2  # pencil bobs with walk
        frames.append(_compose(body, bob, pencil_y=py))
    return frames


def generate_chase_frames() -> list[Image.Image]:
    """Angry, pencil tilted forward aggressively (tip leading)."""
    frames = []
    for i in range(4):
        bob = -2 if i % 2 == 0 else 0
        body = _draw_char_body(bob, frame=i, expression="angry")
        tilt = 3 + (i % 2)  # right end lower = tip points forward
        frames.append(_compose(body, bob, pencil_y=5, tilt=tilt))
    return frames


def generate_erase_frames() -> list[Image.Image]:
    """Eraser end forward — pencil flipped, tilted to jab eraser at target."""
    frames = []
    for i in range(4):
        body = _draw_char_body(0, frame=i, expression="angry")
        tilt = 3 + (i % 2) * 2
        frames.append(_compose(body, 0, pencil_y=5, tilt=tilt, flip=True))
    return frames


def generate_draw_frames() -> list[Image.Image]:
    """Tip forward, pencil tilted to draw with the graphite end."""
    frames = []
    for i in range(4):
        body = _draw_char_body(0, frame=i, expression="surprised")
        tilt = 4 + (i % 2) * 2
        frames.append(_compose(body, 0, pencil_y=5, tilt=tilt))
    return frames


def generate_approach_frames() -> list[Image.Image]:
    """Walking toward window X button, pencil tilted menacingly."""
    frames = []
    for i in range(4):
        bob = -1 if i % 2 == 0 else 1
        body = _draw_char_body(bob, frame=i, expression="angry")
        tilt = 2 + (i % 2)
        frames.append(_compose(body, bob, pencil_y=4, tilt=tilt))
    return frames


def generate_pencil_sprite() -> Image.Image:
    """Standalone magic pencil sprite (horizontal, detailed)."""
    w, h = 64, 16
    img = Image.new("RGBA", (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    cy = h // 2
    t = 5
    # Tip
    draw.polygon([(1, cy), (10, cy - t), (10, cy + t)],
                 fill=PENCIL_TIP, outline=BLACK)
    # Body
    draw.rectangle((10, cy - t, 48, cy + t), fill=PENCIL_YELLOW, outline=BLACK)
    # Ferrule
    draw.rectangle((48, cy - t, 54, cy + t), fill=PENCIL_METAL, outline=BLACK)
    for x in range(49, 54, 2):
        draw.line([(x, cy - t + 1), (x, cy + t - 1)], fill=PENCIL_METAL_DARK)
    # Eraser
    draw.rectangle((54, cy - t, 62, cy + t), fill=PENCIL_ERASER, outline=BLACK)
    return img


def generate_cursor_sprite() -> Image.Image:
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

    for name, gen_func in [("cursor", generate_cursor_sprite),
                           ("pencil", generate_pencil_sprite)]:
        path = os.path.join(SPRITES_DIR, f"{name}.png")
        if force or not os.path.exists(path):
            gen_func().save(path)


def load_sprite_set(name: str, scale: int = 1) -> list[Image.Image]:
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
    path = os.path.join(SPRITES_DIR, f"{name}.png")
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGBA")
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    return img
