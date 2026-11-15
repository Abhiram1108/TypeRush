"""
TypeRush Main Application Shell

Manages the primary window, sidebar navigation, header context, and screen routing.
"""

import os
import tkinter as tk
from typing import Dict, Tuple
from ui import theme, storage
from ui.animations import AnimationManager
from ui.edition_manager import EditionManager
from ui.audio_manager import AudioManager
from ui.components import NavigationButton, HeaderBar, Badge
from ui.screens import (
    BaseScreen,
    HomeScreen,
    TypingScreen,
    ResultsScreen,
    HistoryScreen,
    SettingsScreen,
)


class TypeRushApp(tk.Tk):
    """
    Main TypeRush application window and state container.
    """

    # Screen metadata: (Screen Class, Header Title, Header Subtitle)
    SCREEN_CONFIG = {
        "home": (HomeScreen, "Dashboard", "Overview and typing performance"),
        "typing": (TypingScreen, "Typing Test", "Speed and accuracy benchmark"),
        "results": (ResultsScreen, "Test Results", "Performance analysis and metrics"),
        "history": (HistoryScreen, "History", "Past tests and progression history"),
        "settings": (SettingsScreen, "Settings", "Preferences and configuration"),
    }

    def __init__(self):
        super().__init__()

        self.title("TypeRush")
        self.configure(bg=theme.BG_MAIN)
        self.minsize(theme.WINDOW_MIN_WIDTH, theme.WINDOW_MIN_HEIGHT)

        # Center the window on screen
        self._center_window(theme.WINDOW_DEFAULT_WIDTH, theme.WINDOW_DEFAULT_HEIGHT)

        # Set window icon if locally available
        self._setup_window_icon()

        # Application state
        self.screens: Dict[str, BaseScreen] = {}
        self.active_screen_name: str = ""
        self.nav_buttons: Dict[str, NavigationButton] = {}
        self.last_session_result = None

        # Global animation and edition managers
        self.anim_manager = AnimationManager(self)
        self.edition_manager = EditionManager(self.anim_manager)
        self.audio_manager = AudioManager(self)
        settings = storage.load_settings()
        self.anim_manager.set_reduced_motion(settings.get("reduced_motion", False))
        self.edition_manager.subscribe(self._on_edition_changed)

        # Build application shell layout
        self._build_layout()

        # Register screens
        self._register_screens()

        # Apply current edition theme
        self._apply_edition_theme(self.edition_manager.get_theme_colors())

        # Intercept native window close for safe active test handling
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Display initial screen
        self.show_screen("home")

    def _on_window_close(self) -> None:
        """Handle native Windows title-bar close button reliably."""
        typing_screen = self.screens.get("typing")
        if typing_screen and hasattr(typing_screen, "state") and typing_screen.state == "typing":
            settings = storage.load_settings()
            if settings.get("confirm_exit", False):
                typing_screen.request_exit(action="quit")
                return
            else:
                typing_screen.cancel_test()

        # Cancel any active audio or animations
        if hasattr(self, "audio_manager"):
            try:
                self.audio_manager.stop_all()
            except Exception:
                pass
        if hasattr(self, "anim_manager"):
            try:
                self.anim_manager.cancel_all()
            except Exception:
                pass

        self.destroy()

    def _center_window(self, width: int, height: int) -> None:
        """Position the application window in the center of the display."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, int((screen_w - width) / 2))
        y = max(0, int((screen_h - height) / 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_window_icon(self) -> None:
        """Load and set application window icon if asset is present."""
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "app.ico")
        if os.path.isfile(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def _build_layout(self) -> None:
        """Establish the two-column layout: Sidebar on left, Content on right."""
        # Main horizontal container
        self.main_container = tk.Frame(self, bg=theme.BG_MAIN)
        self.main_container.pack(fill="both", expand=True)

        # 1. Left Navigation Sidebar
        self._build_sidebar()

        # 2. Right Side Workspace (Header + Content Area)
        self.workspace_frame = tk.Frame(self.main_container, bg=theme.BG_MAIN)
        self.workspace_frame.pack(side="right", fill="both", expand=True)

        # Top Header Bar
        self.header_bar = HeaderBar(self.workspace_frame, app=self)
        self.header_bar.pack(side="top", fill="x")

        # Central Screen Container
        self.content_container = tk.Frame(self.workspace_frame, bg=theme.BG_MAIN)
        self.content_container.pack(side="top", fill="both", expand=True)

    def _build_sidebar(self) -> None:
        """Construct the elegant dark sidebar navigation."""
        self.sidebar_frame = tk.Frame(
            self.main_container,
            bg=theme.BG_SECONDARY,
            width=theme.SIDEBAR_WIDTH
        )
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # 1. Brand / Logo Identity
        brand_frame = tk.Frame(
            self.sidebar_frame,
            bg=theme.BG_SECONDARY,
            height=theme.HEADER_HEIGHT
        )
        brand_frame.pack(fill="x", padx=theme.SPACE_MD)
        brand_frame.pack_propagate(False)

        brand_inner = tk.Frame(brand_frame, bg=theme.BG_SECONDARY)
        brand_inner.pack(side="left", pady=(theme.SPACE_MD + 2, 0))

        # Brand Icon symbol
        brand_icon = tk.Label(
            brand_inner,
            text="⚡",
            font=(theme.FONT_FAMILY, 15),
            fg=theme.ACCENT_PRIMARY,
            bg=theme.BG_SECONDARY
        )
        brand_icon.pack(side="left", padx=(0, theme.SPACE_XS))

        # Brand Title
        brand_title = tk.Label(
            brand_inner,
            text="TypeRush",
            font=theme.FONT_BRAND,
            fg=theme.TEXT_PRIMARY,
            bg=theme.BG_SECONDARY
        )
        brand_title.pack(side="left")

        # Subtle sidebar divider
        brand_divider = tk.Frame(self.sidebar_frame, bg=theme.BORDER_SUBTLE, height=1)
        brand_divider.pack(fill="x")

        # 2. Navigation items section
        nav_section = tk.Frame(self.sidebar_frame, bg=theme.BG_SECONDARY)
        nav_section.pack(fill="x", padx=theme.SPACE_SM, pady=(theme.SPACE_LG, 0))

        nav_label = tk.Label(
            nav_section,
            text="MENU",
            font=theme.FONT_STAT_LABEL,
            fg=theme.TEXT_MUTED,
            bg=theme.BG_SECONDARY
        )
        nav_label.pack(anchor="w", padx=theme.SPACE_XS, pady=(0, theme.SPACE_SM))

        # Navigation items definitions (Results is accessed via test completion or History, not sidebar)
        nav_items = [
            ("home", "Home", "⌂"),
            ("typing", "Typing Test", "⌨"),
            ("history", "History", "⏱"),
            ("settings", "Settings", "⚙"),
        ]

        for screen_key, label_text, icon_char in nav_items:
            btn = NavigationButton(
                nav_section,
                text=label_text,
                icon=icon_char,
                command=lambda k=screen_key: self.show_screen(k),
                height=42
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[screen_key] = btn

        # 3. Sidebar Footer / Status
        sidebar_footer = tk.Frame(self.sidebar_frame, bg=theme.BG_SECONDARY)
        sidebar_footer.pack(side="bottom", fill="x", padx=theme.SPACE_MD, pady=theme.SPACE_MD)

        footer_divider = tk.Frame(sidebar_footer, bg=theme.BORDER_SUBTLE, height=1)
        footer_divider.pack(fill="x", pady=(0, theme.SPACE_MD))

        footer_badge = Badge(
            sidebar_footer,
            text="TYPE RUSH • v2.1",
            bg_color=theme.BG_SURFACE,
            text_color=theme.TEXT_MUTED,
            border_color=theme.BORDER_SUBTLE,
            parent_bg=theme.BG_SECONDARY
        )
        footer_badge.pack(anchor="w")

    def _register_screens(self) -> None:
        """Instantiate and register all application screens inside content container."""
        for name, (screen_class, _, _) in self.SCREEN_CONFIG.items():
            screen_instance = screen_class(self.content_container, self)
            self.screens[name] = screen_instance

    def _apply_edition_theme(self, colors: Dict[str, str]) -> None:
        """Apply colors of active edition to outer shell."""
        try:
            self.configure(bg=colors["bg_main"])
            self.main_container.config(bg=colors["bg_main"])
            self.workspace_frame.config(bg=colors["bg_main"])
            self.content_container.config(bg=colors["bg_main"])
            self.sidebar_frame.config(bg=colors["bg_secondary"])
            self.header_bar.config(bg=colors["bg_main"])
        except Exception:
            pass

    def _on_edition_changed(self, new_edition: str, old_edition: str, colors: Dict[str, str]) -> None:
        """Smoothly animate color transition between editions and enforce audio policy."""
        if hasattr(self, "audio_manager"):
            if new_edition == "basic":
                try:
                    self.audio_manager.stop_all()
                except Exception:
                    pass
            self.audio_manager.master_enabled = self.edition_manager.is_sound_enabled()

        if hasattr(self, "header_bar"):
            self.header_bar.sync_edition(self.edition_manager.get_display_name())

        pairs = [
            (self, "bg", colors["bg_main"]),
            (self.main_container, "bg", colors["bg_main"]),
            (self.workspace_frame, "bg", colors["bg_main"]),
            (self.content_container, "bg", colors["bg_main"]),
            (self.sidebar_frame, "bg", colors["bg_secondary"]),
            (self.header_bar, "bg", colors["bg_main"]),
        ]
        color_list = []
        for w, prop, target_c in pairs:
            try:
                cur_c = str(w.cget(prop))
                color_list.append((w, prop, cur_c, target_c))
            except Exception:
                pass

        self.anim_manager.transition_colors(color_list, duration_ms=220)

    @property
    def current_screen_name(self) -> str:
        """Alias for active_screen_name."""
        return self.active_screen_name

    def show_screen(self, screen_name: str, **kwargs) -> None:
        """Switch active screen view with smooth directional animation and update navigation."""
        if screen_name not in self.screens:
            return

        # Cache session result if passed (unless viewing historical record)
        is_historical = kwargs.get("is_historical", False)
        if "session_result" in kwargs and kwargs["session_result"] is not None:
            if not is_historical:
                self.last_session_result = kwargs["session_result"]
        elif screen_name == "results" and self.last_session_result is not None:
            kwargs.setdefault("session_result", self.last_session_result)

        old_screen = self.screens.get(self.active_screen_name) if self.active_screen_name else None
        if old_screen:
            old_screen.on_hide()

        # Update active navigation button indicator
        for key, nav_btn in self.nav_buttons.items():
            nav_btn.set_active(key == screen_name)

        new_screen = self.screens[screen_name]
        self.active_screen_name = screen_name

        # Focus Layout management: during typing tests, prioritize typing workspace over sidebar navigation
        if screen_name == "typing":
            if hasattr(self, "sidebar_frame") and bool(self.sidebar_frame.winfo_manager()):
                self.sidebar_frame.pack_forget()
            if hasattr(self, "header_bar") and bool(self.header_bar.winfo_manager()):
                self.header_bar.pack_forget()
        else:
            if hasattr(self, "sidebar_frame") and not bool(self.sidebar_frame.winfo_manager()):
                self.sidebar_frame.pack(side="left", fill="y", before=self.workspace_frame)
            if hasattr(self, "header_bar") and not bool(self.header_bar.winfo_manager()):
                self.header_bar.pack(side="top", fill="x", before=self.content_container)

        # Update Header Title and Subtitle
        _, title, subtitle = self.SCREEN_CONFIG[screen_name]
        self.header_bar.update_header(title, subtitle)

        # Smooth screen navigation animation (~180-200ms)
        if old_screen and old_screen != new_screen:
            if hasattr(self, "audio_manager"):
                self.audio_manager.play_navigation()
            new_screen.on_show(**kwargs)
            self.anim_manager.transition_screen(
                container=self.content_container,
                old_screen=old_screen,
                new_screen=new_screen,
                duration_ms=180
            )
        else:
            if old_screen:
                old_screen.pack_forget()
            new_screen.pack(fill="both", expand=True)
            new_screen.on_show(**kwargs)
