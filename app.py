"""DoodleBob Desktop Pet - Main application.

Uses a small floating borderless window that moves with the character,
instead of a full-screen overlay. This avoids all click-through and
transparency issues on Windows multi-monitor setups.

Keyboard Controls:
    C — Force cursor steal (with lurking)
    W — Force window close (walk to random window X button)
    D — Force screen doodle
    S — Stop current action (return to wandering)
    B — Toggle behaviors on/off (off = only wander)
    Space — Pause / Resume
    Escape or Q — Close app (quit)
"""

from __future__ import annotations

import atexit
import logging
import sys
import threading
import tkinter as tk

from config import TRANSPARENT_COLOR, UPDATE_MS, SPRITE_SCALE, CHAR_BASE_W, CHAR_BASE_H
from sprite_gen import ensure_sprites_exist
from character import Character
from behaviors import (
    WindowCloseBehavior, CursorStealBehavior, ScreenDoodleBehavior,
    ActionScheduler,
)
from win_api import enable_dpi_awareness, IS_WINDOWS

log = logging.getLogger(__name__)


class DoodleBobApp:
    """Main application: DoodleBob walks across the desktop."""

    def __init__(self, windowed: bool = False):
        self.windowed = windowed
        self.paused = False
        self.behaviors_enabled = True  # False = only wander

        enable_dpi_awareness()
        ensure_sprites_exist()

        self.root = tk.Tk()
        self.root.title("DoodleBob")

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        self.sprite_w = CHAR_BASE_W * SPRITE_SCALE
        self.sprite_h = CHAR_BASE_H * SPRITE_SCALE

        if windowed:
            self._setup_windowed()
        else:
            self._setup_floating()

        canvas_w = 800 if windowed else self.sprite_w
        canvas_h = 600 if windowed else self.sprite_h
        canvas_bg = "#333333" if windowed else TRANSPARENT_COLOR

        self.canvas = tk.Canvas(
            self.root, width=canvas_w, height=canvas_h,
            bg=canvas_bg, highlightthickness=0,
        )
        self.canvas.pack()

        self.character = Character(
            self.canvas,
            screen_w=self.screen_w,
            screen_h=self.screen_h,
            floating=not windowed,
        )

        # Behaviors: window close, cursor steal, screen doodle
        self.window_close_behavior = WindowCloseBehavior(self.character)
        self.cursor_steal_behavior = CursorStealBehavior(
            self.character, self.screen_w, self.screen_h, 0, 0,
        )
        self.screen_doodle_behavior = ScreenDoodleBehavior(
            self.character, self.canvas, windowed,
        )
        self.scheduler = ActionScheduler(
            self.character,
            [
                self.window_close_behavior,
                self.cursor_steal_behavior,
                self.screen_doodle_behavior,
            ],
        )

        # Keyboard bindings
        self._bind_keys()

        atexit.register(self._cleanup)
        self._tray_icon = None
        self._setup_tray()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_floating(self):
        """Small borderless window that follows the character across the full screen."""
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        if IS_WINDOWS:
            self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

        self.root.config(bg=TRANSPARENT_COLOR)
        self.root.geometry(f"{self.sprite_w}x{self.sprite_h}+100+100")
        log.info("Floating window: %dx%d (full screen)", self.sprite_w, self.sprite_h)

    def _setup_windowed(self):
        self.root.geometry("800x600+100+100")
        self.root.resizable(False, False)

    # ------------------------------------------------------------------
    # Keyboard controls
    # ------------------------------------------------------------------

    def _bind_keys(self):
        """Bind keys on both root and canvas, and use bind_all so keys work without focus."""
        for widget in (self.root, self.canvas):
            widget.bind("<KeyPress-c>", self._key_cursor_steal)
            widget.bind("<KeyPress-w>", self._key_window_close)
            widget.bind("<KeyPress-d>", self._key_doodle)
            widget.bind("<KeyPress-s>", self._key_stop)
            widget.bind("<KeyPress-b>", self._key_toggle_behaviors)
            widget.bind("<space>", self._key_pause)
            widget.bind("<Escape>", self._key_quit)
            widget.bind("<KeyPress-q>", self._key_quit)
        self.root.focus_set()
        self.canvas.focus_set()
        self.root.bind_all("<KeyPress-c>", self._key_cursor_steal)
        self.root.bind_all("<KeyPress-w>", self._key_window_close)
        self.root.bind_all("<KeyPress-d>", self._key_doodle)
        self.root.bind_all("<KeyPress-s>", self._key_stop)
        self.root.bind_all("<KeyPress-b>", self._key_toggle_behaviors)
        self.root.bind_all("<space>", self._key_pause)
        self.root.bind_all("<Escape>", self._key_quit)
        self.root.bind_all("<KeyPress-q>", self._key_quit)
        log.info("Keyboard bindings: C=cursor steal, W=window close, D=doodle, S=stop, B=behaviors, Space=pause, Esc/Q=quit")

    def _key_cursor_steal(self, event=None):
        if self.paused or not self.behaviors_enabled:
            return
        log.info("Key: force cursor steal")
        self.scheduler.force_trigger(self.cursor_steal_behavior)
        return "break"

    def _key_window_close(self, event=None):
        if self.paused or not self.behaviors_enabled:
            return
        log.info("Key: force window close")
        self.scheduler.force_trigger(self.window_close_behavior)
        return "break"

    def _key_doodle(self, event=None):
        if self.paused or not self.behaviors_enabled:
            return
        log.info("Key: force screen doodle")
        self.scheduler.force_trigger(self.screen_doodle_behavior)
        return "break"

    def _key_stop(self, event=None):
        log.info("Key: stop current action")
        self.scheduler.stop_current()
        return "break"

    def _key_toggle_behaviors(self, event=None):
        if self.paused:
            return
        self.behaviors_enabled = not self.behaviors_enabled
        if not self.behaviors_enabled:
            self.scheduler.stop_current()
        log.info("Behaviors %s", "on" if self.behaviors_enabled else "off (wander only)")
        return "break"

    def _key_pause(self, event=None):
        self._toggle_pause()
        return "break"

    def _key_quit(self, event=None):
        log.info("Key: close window")
        self._cleanup()
        self.root.quit()
        self.root.destroy()
        return "break"

    # ------------------------------------------------------------------
    # System tray
    # ------------------------------------------------------------------

    def _setup_tray(self):
        try:
            import pystray
            from PIL import Image, ImageDraw

            icon_img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_img)
            draw.rectangle((8, 8, 56, 56), fill=(245, 240, 230),
                           outline=(0, 0, 0), width=3)
            draw.ellipse((18, 16, 32, 30), fill=(245, 240, 230),
                         outline=(0, 0, 0), width=2)
            draw.ellipse((34, 14, 46, 26), fill=(245, 240, 230),
                         outline=(0, 0, 0), width=2)
            draw.arc((20, 32, 44, 48), 0, 180, fill=(0, 0, 0), width=2)

            menu = pystray.Menu(
                pystray.MenuItem("Pause / Resume", self._toggle_pause),
                pystray.MenuItem("Quit", self._quit_from_tray),
            )
            self._tray_icon = pystray.Icon("DoodleBob", icon_img,
                                           "DoodleBob", menu)
            tray_thread = threading.Thread(target=self._tray_icon.run,
                                          daemon=True)
            tray_thread.start()
            log.info("System tray icon created")
        except ImportError:
            log.info("pystray not available; use Ctrl+C or task manager to quit")
        except Exception as e:
            log.warning("Failed to create tray icon: %s", e)

    def _toggle_pause(self, icon=None, item=None):
        self.paused = not self.paused
        log.info("Paused: %s", self.paused)

    def _quit_from_tray(self, icon=None, item=None):
        self._cleanup()
        self.root.after(0, self.root.destroy)

    def _cleanup(self):
        self.cursor_steal_behavior.cleanup()
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def _update(self):
        if not self.paused:
            if self.behaviors_enabled:
                self.scheduler.update()
            self.character.update()

        if not self.windowed:
            wx = int(self.character.x - self.sprite_w // 2)
            wy = int(self.character.y - self.sprite_h // 2)
            try:
                self.root.geometry(f"+{wx}+{wy}")
            except tk.TclError:
                pass

        self.cursor_steal_behavior.keep_cursor_hidden_if_needed()
        self.root.after(UPDATE_MS, self._update)

    def run(self):
        log.info("DoodleBob starting! Screen: %dx%d, Windowed: %s",
                 self.screen_w, self.screen_h, self.windowed)
        log.info("Controls: C=cursor steal, W=window close, D=doodle, S=stop, B=behaviors, Space=pause, Esc/Q=quit")
        self.root.after(UPDATE_MS, self._update)
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            log.info("Interrupted by user")
        finally:
            self._cleanup()
