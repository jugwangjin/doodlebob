"""Windows API wrappers with cross-platform stubs for development."""

import sys
import random
import logging

log = logging.getLogger(__name__)

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes
    import win32gui
    import win32con


# ---------------------------------------------------------------------------
# DPI awareness (must be called before any window creation)
# ---------------------------------------------------------------------------

def enable_dpi_awareness() -> None:
    """Enable per-monitor DPI awareness so the overlay matches actual screen pixels."""
    if not IS_WINDOWS:
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        log.info("DPI awareness: per-monitor")
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            log.info("DPI awareness: system-level")
        except Exception:
            log.warning("Could not set DPI awareness")


# ---------------------------------------------------------------------------
# Click-through overlay
# ---------------------------------------------------------------------------

def make_window_clickthrough(hwnd_int: int) -> None:
    """Make a window click-through by adding only WS_EX_TRANSPARENT.

    Note: tkinter's -transparentcolor already sets WS_EX_LAYERED internally.
    We must NOT re-set WS_EX_LAYERED here or it resets the color-key,
    making the entire window invisible.
    """
    if not IS_WINDOWS:
        log.debug("make_window_clickthrough: no-op on non-Windows")
        return
    GWL_EXSTYLE = -20
    WS_EX_TRANSPARENT = 0x00000020
    style = ctypes.windll.user32.GetWindowLongW(hwnd_int, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(
        hwnd_int, GWL_EXSTYLE, style | WS_EX_TRANSPARENT
    )


# ---------------------------------------------------------------------------
# Cursor visibility
# ---------------------------------------------------------------------------
# Windows ShowCursor uses a reference count; cursor is visible when count >= 0.
# We force-hide by calling ShowCursor(FALSE) until count < 0, and restore by
# calling ShowCursor(TRUE) until count >= 0.

def hide_cursor() -> None:
    """Hide the system cursor (Windows only). Force-hides via ref-count loop."""
    if not IS_WINDOWS:
        log.debug("hide_cursor: no-op on non-Windows")
        return
    ShowCursor = ctypes.windll.user32.ShowCursor
    ShowCursor.argtypes = [wintypes.BOOL]
    ShowCursor.restype = wintypes.INT
    while ShowCursor(0) >= 0:  # FALSE = 0
        pass


def show_cursor() -> None:
    """Show the system cursor (Windows only). Restores visibility via ref-count."""
    if not IS_WINDOWS:
        log.debug("show_cursor: no-op on non-Windows")
        return
    ShowCursor = ctypes.windll.user32.ShowCursor
    ShowCursor.argtypes = [wintypes.BOOL]
    ShowCursor.restype = wintypes.INT
    while ShowCursor(1) < 0:  # TRUE = 1
        pass


def set_cursor_pos(x: int, y: int) -> None:
    """Move the system cursor to (x, y) (Windows only)."""
    if not IS_WINDOWS:
        log.debug("set_cursor_pos(%d, %d): no-op on non-Windows", x, y)
        return
    ctypes.windll.user32.SetCursorPos(x, y)


def get_cursor_pos() -> tuple[int, int]:
    """Get the current cursor position."""
    if IS_WINDOWS:
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y
    else:
        try:
            import tkinter as tk
            root = tk._default_root
            if root:
                return root.winfo_pointerx(), root.winfo_pointery()
        except Exception:
            pass
        return 0, 0


# ---------------------------------------------------------------------------
# Window enumeration & closing
# ---------------------------------------------------------------------------

_EXCLUDED_TITLES = {
    "", "Program Manager", "DoodleBob",
    "Windows Shell Experience Host",
    "Microsoft Text Input Application",
}

_EXCLUDED_CLASSES = {
    "Progman", "WorkerW", "Shell_TrayWnd",
    "Shell_SecondaryTrayWnd", "DV2ControlHost",
    "Windows.UI.Core.CoreWindow",
}


def get_closeable_windows() -> list[tuple[int, str, int, int]]:
    """Return list of (hwnd, title, x_button_x, x_button_y) for closeable windows."""
    if not IS_WINDOWS:
        log.debug("get_closeable_windows: returning empty on non-Windows")
        return []

    results = []

    def _callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if title in _EXCLUDED_TITLES:
            return True
        cls = win32gui.GetClassName(hwnd)
        if cls in _EXCLUDED_CLASSES:
            return True
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x_btn_x = rect[2] - 25
            x_btn_y = rect[1] + 15
            if rect[2] - rect[0] > 50 and rect[3] - rect[1] > 50:
                results.append((hwnd, title, x_btn_x, x_btn_y))
        except Exception:
            pass
        return True

    win32gui.EnumWindows(_callback, None)
    return results


def close_window(hwnd: int) -> None:
    """Send WM_CLOSE to a window (Windows only)."""
    if not IS_WINDOWS:
        log.debug("close_window(%d): no-op on non-Windows", hwnd)
        return
    try:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        log.info("Closed window %d", hwnd)
    except Exception as e:
        log.warning("Failed to close window %d: %s", hwnd, e)


def pick_random_window() -> tuple[int, str, int, int] | None:
    """Pick a random closeable window. Returns (hwnd, title, x, y) or None."""
    windows = get_closeable_windows()
    if not windows:
        return None
    return random.choice(windows)
