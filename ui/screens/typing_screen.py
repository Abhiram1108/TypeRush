"""
TypeRush 2.0 — Typing Test Screen (Midnight Studio Edition)

A distraction-free, high-performance desktop typing benchmark interface providing:
- Region A (Session Header): Minimal TypeRush branding, mode/difficulty/duration metadata, and exit action.
- Region B (Performance Metrics): Clean horizontal editorial metrics (TIME LEFT, WPM, ACCURACY, ERRORS).
- Region C (Main Typing Area): Centered monospace reading passage (Cascadia Code / Consolas), pixel-accurate 2px vertical caret.
- Region D (Typing Progress): Restrained time progress indicator and continuous buffer stream status.
- Region E (Session Controls): Keycap hints ([Tab] Restart, [Esc] Exit) and restart action.
- Focus Layout: Full-width dedicated workspace, sidebar and header bar hidden during active session.
- Dual Feedback: Distraction-free Focus Mode (default) vs Live Feedback Mode (cascade-immune word-level error alignment).
- Exit Confirmation: Discards active tests with modal warning; never saves incomplete sessions.
- Automatic Results Handoff: Smooth direct transition to Results screen upon timer expiration.
"""

import time
import tkinter as tk
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Any

from ui import theme, scoring, storage

if TYPE_CHECKING:
    from ui.app import TypeRushApp
from ui.alignment import TypingAlignmentEngine
from ui.content_generator import ContentGenerator
from ui.components import (
    Badge,
    KeycapHint,
    PrimaryButton,
    SecondaryButton,
    ProgressBar,
)
from ui.screens.base_screen import BaseScreen


class TypingScreen(BaseScreen):
    """
    High-fidelity continuous typing test screen for TypeRush 2.0 (Midnight Studio).
    """
    SCREEN_NAME = "typing"

    def __init__(self, parent: tk.Widget, app: "TypeRushApp", **kwargs):
        super().__init__(parent, app, **kwargs)

        # Active configuration state
        settings = storage.load_settings()
        self.selected_duration: int = int(settings.get("default_duration", 60))
        self.selected_difficulty: str = str(settings.get("default_difficulty", "Medium"))
        self.selected_mode: str = str(settings.get("default_mode", "Mixed"))
        self.feedback_mode: str = str(settings.get("typing_feedback_mode", "live"))  # "live" or "focus"
        self.caret_style: str = str(settings.get("caret_style", "Highlight"))

        # Content generator & alignment engine
        self.content_gen = ContentGenerator(mode=self.selected_mode, difficulty=self.selected_difficulty)
        self.alignment_engine = TypingAlignmentEngine()

        # Session state machine: "ready", "typing", "paused", "completed"
        self.state: str = "ready"
        self.start_time: Optional[float] = None
        self.elapsed_seconds: float = 0.0
        self.pause_start_time: Optional[float] = None
        self.total_paused_seconds: float = 0.0
        self.timer_after_id: Optional[str] = None
        self.wpm_samples: List[Tuple[float, int]] = []
        self.last_sample_sec: int = 0
        self.last_result: Optional[Dict[str, Any]] = None
        self.has_saved_current_session: bool = False
        self.exit_dialog: Optional[tk.Toplevel] = None
        self.auto_nav_after_id: Optional[str] = None
        self.caret_update_id: Optional[str] = None
        self.focus_after_id: Optional[str] = None

        # Caret coordinate tracker & blinking state
        self.caret_x: float = 0
        self.caret_y: float = 0
        self.caret_h: float = 26
        self.caret_blink_id: Optional[str] = None
        self.caret_visible: bool = True

        # Build UI layout
        self._build_ui()

        # Initialize text buffer
        self._reset_buffer_and_state()

    # ========================================================================
    # UI CONSTRUCTION (5 REGIONS OF THE TYPING WORKSPACE)
    # ========================================================================

    def _build_ui(self) -> None:
        """Construct the visual workspace for the typing test."""
        # Attach responsive atmospheric background with deep reading contrast
        self.setup_background("typing")

        self.container = tk.Frame(self.bg_canvas, bg=theme.BG_PRIMARY)
        self.container.pack(fill="both", expand=True, padx=theme.SPACE_XL, pady=theme.SPACE_MD)

        # 1. REGION A: SESSION HEADER (Top bar with branding, metadata & exit)
        self._build_session_header()

        # 2. REGION B: PERFORMANCE METRICS (Editorial horizontal metrics row)
        self._build_metrics_bar()

        # 3. REGION C: MAIN TYPING AREA (Centered monospace reading passage & caret)
        self._build_passage_area()

        # 4. REGION D: TYPING PROGRESS (Subtle countdown progress track & stream status)
        self._build_progress_section()

        # Completion Banner (Packed when test completes)
        self._build_completion_banner()

        # 5. REGION E: SESSION CONTROLS & SHORTCUT HINTS (Restart & exit hints)
        self._build_controls_section()

    def _build_completion_banner(self) -> None:
        """Completion card displayed when benchmark finishes."""
        self.completion_banner = tk.Frame(
            self.container,
            bg=theme.BG_CARD,
            padx=theme.SPACE_LG,
            pady=theme.SPACE_MD,
            highlightbackground=theme.BORDER_COLOR,
            highlightthickness=1
        )
        # Not packed initially

        inner = tk.Frame(self.completion_banner, bg=theme.BG_CARD)
        inner.pack(fill="x")

        left_box = tk.Frame(inner, bg=theme.BG_CARD)
        left_box.pack(side="left")

        title = tk.Label(
            left_box,
            text="Challenge Finished!",
            font=theme.FONT_TITLE_SMALL,
            fg=theme.COLOR_SUCCESS,
            bg=theme.BG_CARD
        )
        title.pack(anchor="w")

        self.completion_stats_lbl = tk.Label(
            left_box,
            text="Final Score: -- WPM  •  100% Accuracy",
            font=theme.FONT_BODY,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD
        )
        self.completion_stats_lbl.pack(anchor="w", pady=(2, 0))

        right_box = tk.Frame(inner, bg=theme.BG_CARD)
        right_box.pack(side="right")

        self.btn_view_results = PrimaryButton(
            right_box,
            text="View Results",
            icon="📊",
            command=self._on_view_results,
            width=140,
            height=36,
            parent_bg=theme.BG_CARD
        )
        self.btn_view_results.pack(side="right", padx=(theme.SPACE_SM, 0))

        self.btn_try_again = SecondaryButton(
            right_box,
            text="Try Again",
            icon="↻",
            command=self.reset_test,
            width=110,
            height=36,
            parent_bg=theme.BG_CARD
        )
        self.btn_try_again.pack(side="right")

    # ========================================================================
    # REGION A: SESSION HEADER
    # ========================================================================

    def _build_session_header(self) -> None:
        """
        Top session header displaying subtle branding, active challenge metadata,
        and an accessible exit/cancel action.
        """
        self.session_header = tk.Frame(self.container, bg=theme.BG_PRIMARY)
        self.session_header.pack(fill="x", pady=(0, theme.SPACE_MD))

        # Left Column: Brand Logo
        left_box = tk.Frame(self.session_header, bg=theme.BG_PRIMARY)
        left_box.pack(side="left")

        brand_icon = tk.Label(
            left_box,
            text="⚡",
            font=(theme.FONT_FAMILY, 14),
            fg=theme.ACCENT_PRIMARY,
            bg=theme.BG_PRIMARY
        )
        brand_icon.pack(side="left", padx=(0, theme.SPACE_XS))

        brand_lbl = tk.Label(
            left_box,
            text="TypeRush",
            font=theme.FONT_BRAND,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_PRIMARY
        )
        brand_lbl.pack(side="left")

        # Center Column: Session Metadata Capsule
        center_box = tk.Frame(self.session_header, bg=theme.BG_PRIMARY)
        center_box.pack(side="left", expand=True)

        self.meta_label = tk.Label(
            center_box,
            text=self._get_header_meta_text(),
            font=theme.FONT_STAT_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        )
        self.meta_label.pack(anchor="center")

        # Right Column: Exit / Cancel Button
        right_box = tk.Frame(self.session_header, bg=theme.BG_PRIMARY)
        right_box.pack(side="right")

        self.btn_exit = SecondaryButton(
            right_box,
            text="Exit [Esc]",
            icon="✕",
            command=self._confirm_exit,
            width=100,
            height=32,
            parent_bg=theme.BG_PRIMARY
        )
        self.btn_exit.pack(side="right")

    def _get_header_meta_text(self) -> str:
        """Format active challenge metadata."""
        return f"{self.selected_difficulty.upper()} CHALLENGE  ·  {self.selected_duration} SECONDS"

    def _update_header_meta(self) -> None:
        """Update header metadata text."""
        if hasattr(self, "meta_label"):
            self.meta_label.config(text=self._get_header_meta_text())

    # ========================================================================
    # REGION B: PERFORMANCE METRICS
    # ========================================================================

    def _build_metrics_bar(self) -> None:
        """
        Horizontal editorial metrics row presenting:
        1. TIME LEFT (visually prominent countdown)
        2. WPM
        3. ACCURACY
        4. ERRORS
        """
        self.metric_separators = []
        self.metrics_container = tk.Frame(self.container, bg=theme.BG_PRIMARY)
        self.metrics_container.pack(fill="x", pady=(0, theme.SPACE_LG))

        inner_metrics = tk.Frame(self.metrics_container, bg=theme.BG_PRIMARY)
        inner_metrics.pack(anchor="center")
        self.inner_metrics = inner_metrics

        # Metric 1: TIME LEFT (Prominent Countdown)
        col_time = tk.Frame(inner_metrics, bg=theme.BG_PRIMARY)
        col_time.pack(side="left", padx=theme.SPACE_LG)
        self.col_time = col_time

        tk.Label(
            col_time,
            text="TIME LEFT",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        ).pack(anchor="center")

        self.val_time = tk.Label(
            col_time,
            text=f"{self.selected_duration}s",
            font=(theme.FONT_FAMILY_MONO, 26, "bold"),
            fg=theme.ACCENT_PRIMARY,
            bg=theme.BG_PRIMARY
        )
        self.val_time.pack(anchor="center", pady=(2, 0))

        # Separator 1
        self._add_metric_separator(inner_metrics)

        # Metric 2: WPM
        col_wpm = tk.Frame(inner_metrics, bg=theme.BG_PRIMARY)
        col_wpm.pack(side="left", padx=theme.SPACE_LG)
        self.col_wpm = col_wpm

        tk.Label(
            col_wpm,
            text="NET WPM",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        ).pack(anchor="center")

        self.val_wpm = tk.Label(
            col_wpm,
            text="--",
            font=(theme.FONT_FAMILY, 24, "bold"),
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_PRIMARY
        )
        self.val_wpm.pack(anchor="center", pady=(2, 0))

        # Separator 2
        self._add_metric_separator(inner_metrics)

        # Metric 3: ACCURACY
        col_acc = tk.Frame(inner_metrics, bg=theme.BG_PRIMARY)
        col_acc.pack(side="left", padx=theme.SPACE_LG)
        self.col_acc = col_acc

        tk.Label(
            col_acc,
            text="ACCURACY",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        ).pack(anchor="center")

        self.val_acc = tk.Label(
            col_acc,
            text="100%",
            font=(theme.FONT_FAMILY, 24, "bold"),
            fg=theme.COLOR_SUCCESS,
            bg=theme.BG_PRIMARY
        )
        self.val_acc.pack(anchor="center", pady=(2, 0))

        # Separator 3
        self._add_metric_separator(inner_metrics)

        # Metric 4: ERRORS
        col_err = tk.Frame(inner_metrics, bg=theme.BG_PRIMARY)
        col_err.pack(side="left", padx=theme.SPACE_LG)
        self.col_err = col_err

        tk.Label(
            col_err,
            text="ERRORS",
            font=theme.FONT_METRIC_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        ).pack(anchor="center")

        self.val_errors = tk.Label(
            col_err,
            text="0",
            font=(theme.FONT_FAMILY, 24, "bold"),
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        )
        self.val_errors.pack(anchor="center", pady=(2, 0))

    def _add_metric_separator(self, parent: tk.Widget) -> None:
        """Subtle vertical separator line between metric columns."""
        sep = tk.Frame(parent, bg=theme.BORDER_SUBTLE, width=1, height=36)
        sep.pack(side="left", padx=theme.SPACE_SM)
        if not hasattr(self, "metric_separators"):
            self.metric_separators = []
        self.metric_separators.append(sep)

    # ========================================================================
    # REGION C: MAIN TYPING AREA
    # ========================================================================

    def _build_passage_area(self) -> None:
        """
        Centrally positioned continuous typing area with optimal line length,
        monospace Cascadia Code rendering, and native high-precision vertical caret.
        """
        # Outer wrapper expanding to fill space
        self.passage_wrapper = tk.Frame(self.container, bg=theme.BG_PRIMARY)
        self.passage_wrapper.pack(fill="both", expand=True, pady=(theme.SPACE_MD, theme.SPACE_MD))

        # Center-constrained inner column for comfortable reading width (~900-1050px)
        self.passage_center_box = tk.Frame(self.passage_wrapper, bg=theme.BG_PRIMARY)
        self.passage_center_box.pack(anchor="center", fill="both", expand=True)

        # Status instruction prompt
        self.prompt_label = tk.Label(
            self.passage_center_box,
            text="Start typing to begin",
            font=theme.FONT_BODY,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        )
        self.prompt_label.pack(anchor="w", pady=(0, theme.SPACE_XS))

        # Text Frame
        self.text_frame = tk.Frame(self.passage_center_box, bg=theme.BG_PRIMARY)
        self.text_frame.pack(fill="both", expand=True)

        # Monospace Text Display Widget
        # Font: Cascadia Code / Consolas 18pt, generous line height and paragraph spacing
        self.text_display = tk.Text(
            self.text_frame,
            font=(theme.FONT_FAMILY_MONO, 18),
            bg=theme.BG_PRIMARY,
            fg=theme.PASSAGE_UNTYPED,
            bd=0,
            highlightthickness=0,
            wrap="word",
            spacing2=12,
            spacing3=8,
            cursor="xterm",
            insertontime=500,
            insertofftime=500,
            insertwidth=2,
            insertbackground=theme.ACCENT_PRIMARY,
            exportselection=False,
            selectbackground=theme.BG_PRIMARY,
            selectforeground=theme.TEXT_PRIMARY,
            takefocus=True
        )
        self.text_display.pack(fill="both", expand=True)

        # Character tags for styling
        self.text_display.tag_configure("untyped", foreground=theme.PASSAGE_UNTYPED, background=theme.BG_PRIMARY)
        self.text_display.tag_configure("correct", foreground=theme.PASSAGE_CORRECT, background=theme.BG_PRIMARY)
        self.text_display.tag_configure("incorrect", foreground=theme.PASSAGE_INCORRECT, background=theme.PASSAGE_INCORRECT_BG)
        self.text_display.tag_configure("current_word", foreground=theme.PASSAGE_CURRENT_WORD, background=theme.PASSAGE_CURRENT_BG)
        self.text_display.tag_configure("current_char_correct", foreground=theme.PASSAGE_CORRECT, background=theme.PASSAGE_CURRENT_BG)
        self.text_display.tag_configure("current_char_incorrect", foreground=theme.PASSAGE_INCORRECT, background=theme.PASSAGE_INCORRECT_BG)

        self.text_display.tag_raise("correct")
        self.text_display.tag_raise("incorrect")
        self.text_display.tag_raise("current_word")
        self.text_display.tag_raise("current_char_correct")
        self.text_display.tag_raise("current_char_incorrect")

        # Benign placeholder for self.caret if any legacy code checks hasattr(self, 'caret')
        self.caret = tk.Frame(self.text_frame, width=0, height=0)

        # Direct keyboard and interaction bindings
        self.text_display.bind("<Key>", self._on_key_press)
        self.text_display.bind("<Button-1>", self._on_text_click)
        self.text_display.bind("<B1-Motion>", lambda e: "break")
        self.text_display.bind("<Double-Button-1>", lambda e: "break")
        self.text_display.bind("<Triple-Button-1>", lambda e: "break")
        self.text_display.bind("<<Paste>>", lambda e: "break")
        self.text_display.bind("<<Cut>>", lambda e: "break")
        self.text_display.bind("<<Clear>>", lambda e: "break")
        self.passage_wrapper.bind("<Button-1>", lambda e: self.focus_input())

    def _on_text_click(self, event: tk.Event) -> str:
        """Clicking text focuses input and restores exact caret placement."""
        self.focus_input()
        return "break"

    # ========================================================================
    # REGION D: TYPING PROGRESS
    # ========================================================================

    def _build_progress_section(self) -> None:
        """
        Restrained countdown time progress indicator and stream position status.
        """
        self.progress_frame = tk.Frame(self.container, bg=theme.BG_PRIMARY)
        self.progress_frame.pack(fill="x", pady=(0, theme.SPACE_SM))

        # Progress bar track
        self.progress_bar = ProgressBar(
            self.progress_frame,
            height=3,
            track_color=theme.BG_SURFACE,
            fill_color=theme.ACCENT_PRIMARY,
            parent_bg=theme.BG_PRIMARY
        )
        self.progress_bar.pack(fill="x", pady=(0, theme.SPACE_XS))

        # Status text row
        status_row = tk.Frame(self.progress_frame, bg=theme.BG_PRIMARY)
        status_row.pack(fill="x")

        self.lbl_progress_stream = tk.Label(
            status_row,
            text=f"Continuous Stream Active  •  {self.selected_mode}",
            font=theme.CAPTION,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        )
        self.lbl_progress_stream.pack(side="left")

        self.lbl_progress_time = tk.Label(
            status_row,
            text=f"{self.selected_duration}s remaining",
            font=theme.CAPTION,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_PRIMARY
        )
        self.lbl_progress_time.pack(side="right")

    # ========================================================================
    # REGION E: SESSION CONTROLS & SHORTCUT HINTS
    # ========================================================================

    def _build_controls_section(self) -> None:
        """Bottom keycap hints and restart action."""
        self.controls_frame = tk.Frame(self.container, bg=theme.BG_PRIMARY)
        self.controls_frame.pack(fill="x", side="bottom")

        # Left Column: Keycap shortcuts
        shortcuts_box = tk.Frame(self.controls_frame, bg=theme.BG_PRIMARY)
        shortcuts_box.pack(side="left")

        hint_restart = KeycapHint(
            shortcuts_box,
            keys=["Tab"],
            description="Restart test",
            parent_bg=theme.BG_PRIMARY
        )
        hint_restart.pack(side="left", padx=(0, theme.SPACE_XL))

        hint_exit = KeycapHint(
            shortcuts_box,
            keys=["Esc"],
            description="Exit challenge",
            parent_bg=theme.BG_PRIMARY
        )
        hint_exit.pack(side="left")

        # Right Column: Restart Button
        self.btn_restart = SecondaryButton(
            self.controls_frame,
            text="Restart [Tab]",
            icon="↻",
            command=self.reset_test,
            width=120,
            height=32,
            parent_bg=theme.BG_PRIMARY
        )
        self.btn_restart.pack(side="right")

    # ========================================================================
    # CONTINUOUS BUFFER & TEXT ENGINE
    # ========================================================================

    @property
    def passage_text(self) -> str:
        """Compatibility property for target text buffer."""
        return self.alignment_engine.target_text

    @property
    def typed_index(self) -> int:
        """Compatibility property for total typed characters."""
        return self.alignment_engine.evaluate()["total_chars"]

    def _reset_buffer_and_state(self) -> None:
        """Generate initial infinite text buffer and initialize alignment engine."""
        self.content_gen.set_config(self.selected_mode, self.selected_difficulty)
        initial_text = self.content_gen.generate_initial_buffer(min_words=120)
        self.alignment_engine.set_target_text(initial_text)

        # Render into Text widget
        self.text_display.delete("1.0", "end")
        self.text_display.insert("1.0", initial_text, "untyped")

        # Apply current word tag to first word
        if self.alignment_engine.expected_words:
            w_start, w_end = self.alignment_engine.get_word_span(0)
            self.text_display.tag_remove("untyped", f"1.0 + {w_start} chars", f"1.0 + {w_end} chars")
            self.text_display.tag_add("current_word", f"1.0 + {w_start} chars", f"1.0 + {w_end} chars")

        # Position native cursor at start
        self._update_caret_position()

    def _check_and_extend_buffer(self) -> None:
        """
        Continuously monitor remaining untyped words. If buffer drops below
        safe threshold, generate and append more text seamlessly.
        """
        remaining_words = self.alignment_engine.get_remaining_untyped_words()
        if remaining_words < 40:
            continuation = self.content_gen.generate_continuation(min_words=40)
            self.alignment_engine.append_target_text(continuation)

            # Append to text display
            sep = ("\n\n" if self.selected_mode == "Code" else " ")
            self.text_display.insert("end", sep + continuation.strip(), "untyped")

    # ========================================================================
    # NATIVE TEXT CURSOR POSITIONING
    # ========================================================================

    def _update_caret_position(self) -> None:
        """
        Position the native insertion cursor cleanly between characters.
        Never overlaps glyphs, scrolls viewport comfortably.
        """
        caret_idx = self.alignment_engine.get_current_caret_index()
        mark_str = f"1.0 + {caret_idx} chars"
        self.text_display.mark_set("insert", mark_str)
        self.text_display.see(mark_str)

    def _reset_caret_blink(self) -> None:
        """Compatibility no-op (native Tkinter cursor handles blinking)."""
        pass

    def _blink_caret(self) -> None:
        """Compatibility no-op (native Tkinter cursor handles blinking)."""
        pass

    # ========================================================================
    # INTERACTION & KEYBOARD CAPTURE
    # ========================================================================

    def focus_input(self) -> None:
        """Focus the typing text area directly."""
        if hasattr(self, "text_display") and self.text_display.winfo_exists():
            self.text_display.focus_set()
            self._update_caret_position()

    def _on_key_press(self, event: tk.Event) -> str:
        """Direct keyboard input interceptor without any visible input box."""
        # Global Shortcut: ESC -> Exit / Confirmation
        if event.keysym == "Escape":
            self._confirm_exit()
            return "break"

        # Global Shortcut: Tab -> Restart Test
        if event.keysym == "Tab":
            self.reset_test()
            return "break"

        # Ignore modifier keys and function keys
        if event.keysym in (
            "Shift_L", "Shift_R", "Control_L", "Control_R",
            "Alt_L", "Alt_R", "Caps_Lock", "Super_L", "Super_R",
            "Up", "Down", "Left", "Right", "Home", "End", "Prior", "Next",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"
        ):
            return "break"

        # Prevent input if test already completed or paused
        if self.state in ("completed", "paused"):
            return "break"

        # Handle Backspace
        if event.keysym == "BackSpace":
            self._handle_backspace()
            return "break"

        # Handle Printable Characters & Spaces
        char = event.char
        if not char:
            return "break"

        # Enter in code mode acts as newline, elsewhere acts as space
        if event.keysym == "Return":
            if self.selected_mode == "Code":
                char = "\n"
            else:
                char = " "

        self._handle_character(char)
        return "break"

    def _handle_character(self, char: str) -> None:
        """Process typed character through alignment engine."""
        # Transition from State 1: Ready -> State 2: Typing on first keystroke
        if self.state == "ready":
            self.state = "typing"
            self.start_time = time.time()
            self.total_paused_seconds = 0.0
            self.prompt_label.config(text="")  # Quiet: disappears on first keystroke
            self._tick_timer()

        # Forward character to alignment engine
        self.alignment_engine.handle_character(char)

        # Trigger mechanical keypress sound
        if hasattr(self.app, "audio_manager"):
            self.app.audio_manager.play_keypress()

        # Check for buffer expansion
        self._check_and_extend_buffer()

        # Update styling (Focus Mode vs Live Feedback Mode)
        self._update_text_display_tags()

        # Check for error sound trigger
        eval_res = self.alignment_engine.evaluate()
        curr_err = eval_res.get("total_errors", 0)
        prev_err = getattr(self, "_prev_err_count", 0)
        if curr_err > prev_err:
            if hasattr(self.app, "audio_manager"):
                self.app.audio_manager.play_error()
            if getattr(self, "master_mode", False):
                self._trigger_master_mode_fail()
                return
        self._prev_err_count = curr_err

        # Position caret
        self._update_caret_position()

        # Update live metrics
        self._update_live_metrics()

    def _handle_backspace(self) -> None:
        """Process Backspace key with intra-word support."""
        if self.state != "typing":
            return

        self.alignment_engine.handle_backspace()
        self._update_text_display_tags()
        self._update_caret_position()
        self._update_live_metrics()

    def _trigger_master_mode_fail(self) -> None:
        """Sudden death: notify user and instantly reset test upon mistake."""
        self.state = "ready"
        if self.timer_after_id:
            try:
                self.after_cancel(self.timer_after_id)
            except Exception:
                pass
            self.timer_after_id = None
        if hasattr(self, "prompt_label"):
            self.prompt_label.config(text="⚠ MASTER MODE: MISTAKE DETECTED! RESETTING...", fg=theme.STATUS_ERROR)
        self.after(500, self.reset_test)

    # ========================================================================
    # DISPLAY STYLING: FOCUS MODE VS LIVE FEEDBACK MODE
    # ========================================================================

    def _update_text_display_tags(self) -> None:
        """
        Apply text tags based on user preference:
        - Focus Mode: Distraction-free reading flow without live color feedback.
        - Live Feedback Mode:
          * Committed correct words: green
          * Committed incorrect words: red
          * Active current word: subtle container highlight (#171C28)
          * Within active word: correct chars green, mistake chars red
          * Untyped words: muted grey (#858D9E)
        """
        if self.feedback_mode == "focus":
            self.text_display.tag_remove("correct", "1.0", "end")
            self.text_display.tag_remove("incorrect", "1.0", "end")
            self.text_display.tag_remove("current_char_correct", "1.0", "end")
            self.text_display.tag_remove("current_char_incorrect", "1.0", "end")
            self.text_display.tag_remove("current_word", "1.0", "end")
            self.text_display.tag_add("untyped", "1.0", "end")
            return

        curr_idx = self.alignment_engine.current_word_idx
        num_words = len(self.alignment_engine.expected_words)

        # 1. Update committed words up to curr_idx
        for w_i in range(min(curr_idx, num_words)):
            start, end = self.alignment_engine.get_word_span(w_i)
            w_start = f"1.0 + {start} chars"
            w_end = f"1.0 + {end} chars"

            self.text_display.tag_remove("untyped", w_start, w_end)
            self.text_display.tag_remove("current_word", w_start, w_end)
            self.text_display.tag_remove("current_char_correct", w_start, w_end)
            self.text_display.tag_remove("current_char_incorrect", w_start, w_end)

            if self.alignment_engine.is_word_correct(w_i):
                self.text_display.tag_remove("incorrect", w_start, w_end)
                self.text_display.tag_add("correct", w_start, w_end)
            else:
                self.text_display.tag_remove("correct", w_start, w_end)
                self.text_display.tag_add("incorrect", w_start, w_end)

        # 2. Update current active word
        if curr_idx < num_words:
            start, end = self.alignment_engine.get_word_span(curr_idx)
            w_start = f"1.0 + {start} chars"
            w_end = f"1.0 + {end} chars"

            self.text_display.tag_remove("untyped", w_start, w_end)
            self.text_display.tag_remove("correct", w_start, w_end)
            self.text_display.tag_remove("incorrect", w_start, w_end)
            self.text_display.tag_remove("current_char_correct", w_start, w_end)
            self.text_display.tag_remove("current_char_incorrect", w_start, w_end)
            self.text_display.tag_add("current_word", w_start, w_end)

            typed = self.alignment_engine.typed_words[curr_idx]
            expected = self.alignment_engine.expected_words[curr_idx]

            for c_i in range(min(len(typed), len(expected))):
                c_start = f"1.0 + {start + c_i} chars"
                c_end = f"1.0 + {start + c_i + 1} chars"
                if typed[c_i].lower() == expected[c_i].lower():
                    self.text_display.tag_add("current_char_correct", c_start, c_end)
                else:
                    self.text_display.tag_add("current_char_incorrect", c_start, c_end)

    # ========================================================================
    # TIMER & METRICS
    # ========================================================================

    def _tick_timer(self) -> None:
        """Countdown timer ticking every 100ms. Test ends ONLY when time expires."""
        if self.state != "typing" or self.start_time is None:
            return

        now = time.time()
        self.elapsed_seconds = (now - self.start_time) - self.total_paused_seconds
        remaining = max(0, self.selected_duration - int(self.elapsed_seconds))
        self.val_time.config(text=f"{remaining}s")

        # 1-second interval WPM progression sampling
        current_sec = int(self.elapsed_seconds)
        if current_sec > self.last_sample_sec and self.elapsed_seconds >= 1.0:
            eval_res = self.alignment_engine.evaluate()
            cur_metrics = scoring.calculate_typing_metrics(
                correct_chars=eval_res["correct_chars"],
                incorrect_chars=eval_res["incorrect_chars"],
                total_typed=eval_res["total_chars"],
                elapsed_seconds=self.elapsed_seconds
            )
            self.wpm_samples.append((float(current_sec), cur_metrics["net_wpm"]))
            self.last_sample_sec = current_sec

        self._update_live_metrics()

        # Update progress bar based on time elapsed
        pct = min(100.0, (self.elapsed_seconds / self.selected_duration) * 100.0)
        self.progress_bar.set_progress(pct)
        word_count = self.alignment_engine.current_word_idx + 1
        self.lbl_progress_stream.config(text=f"Word {word_count}  •  Continuous Stream")
        self.lbl_progress_time.config(text=f"{remaining}s remaining")

        if remaining <= 0:
            self._complete_test(reason="Time Expired")
            return

        self.timer_after_id = self.after(100, self._tick_timer)

    def _update_live_metrics(self) -> None:
        """Update live Net WPM, Accuracy, and Error count displays."""
        eval_res = self.alignment_engine.evaluate()
        total_typed = eval_res["total_chars"]
        errors = eval_res["incorrect_chars"]

        # Errors display
        self.val_errors.config(
            text=str(errors),
            fg=theme.COLOR_ERROR if errors > 0 else theme.TEXT_MUTED
        )

        if total_typed == 0:
            self.val_wpm.config(text="--")
            self.val_acc.config(text="100%")
            return

        metrics = scoring.calculate_typing_metrics(
            correct_chars=eval_res["correct_chars"],
            incorrect_chars=eval_res["incorrect_chars"],
            total_typed=total_typed,
            elapsed_seconds=self.elapsed_seconds
        )

        self.val_acc.config(text=f"{int(metrics['accuracy'])}%")
        if self.elapsed_seconds >= 1.0:
            self.val_wpm.config(text=str(metrics["net_wpm"]))
        else:
            self.val_wpm.config(text="--")

    def _pause_timer(self) -> None:
        """Pause the countdown timer while modal dialogs are presented."""
        if self.state == "typing":
            self.state = "paused"
            self.pause_start_time = time.time()
            if self.timer_after_id:
                self.after_cancel(self.timer_after_id)
                self.timer_after_id = None

    def _resume_timer(self) -> None:
        """Resume countdown timer after modal dialog is dismissed."""
        if self.state == "paused":
            if self.pause_start_time:
                self.total_paused_seconds += (time.time() - self.pause_start_time)
                self.pause_start_time = None
            self.state = "typing"
            self._tick_timer()

    def _complete_test(self, reason: str = "Time Expired") -> None:
        """
        Complete continuous test session, commit results to local storage,
        and automatically navigate to ResultsScreen.
        """
        if self.state == "completed":
            return

        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None

        self.state = "completed"
        self.prompt_label.config(text="Challenge finished! Loading performance report...", fg=theme.COLOR_SUCCESS)

        # Trigger satisfying completion sound
        if hasattr(self.app, "audio_manager"):
            self.app.audio_manager.play_completion()

        if self.start_time:
            self.elapsed_seconds = max(0.5, (time.time() - self.start_time) - self.total_paused_seconds)
        else:
            self.elapsed_seconds = max(0.5, self.elapsed_seconds)

        eval_res = self.alignment_engine.evaluate()

        # Extract word-level error classifications (substitutions, insertions, omissions)
        total_substitutions = 0
        total_insertions = 0
        total_omissions = 0
        mistakes_list = []

        from ui.alignment import levenshtein_align

        for w_eval in eval_res.get("word_evaluations", []):
            if not w_eval.is_correct and (w_eval.is_completed or w_eval.typed != ""):
                align_ops = levenshtein_align(w_eval.expected, w_eval.typed)
                word_subs = sum(1 for _, _, op in align_ops if op == "sub")
                word_ins = sum(1 for _, _, op in align_ops if op == "insert")
                word_dels = sum(1 for _, _, op in align_ops if op == "delete")

                total_substitutions += word_subs
                total_insertions += word_ins
                total_omissions += word_dels

                if word_subs > 0 and word_ins == 0 and word_dels == 0:
                    category = "Substitution"
                elif word_ins > 0 and word_subs == 0 and word_dels == 0:
                    category = "Extra Character"
                elif word_dels > 0 and word_subs == 0 and word_ins == 0:
                    category = "Missing Character"
                else:
                    category = "Multiple Errors"

                mistakes_list.append({
                    "word_index": w_eval.word_index,
                    "expected": w_eval.expected,
                    "typed": w_eval.typed,
                    "category": category,
                    "substitutions": word_subs,
                    "insertions": word_ins,
                    "omissions": word_dels,
                })

        # Ensure final sample is present
        final_time = round(self.elapsed_seconds, 1)
        if not self.wpm_samples or self.wpm_samples[-1][0] != final_time:
            # Estimate current instantaneous net wpm
            temp_metrics = scoring.calculate_typing_metrics(
                correct_chars=eval_res["correct_chars"],
                incorrect_chars=eval_res["incorrect_chars"],
                total_typed=eval_res["total_chars"],
                elapsed_seconds=self.elapsed_seconds
            )
            self.wpm_samples.append((final_time, temp_metrics["net_wpm"]))

        # Build comprehensive session result dictionary
        self.last_result = scoring.create_session_result(
            correct_chars=eval_res["correct_chars"],
            incorrect_chars=eval_res["incorrect_chars"],
            total_typed=eval_res["total_chars"],
            elapsed_seconds=self.elapsed_seconds,
            selected_duration=self.selected_duration,
            difficulty=self.selected_difficulty,
            wpm_samples=self.wpm_samples,
            completed_reason=reason,
            mode=self.selected_mode,
            correct_words=eval_res["correct_words"],
            incorrect_words=eval_res["incorrect_words"],
            substitutions=total_substitutions,
            insertions=total_insertions,
            omissions=total_omissions,
            mistakes=mistakes_list,
            weak_keys=eval_res.get("weak_keys", {})
        )

        # Persist session to local storage ONCE
        if not self.has_saved_current_session:
            self.last_result = storage.save_session(self.last_result)
            self.has_saved_current_session = True
            self.app.last_session_result = self.last_result

        # Update displays
        self.val_wpm.config(text=str(self.last_result["net_wpm"]))
        self.val_acc.config(text=f"{int(self.last_result['accuracy'])}%")

        # Reveal completion banner
        if hasattr(self, "completion_banner"):
            self.completion_banner.pack(fill="x", pady=(theme.SPACE_SM, 0))
            self.completion_stats_lbl.config(
                text=f"Final Speed: {self.last_result['net_wpm']} WPM   •   Accuracy: {int(self.last_result['accuracy'])}% ({self.last_result['rating']})"
            )

        # Automatic navigation to Results screen
        self.auto_nav_after_id = self.after(300, self._on_view_results)

    # ========================================================================
    # EXIT CONFIRMATION & CONTROLS
    # ========================================================================

    def request_exit(self, action: str = "home") -> None:
        """
        Shared exit controller for all entry points:
        - Typing screen Exit button
        - Escape key
        - Windows title-bar close button
        Default: confirm_exit is OFF -> immediate cancel and navigate/quit without interruption.
        """
        # Confirmation enabled: prevent duplicate dialogs
        if self.exit_dialog and self.exit_dialog.winfo_exists():
            return

        # If test is not actively typing or paused, leave immediately
        if self.state not in ("typing", "paused"):
            self.cancel_test()
            if action == "quit":
                self.app.destroy()
            else:
                self.app.show_screen("home")
            return

        # Check confirmation preference (defaults to False)
        settings = storage.load_settings()
        if not settings.get("confirm_exit", False):
            self.cancel_test()
            if action == "quit":
                self.app.destroy()
            else:
                self.app.show_screen("home")
            return

        # Pause countdown while confirmation panel is open
        self._pause_timer()

        # Build compact confirmation panel (approx 420x175 px)
        dialog = tk.Toplevel(self.app)
        dialog_title = "Leave this test?" if action == "home" else "Quit TypeRush?"
        dialog.title(dialog_title)
        dialog.configure(bg=theme.BG_CARD)
        dialog.resizable(False, False)
        dialog.transient(self.app)
        try:
            dialog.grab_set()
        except Exception:
            pass

        # Preferred placement: Top-right area so it does not obscure the main typing passage
        w, h = 420, 175
        root_x = self.app.winfo_rootx()
        root_y = self.app.winfo_rooty()
        root_w = self.app.winfo_width()
        x = max(0, root_x + root_w - w - 40)
        y = max(0, root_y + 80)
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        content = tk.Frame(dialog, bg=theme.BG_CARD, padx=theme.SPACE_LG, pady=theme.SPACE_MD)
        content.pack(fill="both", expand=True)

        tk.Label(
            content,
            text=dialog_title,
            font=theme.FONT_TITLE_SMALL,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_CARD
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Your current attempt will be discarded and will not be saved.",
            font=theme.FONT_BODY_SMALL,
            fg=theme.TEXT_SECONDARY,
            bg=theme.BG_CARD,
            wraplength=380,
            justify="left"
        ).pack(anchor="w", pady=(theme.SPACE_SM, theme.SPACE_MD))

        btn_bar = tk.Frame(content, bg=theme.BG_CARD)
        btn_bar.pack(fill="x", side="bottom")

        def on_continue():
            self.exit_dialog = None
            try:
                dialog.destroy()
            except Exception:
                pass
            self._resume_timer()
            self.focus_input()

        def on_confirm_exit():
            self.exit_dialog = None
            try:
                dialog.destroy()
            except Exception:
                pass
            self.cancel_test()
            if action == "quit":
                self.app.destroy()
            else:
                self.app.show_screen("home")

        self.exit_dialog = dialog
        self.exit_dialog_discard = on_confirm_exit

        # Handle window close and Esc on the dialog itself to resume
        dialog.protocol("WM_DELETE_WINDOW", on_continue)
        dialog.bind("<Escape>", lambda e: on_continue())

        btn_exit_text = "Exit test" if action == "home" else "Quit TypeRush"
        btn_exit = PrimaryButton(
            btn_bar,
            text=btn_exit_text,
            command=on_confirm_exit,
            width=120,
            height=34,
            parent_bg=theme.BG_CARD
        )
        btn_exit.pack(side="right")

        btn_continue = SecondaryButton(
            btn_bar,
            text="Continue typing",
            command=on_continue,
            width=130,
            height=34,
            parent_bg=theme.BG_CARD
        )
        btn_continue.pack(side="right", padx=(0, theme.SPACE_SM))

    def _confirm_exit(self) -> None:
        """Entry point for in-screen Exit button or Escape key."""
        self.request_exit(action="home")

    def cancel_test(self) -> None:
        """
        Immediately cancel the active typing test.
        Cancel all timers, animations, carets, and callbacks.
        Ensure no session record is saved.
        """
        if self.timer_after_id:
            try:
                self.after_cancel(self.timer_after_id)
            except Exception:
                pass
            self.timer_after_id = None

        if self.caret_blink_id:
            try:
                self.after_cancel(self.caret_blink_id)
            except Exception:
                pass
            self.caret_blink_id = None
        if hasattr(self, "caret_update_id") and self.caret_update_id:
            try:
                self.after_cancel(self.caret_update_id)
            except Exception:
                pass
            self.caret_update_id = None
        if hasattr(self, "focus_after_id") and self.focus_after_id:
            try:
                self.after_cancel(self.focus_after_id)
            except Exception:
                pass
            self.focus_after_id = None

        if hasattr(self, "auto_nav_after_id") and self.auto_nav_after_id:
            try:
                self.after_cancel(self.auto_nav_after_id)
            except Exception:
                pass
            self.auto_nav_after_id = None

        if hasattr(self, "caret_update_id") and self.caret_update_id:
            try:
                self.after_cancel(self.caret_update_id)
            except Exception:
                pass
            self.caret_update_id = None

        if hasattr(self, "focus_after_id") and self.focus_after_id:
            try:
                self.after_cancel(self.focus_after_id)
            except Exception:
                pass
            self.focus_after_id = None

        if self.exit_dialog and self.exit_dialog.winfo_exists():
            try:
                self.exit_dialog.destroy()
            except Exception:
                pass
            self.exit_dialog = None

        self.state = "ready"
        self.start_time = None
        self.pause_start_time = None
        self.total_paused_seconds = 0.0
        self.has_saved_current_session = False
        self.last_result = None
        self.wpm_samples = []

    def reset_test(self) -> None:
        """Reset test session to State 1: Ready."""
        if hasattr(self, "auto_nav_after_id") and self.auto_nav_after_id:
            try:
                self.after_cancel(self.auto_nav_after_id)
            except Exception:
                pass
            self.auto_nav_after_id = None

        if self.timer_after_id:
            try:
                self.after_cancel(self.timer_after_id)
            except Exception:
                pass
            self.timer_after_id = None

        self.state = "ready"
        self.start_time = None
        self.elapsed_seconds = 0.0
        self.pause_start_time = None
        self.total_paused_seconds = 0.0
        self.wpm_samples = []
        self.last_sample_sec = 0
        self.last_result = None
        self.has_saved_current_session = False

        if hasattr(self, "completion_banner"):
            self.completion_banner.pack_forget()

        # Reset metric values
        self.val_wpm.config(text="--")
        self.val_acc.config(text="100%")
        self.val_errors.config(text="0", fg=theme.TEXT_MUTED)
        self.val_time.config(text=f"{self.selected_duration}s")
        self.prompt_label.config(text="Start typing to begin", fg=theme.TEXT_MUTED)

        # Reset progress bar
        self.progress_bar.set_progress(0.0)
        self.lbl_progress_stream.config(text=f"Continuous Stream Active  •  {self.selected_mode}")
        self.lbl_progress_time.config(text=f"{self.selected_duration}s remaining")

        # Reload infinite buffer
        self._reset_buffer_and_state()

        # Re-focus keyboard input
        self.focus_input()

    def _on_mode_changed(self, value: str) -> None:
        """Update typing mode (Mixed, Words, Punctuation, Capitalization, Numbers, Code)."""
        self.selected_mode = value
        self._update_header_meta()
        self.reset_test()

    def _on_difficulty_changed(self, value: str) -> None:
        """Update difficulty tier (Easy, Medium, Hard, Expert)."""
        self.selected_difficulty = value
        self._update_header_meta()
        self.reset_test()

    def _on_duration_changed(self, value: str) -> None:
        """Update test duration (15s, 30s, 60s, 120s)."""
        num_str = value.replace("s", "")
        if num_str.isdigit():
            self.selected_duration = int(num_str)
            self._update_header_meta()
            self.reset_test()

    def _on_view_results(self) -> None:
        """Navigate to results screen and pass completed test data."""
        if hasattr(self, "auto_nav_after_id") and self.auto_nav_after_id:
            try:
                self.after_cancel(self.auto_nav_after_id)
            except Exception:
                pass
            self.auto_nav_after_id = None
        self.app.show_screen("results", session_result=self.last_result)

    def restart_with_same_config(self) -> None:
        """Restart test retaining current configuration."""
        self.reset_test()

    def restart_with_new_passage(self) -> None:
        """Regenerate new continuous buffer and restart."""
        self.reset_test()

    # ========================================================================
    # LIFECYCLE HOOKS
    # ========================================================================

    def on_show(self, **kwargs) -> None:
        """
        Invoked when user navigates to this screen.
        Applies navigation parameters or loads user preferences.
        """
        super().on_show(**kwargs)
        settings = storage.load_settings()
        self.feedback_mode = settings.get("typing_feedback_mode", "live")
        self.caret_style = settings.get("caret_style", "Highlight")

        preserve = kwargs.get("preserve_config", False)

        if "duration" in kwargs and kwargs["duration"] is not None:
            self.selected_duration = int(kwargs["duration"])
        elif not preserve:
            self.selected_duration = int(settings.get("default_duration", 60))

        if "difficulty" in kwargs and kwargs["difficulty"] is not None:
            self.selected_difficulty = str(kwargs["difficulty"])
        elif not preserve:
            self.selected_difficulty = str(settings.get("default_difficulty", "Medium"))

        if "mode" in kwargs and kwargs["mode"] is not None:
            self.selected_mode = str(kwargs["mode"])
        elif not preserve:
            self.selected_mode = str(settings.get("default_mode", "Mixed"))

        self.master_mode = bool(settings.get("master_mode", False))
        if "master_mode" in kwargs:
            self.master_mode = bool(kwargs["master_mode"])

        custom_text = kwargs.get("custom_text")
        weak_keys = kwargs.get("weak_keys")
        if custom_text:
            self.content_gen.set_custom_text(custom_text)
        elif weak_keys:
            weak_passage = self.content_gen.generate_weak_key_practice(weak_keys)
            self.content_gen.set_custom_text(weak_passage)
        else:
            self.content_gen.clear_custom_text()

        self._update_header_meta()
        self._apply_preferences()
        self.reset_test()
        if hasattr(self, "focus_after_id") and self.focus_after_id:
            try:
                self.after_cancel(self.focus_after_id)
            except Exception:
                pass
        self.focus_after_id = self.after(50, self.focus_input)

    def _apply_preferences(self) -> None:
        """Apply user configuration for text size, line width, hints, and live metrics."""
        settings = storage.load_settings()
        self.feedback_mode = settings.get("typing_feedback_mode", "live")
        self.caret_style = settings.get("caret_style", "Highlight")

        # 1. Text size preference
        size_pref = str(settings.get("passage_text_size", "medium")).lower()
        if size_pref == "small":
            font_size = 15
            spacing = 10
        elif size_pref == "large":
            font_size = 22
            spacing = 16
        else:  # medium
            font_size = 18
            spacing = 12

        # 2. Caret style, width & blinking
        caret_width = 3 if self.caret_style in ("Minimal", "Thick") else 2
        blinking_pref = bool(settings.get("caret_blinking", True)) and not bool(settings.get("reduced_motion", False))
        ontime = 500 if blinking_pref else 100000
        offtime = 500 if blinking_pref else 0

        if hasattr(self, "text_display"):
            self.text_display.config(
                font=(theme.FONT_FAMILY_MONO, font_size),
                spacing2=spacing,
                insertwidth=caret_width,
                insertontime=ontime,
                insertofftime=offtime,
                insertbackground=theme.ACCENT_PRIMARY
            )

        # 3. Line width padding
        width_pref = str(settings.get("passage_line_width", "balanced")).lower()
        if width_pref == "compact":
            h_pad = 120
        elif width_pref == "wide":
            h_pad = 24
        else:  # balanced
            h_pad = 64

        if hasattr(self, "passage_wrapper"):
            self.passage_wrapper.config(padx=h_pad)

        # 4. Keyboard hints visibility
        show_hints = bool(settings.get("show_keyboard_hints", True))
        if hasattr(self, "controls_frame"):
            if show_hints:
                if not bool(self.controls_frame.winfo_manager()):
                    self.controls_frame.pack(fill="x", side="bottom")
            else:
                if bool(self.controls_frame.winfo_manager()):
                    self.controls_frame.pack_forget()

        # 5. Live metrics visibility (countdown timer stays visible)
        show_metrics = bool(settings.get("show_live_metrics", True))
        if hasattr(self, "col_wpm") and hasattr(self, "metric_separators"):
            ordered_widgets = []
            if len(self.metric_separators) > 0:
                ordered_widgets.append(self.metric_separators[0])
            ordered_widgets.append(self.col_wpm)
            if len(self.metric_separators) > 1:
                ordered_widgets.append(self.metric_separators[1])
            ordered_widgets.append(self.col_acc)
            if len(self.metric_separators) > 2:
                ordered_widgets.append(self.metric_separators[2])
            ordered_widgets.append(self.col_err)

            for w in ordered_widgets:
                if show_metrics:
                    if not bool(w.winfo_manager()):
                        if w in self.metric_separators:
                            w.pack(side="left", fill="y", pady=theme.SPACE_XS)
                        else:
                            w.pack(side="left", padx=theme.SPACE_LG)
                else:
                    if bool(w.winfo_manager()):
                        w.pack_forget()

    def on_hide(self) -> None:
        """Invoked when user navigates away from this screen."""
        if hasattr(self, "auto_nav_after_id") and self.auto_nav_after_id:
            try:
                self.after_cancel(self.auto_nav_after_id)
            except Exception:
                pass
            self.auto_nav_after_id = None
        if self.timer_after_id:
            try:
                self.after_cancel(self.timer_after_id)
            except Exception:
                pass
            self.timer_after_id = None
        if self.caret_blink_id:
            try:
                self.after_cancel(self.caret_blink_id)
            except Exception:
                pass
            self.caret_blink_id = None
        if hasattr(self, "caret_update_id") and self.caret_update_id:
            try:
                self.after_cancel(self.caret_update_id)
            except Exception:
                pass
            self.caret_update_id = None
        if hasattr(self, "focus_after_id") and self.focus_after_id:
            try:
                self.after_cancel(self.focus_after_id)
            except Exception:
                pass
            self.focus_after_id = None

    def _on_edition_changed_bg(self, new_ed: str, old_ed: str, colors: Dict[str, str]) -> None:
        """Update background colors smoothly when active edition theme changes."""
        super()._on_edition_changed_bg(new_ed, old_ed, colors)
        bg = colors.get("bg_primary", theme.BG_PRIMARY)
        for w in (self.container, self.session_header, self.metrics_container, self.passage_wrapper, self.passage_center_box, self.text_frame, self.progress_frame, self.controls_frame):
            try:
                w.config(bg=bg)
            except Exception:
                pass
        if hasattr(self, "text_display"):
            self.text_display.config(bg=bg)
        if hasattr(self, "edition_badge") and hasattr(self.app, "edition_manager"):
            self.edition_badge.set_text(self.app.edition_manager.get_display_name().upper())
