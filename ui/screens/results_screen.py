"""
TypeRush 2.0 Results Screen & Advanced Performance Analytics
Midnight Studio Design Identity

Provides a comprehensive, editorial-grade performance report presenting:
- Section A: Performance Hero (Dominant Net WPM, Accuracy, Context Badge, Personal Best detection)
- Section B: Key Performance Metrics (8-metric responsive grid with Net/Gross WPM, Accuracy, Errors, Word/Char counts)
- Section C: Speed Progression Canvas Chart (Real-time speed curve, spline smoothing, peak/average indicators)
- Section D: Accuracy & Error Typing Breakdown (Character ratio bar, substitutions, insertions, omissions)
- Section E: Mistake Review (Cascade-immune word discrepancy analysis with diff highlighting and flaw categorization)
- Section F: Mode-Specific Analysis (Dynamic contextual insights tailored to Words, Punctuation, Capitalization, Numbers, Mixed, Code)
- Section G: Consistency & Rhythm (Documented standard deviation, CV %, and cadence stability score)
- Section H: Action Buttons & Dynamic Practice Suggestions (Retry Test, New Passage, View History, Return Home)
- Full Three-Edition Support (Pleasant, Basic, Soundscape)
- Responsive Layout (Optimized for 1200x800 and 950x650 bounds with smooth scrollable canvas)
"""

import tkinter as tk
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any, List, Tuple
from ui import theme
from ui import storage

if TYPE_CHECKING:
    from ui.app import TypeRushApp
from ui import scoring
from ui.components import (
    Badge,
    PrimaryButton,
    SecondaryButton,
    WpmLineGraph,
    AccuracyBreakdownBar,
    RoundedCard,
)
from ui.screens.base_screen import BaseScreen


class ResultsScreen(BaseScreen):
    """
    High-fidelity typing analytics and performance report screen (Midnight Studio).
    """
    SCREEN_NAME = "results"

    def __init__(self, parent: tk.Widget, app: "TypeRushApp", **kwargs):
        super().__init__(parent, app, **kwargs)

        self.session_data: Optional[Dict[str, Any]] = None
        self.is_historical_view: bool = False

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the scrollable results workspace container."""
        # Attach responsive atmospheric background
        self.setup_background("results")

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

        # 1. Empty State View (Shown when no session has been run)
        self._build_empty_state()

        # 2. Active Performance Report View (Populated with real data)
        self._build_report_view()

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
        """Tasteful placeholder shown when navigated to directly without taking a test."""
        self.empty_frame = tk.Frame(self.container, bg=theme.BG_MAIN)
        # Not packed initially

        card = RoundedCard(
            self.empty_frame,
            bg_color=theme.BG_CARD,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.BG_MAIN,
            corner_radius=theme.CARD_CORNER_RADIUS,
            padding=theme.SPACE_2XL,
            height=360
        )
        card.pack(fill="both", expand=True, padx=theme.SPACE_XL, pady=theme.SPACE_XL)

        inner = card.inner

        badge = Badge(
            inner,
            text="PERFORMANCE REPORT",
            bg_color=theme.BG_SURFACE,
            text_color=theme.ACCENT_PRIMARY,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.BG_CARD
        )
        badge.pack(anchor="w", pady=(0, theme.SPACE_MD))

        title = tk.Label(
            inner,
            text="No Recent Test Completed",
            font=theme.FONT_TITLE_LARGE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_CARD
        )
        title.pack(anchor="w")

        desc = tk.Label(
            inner,
            text=(
                "Your comprehensive performance report, Net WPM analytics, real-time speed progression graph, "
                "word-level mistake review, and cadence consistency assessment will appear here as soon as you "
                "complete a typing session."
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
    # ACTIVE PERFORMANCE REPORT VIEW
    # ========================================================================

    def _build_report_view(self) -> None:
        """Construct the comprehensive editorial-style performance report layout."""
        self.report_frame = tk.Frame(self.container, bg=theme.BG_MAIN)
        # Packed when session data is present

        inner_content = tk.Frame(self.report_frame, bg=theme.BG_MAIN, padx=theme.SPACE_LG, pady=theme.SPACE_MD)
        inner_content.pack(fill="both", expand=True)

        # Section A: Header & Performance Hero Card
        self._build_section_a_hero(inner_content)

        # Section B: 8-Metric Performance Grid
        self._build_section_b_metrics(inner_content)

        # Section C: Speed Progression Canvas Chart
        self._build_section_c_graph(inner_content)

        # Section D & G: Accuracy Breakdown & Rhythm Consistency (Two-Column Row)
        self._build_section_d_and_g_row(inner_content)

        # Section E: Mistake Review & Alignment Analysis
        self._build_section_e_mistakes(inner_content)

        # Section F: Mode-Specific Analysis
        self._build_section_f_mode_analysis(inner_content)

        # Section H: Action Buttons & Practice Suggestions
        self._build_section_h_actions(inner_content)

    # ------------------------------------------------------------------------
    # SECTION A: PERFORMANCE HERO & CONTEXT HEADER
    # ------------------------------------------------------------------------

    def _build_section_a_hero(self, parent: tk.Widget) -> None:
        """Section A — Context Header & Dominant Performance Hero Card."""
        header_bar = tk.Frame(parent, bg=theme.BG_MAIN)
        header_bar.pack(fill="x", pady=(0, theme.SPACE_SM))

        left_header = tk.Frame(header_bar, bg=theme.BG_MAIN)
        left_header.pack(side="left")

        title_row = tk.Frame(left_header, bg=theme.BG_MAIN)
        title_row.pack(anchor="w")

        self.title_lbl = tk.Label(
            title_row,
            text="Performance Report",
            font=theme.FONT_TITLE_LARGE,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_MAIN
        )
        self.title_lbl.pack(side="left")

        # Context badge (Mode • Difficulty • Duration)
        self.context_badge = Badge(
            title_row,
            text="MIXED • MEDIUM • 60S",
            bg_color=theme.BG_SURFACE,
            text_color=theme.ACCENT_PRIMARY,
            border_color=theme.BORDER_COLOR,
            parent_bg=theme.BG_MAIN
        )
        self.context_badge.pack(side="left", padx=(theme.SPACE_MD, 0), pady=(2, 0))

        # Personal Best / Historical pill
        self.pb_badge = Badge(
            title_row,
            text="★ NEW PERSONAL BEST!",
            bg_color="#1E3A2F",
            text_color=theme.COLOR_SUCCESS,
            border_color=theme.COLOR_SUCCESS,
            parent_bg=theme.BG_MAIN
        )
        self.pb_badge.pack(side="left", padx=(theme.SPACE_SM, 0), pady=(2, 0))

        self.subtitle_lbl = tk.Label(
            left_header,
            text="Comprehensive speed, precision, and cadence telemetry.",
            font=theme.FONT_BODY,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_MAIN
        )
        self.subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Hero Card Container
        hero_card = tk.Frame(
            parent,
            bg=theme.BG_CARD,
            padx=theme.SPACE_XL,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        hero_card.pack(fill="x", pady=(0, theme.SPACE_MD))

        # Left Column: Dominant Net WPM Hero Score
        left_hero = tk.Frame(hero_card, bg=theme.BG_CARD)
        left_hero.pack(side="left", fill="y", padx=(0, theme.SPACE_XL))

        hero_wpm_row = tk.Frame(left_hero, bg=theme.BG_CARD)
        hero_wpm_row.pack(anchor="w")

        self.lbl_hero_wpm = tk.Label(
            hero_wpm_row,
            text="0",
            font=(theme.FONT_FAMILY, 52, "bold"),
            fg=theme.ACCENT_PRIMARY,
            bg=theme.BG_CARD
        )
        self.lbl_hero_wpm.pack(side="left")

        lbl_wpm_unit = tk.Label(
            hero_wpm_row,
            text=" NET WPM",
            font=(theme.FONT_FAMILY, 14, "bold"),
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD
        )
        lbl_wpm_unit.pack(side="left", padx=(4, 0), pady=(26, 0))

        hero_rating_row = tk.Frame(left_hero, bg=theme.BG_CARD)
        hero_rating_row.pack(anchor="w", pady=(2, 0))

        self.lbl_hero_rating = tk.Label(
            hero_rating_row,
            text="Intermediate",
            font=theme.FONT_BODY_BOLD,
            fg=theme.COLOR_SUCCESS,
            bg=theme.BG_CARD
        )
        self.lbl_hero_rating.pack(side="left")

        self.lbl_pb_comparison = tk.Label(
            hero_rating_row,
            text="+0 WPM above previous record",
            font=theme.FONT_BODY_SMALL,
            fg=theme.ACCENT_SECONDARY,
            bg=theme.BG_CARD
        )
        self.lbl_pb_comparison.pack(side="left", padx=(theme.SPACE_MD, 0))

        self.lbl_hero_desc = tk.Label(
            left_hero,
            text="Solid conversational typing pace with consistent accuracy.",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD,
            wraplength=480,
            justify="left"
        )
        self.lbl_hero_desc.pack(anchor="w", pady=(4, 0))

        # Divider
        divider = tk.Frame(hero_card, bg=theme.BORDER_SUBTLE, width=1)
        divider.pack(side="left", fill="y", padx=(0, theme.SPACE_XL))

        # Right Column: Big Accuracy Callout & Session Summary
        right_hero = tk.Frame(hero_card, bg=theme.BG_CARD)
        right_hero.pack(side="left", fill="both", expand=True)

        callouts_row = tk.Frame(right_hero, bg=theme.BG_CARD)
        callouts_row.pack(anchor="w", fill="x")

        # Accuracy Callout Box
        acc_box = tk.Frame(callouts_row, bg=theme.BG_CARD)
        acc_box.pack(side="left", padx=(0, theme.SPACE_XL))

        tk.Label(acc_box, text="ACCURACY", font=theme.FONT_METRIC_LABEL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")
        self.lbl_hero_acc = tk.Label(acc_box, text="100%", font=(theme.FONT_FAMILY, 32, "bold"), fg=theme.COLOR_SUCCESS, bg=theme.BG_CARD)
        self.lbl_hero_acc.pack(anchor="w")

        # Consistency Callout Box
        cons_box = tk.Frame(callouts_row, bg=theme.BG_CARD)
        cons_box.pack(side="left", padx=(0, theme.SPACE_XL))

        tk.Label(cons_box, text="RHYTHM STABILITY", font=theme.FONT_METRIC_LABEL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")
        self.lbl_hero_cons = tk.Label(cons_box, text="100%", font=(theme.FONT_FAMILY, 32, "bold"), fg=theme.ACCENT_SECONDARY, bg=theme.BG_CARD)
        self.lbl_hero_cons.pack(anchor="w")

        # Session Time & Meta
        self.lbl_hero_meta = tk.Label(
            right_hero,
            text="60.0s elapsed  •  Reason: Time Expired  •  All systems verified",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        )
        self.lbl_hero_meta.pack(anchor="w", pady=(theme.SPACE_SM, 0))

    # ------------------------------------------------------------------------
    # SECTION B: 8-METRIC PERFORMANCE GRID
    # ------------------------------------------------------------------------

    def _build_section_b_metrics(self, parent: tk.Widget) -> None:
        """Section B — Balanced Responsive 8-Metric Performance Grid."""
        grid_container = tk.Frame(parent, bg=theme.BG_MAIN)
        grid_container.pack(fill="x", pady=(0, theme.SPACE_MD))

        for col in range(4):
            grid_container.grid_columnconfigure(col, weight=1, uniform="stat_cols")

        # Metric definitions: (label, initial_val, caption, color)
        self.metric_cards = {}

        metrics_config = [
            (0, 0, "net_speed", "NET SPEED", "0 WPM", "Adjusted words per minute", theme.ACCENT_PRIMARY),
            (0, 1, "gross_speed", "GROSS SPEED", "0 WPM", "Raw keystroke velocity", theme.TEXT_PRIMARY),
            (0, 2, "accuracy", "ACCURACY", "100%", "Correct keystroke precision", theme.COLOR_SUCCESS),
            (0, 3, "errors", "TOTAL ERRORS", "0", "Discrepant keystrokes", theme.COLOR_ERROR),
            (1, 0, "correct_words", "CORRECT WORDS", "0", "Accurate word tokens", theme.COLOR_SUCCESS),
            (1, 1, "incorrect_words", "INCORRECT WORDS", "0", "Words with mistakes", theme.COLOR_ERROR),
            (1, 2, "correct_chars", "CORRECT CHARS", "0", "Accurate characters", theme.TEXT_PRIMARY),
            (1, 3, "incorrect_chars", "INCORRECT CHARS", "0", "Erroneous characters", theme.TEXT_MUTED),
        ]

        for row, col, key, title, val, caption, fg_color in metrics_config:
            cell = tk.Frame(
                grid_container,
                bg=theme.BG_CARD,
                padx=theme.SPACE_MD,
                pady=theme.SPACE_SM,
                highlightbackground=theme.BORDER_COLOR,
                highlightthickness=1
            )
            padx_tuple = (0 if col == 0 else theme.SPACE_XS, 0 if col == 3 else theme.SPACE_XS)
            pady_tuple = (0, theme.SPACE_XS if row == 0 else 0)
            cell.grid(row=row, column=col, sticky="nsew", padx=padx_tuple, pady=pady_tuple)

            tk.Label(cell, text=title, font=theme.FONT_METRIC_LABEL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD).pack(anchor="w")

            val_lbl = tk.Label(cell, text=val, font=theme.FONT_METRIC_VALUE, fg=fg_color, bg=theme.BG_CARD)
            val_lbl.pack(anchor="w", pady=(2, 0))

            cap_lbl = tk.Label(cell, text=caption, font=theme.FONT_BODY_SMALL, fg=theme.TEXT_MUTED, bg=theme.BG_CARD)
            cap_lbl.pack(anchor="w", pady=(2, 0))

            self.metric_cards[key] = (val_lbl, cap_lbl)

        # Compatibility references
        self.val_net_speed = self.metric_cards["net_speed"][0]
        self.val_gross_speed = self.metric_cards["gross_speed"][0]
        self.val_accuracy = self.metric_cards["accuracy"][0]
        self.val_errors = self.metric_cards["errors"][0]

    # ------------------------------------------------------------------------
    # SECTION C: SPEED PROGRESSION CANVAS CHART
    # ------------------------------------------------------------------------

    def _build_section_c_graph(self, parent: tk.Widget) -> None:
        """Section C — Custom Canvas Line Graph of Speed Progression."""
        graph_header = tk.Frame(parent, bg=theme.BG_MAIN)
        graph_header.pack(fill="x", pady=(0, theme.SPACE_XS))

        lbl_graph_title = tk.Label(
            graph_header,
            text="SPEED PROGRESSION (WPM OVER TIME)",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_MAIN
        )
        lbl_graph_title.pack(side="left")

        lbl_graph_sub = tk.Label(
            graph_header,
            text="Smooth velocity curve sampled at active intervals",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_MAIN
        )
        lbl_graph_sub.pack(side="right")

        self.wpm_graph = WpmLineGraph(
            parent,
            height=165,
            bg_color=theme.BG_CARD,
            parent_bg=theme.BG_MAIN
        )
        self.wpm_graph.pack(fill="x", pady=(0, theme.SPACE_MD))

    # ------------------------------------------------------------------------
    # SECTION D & G: ACCURACY BREAKDOWN & RHYTHM CONSISTENCY
    # ------------------------------------------------------------------------

    def _build_section_d_and_g_row(self, parent: tk.Widget) -> None:
        """Section D & G — Side-by-Side Accuracy Breakdown & Consistency Analysis."""
        row_frame = tk.Frame(parent, bg=theme.BG_MAIN)
        row_frame.pack(fill="x", pady=(0, theme.SPACE_MD))

        row_frame.grid_columnconfigure(0, weight=1, uniform="mid_cols")
        row_frame.grid_columnconfigure(1, weight=1, uniform="mid_cols")

        # --- Section D: Accuracy & Error Typing Breakdown ---
        box_d = tk.Frame(
            row_frame,
            bg=theme.BG_CARD,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        box_d.grid(row=0, column=0, sticky="nsew", padx=(0, theme.SPACE_SM))

        tk.Label(
            box_d,
            text="ACCURACY & ERROR BREAKDOWN",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        self.accuracy_bar = AccuracyBreakdownBar(box_d, height=8, parent_bg=theme.BG_CARD)
        self.accuracy_bar.pack(fill="x", pady=(theme.SPACE_SM, theme.SPACE_SM))

        # Error Category Pills
        pills_row = tk.Frame(box_d, bg=theme.BG_CARD)
        pills_row.pack(fill="x", pady=(0, theme.SPACE_SM))

        self.lbl_substitutions = tk.Label(
            pills_row,
            text="Substitutions: 0",
            font=theme.FONT_BODY_SMALL_BOLD,
            fg=theme.COLOR_ERROR,
            bg=theme.BG_CARD
        )
        self.lbl_substitutions.pack(side="left", padx=(0, theme.SPACE_MD))

        self.lbl_insertions = tk.Label(
            pills_row,
            text="Extra Chars: 0",
            font=theme.FONT_BODY_SMALL_BOLD,
            fg=theme.COLOR_WARNING,
            bg=theme.BG_CARD
        )
        self.lbl_insertions.pack(side="left", padx=(0, theme.SPACE_MD))

        self.lbl_omissions = tk.Label(
            pills_row,
            text="Missing Chars: 0",
            font=theme.FONT_BODY_SMALL_BOLD,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        )
        self.lbl_omissions.pack(side="left")

        # Stats summary row (compatibility)
        breakdown_row = tk.Frame(box_d, bg=theme.BG_CARD)
        breakdown_row.pack(fill="x")

        self.lbl_correct_chars = tk.Label(
            breakdown_row,
            text="Correct: 0",
            font=theme.FONT_BODY_SMALL,
            fg=theme.COLOR_SUCCESS,
            bg=theme.BG_CARD
        )
        self.lbl_correct_chars.pack(side="left", padx=(0, theme.SPACE_MD))

        self.lbl_incorrect_chars = tk.Label(
            breakdown_row,
            text="Errors: 0",
            font=theme.FONT_BODY_SMALL,
            fg=theme.COLOR_ERROR,
            bg=theme.BG_CARD
        )
        self.lbl_incorrect_chars.pack(side="left", padx=(0, theme.SPACE_MD))

        self.lbl_total_chars = tk.Label(
            breakdown_row,
            text="Total: 0",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        )
        self.lbl_total_chars.pack(side="right")

        # --- Section G: Consistency & Rhythm Analysis ---
        box_g = tk.Frame(
            row_frame,
            bg=theme.BG_CARD,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        box_g.grid(row=0, column=1, sticky="nsew", padx=(theme.SPACE_SM, 0))

        tk.Label(
            box_g,
            text="CADENCE CONSISTENCY & RHYTHM",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        cons_stat_row = tk.Frame(box_g, bg=theme.BG_CARD)
        cons_stat_row.pack(fill="x", pady=(theme.SPACE_SM, 0))

        self.lbl_cons_score = tk.Label(
            cons_stat_row,
            text="100%",
            font=theme.FONT_METRIC_VALUE,
            fg=theme.ACCENT_PRIMARY,
            bg=theme.BG_CARD
        )
        self.lbl_cons_score.pack(side="left")

        self.lbl_cons_rating = tk.Label(
            cons_stat_row,
            text="High Stability (Steady pacing)",
            font=theme.FONT_BODY_BOLD,
            fg=theme.COLOR_SUCCESS,
            bg=theme.BG_CARD
        )
        self.lbl_cons_rating.pack(side="left", padx=(theme.SPACE_MD, 0), pady=(4, 0))

        self.lbl_cons_formula = tk.Label(
            box_g,
            text="Formula: 100 - (σ / μ × 100) via standard Coefficient of Variation",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        )
        self.lbl_cons_formula.pack(anchor="w", pady=(theme.SPACE_XS, 0))

        self.lbl_cons_details = tk.Label(
            box_g,
            text="Mean: 0.0 WPM   •   Std Dev: σ = 0.0 WPM",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD
        )
        self.lbl_cons_details.pack(anchor="w", pady=(2, 0))

    # ------------------------------------------------------------------------
    # SECTION E: MISTAKE REVIEW & WORD ALIGNMENT
    # ------------------------------------------------------------------------

    def _build_section_e_mistakes(self, parent: tk.Widget) -> None:
        """Section E — Word-Level Mistake Review & Cascade-Immune Alignment Analysis."""
        header_e = tk.Frame(parent, bg=theme.BG_MAIN)
        header_e.pack(fill="x", pady=(0, theme.SPACE_XS))

        tk.Label(
            header_e,
            text="MISTAKE REVIEW & WORD ALIGNMENT",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_MAIN
        ).pack(side="left")

        self.lbl_mistake_count = tk.Label(
            header_e,
            text="0 Discrepancies",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_MAIN
        )
        self.lbl_mistake_count.pack(side="right")

        self.mistakes_container = tk.Frame(
            parent,
            bg=theme.BG_CARD,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        self.mistakes_container.pack(fill="x", pady=(0, theme.SPACE_MD))

        # Placeholder widgets inside mistakes container
        self.mistakes_inner = tk.Frame(self.mistakes_container, bg=theme.BG_CARD)
        self.mistakes_inner.pack(fill="x")

    # ------------------------------------------------------------------------
    # SECTION F: MODE-SPECIFIC ANALYSIS
    # ------------------------------------------------------------------------

    def _build_section_f_mode_analysis(self, parent: tk.Widget) -> None:
        """Section F — Dynamic Contextual Analysis Tailored to Mode."""
        self.mode_analysis_box = tk.Frame(
            parent,
            bg=theme.BG_CARD,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        self.mode_analysis_box.pack(fill="x", pady=(0, theme.SPACE_MD))

        tk.Label(
            self.mode_analysis_box,
            text="MODE-SPECIFIC TELEMETRY & INSIGHTS",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        self.lbl_mode_title = tk.Label(
            self.mode_analysis_box,
            text="Mixed Mode Analysis",
            font=theme.FONT_BODY_BOLD,
            fg=theme.ACCENT_PRIMARY,
            bg=theme.BG_CARD
        )
        self.lbl_mode_title.pack(anchor="w", pady=(theme.SPACE_XS, 0))

        self.lbl_mode_desc = tk.Label(
            self.mode_analysis_box,
            text="Evaluates real-world typing agility across alternating words, symbols, and punctuation.",
            font=theme.FONT_BODY,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD,
            wraplength=800,
            justify="left"
        )
        self.lbl_mode_desc.pack(anchor="w", pady=(2, 0))

        self.lbl_mode_tips = tk.Label(
            self.mode_analysis_box,
            text="Tip: Steady cadence around symbol transitions prevents error bursts.",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_CARD
        )
        self.lbl_mode_tips.pack(anchor="w", pady=(theme.SPACE_XS, 0))

    # ------------------------------------------------------------------------
    # SECTION H: ACTION BUTTONS & PRACTICE SUGGESTIONS
    # ------------------------------------------------------------------------

    def _build_section_h_actions(self, parent: tk.Widget) -> None:
        """Section H — Actionable Next Steps & Contextual Practice Advice."""
        advice_box = tk.Frame(
            parent,
            bg=theme.SURFACE_ELEVATED,
            padx=theme.SPACE_MD,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        advice_box.pack(fill="x", pady=(0, theme.SPACE_MD))

        tk.Label(
            advice_box,
            text="PRACTICE RECOMMENDATION",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.ACCENT_SECONDARY,
            bg=theme.SURFACE_ELEVATED
        ).pack(anchor="w")

        self.lbl_practice_advice = tk.Label(
            advice_box,
            text="Focus on maintaining a steady rhythm before accelerating velocity.",
            font=theme.FONT_BODY,
            fg=theme.TEXT_PRIMARY,
            bg=theme.SURFACE_ELEVATED,
            wraplength=800,
            justify="left"
        )
        self.lbl_practice_advice.pack(anchor="w", pady=(2, 0))

        # Four Navigation Action Buttons
        actions_bar = tk.Frame(parent, bg=theme.BG_MAIN)
        actions_bar.pack(fill="x", pady=(theme.SPACE_XS, theme.SPACE_LG))

        # 1. Retry Test (same config)
        self.btn_try_again = PrimaryButton(
            actions_bar,
            text="Retry Test",
            icon="↻",
            command=self._on_try_again,
            width=140,
            height=40,
            parent_bg=theme.BG_MAIN
        )
        self.btn_try_again.pack(side="left")

        # 2. New Test (cycle passage)
        self.btn_new_test = SecondaryButton(
            actions_bar,
            text="New Passage",
            icon="▶",
            command=self._on_new_test,
            width=140,
            height=40,
            parent_bg=theme.BG_MAIN
        )
        self.btn_new_test.pack(side="left", padx=(theme.SPACE_MD, 0))

        # 3. View History
        self.btn_history = SecondaryButton(
            actions_bar,
            text="View History",
            icon="⏱",
            command=self._on_view_history,
            width=140,
            height=40,
            parent_bg=theme.BG_MAIN
        )
        self.btn_history.pack(side="left", padx=(theme.SPACE_MD, 0))

        # 4. Return Home
        self.btn_home = SecondaryButton(
            actions_bar,
            text="Return Home",
            icon="⌂",
            command=self._on_return_home,
            width=140,
            height=40,
            parent_bg=theme.BG_MAIN
        )
        self.btn_home.pack(side="left", padx=(theme.SPACE_MD, 0))

    # ========================================================================
    # DATA BINDING & LIFECYCLE
    # ========================================================================

    def on_show(self, **kwargs) -> None:
        """
        Called when screen becomes visible.
        Extracts session_result or cached session and populates all analytics.
        """
        super().on_show(**kwargs)

        # Bind mousewheel for smooth navigation
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        session_result = kwargs.get("session_result") or kwargs.get("session_data")
        is_historical = kwargs.get("is_historical", False)

        if session_result is not None:
            self.session_data = session_result
            self.is_historical_view = is_historical
            self._render_report(session_result, is_historical=is_historical)
        elif self.session_data is not None:
            # Re-render previous cached session
            self._render_report(self.session_data, is_historical=self.is_historical_view)
        else:
            # Show empty state
            self.report_frame.pack_forget()
            self.empty_frame.pack(fill="both", expand=True)

        # Reset scroll position to top
        self.scroll_canvas.yview_moveto(0.0)

    def on_hide(self) -> None:
        """Unbind mousewheel when leaving the screen."""
        super().on_hide()
        try:
            self.scroll_canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass

    def _render_report(self, data: Dict[str, Any], is_historical: bool = False) -> None:
        """Populate report widgets with authentic performance telemetry."""
        self.empty_frame.pack_forget()
        self.report_frame.pack(fill="both", expand=True)

        net_wpm = data.get("net_wpm", 0)
        gross_wpm = data.get("gross_wpm", 0)
        accuracy = data.get("accuracy", 100.0)
        errors = data.get("error_count", 0)
        correct_chars = data.get("correct_chars", 0)
        incorrect_chars = data.get("incorrect_chars", 0)
        total_chars = data.get("total_chars", 0)
        correct_words = data.get("correct_words", 0)
        incorrect_words = data.get("incorrect_words", 0)
        rating = data.get("rating", "Intermediate")
        rating_desc = data.get("rating_desc", "")
        duration = data.get("selected_duration", 60)
        elapsed = data.get("elapsed_seconds", 0.0)
        difficulty = data.get("difficulty", "Medium")
        mode = data.get("mode", "Mixed")
        reason = data.get("completed_reason", "Time Expired")
        samples = data.get("wpm_samples", [])
        substitutions = data.get("substitutions", 0)
        insertions = data.get("insertions", 0)
        omissions = data.get("omissions", 0)
        mistakes = data.get("mistakes", [])

        # Consistency calculation
        if "consistency" in data and data["consistency"] is not None:
            consistency_pct = data["consistency"]
            consistency_rating = data.get("consistency_rating", "Stable")
            std_dev = data.get("std_dev", 0.0)
            mean_wpm = data.get("mean_wpm", float(net_wpm))
        else:
            consistency_pct, consistency_rating, std_dev, mean_wpm = scoring.calculate_consistency(samples)

        # --------------------------------------------------------------------
        # SECTION A: HERO & CONTEXT
        # --------------------------------------------------------------------
        badge_text = f"{mode.upper()} • {difficulty.upper()} • {duration}S"
        self.context_badge.set_text(badge_text)

        # Personal Best Detection (Honest, data-driven calculation)
        self._evaluate_personal_best_badge(data, net_wpm, is_historical)

        self.lbl_hero_wpm.config(text=str(net_wpm))
        self.lbl_hero_rating.config(text=rating)
        self.lbl_hero_desc.config(text=rating_desc)
        self.lbl_hero_acc.config(text=f"{int(round(accuracy))}%")
        self.lbl_hero_cons.config(text=f"{consistency_pct}%")
        self.lbl_hero_meta.config(
            text=f"{elapsed}s elapsed   •   Reason: {reason}   •   Mode: {mode} ({difficulty})"
        )

        # --------------------------------------------------------------------
        # SECTION B: 8-METRIC GRID
        # --------------------------------------------------------------------
        self.metric_cards["net_speed"][0].config(text=f"{net_wpm} WPM")
        self.metric_cards["gross_speed"][0].config(text=f"{gross_wpm} WPM")
        self.metric_cards["accuracy"][0].config(text=f"{int(round(accuracy))}%")
        self.metric_cards["errors"][0].config(text=str(errors))
        self.metric_cards["correct_words"][0].config(text=str(correct_words))
        self.metric_cards["incorrect_words"][0].config(text=str(incorrect_words))
        self.metric_cards["correct_chars"][0].config(text=str(correct_chars))
        self.metric_cards["incorrect_chars"][0].config(text=str(incorrect_chars))

        # --------------------------------------------------------------------
        # SECTION C: SPEED PROGRESSION
        # --------------------------------------------------------------------
        self.wpm_graph.set_samples(samples)

        # --------------------------------------------------------------------
        # SECTION D: ACCURACY & ERROR BREAKDOWN
        # --------------------------------------------------------------------
        self.accuracy_bar.set_data(correct=correct_chars, incorrect=errors)
        self.lbl_substitutions.config(text=f"Substitutions: {substitutions}")
        self.lbl_insertions.config(text=f"Extra Chars: {insertions}")
        self.lbl_omissions.config(text=f"Missing Chars: {omissions}")
        self.lbl_correct_chars.config(text=f"Correct: {correct_chars}")
        self.lbl_incorrect_chars.config(text=f"Errors: {errors}")
        self.lbl_total_chars.config(text=f"Total: {total_chars}")

        # --------------------------------------------------------------------
        # SECTION G: CONSISTENCY & RHYTHM
        # --------------------------------------------------------------------
        self.lbl_cons_score.config(text=f"{consistency_pct}%")
        self.lbl_cons_rating.config(text=consistency_rating)
        self.lbl_cons_details.config(text=f"Mean: {mean_wpm} WPM   •   Std Dev: σ = {std_dev} WPM")

        # --------------------------------------------------------------------
        # SECTION E: MISTAKE REVIEW
        # --------------------------------------------------------------------
        self._render_mistake_review(mistakes, errors)

        # --------------------------------------------------------------------
        # SECTION F: MODE-SPECIFIC ANALYSIS
        # --------------------------------------------------------------------
        self._render_mode_analysis(mode, difficulty, accuracy, net_wpm)

        # --------------------------------------------------------------------
        # SECTION H: PRACTICE RECOMMENDATION
        # --------------------------------------------------------------------
        self._render_practice_advice(accuracy, net_wpm, consistency_pct, mode, errors)

    def _evaluate_personal_best_badge(self, current_session: Dict[str, Any], net_wpm: int, is_historical: bool) -> None:
        """Determine whether this session achieves a genuine Personal Best record."""
        if is_historical:
            date_str = current_session.get("date", "")
            formatted_date = ""
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str)
                    formatted_date = dt.strftime("%b %d, %Y · %H:%M")
                except Exception:
                    formatted_date = date_str[:16]
            self.pb_badge.set_text(f"HISTORICAL REPORT {('• ' + formatted_date) if formatted_date else ''}")
            self.lbl_pb_comparison.config(text="Historical snapshot", fg=theme.TEXT_MUTED)
            return

        # Check against real saved sessions
        all_sessions = storage.load_all_sessions()
        curr_id = current_session.get("id")
        # Exclude the current session from comparison
        prior_sessions = [s for s in all_sessions if s.get("id") != curr_id]

        if not prior_sessions:
            self.pb_badge.set_text("FIRST BENCHMARK SET")
            self.lbl_pb_comparison.config(text="Inaugural session recorded", fg=theme.ACCENT_SECONDARY)
            return

        prior_best = max((s.get("net_wpm", 0) for s in prior_sessions), default=0)

        if net_wpm > prior_best:
            diff = net_wpm - prior_best
            self.pb_badge.set_text("★ NEW PERSONAL BEST!")
            self.lbl_pb_comparison.config(
                text=f"+{diff} WPM above previous record ({prior_best} WPM)",
                fg=theme.COLOR_SUCCESS
            )
        else:
            self.pb_badge.set_text("SESSION COMPLETED")
            self.lbl_pb_comparison.config(
                text=f"Current Record: {prior_best} WPM",
                fg=theme.TEXT_MUTED
            )

    def _render_mistake_review(self, mistakes: List[Dict[str, Any]], total_errors: int) -> None:
        """Render detailed word-level discrepancies with cascade-immune alignment."""
        for widget in self.mistakes_inner.winfo_children():
            widget.destroy()

        if total_errors == 0 and len(mistakes) == 0:
            # Flawless performance celebration
            flawless_card = tk.Frame(self.mistakes_inner, bg=theme.BG_CARD)
            flawless_card.pack(fill="x", pady=theme.SPACE_XS)

            tk.Label(
                flawless_card,
                text="★ FLAWLESS PRECISION — ZERO MISTAKES",
                font=theme.FONT_BODY_BOLD,
                fg=theme.COLOR_SUCCESS,
                bg=theme.BG_CARD
            ).pack(anchor="w")

            tk.Label(
                flawless_card,
                text="Every character and word matched the target passage perfectly without a single substitution or omission.",
                font=theme.FONT_BODY_SMALL,
                fg=theme.TEXT_MUTED,
                bg=theme.BG_CARD
            ).pack(anchor="w", pady=(2, 0))

            self.lbl_mistake_count.config(text="0 Discrepancies")
            return

        self.lbl_mistake_count.config(text=f"{len(mistakes)} Mistyped Words ({total_errors} Chars)")

        # Display up to 8 mistakes cleanly
        display_limit = 8
        items_to_show = mistakes[:display_limit]

        for m in items_to_show:
            m_row = tk.Frame(self.mistakes_inner, bg=theme.BG_CARD)
            m_row.pack(fill="x", pady=(2, 2))

            # Word index pill
            w_idx = m.get("word_index", 0) + 1
            idx_badge = Badge(
                m_row,
                text=f"WORD #{w_idx}",
                bg_color=theme.BG_SURFACE,
                text_color=theme.TEXT_MUTED,
                border_color=theme.BORDER_COLOR,
                parent_bg=theme.BG_CARD
            )
            idx_badge.pack(side="left", padx=(0, theme.SPACE_MD))

            # Expected word (Green)
            exp_text = m.get("expected", "")
            tk.Label(
                m_row,
                text=f'"{exp_text}"',
                font=theme.FONT_CODE,
                fg=theme.COLOR_SUCCESS,
                bg=theme.BG_CARD
            ).pack(side="left")

            # Arrow
            tk.Label(
                m_row,
                text=" → ",
                font=theme.FONT_BODY,
                fg=theme.TEXT_MUTED,
                bg=theme.BG_CARD
            ).pack(side="left")

            # Typed word (Red)
            typ_text = m.get("typed", "")
            tk.Label(
                m_row,
                text=f'"{typ_text}"' if typ_text else "(omitted)",
                font=theme.FONT_CODE,
                fg=theme.COLOR_ERROR,
                bg=theme.BG_CARD
            ).pack(side="left")

            # Error Category Tag
            cat = m.get("category", "Error")
            cat_badge = Badge(
                m_row,
                text=cat.upper(),
                bg_color=theme.BG_SURFACE,
                text_color=theme.COLOR_ERROR if cat == "Substitution" else theme.COLOR_WARNING,
                border_color=theme.BORDER_COLOR,
                parent_bg=theme.BG_CARD
            )
            cat_badge.pack(side="right")

        if len(mistakes) > display_limit:
            remaining = len(mistakes) - display_limit
            tk.Label(
                self.mistakes_inner,
                text=f"...and {remaining} more word discrepancies recorded across the session.",
                font=theme.FONT_BODY_SMALL,
                fg=theme.TEXT_MUTED,
                bg=theme.BG_CARD
            ).pack(anchor="w", pady=(theme.SPACE_XS, 0))

    def _render_mode_analysis(self, mode: str, difficulty: str, accuracy: float, net_wpm: int) -> None:
        """Dynamic contextual insight tailored to the completed mode."""
        mode_data = {
            "Unified": (
                "Unified Natural Prose Flow",
                "Evaluates real-world typing agility across natural, coherent English sentences with authentic punctuation and grammar.",
                "Sustain an even cadence; prioritize clean character flow and let the vertical caret glide."
            ),
            "Words": (
                "Continuous Vocabulary Fluency",
                "Evaluates continuous rhythmic keystroke velocity across pure vocabulary patterns without special symbol interruptions.",
                "Sustain an even cadence; pure word mode rewards steady uninhibited muscle memory."
            ),
            "Punctuation": (
                "Punctuation & Cadence Dexterity",
                "Tests pause recovery and velocity stability through periods, commas, colons, hyphens, and quotation marks.",
                "Punctuation keystrokes often cause micro-pauses; anticipate commas and quotes to avoid rhythm breaks."
            ),
            "Capitalization": (
                "Shift-Key Coordination",
                "Measures fluid finger coordination between standard lowercase runs and shifted uppercase glyphs.",
                "Keep wrist relaxed when transitioning to Left and Right Shift keys to prevent finger cramping."
            ),
            "Numbers": (
                "Top-Row Numeric Precision",
                "Evaluates reaching confidence and muscle memory on the number row away from the home row rest position.",
                "Practice returning to home row index keys (F & J) immediately after numeric reach strikes."
            ),
            "Numbers & Symbols": (
                "Top-Row & Symbol Dexterity",
                "Tests complex shifted symbol keys (#, $, %, &, @) alongside numeric sequences.",
                "Anticipate shifted symbols one character in advance to coordinate simultaneous Shift presses."
            ),
            "Mixed": (
                "Comprehensive Prose Agility",
                "Multi-discipline real-world assessment balancing standard vocabulary, numbers, and diverse punctuation.",
                "Well-rounded performance across diverse glyphs translates directly into real productivity speed."
            ),
            "Code": (
                "Syntax, Operators & Casing Telemetry",
                "Evaluates brackets, camelCase/snake_case naming conventions, indentation, and programming syntax notation.",
                "Code typing demands near-100% precision because syntax errors break compilation in practical software."
            )
        }

        title, desc, tip = mode_data.get(mode, mode_data["Mixed"])
        self.lbl_mode_title.config(text=f"Mode Analysis: {title} ({difficulty})")
        self.lbl_mode_desc.config(text=desc)
        self.lbl_mode_tips.config(text=f"Optimization Strategy: {tip}")

    def _render_practice_advice(self, accuracy: float, net_wpm: int, consistency_pct: int, mode: str, errors: int) -> None:
        """Synthesize actionable practice recommendations from genuine performance data."""
        if accuracy < 92.0:
            advice = (
                f"Accuracy Priority: Your speed is solid, but {errors} mistakes heavily degraded your net throughput. "
                "Throttle your pace by 15% and prioritize clean keystrokes until accuracy consistently tops 96%."
            )
        elif accuracy >= 97.0 and net_wpm < 50:
            advice = (
                f"Velocity Push: Precision is exceptional at {int(accuracy)}%! Your muscle memory is reliable—"
                "begin pushing your raw speed actively on familiar word tokens to build higher velocity."
            )
        elif consistency_pct < 70:
            advice = (
                f"Rhythm Regulation: Cadence variation detected ({consistency_pct}% stability). "
                "Aim for a steady metronome-like tempo rather than fast sprint bursts followed by recovery pauses."
            )
        elif mode == "Code" and errors > 2:
            advice = (
                "Symbol Drill: Brackets and operators generated friction. Practice Numbers & Symbols challenges "
                "to reinforce spatial memory for non-alphabetic keys."
            )
        else:
            advice = (
                f"Mastery Maintenance: Well-balanced session ({net_wpm} WPM at {int(accuracy)}% accuracy with "
                f"{consistency_pct}% consistency). Repeat this routine regularly to push your personal best higher."
            )

        self.lbl_practice_advice.config(text=advice)

    # ========================================================================
    # ACTIONS
    # ========================================================================

    def _on_try_again(self) -> None:
        """Restart test retaining the same duration, difficulty, and mode."""
        typing_screen = self.app.screens.get("typing")
        if typing_screen and hasattr(typing_screen, "restart_with_same_config"):
            typing_screen.restart_with_same_config()
        self.app.show_screen("typing", preserve_config=True)

    def _on_new_test(self) -> None:
        """Advance to a fresh passage and start a new test."""
        typing_screen = self.app.screens.get("typing")
        if typing_screen and hasattr(typing_screen, "restart_with_new_passage"):
            typing_screen.restart_with_new_passage()
        self.app.show_screen("typing", preserve_config=True)

    def _on_view_history(self) -> None:
        """Navigate to Session History screen."""
        self.app.show_screen("history")

    def _on_return_home(self) -> None:
        """Navigate to main dashboard."""
        self.app.show_screen("home")
