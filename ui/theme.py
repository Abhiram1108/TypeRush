"""
TypeRush 2.1 Design System — Midnight Minimal Theme Tokens & Constants

Centralized configuration for colors, typography, dimensions, spacing,
radii, and semantic visual styles across the TypeRush desktop application.
Inspired by modern dark workspaces, refined minimalism, and Swiss editorial design.
Single unified visual identity: Midnight Minimal.
"""

from typing import Dict, Any, Tuple
import tkinter.font as tkfont


# ============================================================================
# BASE PALETTE & SEMANTIC COLOR SYSTEM (MIDNIGHT MINIMAL)
# ============================================================================

# Base surfaces & backgrounds (Midnight Minimal)
BG_PRIMARY = "#0B0D12"          # Very dark charcoal workspace background
BG_SECONDARY = "#121620"        # Structured framing, sidebar, and header bar
SURFACE_DEFAULT = "#181D29"     # Default card, container, and modal panel surface
SURFACE_ELEVATED = "#181D29"    # Elevated cards, popups, and interactive inputs
SURFACE_HOVER = "#222838"       # Hovered elevated surface
SURFACE_ACTIVE = "#2A3245"      # Active/selected list item or segment
SURFACE_GLASS = "#141822"       # Translucent-tinted surface for glass-inspired panels
SURFACE_GLASS_BORDER = "#252B38"# Soft perimeter boundary for glass panels
SURFACE_GLASS_HIGHLIGHT = "#323B4E" # Top highlight edge creating subtle refraction

# Typography hierarchy
TEXT_PRIMARY = "#F3F4F6"        # High-contrast headers, active labels, primary text
TEXT_SECONDARY = "#9299A8"      # Subtitles, body descriptions, secondary statistics
TEXT_MUTED = "#697386"          # Unselected items, placeholder text, captions, hints
TEXT_INVERSE = "#0B0D12"        # High-contrast dark text on bright accent buttons

# Accent colors (Restrained violet and ice-blue dual palette)
ACCENT_PRIMARY = "#987BFF"      # Restrained violet for primary actions, focus states, and caret
ACCENT_SECONDARY = "#9BCBFF"    # Ice blue for secondary highlights, analytics, and progress
ACCENT_HOVER = "#886AFA"        # Refined hover state for primary accent buttons
ACCENT_PRESSED = "#7756F0"      # Active/pressed feedback for primary accent
ACCENT_SUBTLE = "#1E1A33"       # Subtle purple-tinted pill and selection background
ACCENT_ICE_SUBTLE = "#162030"   # Subtle ice-blue tint for secondary badges

# Semantic status colors
STATUS_SUCCESS = "#4ADE80"      # Readable green for high accuracy, completed states
STATUS_ERROR = "#F87171"        # Readable red for typos and error alerts
STATUS_WARNING = "#FBBF24"      # Amber for notices and caution indicators

# Borders & divider lines
BORDER_SUBTLE = "#252B38"       # Standard component boundary and card outlines
BORDER_MUTED = "#1A1F2B"        # Very subtle interior dividers and separators
BORDER_FOCUS = "#987BFF"        # Focus ring indicator for active keyboard navigation
BORDER_ICE = "#2F3B54"          # Subtle ice-blue accent border

# Passage typing character colors
PASSAGE_CORRECT = "#4ADE80"      # Readable green for correctly typed characters
PASSAGE_INCORRECT = "#F87171"    # Readable red for incorrect characters
PASSAGE_INCORRECT_BG = "#2E151E" # Subtle red background tint for live error feedback
PASSAGE_UNTYPED = "#858D9E"      # Neutral muted grey for characters not yet reached
PASSAGE_CURRENT_WORD = "#C5CAD5" # Clean bright foreground for active word being typed
PASSAGE_CURRENT_BG = "#171C28"   # Subtle dark highlight container under active word
PASSAGE_CURRENT_FG = PASSAGE_CURRENT_WORD # Alias for compatibility
PASSAGE_CARET = "#987BFF"        # Vibrant native insertion caret color
PASSAGE_FOCUS_TYPED = "#9299A8"  # Clean subdued color for passed text in Focus Mode


# ============================================================================
# COMPATIBILITY ALIASES (Preserving v1.0.0 & Part 1-8 API)
# ============================================================================

BG_MAIN = BG_PRIMARY
BG_CARD = SURFACE_DEFAULT
BG_SURFACE = SURFACE_ELEVATED
BG_SURFACE_HOVER = SURFACE_HOVER
BG_ACTIVE = SURFACE_ACTIVE
BORDER_COLOR = BORDER_SUBTLE
COLOR_SUCCESS = STATUS_SUCCESS
COLOR_ERROR = STATUS_ERROR
COLOR_WARNING = STATUS_WARNING


# ============================================================================
# UNIFIED THEME MAPPING (Backwards-Compatible Edition Aliases)
# All legacy edition keys map directly to Midnight Minimal tokens.
# ============================================================================

_MIDNIGHT_MINIMAL_THEME: Dict[str, str] = {
    "bg_primary": BG_PRIMARY,
    "bg_secondary": BG_SECONDARY,
    "surface_default": SURFACE_DEFAULT,
    "surface_elevated": SURFACE_ELEVATED,
    "surface_hover": SURFACE_HOVER,
    "surface_active": SURFACE_ACTIVE,
    "surface_glass": SURFACE_GLASS,
    "surface_glass_border": SURFACE_GLASS_BORDER,
    "accent_primary": ACCENT_PRIMARY,
    "accent_secondary": ACCENT_SECONDARY,
    "accent_hover": ACCENT_HOVER,
    "accent_subtle": ACCENT_SUBTLE,
    "border_subtle": BORDER_SUBTLE,
    "text_primary": TEXT_PRIMARY,
    "text_secondary": TEXT_SECONDARY,
    "text_muted": TEXT_MUTED,
    "caret_color": ACCENT_PRIMARY,
    "has_mountains": "false",
    "has_radial": "false",
}

EDITION_THEMES: Dict[str, Dict[str, str]] = {
    "pleasant": _MIDNIGHT_MINIMAL_THEME,
    "basic": _MIDNIGHT_MINIMAL_THEME,
    "soundscape": _MIDNIGHT_MINIMAL_THEME,
    "midnight_minimal": _MIDNIGHT_MINIMAL_THEME,
}


# ============================================================================
# TYPOGRAPHY SYSTEM
# ============================================================================

FONT_FAMILY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"
FONT_FAMILY_MONO_FALLBACK = "Courier New"

# Font Scale Tokens (Editorial Hierarchy)
DISPLAY_LARGE = (FONT_FAMILY, 28, "bold")      # Hero numbers, celebration titles
HEADING_LARGE = (FONT_FAMILY, 22, "bold")      # Page headers, hero stat metrics
HEADING_MEDIUM = (FONT_FAMILY, 16, "bold")     # Section headers, card titles
HEADING_SMALL = (FONT_FAMILY, 13, "bold")      # Group labels, small card headings
BODY_LARGE = (FONT_FAMILY, 13)                 # Prominent reading body, lead descriptions
BODY_MEDIUM = (FONT_FAMILY, 11)                # Standard UI text, list rows, button labels
BODY_SMALL = (FONT_FAMILY, 10)                 # Secondary labels, metadata, sub-labels
CAPTION = (FONT_FAMILY, 9)                     # Micro hints, keycaps, subtle timestamps
MONOSPACE_TYPING = (FONT_FAMILY_MONO, 17)      # Primary typing passage font

# Compatibility Font Tokens
FONT_BRAND = (FONT_FAMILY, 15, "bold")
FONT_TITLE_LARGE = HEADING_LARGE
FONT_TITLE_MEDIUM = HEADING_MEDIUM
FONT_TITLE_SMALL = HEADING_SMALL
FONT_BODY_LARGE = BODY_LARGE
FONT_BODY = BODY_MEDIUM
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_BODY_SMALL = BODY_SMALL
FONT_BODY_SMALL_BOLD = (FONT_FAMILY, 10, "bold")
FONT_STAT_VALUE = (FONT_FAMILY, 30, "bold")
FONT_STAT_LABEL = (FONT_FAMILY, 10, "bold")
FONT_METRIC_VALUE = (FONT_FAMILY, 22, "bold")
FONT_METRIC_LABEL = (FONT_FAMILY, 9, "bold")
FONT_BUTTON = (FONT_FAMILY, 11, "bold")
FONT_BUTTON_LARGE = (FONT_FAMILY, 12, "bold")
FONT_NAV = (FONT_FAMILY, 11)
FONT_NAV_ACTIVE = (FONT_FAMILY, 11, "bold")
FONT_CODE = (FONT_FAMILY_MONO, 12)
FONT_PASSAGE = MONOSPACE_TYPING
FONT_PASSAGE_ALT = (FONT_FAMILY_MONO_FALLBACK, 17)
FONT_SEGMENT = (FONT_FAMILY, 10)
FONT_SEGMENT_ACTIVE = (FONT_FAMILY, 10, "bold")
FONT_KEYCAP = (FONT_FAMILY, 9, "bold")


# ============================================================================
# SPACING, RADII & SIZING TOKENS
# ============================================================================

# Strict Spacing Scale (4, 8, 12, 16, 20, 24, 32, 40, 48, 64)
SPACE_4 = 4
SPACE_8 = 8
SPACE_12 = 12
SPACE_16 = 16
SPACE_20 = 20
SPACE_24 = 24
SPACE_32 = 32
SPACE_40 = 40
SPACE_48 = 48
SPACE_64 = 64

# Compatibility spacing tokens
SPACE_2XS = SPACE_4
SPACE_XS = SPACE_8
SPACE_SM = SPACE_12
SPACE_MD = SPACE_16
SPACE_LG = SPACE_24
SPACE_XL = SPACE_32
SPACE_2XL = SPACE_48

# Corner Radii Scale
RADIUS_SM = 6       # Badges, small inputs, micro buttons
RADIUS_MD = 10      # Standard buttons, segmented controls
RADIUS_LG = 14      # Standard cards, modal dialogs, elevated containers
RADIUS_XL = 18      # Large hero summary cards, outer containers

CARD_CORNER_RADIUS = RADIUS_LG
BUTTON_CORNER_RADIUS = RADIUS_SM
BORDER_WIDTH = 1

# Window Dimensions & Breakpoints
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 800
WINDOW_MIN_WIDTH = 950
WINDOW_MIN_HEIGHT = 650

# Core Structure Sizing
SIDEBAR_WIDTH = 240
HEADER_HEIGHT = 76
BUTTON_HEIGHT = 38
BUTTON_HEIGHT_LARGE = 44
