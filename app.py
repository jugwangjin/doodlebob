"""DoodleBob Desktop Pet - Main application.

Uses a small floating borderless window that moves with the character,
instead of a full-screen overlay. This avoids all click-through and
transparency issues on Windows multi-monitor setups.
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
from behaviors import WindowCloseBehavior, CursorStealBehavior
from win_api import enable_dpi_awareness, IS_WINDOWS

log = logging.getLogger(__name__)


class DoodleBobApp:
    """Main application: DoodleBob walks across the desktop."""

    def __init__(self, windowed: bool = False):
        self.windowed = windowed
        self.paused = False

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

        self.window_close_behavior = WindowCloseBehavior(self.character)
        self.cursor_steal_behavior = CursorStealBehavior(
            self.character, self.screen_w, self.screen_h,
        )

        atexit.register(self._cleanup)
        self._tray_icon = None
        self._setup_tray()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_floating(self):
        """Small borderless window that follows the character across the desktop.

        -transparentcolor makes the canvas background invisible so only
        the character sprite is visible. No full-screen overlay needed.
        """
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        if IS_WINDOWS:
            self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)

        self.root.config(bg=TRANSPARENT_COLOR)
        self.root.geometry(f"{self.sprite_w}x{self.sprite_h}+100+100")
        log.info("Floating window: %dx%d", self.sprite_w, self.sprite_h)

    def _setup_windowed(self):
        self.root.geometry("800x600+100+100")
        self.root.resizable(False, False)

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
            self.window_close_behavior.update()
            self.cursor_steal_behavior.update()
            self.character.update()

        if not self.windowed:
            wx = int(self.character.x - self.sprite_w // 2)
            wy = int(self.character.y - self.sprite_h // 2)
            try:
                self.root.geometry(f"+{wx}+{wy}")
            except tk.TclError:
                pass

        self.root.after(UPDATE_MS, self._update)

    def run(self):
        log.info("DoodleBob starting! Screen: %dx%d, Windowed: %s",
                 self.screen_w, self.screen_h, self.windowed)
        self.root.after(UPDATE_MS, self._update)
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            log.info("Interrupted by user")
        finally:
            self._cleanup()
