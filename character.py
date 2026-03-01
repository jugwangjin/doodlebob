"""DoodleBob character - state machine, movement, and animation."""

from __future__ import annotations

import enum
import math
import random
import time
import tkinter as tk
from PIL import Image, ImageTk

from config import (
    CHAR_BASE_W, CHAR_BASE_H, SPRITE_SCALE,
    WANDER_SPEED, WANDER_DIR_CHANGE_MIN_S, WANDER_DIR_CHANGE_MAX_S,
    IDLE_PAUSE_CHANCE, IDLE_PAUSE_MIN_S, IDLE_PAUSE_MAX_S,
    WINDOW_CLOSE_APPROACH_SPEED, CURSOR_CHASE_SPEED, CURSOR_CATCH_RADIUS,
    ANIM_FPS,
)
from sprite_gen import load_sprite_set, load_single_sprite


class State(enum.Enum):
    IDLE = "idle"
    WANDERING = "walk"
    APPROACHING_WINDOW = "approach"
    CHASING_CURSOR = "chase"
    ERASING = "erase"
    DRAWING = "draw"


class Character:
    """DoodleBob character with state machine, animation, and movement."""

    def __init__(self, canvas: tk.Canvas, screen_w: int, screen_h: int):
        self.canvas = canvas
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Display dimensions
        self.display_w = CHAR_BASE_W * SPRITE_SCALE
        self.display_h = CHAR_BASE_H * SPRITE_SCALE

        # Position (center of character)
        self.x = random.randint(100, screen_w - 100)
        self.y = random.randint(100, screen_h - 100)

        # Movement
        self.vx = 0.0
        self.vy = 0.0
        self.facing_right = True

        # State
        self.state = State.WANDERING
        self._prev_state = State.WANDERING

        # Targets
        self.target_x: int | None = None
        self.target_y: int | None = None
        self.on_target_reached: callable = None
        self._target_hwnd: int | None = None

        # Timing
        self._direction_change_time = time.time() + random.uniform(
            WANDER_DIR_CHANGE_MIN_S, WANDER_DIR_CHANGE_MAX_S
        )
        self._idle_end_time: float | None = None

        # Animation
        self._sprites: dict[str, list[ImageTk.PhotoImage]] = {}
        self._sprite_pil: dict[str, list[Image.Image]] = {}
        self._frame_index = 0
        self._last_frame_time = time.time()
        self._frame_interval = 1.0 / ANIM_FPS

        # Canvas item
        self._canvas_id: int | None = None

        self._load_sprites()
        self._pick_wander_direction()

    def _load_sprites(self):
        """Load all sprite sets."""
        import logging
        log = logging.getLogger(__name__)
        for name in ("idle", "walk", "chase", "erase", "draw", "approach"):
            pil_frames = load_sprite_set(name, scale=SPRITE_SCALE)
            if not pil_frames:
                log.warning("No sprites for '%s', falling back to idle", name)
                pil_frames = load_sprite_set("idle", scale=SPRITE_SCALE)
            self._sprite_pil[name] = pil_frames
            self._sprites[name] = [ImageTk.PhotoImage(f) for f in pil_frames]
            mirrored = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in pil_frames]
            self._sprite_pil[f"{name}_l"] = mirrored
            self._sprites[f"{name}_l"] = [ImageTk.PhotoImage(f) for f in mirrored]
            log.info("Loaded '%s': %d frames, %dx%d px",
                     name, len(pil_frames),
                     pil_frames[0].width, pil_frames[0].height)

    def _current_sprite_key(self) -> str:
        base = self.state.value
        if not self.facing_right:
            return f"{base}_l"
        return base

    def _pick_wander_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * WANDER_SPEED
        self.vy = math.sin(angle) * WANDER_SPEED
        self.facing_right = self.vx >= 0
        self._direction_change_time = time.time() + random.uniform(
            WANDER_DIR_CHANGE_MIN_S, WANDER_DIR_CHANGE_MAX_S
        )

    def set_state(self, state: State):
        self._prev_state = self.state
        self.state = state
        self._frame_index = 0

    def move_toward(self, tx: int, ty: int, speed: float) -> bool:
        """Move toward target. Returns True if reached."""
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < speed + 2:
            self.x = tx
            self.y = ty
            return True
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        self.facing_right = self.vx >= 0
        self.x += self.vx
        self.y += self.vy
        return False

    def start_approach_window(self, hwnd: int, target_x: int, target_y: int,
                               callback: callable):
        """Begin walking toward a window's X button."""
        self.set_state(State.APPROACHING_WINDOW)
        self.target_x = target_x
        self.target_y = target_y
        self._target_hwnd = hwnd
        self.on_target_reached = callback

    def start_chase_cursor(self, cursor_x: int, cursor_y: int, callback: callable):
        """Begin chasing the cursor."""
        self.set_state(State.CHASING_CURSOR)
        self.target_x = cursor_x
        self.target_y = cursor_y
        self.on_target_reached = callback

    def start_erase(self, callback: callable):
        """Play the erase animation."""
        self.set_state(State.ERASING)
        self._anim_start = time.time()
        self.on_target_reached = callback

    def start_draw(self, callback: callable):
        """Play the draw animation."""
        self.set_state(State.DRAWING)
        self._anim_start = time.time()
        self.on_target_reached = callback

    def return_to_wander(self):
        """Go back to normal wandering."""
        self.set_state(State.WANDERING)
        self.target_x = None
        self.target_y = None
        self.on_target_reached = None
        self._target_hwnd = None
        self._pick_wander_direction()

    def update(self):
        """Update character state, position, and animation."""
        now = time.time()

        if self.state == State.IDLE:
            self._update_idle(now)
        elif self.state == State.WANDERING:
            self._update_wander(now)
        elif self.state == State.APPROACHING_WINDOW:
            self._update_approach()
        elif self.state == State.CHASING_CURSOR:
            self._update_chase()
        elif self.state in (State.ERASING, State.DRAWING):
            self._update_action_anim(now)

        self._clamp_position()
        self._update_animation(now)
        self._render()

    def _update_idle(self, now: float):
        if self._idle_end_time and now >= self._idle_end_time:
            self.set_state(State.WANDERING)
            self._pick_wander_direction()
            self._idle_end_time = None

    def _update_wander(self, now: float):
        self.x += self.vx
        self.y += self.vy

        # Bounce off edges with margin for sprite size
        mx = self.display_w // 2 + 10
        my = self.display_h // 2 + 10
        if self.x < mx or self.x > self.screen_w - mx:
            self.vx = -self.vx
            self.facing_right = self.vx >= 0
        if self.y < my or self.y > self.screen_h - my:
            self.vy = -self.vy

        # Periodic direction change
        if now >= self._direction_change_time:
            if random.random() < IDLE_PAUSE_CHANCE:
                self.set_state(State.IDLE)
                self.vx = 0
                self.vy = 0
                self._idle_end_time = now + random.uniform(
                    IDLE_PAUSE_MIN_S, IDLE_PAUSE_MAX_S
                )
            else:
                self._pick_wander_direction()

    def _update_approach(self):
        if self.target_x is not None and self.target_y is not None:
            reached = self.move_toward(
                self.target_x, self.target_y, WINDOW_CLOSE_APPROACH_SPEED
            )
            if reached and self.on_target_reached:
                cb = self.on_target_reached
                self.on_target_reached = None
                cb()

    def _update_chase(self):
        if self.target_x is not None and self.target_y is not None:
            dist = math.hypot(self.target_x - self.x, self.target_y - self.y)
            if dist <= CURSOR_CATCH_RADIUS:
                if self.on_target_reached:
                    cb = self.on_target_reached
                    self.on_target_reached = None
                    cb()
            else:
                self.move_toward(
                    self.target_x, self.target_y, CURSOR_CHASE_SPEED
                )

    def _update_action_anim(self, now: float):
        """For erase/draw: play through animation frames then callback."""
        key = self._current_sprite_key()
        frames = self._sprites.get(key, [])
        total_frames = len(frames) if frames else 4
        anim_duration = total_frames * self._frame_interval * 2  # Play twice

        if now - self._anim_start >= anim_duration:
            if self.on_target_reached:
                cb = self.on_target_reached
                self.on_target_reached = None
                cb()

    def _clamp_position(self):
        mx = self.display_w // 2 + 4
        my = self.display_h // 2 + 4
        self.x = max(mx, min(self.screen_w - mx, self.x))
        self.y = max(my, min(self.screen_h - my, self.y))

    def _update_animation(self, now: float):
        if now - self._last_frame_time >= self._frame_interval:
            self._frame_index += 1
            self._last_frame_time = now

    def _render(self):
        key = self._current_sprite_key()
        frames = self._sprites.get(key, [])
        if not frames:
            return

        idx = self._frame_index % len(frames)
        sprite = frames[idx]

        if self._canvas_id is None:
            self._canvas_id = self.canvas.create_image(
                int(self.x), int(self.y), image=sprite, anchor=tk.CENTER
            )
        else:
            self.canvas.coords(self._canvas_id, int(self.x), int(self.y))
            self.canvas.itemconfig(self._canvas_id, image=sprite)

    def update_cursor_target(self, cx: int, cy: int):
        """Update the chase target to current cursor position (called each frame)."""
        if self.state == State.CHASING_CURSOR:
            self.target_x = cx
            self.target_y = cy
