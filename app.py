"""DoodleBob Desktop Pet - Main application."""

from __future__ import annotations

import atexit
import logging
import sys
import threading
import tkinter as tk

from config import TRANSPARENT_COLOR, UPDATE_MS, SPRITE_SCALE
from sprite_gen import ensure_sprites_exist
from character import Character
from behaviors import WindowCloseBehavior, CursorStealBehavior
from win_api import make_window_clickthrough, IS_WINDOWS

log = logging.getLogger(__name__)


class DoodleBobApp:
    """Main application: transparent overlay with DoodleBob character."""

    def __init__(self, windowed: bool = False):
        self.windowed = windowed
        self.paused = False

        # Generate placeholder sprites if needed
        ensure_sprites_exist()

        # Create root window
        self.root = tk.Tk()
        self.root.title("DoodleBob")

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        if windowed:
            self._setup_windowed()
        else:
            self._setup_overlay()

        # Canvas
        canvas_bg = "#333333" if windowed else TRANSPARENT_COLOR
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_w if not windowed else 800,
            height=self.screen_h if not windowed else 600,
            bg=canvas_bg,
            highlightthickness=0,
        )
        self.canvas.pack()

        # Use canvas dimensions for character bounds
        cw = 800 if windowed else self.screen_w
        ch = 600 if windowed else self.screen_h

        # Character
        self.character = Character(self.canvas, cw, ch)

        # Behaviors
        self.window_close_behavior = WindowCloseBehavior(self.character)
        self.cursor_steal_behavior = CursorStealBehavior(self.character, cw, ch)

        # Cleanup on exit
        atexit.register(self._cleanup)

        # System tray icon (optional)
        self._tray_icon = None
        self._setup_tray()

    def _setup_overlay(self):
        """Configure as full-screen transparent always-on-top overlay."""
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        if IS_WINDOWS:
            self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
            self.root.config(bg=TRANSPARENT_COLOR)
            # Need to wait for window to be mapped before setting click-through
            self.root.after(100, self._make_clickthrough)
        else:
            # On Linux/Mac, -transparentcolor isn't supported
            # Use a dark background to at least show the character
            self.root.config(bg=TRANSPARENT_COLOR)
            try:
                self.root.wm_attributes("-alpha", 0.9)
            except tk.TclError:
                pass

    def _setup_windowed(self):
        """Configure as a normal windowed mode for testing."""
        self.root.geometry("800x600+100+100")
        self.root.resizable(False, False)

    def _make_clickthrough(self):
        """Make the overlay window click-through on Windows."""
        if IS_WINDOWS:
            try:
                import ctypes
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if hwnd == 0:
                    hwnd = self.root.winfo_id()
                make_window_clickthrough(hwnd)
                log.info("Overlay set to click-through")
            except Exception as e:
                log.warning("Failed to set click-through: %s", e)

    def _setup_tray(self):
        """Set up system tray icon for quitting/pausing."""
        try:
            import pystray
            from PIL import Image, ImageDraw

            # Create a simple tray icon
            icon_img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_img)
            draw.rectangle((8, 8, 56, 56), fill=(245, 240, 230), outline=(0, 0, 0), width=3)
            draw.ellipse((18, 16, 32, 30), fill=(245, 240, 230), outline=(0, 0, 0), width=2)
            draw.ellipse((34, 14, 46, 26), fill=(245, 240, 230), outline=(0, 0, 0), width=2)
            draw.arc((20, 32, 44, 48), 0, 180, fill=(0, 0, 0), width=2)

            menu = pystray.Menu(
                pystray.MenuItem(
                    "Pause / Resume",
                    self._toggle_pause,
                ),
                pystray.MenuItem("Quit", self._quit_from_tray),
            )

            self._tray_icon = pystray.Icon("DoodleBob", icon_img, "DoodleBob", menu)
            tray_thread = threading.Thread(target=self._tray_icon.run, daemon=True)
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

    def _update(self):
        """Main update loop called every UPDATE_MS milliseconds."""
        if not self.paused:
            self.window_close_behavior.update()
            self.cursor_steal_behavior.update()
            self.character.update()

        self.root.after(UPDATE_MS, self._update)

    def run(self):
        """Start the application."""
        log.info("DoodleBob starting! Screen: %dx%d, Windowed: %s",
                 self.screen_w, self.screen_h, self.windowed)
        self.root.after(UPDATE_MS, self._update)

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            log.info("Interrupted by user")
        finally:
            self._cleanup()
