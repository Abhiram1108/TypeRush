"""
TypeRush - Modern Typing Speed Test Application
Release v2.0.0 — Native Python Desktop Application
"""

import sys
import tkinter as tk
from ui.app import TypeRushApp


def enable_windows_dpi_awareness() -> None:
    """
    Enable high-DPI awareness on Windows to ensure crisp rendering
    of typography, canvas elements, and window borders.
    """
    if sys.platform == "win32":
        try:
            import ctypes
            # Try Per-Monitor V2 awareness (Windows 10 1703+)
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                # Fallback to system DPI awareness (Windows Vista+)
                ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main() -> None:
    """Launch the TypeRush application."""
    enable_windows_dpi_awareness()

    app = TypeRushApp()
    app.mainloop()


if __name__ == "__main__":
    main()
