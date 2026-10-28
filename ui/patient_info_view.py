"""Patient Information Form and Symptom Intake Placeholder Views for SasthoSetu (Prompt 06).

This module contains:
- PatientInfoView: Form for collecting patient demographics (Name, Age, Gender, Location, Phone).
- SymptomPlaceholderView: Temporary placeholder confirming saved patient information.
"""

from typing import Any, Callable, Dict, Optional
import customtkinter as ctk
from core import theme
from utils import validators

# Supported sex / gender options
GENDER_OPTIONS = ["Select Gender", "Male", "Female", "Other", "Prefer not to say"]


class PatientInfoView(ctk.CTkFrame):
    """Patient Information Form view."""

    def __init__(
        self,
        master: Any,
        user_record: Dict[str, Any],
        initial_data: Optional[Dict[str, Any]],
        on_continue: Callable[[Dict[str, Any]], None],
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.user_record = user_record
        self.initial_data = initial_data or {}
        self.on_continue = on_continue
        self.on_back = on_back

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the Patient Information layout."""
        # Top Sub-Navbar with Back button
        self._build_top_bar()

        # Scrollable container to maintain responsiveness across all screen sizes
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_container.pack(fill="both", expand=True, padx=25, pady=(0, 10))

        # Main Form Card
        self._build_form_card()

    def _build_top_bar(self) -> None:
        """Constructs the navigation header."""
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

        # Left: Breadcrumb
        lbl_breadcrumb = ctk.CTkLabel(
            inner,
            text="Patient Portal  ➔  New Assessment  ➔  Patient Information",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        lbl_breadcrumb.pack(side="left")

        # Right: Back button
        btn_back = ctk.CTkButton(
            inner,
            text="← Back to Home",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_BODY,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=110,
            height=28,
            corner_radius=6,
            command=self.on_back,
        )
        btn_back.pack(side="right")

    def _build_form_card(self) -> None:
        """Constructs the card containing all form inputs and validation alerts."""
        card = ctk.CTkFrame(
            self.scroll_container,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
        )
        card.pack(fill="x", pady=(0, 15))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=35, pady=28, fill="x")

        # Title & Subtitle
        title_lbl = ctk.CTkLabel(
            inner,
            text="Patient Information",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        title_lbl.pack(fill="x", pady=(0, 4))

        subtitle_lbl = ctk.CTkLabel(
            inner,
            text="Enter the patient's basic information before continuing to symptom assessment.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        subtitle_lbl.pack(fill="x", pady=(0, 16))

        # Alert Banner (for validation errors)
        self.alert_frame = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_DANGER_BG,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER,
            corner_radius=6,
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

        # Form Container using a structured layout
        form_grid = ctk.CTkFrame(inner, fg_color="transparent")
        form_grid.pack(fill="x", pady=(10, 0))

        # --- Field 1: Patient Name (Required) ---
        lbl_name = ctk.CTkLabel(
            form_grid,
            text="Patient Full Name *",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_name.pack(fill="x", pady=(4, 2))

        self.entry_name = ctk.CTkEntry(
            form_grid,
            placeholder_text="e.g. Abul Kashem or Rokeya Begum",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=36,
            corner_radius=6,
        )
        self.entry_name.pack(fill="x", pady=(0, 12))
        if self.initial_data.get("name"):
            self.entry_name.insert(0, self.initial_data["name"])

        # --- Two-Column Row: Age & Gender ---
        row_frame = ctk.CTkFrame(form_grid, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 12))
        row_frame.grid_columnconfigure((0, 1), weight=1, uniform="demo_row")

        # Column 0: Age (Required)
        col_age = ctk.CTkFrame(row_frame, fg_color="transparent")
        col_age.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        lbl_age = ctk.CTkLabel(
            col_age,
            text="Age (0–120) *",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_age.pack(fill="x", pady=(0, 2))

        self.entry_age = ctk.CTkEntry(
            col_age,
            placeholder_text="e.g. 45",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=36,
            corner_radius=6,
        )
        self.entry_age.pack(fill="x")
        if "age" in self.initial_data and self.initial_data["age"] is not None:
            self.entry_age.insert(0, str(self.initial_data["age"]))

        # Column 1: Sex / Gender (Required)
        col_gender = ctk.CTkFrame(row_frame, fg_color="transparent")
        col_gender.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        lbl_gender = ctk.CTkLabel(
            col_gender,
            text="Sex / Gender *",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_gender.pack(fill="x", pady=(0, 2))

        self.combo_gender = ctk.CTkComboBox(
            col_gender,
            values=GENDER_OPTIONS,
            state="readonly",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            dropdown_font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=36,
            corner_radius=6,
        )
        self.combo_gender.pack(fill="x")
        current_gender = self.initial_data.get("gender")
        if current_gender and current_gender in GENDER_OPTIONS:
            self.combo_gender.set(current_gender)
        else:
            self.combo_gender.set(GENDER_OPTIONS[0])

        # --- Field 3: Location (District / Upazila) (Required) ---
        lbl_location = ctk.CTkLabel(
            form_grid,
            text="District / Upazila *",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_location.pack(fill="x", pady=(4, 2))

        self.entry_location = ctk.CTkEntry(
            form_grid,
            placeholder_text="e.g. Rangpur, Pirgachha or Kurigram, Chilmari",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=36,
            corner_radius=6,
        )
        self.entry_location.pack(fill="x", pady=(0, 12))
        if self.initial_data.get("location"):
            self.entry_location.insert(0, self.initial_data["location"])

        # --- Field 4: Phone Number (Optional) ---
        lbl_phone = ctk.CTkLabel(
            form_grid,
            text="Phone Number (Optional)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        lbl_phone.pack(fill="x", pady=(4, 2))

        self.entry_phone = ctk.CTkEntry(
            form_grid,
            placeholder_text="e.g. 01700000000 (Optional for rural patients)",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=36,
            corner_radius=6,
        )
        self.entry_phone.pack(fill="x", pady=(0, 6))
        if self.initial_data.get("phone") and self.initial_data["phone"] != "N/A":
            self.entry_phone.insert(0, self.initial_data["phone"])

        phone_hint = ctk.CTkLabel(
            form_grid,
            text="Note: Phone number may be left blank if patient does not own a mobile device.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        phone_hint.pack(fill="x", pady=(0, 22))

        # --- Form Action Buttons ---
        btn_container = ctk.CTkFrame(form_grid, fg_color="transparent")
        btn_container.pack(fill="x")

        self.btn_continue = ctk.CTkButton(
            btn_container,
            text="Continue ➔",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=14, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=160,
            height=40,
            corner_radius=6,
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
            command=self.on_back,
        )
        self.btn_back.pack(side="left")

    def _show_alert(self, message: str) -> None:
        """Displays error validation banner."""
        self.alert_label.configure(text=f"⚠️ {message}")
        self.alert_frame.pack(fill="x", pady=(0, 14), before=self.entry_name)

    def _hide_alert(self) -> None:
        """Hides error validation banner."""
        self.alert_frame.pack_forget()

    def _handle_continue(self) -> None:
        """Validates all inputs according to Prompt 06 & Prompt 16 specifications."""
        if getattr(self, "_is_submitting", False):
            return

        self._hide_alert()

        name = self.entry_name.get()
        age_str = self.entry_age.get()
        gender = self.combo_gender.get()
        location = self.entry_location.get()
        phone = self.entry_phone.get()

        # 1. Validate Patient Name
        is_valid_name, name_err = validators.validate_name(name)
        if not is_valid_name:
            self._show_alert(name_err)
            return

        # 2. Validate Age
        is_valid_age, age_err, age_int = validators.validate_age(age_str)
        if not is_valid_age:
            self._show_alert(age_err)
            return

        # 3. Validate Sex / Gender
        is_valid_gender, gender_err = validators.validate_gender(gender)
        if not is_valid_gender:
            self._show_alert(gender_err)
            return

        # 4. Validate District / Upazila Location
        is_valid_loc, loc_err = validators.validate_location(location)
        if not is_valid_loc:
            self._show_alert(loc_err)
            return

        # 5. Validate Phone (Optional)
        is_valid_phone, phone_err, clean_phone = validators.validate_phone(phone)
        if not is_valid_phone:
            self._show_alert(phone_err)
            return

        # Prevent duplicate submissions
        self._is_submitting = True
        self.btn_continue.configure(state="disabled", text="Saving...")

        # 6. Build patient data structure
        patient_data: Dict[str, Any] = {
            "name": str(name).strip(),
            "age": age_int,
            "gender": gender,
            "location": str(location).strip(),
            "phone": clean_phone if clean_phone else "N/A",
        }

        # Success: notify master app
        try:
            self.on_continue(patient_data)
        except Exception:
            self._is_submitting = False
            self.btn_continue.configure(state="normal", text="Continue ➔")


class SymptomPlaceholderView(ctk.CTkFrame):
    """Temporary placeholder view after saving patient info (Prompt 06)."""

    def __init__(
        self,
        master: Any,
        patient_data: Dict[str, Any],
        on_edit_info: Callable[[], None],
        on_back_to_home: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.patient_data = patient_data
        self.on_edit_info = on_edit_info
        self.on_back_to_home = on_back_to_home

        self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the temporary next-step placeholder interface."""
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
        inner.pack(padx=40, pady=32, fill="both")

        # Success Badge
        badge = ctk.CTkLabel(
            inner,
            text="✓ Patient Information Saved",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_NOTICE_TEXT,
            fg_color=theme.COLOR_NOTICE_BG,
            corner_radius=6,
            padx=14,
            pady=5,
        )
        badge.pack(pady=(0, 15))

        # Title
        title_lbl = ctk.CTkLabel(
            inner,
            text="Patient Information Recorded",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        title_lbl.pack(pady=(0, 6))

        # Next Step Announcement (as requested by Prompt 06)
        desc_lbl = ctk.CTkLabel(
            inner,
            text=(
                "Patient information saved for this assessment.\n"
                "Symptom Intake will be available in the next development step (Prompt 07)."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_PRIMARY_HOVER,
            justify="center",
        )
        desc_lbl.pack(pady=(0, 20))

        # Summary Card of Temporary Session Data
        summary_frame = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_BG_MAIN,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        summary_frame.pack(fill="x", pady=(0, 25))

        sum_inner = ctk.CTkFrame(summary_frame, fg_color="transparent")
        sum_inner.pack(padx=20, pady=16, fill="x")

        sum_title = ctk.CTkLabel(
            sum_inner,
            text="Temporary Session Data for this Assessment:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        sum_title.pack(fill="x", pady=(0, 8))

        # Render rows
        self._add_summary_row(sum_inner, "Patient Name", self.patient_data.get("name", ""))
        self._add_summary_row(
            sum_inner,
            "Age & Gender",
            f"{self.patient_data.get('age', '')} years, {self.patient_data.get('gender', '')}",
        )
        self._add_summary_row(sum_inner, "District / Upazila", self.patient_data.get("location", ""))
        self._add_summary_row(sum_inner, "Phone Number", self.patient_data.get("phone", "N/A"))

        # Action Buttons
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack()

        btn_edit = ctk.CTkButton(
            btn_frame,
            text="← Edit Patient Info",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=150,
            height=36,
            corner_radius=6,
            command=self.on_edit_info,
        )
        btn_edit.pack(side="left", padx=8)

        btn_home = ctk.CTkButton(
            btn_frame,
            text="Back to Patient Home",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_BODY,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=150,
            height=36,
            corner_radius=6,
            command=self.on_back_to_home,
        )
        btn_home.pack(side="left", padx=8)

    def _add_summary_row(self, parent: Any, label: str, value: str) -> None:
        """Helper to render a key-value row in the summary card."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)

        lbl = ctk.CTkLabel(
            row,
            text=f"{label}:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED,
            width=140,
            anchor="w",
        )
        lbl.pack(side="left")

        val = ctk.CTkLabel(
            row,
            text=value,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        val.pack(side="left")
