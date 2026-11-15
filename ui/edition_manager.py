"""
TypeRush 2.1 Unified Edition & Theme Manager (ui/edition_manager.py)

Refactored to support the single unified Midnight Minimal visual identity.
Maintains backwards-compatible interfaces for legacy tests and references,
while redirecting all theme and color requests to Midnight Minimal tokens.
"""

from typing import Dict, Any, List, Callable, Optional
from ui import storage, theme


class Edition:
    MIDNIGHT_MINIMAL = "midnight_minimal"
    PLEASANT = "pleasant"
    BASIC = "basic"
    SOUNDSCAPE = "soundscape"

    ALL = [MIDNIGHT_MINIMAL, PLEASANT, BASIC, SOUNDSCAPE]
    DISPLAY_NAMES = {
        MIDNIGHT_MINIMAL: "Midnight Minimal",
        PLEASANT: "Midnight Minimal",
        BASIC: "Midnight Minimal",
        SOUNDSCAPE: "Midnight Minimal",
    }


# All profiles map to Midnight Minimal
_UNIFIED_PALETTE = {
    "bg_main": theme.BG_PRIMARY,
    "bg_secondary": theme.BG_SECONDARY,
    "bg_card": theme.SURFACE_DEFAULT,
    "bg_surface": theme.SURFACE_ELEVATED,
    "bg_surface_hover": theme.SURFACE_HOVER,
    "accent_primary": theme.ACCENT_PRIMARY,
    "accent_secondary": theme.ACCENT_SECONDARY,
    "accent_subtle": theme.ACCENT_SUBTLE,
    "border_color": theme.BORDER_SUBTLE,
    "border_subtle": theme.BORDER_MUTED,
    "text_primary": theme.TEXT_PRIMARY,
    "text_secondary": theme.TEXT_SECONDARY,
    "text_muted": theme.TEXT_MUTED,
    "caret_color": theme.ACCENT_PRIMARY,
    "has_mountains": "false",
    "has_radial": "false",
}

EDITION_THEMES: Dict[str, Dict[str, str]] = {
    Edition.MIDNIGHT_MINIMAL: _UNIFIED_PALETTE,
    Edition.PLEASANT: _UNIFIED_PALETTE,
    Edition.BASIC: _UNIFIED_PALETTE,
    Edition.SOUNDSCAPE: _UNIFIED_PALETTE,
}


class EditionManager:
    """
    Unified manager ensuring consistent Midnight Minimal visual identity
    and simple optional audio preference management.
    """

    def __init__(self, animation_manager: Optional[Any] = None):
        self.animation_manager = animation_manager
        self._listeners: List[Callable[[str, str, Dict[str, str]], None]] = []

        settings = storage.load_settings()
        self.current_edition = Edition.MIDNIGHT_MINIMAL

        sound_pref = settings.get("sound_enabled")
        if sound_pref is not None:
            self._user_sound_preference: Optional[bool] = bool(sound_pref)
        else:
            self._user_sound_preference = False

    def get_current_edition(self) -> str:
        """Return the active unified theme identifier."""
        return self.current_edition

    def get_display_name(self, edition: Optional[str] = None) -> str:
        """Return human-readable edition name."""
        return "Midnight Minimal"

    def get_theme_colors(self, edition: Optional[str] = None) -> Dict[str, str]:
        """Return color dictionary for unified Midnight Minimal design."""
        return _UNIFIED_PALETTE

    def is_sound_enabled(self) -> bool:
        """
        Evaluate user sound preference without arbitrary edition restrictions.
        """
        if self._user_sound_preference is not None:
            return self._user_sound_preference
        return False

    def set_sound_preference(self, enabled: bool) -> None:
        """Set and persist user's explicit sound preference."""
        self._user_sound_preference = enabled
        settings = storage.load_settings()
        settings["sound_enabled"] = enabled
        storage.save_settings(settings)

    def subscribe(self, callback: Callable[[str, str, Dict[str, str]], None]) -> None:
        """Subscribe listener callback."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unsubscribe(self, callback: Callable[[str, str, Dict[str, str]], None]) -> None:
        """Unsubscribe listener callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def set_edition(self, new_edition: str, animate: bool = True) -> None:
        """
        Compatibility setter for edition changes.
        """
        old_edition = self.current_edition
        self.current_edition = new_edition

        # Safely notify any registered listeners
        new_colors = self.get_theme_colors(new_edition)
        for listener in list(self._listeners):
            try:
                listener(new_edition, old_edition, new_colors)
            except Exception:
                pass
