"""DoodleBob behaviors: cursor stealing, screen doodling, and action scheduling."""

from __future__ import annotations

import logging
import random
import time

from config import (
    WINDOW_CLOSE_MIN_DELAY_S, WINDOW_CLOSE_MAX_DELAY_S,
    CURSOR_STEAL_MIN_DELAY_S, CURSOR_STEAL_MAX_DELAY_S,
    LURK_DURATION_S,
    DOODLE_MIN_DELAY_S, DOODLE_MAX_DELAY_S,
    DOODLE_DRAW_DURATION_S, DOODLE_FADE_DURATION_S,
    DOODLE_LINE_COUNT,
)
from character import Character, State
from win_api import (
    pick_random_window, close_window,
    hide_cursor, show_cursor, set_cursor_pos, get_cursor_pos,
    IS_WINDOWS,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Window Close Behavior
# ---------------------------------------------------------------------------

class WindowCloseBehavior:
    """Walks DoodleBob to a random window's X button and closes it."""

    def __init__(self, character: Character):
        self.character = character
        self.active = False
        self.available = IS_WINDOWS
        self._on_complete: callable = None

    @property
    def delay_range(self) -> tuple[float, float]:
        return WINDOW_CLOSE_MIN_DELAY_S, WINDOW_CLOSE_MAX_DELAY_S

    def trigger(self, on_complete: callable = None):
        self._on_complete = on_complete
        if not self.available:
            log.debug("WindowClose: not available on this platform")
            self._finish()
            return
        target = pick_random_window()
        if target is None:
            log.debug("WindowClose: no closeable windows found")
            self._finish()
            return
        hwnd, title, x_btn_x, x_btn_y = target
        log.info("WindowClose: targeting '%s' at (%d, %d)", title, x_btn_x, x_btn_y)
        self.active = True

        def on_reached():
            def on_press_done():
                close_window(hwnd)
                log.info("WindowClose: closed '%s'", title)
                self.character.return_to_wander()
                self._finish()
            self.character.start_pencil_press(on_press_done)

        self.character.start_approach_window(hwnd, x_btn_x, x_btn_y, on_reached)

    def update(self):
        pass

    def cancel(self):
        if self.active:
            self.active = False
            self.character.return_to_wander()
            self._finish()

    def _finish(self):
        self.active = False
        if self._on_complete:
            cb = self._on_complete
            self._on_complete = None
            cb()


# ---------------------------------------------------------------------------
# Cursor Steal Behavior (with lurking phase)
# ---------------------------------------------------------------------------

class CursorStealBehavior:
    """Chases the cursor, 'erases' it, and 'redraws' it elsewhere.

    Lurking phase: play lurk (glowing eyes) at current position, then charge at cursor.
    """

    def __init__(self, character: Character, screen_w: int, screen_h: int,
                 region_left: int = 0, region_top: int = 0):
        self.character = character
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.region_left = region_left
        self.region_top = region_top
        self.active = False
        self.available = True
        self._cursor_hidden = False
        self._redraw_x = 0
        self._redraw_y = 0
        self._on_complete: callable = None

    def _cursor_pos_in_region(self) -> tuple[int, int]:
        """Return current cursor position in region coordinates (clamped to region)."""
        cx, cy = get_cursor_pos()
        rx = max(0, min(self.screen_w, cx - self.region_left))
        ry = max(0, min(self.screen_h, cy - self.region_top))
        return rx, ry

    @property
    def delay_range(self) -> tuple[float, float]:
        return CURSOR_STEAL_MIN_DELAY_S, CURSOR_STEAL_MAX_DELAY_S

    def trigger(self, on_complete: callable = None):
        """Start the cursor steal sequence: lurk at current position, then charge at cursor."""
        self._on_complete = on_complete
        self.active = True

        def on_lurk_done():
            cx, cy = self._cursor_pos_in_region()
            log.info("CursorSteal: charging at cursor (%d, %d)", cx, cy)
            self.character.start_lurk_charge(cx, cy, self._on_caught)

        log.info("CursorSteal: lurking at current position (eyes glowing)")
        self.character.start_lurk_wait(LURK_DURATION_S, on_lurk_done)

    def update(self):
        """Mid-action per-frame update: keep updating cursor target while chasing; keep cursor hidden until draw done."""
        if not self.active:
            return
        if self._cursor_hidden:
            hide_cursor()
            set_cursor_pos(-10000, -10000)  # off-screen so even if Windows shows cursor, user won't see it
        if self.character.state in (State.CHASING_CURSOR, State.LURK_CHARGING):
            cx, cy = self._cursor_pos_in_region()
            self.character.update_cursor_target(cx, cy)

    def _on_caught(self):
        log.info("CursorSteal: caught cursor, starting erase")
        hide_cursor()
        self._cursor_hidden = True
        self.character.start_erase(self._on_erase_done)

    def _on_erase_done(self):
        log.info("CursorSteal: erase done, walking to new draw position")
        self._redraw_x = random.randint(50, self.screen_w - 50)
        self._redraw_y = random.randint(50, self.screen_h - 50)
        self.character.start_walk_to_draw(
            self._redraw_x, self._redraw_y, self._on_reached_draw_pos,
        )

    def _on_reached_draw_pos(self):
        log.info("CursorSteal: reached draw position, drawing cursor")
        hide_cursor()  # keep hidden during draw; only show in on_draw_done

        def on_draw_done():
            log.info("CursorSteal: draw done, restoring cursor at (%d, %d)",
                     self._redraw_x, self._redraw_y)
            self._cursor_hidden = False  # do first so this frame's update() won't call hide_cursor()
            set_cursor_pos(self._redraw_x + self.region_left, self._redraw_y + self.region_top)
            show_cursor()  # only place we show; do not call hide_cursor() before or after
            self.character.return_to_wander()
            self._finish()

        self.character.start_draw(on_draw_done)

    def cancel(self):
        """Cancel the active cursor steal action."""
        if self.active:
            if self._cursor_hidden:
                show_cursor()
                self._cursor_hidden = False
            self.active = False
            self.character.return_to_wander()
            self._finish()

    def _finish(self):
        self.active = False
        if self._on_complete:
            cb = self._on_complete
            self._on_complete = None
            cb()

    def keep_cursor_hidden_if_needed(self):
        """Call once per frame (e.g. at end of update loop) to re-apply hide; counters Windows showing cursor mid-frame.
        Only touch cursor while action is still active — after draw done we set active=False and must not touch cursor."""
        if not self.active or not self._cursor_hidden:
            return
        hide_cursor()
        set_cursor_pos(-10000, -10000)

    def cleanup(self):
        """Ensure cursor is visible when app exits."""
        if self._cursor_hidden:
            show_cursor()
            self._cursor_hidden = False


# ---------------------------------------------------------------------------
# Screen Doodle Behavior
# ---------------------------------------------------------------------------

class ScreenDoodleBehavior:
    """DoodleBob draws messy scribbles on the screen with the magic pencil.
    Only produces visual doodle lines in windowed mode.
    """

    def __init__(self, character: Character, canvas, windowed: bool):
        self.character = character
        self.canvas = canvas
        self.windowed = windowed
        self.active = False
        self.available = True
        self._on_complete: callable = None
        self._doodle_items: list[tuple[int, float]] = []  # (canvas_id, expire_time)

    @property
    def delay_range(self) -> tuple[float, float]:
        return DOODLE_MIN_DELAY_S, DOODLE_MAX_DELAY_S

    def trigger(self, on_complete: callable = None):
        """Start the screen doodle sequence."""
        self._on_complete = on_complete
        self.active = True

        tx = random.randint(150, self.character.screen_w - 150)
        ty = random.randint(150, self.character.screen_h - 150)
        log.info("ScreenDoodle: walking to (%d, %d) to doodle", tx, ty)

        def on_reached():
            log.info("ScreenDoodle: starting doodle animation")
            if self.windowed:
                self._create_doodle_lines()

            def on_doodle_done():
                log.info("ScreenDoodle: doodle done, returning to wander")
                self.character.return_to_wander()
                self._finish()

            self.character.start_doodle(on_doodle_done)

        self.character.start_walk_to_draw(tx, ty, on_reached)

    def _create_doodle_lines(self):
        """Draw random scribble lines on the canvas near the character."""
        cx, cy = int(self.character.x), int(self.character.y)
        expire = time.time() + DOODLE_DRAW_DURATION_S + DOODLE_FADE_DURATION_S
        colors = ["#CCCC44", "#DDDD55", "#BBBB33", "#AAAA22"]
        for _ in range(DOODLE_LINE_COUNT):
            points = []
            x, y = cx + random.randint(-20, 20), cy + random.randint(-20, 20)
            for _ in range(random.randint(4, 10)):
                x += random.randint(-40, 40)
                y += random.randint(-40, 40)
                points.extend([x, y])
            if len(points) >= 4:
                item_id = self.canvas.create_line(
                    *points, fill=random.choice(colors),
                    width=random.choice([1, 2, 3]), smooth=True,
                )
                self._doodle_items.append((item_id, expire))

    def update(self):
        """Per-frame: manage fading of doodle lines."""
        now = time.time()
        remaining = []
        for item_id, expire_time in self._doodle_items:
            time_left = expire_time - now
            if time_left <= 0:
                self.canvas.delete(item_id)
            elif time_left < DOODLE_FADE_DURATION_S:
                frac = time_left / DOODLE_FADE_DURATION_S
                if frac < 0.33:
                    self.canvas.itemconfig(item_id, fill="#444444")
                elif frac < 0.66:
                    self.canvas.itemconfig(item_id, fill="#666633")
                remaining.append((item_id, expire_time))
            else:
                remaining.append((item_id, expire_time))
        self._doodle_items = remaining

    def cancel(self):
        if self.active:
            self.active = False
            for item_id, _ in self._doodle_items:
                self.canvas.delete(item_id)
            self._doodle_items.clear()
            self.character.return_to_wander()
            self._finish()

    def _finish(self):
        self.active = False
        if self._on_complete:
            cb = self._on_complete
            self._on_complete = None
            cb()


# ---------------------------------------------------------------------------
# Action Scheduler — random action selection
# ---------------------------------------------------------------------------

class ActionScheduler:
    """Unified scheduler that randomly picks between available actions.

    After each action completes, a new action is randomly selected with
    the chosen action's delay range.
    """

    def __init__(self, character: Character, behaviors: list):
        self.character = character
        self.behaviors = behaviors  # list of behavior instances
        self._next_trigger: float = 0
        self._next_behavior = None
        self._current_behavior = None
        self._schedule_next()

    def _schedule_next(self):
        available = [b for b in self.behaviors if b.available]
        if not available:
            self._next_trigger = time.time() + 5
            return

        chosen = random.choice(available)
        min_d, max_d = chosen.delay_range
        delay = random.uniform(min_d, max_d)
        self._next_trigger = time.time() + delay
        self._next_behavior = chosen
        log.info("ActionScheduler: next=%s in %.1fs",
                 type(chosen).__name__, delay)

    def update(self):
        """Called every frame. Manages behavior updates and scheduling."""
        # Update all behaviors (for mid-action tracking)
        for b in self.behaviors:
            b.update()

        # If an action is active, wait for it to finish
        if self._current_behavior and self._current_behavior.active:
            return

        # Action just finished
        if self._current_behavior and not self._current_behavior.active:
            self._current_behavior = None
            self._schedule_next()
            return

        # Wait for timer
        if time.time() < self._next_trigger:
            return

        # Character must be idle or wandering
        if self.character.state not in (State.IDLE, State.WANDERING):
            return

        # Character must not be walking to a lurk position
        if self.character.target_x is not None:
            return

        # Trigger the chosen action
        if self._next_behavior:
            self._current_behavior = self._next_behavior
            self._next_behavior = None
            log.info("ActionScheduler: triggering %s",
                     type(self._current_behavior).__name__)
            self._current_behavior.trigger(on_complete=self._on_action_complete)

    def _on_action_complete(self):
        """Called when the current action finishes."""
        self._current_behavior = None
        self._schedule_next()

    def force_trigger(self, behavior):
        """Force trigger a specific behavior immediately."""
        # Cancel current action if any
        if self._current_behavior and self._current_behavior.active:
            self._current_behavior.cancel()
            self._current_behavior = None

        # Also ensure character is in a safe state
        if self.character.state not in (State.IDLE, State.WANDERING):
            self.character.return_to_wander()

        self._current_behavior = behavior
        behavior.trigger(on_complete=self._on_action_complete)

    def stop_current(self):
        """Stop the current action and return to wandering."""
        if self._current_behavior and self._current_behavior.active:
            log.info("ActionScheduler: stopping %s",
                     type(self._current_behavior).__name__)
            self._current_behavior.cancel()
            self._current_behavior = None

        if self.character.state not in (State.IDLE, State.WANDERING):
            self.character.return_to_wander()

        self._schedule_next()
