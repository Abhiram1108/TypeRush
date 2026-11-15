"""
TypeRush 2.0 Global Animation System

Provides central, reusable, non-blocking animations across the application:
1. Screen Navigation Transition: Smooth directional sliding/fade of screen frames.
2. Edition Switching Transition: Smooth background and accent color interpolation.
3. Caret Movement Animation: Responsive positional interpolation of the typing caret.
4. Button Hover & Press Feedback: Subtle micro-transitions.
5. Reduced-Motion Support: Instant completion when accessibility mode is enabled.

Technical Guarantees:
- Strictly uses Tkinter's `after()` scheduler (~60 FPS / 16ms steps).
- Zero `time.sleep()` calls; main GUI and keyboard event loop are never blocked.
- Automatic cancellation of obsolete callbacks on rapid navigation.
- No widget recreation, memory leaks, or runaway animation tasks.
"""

import time
import tkinter as tk
from typing import Callable, Dict, Optional, Tuple, List, Any


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Convert hex color string ('#RRGGBB') to RGB tuple."""
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join([c * 2 for c in hex_code])
    if len(hex_code) != 6:
        return (0, 0, 0)
    return (
        int(hex_code[0:2], 16),
        int(hex_code[2:4], 16),
        int(hex_code[4:6], 16),
    )


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string ('#RRGGBB')."""
    r, g, b = [max(0, min(255, int(v))) for v in rgb]
    return f"#{r:02x}{g:02x}{b:02x}"


def interpolate_color(start_hex: str, end_hex: str, progress: float) -> str:
    """Linearly interpolate between two hex color codes."""
    p = max(0.0, min(1.0, progress))
    r1, g1, b1 = hex_to_rgb(start_hex)
    r2, g2, b2 = hex_to_rgb(end_hex)
    r = int(r1 + (r2 - r1) * p)
    g = int(g1 + (g2 - g1) * p)
    b = int(b1 + (b2 - b1) * p)
    return rgb_to_hex((r, g, b))


# ============================================================================
# EASING FUNCTIONS
# ============================================================================

def ease_out_quad(t: float) -> float:
    """Smooth deceleration towards target."""
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_out_cubic(t: float) -> float:
    """Natural gentle deceleration."""
    return 1.0 - pow(1.0 - t, 3)


def ease_in_out_quad(t: float) -> float:
    """Smooth acceleration followed by deceleration."""
    if t < 0.5:
        return 2.0 * t * t
    return 1.0 - pow(-2.0 * t + 2.0, 2) / 2.0


def linear(t: float) -> float:
    return t


# ============================================================================
# CENTRAL ANIMATION MANAGER
# ============================================================================

class AnimationManager:
    """
    Central scheduler and manager for non-blocking UI animations.
    """

    def __init__(self, root: tk.Misc):
        self.root = root
        self._active_tasks: Dict[str, str] = {}  # key -> after_id
        self.reduced_motion: bool = False

    @property
    def _active_tweens(self) -> Dict[str, str]:
        """Compatibility property for active tasks."""
        return self._active_tasks

    def set_reduced_motion(self, enabled: bool) -> None:
        """Toggle accessibility reduced-motion preference."""
        self.reduced_motion = enabled

    def cancel(self, key: str) -> None:
        """Cancel any running animation under the specified key."""
        if key in self._active_tasks:
            after_id = self._active_tasks.pop(key)
            try:
                self.root.after_cancel(after_id)
            except Exception:
                pass

    def cancel_all(self) -> None:
        """Cancel all running animation tasks."""
        for key in list(self._active_tasks.keys()):
            self.cancel(key)

    def animate(
        self,
        key: str,
        duration_ms: int,
        update_fn: Callable[[float], None],
        completion_fn: Optional[Callable[[], None]] = None,
        easing: Callable[[float], float] = ease_out_quad,
        step_ms: int = 16
    ) -> None:
        """
        Execute a smooth time-based animation curve.
        """
        # Cancel any previous animation running on this channel
        self.cancel(key)

        if self.reduced_motion or duration_ms <= 0:
            try:
                update_fn(1.0)
            except Exception:
                pass
            if completion_fn:
                try:
                    completion_fn()
                except Exception:
                    pass
            return

        start_time = time.time()
        duration_sec = duration_ms / 1000.0

        def _step():
            elapsed = time.time() - start_time
            raw_progress = min(1.0, elapsed / duration_sec)
            eased_progress = easing(raw_progress)

            try:
                update_fn(eased_progress)
            except Exception:
                self.cancel(key)
                return

            if raw_progress >= 1.0:
                self._active_tasks.pop(key, None)
                if completion_fn:
                    try:
                        completion_fn()
                    except Exception:
                        pass
            else:
                after_id = self.root.after(step_ms, _step)
                self._active_tasks[key] = after_id

        # Kick off first frame
        after_id = self.root.after(0, _step)
        self._active_tasks[key] = after_id

    # ========================================================================
    # SPECIALIZED ANIMATION ROUTINES
    # ========================================================================

    def transition_screen(
        self,
        container: tk.Frame,
        old_screen: Optional[tk.Widget],
        new_screen: tk.Widget,
        duration_ms: int = 200,
        on_complete: Optional[Callable[[], None]] = None
    ) -> None:
        """
        Animate smooth slide-in transition between screens.
        """
        key = "screen_nav"
        self.cancel(key)

        if not old_screen or self.reduced_motion:
            if old_screen:
                old_screen.pack_forget()
            new_screen.pack(fill="both", expand=True)
            if on_complete:
                on_complete()
            return

        # Prepare geometries: use place for the duration of the transition
        container_w = max(100, container.winfo_width())
        start_offset_pct = 0.04  # Subtle 4% slide-in from right

        # Place new screen offscreen slightly
        old_screen.pack_forget()
        old_screen.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
        new_screen.place(relx=start_offset_pct, rely=0.0, relwidth=1.0, relheight=1.0)

        def _on_step(progress: float):
            # Slide old screen slightly left, new screen to 0.0
            old_relx = -start_offset_pct * progress
            new_relx = start_offset_pct * (1.0 - progress)
            try:
                old_screen.place_configure(relx=old_relx)
                new_screen.place_configure(relx=new_relx)
            except Exception:
                pass

        def _on_done():
            try:
                old_screen.place_forget()
                new_screen.place_forget()
                new_screen.pack(fill="both", expand=True)
            except Exception:
                pass
            if on_complete:
                on_complete()

        self.animate(
            key=key,
            duration_ms=duration_ms,
            update_fn=_on_step,
            completion_fn=_on_done,
            easing=ease_out_cubic,
            step_ms=16
        )

    def transition_colors(
        self,
        widget_color_pairs: List[Tuple[tk.Widget, str, str, str]],
        duration_ms: int = 220,
        on_complete: Optional[Callable[[], None]] = None
    ) -> None:
        """
        Smoothly transition widget colors (e.g. during Edition switching).
        Pairs format: (widget, prop_name: 'bg'|'fg', start_color, end_color)
        """
        key = "edition_colors"
        self.cancel(key)

        def _on_step(progress: float):
            for widget, prop, start_c, end_c in widget_color_pairs:
                try:
                    c = interpolate_color(start_c, end_c, progress)
                    widget.config(**{prop: c})
                except Exception:
                    pass

        def _on_done():
            # Ensure final exact colors
            for widget, prop, _, end_c in widget_color_pairs:
                try:
                    widget.config(**{prop: end_c})
                except Exception:
                    pass
            if on_complete:
                on_complete()

        self.animate(
            key=key,
            duration_ms=duration_ms,
            update_fn=_on_step,
            completion_fn=_on_done,
            easing=ease_out_quad,
            step_ms=16
        )

    def animate_caret(
        self,
        update_pos_fn: Callable[[float, float, float], None],
        start_x: float,
        start_y: float,
        start_h: float,
        target_x: float,
        target_y: float,
        target_h: float,
        duration_ms: int = 60
    ) -> None:
        """
        Smoothly interpolate vertical caret between screen coordinates.
        Very short duration (60ms) guarantees zero input lag while maintaining fluidity.
        """
        key = "caret_move"
        # If distance is very large (e.g. line wrap), jump immediately to prevent diagonal sweeping
        if abs(target_y - start_y) > 8:
            update_pos_fn(target_x, target_y, target_h)
            return

        def _on_step(p: float):
            cx = start_x + (target_x - start_x) * p
            cy = start_y + (target_y - start_y) * p
            ch = start_h + (target_h - start_h) * p
            update_pos_fn(cx, cy, ch)

        self.animate(
            key=key,
            duration_ms=duration_ms,
            update_fn=_on_step,
            easing=ease_out_quad,
            step_ms=16
        )
