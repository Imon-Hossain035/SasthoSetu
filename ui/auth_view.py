"""Authentication UI views for SasthoSetu (Prompt 03).

This module contains:
- LoginView: Form for existing users to sign in.
- RegisterView: Form for new users to create an account.
- AuthSuccessView: Temporary placeholder confirmation screen after login.
"""

from typing import Any, Callable, Dict, Optional
import customtkinter as ctk
from core import theme
from services import auth_service


class LoginView(ctk.CTkFrame):
    """Login screen view for SasthoSetu."""

    def __init__(
        self,
        master: Any,
        on_login_success: Callable[[Dict[str, Any]], None],
        on_switch_to_register: Callable[[], None],
        on_back_to_welcome: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.on_login_success = on_login_success
        self.on_switch_to_register = on_switch_to_register
        self.on_back_to_welcome = on_back_to_welcome

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the Login card and form fields."""
        # Central card container
        card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            width=480,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Inner padding frame
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=35, pady=30, fill="both")

        # Top back navigation button
        btn_back = ctk.CTkButton(
            inner,
            text="← Back to Home",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_MUTED,
            hover_color=theme.COLOR_BG_MAIN,
            anchor="w",
            width=110,
            height=26,
            command=self.on_back_to_welcome,
        )
        btn_back.pack(anchor="w", pady=(0, 10))

        # Card Title & Branding
        title_label = ctk.CTkLabel(
            inner,
            text="SasthoSetu (স্বাস্থ্যসেতু)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_PRIMARY,
            anchor="w",
        )
        title_label.pack(fill="x", pady=(0, 2))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            inner,
            text="AI-Assisted Triage System — Secure Login",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        subtitle_label.pack(fill="x", pady=(0, 16))

        # Alert / Message Banner (hidden by default)
        self.alert_frame = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_DANGER_BG,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER,
            corner_radius=theme.CORNER_RADIUS_SM,
        )
        self.alert_label = ctk.CTkLabel(
            self.alert_frame,
            text="",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_DANGER_TEXT,
            padx=12,
            pady=6,
        )
        self.alert_label.pack()

        # Field 1: Username or Email
        lbl_username = ctk.CTkLabel(
            inner,
            text="Username or Email",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_username.pack(fill="x", pady=(10, 4))

        self.entry_username = ctk.CTkEntry(
            inner,
            placeholder_text="Enter your username or email",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=theme.INPUT_HEIGHT_MD,
            corner_radius=theme.CORNER_RADIUS_SM,
        )
        self.entry_username.pack(fill="x", pady=(0, 12))

        # Field 2: Password
        lbl_password = ctk.CTkLabel(
            inner,
            text="Password",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_password.pack(fill="x", pady=(0, 4))

        self.entry_password = ctk.CTkEntry(
            inner,
            placeholder_text="Enter your password",
            show="*",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=theme.INPUT_HEIGHT_MD,
            corner_radius=theme.CORNER_RADIUS_SM,
        )
        self.entry_password.pack(fill="x", pady=(0, 16))

        # Login Button
        self.btn_login = ctk.CTkButton(
            inner,
            text="Login",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=14, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            height=theme.BTN_HEIGHT_LG,
            corner_radius=theme.CORNER_RADIUS_MD,
            command=self._handle_login,
        )
        self.btn_login.pack(fill="x", pady=(5, 14))

        # Switch to Register prompt
        bottom_frame = ctk.CTkFrame(inner, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(4, 0))

        lbl_no_account = ctk.CTkLabel(
            bottom_frame,
            text="Don't have an account? ",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        lbl_no_account.pack(side="left")

        btn_register_switch = ctk.CTkButton(
            bottom_frame,
            text="Create Account",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color="transparent",
            text_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_NOTICE_BG,
            width=100,
            height=26,
            command=self.on_switch_to_register,
        )
        btn_register_switch.pack(side="left")

    def _show_alert(self, message: str, is_error: bool = True) -> None:
        """Displays error or notification banner."""
        if is_error:
            self.alert_frame.configure(
                fg_color=theme.COLOR_DANGER_BG,
                border_color=theme.COLOR_DANGER_BORDER,
            )
            self.alert_label.configure(
                text=message, text_color=theme.COLOR_DANGER_TEXT
            )
        else:
            self.alert_frame.configure(
                fg_color=theme.COLOR_NOTICE_BG,
                border_color=theme.COLOR_NOTICE_BORDER,
            )
            self.alert_label.configure(
                text=message, text_color=theme.COLOR_NOTICE_TEXT
            )
        self.alert_frame.pack(fill="x", pady=(0, 12), before=self.entry_username)

    def _hide_alert(self) -> None:
        """Hides the alert banner."""
        self.alert_frame.pack_forget()

    def _handle_login(self) -> None:
        """Processes login form submission with double-submit prevention."""
        if getattr(self, "_is_submitting", False):
            return
        self._is_submitting = True
        self.btn_login.configure(state="disabled", text="Logging in...")
        self._hide_alert()

        username = self.entry_username.get()
        password = self.entry_password.get()

        try:
            is_valid, msg, user_record = auth_service.authenticate(username, password)

            if not is_valid:
                self._show_alert(msg, is_error=True)
                self._is_submitting = False
                self.btn_login.configure(state="normal", text="Login")
                return

            # Success - notify master app
            if user_record:
                self.on_login_success(user_record)
        except Exception:
            self._show_alert("An unexpected error occurred. Please try again.", is_error=True)
            self._is_submitting = False
            self.btn_login.configure(state="normal", text="Login")


class RegisterView(ctk.CTkFrame):
    """Registration screen view for SasthoSetu."""

    def __init__(
        self,
        master: Any,
        on_register_success: Callable[[str], None],
        on_switch_to_login: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.on_register_success = on_register_success
        self.on_switch_to_login = on_switch_to_login

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the Register card and form fields."""
        card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            width=500,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=35, pady=25, fill="both")

        # Top back navigation button
        btn_back = ctk.CTkButton(
            inner,
            text="← Back to Login",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_MUTED,
            hover_color=theme.COLOR_BG_MAIN,
            anchor="w",
            width=110,
            height=26,
            command=self.on_switch_to_login,
        )
        btn_back.pack(anchor="w", pady=(0, 8))

        # Title & Subtitle
        title_label = ctk.CTkLabel(
            inner,
            text="SasthoSetu (স্বাস্থ্যসেতু)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_PRIMARY,
            anchor="w",
        )
        title_label.pack(fill="x", pady=(0, 2))

        subtitle_label = ctk.CTkLabel(
            inner,
            text="Create an Account — Health Worker & Clinician Portal",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        subtitle_label.pack(fill="x", pady=(0, 14))

        # Alert banner
        self.alert_frame = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_DANGER_BG,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER,
            corner_radius=theme.CORNER_RADIUS_SM,
        )
        self.alert_label = ctk.CTkLabel(
            self.alert_frame,
            text="",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_DANGER_TEXT,
            padx=12,
            pady=6,
        )
        self.alert_label.pack()

        # Field 1: Full Name
        lbl_fullname = ctk.CTkLabel(
            inner,
            text="Full Name",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_fullname.pack(fill="x", pady=(4, 2))

        self.entry_fullname = ctk.CTkEntry(
            inner,
            placeholder_text="Enter your full name",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=theme.INPUT_HEIGHT_MD,
            corner_radius=theme.CORNER_RADIUS_SM,
        )
        self.entry_fullname.pack(fill="x", pady=(0, 8))

        # Field 2: Username or Email
        lbl_username = ctk.CTkLabel(
            inner,
            text="Email or Username",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_username.pack(fill="x", pady=(0, 2))

        self.entry_username = ctk.CTkEntry(
            inner,
            placeholder_text="e.g. name@upazila.dghs.gov.bd or username",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=theme.INPUT_HEIGHT_MD,
            corner_radius=theme.CORNER_RADIUS_SM,
        )
        self.entry_username.pack(fill="x", pady=(0, 8))

        # Field 3: Password
        lbl_password = ctk.CTkLabel(
            inner,
            text="Password",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_password.pack(fill="x", pady=(0, 2))

        self.entry_password = ctk.CTkEntry(
            inner,
            placeholder_text="Create a password (min 4 characters)",
            show="*",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=theme.INPUT_HEIGHT_MD,
            corner_radius=theme.CORNER_RADIUS_SM,
        )
        self.entry_password.pack(fill="x", pady=(0, 8))

        # Field 4: Confirm Password
        lbl_confirm = ctk.CTkLabel(
            inner,
            text="Confirm Password",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_confirm.pack(fill="x", pady=(0, 2))

        self.entry_confirm = ctk.CTkEntry(
            inner,
            placeholder_text="Re-enter password to confirm",
            show="*",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=theme.INPUT_HEIGHT_MD,
            corner_radius=theme.CORNER_RADIUS_SM,
        )
        self.entry_confirm.pack(fill="x", pady=(0, 14))

        # Register Button
        self.btn_register = ctk.CTkButton(
            inner,
            text="Create Account",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=14, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            height=theme.BTN_HEIGHT_LG,
            corner_radius=theme.CORNER_RADIUS_MD,
            command=self._handle_register,
        )
        self.btn_register.pack(fill="x", pady=(0, 10))

        # Switch to Login prompt
        bottom_frame = ctk.CTkFrame(inner, fg_color="transparent")
        bottom_frame.pack(fill="x")

        lbl_have_account = ctk.CTkLabel(
            bottom_frame,
            text="Already have an account? ",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        lbl_have_account.pack(side="left")

        btn_login_switch = ctk.CTkButton(
            bottom_frame,
            text="Login",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color="transparent",
            text_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_NOTICE_BG,
            width=60,
            height=24,
            command=self.on_switch_to_login,
        )
        btn_login_switch.pack(side="left")

    def _show_alert(self, message: str, is_error: bool = True) -> None:
        """Displays error or success message in the form."""
        if is_error:
            self.alert_frame.configure(
                fg_color=theme.COLOR_DANGER_BG,
                border_color=theme.COLOR_DANGER_BORDER,
            )
            self.alert_label.configure(
                text=message, text_color=theme.COLOR_DANGER_TEXT
            )
        else:
            self.alert_frame.configure(
                fg_color=theme.COLOR_NOTICE_BG,
                border_color=theme.COLOR_NOTICE_BORDER,
            )
            self.alert_label.configure(
                text=message, text_color=theme.COLOR_NOTICE_TEXT
            )
        self.alert_frame.pack(fill="x", pady=(0, 10), before=self.entry_fullname)

    def _hide_alert(self) -> None:
        """Hides the alert banner."""
        self.alert_frame.pack_forget()

    def _handle_register(self) -> None:
        """Processes account registration with double-submit prevention."""
        if getattr(self, "_is_submitting", False):
            return
        self._is_submitting = True
        self.btn_register.configure(state="disabled", text="Creating account...")
        self._hide_alert()

        fullname = self.entry_fullname.get()
        username = self.entry_username.get()
        password = self.entry_password.get()
        confirm = self.entry_confirm.get()

        try:
            is_valid, msg = auth_service.register(fullname, username, password, confirm)

            if not is_valid:
                self._show_alert(msg, is_error=True)
                self._is_submitting = False
                self.btn_register.configure(state="normal", text="Create Account")
                return

            # Registration succeeded: notify master app with username
            self.on_register_success(username)
        except Exception:
            self._show_alert("An unexpected error occurred. Please try again.", is_error=True)
            self._is_submitting = False
            self.btn_register.configure(state="normal", text="Create Account")


class AuthSuccessView(ctk.CTkFrame):
    """Temporary post-login placeholder confirmation screen (Prompt 03).

    Displays confirmation of successful authentication and informs the user
    that User Role selection will be implemented in Prompt 04.
    """

    def __init__(
        self,
        master: Any,
        user_record: Dict[str, Any],
        on_logout: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.user_record = user_record
        self.on_logout = on_logout

        self._build_ui()

    def _build_ui(self) -> None:
        """Renders the success confirmation card."""
        card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            width=550,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=40, pady=35, fill="both")

        # Success icon / badge
        badge = ctk.CTkLabel(
            inner,
            text="✓ Login Successful",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=theme.COLOR_NOTICE_TEXT,
            fg_color=theme.COLOR_NOTICE_BG,
            corner_radius=8,
            padx=16,
            pady=6,
        )
        badge.pack(pady=(0, 15))

        # User greeting
        user_name = self.user_record.get("full_name", "User")
        user_id = self.user_record.get("username_or_email", "")

        greeting_label = ctk.CTkLabel(
            inner,
            text=f"Welcome, {user_name}!",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        greeting_label.pack(pady=(0, 4))

        id_label = ctk.CTkLabel(
            inner,
            text=f"Logged in as: {user_id}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        id_label.pack(pady=(0, 20))

        # Roadmap info card
        info_box = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_BG_MAIN,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        info_box.pack(fill="x", pady=(0, 25))

        info_text = ctk.CTkLabel(
            info_box,
            text=(
                "Authentication verified successfully.\n\n"
                "User role selection (Patient / Community Health Worker / Clinician)\n"
                "will be implemented in the next step (Prompt 04)."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_BODY,
            justify="center",
            padx=15,
            pady=15,
        )
        info_text.pack()

        # Logout button
        btn_logout = ctk.CTkButton(
            inner,
            text="Logout",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color="transparent",
            text_color=theme.COLOR_PRIMARY,
            border_width=1,
            border_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_NOTICE_BG,
            width=140,
            height=36,
            command=self.on_logout,
        )
        btn_logout.pack()
