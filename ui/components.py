"""
TypeRush Reusable UI Component Library

Contains native, high-performance UI components styled according to the
TypeRush design system. Built with Tkinter and Tkinter Canvas for clean,
modern desktop aesthetics without external dependencies.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Tuple, Any, List
from ui import theme


def draw_rounded_rectangle(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: int = 10,
    fill: str = theme.BG_CARD,
    outline: str = "",
    width: int = 1,
    tags: str = "rounded_rect",
) -> None:
    """
    Draw a clean, pixel-perfect rounded rectangle on a Tkinter Canvas
    using four corner arcs and connecting bodies.
    """
    canvas.delete(tags)

    # Constrain radius so corners do not invert on smaller dimensions
    w = max(1, x2 - x1)
    h = max(1, y2 - y1)
    r = min(radius, int(w // 2), int(h // 2))

    if r <= 0:
        canvas.create_rectangle(
            x1, y1, x2, y2, fill=fill, outline=outline, width=width, tags=tags
        )
        return

    # Inner solid shapes
    canvas.create_arc(
        x1, y1, x1 + 2 * r, y1 + 2 * r,
        start=90, extent=90, style="pieslice",
        fill=fill, outline=fill, tags=tags
    )
    canvas.create_arc(
        x2 - 2 * r, y1, x2, y1 + 2 * r,
        start=0, extent=90, style="pieslice",
        fill=fill, outline=fill, tags=tags
    )
    canvas.create_arc(
        x2 - 2 * r, y2 - 2 * r, x2, y2,
        start=270, extent=90, style="pieslice",
        fill=fill, outline=fill, tags=tags
    )
    canvas.create_arc(
        x1, y2 - 2 * r, x1 + 2 * r, y2,
        start=180, extent=90, style="pieslice",
        fill=fill, outline=fill, tags=tags
    )
    canvas.create_rectangle(
        x1 + r, y1, x2 - r, y2,
        fill=fill, outline=fill, tags=tags
    )
    canvas.create_rectangle(
        x1, y1 + r, x2, y2 - r,
        fill=fill, outline=fill, tags=tags
    )

    # Outline borders if specified
    if outline and width > 0:
        canvas.create_arc(
            x1, y1, x1 + 2 * r, y1 + 2 * r,
            start=90, extent=90, style="arc",
            outline=outline, width=width, tags=tags
        )
        canvas.create_arc(
            x2 - 2 * r, y1, x2, y1 + 2 * r,
            start=0, extent=90, style="arc",
            outline=outline, width=width, tags=tags
        )
        canvas.create_arc(
            x2 - 2 * r, y2 - 2 * r, x2, y2,
            start=270, extent=90, style="arc",
            outline=outline, width=width, tags=tags
        )
        canvas.create_arc(
            x1, y2 - 2 * r, x1 + 2 * r, y2,
            start=180, extent=90, style="arc",
            outline=outline, width=width, tags=tags
        )
        canvas.create_line(x1 + r, y1, x2 - r, y1, fill=outline, width=width, tags=tags)
        canvas.create_line(x2, y1 + r, x2, y2 - r, fill=outline, width=width, tags=tags)
        canvas.create_line(x1 + r, y2, x2 - r, y2, fill=outline, width=width, tags=tags)
        canvas.create_line(x1, y1 + r, x1, y2 - r, fill=outline, width=width, tags=tags)


class RoundedCard(tk.Canvas):
    """
    A modern card container with rounded corners and a subtle border.
    Exposes an `inner` Frame where child widgets can be packed or gridded.
    """

    def __init__(
        self,
        parent: tk.Widget,
        bg_color: str = theme.BG_CARD,
        border_color: str = theme.BORDER_COLOR,
        parent_bg: str = theme.BG_MAIN,
        corner_radius: int = theme.CARD_CORNER_RADIUS,
        padding: int = theme.SPACE_MD,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.bg_color = bg_color
        self.border_color = border_color
        self.corner_radius = corner_radius
        self.padding = padding

        # Embedded frame for child content
        self.inner = tk.Frame(self, bg=self.bg_color)
        self.inner.place(
            x=self.padding,
            y=self.padding,
            relwidth=1.0,
            relheight=1.0,
            width=-2 * self.padding,
            height=-2 * self.padding
        )

        self.bind("<Configure>", self._on_configure)
        self.inner.bind("<Configure>", self._on_inner_configure)

    def _on_inner_configure(self, event: tk.Event) -> None:
        """Dynamically expand card height if contents require more space."""
        try:
            req_h = self.inner.winfo_reqheight() + 2 * self.padding
            cur_h = self.winfo_height()
            if req_h > cur_h and cur_h > 10:
                self.config(height=req_h)
        except Exception:
            pass

    def _on_configure(self, event: tk.Event) -> None:
        """Redraw the rounded background whenever dimensions change."""
        w = event.width
        h = event.height
        if w > 2 and h > 2:
            # Leave 1px inset for clean border drawing
            draw_rounded_rectangle(
                self,
                1, 1, w - 2, h - 2,
                radius=self.corner_radius,
                fill=self.bg_color,
                outline=self.border_color,
                width=1,
                tags="card_bg"
            )
            # Ensure inner frame stays on top of drawn canvas items
            self.tag_lower("card_bg")


class GlassCard(tk.Canvas):
    """
    Midnight Studio Glass-Inspired Surface Card.
    Features dark translucent-looking surface, subtle border, soft layered top highlight,
    moderate corner radius, and comfortable internal spacing.
    Exposes an `inner` Frame where child widgets can be packed or gridded.
    """

    def __init__(
        self,
        parent: tk.Widget,
        bg_color: str = theme.SURFACE_GLASS,
        border_color: str = theme.SURFACE_GLASS_BORDER,
        highlight_color: str = theme.SURFACE_GLASS_HIGHLIGHT,
        parent_bg: str = theme.BG_PRIMARY,
        corner_radius: int = theme.RADIUS_LG,
        padding: int = theme.SPACE_MD,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.bg_color = bg_color
        self.border_color = border_color
        self.highlight_color = highlight_color
        self.corner_radius = corner_radius
        self.padding = padding

        # Embedded frame for child content
        self.inner = tk.Frame(self, bg=self.bg_color)
        self.inner.place(
            x=self.padding,
            y=self.padding,
            relwidth=1.0,
            relheight=1.0,
            width=-2 * self.padding,
            height=-2 * self.padding
        )

        self.bind("<Configure>", self._on_configure)
        self.inner.bind("<Configure>", self._on_inner_configure)

    def _on_inner_configure(self, event: tk.Event) -> None:
        """Dynamically expand card height if contents require more space."""
        try:
            req_h = self.inner.winfo_reqheight() + 2 * self.padding
            cur_h = self.winfo_height()
            if req_h > cur_h and cur_h > 10:
                self.config(height=req_h)
        except Exception:
            pass

    def _on_configure(self, event: tk.Event) -> None:
        """Redraw the rounded glass background and subtle top highlight."""
        w = event.width
        h = event.height
        if w > 2 and h > 2:
            self.delete("glass_bg")
            self.delete("glass_highlight")
            draw_rounded_rectangle(
                self,
                1, 1, w - 2, h - 2,
                radius=self.corner_radius,
                fill=self.bg_color,
                outline=self.border_color,
                width=1,
                tags="glass_bg"
            )
            r = min(self.corner_radius, w // 2, h // 2)
            if w > 2 * r:
                self.create_line(
                    1 + r, 2, w - 2 - r, 2,
                    fill=self.highlight_color,
                    width=1,
                    tags="glass_highlight"
                )
            self.tag_lower("glass_bg")
            self.tag_lower("glass_highlight")


class ElevatedCard(RoundedCard):
    """
    Slightly brighter surface with distinct separation from background
    for focal information and prominent metrics.
    """

    def __init__(
        self,
        parent: tk.Widget,
        bg_color: str = theme.SURFACE_ELEVATED,
        border_color: str = theme.BORDER_SUBTLE,
        parent_bg: str = theme.BG_PRIMARY,
        corner_radius: int = theme.RADIUS_LG,
        padding: int = theme.SPACE_MD,
        **kwargs
    ):
        super().__init__(
            parent,
            bg_color=bg_color,
            border_color=border_color,
            parent_bg=parent_bg,
            corner_radius=corner_radius,
            padding=padding,
            **kwargs
        )


class IconButton(tk.Canvas):
    """
    Minimalist icon button with tooltip support, hover state, and clear active feedback.
    """

    def __init__(
        self,
        parent: tk.Widget,
        icon: str,
        command: Optional[Callable[[], None]] = None,
        tooltip: str = "",
        size: int = 36,
        corner_radius: int = theme.RADIUS_SM,
        parent_bg: str = theme.SURFACE_DEFAULT,
        **kwargs
    ):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs
        )
        self.icon = icon
        self.command = command
        self.tooltip = tooltip
        self.btn_size = size
        self.corner_radius = corner_radius
        self.is_hovered = False
        self.is_pressed = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._render()

    def _on_enter(self, _event: tk.Event) -> None:
        self.is_hovered = True
        self._render()

    def _on_leave(self, _event: tk.Event) -> None:
        self.is_hovered = False
        self.is_pressed = False
        self._render()

    def _on_press(self, _event: tk.Event) -> None:
        self.is_pressed = True
        self._render()

    def _on_release(self, event: tk.Event) -> None:
        if self.is_pressed:
            self.is_pressed = False
            self._render()
            if 0 <= event.x <= self.btn_size and 0 <= event.y <= self.btn_size:
                if self.command:
                    self.command()

    def _render(self) -> None:
        self.delete("all")
        if self.is_pressed:
            bg = theme.SURFACE_ACTIVE
            fg = theme.ACCENT_PRIMARY
            border = theme.BORDER_FOCUS
        elif self.is_hovered:
            bg = theme.SURFACE_HOVER
            fg = theme.TEXT_PRIMARY
            border = theme.BORDER_SUBTLE
        else:
            bg = theme.SURFACE_ELEVATED
            fg = theme.TEXT_SECONDARY
            border = theme.BORDER_MUTED

        draw_rounded_rectangle(
            self,
            1, 1, self.btn_size - 2, self.btn_size - 2,
            radius=self.corner_radius,
            fill=bg,
            outline=border,
            width=1,
            tags="icon_bg"
        )
        self.create_text(
            self.btn_size / 2,
            self.btn_size / 2,
            text=self.icon,
            fill=fg,
            font=(theme.FONT_FAMILY, 12),
            anchor="center",
            tags="icon_txt"
        )


class PrimaryButton(tk.Canvas):
    """
    High-contrast accent button with rounded corners, responsive hover,
    and click animation.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: Optional[Callable[[], None]] = None,
        width: int = 140,
        height: int = 42,
        icon: str = "",
        corner_radius: int = theme.BUTTON_CORNER_RADIUS,
        parent_bg: str = theme.BG_CARD,
        font: Tuple = theme.FONT_BUTTON,
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs
        )
        self.text = text
        self.icon = icon
        self.command = command
        self.btn_width = width
        self.btn_height = height
        self.corner_radius = corner_radius
        self.font = font
        self.is_hovered = False
        self.is_pressed = False
        self.is_disabled = False

        self._bind_events()
        self._render()

    def _bind_events(self) -> None:
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event: tk.Event) -> None:
        if event.width > 2 and event.height > 2:
            self.btn_width = event.width
            self.btn_height = event.height
            self._render()

    def _on_enter(self, _event: tk.Event) -> None:
        if not self.is_disabled:
            self.is_hovered = True
            self._render()

    def _on_leave(self, _event: tk.Event) -> None:
        if not self.is_disabled:
            self.is_hovered = False
            self.is_pressed = False
            self._render()

    def _on_press(self, _event: tk.Event) -> None:
        if not self.is_disabled:
            self.is_pressed = True
            self._render()

    def _on_release(self, event: tk.Event) -> None:
        if not self.is_disabled and self.is_pressed:
            self.is_pressed = False
            self._render()
            # Verify cursor was inside button upon release
            if 0 <= event.x <= self.btn_width and 0 <= event.y <= self.btn_height:
                if self.command:
                    self.command()

    def _render(self) -> None:
        if self.is_disabled:
            bg = theme.BG_SURFACE
            fg = theme.TEXT_MUTED
            border = theme.BORDER_COLOR
        elif self.is_pressed:
            bg = theme.ACCENT_PRESSED
            fg = theme.TEXT_PRIMARY
            border = theme.ACCENT_PRESSED
        elif self.is_hovered:
            bg = theme.ACCENT_HOVER
            fg = theme.TEXT_INVERSE
            border = theme.ACCENT_HOVER
        else:
            bg = theme.ACCENT_PRIMARY
            fg = theme.TEXT_INVERSE
            border = theme.ACCENT_PRIMARY

        display_text = f"{self.icon}  {self.text}".strip() if self.icon else self.text
        import tkinter.font as tkfont
        try:
            f = tkfont.Font(font=self.font)
            req_w = f.measure(display_text) + 32
            if req_w > self.btn_width:
                self.btn_width = req_w
                self.config(width=req_w)
        except Exception:
            pass

        draw_rounded_rectangle(
            self,
            1, 1, self.btn_width - 2, self.btn_height - 2,
            radius=self.corner_radius,
            fill=bg,
            outline=border,
            width=1,
            tags="btn_bg"
        )

        self.delete("btn_text")
        self.create_text(
            self.btn_width / 2,
            self.btn_height / 2,
            text=display_text,
            fill=fg,
            font=self.font,
            tags="btn_text"
        )

    def set_text(self, text: str) -> None:
        self.text = text
        self._render()

    def set_disabled(self, disabled: bool) -> None:
        self.is_disabled = disabled
        self.config(cursor="arrow" if disabled else "hand2")
        self._render()


class SecondaryButton(tk.Canvas):
    """
    Subtle elevated surface button with muted border and responsive hover.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: Optional[Callable[[], None]] = None,
        width: int = 130,
        height: int = 40,
        icon: str = "",
        corner_radius: int = theme.BUTTON_CORNER_RADIUS,
        parent_bg: str = theme.BG_CARD,
        font: Tuple = theme.FONT_BUTTON,
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs
        )
        self.text = text
        self.icon = icon
        self.command = command
        self.btn_width = width
        self.btn_height = height
        self.corner_radius = corner_radius
        self.font = font
        self.is_hovered = False
        self.is_pressed = False
        self.is_disabled = False

        self._bind_events()
        self._render()

    def _bind_events(self) -> None:
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event: tk.Event) -> None:
        if event.width > 2 and event.height > 2:
            self.btn_width = event.width
            self.btn_height = event.height
            self._render()

    def _on_enter(self, _event: tk.Event) -> None:
        if not self.is_disabled:
            self.is_hovered = True
            self._render()

    def _on_leave(self, _event: tk.Event) -> None:
        if not self.is_disabled:
            self.is_hovered = False
            self.is_pressed = False
            self._render()

    def _on_press(self, _event: tk.Event) -> None:
        if not self.is_disabled:
            self.is_pressed = True
            self._render()

    def _on_release(self, event: tk.Event) -> None:
        if not self.is_disabled and self.is_pressed:
            self.is_pressed = False
            self._render()
            if 0 <= event.x <= self.btn_width and 0 <= event.y <= self.btn_height:
                if self.command:
                    self.command()

    def _render(self) -> None:
        if self.is_disabled:
            bg = theme.BG_SECONDARY
            fg = theme.TEXT_MUTED
            border = theme.BORDER_SUBTLE
        elif self.is_pressed:
            bg = theme.BG_ACTIVE
            fg = theme.TEXT_PRIMARY
            border = theme.BORDER_COLOR
        elif self.is_hovered:
            bg = theme.BG_SURFACE_HOVER
            fg = theme.TEXT_PRIMARY
            border = theme.ACCENT_PRIMARY
        else:
            bg = theme.BG_SURFACE
            fg = theme.TEXT_SECONDARY
            border = theme.BORDER_COLOR

        display_text = f"{self.icon}  {self.text}".strip() if self.icon else self.text
        import tkinter.font as tkfont
        try:
            f = tkfont.Font(font=self.font)
            req_w = f.measure(display_text) + 32
            if req_w > self.btn_width:
                self.btn_width = req_w
                self.config(width=req_w)
        except Exception:
            pass

        draw_rounded_rectangle(
            self,
            1, 1, self.btn_width - 2, self.btn_height - 2,
            radius=self.corner_radius,
            fill=bg,
            outline=border,
            width=1,
            tags="btn_bg"
        )

        self.delete("btn_text")
        self.create_text(
            self.btn_width / 2,
            self.btn_height / 2,
            text=display_text,
            fill=fg,
            font=self.font,
            tags="btn_text"
        )

    def set_text(self, text: str) -> None:
        self.text = text
        self._render()

    def set_disabled(self, disabled: bool) -> None:
        self.is_disabled = disabled
        self.config(cursor="arrow" if disabled else "hand2")
        self._render()


class StatCard(RoundedCard):
    """
    Dashboard metric card displaying a label, large value, and supporting subtitle.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        value: str = "--",
        unit: str = "",
        subtitle: str = "",
        icon: str = "",
        accent_color: str = theme.TEXT_PRIMARY,
        **kwargs
    ):
        super().__init__(
            parent,
            bg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            corner_radius=theme.CARD_CORNER_RADIUS,
            padding=theme.SPACE_MD,
            height=135,
            **kwargs
        )
        self.title_text = title
        self.unit_text = unit
        self.accent_color = accent_color

        # Card Top Row: Label and Icon
        top_frame = tk.Frame(self.inner, bg=theme.BG_CARD)
        top_frame.pack(fill="x", anchor="w")

        self.label_title = tk.Label(
            top_frame,
            text=title.upper(),
            font=theme.FONT_STAT_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        )
        self.label_title.pack(side="left")

        if icon:
            self.label_icon = tk.Label(
                top_frame,
                text=icon,
                font=theme.FONT_BODY,
                fg=theme.TEXT_SECONDARY,
                bg=theme.BG_CARD
            )
            self.label_icon.pack(side="right")

        # Value Row
        val_frame = tk.Frame(self.inner, bg=theme.BG_CARD)
        val_frame.pack(fill="x", anchor="w", pady=(theme.SPACE_XS, 2))

        self.label_value = tk.Label(
            val_frame,
            text=value,
            font=theme.FONT_STAT_VALUE,
            fg=self.accent_color,
            bg=theme.BG_CARD
        )
        self.label_value.pack(side="left")

        if unit:
            self.label_unit = tk.Label(
                val_frame,
                text=f" {unit}",
                font=theme.FONT_BODY_BOLD,
                fg=theme.TEXT_SECONDARY,
                bg=theme.BG_CARD
            )
            self.label_unit.pack(side="left", padx=(2, 0), pady=(10, 0))

        # Subtitle Row
        self.label_subtitle = tk.Label(
            self.inner,
            text=subtitle,
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        )
        self.label_subtitle.pack(fill="x", anchor="w")

    def set_value(self, value: str, subtitle: Optional[str] = None) -> None:
        """Update the displayed metric value and optional subtitle."""
        self.label_value.config(text=value)
        if subtitle is not None:
            self.label_subtitle.config(text=subtitle)


class SectionHeader(tk.Frame):
    """
    Standard section header with primary title and supporting description.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        subtitle: str = "",
        bg: str = theme.BG_MAIN,
        **kwargs
    ):
        super().__init__(parent, bg=bg, **kwargs)

        self.title_label = tk.Label(
            self,
            text=title,
            font=theme.FONT_TITLE_MEDIUM,
            fg=theme.TEXT_PRIMARY,
            bg=bg
        )
        self.title_label.pack(anchor="w")

        if subtitle:
            self.subtitle_label = tk.Label(
                self,
                text=subtitle,
                font=theme.FONT_BODY,
                fg=theme.TEXT_SECONDARY,
                bg=bg
            )
            self.subtitle_label.pack(anchor="w", pady=(theme.SPACE_2XS, 0))


class NavigationButton(tk.Canvas):
    """
    Sidebar navigation item with hover effect, active indicator bar,
    and distinct icon/label presentation.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        icon: str,
        command: Callable[[], None],
        height: int = 44,
        **kwargs
    ):
        super().__init__(
            parent,
            height=height,
            bg=theme.BG_SECONDARY,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs
        )
        self.text = text
        self.icon = icon
        self.command = command
        self.item_height = height
        self.item_width = theme.SIDEBAR_WIDTH - (theme.SPACE_MD * 2)
        self.is_active = False
        self.is_hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", self._on_configure)

        self._render()

    def _on_configure(self, event: tk.Event) -> None:
        if event.width > 2:
            self.item_width = event.width
            self._render()

    def _on_enter(self, _event: tk.Event) -> None:
        if not self.is_active:
            self.is_hovered = True
            self._render()

    def _on_leave(self, _event: tk.Event) -> None:
        if not self.is_active:
            self.is_hovered = False
            self._render()

    def _on_click(self, _event: tk.Event) -> None:
        if self.command:
            self.command()

    def set_active(self, active: bool) -> None:
        self.is_active = active
        self.is_hovered = False
        self._render()

    def _render(self) -> None:
        self.delete("all")

        # Determine colors based on state
        if self.is_active:
            bg_color = theme.BG_ACTIVE
            text_color = theme.TEXT_PRIMARY
            icon_color = theme.ACCENT_PRIMARY
            font = theme.FONT_NAV_ACTIVE
        elif self.is_hovered:
            bg_color = theme.BG_SURFACE
            text_color = theme.TEXT_PRIMARY
            icon_color = theme.TEXT_SECONDARY
            font = theme.FONT_NAV
        else:
            bg_color = theme.BG_SECONDARY
            text_color = theme.TEXT_SECONDARY
            icon_color = theme.TEXT_MUTED
            font = theme.FONT_NAV

        # Background rounded pill
        draw_rounded_rectangle(
            self,
            2, 2, self.item_width - 2, self.item_height - 2,
            radius=6,
            fill=bg_color,
            outline="",
            width=0,
            tags="nav_bg"
        )

        # Left accent pill indicator for active item
        if self.is_active:
            draw_rounded_rectangle(
                self,
                2, 8, 6, self.item_height - 8,
                radius=2,
                fill=theme.ACCENT_PRIMARY,
                outline="",
                width=0,
                tags="nav_indicator"
            )

        # Icon
        self.create_text(
            22,
            self.item_height / 2,
            text=self.icon,
            fill=icon_color,
            font=(theme.FONT_FAMILY, 13),
            anchor="center",
            tags="nav_content"
        )

        # Text label
        self.create_text(
            44,
            self.item_height / 2,
            text=self.text,
            fill=text_color,
            font=font,
            anchor="w",
            tags="nav_content"
        )


class Badge(tk.Canvas):
    """
    Subtle status chip or pill tag.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        bg_color: str = theme.BG_SURFACE,
        text_color: str = theme.ACCENT_PRIMARY,
        border_color: str = theme.BORDER_COLOR,
        parent_bg: str = theme.BG_MAIN,
        font: Tuple = theme.FONT_BODY_SMALL_BOLD,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.font = font

        self.padding_h = 10
        self.char_width = 7
        self.badge_height = 22
        self._render()

    def _render(self) -> None:
        self.delete("all")
        import tkinter.font as tkfont
        try:
            f = tkfont.Font(font=self.font)
            text_w = f.measure(self.text)
            text_h = f.metrics("linespace")
        except Exception:
            text_w = len(self.text) * 8
            text_h = 14

        width = text_w + 24
        height = max(24, text_h + 8)
        self.config(width=width, height=height)
        draw_rounded_rectangle(
            self,
            1, 1, width - 2, height - 2,
            radius=min(11, height // 2),
            fill=self.bg_color,
            outline=self.border_color,
            width=1,
            tags="badge_bg"
        )
        self.create_text(
            width / 2,
            height / 2,
            text=self.text,
            fill=self.text_color,
            font=self.font,
            tags="badge_text"
        )

    def set_text(self, text: str) -> None:
        """Update badge label and resize automatically."""
        self.text = text
        self._render()

    def get_text(self) -> str:
        """Return the current badge label."""
        return self.text

    def set_colors(
        self,
        bg: Optional[str] = None,
        fg: Optional[str] = None,
        border: Optional[str] = None,
        bg_color: Optional[str] = None,
        text_color: Optional[str] = None,
        border_color: Optional[str] = None,
    ) -> None:
        """Update badge colors and re-render."""
        b = bg_color or bg
        t = text_color or fg
        brd = border_color or border
        if b is not None:
            self.bg_color = b
        if t is not None:
            self.text_color = t
        if brd is not None:
            self.border_color = brd
        self._render()

    config_colors = set_colors


class AvatarPlaceholder(tk.Canvas):
    """
    A sleek rounded avatar placeholder with initials and subtle status styling.
    """

    def __init__(
        self,
        parent: tk.Widget,
        initials: str = "TR",
        size: int = 36,
        parent_bg: str = theme.BG_MAIN,
        **kwargs
    ):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.size = size
        self.initials = initials

        draw_rounded_rectangle(
            self,
            1, 1, size - 2, size - 2,
            radius=size // 2,
            fill=theme.BG_SURFACE,
            outline=theme.BORDER_COLOR,
            width=1,
            tags="avatar_bg"
        )
        self.create_text(
            size / 2,
            size / 2,
            text=initials,
            fill=theme.ACCENT_PRIMARY,
            font=(theme.FONT_FAMILY, 11, "bold"),
            tags="avatar_text"
        )


class HeaderBar(tk.Frame):
    """
    Top application header displaying current screen context and edition switcher.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str = "Dashboard",
        subtitle: str = "Overview and typing performance",
        app: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=theme.BG_SECONDARY,
            height=theme.HEADER_HEIGHT,
            **kwargs
        )
        self.app = app
        self.pack_propagate(False)

        # Content frame with padding
        content = tk.Frame(self, bg=theme.BG_SECONDARY)
        content.pack(fill="both", expand=True, padx=theme.SPACE_XL)

        # Left title & subtitle container
        titles_frame = tk.Frame(content, bg=theme.BG_SECONDARY)
        titles_frame.pack(side="left", fill="y", pady=(12, 0))

        self.title_label = tk.Label(
            titles_frame,
            text=title,
            font=theme.HEADING_LARGE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_SECONDARY
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            titles_frame,
            text=subtitle,
            font=theme.BODY_SMALL,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_SECONDARY
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # Right side context capsule
        self.right_frame = tk.Frame(content, bg=theme.BG_SECONDARY)
        self.right_frame.pack(side="right", fill="y", pady=(18, 0))

        self.status_badge = Badge(
            self.right_frame,
            text="MIDNIGHT MINIMAL",
            bg_color=theme.SURFACE_ELEVATED,
            text_color=theme.TEXT_SECONDARY,
            border_color=theme.BORDER_SUBTLE,
            parent_bg=theme.BG_SECONDARY
        )
        self.status_badge.pack(side="right")
        self.edition_pill = None

        # Bottom subtle separator
        divider = tk.Frame(self, bg=theme.BORDER_SUBTLE, height=1)
        divider.pack(side="bottom", fill="x")

    def _on_edition_changed(self, value: str) -> None:
        pass

    def sync_edition(self, edition_name: str) -> None:
        """Compatibility no-op for legacy edition synchronization."""
        pass

    def update_header(self, title: str, subtitle: str) -> None:
        """Update current view title and description."""
        self.title_label.config(text=title)
        self.subtitle_label.config(text=subtitle)


class SegmentedControl(tk.Frame):
    """
    Compact, understated segmented selector for options like Duration and Difficulty.
    Employs subtle contrast and restrained accents inspired by Apple interfaces.
    """

    def __init__(
        self,
        parent: tk.Widget,
        options: list,
        initial_selection: str,
        on_change: Optional[Callable[[str], None]] = None,
        label: str = "",
        **kwargs
    ):
        parent_bg = kwargs.pop("bg", theme.BG_MAIN)
        super().__init__(parent, bg=parent_bg, **kwargs)
        self.options = options
        self.selected_value = initial_selection if initial_selection in options else options[0]
        self.on_change = on_change
        self.segment_labels = {}

        # Optional subtle leading label (e.g., "time:" or "mode:")
        if label:
            lbl = tk.Label(
                self,
                text=label,
                font=theme.FONT_BODY_SMALL,
                fg=theme.TEXT_MUTED,
                bg=parent_bg
            )
            lbl.pack(side="left", padx=(0, theme.SPACE_XS))

        # Enclosing segmented capsule container
        self.capsule = tk.Frame(
            self,
            bg=theme.BG_SECONDARY,
            padx=2,
            pady=2,
            highlightbackground=theme.BORDER_SUBTLE,
            highlightthickness=1
        )
        self.capsule.pack(side="left")

        for opt in self.options:
            is_active = (opt == self.selected_value)
            seg = tk.Label(
                self.capsule,
                text=str(opt),
                font=theme.FONT_SEGMENT_ACTIVE if is_active else theme.FONT_SEGMENT,
                fg=theme.TEXT_PRIMARY if is_active else theme.TEXT_MUTED,
                bg=theme.BG_SURFACE if is_active else theme.BG_SECONDARY,
                padx=10,
                pady=4,
                cursor="hand2"
            )
            seg.pack(side="left", padx=1)
            seg.bind("<Button-1>", lambda e, val=opt: self._on_select(val))
            seg.bind("<Enter>", lambda e, s=seg, val=opt: self._on_hover(s, val))
            seg.bind("<Leave>", lambda e, s=seg, val=opt: self._on_leave(s, val))
            self.segment_labels[opt] = seg

    def _on_hover(self, label_widget: tk.Label, val: str) -> None:
        if val != self.selected_value:
            label_widget.config(fg=theme.TEXT_SECONDARY, bg=theme.BG_SURFACE_HOVER)

    def _on_leave(self, label_widget: tk.Label, val: str) -> None:
        if val != self.selected_value:
            label_widget.config(fg=theme.TEXT_MUTED, bg=theme.BG_SECONDARY)

    def _on_select(self, val: str) -> None:
        if val != self.selected_value:
            self.set_selected(val, trigger_callback=True)

    def set_selected(self, val: str, trigger_callback: bool = False) -> None:
        """Update active segment styling and optionally trigger change callback."""
        self.selected_value = val
        for opt, seg in self.segment_labels.items():
            is_active = (opt == val)
            seg.config(
                font=theme.FONT_SEGMENT_ACTIVE if is_active else theme.FONT_SEGMENT,
                fg=theme.TEXT_PRIMARY if is_active else theme.TEXT_MUTED,
                bg=theme.BG_SURFACE if is_active else theme.BG_SECONDARY
            )
        if trigger_callback and self.on_change:
            self.on_change(val)

    def get_selected(self) -> str:
        return self.selected_value


class ProgressBar(tk.Canvas):
    """
    Subtle 4px horizontal progress bar indicating passage completion.
    """

    def __init__(
        self,
        parent: tk.Widget,
        height: int = 4,
        track_color: str = theme.BG_SURFACE,
        fill_color: str = theme.ACCENT_PRIMARY,
        parent_bg: str = theme.BG_MAIN,
        **kwargs
    ):
        super().__init__(
            parent,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.bar_height = height
        self.track_color = track_color
        self.fill_color = fill_color
        self.progress_percent = 0.0
        self.canvas_width = 100

        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event: tk.Event) -> None:
        if event.width > 2:
            self.canvas_width = event.width
            self._render()

    def set_progress(self, percent: float) -> None:
        """Set progress percentage (0.0 to 100.0)."""
        self.progress_percent = max(0.0, min(100.0, float(percent)))
        self._render()

    def _render(self) -> None:
        self.delete("all")
        w = max(1, self.canvas_width)
        h = max(1, self.bar_height)

        # Track background
        self.create_rectangle(
            0, 0, w, h,
            fill=self.track_color,
            outline=""
        )

        # Progress bar fill
        filled_w = (self.progress_percent / 100.0) * w
        if filled_w > 0:
            self.create_rectangle(
                0, 0, filled_w, h,
                fill=self.fill_color,
                outline=""
            )


class KeycapHint(tk.Frame):
    """
    Subtle keyboard shortcut visual indicator (e.g., [Tab] + [Enter] Restart).
    """

    def __init__(
        self,
        parent: tk.Widget,
        keys: list,
        description: str,
        parent_bg: str = theme.BG_MAIN,
        **kwargs
    ):
        super().__init__(parent, bg=parent_bg, **kwargs)

        for i, k in enumerate(keys):
            if i > 0:
                plus = tk.Label(
                    self,
                    text="+",
                    font=theme.FONT_KEYCAP,
                    fg=theme.TEXT_MUTED,
                    bg=parent_bg
                )
                plus.pack(side="left", padx=2)

            key_frame = tk.Frame(
                self,
                bg=theme.BG_SURFACE,
                padx=5,
                pady=2,
                highlightbackground=theme.BORDER_COLOR,
                highlightthickness=1
            )
            key_frame.pack(side="left", padx=1)

            key_lbl = tk.Label(
                key_frame,
                text=k,
                font=theme.FONT_KEYCAP,
                fg=theme.TEXT_SECONDARY,
                bg=theme.BG_SURFACE
            )
            key_lbl.pack()

        desc_lbl = tk.Label(
            self,
            text=f"  {description}",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=parent_bg
        )
        desc_lbl.pack(side="left", padx=(2, 0))


class WpmLineGraph(tk.Canvas):
    """
    Custom Canvas-based line graph rendering real-time typing speed progression.
    Features subtle gridlines, restrained typography, and fallback handling for short tests.
    """

    def __init__(
        self,
        parent: tk.Widget,
        samples: Optional[list] = None,
        height: int = 200,
        bg_color: str = theme.BG_CARD,
        parent_bg: str = theme.BG_MAIN,
        **kwargs
    ):
        super().__init__(
            parent,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.samples = samples or []
        self.bg_color = bg_color
        self.parent_bg = parent_bg
        self.chart_height = height
        self.chart_width = 500

        self.bind("<Configure>", self._on_configure)

    def set_samples(self, samples: list) -> None:
        """Update graph with new time-series samples: list of (seconds, wpm)."""
        self.samples = list(samples)
        self._render()

    def _on_configure(self, event: tk.Event) -> None:
        if event.width > 20 and event.height > 20:
            self.chart_width = event.width
            self.chart_height = event.height
            self._render()

    def _render(self) -> None:
        self.delete("all")
        w = max(100, self.chart_width)
        h = max(60, self.chart_height)

        # Draw card container background
        draw_rounded_rectangle(
            self,
            1, 1, w - 2, h - 2,
            radius=theme.CARD_CORNER_RADIUS,
            fill=self.bg_color,
            outline=theme.BORDER_COLOR,
            width=1,
            tags="graph_bg"
        )

        # Handle Insufficient Data / Empty State (< 2 samples)
        if len(self.samples) < 2:
            self.create_text(
                w / 2,
                h / 2 - 10,
                text="Insufficient progression data recorded",
                fill=theme.TEXT_SECONDARY,
                font=theme.FONT_BODY_BOLD,
                tags="graph_empty"
            )
            self.create_text(
                w / 2,
                h / 2 + 14,
                text="Speed progression curve requires at least 2 active time intervals.",
                fill=theme.TEXT_MUTED,
                font=theme.FONT_BODY_SMALL,
                tags="graph_empty"
            )
            return

        # Margins for axis labels
        left_margin = 46
        right_margin = 28
        top_margin = 24
        bottom_margin = 32

        plot_w = max(10, w - left_margin - right_margin)
        plot_h = max(10, h - top_margin - bottom_margin)

        # Calculate data boundaries
        x_vals = [s[0] for s in self.samples]
        y_vals = [s[1] for s in self.samples]

        min_x = 0.0
        max_x = max(max(x_vals), 5.0)

        min_y = 0
        peak_y = max(max(y_vals), 10)
        avg_y = int(round(sum(y_vals) / len(y_vals)))
        # Round up max_y to clean multiple of 10 or 20
        max_y = int(((peak_y + 19) // 20) * 20)
        if max_y <= 20:
            max_y = 40

        # Draw 4 horizontal gridlines & Y-axis labels
        grid_steps = 4
        for step in range(grid_steps + 1):
            y_val = int((max_y / grid_steps) * step)
            py = (top_margin + plot_h) - (step / grid_steps) * plot_h

            # Gridline
            self.create_line(
                left_margin, py, left_margin + plot_w, py,
                fill=theme.BORDER_SUBTLE,
                width=1,
                dash=(2, 4) if step > 0 else (),
                tags="gridline"
            )

            # Y-axis label
            self.create_text(
                left_margin - 8,
                py,
                text=str(y_val),
                fill=theme.TEXT_MUTED,
                font=theme.FONT_BODY_SMALL,
                anchor="e",
                tags="axis_y"
            )

        # Draw X-axis timestamps (0s, mid, end)
        x_ticks = [0.0, max_x / 2.0, max_x]
        for tx in x_ticks:
            px = left_margin + (tx / max_x) * plot_w
            self.create_text(
                px,
                top_margin + plot_h + 16,
                text=f"{int(round(tx))}s",
                fill=theme.TEXT_MUTED,
                font=theme.FONT_BODY_SMALL,
                anchor="center",
                tags="axis_x"
            )

        # Map data coordinates to canvas pixels
        points = []
        peak_idx = 0
        max_val_found = -1
        for idx, (x, y) in enumerate(self.samples):
            if y > max_val_found:
                max_val_found = y
                peak_idx = idx
            norm_x = min(1.0, max(0.0, (x - min_x) / max(1.0, (max_x - min_x))))
            norm_y = min(1.0, max(0.0, (y - min_y) / max(1.0, (max_y - min_y))))
            cx = left_margin + norm_x * plot_w
            cy = (top_margin + plot_h) - norm_y * plot_h
            points.append((cx, cy))

        # Flatten points for create_line
        flat_coords = []
        for cx, cy in points:
            flat_coords.extend([cx, cy])

        # Plot average reference line if avg_y > 0
        if avg_y > 0:
            avg_norm_y = min(1.0, max(0.0, (avg_y - min_y) / max(1.0, (max_y - min_y))))
            avg_py = (top_margin + plot_h) - avg_norm_y * plot_h
            self.create_line(
                left_margin, avg_py, left_margin + plot_w, avg_py,
                fill=theme.ACCENT_SECONDARY,
                dash=(3, 3),
                width=1,
                tags="avg_line"
            )
            self.create_text(
                left_margin + plot_w - 4,
                avg_py - 8,
                text=f"Avg {avg_y} WPM",
                fill=theme.ACCENT_SECONDARY,
                font=theme.FONT_BODY_SMALL,
                anchor="e",
                tags="avg_label"
            )

        # Plot line (smooth spline if >= 3 points)
        if len(flat_coords) >= 4:
            is_smooth = len(points) >= 3
            self.create_line(
                flat_coords,
                fill=theme.ACCENT_PRIMARY,
                width=2,
                smooth=is_smooth,
                splinesteps=16 if is_smooth else 1,
                capstyle="round",
                joinstyle="round",
                tags="data_line"
            )

        # Plot data marker points
        for idx, (cx, cy) in enumerate(points):
            is_peak = (idx == peak_idx and len(points) > 1 and max_val_found > 0)
            dot_r = 4 if is_peak else 3
            dot_color = theme.COLOR_SUCCESS if is_peak else theme.ACCENT_PRIMARY
            self.create_oval(
                cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r,
                fill=dot_color,
                outline=theme.BG_CARD,
                width=1,
                tags="data_point"
            )
            if is_peak and cy > top_margin + 15:
                self.create_text(
                    cx, cy - 10,
                    text=f"Peak {max_val_found}",
                    fill=theme.COLOR_SUCCESS,
                    font=theme.FONT_BODY_SMALL,
                    anchor="center",
                    tags="peak_label"
                )


class AccuracyBreakdownBar(tk.Canvas):
    """
    Horizontal stacked comparison bar visualizing correct vs incorrect keystrokes.
    """

    def __init__(
        self,
        parent: tk.Widget,
        correct_chars: int = 0,
        incorrect_chars: int = 0,
        height: int = 8,
        parent_bg: str = theme.BG_CARD,
        **kwargs
    ):
        super().__init__(
            parent,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.correct_chars = correct_chars
        self.incorrect_chars = incorrect_chars
        self.bar_height = height
        self.bar_width = 300
        self.parent_bg = parent_bg

        self.bind("<Configure>", self._on_configure)

    def set_data(self, correct: int, incorrect: int) -> None:
        self.correct_chars = max(0, int(correct))
        self.incorrect_chars = max(0, int(incorrect))
        self._render()

    def _on_configure(self, event: tk.Event) -> None:
        if event.width > 2:
            self.bar_width = event.width
            self._render()

    def _render(self) -> None:
        self.delete("all")
        w = max(10, self.bar_width)
        h = max(4, self.bar_height)
        r = h // 2

        total = self.correct_chars + self.incorrect_chars
        if total == 0:
            # Empty track
            draw_rounded_rectangle(
                self, 1, 1, w - 2, h - 2, radius=r,
                fill=theme.BG_SURFACE, outline="", width=0
            )
            return

        correct_ratio = self.correct_chars / total
        cw = int(round(w * correct_ratio))

        # Background container track (shows error portion in red if any errors)
        error_bg = theme.COLOR_ERROR if self.incorrect_chars > 0 else theme.COLOR_SUCCESS
        draw_rounded_rectangle(
            self, 1, 1, w - 2, h - 2, radius=r,
            fill=error_bg, outline="", width=0, tags="bar_err"
        )

        # Green correct segment
        if cw > 0:
            if self.incorrect_chars == 0:
                draw_rounded_rectangle(
                    self, 1, 1, w - 2, h - 2, radius=r,
                    fill=theme.COLOR_SUCCESS, outline="", width=0, tags="bar_ok"
                )
            else:
                self.create_rectangle(
                    1, 1, cw, h - 1,
                    fill=theme.COLOR_SUCCESS, outline="", tags="bar_ok"
                )


class PerformanceTrendCanvas(GlassCard):
    """
    Compact performance progression line graph for recent completed sessions.
    Renders pure Canvas bezier/spline curves with subtle gridlines and data points.
    """

    def __init__(
        self,
        parent: tk.Widget,
        height: int = 220,
        parent_bg: str = theme.BG_PRIMARY,
        **kwargs
    ):
        super().__init__(
            parent,
            bg_color=theme.SURFACE_GLASS,
            border_color=theme.SURFACE_GLASS_BORDER,
            highlight_color=theme.SURFACE_GLASS_HIGHLIGHT,
            parent_bg=parent_bg,
            corner_radius=theme.RADIUS_LG,
            padding=theme.SPACE_MD,
            height=height,
            **kwargs
        )
        self.sessions = []

        # Top Header
        top_row = tk.Frame(self.inner, bg=theme.SURFACE_GLASS)
        top_row.pack(fill="x", pady=(0, theme.SPACE_XS))

        self.title_lbl = tk.Label(
            top_row,
            text="SPEED PROGRESSION",
            font=theme.FONT_STAT_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.SURFACE_GLASS
        )
        self.title_lbl.pack(side="left")

        self.trend_badge = tk.Label(
            top_row,
            text="RECENT SESSIONS",
            font=theme.FONT_BODY_SMALL_BOLD,
            fg=theme.ACCENT_PRIMARY,
            bg=theme.SURFACE_GLASS
        )
        self.trend_badge.pack(side="right")

        # Inner Drawing Canvas
        self.canvas = tk.Canvas(
            self.inner,
            bg=theme.SURFACE_GLASS,
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._render_graph())

    def set_sessions(self, sessions: list) -> None:
        """Update historical data (up to last 10 completed sessions)."""
        self.sessions = list(sessions[:10])
        # Display in chronological order (left to right)
        self.sessions.reverse()
        self._render_graph()

    def _render_graph(self) -> None:
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 20 or h < 20:
            return

        if len(self.sessions) < 2:
            # Empty state
            self.canvas.create_text(
                w / 2, h / 2 - 12,
                text="📈",
                fill=theme.TEXT_MUTED,
                font=(theme.FONT_FAMILY, 24),
                anchor="center"
            )
            self.canvas.create_text(
                w / 2, h / 2 + 18,
                text="Complete at least 2 sessions to visualize speed trend",
                fill=theme.TEXT_MUTED,
                font=theme.FONT_BODY_SMALL,
                anchor="center"
            )
            return

        wpms = [max(0, int(s.get("net_wpm", 0))) for s in self.sessions]
        min_v = max(0, min(wpms) - 10)
        max_v = max(wpms) + 15
        val_range = max(1, max_v - min_v)

        pad_left = 36
        pad_right = 20
        pad_top = 15
        pad_bottom = 24

        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom

        # Subtle horizontal grid lines & Y labels (3 levels)
        for level in [0.0, 0.5, 1.0]:
            y = pad_top + plot_h - (level * plot_h)
            lbl_val = int(round(min_v + level * val_range))
            self.canvas.create_line(pad_left, y, w - pad_right, y, fill=theme.BORDER_MUTED, width=1, dash=(2, 4))
            self.canvas.create_text(pad_left - 8, y, text=f"{lbl_val}", fill=theme.TEXT_MUTED, font=theme.CAPTION, anchor="e")

        # Calculate coordinates
        n = len(wpms)
        points = []
        for i, val in enumerate(wpms):
            x = pad_left + (i * plot_w / (n - 1))
            norm = (val - min_v) / val_range
            y = pad_top + plot_h - (norm * plot_h)
            points.append((x, y))

        # Draw smooth trend line
        coords = []
        for pt in points:
            coords.extend(pt)
        if len(coords) >= 4:
            self.canvas.create_line(*coords, fill=theme.ACCENT_PRIMARY, width=2, smooth=True, tags="trend_line")

        # Draw data points & X session labels
        for i, (x, y) in enumerate(points):
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=theme.ACCENT_SECONDARY, outline=theme.SURFACE_DEFAULT, width=1)
            self.canvas.create_text(x, h - 8, text=f"#{i + 1}", fill=theme.TEXT_MUTED, font=theme.CAPTION, anchor="center")


class RecentActivityList(GlassCard):
    """
    Compact recent activity feed showing latest 3-5 completed tests
    with WPM, Accuracy, Mode, and click-to-inspect navigation.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_inspect: Optional[Callable[[dict], None]] = None,
        on_view_all: Optional[Callable[[], None]] = None,
        height: int = 220,
        parent_bg: str = theme.BG_PRIMARY,
        **kwargs
    ):
        super().__init__(
            parent,
            bg_color=theme.SURFACE_GLASS,
            border_color=theme.SURFACE_GLASS_BORDER,
            highlight_color=theme.SURFACE_GLASS_HIGHLIGHT,
            parent_bg=parent_bg,
            corner_radius=theme.RADIUS_LG,
            padding=theme.SPACE_MD,
            height=height,
            **kwargs
        )
        self.on_inspect = on_inspect
        self.on_view_all = on_view_all

        # Top Header
        top_row = tk.Frame(self.inner, bg=theme.SURFACE_GLASS)
        top_row.pack(fill="x", pady=(0, theme.SPACE_XS))

        lbl = tk.Label(
            top_row,
            text="RECENT ACTIVITY",
            font=theme.FONT_STAT_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.SURFACE_GLASS
        )
        lbl.pack(side="left")

        btn_view_all = tk.Label(
            top_row,
            text="View All History →",
            font=theme.FONT_BODY_SMALL_BOLD,
            fg=theme.ACCENT_PRIMARY,
            bg=theme.SURFACE_GLASS,
            cursor="hand2"
        )
        btn_view_all.pack(side="right")
        btn_view_all.bind("<Button-1>", lambda e: self.on_view_all() if self.on_view_all else None)
        btn_view_all.bind("<Enter>", lambda e: btn_view_all.config(fg=theme.ACCENT_HOVER))
        btn_view_all.bind("<Leave>", lambda e: btn_view_all.config(fg=theme.ACCENT_PRIMARY))

        # Container for session rows
        self.rows_frame = tk.Frame(self.inner, bg=theme.SURFACE_GLASS)
        self.rows_frame.pack(fill="both", expand=True)

    def set_sessions(self, sessions: list) -> None:
        """Populate activity list with up to 4 recent sessions."""
        for w in self.rows_frame.winfo_children():
            w.destroy()

        recent = sessions[:4]
        if not recent:
            empty_lbl = tk.Label(
                self.rows_frame,
                text="No practice sessions recorded yet.\nStart your first challenge above!",
                font=theme.FONT_BODY_SMALL,
                fg=theme.TEXT_MUTED,
                bg=theme.SURFACE_GLASS,
                justify="center"
            )
            empty_lbl.pack(fill="both", expand=True, pady=20)
            return

        for sess in recent:
            row = tk.Frame(
                self.rows_frame,
                bg=theme.SURFACE_DEFAULT,
                padx=10,
                pady=6,
                cursor="hand2",
                highlightbackground=theme.BORDER_MUTED,
                highlightthickness=1
            )
            row.pack(fill="x", pady=2)

            date_raw = sess.get("date", "")
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(date_raw)
                date_str = dt.strftime("%b %d, %H:%M")
            except Exception:
                date_str = "Recent"

            mode = sess.get("mode", "Mixed")
            diff = sess.get("difficulty", "Medium")
            dur = sess.get("selected_duration", 60)
            net_wpm = sess.get("net_wpm", 0)
            acc = sess.get("accuracy", 100.0)

            left = tk.Frame(row, bg=theme.SURFACE_DEFAULT)
            left.pack(side="left")

            l1 = tk.Label(
                left,
                text=f"{date_str}  •  {mode}",
                font=theme.FONT_BODY_SMALL_BOLD,
                fg=theme.TEXT_PRIMARY,
                bg=theme.SURFACE_DEFAULT
            )
            l1.pack(anchor="w")

            l2 = tk.Label(
                left,
                text=f"{diff}  •  {dur}s",
                font=theme.CAPTION,
                fg=theme.TEXT_MUTED,
                bg=theme.SURFACE_DEFAULT
            )
            l2.pack(anchor="w")

            right = tk.Frame(row, bg=theme.SURFACE_DEFAULT)
            right.pack(side="right")

            arrow = tk.Label(right, text="→", font=theme.FONT_BODY_BOLD, fg=theme.TEXT_MUTED, bg=theme.SURFACE_DEFAULT)
            arrow.pack(side="right", padx=(8, 0))

            acc_lbl = tk.Label(
                right,
                text=f"{int(round(acc))}% ACC",
                font=theme.FONT_BODY_SMALL_BOLD,
                fg=theme.STATUS_SUCCESS if acc >= 95 else theme.ACCENT_SECONDARY,
                bg=theme.SURFACE_DEFAULT
            )
            acc_lbl.pack(side="right", padx=(10, 0))

            wpm_lbl = tk.Label(
                right,
                text=f"{net_wpm} WPM",
                font=theme.FONT_BODY_BOLD,
                fg=theme.TEXT_PRIMARY,
                bg=theme.SURFACE_DEFAULT
            )
            wpm_lbl.pack(side="right")

            def make_hover(widget, r_frame, s_data):
                def on_enter(e):
                    r_frame.config(bg=theme.SURFACE_HOVER)
                    for child in r_frame.winfo_children():
                        child.config(bg=theme.SURFACE_HOVER)
                        for sub in child.winfo_children():
                            sub.config(bg=theme.SURFACE_HOVER)

                def on_leave(e):
                    r_frame.config(bg=theme.SURFACE_DEFAULT)
                    for child in r_frame.winfo_children():
                        child.config(bg=theme.SURFACE_DEFAULT)
                        for sub in child.winfo_children():
                            sub.config(bg=theme.SURFACE_DEFAULT)

                def on_click(e):
                    if self.on_inspect:
                        self.on_inspect(s_data)

                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", on_click)

            make_hover(row, row, sess)
            for ch in (left, l1, l2, right, arrow, acc_lbl, wpm_lbl):
                make_hover(ch, row, sess)


# ============================================================================
# SETTINGS & PREFERENCES COMPONENTS (PART 7)
# ============================================================================

class ToggleSwitch(tk.Canvas):
    """
    Refined pill-style toggle switch for boolean preferences.
    Renders a crisp track with a sliding thumb circle.
    """

    def __init__(
        self,
        parent: tk.Widget,
        initial_state: bool = False,
        on_toggle: Optional[Callable[[bool], None]] = None,
        width: int = 44,
        height: int = 24,
        parent_bg: str = theme.BG_CARD,
        accent_color: str = theme.ACCENT_PRIMARY,
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs
        )
        self.width = width
        self.height = height
        self.parent_bg = parent_bg
        self.accent_color = accent_color
        self.is_on = bool(initial_state)
        self.on_toggle = on_toggle

        self.bind("<Button-1>", self._on_click)
        self.bind("<Return>", self._on_click)
        self.bind("<space>", self._on_click)

        self._render()

    def _render(self) -> None:
        self.delete("all")
        r = self.height / 2.0

        track_bg = self.accent_color if self.is_on else theme.BG_SURFACE
        border_c = self.accent_color if self.is_on else theme.BORDER_COLOR

        draw_rounded_rectangle(
            self,
            1, 1, self.width - 2, self.height - 2,
            radius=int(r) - 1,
            fill=track_bg,
            outline=border_c,
            width=1,
            tags="track"
        )

        thumb_r = r - 3.5
        thumb_x = (self.width - r) if self.is_on else r
        thumb_y = r
        thumb_color = "#FFFFFF" if self.is_on else theme.TEXT_MUTED

        self.create_oval(
            thumb_x - thumb_r,
            thumb_y - thumb_r,
            thumb_x + thumb_r,
            thumb_y + thumb_r,
            fill=thumb_color,
            outline="",
            tags="thumb"
        )

    def _on_click(self, _event=None) -> None:
        self.set_state(not self.is_on, trigger_callback=True)

    def set_state(self, state: bool, trigger_callback: bool = False) -> None:
        self.is_on = bool(state)
        self._render()
        if trigger_callback and self.on_toggle:
            self.on_toggle(self.is_on)

    def get_state(self) -> bool:
        return self.is_on


class SliderControl(tk.Frame):
    """
    Understated horizontal slider with value percentage readout.
    Debounces persistent storage writes while providing immediate visual feedback.
    """

    def __init__(
        self,
        parent: tk.Widget,
        min_val: int = 0,
        max_val: int = 100,
        initial_val: int = 70,
        on_change: Optional[Callable[[int], None]] = None,
        parent_bg: str = theme.BG_CARD,
        width: int = 180,
        **kwargs
    ):
        super().__init__(parent, bg=parent_bg, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = initial_val
        self.on_change = on_change
        self.parent_bg = parent_bg

        # Value readout label
        self.val_label = tk.Label(
            self,
            text=f"{self.current_val}%",
            font=theme.FONT_BODY_BOLD,
            fg=theme.TEXT_PRIMARY,
            bg=parent_bg,
            width=5,
            anchor="e"
        )
        self.val_label.pack(side="right", padx=(theme.SPACE_SM, 0))

        # Tkinter Scale widget styled cleanly
        self.scale = ttk.Scale(
            self,
            from_=min_val,
            to=max_val,
            orient="horizontal",
            command=self._on_scale_motion
        )
        self.scale.set(initial_val)
        self.scale.pack(side="left", fill="x", expand=True)

    def _on_scale_motion(self, val_str: str) -> None:
        val = int(float(val_str))
        self.current_val = val
        self.val_label.config(text=f"{val}%")
        if self.on_change:
            self.on_change(val)

    def set_value(self, val: int) -> None:
        self.current_val = max(self.min_val, min(self.max_val, int(val)))
        self.scale.set(self.current_val)
        self.val_label.config(text=f"{self.current_val}%")

    def get_value(self) -> int:
        return self.current_val


class SettingRow(tk.Frame):
    """
    Standardized horizontal setting container.
    Left: Title & descriptive supporting text.
    Right: Interacting control widget.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        description: str = "",
        control_widget: Optional[tk.Widget] = None,
        parent_bg: str = theme.BG_CARD,
        show_divider: bool = True,
        **kwargs
    ):
        super().__init__(parent, bg=parent_bg, **kwargs)
        self.parent_bg = parent_bg

        # Main inner row
        inner_row = tk.Frame(self, bg=parent_bg)
        inner_row.pack(fill="x", pady=theme.SPACE_SM)

        # Left label group
        left_group = tk.Frame(inner_row, bg=parent_bg)
        left_group.pack(side="left", fill="x", expand=True)

        self.title_lbl = tk.Label(
            left_group,
            text=title,
            font=theme.FONT_BODY_BOLD,
            fg=theme.TEXT_PRIMARY,
            bg=parent_bg,
            anchor="w"
        )
        self.title_lbl.pack(anchor="w")

        if description:
            self.desc_lbl = tk.Label(
                left_group,
                text=description,
                font=theme.FONT_BODY_SMALL,
                fg=theme.TEXT_MUTED,
                bg=parent_bg,
                anchor="w",
                justify="left",
                wraplength=480
            )
            self.desc_lbl.pack(anchor="w", pady=(2, 0))

        # Right control container
        self.control_container = tk.Frame(inner_row, bg=parent_bg)
        self.control_container.pack(side="right", padx=(theme.SPACE_MD, 0))
        self.control_area = self.control_container

        if control_widget:
            control_widget.pack(in_=self.control_container, side="right")

        # Optional bottom separator
        if show_divider:
            div = tk.Frame(self, bg=theme.BORDER_SUBTLE, height=1)
            div.pack(fill="x", pady=(theme.SPACE_XS, 0))


class EditionSelectCard(GlassCard):
    """
    Selectable edition card highlighting the three design identities:
    Pleasant, Basic, and Soundscape.
    """

    def __init__(
        self,
        parent: tk.Widget,
        edition_key: str,
        title: str,
        description: str,
        tags: List[str],
        is_selected: bool = False,
        on_select: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(parent, padding=theme.SPACE_LG, **kwargs)
        self.edition_key = edition_key
        self.is_selected = is_selected
        self.on_select = on_select

        inner = self.inner

        # Header with edition title and active indicator
        top = tk.Frame(inner, bg=theme.BG_CARD)
        top.pack(fill="x")

        self.lbl_title = tk.Label(
            top,
            text=title,
            font=theme.FONT_TITLE_SMALL,
            fg=theme.ACCENT_PRIMARY if is_selected else theme.TEXT_PRIMARY,
            bg=theme.BG_CARD
        )
        self.lbl_title.pack(side="left")

        self.badge_active = Badge(
            top,
            text="ACTIVE" if is_selected else "SELECT",
            bg_color=theme.ACCENT_SUBTLE if is_selected else theme.BG_SURFACE,
            text_color=theme.ACCENT_PRIMARY if is_selected else theme.TEXT_MUTED,
            border_color=theme.ACCENT_PRIMARY if is_selected else theme.BORDER_SUBTLE,
            parent_bg=theme.BG_CARD
        )
        self.badge_active.pack(side="right")

        # Description
        self.lbl_desc = tk.Label(
            inner,
            text=description,
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD,
            wraplength=260,
            justify="left"
        )
        self.lbl_desc.pack(anchor="w", pady=(theme.SPACE_XS, theme.SPACE_MD))

        # Trailing feature pills
        tag_frame = tk.Frame(inner, bg=theme.BG_CARD)
        tag_frame.pack(fill="x", side="bottom")

        for t in tags:
            pill = tk.Label(
                tag_frame,
                text=t,
                font=theme.FONT_STAT_LABEL,
                fg=theme.TEXT_MUTED,
                bg=theme.BG_SURFACE,
                padx=6,
                pady=2
            )
            pill.pack(side="left", padx=(0, 4))

        # Click handler bindings
        self._bind_clicks(self)

    def _bind_clicks(self, widget: tk.Widget) -> None:
        widget.bind("<Button-1>", lambda e: self._on_card_click())
        widget.config(cursor="hand2")
        for child in widget.winfo_children():
            self._bind_clicks(child)

    def _on_card_click(self) -> None:
        if self.on_select:
            self.on_select(self.edition_key)

    def set_active(self, is_active: bool) -> None:
        self.is_selected = is_active
        self.lbl_title.config(fg=theme.ACCENT_PRIMARY if is_active else theme.TEXT_PRIMARY)
        self.badge_active.set_text("ACTIVE" if is_active else "SELECT")
        self.badge_active.config_colors(
            bg=theme.ACCENT_SUBTLE if is_active else theme.BG_SURFACE,
            fg=theme.ACCENT_PRIMARY if is_active else theme.TEXT_MUTED,
            border=theme.ACCENT_PRIMARY if is_active else theme.BORDER_SUBTLE
        )


