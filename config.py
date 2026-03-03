"""DoodleBob Desktop Pet - Configuration."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITES_DIR = os.path.join(BASE_DIR, "assets", "sprites")

# Display
SPRITE_SCALE = 2
TRANSPARENT_COLOR = "#010101"
UPDATE_MS = 33  # ~30 FPS

# Character sprite base size (before scaling)
# Width is 120 to fit the giant magic pencil held above DoodleBob's head
CHAR_BASE_W = 120
CHAR_BASE_H = 80

# Wandering (1.5x speed)
WANDER_SPEED_FRACTION = 0.105  # 0.07 * 1.5
WANDER_DIR_CHANGE_MIN_S = 2.0
WANDER_DIR_CHANGE_MAX_S = 6.0
IDLE_PAUSE_CHANCE = 0.2
IDLE_PAUSE_MIN_S = 1.0
IDLE_PAUSE_MAX_S = 3.0

# Window close behavior
WINDOW_CLOSE_MIN_DELAY_S = 10
WINDOW_CLOSE_MAX_DELAY_S = 15
WINDOW_CLOSE_APPROACH_SPEED_MULT = 0.75  # 0.5 * 1.5

# Cursor steal behavior
CURSOR_STEAL_MIN_DELAY_S = 10
CURSOR_STEAL_MAX_DELAY_S = 15
CURSOR_CHASE_ARRIVAL_S = 2.0  # time to run to cursor (seconds)
CURSOR_CATCH_RADIUS = 30
CURSOR_HIDE_DURATION_S = 1.5
WALK_TO_DRAW_ARRIVAL_S = 2.0  # time from erase done to draw position (seconds)

# Lurking phase (pre-cursor-steal)
LURK_DURATION_S = 1.5
LURK_SPEED_MULT = 2.24  # 1.28 * 1.75

# Screen doodle behavior
DOODLE_MIN_DELAY_S = 25
DOODLE_MAX_DELAY_S = 40
DOODLE_LINE_COUNT = 5
DOODLE_DRAW_DURATION_S = 2.0
DOODLE_FADE_DURATION_S = 3.0

# Pencil particle effect
PARTICLE_SPAWN_INTERVAL_S = 0.15
PARTICLE_LIFETIME_S = 0.6
PARTICLE_COUNT_PER_SPAWN = 2
PARTICLE_COLORS = ["#888888", "#999999", "#777777", "#AAAAAA"]

# Animation timing (frames per second for sprite animation)
ANIM_FPS = 8

# Sprite sheet
SPRITE_SHEET_BG = (192, 192, 192, 255)
SPRITE_SHEET_COLS = 4
SPRITE_SHEET_LAYOUT = [
    ("walk", 4),
    ("chase", 4),
    ("erase", 4),
    ("approach", 4),
    ("idle", 2),
    ("draw", 4),
    ("pencil_press", 4),
    ("lurk", 2),
    ("doodle", 4),
]
