"""
Base screen class for all TypeRush application screens.
"""

from typing import TYPE_CHECKING, Optional, Dict
import tkinter as tk
from ui import theme
from ui.backgrounds import ScreenBackground

if TYPE_CHECKING:
    from ui.app import TypeRushApp


class BaseScreen(tk.Frame):
    """
    Abstract base screen providing lifecycle hooks, background integration,
    and navigation references.
    """
    SCREEN_NAME = "base"

    def __init__(self, parent: tk.Widget, app: "TypeRushApp", **kwargs):
        super().__init__(parent, bg=theme.BG_PRIMARY, **kwargs)
        self.app = app
        self.bg_canvas: Optional[ScreenBackground] = None

    def setup_background(self, screen_name: Optional[str] = None) -> ScreenBackground:
        """Initialize and attach responsive atmospheric background canvas."""
        name = screen_name or self.SCREEN_NAME
        curr_ed = self.app.edition_manager.get_current_edition() if hasattr(self.app, "edition_manager") else "pleasant"
        self.bg_canvas = ScreenBackground(self, screen_name=name, edition=curr_ed)
        self.bg_canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)

        # Subscribe to edition manager
        if hasattr(self.app, "edition_manager"):
            self.app.edition_manager.subscribe(self._on_edition_changed_bg)
        return self.bg_canvas

    def _on_edition_changed_bg(self, new_ed: str, old_ed: str, colors: Dict[str, str]) -> None:
        """Handle edition change event by refreshing background."""
        if self.bg_canvas:
            self.bg_canvas.set_edition(new_ed)

    def on_show(self, **kwargs) -> None:
        """Called whenever the screen becomes visible with optional route payload."""
        if self.bg_canvas:
            self.bg_canvas.refresh()

    def on_hide(self) -> None:
        """Called whenever the screen is navigated away from."""
        pass
