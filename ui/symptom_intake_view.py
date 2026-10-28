"""Symptom Intake Form and Triage Placeholder Views for SasthoSetu (Prompt 07).

This module contains:
- SymptomIntakeView: Collects free-text symptoms, duration, severity, and medical history.
- TriagePlaceholderView: Temporary placeholder confirming recorded assessment data.
"""

from typing import Any, Callable, Dict, Optional
import customtkinter as ctk
from core import constants, theme
from utils import validators

# Supported duration units and severity choices
DURATION_UNITS = ["Hours", "Days", "Weeks", "Months"]
SEVERITY_OPTIONS = ["Select Severity (Optional)", "Mild", "Moderate", "Severe", "Not sure"]


class SymptomIntakeView(ctk.CTkFrame):
    """Symptom Intake Form view for collecting patient complaints."""

    def __init__(
        self,
        master: Any,
        user_record: Dict[str, Any],
        patient_data: Dict[str, Any],
        initial_symptoms: Optional[Dict[str, Any]],
        on_continue: Callable[[Dict[str, Any]], None],
        on_back: Callable[..., None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.user_record = user_record
        self.patient_data = patient_data
        self.initial_symptoms = initial_symptoms or {}
        self.on_continue = on_continue
        self.on_back = on_back
        self._is_submitting = False

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the Symptom Intake interface."""
        # Top Navigation Bar
        self._build_top_bar()

        # Scrollable container for perfect responsiveness
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_container.pack(fill="both", expand=True, padx=25, pady=(0, 10))

        # Emergency Medical Warning
        self._build_emergency_warning()

        # Main Symptom Card
        self._build_form_card()

    def _build_top_bar(self) -> None:
        """Constructs the navigation header with patient summary."""
        bar = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            height=50,
        )
        bar.pack(fill="x", padx=25, pady=(12, 10))
        bar.pack_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=8)

        # Left: Breadcrumb & Patient Context
        p_name = self.patient_data.get("name", "Unknown")
        p_age = self.patient_data.get("age", "")
        p_gender = self.patient_data.get("gender", "")
        patient_summary = f"Patient: {p_name} ({p_age}y, {p_gender})"

        lbl_context = ctk.CTkLabel(
            inner,
            text=f"New Assessment  ➔  Symptom Information  |  {patient_summary}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        lbl_context.pack(side="left")

        # Right: Back button
        btn_back = ctk.CTkButton(
            inner,
            text="← Back to Patient Info",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_BODY,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=150,
            height=28,
            corner_radius=6,
            command=self._handle_back,
        )
        btn_back.pack(side="right")

    def _build_emergency_warning(self) -> None:
        """Constructs the mandatory emergency safety warning banner."""
        warning_frame = ctk.CTkFrame(
            self.scroll_container,
            fg_color=theme.COLOR_DANGER_BG,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER,
            corner_radius=8,
        )
        warning_frame.pack(fill="x", pady=(0, 15))

        inner = ctk.CTkFrame(warning_frame, fg_color="transparent")
        inner.pack(padx=18, pady=12, fill="x")

        lbl_warning = ctk.CTkLabel(
            inner,
            text=(
                "⚠️ Emergency Notice: If the patient is currently experiencing severe or life-threatening symptoms\n"
                "(such as sudden severe chest pain, extreme difficulty breathing, loss of consciousness, or heavy uncontrolled bleeding),\n"
                "seek immediate emergency medical assistance. Do not wait for this triage application to complete."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_DANGER_TEXT,
            justify="left",
            anchor="w",
        )
        lbl_warning.pack(fill="x")

    def _build_form_card(self) -> None:
        """Constructs the card containing all symptom inputs and validation alerts."""
        card = ctk.CTkFrame(
            self.scroll_container,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
        )
        card.pack(fill="x", pady=(0, 15))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=35, pady=25, fill="x")

        # Title & Subtitle
        title_lbl = ctk.CTkLabel(
            inner,
            text="Describe Your Symptoms",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        title_lbl.pack(fill="x", pady=(0, 4))

        subtitle_lbl = ctk.CTkLabel(
            inner,
            text="Please describe what the patient is experiencing, including how long they have had the symptoms.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        subtitle_lbl.pack(fill="x", pady=(0, 15))

        # Alert Banner (for validation errors)
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
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_DANGER_TEXT,
            padx=14,
            pady=8,
        )
        self.alert_label.pack(anchor="w")

        # --- Field 1: Symptoms / Main Complaint (Required Multiline) ---
        lbl_symptoms = ctk.CTkLabel(
            inner,
            text="Symptoms / Main Complaint *",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_symptoms.pack(fill="x", pady=(4, 2))

        self.txt_symptoms = ctk.CTkTextbox(
            inner,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_width=1,
            border_color=theme.COLOR_INPUT_BORDER,
            corner_radius=theme.CORNER_RADIUS_SM,
            height=130,
            wrap="word",
        )
        self.txt_symptoms.pack(fill="x", pady=(0, 4))
        if self.initial_symptoms.get("description"):
            self.txt_symptoms.insert("1.0", self.initial_symptoms["description"])

        symptom_hint = ctk.CTkLabel(
            inner,
            text="Supports English, Bangla (বাংলা), or Banglish (e.g. chest pain, শ্বাসকষ্ট, jor o matha betha). Max 1,500 characters.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        symptom_hint.pack(fill="x", pady=(0, 16))

        # --- Two-Column Row: Duration & Severity ---
        row_frame = ctk.CTkFrame(inner, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 16))
        row_frame.grid_columnconfigure((0, 1), weight=1, uniform="symptom_row")

        # Column 0: Symptom Duration (Optional)
        col_duration = ctk.CTkFrame(row_frame, fg_color="transparent")
        col_duration.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        lbl_duration = ctk.CTkLabel(
            col_duration,
            text="Duration (Optional)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_duration.pack(fill="x", pady=(0, 2))

        duration_inputs = ctk.CTkFrame(col_duration, fg_color="transparent")
        duration_inputs.pack(fill="x", pady=(0, 2))

        self.entry_duration_val = ctk.CTkEntry(
            duration_inputs,
            placeholder_text="e.g. 2",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=36,
            width=90,
            corner_radius=6,
        )
        self.entry_duration_val.pack(side="left", padx=(0, 8))
        if self.initial_symptoms.get("duration_value"):
            self.entry_duration_val.insert(0, str(self.initial_symptoms["duration_value"]))

        self.combo_duration_unit = ctk.CTkComboBox(
            duration_inputs,
            values=DURATION_UNITS,
            state="readonly",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            dropdown_font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=36,
            corner_radius=6,
        )
        self.combo_duration_unit.pack(side="left", fill="x", expand=True)
        init_unit = self.initial_symptoms.get("duration_unit", "Days")
        if init_unit in DURATION_UNITS:
            self.combo_duration_unit.set(init_unit)
        else:
            self.combo_duration_unit.set("Days")

        dur_hint = ctk.CTkLabel(
            col_duration,
            text="How long symptoms have lasted (leave empty if unknown).",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        dur_hint.pack(fill="x")

        # Column 1: Current Symptom Severity (Optional)
        col_severity = ctk.CTkFrame(row_frame, fg_color="transparent")
        col_severity.grid(row=0, column=1, padx=(12, 0), sticky="nsew")

        lbl_severity = ctk.CTkLabel(
            col_severity,
            text="Reported Severity (Optional)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_severity.pack(fill="x", pady=(0, 2))

        self.combo_severity = ctk.CTkComboBox(
            col_severity,
            values=SEVERITY_OPTIONS,
            state="readonly",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            dropdown_font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=36,
            corner_radius=6,
        )
        self.combo_severity.pack(fill="x", pady=(0, 2))
        init_sev = self.initial_symptoms.get("severity")
        if init_sev and init_sev in SEVERITY_OPTIONS:
            self.combo_severity.set(init_sev)
        else:
            self.combo_severity.set(SEVERITY_OPTIONS[0])

        sev_hint = ctk.CTkLabel(
            col_severity,
            text="Patient-reported subjective feeling.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        sev_hint.pack(fill="x")

        # --- Field 3: Additional Information (Optional Multiline) ---
        lbl_additional = ctk.CTkLabel(
            inner,
            text="Additional Information (Optional)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_additional.pack(fill="x", pady=(4, 2))

        self.txt_additional = ctk.CTkTextbox(
            inner,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_width=1,
            border_color=theme.COLOR_INPUT_BORDER,
            corner_radius=6,
            height=75,
            wrap="word",
        )
        self.txt_additional.pack(fill="x", pady=(0, 4))
        if self.initial_symptoms.get("additional_info"):
            self.txt_additional.insert("1.0", self.initial_symptoms["additional_info"])

        add_hint = ctk.CTkLabel(
            inner,
            text="Relevant medical history, current medications, chronic conditions, pregnancy, or recent injury.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        add_hint.pack(fill="x", pady=(0, 22))

        # --- Action Buttons ---
        btn_container = ctk.CTkFrame(inner, fg_color="transparent")
        btn_container.pack(fill="x")

        self.btn_continue = ctk.CTkButton(
            btn_container,
            text="Run Triage Assessment ➔",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=14, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=210,
            height=theme.BTN_HEIGHT_LG,
            corner_radius=theme.CORNER_RADIUS_MD,
            command=self._handle_continue,
        )
        self.btn_continue.pack(side="left", padx=(0, 10))

        self.btn_back = ctk.CTkButton(
            btn_container,
            text="Back",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_BODY,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=100,
            height=40,
            corner_radius=6,
            command=self._handle_back,
        )
        self.btn_back.pack(side="left")

    def _handle_back(self) -> None:
        """Captures in-progress symptom entries before navigating back to Patient Info."""
        symptoms = self.txt_symptoms.get("1.0", "end-1c").strip()
        dur_val_str = self.entry_duration_val.get().strip()
        dur_unit = self.combo_duration_unit.get().strip()
        severity = self.combo_severity.get().strip()
        additional_info = self.txt_additional.get("1.0", "end-1c").strip()

        partial_data = None
        if symptoms or dur_val_str or additional_info:
            try:
                val = float(dur_val_str) if dur_val_str else None
            except ValueError:
                val = None
            partial_data = {
                "description": symptoms,
                "duration_value": val,
                "duration_unit": dur_unit,
                "severity": severity,
                "additional_info": additional_info,
            }

        try:
            self.on_back(partial_data)
        except TypeError:
            self.on_back()

    def _show_alert(self, message: str) -> None:
        """Displays error validation banner."""
        self.alert_label.configure(text=f"⚠️ {message}")
        self.alert_frame.pack(fill="x", pady=(0, 14), before=self.txt_symptoms)

    def _hide_alert(self) -> None:
        """Hides error validation banner."""
        self.alert_frame.pack_forget()

    def _handle_continue(self) -> None:
        """Validates all symptom inputs according to Prompt 07 & Prompt 16 specifications."""
        if getattr(self, "_is_submitting", False):
            return

        self._hide_alert()

        symptoms = self.txt_symptoms.get("1.0", "end-1c").strip()
        dur_val_str = self.entry_duration_val.get().strip()
        dur_unit = self.combo_duration_unit.get().strip()
        severity = self.combo_severity.get().strip()
        additional_info = self.txt_additional.get("1.0", "end-1c").strip()

        # 1. Validate Symptoms / Main Complaint (Required & max length limit)
        is_valid_sym, sym_err = validators.validate_symptoms(
            symptoms, max_length=constants.MAX_SYMPTOM_LENGTH
        )
        if not is_valid_sym:
            self._show_alert(sym_err)
            return

        # 2. Validate Duration (Optional, but if given must be valid positive number)
        is_valid_dur, dur_err, parsed_duration_val, parsed_duration_unit = validators.validate_duration(
            dur_val_str, dur_unit
        )
        if not is_valid_dur:
            self._show_alert(dur_err)
            return

        # 3. Validate Additional Info length if present
        if additional_info and len(additional_info) > constants.MAX_ADDITIONAL_INFO_LENGTH:
            self._show_alert(
                f"Additional information exceeds the maximum allowed length of {constants.MAX_ADDITIONAL_INFO_LENGTH} characters."
            )
            return

        # 4. Clean Severity
        clean_severity = severity if severity != SEVERITY_OPTIONS[0] else "Not specified"

        # 5. Construct Symptom Data Structure
        symptom_data: Dict[str, Any] = {
            "description": symptoms,
            "duration_value": parsed_duration_val,
            "duration_unit": parsed_duration_unit,
            "severity": clean_severity,
            "additional_info": additional_info if additional_info else "None reported",
        }

        # Prevent duplicate submissions from multiple quick clicks
        self._is_submitting = True
        self.btn_continue.configure(state="disabled", text="⏳ Assessing symptoms... Please wait.")

        try:
            self.on_continue(symptom_data)
        except Exception:
            self._is_submitting = False
            self.btn_continue.configure(state="normal", text="Run Triage Assessment ➔")


class TriagePlaceholderView(ctk.CTkFrame):
    """Temporary placeholder view after recording symptoms (Prompt 07).

    Confirms that patient information and symptom information are saved
    in the temporary session state and ready for Rule-Based Triage in Prompt 08.
    """

    def __init__(
        self,
        master: Any,
        assessment_data: Dict[str, Any],
        on_edit_symptoms: Callable[[], None],
        on_new_assessment: Callable[[], None],
        on_back_to_home: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.assessment_data = assessment_data
        self.on_edit_symptoms = on_edit_symptoms
        self.on_new_assessment = on_new_assessment
        self.on_back_to_home = on_back_to_home

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the triage placeholder confirmation interface with Prompt 10 safety-net feedback."""
        triage = self.assessment_data.get("triage", {})
        is_urgent = (triage.get("urgency") == constants.TIER_URGENT) or triage.get("matched", False)

        card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER if is_urgent else theme.COLOR_CARD_BORDER,
            width=720,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=35, pady=25, fill="both")

        # 1. Status / Safety-Net Badge
        if is_urgent:
            badge_text = "🔴 URGENT — Potential Emergency Detected"
            badge_fg = theme.COLOR_DANGER_BG
            badge_color = theme.COLOR_DANGER_TEXT
            title_text = "Emergency Warning Detected"
            desc_text = "Potential emergency warning detected. The case has been marked URGENT for clinician review."
            desc_color = theme.COLOR_DANGER_TEXT
        else:
            badge_text = "✓ Assessment Saved — Contextual Review Pending"
            badge_fg = theme.COLOR_NOTICE_BG
            badge_color = theme.COLOR_NOTICE_TEXT
            title_text = "Assessment Recorded in Queue"
            desc_text = "No immediate rule-based emergency warning was detected. Further contextual triage is required."
            desc_color = theme.COLOR_TEXT_BODY

        badge = ctk.CTkLabel(
            inner,
            text=badge_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=badge_color,
            fg_color=badge_fg,
            corner_radius=6,
            padx=14,
            pady=5,
        )
        badge.pack(pady=(0, 10))

        # 2. Title & Safety-Net State Description
        title_lbl = ctk.CTkLabel(
            inner,
            text=title_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        title_lbl.pack(pady=(0, 6))

        desc_lbl = ctk.CTkLabel(
            inner,
            text=desc_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold" if is_urgent else "normal"),
            text_color=desc_color,
            justify="center",
            wraplength=640,
        )
        desc_lbl.pack(pady=(0, 16))

        # 3. Assessment Summary Box (Patient + Symptoms + Safety-Net Evaluation)
        summary_frame = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_BG_MAIN,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        summary_frame.pack(fill="x", pady=(0, 16))

        sum_inner = ctk.CTkFrame(summary_frame, fg_color="transparent")
        sum_inner.pack(padx=18, pady=14, fill="x")

        assessment_id = self.assessment_data.get("assessment_id")
        status = self.assessment_data.get("status", "Waiting")
        if assessment_id:
            self._add_row(sum_inner, "Database Record", f"Assessment #{assessment_id}  |  Queue Status: {status}")

        # Urgency Tier & Safety-Net Reason rows
        if is_urgent:
            self._add_row(sum_inner, "Triage Urgency", "🔴 URGENT (Immediate Clinician Attention Required)")
            self._add_row(sum_inner, "Safety Reason", triage.get("reason", "Emergency red flag reported."))
            if triage.get("advice"):
                self._add_row(sum_inner, "Immediate Guidance", triage["advice"])
        else:
            self._add_row(sum_inner, "Triage Urgency", "Pending Contextual Triage (Awaiting AI/Clinician Review)")
            self._add_row(sum_inner, "Safety-Net Check", "No immediate rule-based emergency red flags detected.")

        patient = self.assessment_data.get("patient", {})
        symptoms = self.assessment_data.get("symptoms", {})

        p_name = patient.get("name", "N/A")
        p_demo = f"{patient.get('age', 'N/A')} yrs, {patient.get('gender', 'N/A')}"
        p_loc = patient.get("location", "N/A")

        self._add_row(sum_inner, "Patient", f"{p_name} ({p_demo}) - {p_loc}")
        self._add_row(sum_inner, "Reported Symptoms", symptoms.get("description", "N/A"))

        # Duration format
        dur_val = symptoms.get("duration_value")
        dur_unit = symptoms.get("duration_unit")
        dur_display = f"{dur_val} {dur_unit}" if dur_val else "Not specified"
        self._add_row(sum_inner, "Duration", dur_display)

        self._add_row(sum_inner, "Severity", symptoms.get("severity", "Not specified"))
        if symptoms.get("additional_info"):
            self._add_row(sum_inner, "Additional Info", symptoms.get("additional_info"))

        # 4. Mandatory Medical Safety Disclaimer (Prompt 10 Section 17)
        disclaimer_box = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_DANGER_BG if is_urgent else theme.COLOR_NOTICE_BG,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER if is_urgent else theme.COLOR_NOTICE_BORDER,
            corner_radius=6,
        )
        disclaimer_box.pack(fill="x", pady=(0, 18))

        if is_urgent:
            disclaimer_msg = (
                "⚠️ Safety-Net Alert: This is a safety-net alert, not a medical diagnosis.\n"
                "Seek immediate professional medical attention for serious symptoms."
            )
            disclaimer_txt_color = theme.COLOR_DANGER_TEXT
        else:
            disclaimer_msg = (
                "ℹ️ SasthoSetu Triage Notice: Decision-support prioritization only, not a clinical diagnosis.\n"
                "The attending clinician retains final authority on patient queueing and care decisions."
            )
            disclaimer_txt_color = theme.COLOR_NOTICE_TEXT

        ctk.CTkLabel(
            disclaimer_box,
            text=disclaimer_msg,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11, weight="bold" if is_urgent else "normal"),
            text_color=disclaimer_txt_color,
            justify="center",
        ).pack(padx=12, pady=8)

        # Action Buttons
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack()

        btn_edit = ctk.CTkButton(
            btn_frame,
            text="← Edit Symptoms",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=140,
            height=36,
            corner_radius=6,
            command=self.on_edit_symptoms,
        )
        btn_edit.pack(side="left", padx=6)

        btn_new = ctk.CTkButton(
            btn_frame,
            text="New Assessment",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color="transparent",
            text_color=theme.COLOR_PRIMARY,
            border_width=1,
            border_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_NOTICE_BG,
            width=140,
            height=36,
            corner_radius=6,
            command=self.on_new_assessment,
        )
        btn_new.pack(side="left", padx=6)

        btn_home = ctk.CTkButton(
            btn_frame,
            text="Back to Home",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_BODY,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=120,
            height=36,
            corner_radius=6,
            command=self.on_back_to_home,
        )
        btn_home.pack(side="left", padx=6)

    def _add_row(self, parent: Any, label: str, value: str) -> None:
        """Helper to render a key-value row in the assessment summary."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)

        lbl = ctk.CTkLabel(
            row,
            text=f"{label}:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED,
            width=135,
            anchor="w",
        )
        lbl.pack(side="left", anchor="n")

        val = ctk.CTkLabel(
            row,
            text=value,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
            wraplength=460,
            justify="left",
        )
        val.pack(side="left", fill="x", expand=True)
