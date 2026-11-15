"""
TypeRush Home Screen — Midnight Studio Edition

Polished desktop dashboard providing:
- Section A: Welcome Header with headline, subtitle, and live status badge.
- Section B: Quick Start Hero with full Mode, Difficulty, and Duration selectors + Start Test CTA.
- Section C: 4-column Performance Overview metric cards (Personal Best, Average, Accuracy, Total Tests).
- Section D & E: Two-column lower section with Canvas speed progression chart and Recent Activity feed.
- Section F: Contextual practice tip card (respecting show_tips setting).
"""

from datetime import datetime
import tkinter as tk
from typing import TYPE_CHECKING, Optional, Dict, Any, List
from ui import theme
from ui import storage

if TYPE_CHECKING:
    from ui.app import TypeRushApp
from ui.components import (
    GlassCard,
    PrimaryButton,
    SecondaryButton,
    StatCard,
    Badge,
    SegmentedControl,
    PerformanceTrendCanvas,
    RecentActivityList,
    RoundedCard,
)
from ui.screens.base_screen import BaseScreen


class HomeScreen(BaseScreen):
    """
    Midnight Studio Home Dashboard for TypeRush 2.0.
    """
    SCREEN_NAME = "home"

    def __init__(self, parent: tk.Widget, app: "TypeRushApp", **kwargs):
        super().__init__(parent, app, **kwargs)

        # Active configuration state
        settings = storage.load_settings()
        self.selected_mode: str = "Unified"
        self.selected_diff: str = str(settings.get("default_difficulty", "Medium"))
        dur_int = int(settings.get("default_duration", 60))
        self.selected_duration: str = f"{dur_int}s"

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the atmospheric, responsive home dashboard workspace."""
        # 1. Establish responsive atmospheric background canvas
        self.setup_background("home")

        # 2. Scrollable container to maintain responsiveness across resolutions (1200x800 and 950x650)
        self.scroll_canvas = tk.Canvas(
            self.bg_canvas,
            bg=theme.BG_PRIMARY,
            bd=0,
            highlightthickness=0
        )
        self.scroll_canvas.pack(fill="both", expand=True)

        self.container = tk.Frame(self.scroll_canvas, bg=theme.BG_PRIMARY)
        self.canvas_window = self.scroll_canvas.create_window(
            (0, 0),
            window=self.container,
            anchor="nw"
        )

        # Responsive canvas configuration bindings
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self.container.bind("<Configure>", self._on_container_configure)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Build dashboard content sections inside container
        self.content_padding_frame = tk.Frame(self.container, bg=theme.BG_PRIMARY)
        self.content_padding_frame.pack(fill="both", expand=True, padx=theme.SPACE_XL, pady=theme.SPACE_LG)

        # Section A: Welcome Header
        self._build_header_section()

        # Section B: Quick Start Hero (Centerpiece)
        self._build_hero_section()

        # Section C: Performance Overview
        self._build_stats_section()

        # Section D & E: Lower Two-Column Section (Speed Progression & Recent Activity)
        self._build_lower_section()

        # Section F: Practice Tip Card
        self._build_tip_section()

        # Populate with real statistics and recent sessions
        self.update_statistics()

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """Keep the inner content container matched to the viewport width."""
        if event.width > 10:
            self.scroll_canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_container_configure(self, _event: tk.Event) -> None:
        """Update scrollable region when children resize."""
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_mousewheel(self, event: tk.Event) -> None:
        """Provide smooth vertical scrolling when window height is compact."""
        if self.winfo_ismapped():
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ========================================================================
    # SECTION A: WELCOME HEADER
    # ========================================================================

    def _build_header_section(self) -> None:
        """Top welcome title, subtitle, and contextual status badge."""
        header_frame = tk.Frame(self.content_padding_frame, bg=theme.BG_PRIMARY)
        header_frame.pack(fill="x", anchor="w", pady=(0, theme.SPACE_LG))

        top_row = tk.Frame(header_frame, bg=theme.BG_PRIMARY)
        top_row.pack(fill="x", anchor="w")

        title_label = tk.Label(
            top_row,
            text="Make every keystroke count.",
            font=theme.FONT_TITLE_LARGE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_PRIMARY
        )
        title_label.pack(side="left")

        version_badge = Badge(
            top_row,
            text="v2.1 • MIDNIGHT MINIMAL",
            bg_color=theme.ACCENT_SUBTLE,
            text_color=theme.ACCENT_PRIMARY,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.BG_PRIMARY
        )
        version_badge.pack(side="left", padx=(theme.SPACE_MD, 0), pady=(4, 0))

        # Status badge on right side
        self.status_badge = Badge(
            top_row,
            text="PRACTICE READY",
            bg_color=theme.BG_SURFACE,
            text_color=theme.COLOR_SUCCESS,
            border_color=theme.BORDER_SUBTLE,
            parent_bg=theme.BG_PRIMARY
        )
        self.status_badge.pack(side="right", pady=(4, 0))

        subtitle_label = tk.Label(
            header_frame,
            text="Unified natural sentence typing, live error alignment, and precision analytics.",
            font=theme.FONT_BODY_LARGE,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_PRIMARY
        )
        subtitle_label.pack(anchor="w", pady=(theme.SPACE_2XS, 0))

    # ========================================================================
    # SECTION B: QUICK START HERO (Visual Centerpiece)
    # ========================================================================

    def _build_hero_section(self) -> None:
        """
        Prominent Quick Start card providing direct configuration selectors
        for Difficulty, Duration, and the primary Start Typing Test action.
        """
        self.hero_card = GlassCard(
            self.content_padding_frame,
            bg_color=theme.SURFACE_GLASS,
            border_color=theme.SURFACE_GLASS_BORDER,
            highlight_color=theme.SURFACE_GLASS_HIGHLIGHT,
            parent_bg=theme.BG_PRIMARY,
            corner_radius=theme.RADIUS_LG,
            padding=theme.SPACE_LG,
            height=180
        )
        self.hero_card.pack(fill="x", pady=(0, theme.SPACE_LG))

        inner = self.hero_card.inner

        # 1. Hero Header Row
        header_row = tk.Frame(inner, bg=theme.SURFACE_GLASS)
        header_row.pack(fill="x", anchor="w", pady=(0, theme.SPACE_XS))

        hero_badge = Badge(
            header_row,
            text="QUICK START",
            bg_color=theme.BG_SURFACE,
            text_color=theme.COLOR_SUCCESS,
            border_color=theme.BORDER_SUBTLE,
            parent_bg=theme.SURFACE_GLASS
        )
        hero_badge.pack(side="left")

        hero_title = tk.Label(
            header_row,
            text="Benchmark Speed Challenge",
            font=theme.FONT_BODY_BOLD,
            fg=theme.TEXT_PRIMARY,
            bg=theme.SURFACE_GLASS
        )
        hero_title.pack(side="left", padx=(theme.SPACE_SM, 0))

        engine_badge = Badge(
            header_row,
            text="CONTINUOUS STREAM",
            bg_color=theme.ACCENT_SUBTLE,
            text_color=theme.ACCENT_PRIMARY,
            border_color=theme.BORDER_SUBTLE,
            parent_bg=theme.SURFACE_GLASS
        )
        engine_badge.pack(side="right")

        # 2. Hero Description
        hero_desc = tk.Label(
            inner,
            text=(
                "Challenge yourself with natural, coherent English passages. "
                "Immediate character feedback, cascade-immune error alignment, and live metrics."
            ),
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_SECONDARY,
            bg=theme.SURFACE_GLASS,
            wraplength=850,
            justify="left"
        )
        hero_desc.pack(anchor="w", pady=(0, theme.SPACE_MD))

        # 3. Difficulty & Duration Selector Row (Unified typing, no 6-mode bar)
        config_row = tk.Frame(inner, bg=theme.SURFACE_GLASS)
        config_row.pack(fill="x", pady=(0, theme.SPACE_MD))

        self.diff_selector = SegmentedControl(
            config_row,
            options=["Easy", "Medium", "Hard", "Expert"],
            initial_selection=self.selected_diff,
            label="DIFFICULTY:",
            on_change=self._on_diff_changed,
            bg=theme.SURFACE_GLASS
        )
        self.diff_selector.pack(side="left")

        self.duration_selector = SegmentedControl(
            config_row,
            options=["15s", "30s", "60s", "120s"],
            initial_selection=self.selected_duration,
            label="DURATION:",
            on_change=self._on_duration_changed,
            bg=theme.SURFACE_GLASS
        )
        self.duration_selector.pack(side="left", padx=(theme.SPACE_XL, 0))

        # 4. Action Row: Active Summary + Prominent Primary Button
        action_row = tk.Frame(inner, bg=theme.SURFACE_GLASS)
        action_row.pack(fill="x", side="bottom")

        self.summary_label = tk.Label(
            action_row,
            text=self._get_summary_text(),
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.SURFACE_GLASS
        )
        self.summary_label.pack(side="left", pady=(8, 0))

        self.start_btn = PrimaryButton(
            action_row,
            text="Start Typing Test",
            icon="▶",
            command=self._on_start_test,
            width=180,
            height=42,
            parent_bg=theme.SURFACE_GLASS
        )
        self.start_btn.pack(side="right")

    def _get_summary_text(self) -> str:
        """Formatted configuration summary string."""
        return f"Configured: {self.selected_diff}  •  {self.selected_duration} challenge"

    def _update_summary(self) -> None:
        """Update active configuration summary label."""
        if hasattr(self, "summary_label"):
            self.summary_label.config(text=self._get_summary_text())

    def _on_mode_changed(self, val: str) -> None:
        self.selected_mode = val
        self._update_summary()
        self.selected_mode = val
        self._update_summary()

    def _on_diff_changed(self, val: str) -> None:
        self.selected_diff = val
        self._update_summary()

    def _on_duration_changed(self, val: str) -> None:
        self.selected_duration = val
        self._update_summary()

    def _on_start_test(self) -> None:
        """
        Persist active configuration choices and immediately launch Typing Test
        with the chosen mode, difficulty, and duration.
        """
        # Save user choices to settings
        settings = storage.load_settings()
        settings["default_mode"] = self.selected_mode
        settings["default_difficulty"] = self.selected_diff
        dur_int = int(self.selected_duration.replace("s", ""))
        settings["default_duration"] = dur_int
        storage.save_settings(settings)

        # Transition directly to typing test
        self.app.show_screen(
            "typing",
            mode=self.selected_mode,
            difficulty=self.selected_diff,
            duration=dur_int,
            preserve_config=True
        )

    def _on_select_passage(self) -> None:
        """Open an interactive Mode & Difficulty configuration and preview modal dialog."""
        from ui.content_generator import ContentGenerator

        dialog = tk.Toplevel(self.app)
        dialog.title("Select Practice Passage")
        dialog.configure(bg=theme.BG_CARD)
        dialog.resizable(False, False)
        dialog.transient(self.app)
        try:
            dialog.grab_set()
        except Exception:
            pass

        w, h = 640, 430
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
            text="Configure Typing Challenge",
            font=theme.FONT_TITLE_SMALL,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Choose your typing mode and difficulty to preview text stream patterns.",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD
        ).pack(anchor="w", pady=(2, theme.SPACE_SM))

        selected_mode = [self.selected_mode]
        selected_diff = [self.selected_diff]
        preview_gen = ContentGenerator(mode=selected_mode[0], difficulty=selected_diff[0])

        mode_row = tk.Frame(content, bg=theme.BG_CARD)
        mode_row.pack(fill="x", pady=(0, theme.SPACE_XS))

        diff_row = tk.Frame(content, bg=theme.BG_CARD)
        diff_row.pack(fill="x", pady=(0, theme.SPACE_MD))

        preview_card = RoundedCard(
            content,
            bg_color=theme.BG_SECONDARY,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.BG_CARD,
            corner_radius=theme.CARD_CORNER_RADIUS,
            padding=theme.SPACE_MD,
            height=130
        )
        preview_card.pack(fill="both", expand=True, pady=(0, theme.SPACE_MD))

        preview_lbl = tk.Label(
            preview_card.inner,
            text="",
            font=theme.FONT_BODY,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_SECONDARY,
            wraplength=560,
            justify="left",
            anchor="nw"
        )
        preview_lbl.pack(fill="both", expand=True)

        def update_preview():
            preview_gen.set_config(selected_mode[0], selected_diff[0])
            snippet = preview_gen.generate_chunk(word_target=30)
            preview_lbl.config(text=snippet)

        def on_mode_changed(val: str):
            selected_mode[0] = val
            update_preview()

        def on_diff_changed(val: str):
            selected_diff[0] = val
            update_preview()

        mode_ctrl = SegmentedControl(
            mode_row,
            options=["Words", "Punctuation", "Capitalization", "Numbers", "Mixed", "Code"],
            initial_selection=selected_mode[0],
            label="MODE",
            on_change=on_mode_changed,
            bg=theme.BG_CARD
        )
        mode_ctrl.pack(side="left")

        diff_ctrl = SegmentedControl(
            diff_row,
            options=["Easy", "Medium", "Hard", "Expert"],
            initial_selection=selected_diff[0],
            label="DIFFICULTY",
            on_change=on_diff_changed,
            bg=theme.BG_CARD
        )
        diff_ctrl.pack(side="left")

        update_preview()

        btn_bar = tk.Frame(content, bg=theme.BG_CARD)
        btn_bar.pack(fill="x", side="bottom")

        def on_start():
            dialog.destroy()
            self.selected_mode = selected_mode[0]
            self.selected_diff = selected_diff[0]
            if hasattr(self, "mode_selector"):
                self.mode_selector.set_selected(self.selected_mode)
            if hasattr(self, "diff_selector"):
                self.diff_selector.set_selected(self.selected_diff)
            self._update_summary()
            self._on_start_test()

        btn_cancel = SecondaryButton(
            btn_bar,
            text="Cancel",
            command=dialog.destroy,
            width=80,
            height=34,
            parent_bg=theme.BG_CARD
        )
        btn_cancel.pack(side="right", padx=(theme.SPACE_SM, 0))

        btn_choose = PrimaryButton(
            btn_bar,
            text="Start With This Configuration",
            icon="▶",
            command=on_start,
            width=220,
            height=34,
            parent_bg=theme.BG_CARD
        )
        btn_choose.pack(side="right")

    # ========================================================================
    # SECTION C: PERFORMANCE OVERVIEW
    # ========================================================================

    def _build_stats_section(self) -> None:
        """Row of 4 metric cards summarizing personal typing statistics."""
        section_label = tk.Label(
            self.content_padding_frame,
            text="YOUR PERFORMANCE OVERVIEW",
            font=theme.FONT_STAT_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        )
        section_label.pack(anchor="w", pady=(0, theme.SPACE_XS))

        stats_grid = tk.Frame(self.content_padding_frame, bg=theme.BG_PRIMARY)
        stats_grid.pack(fill="x", pady=(0, theme.SPACE_MD))

        # Configure 4 equal-width responsive columns
        for col_idx in range(4):
            stats_grid.grid_columnconfigure(col_idx, weight=1, uniform="stat_col")

        self.card_best_speed = StatCard(
            stats_grid,
            title="Personal Best",
            value="--",
            unit="WPM",
            subtitle="Personal high score",
            icon="🏆",
            accent_color=theme.COLOR_SUCCESS,
            parent_bg=theme.BG_PRIMARY
        )
        self.card_best_speed.grid(row=0, column=0, padx=(0, theme.SPACE_SM), sticky="nsew")

        self.card_avg_speed = StatCard(
            stats_grid,
            title="Average Speed",
            value="--",
            unit="WPM",
            subtitle="Overall average rate",
            icon="⚡",
            accent_color=theme.ACCENT_PRIMARY,
            parent_bg=theme.BG_PRIMARY
        )
        self.card_avg_speed.grid(row=0, column=1, padx=(theme.SPACE_XS, theme.SPACE_SM), sticky="nsew")

        self.card_accuracy = StatCard(
            stats_grid,
            title="Accuracy",
            value="--",
            unit="%",
            subtitle="Precision index",
            icon="🎯",
            accent_color=theme.TEXT_PRIMARY,
            parent_bg=theme.BG_PRIMARY
        )
        self.card_accuracy.grid(row=0, column=2, padx=(theme.SPACE_SM, theme.SPACE_XS), sticky="nsew")

        self.card_tests = StatCard(
            stats_grid,
            title="Tests Completed",
            value="0",
            unit="Tests",
            subtitle="Lifetime session count",
            icon="📊",
            accent_color=theme.TEXT_PRIMARY,
            parent_bg=theme.BG_PRIMARY
        )
        self.card_tests.grid(row=0, column=3, padx=(theme.SPACE_SM, 0), sticky="nsew")

    # ========================================================================
    # SECTION D & E: SPEED PROGRESSION CHART & RECENT ACTIVITY
    # ========================================================================

    def _build_lower_section(self) -> None:
        """
        Two-column lower section:
        Left Column: PerformanceTrendCanvas line graph.
        Right Column: RecentActivityList with click-to-inspect and View All History.
        """
        lower_grid = tk.Frame(self.content_padding_frame, bg=theme.BG_PRIMARY)
        lower_grid.pack(fill="x", pady=(0, theme.SPACE_MD))
        lower_grid.grid_columnconfigure(0, weight=1, uniform="lower_col")
        lower_grid.grid_columnconfigure(1, weight=1, uniform="lower_col")

        # Left Column: Speed progression graph
        self.trend_card = PerformanceTrendCanvas(
            lower_grid,
            height=230,
            parent_bg=theme.BG_PRIMARY
        )
        self.trend_card.grid(row=0, column=0, padx=(0, theme.SPACE_SM), sticky="nsew")

        # Right Column: Recent activity feed
        self.activity_card = RecentActivityList(
            lower_grid,
            height=230,
            on_inspect=self._on_inspect_session,
            on_view_all=lambda: self.app.show_screen("history"),
            parent_bg=theme.BG_PRIMARY
        )
        self.activity_card.grid(row=0, column=1, padx=(theme.SPACE_SM, 0), sticky="nsew")

    def _on_inspect_session(self, session_data: dict) -> None:
        """Navigate to Results screen to inspect a past session's performance report."""
        self.app.show_screen("results", session_result=session_data, is_historical=True)

    # ========================================================================
    # SECTION F: CONTEXTUAL TIP CARD
    # ========================================================================

    def _build_tip_section(self) -> None:
        """Subtle tip card at the bottom of the dashboard."""
        self.tip_card = GlassCard(
            self.content_padding_frame,
            bg_color=theme.SURFACE_GLASS,
            border_color=theme.SURFACE_GLASS_BORDER,
            highlight_color=theme.SURFACE_GLASS_HIGHLIGHT,
            parent_bg=theme.BG_PRIMARY,
            corner_radius=theme.RADIUS_MD,
            padding=theme.SPACE_MD,
            height=54
        )
        self.tip_card.pack(fill="x", pady=(0, theme.SPACE_MD))

        tip_inner = self.tip_card.inner
        tip_icon = tk.Label(
            tip_inner,
            text="💡",
            font=theme.FONT_BODY,
            fg=theme.TEXT_PRIMARY,
            bg=theme.SURFACE_GLASS
        )
        tip_icon.pack(side="left", padx=(0, theme.SPACE_SM))

        tip_text = tk.Label(
            tip_inner,
            text="Practice tip: Prioritize rhythm and accuracy over raw speed. Smooth typing cadence naturally unlocks higher velocity over time.",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_SECONDARY,
            bg=theme.SURFACE_GLASS
        )
        tip_text.pack(side="left")

    def set_tips_visible(self, visible: bool) -> None:
        """Dynamically toggle practice tip visibility based on user settings."""
        if hasattr(self, "tip_card"):
            if visible:
                if not self.tip_card.winfo_manager():
                    self.tip_card.pack(fill="x", pady=(0, theme.SPACE_MD))
            else:
                self.tip_card.pack_forget()

    # ========================================================================
    # LIFECYCLE & DATA BINDING
    # ========================================================================

    def on_show(self, **kwargs) -> None:
        """Refresh personal statistics, trend chart, recent activity, and tip visibility."""
        super().on_show(**kwargs)
        try:
            self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        except Exception:
            pass
        self.update_statistics()

        # Update tip visibility from settings
        settings = storage.load_settings()
        self.set_tips_visible(settings.get("show_tips", True))

        # Sync selectors if updated from settings
        if not kwargs.get("preserve_config", False):
            mode = settings.get("default_mode", self.selected_mode)
            diff = settings.get("default_difficulty", self.selected_diff)
            dur = f"{settings.get('default_duration', 60)}s"

            self.selected_mode = mode
            self.selected_diff = diff
            self.selected_duration = dur

            if hasattr(self, "mode_selector"):
                self.mode_selector.set_selected(mode)
            if hasattr(self, "diff_selector"):
                self.diff_selector.set_selected(diff)
            if hasattr(self, "duration_selector"):
                self.duration_selector.set_selected(dur)
            self._update_summary()

    def on_hide(self) -> None:
        """Unbind mousewheel when leaving the home dashboard."""
        super().on_hide()
        try:
            self.scroll_canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass

    def update_statistics(self) -> None:
        """Fetch latest aggregate metrics and session records from storage."""
        stats = storage.get_personal_statistics()
        sessions = storage.load_all_sessions()
        total = stats.get("total_tests", 0)

        # Update Metric Cards
        if total > 0:
            self.card_best_speed.set_value(f"{stats['personal_best']}", subtitle="Personal record")
            self.card_avg_speed.set_value(f"{stats['average_wpm']}", subtitle="Lifetime average")
            self.card_accuracy.set_value(f"{int(round(stats['average_accuracy']))}", subtitle="Average precision")
            self.card_tests.set_value(f"{total}", subtitle="Completed tests")
            if hasattr(self, "status_badge"):
                self.status_badge.set_text(f"{total} TESTS LOGGED")
        else:
            self.card_best_speed.set_value("--", subtitle="No tests yet")
            self.card_avg_speed.set_value("--", subtitle="No tests yet")
            self.card_accuracy.set_value("--", subtitle="No tests yet")
            self.card_tests.set_value("0", subtitle="Start your first test")
            if hasattr(self, "status_badge"):
                self.status_badge.set_text("PRACTICE READY")

        # Update Trend Chart and Recent Activity Feed
        if hasattr(self, "trend_card"):
            self.trend_card.set_sessions(sessions)
        if hasattr(self, "activity_card"):
            self.activity_card.set_sessions(sessions)

    def on_show(self) -> None:
        """Invoked when navigating to Home screen."""
        super().on_show()
        settings = storage.load_settings()
        self.selected_mode = settings.get("default_mode", "Unified")
        self.selected_diff = settings.get("default_difficulty", "Medium")
        dur_int = settings.get("default_duration", 60)
        self.selected_duration = f"{dur_int}s"

        if hasattr(self, "diff_selector") and self.diff_selector:
            self.diff_selector.set_selected(self.selected_diff)
        if hasattr(self, "duration_selector") and self.duration_selector:
            self.duration_selector.set_selected(self.selected_duration)
        self._update_summary()
        self.update_statistics()

    def _on_edition_changed_bg(self, new_ed: str, old_ed: str, colors: Dict[str, str]) -> None:
        """Update scrollable container backgrounds when edition theme shifts."""
        super()._on_edition_changed_bg(new_ed, old_ed, colors)
        bg = colors.get("bg_primary", theme.BG_PRIMARY)
        if hasattr(self, "scroll_canvas"):
            self.scroll_canvas.config(bg=bg)
        if hasattr(self, "container"):
            self.container.config(bg=bg)
        if hasattr(self, "content_padding_frame"):
            self.content_padding_frame.config(bg=bg)
