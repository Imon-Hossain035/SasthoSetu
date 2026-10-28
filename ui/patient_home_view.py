"""Patient / Health Worker Home Page View for SasthoSetu (Prompt 05).

This module defines the main landing dashboard for health workers and patients,
providing the entry point for new assessments and explaining the triage tiers.
"""

from typing import Any, Callable, Dict, Optional
import customtkinter as ctk
from core import constants, theme


class PatientHomeView(ctk.CTkFrame):
    """Patient / Health Worker Home Page dashboard."""

    def __init__(
        self,
        master: Any,
        user_record: Dict[str, Any],
        on_start_assessment: Optional[Callable[[], None]] = None,
        on_switch_role: Optional[Callable[[], None]] = None,
        on_logout: Optional[Callable[[], None]] = None,
        access_error: Optional[str] = None,
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.user_record = user_record
        self.on_start_assessment = on_start_assessment
        self.on_switch_role = on_switch_role or (lambda: None)
        self.on_logout = on_logout or (lambda: None)
        self.access_error = access_error

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the Patient / Health Worker dashboard layout."""
        # Top Sub-Navbar with Portal Title & User Controls
        self._build_portal_header()

        # Scrollable Content Body to ensure perfect responsiveness on all screen sizes
        self.scroll_body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_body.pack(fill="both", expand=True, padx=25, pady=(0, 10))

        # Access Denied Warning Banner (if patient role attempted clinician access)
        if self.access_error:
            err_box = ctk.CTkFrame(
                self.scroll_body,
                fg_color=theme.COLOR_DANGER_BG,
                border_width=1,
                border_color=theme.COLOR_DANGER_BORDER,
                corner_radius=8,
            )
            err_box.pack(fill="x", pady=(0, 14))

            ctk.CTkLabel(
                err_box,
                text=f"⚠️ {self.access_error}",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
                text_color=theme.COLOR_DANGER_TEXT,
                justify="center",
            ).pack(padx=16, pady=10)

        # 1. Welcome Section
        self._build_welcome_section()

        # 2. Main Action Card ("New Patient Assessment")
        self._build_assessment_action_card()

        # 3. Urgency Categories Explanation Section
        self._build_urgency_explanation_section()

        # 4. Embedded Safety Disclaimer Card
        self._build_disclaimer_card()

    def _build_portal_header(self) -> None:
        """Creates the portal sub-header with role indicator and logout buttons."""
        header_bar = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            height=50,
        )
        header_bar.pack(fill="x", padx=25, pady=(12, 10))
        header_bar.pack_propagate(False)

        inner = ctk.CTkFrame(header_bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=8)

        # Left: Portal Title & Role Badge
        left_box = ctk.CTkFrame(inner, fg_color="transparent")
        left_box.pack(side="left")

        portal_title = ctk.CTkLabel(
            left_box,
            text="Patient / Health Worker Portal",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        portal_title.pack(side="left")

        role_badge = ctk.CTkLabel(
            left_box,
            text="Intake Desk",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_NOTICE_TEXT,
            fg_color=theme.COLOR_NOTICE_BG,
            corner_radius=5,
            padx=8,
            pady=2,
        )
        role_badge.pack(side="left", padx=(10, 0))

        # Right: User info & action buttons
        right_box = ctk.CTkFrame(inner, fg_color="transparent")
        right_box.pack(side="right")

        user_name = self.user_record.get("full_name", "Health Worker")
        user_lbl = ctk.CTkLabel(
            right_box,
            text=f"User: {user_name}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        user_lbl.pack(side="left", padx=(0, 15))

        btn_switch = ctk.CTkButton(
            right_box,
            text="Switch Role",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_BODY,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=90,
            height=28,
            corner_radius=5,
            command=self.on_switch_role,
        )
        btn_switch.pack(side="left", padx=(0, 8))

        btn_logout = ctk.CTkButton(
            right_box,
            text="Logout",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            fg_color="transparent",
            text_color=theme.COLOR_DANGER_TEXT,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER,
            hover_color=theme.COLOR_DANGER_BG,
            width=70,
            height=28,
            corner_radius=5,
            command=self.on_logout,
        )
        btn_logout.pack(side="left")

    def _build_welcome_section(self) -> None:
        """Renders the welcoming banner introducing the triage desk workflow."""
        welcome_card = ctk.CTkFrame(
            self.scroll_body,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
        )
        welcome_card.pack(fill="x", pady=(0, 15))

        inner = ctk.CTkFrame(welcome_card, fg_color="transparent")
        inner.pack(padx=25, pady=20, fill="x")

        welcome_title = ctk.CTkLabel(
            inner,
            text="Welcome to SasthoSetu",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        welcome_title.pack(fill="x", pady=(0, 6))

        welcome_desc = ctk.CTkLabel(
            inner,
            text=(
                "Submit patient information and symptoms to receive an urgency assessment "
                "and help prioritize the case for clinician review."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_PRIMARY_HOVER,
            anchor="w",
        )
        welcome_desc.pack(fill="x")

    def _build_assessment_action_card(self) -> None:
        """Renders the primary 'New Patient Assessment' CTA card."""
        action_card = ctk.CTkFrame(
            self.scroll_body,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
        )
        action_card.pack(fill="x", pady=(0, 15))

        inner = ctk.CTkFrame(action_card, fg_color="transparent")
        inner.pack(padx=25, pady=22, fill="x")

        title_lbl = ctk.CTkLabel(
            inner,
            text="New Patient Assessment",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        title_lbl.pack(fill="x", pady=(0, 4))

        desc_lbl = ctk.CTkLabel(
            inner,
            text="Enter patient information and reported symptoms for triage.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        desc_lbl.pack(fill="x", pady=(0, 16))

        btn_start = ctk.CTkButton(
            inner,
            text="Start Assessment",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=14, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=200,
            height=40,
            corner_radius=6,
            command=self._on_start_assessment_clicked,
        )
        btn_start.pack(anchor="w")

        # Placeholder notification banner (hidden by default, revealed on click)
        self.notice_frame = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_NOTICE_BG,
            border_width=1,
            border_color=theme.COLOR_NOTICE_BORDER,
            corner_radius=6,
        )
        self.notice_label = ctk.CTkLabel(
            self.notice_frame,
            text="",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_NOTICE_TEXT,
            padx=14,
            pady=8,
        )
        self.notice_label.pack(anchor="w")

    def _build_urgency_explanation_section(self) -> None:
        """Renders information cards explaining URGENT, MODERATE, and ROUTINE tiers."""
        section_frame = ctk.CTkFrame(
            self.scroll_body,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
        )
        section_frame.pack(fill="x", pady=(0, 15))

        inner = ctk.CTkFrame(section_frame, fg_color="transparent")
        inner.pack(padx=25, pady=20, fill="x")

        section_title = ctk.CTkLabel(
            inner,
            text="Triage Urgency Categories",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        section_title.pack(fill="x", pady=(0, 4))

        section_desc = ctk.CTkLabel(
            inner,
            text="The SasthoSetu triage engine categorizes submitted complaints into three priority levels:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        section_desc.pack(fill="x", pady=(0, 15))

        # 3-column Grid for the Urgency Cards
        cards_grid = ctk.CTkFrame(inner, fg_color="transparent")
        cards_grid.pack(fill="x")
        cards_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="urgency_col")

        # 1. URGENT Card
        self._build_tier_card(
            parent=cards_grid,
            col=0,
            tier_title="🔴 URGENT",
            badge_color=theme.COLOR_URGENT_ACCENT,
            bg_color=theme.COLOR_URGENT_BG,
            border_color=theme.COLOR_URGENT_BORDER,
            headline=constants.TIER_DESCRIPTIONS[constants.TIER_URGENT],
            details="Critical indicators like severe dyspnea, acute chest pain, or active hemorrhage.",
        )

        # 2. MODERATE Card
        self._build_tier_card(
            parent=cards_grid,
            col=1,
            tier_title="🟡 MODERATE",
            badge_color=theme.COLOR_MODERATE_ACCENT,
            bg_color=theme.COLOR_MODERATE_BG,
            border_color=theme.COLOR_MODERATE_BORDER,
            headline=constants.TIER_DESCRIPTIONS[constants.TIER_MODERATE],
            details="Sub-acute conditions or severe discomfort requiring same-day physician evaluation.",
        )

        # 3. ROUTINE Card
        self._build_tier_card(
            parent=cards_grid,
            col=2,
            tier_title="🟢 ROUTINE",
            badge_color=theme.COLOR_ROUTINE_ACCENT,
            bg_color=theme.COLOR_ROUTINE_BG,
            border_color=theme.COLOR_ROUTINE_BORDER,
            headline=constants.TIER_DESCRIPTIONS[constants.TIER_ROUTINE],
            details="Mild, chronic, or common complaints that can wait safely in the standard queue.",
        )

    def _build_tier_card(
        self,
        parent: Any,
        col: int,
        tier_title: str,
        badge_color: str,
        bg_color: str,
        border_color: str,
        headline: str,
        details: str,
    ) -> None:
        """Helper to create a single urgency tier explanation card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            border_width=1,
            border_color=border_color,
            corner_radius=8,
        )
        card.grid(row=0, column=col, padx=6, pady=5, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=14, pady=14, fill="both", expand=True)

        title_lbl = ctk.CTkLabel(
            inner,
            text=tier_title,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=14, weight="bold"),
            text_color=badge_color,
            anchor="w",
        )
        title_lbl.pack(fill="x", pady=(0, 4))

        headline_lbl = ctk.CTkLabel(
            inner,
            text=headline,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
            wraplength=230,
            justify="left",
        )
        headline_lbl.pack(fill="x", pady=(0, 6))

        detail_lbl = ctk.CTkLabel(
            inner,
            text=details,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
            wraplength=230,
            justify="left",
        )
        detail_lbl.pack(fill="x")

    def _build_disclaimer_card(self) -> None:
        """Renders the visible decision-support safety disclaimer."""
        disclaimer_card = ctk.CTkFrame(
            self.scroll_body,
            fg_color=theme.COLOR_BG_MAIN,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        disclaimer_card.pack(fill="x", pady=(5, 15))

        inner = ctk.CTkFrame(disclaimer_card, fg_color="transparent")
        inner.pack(padx=20, pady=12, fill="x")

        lbl = ctk.CTkLabel(
            inner,
            text=(
                "⚠️ Medical Safety Boundary: SasthoSetu is a decision-support prototype. "
                "It does not provide medical diagnosis or prescriptions. A clinician makes the final clinical decision."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_DISCLAIMER,
            justify="center",
        )
        lbl.pack(fill="x")

    def _on_start_assessment_clicked(self) -> None:
        """Handles click on 'Start Assessment' button.

        If a navigation handler is provided, transitions to Patient Information Form.
        Otherwise falls back to displaying the informative notice.
        """
        if self.on_start_assessment:
            self.on_start_assessment()
        else:
            self.notice_label.configure(
                text="✓ Patient Information Form will be available in the next step (Prompt 06)."
            )
            self.notice_frame.pack(fill="x", pady=(14, 0), anchor="w")
