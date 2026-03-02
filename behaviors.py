"""DoodleBob behaviors: window closing and cursor stealing."""

from __future__ import annotations

import logging
import random
import time

from config import (
    WINDOW_CLOSE_MIN_DELAY_S, WINDOW_CLOSE_MAX_DELAY_S,
    CURSOR_STEAL_MIN_DELAY_S, CURSOR_STEAL_MAX_DELAY_S,
    CURSOR_HIDE_DURATION_S,
)
from character import Character, State
from win_api import (
    pick_random_window, close_window,
    hide_cursor, show_cursor, set_cursor_pos, get_cursor_pos,
    IS_WINDOWS,
)

log = logging.getLogger(__name__)


class WindowCloseBehavior:
    """Periodically walks DoodleBob to a random window's X button and closes it."""

    def __init__(self, character: Character):
        self.character = character
        self.active = False
        self.enabled = IS_WINDOWS  # Only works on Windows (requires win32gui)
        self._schedule_next()

    def _schedule_next(self):
        delay = random.uniform(WINDOW_CLOSE_MIN_DELAY_S, WINDOW_CLOSE_MAX_DELAY_S)
        self._next_trigger = time.time() + delay
        self.active = False
        log.info("WindowClose: next trigger in %.1fs", delay)

    def update(self):
        if not self.enabled:
            return

        if self.active:
            return

        if self.character.state not in (State.IDLE, State.WANDERING):
            return

        if time.time() < self._next_trigger:
            return

        target = pick_random_window()
        if target is None:
            log.debug("WindowClose: no closeable windows found, retrying later")
            self._next_trigger = time.time() + 5
            return

        hwnd, title, x_btn_x, x_btn_y = target
        log.info("WindowClose: targeting '%s' at (%d, %d)", title, x_btn_x, x_btn_y)
        self.active = True

        def on_reached():
            def on_press_done():
                close_window(hwnd)
                log.info("WindowClose: closed '%s'", title)
                self.character.return_to_wander()
                self._schedule_next()
            self.character.start_pencil_press(on_press_done)

        self.character.start_approach_window(hwnd, x_btn_x, x_btn_y, on_reached)


class CursorStealBehavior:
    """Periodically chases the cursor, 'erases' it, and 'redraws' it elsewhere."""

    def __init__(self, character: Character, screen_w: int, screen_h: int):
        self.character = character
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.active = False
        self._cursor_hidden = False
        self._redraw_x = 0
        self._redraw_y = 0
        self.enabled = True
        self._schedule_next()

    def _schedule_next(self):
        delay = random.uniform(CURSOR_STEAL_MIN_DELAY_S, CURSOR_STEAL_MAX_DELAY_S)
        self._next_trigger = time.time() + delay
        self.active = False
        log.info("CursorSteal: next trigger in %.1fs", delay)

    def update(self):
        if not self.enabled:
            return

        if self.active:
            # Keep updating cursor target while chasing
            if self.character.state == State.CHASING_CURSOR:
                cx, cy = get_cursor_pos()
                self.character.update_cursor_target(cx, cy)
            return

        if self.character.state not in (State.IDLE, State.WANDERING):
            return

        if time.time() < self._next_trigger:
            return

        cx, cy = get_cursor_pos()
        log.info("CursorSteal: chasing cursor at (%d, %d)", cx, cy)
        self.active = True

        def on_caught():
            log.info("CursorSteal: caught cursor, starting erase")
            hide_cursor()
            self._cursor_hidden = True
            self.character.start_erase(self._on_erase_done)

        self.character.start_chase_cursor(cx, cy, on_caught)

    def _on_erase_done(self):
        log.info("CursorSteal: erase done, walking to new draw position")
        self._redraw_x = random.randint(50, self.screen_w - 50)
        self._redraw_y = random.randint(50, self.screen_h - 50)
        self.character.start_walk_to_draw(
            self._redraw_x, self._redraw_y, self._on_reached_draw_pos,
        )

    def _on_reached_draw_pos(self):
        log.info("CursorSteal: reached draw position, drawing cursor")

        def on_draw_done():
            log.info("CursorSteal: draw done, restoring cursor at (%d, %d)",
                     self._redraw_x, self._redraw_y)
            set_cursor_pos(self._redraw_x, self._redraw_y)
            show_cursor()
            self._cursor_hidden = False
            self.character.return_to_wander()
            self._schedule_next()

        self.character.start_draw(on_draw_done)

    def cleanup(self):
        """Ensure cursor is visible when app exits."""
        if self._cursor_hidden:
            show_cursor()
            self._cursor_hidden = False
