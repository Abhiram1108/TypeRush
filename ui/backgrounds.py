"""
TypeRush 2.1 — Clean Minimal Background Architecture (ui/backgrounds.py)

Single unified dark background rendering for the Midnight Minimal visual identity.
Replaces mountain imagery and radial atmospheric glows with clean, distraction-free
solid surfaces (#0B0D12) and native glass-inspired layering.

Features:
- Solid dark canvas (#0B0D12).
- Zero disk reads during typing.
- Backwards-compatible API for existing screens and tests.
"""

import tkinter as tk
from typing import Dict, Optional, Tuple, Any
from ui import theme


class BackgroundCache:
    """Compatibility image cache (No-op in Midnight Minimal)."""
    _images: Dict[Tuple[int, str], tk.PhotoImage] = {}

    @classmethod
    def get_image(cls, relative_path: str, master: Optional[tk.Widget] = None) -> Optional[tk.PhotoImage]:
        return None

    @classmethod
    def clear(cls) -> None:
        cls._images.clear()


class ScreenBackground(tk.Canvas):
    """
    Clean solid dark canvas component providing the foundational surface
    for all application screens under the Midnight Minimal design system.
    """

    def __init__(
        self,
        master: tk.Widget,
        screen_name: str = "home",
        edition: str = "midnight_minimal",
        **kwargs
    ):
        super().__init__(
            master,
            bg=theme.BG_PRIMARY,
            bd=0,
            highlightthickness=0,
            **kwargs
        )
        self.screen_name = screen_name
        self.edition = "midnight_minimal"
        self._width = master.winfo_width() or theme.WINDOW_DEFAULT_WIDTH
        self._height = master.winfo_height() or theme.WINDOW_DEFAULT_HEIGHT

        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event: tk.Event) -> None:
        if event.width > 10 and event.height > 10:
            if (event.width, event.height) != (self._width, self._height):
                self._width = event.width
                self._height = event.height
                self.render_background()

    def set_edition(self, edition: str) -> None:
        """Compatibility method for legacy edition switches."""
        self.edition = "midnight_minimal"
        self.render_background()

    def refresh(self) -> None:
        """Refresh background canvas."""
        self.render_background()

    def render_background(self) -> None:
        """Render solid minimal background surface."""
        self.delete("all")
