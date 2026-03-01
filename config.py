"""DoodleBob Desktop Pet - Configuration."""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITES_DIR = os.path.join(BASE_DIR, "assets", "sprites")

# Display
SPRITE_SCALE = 2
TRANSPARENT_COLOR = "#010101"
UPDATE_MS = 33  # ~30 FPS

# Character sprite base size (before scaling)
CHAR_BASE_W = 64
CHAR_BASE_H = 80

# Wandering
WANDER_SPEED = 1.5
WANDER_DIR_CHANGE_MIN_S = 2.0
WANDER_DIR_CHANGE_MAX_S = 6.0
IDLE_PAUSE_CHANCE = 0.2
IDLE_PAUSE_MIN_S = 1.0
IDLE_PAUSE_MAX_S = 3.0

# Window close behavior
WINDOW_CLOSE_MIN_DELAY_S = 30
WINDOW_CLOSE_MAX_DELAY_S = 90
WINDOW_CLOSE_APPROACH_SPEED = 3.5

# Cursor steal behavior
CURSOR_STEAL_MIN_DELAY_S = 15
CURSOR_STEAL_MAX_DELAY_S = 40
CURSOR_CHASE_SPEED = 4.0
CURSOR_CATCH_RADIUS = 30
CURSOR_HIDE_DURATION_S = 1.5

# Animation timing (frames per second for sprite animation)
ANIM_FPS = 8
