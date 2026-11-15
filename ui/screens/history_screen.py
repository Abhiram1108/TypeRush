"""
TypeRush 2.0 History Screen & Long-Term Performance Analytics
Midnight Studio Design Identity

Provides a comprehensive, editorial-grade performance archive presenting:
- Section A: History Header (Title, subtitle, session count, active filter summary, CSV export, Clear action)
- Section B: Overall Performance Overview (4 StatCards: Total Tests, Personal Best, Average WPM, Average Accuracy)
- Section C: Long-Term Performance Trends (Interactive Canvas chart with Speed WPM ↔ Accuracy % view toggle, splines, peak/avg markers)
- Section D: Session History Timeline (Date-grouped chronological timeline with detailed session cards, PB indicator, delete action)
- Section E: Search Functionality (Live case-insensitive search by mode, difficulty, date, ID)
- Section F: Filters and Sorting (Multi-criteria filtering by mode, difficulty, time period, speed tier, and sorting)
- Section G: Mode-Specific Performance (Breakdown and comparative telemetry across all 6 typing modes)
- Section H: Difficulty-Based Progress (Metrics across Easy, Medium, Hard, Expert with context footnote)
- Section I: Personal Records & Milestones (Peak speed, peak accuracy, mode bests, favorite mode, clickable report links)
- Section J: History Management (Safe clear-all confirmation modal and individual session deletion with atomic writes)
- Section K: Native CSV Export (Exports full schema to user-selected path via standard library csv module)
- Three-Edition Support (Pleasant, Basic, Soundscape)
- Responsive Layout (Scrollable container optimized for 1200x800 and 950x650 bounds)
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from ui import theme
from ui import storage
from ui.components import (
    Badge,
    PrimaryButton,
    SecondaryButton,
    RoundedCard,
    GlassCard,
    draw_rounded_rectangle,
)
from ui.screens.base_screen import BaseScreen


class HistoryProgressChart(GlassCard):
    """
    Dedicated interactive Canvas progress chart for the History screen.
    Supports switching between Net WPM velocity and Accuracy % views,
    smooth splines, gridlines, average reference line, and peak marker.
    """

    def __init__(
        self,
        parent: tk.Widget,
        height: int = 210,
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
        self.sessions: List[Dict[str, Any]] = []
        self.metric: str = "wpm"  # "wpm" or "accuracy"

        # Chart Header
        top_row = tk.Frame(self.inner, bg=theme.SURFACE_GLASS)
        top_row.pack(fill="x", pady=(0, theme.SPACE_XS))

        left_title_box = tk.Frame(top_row, bg=theme.SURFACE_GLASS)
        left_title_box.pack(side="left")

        self.title_lbl = tk.Label(
            left_title_box,
            text="PERFORMANCE PROGRESSION",
            font=theme.FONT_STAT_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.SURFACE_GLASS
        )
        self.title_lbl.pack(side="left")

        self.scope_badge = Badge(
            left_title_box,
            text="ALL SESSIONS",
            bg_color=theme.BG_SURFACE,
            text_color=theme.ACCENT_PRIMARY,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.SURFACE_GLASS
        )
        self.scope_badge.pack(side="left", padx=(theme.SPACE_SM, 0))

        # Right Controls: Metric Switcher Buttons
        right_controls = tk.Frame(top_row, bg=theme.SURFACE_GLASS)
        right_controls.pack(side="right")

        self.btn_metric_wpm = tk.Label(
            right_controls,
            text="Speed / WPM",
            font=theme.FONT_BODY_SMALL_BOLD,
            fg=theme.TEXT_PRIMARY,
            bg=theme.ACCENT_SUBTLE,
            padx=10,
            pady=4,
            cursor="hand2",
            relief="solid",
            bd=1
        )
        self.btn_metric_wpm.pack(side="left", padx=(0, 4))
        self.btn_metric_wpm.bind("<Button-1>", lambda e: self.set_metric("wpm"))

        self.btn_metric_acc = tk.Label(
            right_controls,
            text="Accuracy %",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.SURFACE_GLASS,
            padx=10,
            pady=4,
            cursor="hand2",
            relief="flat",
            bd=0
        )
        self.btn_metric_acc.pack(side="left")
        self.btn_metric_acc.bind("<Button-1>", lambda e: self.set_metric("accuracy"))

        self.chart_width: int = 500
        self.chart_height: int = height

        # Canvas drawing surface
        self.canvas = tk.Canvas(
            self.inner,
            bg=theme.SURFACE_GLASS,
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_canvas_configure(self, event: tk.Event) -> None:
        if event.width > 20 and event.height > 20:
            self.chart_width = event.width
            self.chart_height = event.height
            self._render_graph()

    def set_metric(self, metric: str) -> None:
        """Toggle active metric between 'wpm' and 'accuracy'."""
        if metric == self.metric:
            return
        self.metric = metric

        if metric == "wpm":
            self.btn_metric_wpm.config(
                font=theme.FONT_BODY_SMALL_BOLD,
                fg=theme.TEXT_PRIMARY,
                bg=theme.ACCENT_SUBTLE,
                relief="solid",
                bd=1
            )
            self.btn_metric_acc.config(
                font=theme.FONT_BODY_SMALL,
                fg=theme.TEXT_MUTED,
                bg=theme.SURFACE_GLASS,
                relief="flat",
                bd=0
            )
            self.title_lbl.config(text="SPEED PROGRESSION (NET WPM)")
        else:
            self.btn_metric_acc.config(
                font=theme.FONT_BODY_SMALL_BOLD,
                fg=theme.TEXT_PRIMARY,
                bg=theme.ACCENT_SUBTLE,
                relief="solid",
                bd=1
            )
            self.btn_metric_wpm.config(
                font=theme.FONT_BODY_SMALL,
                fg=theme.TEXT_MUTED,
                bg=theme.SURFACE_GLASS,
                relief="flat",
                bd=0
            )
            self.title_lbl.config(text="ACCURACY PROGRESSION (%)")

        self._render_graph()

    def set_sessions(self, sessions: List[Dict[str, Any]], is_filtered: bool = False) -> None:
        """Update chart with session data. Displays oldest to newest (left to right)."""
        # Load chronological order (oldest first)
        self.sessions = list(reversed(sessions))
        self.scope_badge.set_text("FILTERED SESSIONS" if is_filtered else "ALL SESSIONS")
        self._render_graph()

    def _render_graph(self) -> None:
        """Render the spline or markers on canvas."""
        self.canvas.delete("all")
        w = max(100, self.chart_width if self.canvas.winfo_width() <= 1 else self.canvas.winfo_width())
        h = max(60, self.chart_height if self.canvas.winfo_height() <= 1 else self.canvas.winfo_height())

        total_pts = len(self.sessions)

        # 1. Zero Sessions: Empty state
        if total_pts == 0:
            self.canvas.create_text(
                w / 2, h / 2 - 8,
                text="📈 No Progression Data Available",
                fill=theme.TEXT_SECONDARY,
                font=theme.FONT_BODY_BOLD,
                anchor="center",
                tags="graph_empty"
            )
            self.canvas.create_text(
                w / 2, h / 2 + 14,
                text="Complete typing tests or adjust filters to visualize your historical trend.",
                fill=theme.TEXT_MUTED,
                font=theme.FONT_BODY_SMALL,
                anchor="center",
                tags="graph_empty"
            )
            return

        # Extract values based on active metric
        if self.metric == "wpm":
            vals = [max(0, int(s.get("net_wpm", 0))) for s in self.sessions]
            unit = "WPM"
            line_color = theme.ACCENT_PRIMARY
            min_y_bound = 0
            peak_val = max(vals)
            max_y_bound = max(40, int(((peak_val + 19) // 20) * 20))
        else:
            vals = [max(0.0, min(100.0, float(s.get("accuracy", 100.0)))) for s in self.sessions]
            unit = "%"
            line_color = theme.ACCENT_SECONDARY
            min_val = min(vals) if vals else 0.0
            peak_val = max(vals) if vals else 100.0
            min_y_bound = 50 if min_val >= 55 else 0
            max_y_bound = 100

        avg_val = round(sum(vals) / total_pts, 1) if total_pts > 0 else 0

        # Margins
        pad_left = 46
        pad_right = 28
        pad_top = 22
        pad_bottom = 26

        plot_w = max(10, w - pad_left - pad_right)
        plot_h = max(10, h - pad_top - pad_bottom)
        y_range = max(1.0, float(max_y_bound - min_y_bound))

        # Draw horizontal gridlines & Y labels (4 steps)
        steps = 4
        for step in range(steps + 1):
            y_val = min_y_bound + (y_range / steps) * step
            py = (pad_top + plot_h) - (step / steps) * plot_h

            self.canvas.create_line(
                pad_left, py, pad_left + plot_w, py,
                fill=theme.BORDER_MUTED,
                width=1,
                dash=(2, 4) if step > 0 else (),
                tags="gridline"
            )
            self.canvas.create_text(
                pad_left - 8, py,
                text=f"{int(round(y_val))}{unit if step == steps else ''}",
                fill=theme.TEXT_MUTED,
                font=theme.CAPTION,
                anchor="e",
                tags="axis_y"
            )

        # 2. Single Session Honest Data Point
        if total_pts == 1:
            cx = pad_left + plot_w / 2
            norm_y = min(1.0, max(0.0, (vals[0] - min_y_bound) / y_range))
            cy = (pad_top + plot_h) - norm_y * plot_h

            self.canvas.create_oval(
                cx - 5, cy - 5, cx + 5, cy + 5,
                fill=line_color,
                outline=theme.SURFACE_GLASS,
                width=2,
                tags="data_point"
            )
            self.canvas.create_text(
                cx, cy - 14,
                text=f"Single Session: {vals[0]} {unit}",
                fill=theme.TEXT_PRIMARY,
                font=theme.FONT_BODY_SMALL_BOLD,
                anchor="center",
                tags="point_label"
            )
            self.canvas.create_text(
                cx, pad_top + plot_h + 14,
                text="Inaugural point recorded. Complete additional sessions to generate trend line.",
                fill=theme.TEXT_MUTED,
                font=theme.CAPTION,
                anchor="center",
                tags="single_hint"
            )
            return

        # 3. Two or More Sessions: Full Graph
        points = []
        peak_idx = 0
        found_peak = -1

        for idx, val in enumerate(vals):
            if val > found_peak:
                found_peak = val
                peak_idx = idx

            norm_x = idx / max(1, total_pts - 1)
            norm_y = min(1.0, max(0.0, (val - min_y_bound) / y_range))
            cx = pad_left + norm_x * plot_w
            cy = (pad_top + plot_h) - norm_y * plot_h
            points.append((cx, cy))

        # Flatten coords
        flat_coords = []
        for cx, cy in points:
            flat_coords.extend([cx, cy])

        # Average reference line
        avg_norm_y = min(1.0, max(0.0, (avg_val - min_y_bound) / y_range))
        avg_py = (pad_top + plot_h) - avg_norm_y * plot_h
        self.canvas.create_line(
            pad_left, avg_py, pad_left + plot_w, avg_py,
            fill=theme.ACCENT_SECONDARY,
            dash=(3, 3),
            width=1,
            tags="avg_line"
        )
        self.canvas.create_text(
            pad_left + plot_w - 4, avg_py - 8,
            text=f"Avg {avg_val} {unit}",
            fill=theme.ACCENT_SECONDARY,
            font=theme.CAPTION,
            anchor="e",
            tags="avg_label"
        )

        # Plot connecting line (spline if >= 3 points)
        if len(flat_coords) >= 4:
            is_smooth = len(points) >= 3
            self.canvas.create_line(
                flat_coords,
                fill=line_color,
                width=2,
                smooth=is_smooth,
                splinesteps=16 if is_smooth else 1,
                capstyle="round",
                joinstyle="round",
                tags="data_line"
            )

        # Plot data points & Peak highlight
        for idx, (cx, cy) in enumerate(points):
            is_peak = (idx == peak_idx and total_pts > 1 and found_peak > 0)
            dot_r = 4 if is_peak else 3
            dot_color = theme.COLOR_SUCCESS if is_peak else line_color

            self.canvas.create_oval(
                cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r,
                fill=dot_color,
                outline=theme.SURFACE_GLASS,
                width=1,
                tags="data_point"
            )

            if is_peak and cy > pad_top + 16:
                self.canvas.create_text(
                    cx, cy - 10,
                    text=f"Peak {found_peak}{unit}",
                    fill=theme.COLOR_SUCCESS,
                    font=theme.CAPTION,
                    anchor="center",
                    tags="peak_label"
                )

        # X-axis label anchors (First session, mid session, latest session)
        x_indices = [0, total_pts // 2, total_pts - 1]
        for x_idx in set(x_indices):
            cx = points[x_idx][0]
            s_item = self.sessions[x_idx]
            raw_d = s_item.get("date", "")
            d_label = f"#{x_idx + 1}"
            try:
                dt = datetime.fromisoformat(raw_d)
                d_label = dt.strftime("%b %d")
            except Exception:
                pass

            self.canvas.create_text(
                cx, pad_top + plot_h + 14,
                text=d_label,
                fill=theme.TEXT_MUTED,
                font=theme.CAPTION,
                anchor="center",
                tags="axis_x"
            )


class HistoryScreen(BaseScreen):
    """
    High-fidelity session history, progress tracking and analytics archive (Midnight Studio).
    """
    SCREEN_NAME = "history"

    def __init__(self, parent: tk.Widget, app: "TypeRushApp", **kwargs):
        super().__init__(parent, app, **kwargs)

        self.sessions: List[Dict[str, Any]] = []
        self.filtered_sessions: List[Dict[str, Any]] = []

        # Persistent user filter & search state
        self.search_query: str = ""
        self.filter_mode: str = "All Modes"
        self.filter_difficulty: str = "All Difficulties"
        self.filter_time: str = "All Time"
        self.filter_perf: str = "All Speeds"
        self.sort_by: str = "Newest First"

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the scrollable history workspace container."""
        # Attach responsive atmospheric background
        self.setup_background("history")

        # Scrollable container for responsive resilience across resolutions (1200x800 & 950x650)
        self.scroll_canvas = tk.Canvas(
            self.bg_canvas,
            bg=theme.BG_PRIMARY,
            highlightthickness=0,
            bd=0
        )
        self.scroll_canvas.pack(fill="both", expand=True)

        self.container = tk.Frame(self.scroll_canvas, bg=theme.BG_PRIMARY)
        self.canvas_window = self.scroll_canvas.create_window(
            (0, 0), window=self.container, anchor="nw"
        )

        # Responsive canvas configuration bindings
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self.container.bind("<Configure>", self._on_container_configure)

        # 1. Empty State View (Shown when 0 sessions exist in storage)
        self._build_empty_state()

        # 2. Main History Archive Content (Holds all analytics, trends, timeline)
        self._build_history_content()

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """Expand container frame to match canvas width dynamically."""
        if hasattr(self, "scroll_canvas") and hasattr(self, "canvas_window"):
            self.scroll_canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_container_configure(self, event: tk.Event) -> None:
        """Update scrollable region when child dimensions change."""
        if hasattr(self, "scroll_canvas"):
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event: tk.Event) -> None:
        """Provide smooth vertical scrolling on wheel events."""
        if self.winfo_ismapped() and hasattr(self, "scroll_canvas"):
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ========================================================================
    # EMPTY STATE VIEW
    # ========================================================================

    def _build_empty_state(self) -> None:
        """Tasteful placeholder displayed when zero completed sessions exist."""
        self.empty_frame = tk.Frame(self.container, bg=theme.BG_MAIN)
        # Not packed initially

        card = RoundedCard(
            self.empty_frame,
            bg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.BG_MAIN,
            corner_radius=theme.CARD_CORNER_RADIUS,
            padding=theme.SPACE_2XL,
            height=340
        )
        card.pack(fill="both", expand=True, padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        inner = card.inner

        badge = Badge(
            inner,
            text="SESSION ARCHIVE",
            bg_color=theme.BG_SURFACE,
            text_color=theme.ACCENT_PRIMARY,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.BG_CARD
        )
        badge.pack(anchor="w", pady=(0, theme.SPACE_MD))

        title = tk.Label(
            inner,
            text="No typing sessions yet.",
            font=theme.FONT_TITLE_LARGE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_CARD
        )
        title.pack(anchor="w")

        desc = tk.Label(
            inner,
            text=(
                "Complete your first typing test to start building your personal speed progression, "
                "timeline records, mode-specific mastery telemetry, and long-term accuracy analytics."
            ),
            font=theme.FONT_BODY_LARGE,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD,
            wraplength=640,
            justify="left"
        )
        desc.pack(anchor="w", pady=(theme.SPACE_MD, theme.SPACE_XL))

        btn = PrimaryButton(
            inner,
            text="Take a Typing Test",
            icon="▶",
            command=lambda: self.app.show_screen("typing"),
            width=180,
            height=42,
            parent_bg=theme.BG_CARD
        )
        btn.pack(anchor="w")

    # ========================================================================
    # MAIN HISTORY ARCHIVE VIEW (table_frame for backwards compatibility)
    # ========================================================================

    def _build_history_content(self) -> None:
        """Construct the comprehensive history archive hierarchy."""
        # Using attribute name table_frame for 100% compatibility with test_final_audit.py
        self.table_frame = tk.Frame(self.container, bg=theme.BG_MAIN)
        # Packed when sessions exist

        inner_content = tk.Frame(self.table_frame, bg=theme.BG_MAIN, padx=theme.SPACE_LG, pady=theme.SPACE_MD)
        inner_content.pack(fill="both", expand=True)

        # Section A: Header Context & Action Buttons
        self._build_section_a_header(inner_content)

        # Section B: Overall Performance Overview (4 StatCards)
        self._build_section_b_overview(inner_content)

        # Section C: Long-Term Performance Trends (Interactive Graph)
        self._build_section_c_trend(inner_content)

        # Section E & F: Search, Filter & Sorting Bar
        self._build_section_e_f_filter_bar(inner_content)

        # Section D: Chronological Session Timeline
        self._build_section_d_timeline(inner_content)

        # Section G & H: Mode Mastery & Difficulty Telemetry (Two-Column Row)
        self._build_section_g_h_telemetry(inner_content)

        # Section I: Personal Records & Milestones
        self._build_section_i_personal_records(inner_content)

        # Section J & K: History Management & CSV Export
        self._build_section_j_k_management(inner_content)

    # ------------------------------------------------------------------------
    # SECTION A: HEADER
    # ------------------------------------------------------------------------

    def _build_section_a_header(self, parent: tk.Widget) -> None:
        """Section A — History Header with metadata and global actions."""
        header_bar = tk.Frame(parent, bg=theme.BG_MAIN)
        header_bar.pack(fill="x", pady=(0, theme.SPACE_SM))

        left_header = tk.Frame(header_bar, bg=theme.BG_MAIN)
        left_header.pack(side="left")

        title_row = tk.Frame(left_header, bg=theme.BG_MAIN)
        title_row.pack(anchor="w")

        title_lbl = tk.Label(
            title_row,
            text="Your Typing History",
            font=theme.FONT_TITLE_LARGE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_MAIN
        )
        title_lbl.pack(side="left")

        self.session_count_badge = Badge(
            title_row,
            text="0 SESSIONS RECORDED",
            bg_color=theme.BG_SURFACE,
            text_color=theme.ACCENT_PRIMARY,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.BG_MAIN
        )
        self.session_count_badge.pack(side="left", padx=(theme.SPACE_MD, 0), pady=(2, 0))

        subtitle_lbl = tk.Label(
            left_header,
            text="Every session is another step towards better typing.",
            font=theme.FONT_BODY,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_MAIN
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Right Header Actions
        right_actions = tk.Frame(header_bar, bg=theme.BG_MAIN)
        right_actions.pack(side="right", anchor="e")

        self.btn_export_csv = SecondaryButton(
            right_actions,
            text="Export CSV",
            icon="📥",
            command=self._on_export_csv,
            width=120,
            height=34,
            parent_bg=theme.BG_MAIN
        )
        self.btn_export_csv.pack(side="left", padx=(0, theme.SPACE_SM))

        self.btn_clear_history = SecondaryButton(
            right_actions,
            text="Clear History",
            icon="🗑",
            command=self._confirm_clear_history,
            width=130,
            height=34,
            parent_bg=theme.BG_MAIN
        )
        self.btn_clear_history.pack(side="left")

    # ------------------------------------------------------------------------
    # SECTION B: OVERALL PERFORMANCE OVERVIEW (4 StatCards)
    # ------------------------------------------------------------------------

    def _build_section_b_overview(self, parent: tk.Widget) -> None:
        """Section B — Four Reusable StatCards for High-Level Telemetry."""
        stats_strip = tk.Frame(
            parent,
            bg=theme.BG_CARD,
            padx=theme.SPACE_LG,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        stats_strip.pack(fill="x", pady=(0, theme.SPACE_MD))

        for col in range(4):
            stats_strip.grid_columnconfigure(col, weight=1, uniform="stat_cols")

        # Stat 1: Personal Best
        col0 = tk.Frame(stats_strip, bg=theme.BG_CARD)
        col0.grid(row=0, column=0, sticky="nsew", padx=theme.SPACE_SM)
        tk.Label(col0, text="PERSONAL BEST", font=theme.FONT_METRIC_LABEL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")
        self.val_best = tk.Label(col0, text="-- WPM", font=theme.FONT_TITLE_MEDIUM, fg=theme.COLOR_SUCCESS, bg=theme.BG_CARD)
        self.val_best.pack(anchor="w", pady=(2, 0))
        tk.Label(col0, text="All-time highest net velocity", font=theme.FONT_BODY_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")

        # Stat 2: Average Speed
        col1 = tk.Frame(stats_strip, bg=theme.BG_CARD)
        col1.grid(row=0, column=1, sticky="nsew", padx=theme.SPACE_SM)
        tk.Label(col1, text="AVERAGE SPEED", font=theme.FONT_METRIC_LABEL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")
        self.val_avg = tk.Label(col1, text="-- WPM", font=theme.FONT_TITLE_MEDIUM, fg=theme.ACCENT_PRIMARY, bg=theme.BG_CARD)
        self.val_avg.pack(anchor="w", pady=(2, 0))
        tk.Label(col1, text="Mean words per minute", font=theme.FONT_BODY_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")

        # Stat 3: Average Accuracy
        col2 = tk.Frame(stats_strip, bg=theme.BG_CARD)
        col2.grid(row=0, column=2, sticky="nsew", padx=theme.SPACE_SM)
        tk.Label(col2, text="AVERAGE ACCURACY", font=theme.FONT_METRIC_LABEL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")
        self.val_acc = tk.Label(col2, text="--%", font=theme.FONT_TITLE_MEDIUM, fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD)
        self.val_acc.pack(anchor="w", pady=(2, 0))
        tk.Label(col2, text="Mean precision ratio", font=theme.FONT_BODY_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")

        # Stat 4: Total Tests
        col3 = tk.Frame(stats_strip, bg=theme.BG_CARD)
        col3.grid(row=0, column=3, sticky="nsew", padx=theme.SPACE_SM)
        tk.Label(col3, text="TESTS COMPLETED", font=theme.FONT_METRIC_LABEL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")
        self.val_total = tk.Label(col3, text="0", font=theme.FONT_TITLE_MEDIUM, fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD)
        self.val_total.pack(anchor="w", pady=(2, 0))
        tk.Label(col3, text="Eligible completed challenges", font=theme.FONT_BODY_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")

    # ------------------------------------------------------------------------
    # SECTION C: LONG-TERM PERFORMANCE TRENDS
    # ------------------------------------------------------------------------

    def _build_section_c_trend(self, parent: tk.Widget) -> None:
        """Section C — Progress Line Graph with Speed vs Accuracy views."""
        self.trend_chart = HistoryProgressChart(
            parent,
            height=210,
            parent_bg=theme.BG_MAIN
        )
        self.trend_chart.pack(fill="x", pady=(0, theme.SPACE_MD))

    # ------------------------------------------------------------------------
    # SECTION E & F: SEARCH, FILTERS & SORTING BAR
    # ------------------------------------------------------------------------

    def _build_section_e_f_filter_bar(self, parent: tk.Widget) -> None:
        """Section E & F — Search field, Multi-criteria dropdowns, and sorting."""
        filter_card = tk.Frame(
            parent,
            bg=theme.BG_CARD,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_SM,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        filter_card.pack(fill="x", pady=(0, theme.SPACE_MD))

        # Top line: Search Input & Matches Counter
        top_line = tk.Frame(filter_card, bg=theme.BG_CARD)
        top_line.pack(fill="x", pady=(0, theme.SPACE_XS))

        # Search Bar
        search_box = tk.Frame(top_line, bg=theme.SURFACE_ELEVATED, padx=8, pady=4, highlightbackground=theme.BORDER_SUBTLE, highlightthickness=1)
        search_box.pack(side="left", fill="x", expand=True)

        tk.Label(search_box, text="🔍", font=theme.FONT_BODY_SMALL, fg=theme.TEXT_MUTED, bg=theme.SURFACE_ELEVATED).pack(side="left", padx=(0, 4))

        self.search_entry = tk.Entry(
            search_box,
            font=theme.FONT_BODY,
            fg=theme.TEXT_PRIMARY,
            bg=theme.SURFACE_ELEVATED,
            bd=0,
            highlightthickness=0,
            insertbackground=theme.ACCENT_PRIMARY
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

        self.btn_clear_search = tk.Label(
            search_box,
            text="✕",
            font=theme.FONT_BODY_SMALL_BOLD,
            fg=theme.TEXT_MUTED,
            bg=theme.SURFACE_ELEVATED,
            cursor="hand2"
        )
        self.btn_clear_search.pack(side="right", padx=(4, 0))
        self.btn_clear_search.bind("<Button-1>", lambda e: self._clear_search())

        # Match Counter Label
        self.lbl_match_count = tk.Label(
            top_line,
            text="Showing 0 sessions",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        )
        self.lbl_match_count.pack(side="right", padx=(theme.SPACE_MD, 0))

        # Bottom line: 5 Dropdown Selectors & Reset Action
        bottom_line = tk.Frame(filter_card, bg=theme.BG_CARD)
        bottom_line.pack(fill="x", pady=(theme.SPACE_XS, 0))

        # 1. Mode Filter
        tk.Label(bottom_line, text="Mode:", font=theme.CAPTION, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left", padx=(0, 2))
        self.combo_mode = ttk.Combobox(
            bottom_line,
            values=["All Modes", "Unified", "Words", "Punctuation", "Capitalization", "Numbers", "Mixed", "Code"],
            state="readonly",
            width=11
        )
        self.combo_mode.set("All Modes")
        self.combo_mode.pack(side="left", padx=(0, theme.SPACE_SM))
        self.combo_mode.bind("<<ComboboxSelected>>", self._on_filter_change)

        # 2. Difficulty Filter
        tk.Label(bottom_line, text="Difficulty:", font=theme.CAPTION, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left", padx=(0, 2))
        self.combo_diff = ttk.Combobox(
            bottom_line,
            values=["All Difficulties", "Easy", "Medium", "Hard", "Expert"],
            state="readonly",
            width=13
        )
        self.combo_diff.set("All Difficulties")
        self.combo_diff.pack(side="left", padx=(0, theme.SPACE_SM))
        self.combo_diff.bind("<<ComboboxSelected>>", self._on_filter_change)

        # 3. Time Period Filter
        tk.Label(bottom_line, text="Period:", font=theme.CAPTION, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left", padx=(0, 2))
        self.combo_time = ttk.Combobox(
            bottom_line,
            values=["All Time", "Today", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
            state="readonly",
            width=11
        )
        self.combo_time.set("All Time")
        self.combo_time.pack(side="left", padx=(0, theme.SPACE_SM))
        self.combo_time.bind("<<ComboboxSelected>>", self._on_filter_change)

        # 4. Performance Speed Filter
        tk.Label(bottom_line, text="Speed:", font=theme.CAPTION, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left", padx=(0, 2))
        self.combo_perf = ttk.Combobox(
            bottom_line,
            values=["All Speeds", "< 30 WPM", "30–49 WPM", "50–69 WPM", "70–89 WPM", "90+ WPM"],
            state="readonly",
            width=10
        )
        self.combo_perf.set("All Speeds")
        self.combo_perf.pack(side="left", padx=(0, theme.SPACE_SM))
        self.combo_perf.bind("<<ComboboxSelected>>", self._on_filter_change)

        # 5. Sorting
        tk.Label(bottom_line, text="Sort:", font=theme.CAPTION, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left", padx=(0, 2))
        self.combo_sort = ttk.Combobox(
            bottom_line,
            values=["Newest First", "Oldest First", "Highest WPM", "Lowest WPM", "Highest Accuracy", "Lowest Accuracy"],
            state="readonly",
            width=13
        )
        self.combo_sort.set("Newest First")
        self.combo_sort.pack(side="left", padx=(0, theme.SPACE_SM))
        self.combo_sort.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Reset Filters Button
        self.btn_reset_filters = SecondaryButton(
            bottom_line,
            text="Reset Filters",
            icon="↻",
            command=self._reset_filters,
            width=110,
            height=28,
            parent_bg=theme.BG_CARD
        )
        self.btn_reset_filters.pack(side="right")

    # ------------------------------------------------------------------------
    # SECTION D: CHRONOLOGICAL SESSION TIMELINE
    # ------------------------------------------------------------------------

    def _build_section_d_timeline(self, parent: tk.Widget) -> None:
        """Section D — Date-Grouped Interactive Session Timeline."""
        timeline_header = tk.Frame(parent, bg=theme.BG_MAIN)
        timeline_header.pack(fill="x", pady=(0, theme.SPACE_XS))

        tk.Label(
            timeline_header,
            text="SESSION TIMELINE",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_MAIN
        ).pack(side="left")

        # Container for date groups and session cards
        self.timeline_container = tk.Frame(parent, bg=theme.BG_MAIN)
        self.timeline_container.pack(fill="x", pady=(0, theme.SPACE_MD))

    # ------------------------------------------------------------------------
    # SECTION G & H: MODE MASTERY & DIFFICULTY TELEMETRY
    # ------------------------------------------------------------------------

    def _build_section_g_h_telemetry(self, parent: tk.Widget) -> None:
        """Section G & H — Side-by-Side Mode Mastery & Difficulty Progression."""
        row_frame = tk.Frame(parent, bg=theme.BG_MAIN)
        row_frame.pack(fill="x", pady=(0, theme.SPACE_MD))

        row_frame.grid_columnconfigure(0, weight=3, uniform="mid_cols")
        row_frame.grid_columnconfigure(1, weight=2, uniform="mid_cols")

        # --- Section G: Mode-Specific Performance ---
        box_g = tk.Frame(
            row_frame,
            bg=theme.BG_CARD,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        box_g.grid(row=0, column=0, sticky="nsew", padx=(0, theme.SPACE_SM))

        tk.Label(
            box_g,
            text="MODE-SPECIFIC MASTERY",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        self.mode_stats_inner = tk.Frame(box_g, bg=theme.BG_CARD)
        self.mode_stats_inner.pack(fill="x", pady=(theme.SPACE_SM, 0))

        # --- Section H: Difficulty-Based Progress ---
        box_h = tk.Frame(
            row_frame,
            bg=theme.BG_CARD,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        box_h.grid(row=0, column=1, sticky="nsew", padx=(theme.SPACE_SM, 0))

        tk.Label(
            box_h,
            text="DIFFICULTY PROGRESSION",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        self.diff_stats_inner = tk.Frame(box_h, bg=theme.BG_CARD)
        self.diff_stats_inner.pack(fill="x", pady=(theme.SPACE_SM, 0))

        tk.Label(
            box_h,
            text="Note: Performance reflects content challenge complexity rather than skill regression.",
            font=theme.CAPTION,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD,
            wraplength=320,
            justify="left"
        ).pack(anchor="w", pady=(theme.SPACE_SM, 0))

    # ------------------------------------------------------------------------
    # SECTION I: PERSONAL RECORDS & MILESTONES
    # ------------------------------------------------------------------------

    def _build_section_i_personal_records(self, parent: tk.Widget) -> None:
        """Section I — Personal Milestone Benchmark Cards."""
        box_i = tk.Frame(
            parent,
            bg=theme.BG_CARD,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        box_i.pack(fill="x", pady=(0, theme.SPACE_MD))

        tk.Label(
            box_i,
            text="PERSONAL RECORDS & MILESTONES",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        self.records_inner = tk.Frame(box_i, bg=theme.BG_CARD)
        self.records_inner.pack(fill="x", pady=(theme.SPACE_SM, 0))

    # ------------------------------------------------------------------------
    # SECTION J & K: HISTORY MANAGEMENT & ARCHIVE EXPORT
    # ------------------------------------------------------------------------

    def _build_section_j_k_management(self, parent: tk.Widget) -> None:
        """Section J & K — Data Management Actions."""
        box_j = tk.Frame(
            parent,
            bg=theme.SURFACE_ELEVATED,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        box_j.pack(fill="x", pady=(0, theme.SPACE_LG))

        tk.Label(
            box_j,
            text="DATA ARCHIVE & INTEGRITY",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.SURFACE_ELEVATED
        ).pack(anchor="w")

        info_lbl = tk.Label(
            box_j,
            text="TypeRush stores your sessions locally using atomic JSON writes in data/history.json. You can safely export your full typing telemetry as a CSV spreadsheet or reset your history.",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_SECONDARY,
            bg=theme.SURFACE_ELEVATED,
            wraplength=800,
            justify="left"
        )
        info_lbl.pack(anchor="w", pady=(2, theme.SPACE_SM))

        action_row = tk.Frame(box_j, bg=theme.SURFACE_ELEVATED)
        action_row.pack(fill="x")

        PrimaryButton(
            action_row,
            text="Export CSV Spreadsheet",
            icon="📥",
            command=self._on_export_csv,
            width=180,
            height=34,
            parent_bg=theme.SURFACE_ELEVATED
        ).pack(side="left")

        SecondaryButton(
            action_row,
            text="Clear All Saved History",
            icon="🗑",
            command=self._confirm_clear_history,
            width=180,
            height=34,
            parent_bg=theme.SURFACE_ELEVATED
        ).pack(side="left", padx=(theme.SPACE_MD, 0))

    # ========================================================================
    # FILTER, SEARCH & SORTING LOGIC
    # ========================================================================

    def _on_search_change(self, _event: Optional[tk.Event] = None) -> None:
        """Invoked when text is entered into the search input."""
        self.search_query = self.search_entry.get().strip()
        self._apply_filters_and_render()

    def _clear_search(self) -> None:
        """Clear search input field."""
        self.search_entry.delete(0, tk.END)
        self.search_query = ""
        self._apply_filters_and_render()

    def _on_filter_change(self, _event: Optional[tk.Event] = None) -> None:
        """Invoked when any dropdown filter or sort selection changes."""
        self.filter_mode = self.combo_mode.get()
        self.filter_difficulty = self.combo_diff.get()
        self.filter_time = self.combo_time.get()
        self.filter_perf = self.combo_perf.get()
        self.sort_by = self.combo_sort.get()
        self._apply_filters_and_render()

    def _reset_filters(self) -> None:
        """Reset all search and dropdown filters back to defaults."""
        self.search_entry.delete(0, tk.END)
        self.search_query = ""
        self.combo_mode.set("All Modes")
        self.combo_diff.set("All Difficulties")
        self.combo_time.set("All Time")
        self.combo_perf.set("All Speeds")
        self.combo_sort.set("Newest First")
        self.filter_mode = "All Modes"
        self.filter_difficulty = "All Difficulties"
        self.filter_time = "All Time"
        self.filter_perf = "All Speeds"
        self.sort_by = "Newest First"
        self._apply_filters_and_render()

    def _apply_filters_and_render(self) -> None:
        """Filter, sort, and re-render the timeline and progression chart."""
        matched = []
        now = datetime.now()
        today_date = now.date()

        for s in self.sessions:
            # 1. Mode Filter
            s_mode = s.get("mode", "Mixed")
            if self.filter_mode != "All Modes":
                if self.filter_mode == "Numbers" and s_mode not in ("Numbers", "Numbers & Symbols"):
                    continue
                elif self.filter_mode != "Numbers" and s_mode != self.filter_mode:
                    continue

            # 2. Difficulty Filter
            s_diff = s.get("difficulty", "Medium")
            if self.filter_difficulty != "All Difficulties" and s_diff != self.filter_difficulty:
                continue

            # 3. Time Period Filter
            raw_date = s.get("date", "")
            try:
                s_dt = datetime.fromisoformat(raw_date)
            except Exception:
                s_dt = datetime.min

            if self.filter_time == "Today":
                if s_dt.date() != today_date:
                    continue
            elif self.filter_time == "Last 7 Days":
                if (now - s_dt).total_seconds() > 7 * 86400:
                    continue
            elif self.filter_time == "Last 30 Days":
                if (now - s_dt).total_seconds() > 30 * 86400:
                    continue
            elif self.filter_time == "Last 90 Days":
                if (now - s_dt).total_seconds() > 90 * 86400:
                    continue

            # 4. Performance Speed Filter
            s_wpm = s.get("net_wpm", 0)
            if self.filter_perf == "< 30 WPM" and s_wpm >= 30:
                continue
            elif self.filter_perf == "30–49 WPM" and not (30 <= s_wpm <= 49):
                continue
            elif self.filter_perf == "50–69 WPM" and not (50 <= s_wpm <= 69):
                continue
            elif self.filter_perf == "70–89 WPM" and not (70 <= s_wpm <= 89):
                continue
            elif self.filter_perf == "90+ WPM" and s_wpm < 90:
                continue

            # 5. Search Query (Mode, Difficulty, Date, ID)
            if self.search_query:
                q = self.search_query.lower()
                date_str = s_dt.strftime("%d %b %Y %B %A").lower() if s_dt != datetime.min else ""
                combined_text = (
                    f"{s_mode} {s_diff} {s.get('id', '')} {s_wpm}wpm {int(round(s.get('accuracy', 0)))}% "
                    f"{s.get('rating', '')} {raw_date} {date_str}"
                ).lower()
                if q not in combined_text:
                    continue

            matched.append(s)

        # 6. Sorting
        def sort_key(item):
            try:
                dt_val = datetime.fromisoformat(item.get("date", ""))
            except Exception:
                dt_val = datetime.min
            wpm_val = item.get("net_wpm", 0)
            acc_val = float(item.get("accuracy", 0.0))

            if self.sort_by in ("Oldest First", "Newest First"):
                return dt_val
            elif self.sort_by in ("Highest WPM", "Lowest WPM"):
                return (wpm_val, dt_val)
            elif self.sort_by in ("Highest Accuracy", "Lowest Accuracy"):
                return (acc_val, dt_val)
            else:  # Default "Newest First"
                return dt_val

        reverse_order = self.sort_by in ("Newest First", "Highest WPM", "Highest Accuracy")
        matched.sort(key=sort_key, reverse=reverse_order)

        self.filtered_sessions = matched

        # Update Match Count
        total_all = len(self.sessions)
        total_matched = len(matched)
        is_filtered = (total_matched != total_all or self.search_query != "" or self.filter_mode != "All Modes" or self.filter_difficulty != "All Difficulties")

        if is_filtered:
            self.lbl_match_count.config(text=f"Showing {total_matched} of {total_all} sessions")
        else:
            self.lbl_match_count.config(text=f"{total_all} sessions found")

        # Update Progress Trend Graph
        self.trend_chart.set_sessions(self.filtered_sessions, is_filtered=is_filtered)

        # Render Timeline Cards
        self._render_timeline_items(matched)

    # ------------------------------------------------------------------------
    # TIMELINE RENDERING
    # ------------------------------------------------------------------------

    def _render_timeline_items(self, sessions: List[Dict[str, Any]]) -> None:
        """Render date-grouped session cards inside the timeline container."""
        for widget in self.timeline_container.winfo_children():
            widget.destroy()

        if not sessions:
            # Empty search / filter state
            empty_card = tk.Frame(
                self.timeline_container,
                bg=theme.BG_CARD,
                padx=theme.SPACE_XL,
                pady=theme.SPACE_XL,
                highlightbackground=theme.BORDER_COLOR,
                highlightthickness=1
            )
            empty_card.pack(fill="x", pady=theme.SPACE_SM)

            tk.Label(
                empty_card,
                text="🔍 No Matching Sessions Found",
                font=theme.FONT_BODY_BOLD,
                fg=theme.TEXT_PRIMARY,
                bg=theme.BG_CARD
            ).pack(anchor="w")

            tk.Label(
                empty_card,
                text="No typing sessions match the current search query or active filter combination.",
                font=theme.FONT_BODY_SMALL,
                fg=theme.TEXT_MUTED,
                bg=theme.BG_CARD
            ).pack(anchor="w", pady=(2, theme.SPACE_MD))

            SecondaryButton(
                empty_card,
                text="Reset Search & Filters",
                icon="↻",
                command=self._reset_filters,
                width=160,
                height=32,
                parent_bg=theme.BG_CARD
            ).pack(anchor="w")
            return

        # Determine overall Personal Best Net WPM across all sessions for PB badge
        all_time_pb = storage.get_personal_best()

        # Group sessions by date
        today_date = datetime.now().date()
        yesterday_date = today_date - timedelta(days=1)
        grouped: Dict[str, List[Dict[str, Any]]] = {}

        for s in sessions:
            raw_d = s.get("date", "")
            try:
                dt = datetime.fromisoformat(raw_d)
                s_date = dt.date()
                if s_date == today_date:
                    group_label = f"TODAY — {dt.strftime('%d %B %Y').upper()}"
                elif s_date == yesterday_date:
                    group_label = f"YESTERDAY — {dt.strftime('%d %B %Y').upper()}"
                else:
                    group_label = dt.strftime("%d %B %Y").upper()
            except Exception:
                group_label = "EARLIER SESSIONS"

            grouped.setdefault(group_label, []).append(s)

        # Render groups
        for group_label, group_sessions in grouped.items():
            # Group Header
            grp_header = tk.Frame(self.timeline_container, bg=theme.BG_MAIN)
            grp_header.pack(fill="x", pady=(theme.SPACE_SM, 2))

            tk.Label(
                grp_header,
                text=group_label,
                font=theme.FONT_METRIC_LABEL,
                fg=theme.ACCENT_PRIMARY,
                bg=theme.BG_MAIN
            ).pack(side="left")

            tk.Label(
                grp_header,
                text=f"{len(group_sessions)} session{'s' if len(group_sessions) > 1 else ''}",
                font=theme.CAPTION,
                fg=theme.TEXT_MUTED,
                bg=theme.BG_MAIN
            ).pack(side="right")

            # Session rows in this group
            for session in group_sessions:
                self._render_timeline_row(session, all_time_pb)

    def _render_timeline_row(self, session: Dict[str, Any], all_time_pb: int) -> None:
        """Render an individual session card in the timeline."""
        row = tk.Frame(
            self.timeline_container,
            bg=theme.BG_CARD,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_SM,
            cursor="hand2",
            highlightbackground=theme.BORDER_SUBTLE,
            highlightthickness=1
        )
        row.pack(fill="x", pady=2)

        # Parse time & ID
        raw_date = session.get("date", "")
        time_str = ""
        try:
            dt = datetime.fromisoformat(raw_date)
            time_str = dt.strftime("%I:%M %p")
        except Exception:
            time_str = raw_date[:10]

        sess_id = session.get("id", "")
        short_id = f"#{sess_id[:6]}" if sess_id else ""

        # Left Column: Time, ID, Mode Badge, Config
        left_box = tk.Frame(row, bg=theme.BG_CARD)
        left_box.pack(side="left", fill="y")

        top_left = tk.Frame(left_box, bg=theme.BG_CARD)
        top_left.pack(anchor="w")

        tk.Label(top_left, text=time_str, font=theme.FONT_BODY_BOLD, fg=theme.TEXT_PRIMARY, bg=theme.BG_CARD).pack(side="left")

        if short_id:
            tk.Label(top_left, text=short_id, font=theme.CAPTION, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(side="left", padx=(theme.SPACE_XS, 0))

        mode = session.get("mode", "Mixed")
        diff = session.get("difficulty", "Medium")
        dur = session.get("selected_duration", session.get("duration", 60))

        bot_left = tk.Frame(left_box, bg=theme.BG_CARD)
        bot_left.pack(anchor="w", pady=(2, 0))

        Badge(
            bot_left,
            text=mode.upper(),
            bg_color=theme.BG_SURFACE,
            text_color=theme.ACCENT_PRIMARY,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.BG_CARD
        ).pack(side="left")

        tk.Label(
            bot_left,
            text=f"•  {diff.upper()}  •  {dur}S",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        ).pack(side="left", padx=(theme.SPACE_XS, 0))

        # Center Column: Net Speed, Accuracy, Errors
        mid_box = tk.Frame(row, bg=theme.BG_CARD)
        mid_box.pack(side="left", fill="both", expand=True, padx=theme.SPACE_XL)

        net_wpm = session.get("net_wpm", 0)
        acc = session.get("accuracy", 100.0)
        errs = session.get("error_count", session.get("incorrect_chars", 0))

        tk.Label(
            mid_box,
            text=f"{net_wpm} WPM",
            font=theme.FONT_TITLE_MEDIUM,
            fg=theme.ACCENT_PRIMARY,
            bg=theme.BG_CARD
        ).pack(side="left")

        acc_color = theme.COLOR_SUCCESS if acc >= 95.0 else (theme.COLOR_WARNING if acc >= 90.0 else theme.COLOR_ERROR)
        tk.Label(
            mid_box,
            text=f"{int(round(acc))}% ACC",
            font=theme.FONT_BODY_BOLD,
            fg=acc_color,
            bg=theme.BG_CARD
        ).pack(side="left", padx=(theme.SPACE_MD, 0))

        tk.Label(
            mid_box,
            text=f"{errs} err",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        ).pack(side="left", padx=(theme.SPACE_SM, 0))

        # Right Column: PB Badge, Delete Icon, View Action
        right_box = tk.Frame(row, bg=theme.BG_CARD)
        right_box.pack(side="right")

        # Personal Best Badge
        if net_wpm == all_time_pb and all_time_pb > 0:
            pb_pill = Badge(
                right_box,
                text="★ BEST",
                bg_color="#1E3A2F",
                text_color=theme.COLOR_SUCCESS,
                border_color=theme.COLOR_SUCCESS,
                parent_bg=theme.BG_CARD
            )
            pb_pill.pack(side="left", padx=(0, theme.SPACE_MD))

        # View Report Label
        lbl_inspect = tk.Label(
            right_box,
            text="View Report →",
            font=theme.FONT_BODY_SMALL_BOLD,
            fg=theme.ACCENT_PRIMARY,
            bg=theme.BG_CARD,
            cursor="hand2"
        )
        lbl_inspect.pack(side="left", padx=(0, theme.SPACE_MD))

        # Delete Action Icon
        btn_del = tk.Label(
            right_box,
            text="🗑",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD,
            cursor="hand2"
        )
        btn_del.pack(side="right")
        btn_del.bind("<Button-1>", lambda e, s=session: self._confirm_delete_session(s))

        # Click & Hover Event Bindings
        def on_enter(_event):
            row.config(bg=theme.SURFACE_HOVER)
            for child in [left_box, top_left, bot_left, mid_box, right_box]:
                child.config(bg=theme.SURFACE_HOVER)
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label) and sub != btn_del:
                        sub.config(bg=theme.SURFACE_HOVER)

        def on_leave(_event):
            row.config(bg=theme.BG_CARD)
            for child in [left_box, top_left, bot_left, mid_box, right_box]:
                child.config(bg=theme.BG_CARD)
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label):
                        sub.config(bg=theme.BG_CARD)

        def on_row_click(_event, s=session):
            self._inspect_session(s)

        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        row.bind("<Button-1>", on_row_click)
        lbl_inspect.bind("<Button-1>", on_row_click)

    # ------------------------------------------------------------------------
    # SECTION G & H: TELEMETRY POPULATION
    # ------------------------------------------------------------------------

    def _render_mode_and_difficulty_stats(self) -> None:
        """Render Section G mode breakdown and Section H difficulty progression."""
        # 1. Mode Breakdown
        for w in self.mode_stats_inner.winfo_children():
            w.destroy()

        mode_stats = storage.get_mode_statistics(self.sessions)
        modes = ["Words", "Punctuation", "Capitalization", "Numbers", "Mixed", "Code"]

        for i in range(3):
            self.mode_stats_inner.grid_columnconfigure(i, weight=1, uniform="m_col")

        for idx, mode in enumerate(modes):
            r = idx // 3
            c = idx % 3
            st = mode_stats.get(mode, {"count": 0, "avg_wpm": 0, "best_wpm": 0, "avg_accuracy": 0.0})

            cell = tk.Frame(
                self.mode_stats_inner,
                bg=theme.SURFACE_ELEVATED,
                padx=theme.SPACE_SM,
                pady=theme.SPACE_XS,
                highlightbackground=theme.BORDER_SUBTLE,
                highlightthickness=1
            )
            cell.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

            tk.Label(cell, text=mode.upper(), font=theme.FONT_METRIC_LABEL, fg=theme.ACCENT_PRIMARY, bg=theme.SURFACE_ELEVATED).pack(anchor="w")

            if st["count"] > 0:
                tk.Label(
                    cell,
                    text=f"{st['avg_wpm']} WPM  ({st['best_wpm']} Best)",
                    font=theme.FONT_BODY_BOLD,
                    fg=theme.TEXT_PRIMARY,
                    bg=theme.SURFACE_ELEVATED
                ).pack(anchor="w")
                tk.Label(
                    cell,
                    text=f"{st['count']} tests  •  {int(round(st['avg_accuracy']))}% acc",
                    font=theme.CAPTION,
                    fg=theme.TEXT_MUTED,
                    bg=theme.SURFACE_ELEVATED
                ).pack(anchor="w")
            else:
                tk.Label(
                    cell,
                    text="No sessions recorded",
                    font=theme.FONT_BODY_SMALL,
                    fg=theme.TEXT_MUTED,
                    bg=theme.SURFACE_ELEVATED
                ).pack(anchor="w")

        # 2. Difficulty Breakdown
        for w in self.diff_stats_inner.winfo_children():
            w.destroy()

        diff_stats = storage.get_difficulty_statistics(self.sessions)
        diffs = ["Easy", "Medium", "Hard", "Expert"]

        for idx, diff in enumerate(diffs):
            st = diff_stats.get(diff, {"count": 0, "avg_wpm": 0, "avg_accuracy": 0.0})
            d_row = tk.Frame(self.diff_stats_inner, bg=theme.BG_CARD)
            d_row.pack(fill="x", pady=2)

            tk.Label(
                d_row,
                text=diff,
                font=theme.FONT_BODY_BOLD,
                fg=theme.TEXT_PRIMARY,
                bg=theme.BG_CARD,
                width=8,
                anchor="w"
            ).pack(side="left")

            if st["count"] > 0:
                tk.Label(
                    d_row,
                    text=f"{st['avg_wpm']} WPM   •   {int(round(st['avg_accuracy']))}% Acc",
                    font=theme.FONT_BODY,
                    fg=theme.ACCENT_PRIMARY,
                    bg=theme.BG_CARD
                ).pack(side="left")

                tk.Label(
                    d_row,
                    text=f"({st['count']} tests)",
                    font=theme.CAPTION,
                    fg=theme.TEXT_MUTED,
                    bg=theme.BG_CARD
                ).pack(side="right")
            else:
                tk.Label(
                    d_row,
                    text="No tests completed",
                    font=theme.CAPTION,
                    fg=theme.TEXT_MUTED,
                    bg=theme.BG_CARD
                ).pack(side="left")

    # ------------------------------------------------------------------------
    # SECTION I: PERSONAL RECORDS POPULATION
    # ------------------------------------------------------------------------

    def _render_personal_records(self) -> None:
        """Render Section I personal milestones grid."""
        for w in self.records_inner.winfo_children():
            w.destroy()

        records = storage.get_personal_records(self.sessions)

        for i in range(4):
            self.records_inner.grid_columnconfigure(i, weight=1, uniform="r_col")

        rec_items = [
            (0, 0, "OVERALL HIGHEST SPEED", f"{records['best_wpm']} WPM" if records['best_wpm'] > 0 else "--", theme.COLOR_SUCCESS, records['best_wpm_session']),
            (0, 1, "PEAK ACCURACY", f"{int(round(records['best_accuracy']))}%" if records['best_accuracy'] > 0 else "--", theme.TEXT_PRIMARY, records['best_accuracy_session']),
            (0, 2, "WORDS SPRINT BEST", f"{records['best_words_wpm']} WPM" if records['best_words_wpm'] > 0 else "--", theme.ACCENT_PRIMARY, records['best_words_session']),
            (0, 3, "CODE SYNTAX BEST", f"{records['best_code_wpm']} WPM" if records['best_code_wpm'] > 0 else "--", theme.ACCENT_PRIMARY, records['best_code_session']),
            (1, 0, "FAVORITE MODE", f"{records['most_practiced_mode']} ({records['most_practiced_count']} tests)" if records['most_practiced_count'] > 0 else "--", theme.TEXT_PRIMARY, None),
            (1, 1, "LONGEST CHALLENGE", f"{records['longest_session_seconds']}s" if records['longest_session_seconds'] > 0 else "--", theme.TEXT_PRIMARY, records['longest_session']),
            (1, 2, "MOST RECENT SPEED", f"{records['most_recent_session'].get('net_wpm', 0)} WPM" if records['most_recent_session'] else "--", theme.TEXT_PRIMARY, records['most_recent_session']),
            (1, 3, "TOTAL PRACTICE SESSIONS", f"{len(self.sessions)} completed", theme.TEXT_MUTED, None),
        ]

        for r, c, title, val_str, val_fg, linked_sess in rec_items:
            cell = tk.Frame(
                self.records_inner,
                bg=theme.SURFACE_ELEVATED,
                padx=theme.SPACE_SM,
                pady=theme.SPACE_SM,
                highlightbackground=theme.BORDER_SUBTLE,
                highlightthickness=1,
                cursor="hand2" if linked_sess else ""
            )
            cell.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

            tk.Label(cell, text=title, font=theme.FONT_METRIC_LABEL, fg=theme.TEXT_MUTED, bg=theme.SURFACE_ELEVATED).pack(anchor="w")

            val_lbl = tk.Label(cell, text=val_str, font=theme.FONT_BODY_BOLD, fg=val_fg, bg=theme.SURFACE_ELEVATED)
            val_lbl.pack(anchor="w", pady=(2, 0))

            if linked_sess:
                link_lbl = tk.Label(cell, text="View Report →", font=theme.CAPTION, fg=theme.ACCENT_PRIMARY, bg=theme.SURFACE_ELEVATED, cursor="hand2")
                link_lbl.pack(anchor="w", pady=(2, 0))

                def on_rec_click(_event, s=linked_sess):
                    self._inspect_session(s)

                cell.bind("<Button-1>", on_rec_click)
                val_lbl.bind("<Button-1>", on_rec_click)
                link_lbl.bind("<Button-1>", on_rec_click)

    # ========================================================================
    # DATA REFRESH & SYNCHRONIZATION
    # ========================================================================

    def refresh_history(self) -> None:
        """Reload sessions from storage, recalculate aggregates, and update UI."""
        self.sessions = storage.load_all_sessions()
        stats = storage.get_personal_statistics()
        total = stats["total_tests"]

        # Update Section B Overview Strip
        if total > 0:
            self.val_best.config(text=f"{stats['personal_best']} WPM")
            self.val_avg.config(text=f"{stats['average_wpm']} WPM")
            self.val_acc.config(text=f"{int(round(stats['average_accuracy']))}%")
            self.val_total.config(text=str(total))
            self.session_count_badge.set_text(f"{total} SESSIONS RECORDED")
            self.btn_clear_history.config(state="normal")
            self.btn_export_csv.config(state="normal")
        else:
            self.val_best.config(text="-- WPM")
            self.val_avg.config(text="-- WPM")
            self.val_acc.config(text="--%")
            self.val_total.config(text="0")
            self.session_count_badge.set_text("0 SESSIONS")
            self.btn_clear_history.config(state="disabled")
            self.btn_export_csv.config(state="disabled")

        if total == 0:
            self.table_frame.pack_forget()
            self.empty_frame.pack(fill="both", expand=True)
            return

        self.empty_frame.pack_forget()
        self.table_frame.pack(fill="both", expand=True)

        # Apply active search/filters to render timeline and trend
        self._apply_filters_and_render()

        # Render Section G & H Mode Mastery & Difficulty Telemetry
        self._render_mode_and_difficulty_stats()

        # Render Section I Personal Records
        self._render_personal_records()

    # ========================================================================
    # ACTIONS & MODAL DIALOGS
    # ========================================================================

    def _inspect_session(self, session: Dict[str, Any]) -> None:
        """
        Navigate to ResultsScreen to display full performance report for this session.
        Uses `is_historical=True` so `app.last_session_result` is not overwritten and no duplicate writes occur.
        """
        self.app.show_screen("results", session_result=session, is_historical=True)

    def _on_export_csv(self) -> None:
        """Prompt user for a destination file path and export history to CSV."""
        if not self.sessions:
            messagebox.showinfo("Export CSV", "No sessions recorded to export.", parent=self.app)
            return

        default_name = f"typerush_history_export_{datetime.now().strftime('%Y-%m-%d')}.csv"
        path = filedialog.asksaveasfilename(
            parent=self.app,
            title="Export Typing History to CSV",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")]
        )
        if not path:
            return

        # Export current filtered sessions if filter is active, else all sessions
        target_sessions = self.filtered_sessions if self.filtered_sessions else self.sessions
        ok, msg = storage.export_history_to_csv(path, target_sessions)

        if ok:
            messagebox.showinfo("Export Successful", f"{msg}\nSaved to:\n{path}", parent=self.app)
        else:
            messagebox.showerror("Export Failed", f"Could not export history:\n{msg}", parent=self.app)

    def _confirm_clear_history(self) -> None:
        """Display an elegant dark confirmation modal dialog before deleting all history."""
        dialog = tk.Toplevel(self.app)
        dialog.title("Clear History")
        dialog.configure(bg=theme.BG_CARD)
        dialog.resizable(False, False)
        dialog.transient(self.app)
        try:
            dialog.grab_set()
        except Exception:
            pass

        w = 440
        h = 220
        root_x = self.app.winfo_x()
        root_y = self.app.winfo_y()
        root_w = self.app.winfo_width()
        root_h = self.app.winfo_height()
        x = max(0, root_x + (root_w - w) // 2)
        y = max(0, root_y + (root_h - h) // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        content = tk.Frame(dialog, bg=theme.BG_CARD, padx=theme.SPACE_XL, pady=theme.SPACE_LG)
        content.pack(fill="both", expand=True)

        tk.Label(
            content,
            text="Clear All Typing History?",
            font=theme.FONT_TITLE_SMALL,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Are you sure you want to delete all saved sessions? Your personal best, averages, mode statistics, and past records will be permanently reset.",
            font=theme.FONT_BODY,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD,
            wraplength=380,
            justify="left"
        ).pack(anchor="w", pady=(theme.SPACE_SM, theme.SPACE_LG))

        btn_bar = tk.Frame(content, bg=theme.BG_CARD)
        btn_bar.pack(fill="x", side="bottom")

        def on_confirm():
            storage.clear_all_history()
            dialog.destroy()
            self.refresh_history()
            # Also update home dashboard statistics immediately
            home_screen = self.app.screens.get("home")
            if home_screen and hasattr(home_screen, "update_statistics"):
                home_screen.update_statistics()

        def on_cancel():
            dialog.destroy()

        btn_cancel = SecondaryButton(
            btn_bar,
            text="Cancel",
            command=on_cancel,
            width=90,
            height=34,
            parent_bg=theme.BG_CARD
        )
        btn_cancel.pack(side="right", padx=(theme.SPACE_SM, 0))

        btn_delete = PrimaryButton(
            btn_bar,
            text="Clear Everything",
            command=on_confirm,
            width=140,
            height=34,
            parent_bg=theme.BG_CARD
        )
        btn_delete.pack(side="right")

    def _confirm_delete_session(self, session: Dict[str, Any]) -> None:
        """Display an explicit confirmation modal before deleting an individual session."""
        dialog = tk.Toplevel(self.app)
        dialog.title("Delete Session")
        dialog.configure(bg=theme.BG_CARD)
        dialog.resizable(False, False)
        dialog.transient(self.app)
        try:
            dialog.grab_set()
        except Exception:
            pass

        w = 420
        h = 200
        root_x = self.app.winfo_x()
        root_y = self.app.winfo_y()
        root_w = self.app.winfo_width()
        root_h = self.app.winfo_height()
        x = max(0, root_x + (root_w - w) // 2)
        y = max(0, root_y + (root_h - h) // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        content = tk.Frame(dialog, bg=theme.BG_CARD, padx=theme.SPACE_XL, pady=theme.SPACE_LG)
        content.pack(fill="both", expand=True)

        tk.Label(
            content,
            text="Delete Individual Session?",
            font=theme.FONT_TITLE_SMALL,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        raw_d = session.get("date", "")
        formatted_d = raw_d[:16]
        try:
            dt = datetime.fromisoformat(raw_d)
            formatted_d = dt.strftime("%b %d, %Y · %I:%M %p")
        except Exception:
            pass

        tk.Label(
            content,
            text=f"Delete {session.get('mode', 'Mixed')} session from {formatted_d} ({session.get('net_wpm', 0)} WPM)? This action cannot be undone.",
            font=theme.FONT_BODY,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD,
            wraplength=360,
            justify="left"
        ).pack(anchor="w", pady=(theme.SPACE_SM, theme.SPACE_LG))

        btn_bar = tk.Frame(content, bg=theme.BG_CARD)
        btn_bar.pack(fill="x", side="bottom")

        def on_confirm():
            storage.delete_session(session.get("id", ""))
            dialog.destroy()
            self.refresh_history()
            home_screen = self.app.screens.get("home")
            if home_screen and hasattr(home_screen, "update_statistics"):
                home_screen.update_statistics()

        def on_cancel():
            dialog.destroy()

        btn_cancel = SecondaryButton(
            btn_bar,
            text="Cancel",
            command=on_cancel,
            width=90,
            height=34,
            parent_bg=theme.BG_CARD
        )
        btn_cancel.pack(side="right", padx=(theme.SPACE_SM, 0))

        btn_delete = PrimaryButton(
            btn_bar,
            text="Delete Session",
            command=on_confirm,
            width=130,
            height=34,
            parent_bg=theme.BG_CARD
        )
        btn_delete.pack(side="right")

    # ========================================================================
    # LIFECYCLE
    # ========================================================================

    def on_show(self, **kwargs) -> None:
        """
        Called when screen becomes visible.
        Refreshes session data and preserves user's active filter and search state.
        """
        super().on_show(**kwargs)

        # Bind mousewheel for smooth navigation
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Refresh history and re-apply current search/filters
        self.refresh_history()

    def on_hide(self) -> None:
        """Unbind mousewheel when navigating away."""
        super().on_hide()
        try:
            self.scroll_canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass
