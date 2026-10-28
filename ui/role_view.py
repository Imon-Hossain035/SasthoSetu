"""User Role Selection and Role Placeholder Views for SasthoSetu (Prompt 04).

This module contains:
- RoleSelectionView: Allows authenticated users to pick their role.
- PatientPlaceholderView: Temporary screen for Patient / Health Worker.
- ClinicianPlaceholderView: Temporary screen for Clinician.
"""

from typing import Any, Callable, Dict, Optional
import customtkinter as ctk
from core import constants, theme


class RoleSelectionView(ctk.CTkFrame):
    """View allowing the user to select between Patient/Health Worker and Clinician."""

    def __init__(
        self,
        master: Any,
        user_record: Dict[str, Any],
        on_select_role: Callable[[str], None],
        on_logout: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.user_record = user_record
        self.on_select_role = on_select_role
        self.on_logout = on_logout

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the role selection interface."""
        # Main Card Container
        card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            width=780,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=40, pady=30, fill="both")

        # Top Bar: User info + Logout button
        top_bar = ctk.CTkFrame(inner, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 15))

        user_name = self.user_record.get("full_name", "User")
        user_label = ctk.CTkLabel(
            top_bar,
            text=f"Logged in as: {user_name}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        user_label.pack(side="left")

        btn_logout = ctk.CTkButton(
            top_bar,
            text="Logout",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=theme.COLOR_PRIMARY,
            border_width=1,
            border_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_NOTICE_BG,
            width=80,
            height=28,
            command=self.on_logout,
        )
        btn_logout.pack(side="right")

        # Section Header
        title_label = ctk.CTkLabel(
            inner,
            text="Select Your Role",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=24, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        title_label.pack(pady=(5, 4))

        subtitle_label = ctk.CTkLabel(
            inner,
            text="Choose how you will be using SasthoSetu today to continue.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        subtitle_label.pack(pady=(0, 25))

        # Container for the two role cards side-by-side
        roles_container = ctk.CTkFrame(inner, fg_color="transparent")
        roles_container.pack(fill="x", pady=(0, 10))

        # Configure columns so both cards have equal width
        roles_container.grid_columnconfigure(0, weight=1, uniform="role_card")
        roles_container.grid_columnconfigure(1, weight=1, uniform="role_card")

        # --- Role Card 1: Patient / Health Worker ---
        self._build_role_card(
            parent=roles_container,
            column=0,
            badge_text="Intake & Screening",
            title="Patient / Health Worker",
            description="Enter patient information and symptoms for triage.",
            details="Used at community clinics and upazila telemedicine desks to register incoming patients.",
            button_text="Enter as Health Worker",
            role_key=constants.ROLE_PATIENT_HEALTH_WORKER,
        )

        # --- Role Card 2: Clinician ---
        self._build_role_card(
            parent=roles_container,
            column=1,
            badge_text="Physician Review",
            title="Clinician",
            description="Review patients and manage the triage queue.",
            details="Used by remote doctors to inspect prioritized patient cases and provide consultations.",
            button_text="Enter as Clinician",
            role_key=constants.ROLE_CLINICIAN,
        )

    def _build_role_card(
        self,
        parent: Any,
        column: int,
        badge_text: str,
        title: str,
        description: str,
        details: str,
        button_text: str,
        role_key: str,
    ) -> None:
        """Helper to create a unified role selection card."""
        card_frame = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_BG_MAIN,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=10,
        )
        card_frame.grid(row=0, column=column, padx=12, pady=5, sticky="nsew")

        inner_card = ctk.CTkFrame(card_frame, fg_color="transparent")
        inner_card.pack(padx=20, pady=22, fill="both", expand=True)

        # Role Badge
        badge = ctk.CTkLabel(
            inner_card,
            text=badge_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_PRIMARY,
            fg_color=theme.COLOR_NOTICE_BG,
            corner_radius=6,
            padx=10,
            pady=3,
        )
        badge.pack(anchor="w", pady=(0, 10))

        # Role Title
        title_lbl = ctk.CTkLabel(
            inner_card,
            text=title,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        title_lbl.pack(fill="x", pady=(0, 6))

        # Short Description
        desc_lbl = ctk.CTkLabel(
            inner_card,
            text=description,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_PRIMARY_HOVER,
            anchor="w",
            wraplength=300,
            justify="left",
        )
        desc_lbl.pack(fill="x", pady=(0, 8))

        # Detail text
        detail_lbl = ctk.CTkLabel(
            inner_card,
            text=details,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
            wraplength=300,
            justify="left",
        )
        detail_lbl.pack(fill="x", pady=(0, 20))

        # Selection Button
        btn = ctk.CTkButton(
            inner_card,
            text=button_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            height=38,
            corner_radius=6,
            command=lambda: self.on_select_role(role_key),
        )
        btn.pack(fill="x")


class PatientPlaceholderView(ctk.CTkFrame):
    """Temporary placeholder for Patient / Health Worker role (Prompt 04)."""

    def __init__(
        self,
        master: Any,
        user_record: Dict[str, Any],
        on_switch_role: Callable[[], None],
        on_logout: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.user_record = user_record
        self.on_switch_role = on_switch_role
        self.on_logout = on_logout

        self._build_ui()

    def _build_ui(self) -> None:
        """Renders the Patient/Health Worker role placeholder."""
        card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            width=650,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=45, pady=35, fill="both")

        # Role Badge
        badge = ctk.CTkLabel(
            inner,
            text="Active Role: Patient / Health Worker",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_NOTICE_TEXT,
            fg_color=theme.COLOR_NOTICE_BG,
            corner_radius=6,
            padx=14,
            pady=5,
        )
        badge.pack(pady=(0, 15))

        # Title
        user_name = self.user_record.get("full_name", "User")
        title_label = ctk.CTkLabel(
            inner,
            text="Patient / Health Worker Portal",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=24, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        title_label.pack(pady=(0, 6))

        user_label = ctk.CTkLabel(
            inner,
            text=f"Logged in: {user_name} ({self.user_record.get('username_or_email', '')})",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        user_label.pack(pady=(0, 20))

        # Explanatory card
        info_frame = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_BG_MAIN,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        info_frame.pack(fill="x", pady=(0, 25))

        info_text = ctk.CTkLabel(
            info_frame,
            text=(
                "The Patient Home Page and Symptom Intake workflow will be implemented\n"
                "in the next development stages (Prompts 05, 06, and 07).\n\n"
                "In those stages, health workers will record patient demographics,\n"
                "enter clinical symptoms, and submit cases for automated urgency triage."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_BODY,
            justify="center",
            padx=20,
            pady=18,
        )
        info_text.pack()

        # Action Buttons
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack()

        btn_switch = ctk.CTkButton(
            btn_frame,
            text="← Switch Role",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=140,
            height=36,
            corner_radius=6,
            command=self.on_switch_role,
        )
        btn_switch.pack(side="left", padx=8)

        btn_logout = ctk.CTkButton(
            btn_frame,
            text="Logout",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_MUTED,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=100,
            height=36,
            corner_radius=6,
            command=self.on_logout,
        )
        btn_logout.pack(side="left", padx=8)


class ClinicianPlaceholderView(ctk.CTkFrame):
    """Temporary placeholder for Clinician role (Prompt 04)."""

    def __init__(
        self,
        master: Any,
        user_record: Dict[str, Any],
        on_switch_role: Callable[[], None],
        on_logout: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.user_record = user_record
        self.on_switch_role = on_switch_role
        self.on_logout = on_logout

        self._build_ui()

    def _build_ui(self) -> None:
        """Renders the Clinician role placeholder."""
        card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            width=650,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=45, pady=35, fill="both")

        # Role Badge
        badge = ctk.CTkLabel(
            inner,
            text="Active Role: Clinician",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_PRIMARY,
            fg_color=theme.COLOR_NOTICE_BG,
            corner_radius=6,
            padx=14,
            pady=5,
        )
        badge.pack(pady=(0, 15))

        # Title
        user_name = self.user_record.get("full_name", "Doctor")
        title_label = ctk.CTkLabel(
            inner,
            text="Clinician Portal",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=24, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        title_label.pack(pady=(0, 6))

        user_label = ctk.CTkLabel(
            inner,
            text=f"Logged in: {user_name} ({self.user_record.get('username_or_email', '')})",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        user_label.pack(pady=(0, 20))

        # Explanatory card
        info_frame = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_BG_MAIN,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        info_frame.pack(fill="x", pady=(0, 25))

        info_text = ctk.CTkLabel(
            info_frame,
            text=(
                "The Clinician Dashboard and Priority Queue Management will be implemented\n"
                "in later development stages (Prompt 13 and Prompt 14).\n\n"
                "In those stages, physicians will inspect patients ordered by triage urgency\n"
                "(URGENT > MODERATE > ROUTINE), review symptoms, and update case statuses."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_BODY,
            justify="center",
            padx=20,
            pady=18,
        )
        info_text.pack()

        # Action Buttons
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack()

        btn_switch = ctk.CTkButton(
            btn_frame,
            text="← Switch Role",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=140,
            height=36,
            corner_radius=6,
            command=self.on_switch_role,
        )
        btn_switch.pack(side="left", padx=8)

        btn_logout = ctk.CTkButton(
            btn_frame,
            text="Logout",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_MUTED,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=100,
            height=36,
            corner_radius=6,
            command=self.on_logout,
        )
        btn_logout.pack(side="left", padx=8)
