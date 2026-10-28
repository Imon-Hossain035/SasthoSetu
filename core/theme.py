"""Theme and styling configuration for SasthoSetu (Prompt 18 Final Polishing).

This module defines the color palette, typography hierarchy, component dimensions,
and appearance settings used across the desktop application to maintain a clean,
modern, professional, healthcare-oriented visual identity suitable for university demonstration.
"""

# Appearance Mode: Light mode by default as required
APPEARANCE_MODE = "Light"
DEFAULT_COLOR_THEME = "blue"

# =============================================================================
# 1. Professional Healthcare Color Palette
# =============================================================================
COLOR_PRIMARY = "#0D9488"          # Clinical Teal (trustworthy, modern healthcare)
COLOR_PRIMARY_HOVER = "#0F766E"    # Darker teal for button hover states
COLOR_PRIMARY_TEXT = "#FFFFFF"     # White text on primary buttons

COLOR_BG_MAIN = "#F1F5F9"          # Soft slate background (comfortable for daily use)
COLOR_CARD_BG = "#FFFFFF"          # Pure white container/card background
COLOR_CARD_BORDER = "#E2E8F0"      # Subtle border for structured containers

COLOR_TEXT_TITLE = "#0F172A"       # Dark slate for primary titles
COLOR_TEXT_BODY = "#334155"        # Medium slate for readable body text
COLOR_TEXT_MUTED = "#64748B"       # Muted slate for subtitles and helper notes
COLOR_TEXT_DISCLAIMER = "#64748B"  # Muted slate for medical disclaimers

# --- Form Inputs ---
COLOR_INPUT_BG = "#F8FAFC"         # Light slate input background
COLOR_INPUT_BORDER = "#CBD5E1"     # Neutral border for text entries
COLOR_INPUT_FOCUS = "#0D9488"      # Teal highlight on focus

# --- Alerts & Notifications ---
COLOR_NOTICE_BG = "#ECFDF5"        # Soft emerald tint for success notifications
COLOR_NOTICE_TEXT = "#065F46"      # Deep emerald text for confirmation messages
COLOR_NOTICE_BORDER = "#A7F3D0"    # Subtle notice border

COLOR_DANGER_BG = "#FEF2F2"        # Soft red tint for error messages
COLOR_DANGER_TEXT = "#991B1B"      # Dark red text for error messages
COLOR_DANGER_BORDER = "#FECACA"    # Subtle red border for errors

# --- Triage Urgency Semantic Colors ---
COLOR_URGENT_ACCENT = "#DC2626"    # Emergency red
COLOR_URGENT_BG = "#FEF2F2"        # Light red container
COLOR_URGENT_BORDER = "#FECACA"
COLOR_URGENT_HOVER = "#B91C1C"

COLOR_MODERATE_ACCENT = "#D97706"  # Warning amber
COLOR_MODERATE_BG = "#FFFBEB"      # Light amber container
COLOR_MODERATE_BORDER = "#FDE68A"
COLOR_MODERATE_HOVER = "#B45309"

COLOR_ROUTINE_ACCENT = "#16A34A"   # Calming green
COLOR_ROUTINE_BG = "#F0FDF4"       # Light green container
COLOR_ROUTINE_BORDER = "#BBF7D0"
COLOR_ROUTINE_HOVER = "#15803D"

COLOR_PENDING_ACCENT = "#64748B"   # Neutral pending slate
COLOR_PENDING_BG = "#F8FAFC"       # Light neutral container
COLOR_PENDING_BORDER = "#E2E8F0"

# --- Consultation Status Colors ---
COLOR_STATUS_WAITING_BG = "#EFF6FF"
COLOR_STATUS_WAITING_TEXT = "#1E40AF"
COLOR_STATUS_WAITING_BORDER = "#BFDBFE"

COLOR_STATUS_IN_CONSULTATION_BG = "#FFF7ED"
COLOR_STATUS_IN_CONSULTATION_TEXT = "#9A3412"
COLOR_STATUS_IN_CONSULTATION_BORDER = "#FED7AA"

COLOR_STATUS_COMPLETED_BG = "#F1F5F9"
COLOR_STATUS_COMPLETED_TEXT = "#475569"
COLOR_STATUS_COMPLETED_BORDER = "#CBD5E1"

# =============================================================================
# 2. Typography Hierarchy (Windows & Unicode Compatible)
# =============================================================================
# "Segoe UI" reliably renders Latin, numbers, and Bengali Unicode glyphs on Windows
FONT_FAMILY = "Segoe UI"

FONT_APP_TITLE = (FONT_FAMILY, 20, "bold")
FONT_PAGE_TITLE = (FONT_FAMILY, 22, "bold")
FONT_SECTION_HEADING = (FONT_FAMILY, 15, "bold")
FONT_SUBHEADING = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 13)
FONT_BODY_BOLD = (FONT_FAMILY, 13, "bold")
FONT_CAPTION = (FONT_FAMILY, 11)
FONT_CAPTION_BOLD = (FONT_FAMILY, 11, "bold")
FONT_BUTTON = (FONT_FAMILY, 13, "bold")
FONT_BADGE = (FONT_FAMILY, 11, "bold")
FONT_HERO_URGENCY = (FONT_FAMILY, 28, "bold")

# =============================================================================
# 3. Standard Layout Spacing & Component Dimensions
# =============================================================================
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 12
SPACING_LG = 16
SPACING_XL = 24

CORNER_RADIUS_SM = 6
CORNER_RADIUS_MD = 8
CORNER_RADIUS_LG = 12

BTN_HEIGHT_SM = 30
BTN_HEIGHT_MD = 38
BTN_HEIGHT_LG = 42

INPUT_HEIGHT_MD = 38
