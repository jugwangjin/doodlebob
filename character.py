"""DoodleBob character - state machine, movement, animation, and particles."""

from __future__ import annotations

import enum
import math
import random
import time
import tkinter as tk
from PIL import Image, ImageTk

from config import (
    CHAR_BASE_W, CHAR_BASE_H, SPRITE_SCALE, UPDATE_MS,
    WANDER_SPEED_FRACTION, WANDER_DIR_CHANGE_MIN_S, WANDER_DIR_CHANGE_MAX_S,
    IDLE_PAUSE_CHANCE, IDLE_PAUSE_MIN_S, IDLE_PAUSE_MAX_S,
    WINDOW_CLOSE_APPROACH_SPEED_MULT, CURSOR_CHASE_ARRIVAL_S, CURSOR_CATCH_RADIUS,
    WALK_TO_DRAW_ARRIVAL_S, LURK_SPEED_MULT,
    ANIM_FPS,
    PARTICLE_SPAWN_INTERVAL_S, PARTICLE_LIFETIME_S,
    PARTICLE_COUNT_PER_SPAWN, PARTICLE_COLORS,
)
from sprite_gen import load_sprite_set, load_single_sprite


class State(enum.Enum):
    IDLE = "idle"
    WANDERING = "walk"
    APPROACHING_WINDOW = "approach"
    PENCIL_PRESSING = "pencil_press"
    CHASING_CURSOR = "chase"
    ERASING = "erase"
    WALKING_TO_DRAW = "walk_to_draw"
    DRAWING = "draw"
    LURKING = "lurk"
    LURK_CHARGING = "chase"  # reuse chase sprites for the charge
    DOODLING = "doodle"


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "born", "color", "canvas_id")

    def __init__(self, x: float, y: float, color: str):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(0.5, 2.0)
        self.born = time.time()
        self.color = color
        self.canvas_id: int | None = None


class Character:
    """DoodleBob character with state machine, animation, and movement."""

    def __init__(self, canvas: tk.Canvas, screen_w: int, screen_h: int,
                 floating: bool = False):
        self.canvas = canvas
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.floating = floating

        # Display dimensions
        self.display_w = CHAR_BASE_W * SPRITE_SCALE
        self.display_h = CHAR_BASE_H * SPRITE_SCALE

        # Position (center of character)
        self.x = random.randint(100, screen_w - 100)
        self.y = random.randint(100, screen_h - 100)

        # Movement — speeds derived from screen size
        fps = 1000.0 / UPDATE_MS
        long_axis = max(screen_w, screen_h)
        self.wander_speed = WANDER_SPEED_FRACTION * long_axis / fps
        self.approach_speed = self.wander_speed * WINDOW_CLOSE_APPROACH_SPEED_MULT
        self.lurk_speed = self.wander_speed * LURK_SPEED_MULT

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

        # Chase / walk-to-draw timing
        self._chase_start_time: float = 0.0
        self._walk_to_draw_start_time: float = 0.0

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

        # Lurking
        self._lurk_end_time: float | None = None

        # Particles
        self._particles: list[Particle] = []
        self._last_particle_spawn = 0.0
        self._particles_enabled = not floating  # particles only in windowed mode

        self._load_sprites()
        self._pick_wander_direction()

    def _load_sprites(self):
        """Load all sprite sets."""
        import logging
        log = logging.getLogger(__name__)
        sprite_names = (
            "idle", "walk", "chase", "erase", "draw",
            "approach", "pencil_press", "lurk", "doodle",
        )
        for name in sprite_names:
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
        if self.state == State.WALKING_TO_DRAW:
            base = "walk"
        elif self.state == State.LURK_CHARGING:
            base = "chase"
        suffix = "" if self.facing_right else "_l"
        return base + suffix

    def _pick_wander_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * self.wander_speed
        self.vy = math.sin(angle) * self.wander_speed
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
        """Begin chasing the cursor — guaranteed arrival in CURSOR_CHASE_ARRIVAL_S."""
        self.set_state(State.CHASING_CURSOR)
        self.target_x = cursor_x
        self.target_y = cursor_y
        self.on_target_reached = callback
        self._chase_start_time = time.time()

    def start_lurk_charge(self, cursor_x: int, cursor_y: int, callback: callable):
        """Charge at cursor from lurking position (uses chase sprites)."""
        self.set_state(State.LURK_CHARGING)
        self.target_x = cursor_x
        self.target_y = cursor_y
        self.on_target_reached = callback
        self._chase_start_time = time.time()

    def start_erase(self, callback: callable):
        """Play the erase animation."""
        self.set_state(State.ERASING)
        self._anim_start = time.time()
        self.on_target_reached = callback

    def start_pencil_press(self, callback: callable):
        """Play the pencil-press animation (jabbing X button)."""
        self.set_state(State.PENCIL_PRESSING)
        self._anim_start = time.time()
        self.on_target_reached = callback

    def start_draw(self, callback: callable):
        """Play the draw animation."""
        self.set_state(State.DRAWING)
        self._anim_start = time.time()
        self.on_target_reached = callback

    def start_walk_to_draw(self, target_x: int, target_y: int, callback: callable):
        """Walk to target position (used after erasing cursor, before drawing). Arrives in WALK_TO_DRAW_ARRIVAL_S."""
        self.set_state(State.WALKING_TO_DRAW)
        self.target_x = target_x
        self.target_y = target_y
        self.on_target_reached = callback
        self._walk_to_draw_start_time = time.time()

    def start_lurk(self, edge_x: int, edge_y: int, callback: callable):
        """Move quickly to screen edge for lurking."""
        self.set_state(State.WANDERING)  # walk sprite during movement
        self.target_x = edge_x
        self.target_y = edge_y
        self.on_target_reached = callback

    def start_lurk_wait(self, duration: float, callback: callable):
        """Show lurking sprite (eyes only) for a duration."""
        self.set_state(State.LURKING)
        self._lurk_end_time = time.time() + duration
        self.on_target_reached = callback

    def start_doodle(self, callback: callable):
        """Play the doodling animation."""
        self.set_state(State.DOODLING)
        self._anim_start = time.time()
        self.on_target_reached = callback

    def return_to_wander(self):
        """Go back to normal wandering."""
        self.set_state(State.WANDERING)
        self.target_x = None
        self.target_y = None
        self.on_target_reached = None
        self._target_hwnd = None
        self._lurk_end_time = None
        self._pick_wander_direction()

    def update(self):
        """Update character state, position, and animation."""
        now = time.time()

        if self.state == State.IDLE:
            self._update_idle(now)
        elif self.state == State.WANDERING:
            if self.target_x is not None:
                self._update_lurk_move()
            else:
                self._update_wander(now)
        elif self.state == State.APPROACHING_WINDOW:
            self._update_approach()
        elif self.state in (State.CHASING_CURSOR, State.LURK_CHARGING):
            self._update_chase()
        elif self.state in (State.ERASING, State.DRAWING, State.PENCIL_PRESSING,
                            State.DOODLING):
            self._update_action_anim(now)
        elif self.state == State.WALKING_TO_DRAW:
            self._update_walk_to_draw()
        elif self.state == State.LURKING:
            self._update_lurk_wait(now)

        self._clamp_position()
        self._update_animation(now)
        self._update_particles(now)
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

    def _update_lurk_move(self):
        """Fast movement toward lurk edge position."""
        reached = self.move_toward(
            self.target_x, self.target_y, self.lurk_speed
        )
        if reached and self.on_target_reached:
            cb = self.on_target_reached
            self.on_target_reached = None
            self.target_x = None
            self.target_y = None
            cb()

    def _update_lurk_wait(self, now: float):
        """Wait in lurking state (showing glowing eyes)."""
        if self._lurk_end_time and now >= self._lurk_end_time:
            self._lurk_end_time = None
            if self.on_target_reached:
                cb = self.on_target_reached
                self.on_target_reached = None
                cb()

    def _update_approach(self):
        if self.target_x is not None and self.target_y is not None:
            reached = self.move_toward(
                self.target_x, self.target_y, self.approach_speed
            )
            if reached and self.on_target_reached:
                cb = self.on_target_reached
                self.on_target_reached = None
                cb()

    def _update_chase(self):
        if self.target_x is not None and self.target_y is not None:
            elapsed = time.time() - self._chase_start_time
            remaining = CURSOR_CHASE_ARRIVAL_S - elapsed
            dist = math.hypot(self.target_x - self.x, self.target_y - self.y)

            if remaining <= 0 or dist <= CURSOR_CATCH_RADIUS:
                self.x = float(self.target_x)
                self.y = float(self.target_y)
                if self.on_target_reached:
                    cb = self.on_target_reached
                    self.on_target_reached = None
                    cb()
            else:
                fps = 1000.0 / UPDATE_MS
                speed = max(dist / remaining / fps, 1.0)
                self.move_toward(self.target_x, self.target_y, speed)

    def _update_action_anim(self, now: float):
        """For erase/draw/doodle: play through animation frames then callback."""
        key = self._current_sprite_key()
        frames = self._sprites.get(key, [])
        total_frames = len(frames) if frames else 4
        anim_duration = total_frames * self._frame_interval * 2  # Play twice

        if now - self._anim_start >= anim_duration:
            if self.on_target_reached:
                cb = self.on_target_reached
                self.on_target_reached = None
                cb()

    def _update_walk_to_draw(self):
        if self.target_x is not None and self.target_y is not None:
            elapsed = time.time() - self._walk_to_draw_start_time
            remaining = WALK_TO_DRAW_ARRIVAL_S - elapsed
            dist = math.hypot(self.target_x - self.x, self.target_y - self.y)
            if remaining <= 0 or dist <= 4:
                self.x = float(self.target_x)
                self.y = float(self.target_y)
                if self.on_target_reached:
                    cb = self.on_target_reached
                    self.on_target_reached = None
                    cb()
            else:
                fps = 1000.0 / UPDATE_MS
                speed = max(dist / remaining / fps, 1.0)
                reached = self.move_toward(self.target_x, self.target_y, speed)
                if reached and self.on_target_reached:
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

    # ------------------------------------------------------------------
    # Particles
    # ------------------------------------------------------------------

    def _update_particles(self, now: float):
        if not self._particles_enabled:
            return

        moving = self.state in (
            State.WANDERING, State.APPROACHING_WINDOW,
            State.CHASING_CURSOR, State.LURK_CHARGING,
            State.WALKING_TO_DRAW,
        )
        if moving and self.target_x is None and self.state == State.WANDERING:
            moving = True
        elif self.state == State.WANDERING and self.target_x is not None:
            moving = True

        if moving and now - self._last_particle_spawn >= PARTICLE_SPAWN_INTERVAL_S:
            self._spawn_particles()
            self._last_particle_spawn = now

        alive = []
        for p in self._particles:
            age = now - p.born
            if age > PARTICLE_LIFETIME_S:
                if p.canvas_id is not None:
                    self.canvas.delete(p.canvas_id)
                continue
            p.x += p.vx
            p.y += p.vy
            # Fade: reduce size with age
            r = max(1, int(3 * (1.0 - age / PARTICLE_LIFETIME_S)))
            if p.canvas_id is None:
                p.canvas_id = self.canvas.create_oval(
                    p.x - r, p.y - r, p.x + r, p.y + r,
                    fill=p.color, outline="",
                )
            else:
                self.canvas.coords(
                    p.canvas_id,
                    p.x - r, p.y - r, p.x + r, p.y + r,
                )
            alive.append(p)
        self._particles = alive

    def _spawn_particles(self):
        # Pencil tip position relative to character center
        # In right-facing mode: pencil tip is on the left side of the sprite
        tip_offset_x = -self.display_w // 2 + 10 if self.facing_right else self.display_w // 2 - 10
        tip_y_offset = -self.display_h // 2 + 10

        for _ in range(PARTICLE_COUNT_PER_SPAWN):
            px = self.x + tip_offset_x + random.uniform(-5, 5)
            py = self.y + tip_y_offset + random.uniform(-3, 3)
            color = random.choice(PARTICLE_COLORS)
            self._particles.append(Particle(px, py, color))

    def clear_particles(self):
        """Remove all active particles from canvas."""
        for p in self._particles:
            if p.canvas_id is not None:
                self.canvas.delete(p.canvas_id)
        self._particles.clear()

    def _render(self):
        key = self._current_sprite_key()
        frames = self._sprites.get(key, [])
        if not frames:
            return

        idx = self._frame_index % len(frames)
        sprite = frames[idx]

        if self.floating:
            # In floating mode the window moves, sprite stays at canvas center
            rx = self.display_w // 2
            ry = self.display_h // 2
        else:
            rx = int(self.x)
            ry = int(self.y)

        if self._canvas_id is None:
            self._canvas_id = self.canvas.create_image(
                rx, ry, image=sprite, anchor=tk.CENTER
            )
        else:
            self.canvas.coords(self._canvas_id, rx, ry)
            self.canvas.itemconfig(self._canvas_id, image=sprite)

    def update_cursor_target(self, cx: int, cy: int):
        """Update the chase target to current cursor position (called each frame)."""
        if self.state in (State.CHASING_CURSOR, State.LURK_CHARGING):
            self.target_x = cx
            self.target_y = cy
