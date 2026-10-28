"""SasthoSetu - Main Application Window & Navigation Controller (Prompt 08).

This module manages the single application window and coordinates
clean frame switching between all pages (Welcome, Login, Register,
Role Selection, Patient Home, Patient Info, Symptom Intake, and
Clinician Portal) with authentication and role-based safeguards.
"""

import json
import threading
from typing import Any, Dict, Optional
import customtkinter as ctk
from core import constants, theme, triage_engine
from database import db
from ui.auth_view import LoginView, RegisterView
from ui.dashboard_view import ClinicianDashboardView
from ui.patient_home_view import PatientHomeView
from ui.patient_info_view import PatientInfoView
from ui.role_view import (
    ClinicianPlaceholderView,
    PatientPlaceholderView,
    RoleSelectionView,
)
from ui.symptom_intake_view import SymptomIntakeView, TriagePlaceholderView
from ui.triage_result_view import TriageResultView
from utils.logger import get_logger

log = get_logger("ui.app")


class SasthoSetuApp(ctk.CTk):
    """Main desktop application window and navigation controller."""

    def __init__(self) -> None:
        super().__init__()

        # --- 1. Central Session & Assessment State ---
        self.current_user: Optional[Dict[str, Any]] = None
        self.current_user_role: Optional[str] = None
        self.current_patient_id: Optional[int] = None
        self.current_assessment_id: Optional[int] = None
        self.current_patient_data: Optional[Dict[str, Any]] = None
        self.current_symptom_data: Optional[Dict[str, Any]] = None
        self.current_assessment_data: Optional[Dict[str, Any]] = None
        self.current_triage_output: Optional[Dict[str, Any]] = None
        self.current_page: str = constants.PAGE_WELCOME

        # --- 2. Window Configuration ---
        self.title("SasthoSetu - AI-Assisted Triage System")
        self._center_window(width=1000, height=650)
        self.configure(fg_color=theme.COLOR_BG_MAIN)

        # --- 3. Persistent Shell Elements (Header & Footer) ---
        self._create_header()
        self._create_footer()

        # --- 4. Dynamic Main Content Container ---
        # Single frame where all pages are mounted and unmounted
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # Start on the Welcome Screen
        self.show_page(constants.PAGE_WELCOME)

    def _center_window(self, width: int = 1000, height: int = 650) -> None:
        """Centers the desktop window on the user's screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(850, 550)

    def _clear_main_container(self) -> None:
        """Removes all widgets currently in the main content container."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def _create_header(self) -> None:
        """Creates the persistent top header bar with branding."""
        header_frame = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=0,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            height=65,
        )
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        inner_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        inner_header.pack(fill="both", expand=True, padx=30, pady=10)

        # Left branding: Application Title & Subtitle
        title_label = ctk.CTkLabel(
            inner_header,
            text="SasthoSetu (স্বাস্থ্যসেতু)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=theme.COLOR_PRIMARY,
            anchor="w",
        )
        title_label.pack(side="left")

        subtitle_separator = ctk.CTkLabel(
            inner_header,
            text=" | ",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=16),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        subtitle_separator.pack(side="left", padx=4)

        subtitle_label = ctk.CTkLabel(
            inner_header,
            text="AI-Assisted Triage System",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=14),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        subtitle_label.pack(side="left")

        # Right side: Prototype stage badge
        badge = ctk.CTkLabel(
            inner_header,
            text=constants.APP_VERSION,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_PRIMARY,
            fg_color=theme.COLOR_NOTICE_BG,
            corner_radius=6,
            padx=10,
            pady=4,
        )
        badge.pack(side="right")

    def _create_footer(self) -> None:
        """Creates the persistent bottom footer displaying medical disclaimers."""
        footer_frame = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=0,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            height=40,
        )
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)

        disclaimer_label = ctk.CTkLabel(
            footer_frame,
            text=(
                "Disclaimer: SasthoSetu is a decision-support prototype and does not provide "
                "medical diagnosis or prescriptions. Final clinical decisions belong to the clinician."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_DISCLAIMER,
        )
        disclaimer_label.pack(pady=8)

    # =========================================================================
    # Central Navigation Controller (Prompt 08)
    # =========================================================================

    def show_page(self, page_name: str, **kwargs: Any) -> None:
        """Navigates to the specified page within the single main window.

        Applies simple safeguards for authentication, role boundaries,
        and step progression.
        """
        # --- Safeguard 1: Authentication Check ---
        authenticated_pages = {
            constants.PAGE_ROLE_SELECTION,
            constants.PAGE_PATIENT_HOME,
            constants.PAGE_PATIENT_INFO,
            constants.PAGE_SYMPTOM_INTAKE,
            constants.PAGE_TRIAGE_RESULT,
            constants.PAGE_TRIAGE_PLACEHOLDER,
            constants.PAGE_CLINICIAN_DASHBOARD,
            constants.PAGE_CLINICIAN_PLACEHOLDER,
        }
        if page_name in authenticated_pages and not self.current_user:
            self._mount_login_view(
                initial_message="Please log in to continue.", is_error=True
            )
            return

        # --- Safeguard 2: Role Authorization Boundaries ---
        patient_pages = {
            constants.PAGE_PATIENT_HOME,
            constants.PAGE_PATIENT_INFO,
            constants.PAGE_SYMPTOM_INTAKE,
            constants.PAGE_TRIAGE_RESULT,
            constants.PAGE_TRIAGE_PLACEHOLDER,
        }
        clinician_pages = {
            constants.PAGE_CLINICIAN_DASHBOARD,
            constants.PAGE_CLINICIAN_PLACEHOLDER,
        }

        if page_name in patient_pages:
            if self.current_user_role != constants.ROLE_PATIENT_HEALTH_WORKER:
                if self.current_user_role == constants.ROLE_CLINICIAN:
                    self.show_page(constants.PAGE_CLINICIAN_DASHBOARD)
                else:
                    self.show_page(constants.PAGE_ROLE_SELECTION)
                return

        if page_name in clinician_pages:
            if self.current_user_role != constants.ROLE_CLINICIAN:
                # Patient account attempting to access clinician dashboard (Prompt 13 Section 16)
                if self.current_user_role == constants.ROLE_PATIENT_HEALTH_WORKER:
                    self.show_page(
                        constants.PAGE_PATIENT_HOME,
                        initial_error="Access denied. Clinician access is required.",
                    )
                else:
                    self.show_page(constants.PAGE_ROLE_SELECTION)
                return

        # --- Safeguard 3: Sequential Assessment Progression ---
        if page_name == constants.PAGE_SYMPTOM_INTAKE and not self.current_patient_data:
            # Cannot jump to symptom intake without patient info
            page_name = constants.PAGE_PATIENT_INFO

        if page_name in (constants.PAGE_TRIAGE_RESULT, constants.PAGE_TRIAGE_PLACEHOLDER) and not self.current_assessment_data:
            page_name = constants.PAGE_PATIENT_HOME

        # --- Mount Destination Page ---
        self._clear_main_container()
        self.current_page = page_name

        try:
            if page_name == constants.PAGE_WELCOME:
                self._mount_welcome_view()
            elif page_name == constants.PAGE_LOGIN:
                self._mount_login_view(
                    initial_message=kwargs.get("initial_message"),
                    is_error=kwargs.get("is_error", False),
                )
            elif page_name == constants.PAGE_REGISTER:
                self._mount_register_view()
            elif page_name == constants.PAGE_ROLE_SELECTION:
                self._mount_role_selection_view()
            elif page_name == constants.PAGE_PATIENT_HOME:
                self._mount_patient_home_view(initial_error=kwargs.get("initial_error"))
            elif page_name == constants.PAGE_PATIENT_INFO:
                self._mount_patient_info_view()
            elif page_name == constants.PAGE_SYMPTOM_INTAKE:
                self._mount_symptom_intake_view()
            elif page_name in (constants.PAGE_TRIAGE_RESULT, constants.PAGE_TRIAGE_PLACEHOLDER):
                self._mount_triage_result_view()
            elif page_name in (constants.PAGE_CLINICIAN_DASHBOARD, constants.PAGE_CLINICIAN_PLACEHOLDER):
                self._mount_clinician_dashboard_view()
        except Exception as err:
            log.error(f"Navigation error mounting view '{page_name}': {err}")
            self._mount_navigation_error_view(page_name, str(err))

    # =========================================================================
    # Internal View Mounting Helpers
    # =========================================================================

    def _mount_navigation_error_view(self, page_name: str, error_detail: str) -> None:
        """Renders a graceful error recovery view when a page fails to mount."""
        self._clear_main_container()

        card = ctk.CTkFrame(
            self.main_container,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            width=550,
            height=320,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=35, pady=30, fill="both", expand=True)

        ctk.CTkLabel(
            inner,
            text="⚠️ View Loading Error",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=theme.COLOR_DANGER_TEXT,
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            inner,
            text=(
                f"We encountered an issue while loading '{page_name}'.\n"
                "Your previous data has been preserved. Please return to the Home page or try again."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_BODY,
            justify="left",
            wraplength=460,
        ).pack(fill="x", pady=(0, 20))

        btn_box = ctk.CTkFrame(inner, fg_color="transparent")
        btn_box.pack(fill="x")

        target_home = (
            constants.PAGE_CLINICIAN_DASHBOARD
            if self.current_user_role == constants.ROLE_CLINICIAN
            else (constants.PAGE_PATIENT_HOME if self.current_user else constants.PAGE_WELCOME)
        )

        ctk.CTkButton(
            btn_box,
            text="Return to Home",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=140,
            height=36,
            corner_radius=6,
            command=lambda: self.show_page(target_home),
        ).pack(side="left")

    def _mount_welcome_view(self) -> None:
        """Mounts the Welcome / Landing view."""
        card = ctk.CTkFrame(
            self.main_container,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.80)

        card_content = ctk.CTkFrame(card, fg_color="transparent")
        card_content.pack(fill="both", expand=True, padx=40, pady=35)

        welcome_title = ctk.CTkLabel(
            card_content,
            text="Welcome to SasthoSetu",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=26, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        welcome_title.pack(pady=(10, 8))

        purpose_label = ctk.CTkLabel(
            card_content,
            text="Helping prioritize patients based on reported symptoms and urgency.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=16),
            text_color=theme.COLOR_PRIMARY_HOVER,
        )
        purpose_label.pack(pady=(0, 14))

        desc_label = ctk.CTkLabel(
            card_content,
            text=(
                "SasthoSetu is designed for rural telemedicine centers in Bangladesh.\n"
                "It combines a deterministic safety-net with AI-assisted contextual triage\n"
                "to ensure high-urgency cases receive timely clinical attention."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_BODY,
            justify="center",
        )
        desc_label.pack(pady=(0, 25))

        btn_get_started = ctk.CTkButton(
            card_content,
            text="Get Started",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=15, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            corner_radius=8,
            width=200,
            height=42,
            command=lambda: self.show_page(constants.PAGE_LOGIN),
        )
        btn_get_started.pack(pady=(0, 15))

    def _mount_login_view(
        self, initial_message: Optional[str] = None, is_error: bool = False
    ) -> None:
        """Mounts the Login view."""
        login_view = LoginView(
            master=self.main_container,
            on_login_success=self._on_login_success,
            on_switch_to_register=lambda: self.show_page(constants.PAGE_REGISTER),
            on_back_to_welcome=lambda: self.show_page(constants.PAGE_WELCOME),
        )
        login_view.pack(fill="both", expand=True)

        if initial_message:
            login_view._show_alert(initial_message, is_error=is_error)

    def _on_login_success(self, user_record: Dict[str, Any]) -> None:
        """Handles successful authentication: stores user and opens role selection."""
        self.current_user = user_record
        self.current_user_role = None
        self.show_page(constants.PAGE_ROLE_SELECTION)

    def _mount_register_view(self) -> None:
        """Mounts the Register view."""
        register_view = RegisterView(
            master=self.main_container,
            on_register_success=self._on_register_success,
            on_switch_to_login=lambda: self.show_page(constants.PAGE_LOGIN),
        )
        register_view.pack(fill="both", expand=True)

    def _on_register_success(self, username: str) -> None:
        """Handles successful account creation: redirects to login with notice."""
        self.show_page(
            constants.PAGE_LOGIN,
            initial_message="✓ Account created successfully! Please log in.",
            is_error=False,
        )

    def _mount_role_selection_view(self) -> None:
        """Mounts the Role Selection view."""
        role_view = RoleSelectionView(
            master=self.main_container,
            user_record=self.current_user or {},
            on_select_role=self.select_role,
            on_logout=self.logout,
        )
        role_view.pack(fill="both", expand=True)

    def select_role(self, role_key: str) -> None:
        """Stores the active role in session and routes to the appropriate portal."""
        self.current_user_role = role_key

        if role_key == constants.ROLE_PATIENT_HEALTH_WORKER:
            self.show_page(constants.PAGE_PATIENT_HOME)
        elif role_key == constants.ROLE_CLINICIAN:
            self.show_page(constants.PAGE_CLINICIAN_DASHBOARD)

    def _mount_patient_home_view(self, initial_error: Optional[str] = None) -> None:
        """Mounts the Patient / Health Worker Home Page."""
        home_view = PatientHomeView(
            master=self.main_container,
            user_record=self.current_user or {},
            on_start_assessment=self.start_new_assessment,
            on_switch_role=lambda: self.show_page(constants.PAGE_ROLE_SELECTION),
            on_logout=self.logout,
            access_error=initial_error,
        )
        home_view.pack(fill="both", expand=True)

    def _mount_patient_info_view(self) -> None:
        """Mounts the Patient Information Form, preserving any previous inputs."""
        info_view = PatientInfoView(
            master=self.main_container,
            user_record=self.current_user or {},
            initial_data=self.current_patient_data,
            on_continue=self._on_patient_info_submitted,
            on_back=lambda: self.show_page(constants.PAGE_PATIENT_HOME),
        )
        info_view.pack(fill="both", expand=True)

    def _on_patient_info_submitted(self, patient_data: Dict[str, Any]) -> None:
        """Stores validated patient info in session and advances to symptom intake."""
        self.current_patient_data = patient_data
        self.show_page(constants.PAGE_SYMPTOM_INTAKE)

    def _mount_symptom_intake_view(self) -> None:
        """Mounts the Symptom Intake Form, preserving any previous inputs."""
        symptom_view = SymptomIntakeView(
            master=self.main_container,
            user_record=self.current_user or {},
            patient_data=self.current_patient_data or {},
            initial_symptoms=self.current_symptom_data,
            on_continue=self._on_symptoms_submitted,
            on_back=self._on_symptom_intake_back,
        )
        symptom_view.pack(fill="both", expand=True)

    def _on_symptom_intake_back(
        self, partial_symptoms: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handles back from symptom intake, preserving in-progress symptom entries."""
        if partial_symptoms:
            self.current_symptom_data = partial_symptoms
        self.show_page(constants.PAGE_PATIENT_INFO)

    def _on_symptoms_submitted(self, symptom_data: Dict[str, Any]) -> None:
        """Evaluates symptoms asynchronously via hybrid triage engine and saves to SQLite."""
        self.current_symptom_data = symptom_data

        def worker() -> None:
            try:
                triage_output = triage_engine.run_triage(
                    symptoms=symptom_data["description"],
                    reported_severity=symptom_data.get("severity"),
                    duration_val=symptom_data.get("duration_value"),
                    duration_unit=symptom_data.get("duration_unit"),
                    additional_info=symptom_data.get("additional_info"),
                    patient_data=self.current_patient_data,
                )
            except Exception as exc:
                triage_output = {
                    "urgency": constants.TIER_URGENT,
                    "reason": "An unexpected error occurred during symptom triage. Case escalated for urgent clinician review.",
                    "advice": "Seek immediate professional medical attention.",
                    "source": constants.SOURCE_FALLBACK,
                    "safety_rule_matched": False,
                    "is_safety_net_override": False,
                    "status": constants.STATUS_WAITING,
                }

            # Return execution safely to CustomTkinter main loop
            self.after(0, lambda: self._finalize_symptom_submission(symptom_data, triage_output))

        threading.Thread(target=worker, daemon=True).start()

    def _finalize_symptom_submission(
        self, symptom_data: Dict[str, Any], triage_output: Dict[str, Any]
    ) -> None:
        """Persists triage results to SQLite and transitions to the Triage Result view."""
        self.current_triage_output = triage_output

        # 1. Insert patient record into SQLite (if not already created for this session)
        try:
            if not self.current_patient_id and self.current_patient_data:
                self.current_patient_id = db.create_patient(
                    name=self.current_patient_data["name"],
                    age=self.current_patient_data["age"],
                    gender=self.current_patient_data["gender"],
                    location=self.current_patient_data["location"],
                    phone=self.current_patient_data.get("phone"),
                )

            # 2. Insert or update triage record in SQLite (linked to patient_id)
            if self.current_patient_id:
                matched_rules_json = json.dumps(triage_output.get("matched_rules", []))
                triage_source = triage_output.get("source", constants.SOURCE_GEMINI)

                if self.current_assessment_id:
                    # Update existing record if user went back to edit symptoms and re-submitted
                    db.update_triage_record(
                        record_id=self.current_assessment_id,
                        symptoms=symptom_data["description"],
                        symptom_duration=symptom_data.get("duration_value"),
                        duration_unit=symptom_data.get("duration_unit"),
                        reported_severity=symptom_data.get("severity"),
                        additional_information=symptom_data.get("additional_info"),
                        urgency_level=triage_output.get("urgency"),
                        triage_reason=triage_output.get("reason"),
                        triage_advice=triage_output.get("advice"),
                        matched_rules=matched_rules_json,
                        triage_source=triage_source,
                        status=triage_output.get("status", "Waiting"),
                    )
                else:
                    self.current_assessment_id = db.create_triage_record(
                        patient_id=self.current_patient_id,
                        symptoms=symptom_data["description"],
                        symptom_duration=symptom_data.get("duration_value"),
                        duration_unit=symptom_data.get("duration_unit"),
                        reported_severity=symptom_data.get("severity"),
                        additional_information=symptom_data.get("additional_info"),
                        urgency_level=triage_output.get("urgency"),
                        triage_reason=triage_output.get("reason"),
                        triage_advice=triage_output.get("advice"),
                        matched_rules=matched_rules_json,
                        triage_source=triage_source,
                        status=triage_output.get("status", "Waiting"),
                    )
        except Exception as db_err:
            log.error(f"Error persisting triage assessment to SQLite: {db_err}")

        # 3. Assemble combined session data with database IDs and triage evaluation
        self.current_assessment_data = {
            "assessment_id": self.current_assessment_id,
            "patient_id": self.current_patient_id,
            "patient": self.current_patient_data,
            "symptoms": self.current_symptom_data,
            "triage": triage_output,
            "status": triage_output.get("status", "Waiting"),
        }
        self.show_page(constants.PAGE_TRIAGE_RESULT)

    def _mount_triage_result_view(self) -> None:
        """Mounts the dedicated Triage Assessment Result view (Prompt 11)."""
        result_view = TriageResultView(
            master=self.main_container,
            assessment_data=self.current_assessment_data or {},
            on_back_to_symptoms=lambda: self.show_page(constants.PAGE_SYMPTOM_INTAKE),
            on_finish_assessment=lambda: self.show_page(constants.PAGE_PATIENT_HOME),
            on_start_new_assessment=self.start_new_assessment,
        )
        result_view.pack(fill="both", expand=True)

    def _mount_triage_placeholder_view(self) -> None:
        """Legacy alias redirecting to dedicated TriageResultView."""
        self._mount_triage_result_view()

    def _mount_clinician_dashboard_view(self) -> None:
        """Mounts the main Clinician Dashboard view (Prompt 13)."""
        dashboard_view = ClinicianDashboardView(
            master=self.main_container,
            user_record=self.current_user or {},
            on_switch_role=lambda: self.show_page(constants.PAGE_ROLE_SELECTION),
            on_logout=self.logout,
        )
        dashboard_view.pack(fill="both", expand=True)

    def _mount_clinician_placeholder_view(self) -> None:
        """Legacy alias redirecting to dedicated ClinicianDashboardView."""
        self._mount_clinician_dashboard_view()

    def start_new_assessment(self) -> None:
        """Clears previous assessment data and opens a clean Patient Info Form."""
        self.current_patient_id = None
        self.current_assessment_id = None
        self.current_patient_data = None
        self.current_symptom_data = None
        self.current_assessment_data = None
        self.current_triage_output = None
        self.show_page(constants.PAGE_PATIENT_INFO)

    def logout(self) -> None:
        """Safely logs out the user, resets all session and assessment state, and returns to Login."""
        self.current_user = None
        self.current_user_role = None
        self.current_patient_id = None
        self.current_assessment_id = None
        self.current_patient_data = None
        self.current_symptom_data = None
        self.current_assessment_data = None
        self.current_triage_output = None
        self.show_page(
            constants.PAGE_LOGIN,
            initial_message="Logged out successfully.",
            is_error=False,
        )

    # =========================================================================
    # Explicit Navigation Aliases (for backward compatibility & readability)
    # =========================================================================

    def show_welcome_view(self) -> None:
        self.show_page(constants.PAGE_WELCOME)

    def show_login_view(
        self, initial_message: Optional[str] = None, is_error: bool = False
    ) -> None:
        self.show_page(constants.PAGE_LOGIN, initial_message=initial_message, is_error=is_error)

    def show_register_view(self) -> None:
        self.show_page(constants.PAGE_REGISTER)

    def show_role_selection_view(self, user_record: Dict[str, Any]) -> None:
        self.current_user = user_record
        self.show_page(constants.PAGE_ROLE_SELECTION)

    def show_patient_home_view(self) -> None:
        self.show_page(constants.PAGE_PATIENT_HOME)

    def show_patient_info_view(self) -> None:
        self.show_page(constants.PAGE_PATIENT_INFO)

    def show_symptom_intake_view(self) -> None:
        self.show_page(constants.PAGE_SYMPTOM_INTAKE)

    def show_triage_result_view(self) -> None:
        self.show_page(constants.PAGE_TRIAGE_RESULT)

    def show_triage_placeholder(self) -> None:
        self.show_page(constants.PAGE_TRIAGE_RESULT)

    def show_clinician_dashboard(self) -> None:
        self.show_page(constants.PAGE_CLINICIAN_DASHBOARD)

    def show_clinician_dashboard_placeholder(self) -> None:
        self.show_page(constants.PAGE_CLINICIAN_DASHBOARD)
