"""Clinician Dashboard & Patient Review View for SasthoSetu (Prompt 13, 14 & 15).

Provides the main Clinician Dashboard interface:
- Displays prioritized patient triage queue directly from local SQLite database.
- Ranks patients by effective urgency (incorporating clinician overrides) and FIFO arrival order.
- Shows live summary count cards based on effective urgency for active waiting cases.
- Provides instant search by Patient Name, ID, or Location.
- Provides filtering by Urgency tier and Consultation Status.
- Allows clicking any record to view Patient Assessment Details and Clinician Review.
- Enables clinicians to review symptoms, automated triage, record clinical notes,
  optionally override urgency with confirmation, and manage consultation status.
- Strictly preserves the original automated safety-net / AI assessment for medical audit.
- Non-diagnostic: provides decision support and queue prioritization without clinical diagnosis.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk

from core import constants, priority_queue, theme
from core.safety_rules import get_rule_readable_label
from database import db
from utils import validators
from utils.logger import get_logger

log = get_logger("ui.dashboard")


class ConfirmActionDialog(ctk.CTkToplevel):
    """Reusable modal dialog for confirming high-impact clinician actions (Prompt 15)."""

    def __init__(
        self,
        master: Any,
        title: str,
        message: str,
        confirm_btn_text: str = "Confirm",
        confirm_btn_color: str = theme.COLOR_PRIMARY,
        on_confirm: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(master)
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        self.title(title)
        self.geometry("480x250")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.configure(fg_color=theme.COLOR_BG_MAIN)
        self._build_ui(title, message, confirm_btn_text, confirm_btn_color)
        self._center_window()

    def _center_window(self) -> None:
        """Centers confirmation modal over parent window."""
        self.update_idletasks()
        try:
            parent_x = self.master.winfo_rootx()
            parent_y = self.master.winfo_rooty()
            parent_w = self.master.winfo_width()
            parent_h = self.master.winfo_height()
            win_w = 480
            win_h = 250
            pos_x = parent_x + (parent_w - win_w) // 2
            pos_y = parent_y + (parent_h - win_h) // 2
            self.geometry(f"{win_w}x{win_h}+{max(0, pos_x)}+{max(0, pos_y)}")
        except Exception:
            pass

    def _build_ui(self, title: str, message: str, btn_text: str, btn_color: str) -> None:
        card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        card.pack(fill="both", expand=True, padx=20, pady=20)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=20, pady=16, fill="both", expand=True)

        lbl_title = ctk.CTkLabel(
            inner,
            text=title,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        lbl_title.pack(anchor="w", pady=(0, 8))

        lbl_msg = ctk.CTkLabel(
            inner,
            text=message,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            justify="left",
            wraplength=400,
            anchor="w",
        )
        lbl_msg.pack(fill="x", pady=(0, 16))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom")

        btn_cancel = ctk.CTkButton(
            btn_row,
            text="Cancel",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_MUTED,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=100,
            height=32,
            corner_radius=6,
            command=self._do_cancel,
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_confirm = ctk.CTkButton(
            btn_row,
            text=btn_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color=btn_color,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=140,
            height=32,
            corner_radius=6,
            command=self._do_confirm,
        )
        btn_confirm.pack(side="right")

    def _do_confirm(self) -> None:
        self.destroy()
        if self.on_confirm:
            self.on_confirm()

    def _do_cancel(self) -> None:
        self.destroy()
        if self.on_cancel:
            self.on_cancel()


class PatientDetailDialog(ctk.CTkToplevel):
    """Modal dialog displaying comprehensive patient assessment details and clinician review (Prompt 15)."""

    def __init__(
        self,
        master: Any,
        record: Dict[str, Any],
        queue_pos: Optional[str] = None,
        user_record: Optional[Dict[str, Any]] = None,
        on_review_saved: Optional[Callable[[], None]] = None,
        db_path: Optional[str] = None,
    ) -> None:
        super().__init__(master)

        self.record = record
        self.queue_pos = queue_pos or " — "
        self.user_record = user_record or {}
        self.on_review_saved = on_review_saved
        self.db_path = db_path

        self.title("Patient Assessment & Clinician Review — SasthoSetu")
        self.geometry("760x720")
        self.minsize(720, 600)
        self.resizable(True, True)

        # Modal window configuration
        self.transient(master)
        self.grab_set()

        self._build_ui()
        self._center_window()

    def _center_window(self) -> None:
        """Centers the dialog on top of the parent window."""
        self.update_idletasks()
        try:
            parent_x = self.master.winfo_rootx()
            parent_y = self.master.winfo_rooty()
            parent_w = self.master.winfo_width()
            parent_h = self.master.winfo_height()
            win_w = 760
            win_h = 720
            pos_x = parent_x + (parent_w - win_w) // 2
            pos_y = parent_y + (parent_h - win_h) // 2
            self.geometry(f"{win_w}x{win_h}+{max(0, pos_x)}+{max(0, pos_y)}")
        except Exception:
            pass

    def _build_ui(self) -> None:
        """Constructs the patient assessment detail layout."""
        self.configure(fg_color=theme.COLOR_BG_MAIN)

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=25, pady=(15, 15))

        # ---------------------------------------------------------------------
        # 1. Dialog Header (Title + Effective Urgency Badge)
        # ---------------------------------------------------------------------
        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        rec_id = self.record.get("id", "N/A")
        name = self.record.get("patient_name", "Patient")
        auto_urgency = self.record.get("urgency_level")
        override_urgency = self.record.get("clinician_override_urgency")
        effective_urgency = self.record.get("final_urgency") or override_urgency or auto_urgency
        is_overridden = bool(override_urgency and override_urgency != auto_urgency)

        left_hdr = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_hdr.pack(side="left", fill="x", expand=True)

        title_lbl = ctk.CTkLabel(
            left_hdr,
            text=f"Assessment #{rec_id} — {name}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        title_lbl.pack(anchor="w")

        sub_hdr = ctk.CTkLabel(
            left_hdr,
            text="Patient Clinical Intake & Physician Decision Support",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        sub_hdr.pack(anchor="w")

        # Right Header: Urgency Badges
        right_hdr = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_hdr.pack(side="right")

        badge_text, badge_fg, badge_text_color = self._get_urgency_badge_props(effective_urgency)
        urg_badge = ctk.CTkLabel(
            right_hdr,
            text=badge_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=badge_text_color,
            fg_color=badge_fg,
            corner_radius=6,
            padx=12,
            pady=4,
        )
        urg_badge.pack(anchor="e")

        if is_overridden:
            lbl_ovr = ctk.CTkLabel(
                right_hdr,
                text=f"Overridden by Clinician (Automated: {auto_urgency})",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=10, weight="bold"),
                text_color=theme.COLOR_PRIMARY_HOVER,
            )
            lbl_ovr.pack(anchor="e", pady=(2, 0))

        # ---------------------------------------------------------------------
        # 2. Patient Demographics Card
        # ---------------------------------------------------------------------
        demo_card = self._create_card(scroll_frame, "Patient Demographics")
        age = self.record.get("patient_age", "N/A")
        gender = self.record.get("patient_gender", "N/A")
        location = self.record.get("patient_location", "N/A")
        phone = self.record.get("patient_phone") or "Not provided"
        raw_time = self.record.get("created_at", "N/A")

        self._add_detail_row(demo_card, "Patient Name", name)
        self._add_detail_row(demo_card, "Demographics", f"{age} yrs, {gender}")
        self._add_detail_row(demo_card, "Location", location)
        self._add_detail_row(demo_card, "Contact Phone", phone)
        self._add_detail_row(demo_card, "Submission Timestamp", str(raw_time))

        # ---------------------------------------------------------------------
        # 3. Reported Symptoms Card (Original Verbatim Symptoms)
        # ---------------------------------------------------------------------
        sym_card = self._create_card(scroll_frame, "Reported Symptoms (Patient Original Description)")
        symptoms_text = self.record.get("symptoms", "None reported")
        dur_val = self.record.get("symptom_duration")
        dur_unit = self.record.get("duration_unit")
        dur_display = f"{dur_val} {dur_unit}" if dur_val else "Not specified"
        severity = self.record.get("reported_severity") or "Not specified"
        additional = self.record.get("additional_information") or "None"

        self._add_detail_row(sym_card, "Chief Complaints", symptoms_text)
        self._add_detail_row(sym_card, "Symptom Duration", dur_display)
        self._add_detail_row(sym_card, "Reported Severity", severity)
        self._add_detail_row(sym_card, "Medical Background", additional)

        # ---------------------------------------------------------------------
        # 4. Automated Triage Assessment Card
        # ---------------------------------------------------------------------
        triage_card = self._create_card(scroll_frame, "Automated Triage Assessment (Preserved)")
        source = self.record.get("triage_source")
        source_display = constants.SOURCE_DISPLAY_NAMES.get(
            source,
            "Deterministic Safety-Net Rule" if auto_urgency == constants.TIER_URGENT else "Contextual AI (Gemini)",
        )
        reason = self.record.get("triage_reason") or "No detailed reason recorded."
        advice = self.record.get("triage_advice") or "Clinical assessment advised."

        auto_badge_text, _, _ = self._get_urgency_badge_props(auto_urgency)
        self._add_detail_row(triage_card, "Automated Urgency", auto_badge_text)
        self._add_detail_row(triage_card, "Assessment Source", source_display)
        self._add_detail_row(triage_card, "Clinical Observation", reason)
        self._add_detail_row(triage_card, "Conservative Guidance", advice)

        # Preservation note
        pres_banner = ctk.CTkFrame(triage_card, fg_color=theme.COLOR_BG_MAIN, corner_radius=6)
        pres_banner.pack(fill="x", pady=(8, 2))
        ctk.CTkLabel(
            pres_banner,
            text="🛡️ Automated Assessment Protection: Original safety-net and AI records are preserved permanently for medical audit.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
            padx=10,
            pady=4,
        ).pack(anchor="w")

        # ---------------------------------------------------------------------
        # 5. Clinician Review Section (Prompt 15)
        # ---------------------------------------------------------------------
        review_card = self._create_card(scroll_frame, "Clinician Review & Urgency Override")

        user_role = self.user_record.get("role")
        is_clinician = (user_role == constants.ROLE_CLINICIAN)

        if not is_clinician:
            # Role protection notice for non-clinicians
            role_banner = ctk.CTkFrame(
                review_card,
                fg_color=theme.COLOR_NOTICE_BG,
                border_width=1,
                border_color=theme.COLOR_NOTICE_BORDER,
                corner_radius=6,
            )
            role_banner.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(
                role_banner,
                text="🔒 Role Protection: Clinician review actions (urgency override, clinician notes, and status management) require an authenticated Clinician account.",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11, weight="bold"),
                text_color=theme.COLOR_NOTICE_TEXT,
                wraplength=600,
                justify="left",
                padx=12,
                pady=8,
            ).pack(anchor="w")

            # Display existing review notes in read-only form if present
            stored_notes = self.record.get("clinician_notes") or "No clinician notes entered yet."
            self._add_detail_row(review_card, "Final Queue Urgency", effective_urgency or auto_urgency or "N/A")
            self._add_detail_row(review_card, "Clinician Override", override_urgency or "None (Automated)")
            self._add_detail_row(review_card, "Clinician Notes", stored_notes)
            if self.record.get("reviewed_by"):
                self._add_detail_row(review_card, "Reviewed By", f"{self.record.get('reviewed_by')} ({self.record.get('reviewed_at')})")

        else:
            # Active Clinician Review Controls
            # 5a. Urgency Override Selector
            urg_row = ctk.CTkFrame(review_card, fg_color="transparent")
            urg_row.pack(fill="x", pady=(0, 8))

            lbl_urg_title = ctk.CTkLabel(
                urg_row,
                text="Triage Priority Override:",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=theme.COLOR_TEXT_BODY,
                width=160,
                anchor="w",
            )
            lbl_urg_title.pack(side="left")

            initial_override = override_urgency if override_urgency in [
                constants.TIER_URGENT,
                constants.TIER_MODERATE,
                constants.TIER_ROUTINE,
            ] else constants.OVERRIDE_USE_AUTOMATED

            self.combo_override = ctk.CTkOptionMenu(
                urg_row,
                values=constants.CLINICIAN_OVERRIDE_OPTIONS,
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
                fg_color=theme.COLOR_CARD_BG,
                text_color=theme.COLOR_TEXT_TITLE,
                button_color=theme.COLOR_CARD_BORDER,
                button_hover_color=theme.COLOR_BG_MAIN,
                dropdown_fg_color=theme.COLOR_CARD_BG,
                height=32,
                width=240,
            )
            self.combo_override.set(initial_override)
            self.combo_override.pack(side="left")

            lbl_hint = ctk.CTkLabel(
                review_card,
                text="Select 'Use Automated Assessment' to accept the AI/safety-net result, or choose a specific urgency to override.",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
                text_color=theme.COLOR_TEXT_MUTED,
                anchor="w",
            )
            lbl_hint.pack(anchor="w", pady=(0, 10))

            # 5b. Consultation Status Selector & Quick Action Buttons
            stat_row = ctk.CTkFrame(review_card, fg_color="transparent")
            stat_row.pack(fill="x", pady=(0, 8))

            lbl_stat_title = ctk.CTkLabel(
                stat_row,
                text="Consultation Status:",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=theme.COLOR_TEXT_BODY,
                width=160,
                anchor="w",
            )
            lbl_stat_title.pack(side="left")

            current_status = self.record.get("status", constants.STATUS_WAITING)
            self.combo_status = ctk.CTkOptionMenu(
                stat_row,
                values=constants.CONSULTATION_STATUS_FLOW,
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
                fg_color=theme.COLOR_CARD_BG,
                text_color=theme.COLOR_TEXT_TITLE,
                button_color=theme.COLOR_CARD_BORDER,
                button_hover_color=theme.COLOR_BG_MAIN,
                dropdown_fg_color=theme.COLOR_CARD_BG,
                height=32,
                width=180,
            )
            self.combo_status.set(current_status)
            self.combo_status.pack(side="left", padx=(0, 12))

            # Quick status advance buttons
            if current_status == constants.STATUS_WAITING:
                btn_quick_consult = ctk.CTkButton(
                    stat_row,
                    text="🩺 Start Consultation",
                    font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
                    fg_color="transparent",
                    text_color=theme.COLOR_PRIMARY,
                    border_width=1,
                    border_color=theme.COLOR_PRIMARY,
                    hover_color=theme.COLOR_NOTICE_BG,
                    height=28,
                    command=lambda: self.combo_status.set(constants.STATUS_IN_CONSULTATION),
                )
                btn_quick_consult.pack(side="left")
            elif current_status == constants.STATUS_IN_CONSULTATION:
                btn_quick_complete = ctk.CTkButton(
                    stat_row,
                    text="✅ Complete Consultation",
                    font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
                    fg_color="transparent",
                    text_color=theme.COLOR_ROUTINE_ACCENT,
                    border_width=1,
                    border_color=theme.COLOR_ROUTINE_ACCENT,
                    hover_color=theme.COLOR_ROUTINE_BG,
                    height=28,
                    command=lambda: self.combo_status.set(constants.STATUS_COMPLETED),
                )
                btn_quick_complete.pack(side="left")

            # 5c. Clinician Review Notes
            lbl_notes = ctk.CTkLabel(
                review_card,
                text="Clinician Review Notes:",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=theme.COLOR_TEXT_BODY,
                anchor="w",
            )
            lbl_notes.pack(anchor="w", pady=(4, 4))

            self.textbox_notes = ctk.CTkTextbox(
                review_card,
                height=75,
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
                fg_color=theme.COLOR_INPUT_BG,
                border_width=1,
                border_color=theme.COLOR_INPUT_BORDER,
                corner_radius=6,
            )
            self.textbox_notes.pack(fill="x", pady=(0, 6))

            # Pre-fill existing notes
            existing_notes = self.record.get("clinician_notes") or ""
            if existing_notes:
                self.textbox_notes.insert("1.0", existing_notes)

            # Audit attribution if previously reviewed
            if self.record.get("reviewed_by"):
                rev_by = self.record.get("reviewed_by")
                rev_at = self.record.get("reviewed_at")
                lbl_rev_meta = ctk.CTkLabel(
                    review_card,
                    text=f"Last reviewed by {rev_by} on {rev_at}",
                    font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11, slant="italic"),
                    text_color=theme.COLOR_TEXT_MUTED,
                    anchor="w",
                )
                lbl_rev_meta.pack(anchor="w", pady=(0, 10))

            # Feedback Banner (Errors or confirmation messages)
            self.lbl_feedback = ctk.CTkLabel(
                review_card,
                text="",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=theme.COLOR_DANGER_TEXT,
                anchor="w",
            )
            self.lbl_feedback.pack(anchor="w", pady=(2, 6))

            # 5d. Review Action Buttons Row
            btn_actions_frame = ctk.CTkFrame(review_card, fg_color="transparent")
            btn_actions_frame.pack(fill="x", pady=(5, 0))

            btn_save = ctk.CTkButton(
                btn_actions_frame,
                text="💾 Save Review",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
                fg_color=theme.COLOR_PRIMARY,
                hover_color=theme.COLOR_PRIMARY_HOVER,
                text_color=theme.COLOR_PRIMARY_TEXT,
                width=140,
                height=34,
                corner_radius=6,
                command=self._on_save_review,
            )
            btn_save.pack(side="left", padx=(0, 10))

            btn_cancel = ctk.CTkButton(
                btn_actions_frame,
                text="✕ Cancel",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
                fg_color="transparent",
                text_color=theme.COLOR_TEXT_MUTED,
                border_width=1,
                border_color=theme.COLOR_CARD_BORDER,
                hover_color=theme.COLOR_BG_MAIN,
                width=100,
                height=34,
                corner_radius=6,
                command=self.destroy,
            )
            btn_cancel.pack(side="left")

        # ---------------------------------------------------------------------
        # 6. Consultation Status & Record Metadata Card
        # ---------------------------------------------------------------------
        meta_card = self._create_card(scroll_frame, "Queue Position & Metadata")
        if self.queue_pos and self.queue_pos != " — ":
            self._add_detail_row(meta_card, "Active Queue Position", self.queue_pos)
        self._add_detail_row(meta_card, "Current Consultation Status", str(self.record.get("status", "Waiting")))
        self._add_detail_row(meta_card, "Intake Timestamp", str(raw_time))

        # ---------------------------------------------------------------------
        # 7. Medical Safety Disclaimer
        # ---------------------------------------------------------------------
        disclaimer_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color=theme.COLOR_NOTICE_BG,
            border_width=1,
            border_color=theme.COLOR_NOTICE_BORDER,
            corner_radius=6,
        )
        disclaimer_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            disclaimer_frame,
            text=(
                "ℹ️ Medical Safety Boundary: SasthoSetu is a decision-support prototype.\n"
                "The attending clinician retains final authority on patient queueing, evaluation, and medical treatment."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_NOTICE_TEXT,
            justify="center",
        ).pack(padx=14, pady=8)

        # ---------------------------------------------------------------------
        # 8. Close Button (when read-only or viewing)
        # ---------------------------------------------------------------------
        if not is_clinician:
            btn_close = ctk.CTkButton(
                scroll_frame,
                text="Close Details",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
                fg_color=theme.COLOR_PRIMARY,
                hover_color=theme.COLOR_PRIMARY_HOVER,
                text_color=theme.COLOR_PRIMARY_TEXT,
                width=140,
                height=36,
                corner_radius=6,
                command=self.destroy,
            )
            btn_close.pack(anchor="center", pady=(5, 10))

    def _create_card(self, parent: Any, title: str) -> ctk.CTkFrame:
        """Helper to create a structured section card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=18, pady=12, fill="both")

        lbl_title = ctk.CTkLabel(
            inner,
            text=title,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=14, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        lbl_title.pack(anchor="w", pady=(0, 8))
        return inner

    def _add_detail_row(self, parent: Any, label: str, value: str) -> None:
        """Helper to render a key-value row inside a detail card."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)

        lbl = ctk.CTkLabel(
            row,
            text=f"{label}:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED,
            width=170,
            anchor="nw",
        )
        lbl.pack(side="left", anchor="nw")

        val = ctk.CTkLabel(
            row,
            text=str(value),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
            wraplength=480,
            justify="left",
        )
        val.pack(side="left", fill="x", expand=True)

    def _get_urgency_badge_props(self, urgency: Optional[str]) -> tuple:
        """Returns (badge_text, bg_color, text_color) based on urgency tier."""
        if urgency == constants.TIER_URGENT:
            return "🔴 URGENT", theme.COLOR_URGENT_BG, theme.COLOR_URGENT_ACCENT
        elif urgency == constants.TIER_MODERATE:
            return "🟡 MODERATE", theme.COLOR_MODERATE_BG, theme.COLOR_MODERATE_ACCENT
        elif urgency == constants.TIER_ROUTINE:
            return "🟢 ROUTINE", theme.COLOR_ROUTINE_BG, theme.COLOR_ROUTINE_ACCENT
        else:
            return "⚪ PENDING", "#F1F5F9", theme.COLOR_TEXT_MUTED

    # =========================================================================
    # Clinician Review Saving & Confirmation Handlers (Prompt 15)
    # =========================================================================

    def _on_save_review(self) -> None:
        """Validates inputs and coordinates confirmation dialogs before saving review."""
        selected_override = self.combo_override.get()
        selected_status = self.combo_status.get()
        notes = self.textbox_notes.get("1.0", "end").strip()

        auto_urgency = self.record.get("urgency_level")
        prev_override = self.record.get("clinician_override_urgency")
        current_status = self.record.get("status", constants.STATUS_WAITING)

        # 1. Validation: Allowed override choices
        if selected_override not in constants.CLINICIAN_OVERRIDE_OPTIONS:
            self.lbl_feedback.configure(
                text="⚠️ Invalid urgency selection. Choose a valid tier.",
                text_color=theme.COLOR_DANGER_TEXT,
            )
            return

        # 1b. Status transition guard: Reopening completed consultations is prohibited
        if current_status == constants.STATUS_COMPLETED and selected_status != constants.STATUS_COMPLETED:
            self.lbl_feedback.configure(
                text="⚠️ This consultation has already been completed.",
                text_color=theme.COLOR_DANGER_TEXT,
            )
            return

        # 1c. Notes length validation
        if len(notes) > constants.MAX_CLINICIAN_NOTES_LENGTH:
            self.lbl_feedback.configure(
                text=f"⚠️ Clinician note exceeds the maximum length of {constants.MAX_CLINICIAN_NOTES_LENGTH} characters.",
                text_color=theme.COLOR_DANGER_TEXT,
            )
            return

        # 2. Check if an urgency override confirmation is required (Section 9)
        # Required if selecting a specific urgency that differs from the automated urgency
        is_urgency_changing = (
            selected_override != constants.OVERRIDE_USE_AUTOMATED
            and selected_override != auto_urgency
            and selected_override != prev_override
        )

        # 3. Check if status completion confirmation is required (Section 13)
        is_completing = (
            selected_status == constants.STATUS_COMPLETED
            and current_status != constants.STATUS_COMPLETED
        )

        def _execute_save() -> None:
            reviewer = (
                self.user_record.get("full_name")
                or self.user_record.get("username_or_email")
                or "Clinician"
            )
            user_id = self.user_record.get("id")

            try:
                success = db.save_clinician_review(
                    record_id=int(self.record["id"]),
                    reviewed_by=reviewer,
                    clinician_notes=notes,
                    clinician_override_urgency=selected_override,
                    status=selected_status,
                    user_id=user_id,
                    db_path=self.db_path,
                )

                if success:
                    if self.on_review_saved:
                        self.on_review_saved()
                    self.destroy()
                else:
                    self.lbl_feedback.configure(
                        text="⚠️ Failed to update database. Record not found.",
                        text_color=theme.COLOR_DANGER_TEXT,
                    )
            except Exception as err:
                self.lbl_feedback.configure(
                    text=f"⚠️ Error saving review: {err}",
                    text_color=theme.COLOR_DANGER_TEXT,
                )

        # If urgency is being overridden, trigger confirmation modal first
        if is_urgency_changing:
            ConfirmActionDialog(
                master=self,
                title="Confirm Triage Urgency Override",
                message=(
                    "You are changing the patient's triage priority.\n\n"
                    f"Automated Urgency: {auto_urgency or 'None'}\n"
                    f"New Clinician Urgency: {selected_override}\n\n"
                    "Do you want to continue?"
                ),
                confirm_btn_text="Confirm Override",
                confirm_btn_color=theme.COLOR_WARNING_ACCENT if selected_override == constants.TIER_MODERATE else theme.COLOR_PRIMARY,
                on_confirm=lambda: _execute_save() if not is_completing else self._prompt_completion_confirm(_execute_save),
            )
        elif is_completing:
            self._prompt_completion_confirm(_execute_save)
        else:
            _execute_save()

    def _prompt_completion_confirm(self, on_confirmed_callback: Callable[[], None]) -> None:
        """Prompts confirmation before archiving a patient as Completed."""
        ConfirmActionDialog(
            master=self,
            title="Confirm Complete Consultation",
            message=(
                "Mark this consultation as completed?\n\n"
                "The patient will be archived from the active waiting queue."
            ),
            confirm_btn_text="Mark Completed",
            confirm_btn_color=theme.COLOR_PRIMARY,
            on_confirm=on_confirmed_callback,
        )


class ClinicianDashboardView(ctk.CTkFrame):
    """Main Clinician Dashboard view for patient triage review and queue management."""

    def __init__(
        self,
        master: Any,
        user_record: Dict[str, Any],
        on_switch_role: Callable[[], None],
        on_logout: Callable[[], None],
        db_path: Optional[str] = None,
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.user_record = user_record or {}
        self.on_switch_role = on_switch_role
        self.on_logout = on_logout
        self.db_path = db_path

        # Local state
        self.all_records: List[Dict[str, Any]] = []
        self.filtered_records: List[Dict[str, Any]] = []
        self.current_urgency_filter: str = "All Urgencies"
        self.current_status_filter: str = "Waiting"
        self.search_query: str = ""

        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        """Constructs the dashboard layout."""
        # Main padding container
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=20, pady=(15, 10))

        # ---------------------------------------------------------------------
        # 1. Header Bar: Title, Subtitle, User Identity, Switch Role / Logout
        # ---------------------------------------------------------------------
        header_bar = ctk.CTkFrame(main_layout, fg_color="transparent")
        header_bar.pack(fill="x", pady=(0, 10))

        left_header = ctk.CTkFrame(header_bar, fg_color="transparent")
        left_header.pack(side="left")

        title_lbl = ctk.CTkLabel(
            left_header,
            text="SasthoSetu — Clinician Dashboard",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            left_header,
            text="Prioritized Patient Triage Queue & Clinical Review",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        sub_lbl.pack(anchor="w")

        # Right Header: Clinician profile & actions
        right_header = ctk.CTkFrame(header_bar, fg_color="transparent")
        right_header.pack(side="right")

        user_name = self.user_record.get("full_name") or self.user_record.get("username_or_email", "Clinician")
        user_lbl = ctk.CTkLabel(
            right_header,
            text=f"Logged in: {user_name}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_PRIMARY_HOVER,
            fg_color=theme.COLOR_NOTICE_BG,
            corner_radius=6,
            padx=10,
            pady=4,
        )
        user_lbl.pack(side="left", padx=(0, 10))

        btn_role = ctk.CTkButton(
            right_header,
            text="Switch Role",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=theme.COLOR_PRIMARY,
            border_width=1,
            border_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_NOTICE_BG,
            width=90,
            height=30,
            corner_radius=6,
            command=self.on_switch_role,
        )
        btn_role.pack(side="left", padx=(0, 6))

        btn_logout = ctk.CTkButton(
            right_header,
            text="Logout",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color="transparent",
            text_color=theme.COLOR_DANGER_TEXT,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER,
            hover_color=theme.COLOR_DANGER_BG,
            width=70,
            height=30,
            corner_radius=6,
            command=self.on_logout,
        )
        btn_logout.pack(side="left")

        # ---------------------------------------------------------------------
        # 1b. Database Refresh Warning Banner (Prompt 16)
        # ---------------------------------------------------------------------
        self.db_warning_banner = ctk.CTkFrame(
            main_layout,
            fg_color=theme.COLOR_DANGER_BG,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER,
            corner_radius=6,
        )
        self.lbl_db_warning = ctk.CTkLabel(
            self.db_warning_banner,
            text="⚠️ Unable to refresh the patient queue. Please try again.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_DANGER_TEXT,
            anchor="w",
        )
        self.lbl_db_warning.pack(side="left", padx=12, pady=6)

        # ---------------------------------------------------------------------
        # 2. Summary Metric Cards Row (Based on Effective Urgency)
        # ---------------------------------------------------------------------
        self.summary_frame = ctk.CTkFrame(main_layout, fg_color="transparent")
        self.summary_frame.pack(fill="x", pady=(0, 10))

        self.card_total = self._create_summary_metric(self.summary_frame, "Total Waiting", "0", theme.COLOR_TEXT_TITLE)
        self.card_urgent = self._create_summary_metric(self.summary_frame, "🔴 Urgent", "0", theme.COLOR_URGENT_ACCENT)
        self.card_moderate = self._create_summary_metric(self.summary_frame, "🟡 Moderate", "0", theme.COLOR_MODERATE_ACCENT)
        self.card_routine = self._create_summary_metric(self.summary_frame, "🟢 Routine", "0", theme.COLOR_ROUTINE_ACCENT)
        self.card_pending = self._create_summary_metric(self.summary_frame, "⚪ Pending", "0", theme.COLOR_TEXT_MUTED)

        # ---------------------------------------------------------------------
        # 2b. Priority Queue Educational Notice (Prompt 14 Demonstration)
        # ---------------------------------------------------------------------
        banner_frame = ctk.CTkFrame(
            main_layout,
            fg_color=theme.COLOR_NOTICE_BG,
            border_width=1,
            border_color=theme.COLOR_NOTICE_BORDER,
            corner_radius=6,
        )
        banner_frame.pack(fill="x", pady=(0, 10))

        lbl_banner = ctk.CTkLabel(
            banner_frame,
            text=f"ℹ️ {priority_queue.QUEUE_RULE_EXPLANATION}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=theme.COLOR_NOTICE_TEXT,
            anchor="w",
        )
        lbl_banner.pack(side="left", padx=12, pady=5)

        # ---------------------------------------------------------------------
        # 3. Search & Filter Bar
        # ---------------------------------------------------------------------
        controls_frame = ctk.CTkFrame(
            main_layout,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        controls_frame.pack(fill="x", pady=(0, 12))

        ctrl_inner = ctk.CTkFrame(controls_frame, fg_color="transparent")
        ctrl_inner.pack(padx=14, pady=10, fill="x")

        # Search Entry
        self.entry_search = ctk.CTkEntry(
            ctrl_inner,
            placeholder_text="🔍 Search by Patient Name, ID, or Location...",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color=theme.COLOR_INPUT_BG,
            border_color=theme.COLOR_INPUT_BORDER,
            height=34,
            width=300,
        )
        self.entry_search.pack(side="left", padx=(0, 12))
        self.entry_search.bind("<KeyRelease>", self._on_search_key)

        # Urgency Filter
        lbl_urg = ctk.CTkLabel(
            ctrl_inner,
            text="Urgency:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        lbl_urg.pack(side="left", padx=(0, 6))

        self.combo_urgency = ctk.CTkOptionMenu(
            ctrl_inner,
            values=["All Urgencies", "URGENT", "MODERATE", "ROUTINE", "PENDING"],
            command=self._on_urgency_filter_changed,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color=theme.COLOR_CARD_BG,
            text_color=theme.COLOR_TEXT_BODY,
            button_color=theme.COLOR_CARD_BORDER,
            button_hover_color=theme.COLOR_BG_MAIN,
            dropdown_fg_color=theme.COLOR_CARD_BG,
            height=34,
            width=130,
        )
        self.combo_urgency.set("All Urgencies")
        self.combo_urgency.pack(side="left", padx=(0, 12))

        # Status Filter
        lbl_stat = ctk.CTkLabel(
            ctrl_inner,
            text="Status:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        lbl_stat.pack(side="left", padx=(0, 6))

        self.combo_status = ctk.CTkOptionMenu(
            ctrl_inner,
            values=["Waiting", "In Consultation", "Completed", "All Statuses"],
            command=self._on_status_filter_changed,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            fg_color=theme.COLOR_CARD_BG,
            text_color=theme.COLOR_TEXT_BODY,
            button_color=theme.COLOR_CARD_BORDER,
            button_hover_color=theme.COLOR_BG_MAIN,
            dropdown_fg_color=theme.COLOR_CARD_BG,
            height=34,
            width=130,
        )
        self.combo_status.set("Waiting")
        self.combo_status.pack(side="left", padx=(0, 14))

        # Refresh Button
        self.btn_refresh = ctk.CTkButton(
            ctrl_inner,
            text="🔄 Refresh",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            height=34,
            width=100,
            corner_radius=6,
            command=self.refresh_data,
        )
        self.btn_refresh.pack(side="right")

        # ---------------------------------------------------------------------
        # 4. Patient Queue Table Area (Header + Scrollable List)
        # ---------------------------------------------------------------------
        table_container = ctk.CTkFrame(
            main_layout,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        table_container.pack(fill="both", expand=True)

        # Table Column Headers
        tbl_header = ctk.CTkFrame(table_container, fg_color=theme.COLOR_BG_MAIN, height=36, corner_radius=0)
        tbl_header.pack(fill="x", padx=1, pady=(1, 0))

        self._create_header_col(tbl_header, "Pos", width=55)
        self._create_header_col(tbl_header, "ID", width=60)
        self._create_header_col(tbl_header, "Patient Name", width=150)
        self._create_header_col(tbl_header, "Age / Gender", width=95)
        self._create_header_col(tbl_header, "Location", width=120)
        self._create_header_col(tbl_header, "Urgency", width=120)
        self._create_header_col(tbl_header, "Source", width=120)
        self._create_header_col(tbl_header, "Arrival", width=75)
        self._create_header_col(tbl_header, "Status", width=85)
        self._create_header_col(tbl_header, "Action", width=65)

        # Scrollable Rows Frame
        self.rows_scroll = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.rows_scroll.pack(fill="both", expand=True, padx=4, pady=4)

    def _create_summary_metric(self, parent: Any, label: str, value: str, text_color: str) -> Dict[str, Any]:
        """Creates a modern metric counter card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=8,
        )
        card.pack(side="left", fill="both", expand=True, padx=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=12, pady=10)

        val_lbl = ctk.CTkLabel(
            inner,
            text=value,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=24, weight="bold"),
            text_color=text_color,
        )
        val_lbl.pack()

        lbl_desc = ctk.CTkLabel(
            inner,
            text=label,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        lbl_desc.pack()

        return {"card": card, "val_lbl": val_lbl}

    def _create_header_col(self, parent: Any, text: str, width: int) -> None:
        """Helper to create a column title in the table header."""
        lbl = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED,
            width=width,
            anchor="w",
        )
        lbl.pack(side="left", padx=6, pady=6)

    # =========================================================================
    # Data Loading, Filtering & Rendering
    # =========================================================================

    def refresh_data(self) -> None:
        """Reads the latest records from SQLite, sorts by priority queue rules, and updates cards and table."""
        try:
            raw_records = db.get_all_triage_records(self.db_path)
            self.all_records = priority_queue.sort_patients_by_priority(raw_records)
            self._hide_refresh_warning()
            self._update_summary_cards()
            self._apply_filters()
        except Exception as err:
            log.error(f"Error refreshing dashboard data: {err}")
            if self.all_records:
                # Prompt 16 Section 26: Preserve existing queue, display warning banner
                self._show_refresh_warning("⚠️ Unable to refresh the patient queue. Please try again.")
            else:
                self._render_db_error_state(str(err))

    def _show_refresh_warning(self, message: str) -> None:
        """Displays persistent warning banner without wiping existing records."""
        self.lbl_db_warning.configure(text=message)
        self.db_warning_banner.pack(fill="x", pady=(0, 10), before=self.summary_frame)

    def _hide_refresh_warning(self) -> None:
        """Hides the refresh warning banner."""
        self.db_warning_banner.pack_forget()

    def _update_summary_cards(self) -> None:
        """Calculates metric counts strictly for waiting patients using effective urgency (Prompt 15)."""
        waiting_cases = [r for r in self.all_records if r.get("status") == "Waiting"]

        total_waiting = len(waiting_cases)
        urgent_count = sum(
            1 for r in waiting_cases
            if priority_queue.get_effective_urgency(r) == constants.TIER_URGENT
        )
        moderate_count = sum(
            1 for r in waiting_cases
            if priority_queue.get_effective_urgency(r) == constants.TIER_MODERATE
        )
        routine_count = sum(
            1 for r in waiting_cases
            if priority_queue.get_effective_urgency(r) == constants.TIER_ROUTINE
        )
        pending_count = sum(
            1 for r in waiting_cases
            if priority_queue.get_effective_urgency(r) in (None, "", constants.STATE_PENDING_CONTEXTUAL_TRIAGE)
        )

        self.card_total["val_lbl"].configure(text=str(total_waiting))
        self.card_urgent["val_lbl"].configure(text=str(urgent_count))
        self.card_moderate["val_lbl"].configure(text=str(moderate_count))
        self.card_routine["val_lbl"].configure(text=str(routine_count))
        self.card_pending["val_lbl"].configure(text=str(pending_count))

    def _on_search_key(self, event: Any = None) -> None:
        """Triggered on typing in the search box with safe length limiting."""
        try:
            raw_query = self.entry_search.get() or ""
            if len(raw_query) > constants.MAX_SEARCH_QUERY_LENGTH:
                raw_query = raw_query[:constants.MAX_SEARCH_QUERY_LENGTH]
            self.search_query = raw_query.strip().lower()
            self._apply_filters()
        except Exception as err:
            log.error(f"Error handling search query: {err}")

    def _on_urgency_filter_changed(self, choice: str) -> None:
        """Triggered on selecting an urgency filter option."""
        self.current_urgency_filter = choice
        self._apply_filters()

    def _on_status_filter_changed(self, choice: str) -> None:
        """Triggered on selecting a status filter option."""
        self.current_status_filter = choice
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Filters self.all_records based on search, effective urgency, and status."""
        results = []

        for r in self.all_records:
            # 1. Status Filter
            status = r.get("status", "Waiting")
            if self.current_status_filter != "All Statuses" and status != self.current_status_filter:
                continue

            # 2. Urgency Filter (Evaluated against Effective Urgency)
            eff_urgency = priority_queue.get_effective_urgency(r)
            if self.current_urgency_filter == "URGENT" and eff_urgency != constants.TIER_URGENT:
                continue
            elif self.current_urgency_filter == "MODERATE" and eff_urgency != constants.TIER_MODERATE:
                continue
            elif self.current_urgency_filter == "ROUTINE" and eff_urgency != constants.TIER_ROUTINE:
                continue
            elif self.current_urgency_filter == "PENDING" and eff_urgency not in (None, "", constants.STATE_PENDING_CONTEXTUAL_TRIAGE):
                continue

            # 3. Search Query (Patient Name, ID, Location)
            if self.search_query:
                p_name = (r.get("patient_name") or "").lower()
                p_id = str(r.get("id", ""))
                p_loc = (r.get("patient_location") or "").lower()

                if (
                    self.search_query not in p_name
                    and self.search_query not in p_id
                    and self.search_query not in p_loc
                ):
                    continue

            results.append(r)

        self.filtered_records = results
        self._render_rows()

    def _render_rows(self) -> None:
        """Renders patient queue rows with dynamic queue positions in the scrollable container."""
        # Clear existing rows
        for child in self.rows_scroll.winfo_children():
            child.destroy()

        if not self.filtered_records:
            self._render_empty_state()
            return

        waiting_pos_counter = 1
        for record in self.filtered_records:
            status = record.get("status", "Waiting")
            if status == "Waiting":
                display_pos = f"#{waiting_pos_counter}"
                waiting_pos_counter += 1
            else:
                display_pos = " — "
            self._render_single_row(record, display_pos=display_pos)

    def _render_single_row(self, record: Dict[str, Any], display_pos: str = " — ") -> None:
        """Renders an individual patient row card."""
        rec_id = record.get("id")
        name = record.get("patient_name", "N/A")
        age = record.get("patient_age", "N/A")
        gender = record.get("patient_gender", "N/A")
        location = record.get("patient_location", "N/A")
        auto_urgency = record.get("urgency_level")
        override = record.get("clinician_override_urgency")
        effective_urgency = priority_queue.get_effective_urgency(record)
        is_overridden = bool(override and override != auto_urgency)

        status = record.get("status", "Waiting")
        raw_time = record.get("created_at")

        # Format time for display (e.g. "10:42 AM")
        time_display = self._format_timestamp(raw_time)

        # Source label
        source = record.get("triage_source")
        if not source:
            source = constants.SOURCE_SAFETY_RULE if auto_urgency == constants.TIER_URGENT else constants.SOURCE_GEMINI
        source_short = self._get_short_source_name(source)

        # Row Frame
        row = ctk.CTkFrame(
            self.rows_scroll,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=6,
            height=48,
        )
        row.pack(fill="x", pady=2)

        # Clickable trigger opens PatientDetailDialog
        row.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 1. Queue Position
        lbl_pos = ctk.CTkLabel(
            row,
            text=display_pos,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_PRIMARY if display_pos != " — " else theme.COLOR_TEXT_MUTED,
            width=55,
            anchor="w",
        )
        lbl_pos.pack(side="left", padx=6)
        lbl_pos.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 2. ID
        lbl_id = ctk.CTkLabel(
            row,
            text=f"#{rec_id}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            width=60,
            anchor="w",
        )
        lbl_id.pack(side="left", padx=6)
        lbl_id.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 3. Patient Name
        lbl_name = ctk.CTkLabel(
            row,
            text=name,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            width=150,
            anchor="w",
        )
        lbl_name.pack(side="left", padx=6)
        lbl_name.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 4. Age / Sex
        lbl_demo = ctk.CTkLabel(
            row,
            text=f"{age} y, {gender[:1].upper() if gender else ''}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            width=95,
            anchor="w",
        )
        lbl_demo.pack(side="left", padx=6)
        lbl_demo.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 5. Location
        lbl_loc = ctk.CTkLabel(
            row,
            text=location,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            width=120,
            anchor="w",
        )
        lbl_loc.pack(side="left", padx=6)
        lbl_loc.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 6. Urgency Badge & Override Indicator (Prompt 15)
        badge_text, badge_fg, badge_color = self._get_urgency_badge_props(effective_urgency)
        urg_frame = ctk.CTkFrame(row, fg_color="transparent", width=120)
        urg_frame.pack(side="left", padx=6)

        lbl_urg = ctk.CTkLabel(
            urg_frame,
            text=badge_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=badge_color,
            fg_color=badge_fg,
            corner_radius=4,
            padx=8,
            pady=2,
        )
        lbl_urg.pack(anchor="w")
        lbl_urg.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        if is_overridden:
            lbl_override = ctk.CTkLabel(
                urg_frame,
                text="✏️ Override",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=9, weight="bold"),
                text_color=theme.COLOR_PRIMARY_HOVER,
            )
            lbl_override.pack(anchor="w")
            lbl_override.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 7. Source
        lbl_src = ctk.CTkLabel(
            row,
            text=source_short,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_MUTED,
            width=120,
            anchor="w",
        )
        lbl_src.pack(side="left", padx=6)
        lbl_src.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 8. Arrival Time
        lbl_time = ctk.CTkLabel(
            row,
            text=time_display,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.COLOR_TEXT_MUTED,
            width=75,
            anchor="w",
        )
        lbl_time.pack(side="left", padx=6)
        lbl_time.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 9. Status Badge
        status_text, status_fg, status_color = self._get_status_badge_props(status)
        stat_frame = ctk.CTkFrame(row, fg_color="transparent", width=85)
        stat_frame.pack(side="left", padx=6)
        lbl_stat = ctk.CTkLabel(
            stat_frame,
            text=status_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=10, weight="bold"),
            text_color=status_color,
            fg_color=status_fg,
            corner_radius=4,
            padx=6,
            pady=2,
        )
        lbl_stat.pack(anchor="w")
        lbl_stat.bind("<Button-1>", lambda e, r=record, p=display_pos: self._open_patient_dialog(r, p))

        # 10. Action: View Details / Review Button
        btn_view = ctk.CTkButton(
            row,
            text="Review" if self.user_record.get("role") == constants.ROLE_CLINICIAN else "View",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color="transparent",
            text_color=theme.COLOR_PRIMARY,
            border_width=1,
            border_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_NOTICE_BG,
            width=65,
            height=28,
            corner_radius=4,
            command=lambda r=record, p=display_pos: self._open_patient_dialog(r, p),
        )
        btn_view.pack(side="left", padx=6)

    def _open_patient_dialog(self, record: Dict[str, Any], queue_pos: Optional[str] = None) -> None:
        """Opens the patient assessment details and clinician review modal dialog."""
        rec_id = record.get("id")
        fresh_record = db.get_triage_record_by_id(rec_id, db_path=self.db_path) or record
        PatientDetailDialog(
            self,
            record=fresh_record,
            queue_pos=queue_pos,
            user_record=self.user_record,
            on_review_saved=self.refresh_data,
            db_path=self.db_path,
        )

    def _render_empty_state(self) -> None:
        """Renders a friendly message when no records match the criteria."""
        card = ctk.CTkFrame(self.rows_scroll, fg_color="transparent")
        card.pack(fill="x", pady=40)

        if not self.all_records:
            icon_text = "📋 No patient records in the queue yet."
            sub_text = "Patients assessed through the triage intake will automatically appear here."
        else:
            icon_text = "🔍 No matching patients found."
            sub_text = "Try clearing your search query or changing the urgency/status filters."

        ctk.CTkLabel(
            card,
            text=icon_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            card,
            text=sub_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack()

    def _get_status_badge_props(self, status: Optional[str]) -> tuple:
        """Returns (badge_text, bg_color, text_color) based on consultation status."""
        st = status or constants.STATUS_WAITING
        if st == constants.STATUS_WAITING:
            return "⏳ Waiting", theme.COLOR_STATUS_WAITING_BG, theme.COLOR_STATUS_WAITING_TEXT
        elif st == constants.STATUS_IN_CONSULTATION:
            return "🩺 Consulting", theme.COLOR_STATUS_IN_CONSULTATION_BG, theme.COLOR_STATUS_IN_CONSULTATION_TEXT
        elif st == constants.STATUS_COMPLETED:
            return "✅ Completed", theme.COLOR_STATUS_COMPLETED_BG, theme.COLOR_STATUS_COMPLETED_TEXT
        return st, theme.COLOR_BG_MAIN, theme.COLOR_TEXT_BODY

    def _render_db_error_state(self, error_msg: str) -> None:
        """Renders an error banner if SQLite fails to load."""
        for child in self.rows_scroll.winfo_children():
            child.destroy()

        err_box = ctk.CTkFrame(
            self.rows_scroll,
            fg_color=theme.COLOR_DANGER_BG,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER,
            corner_radius=8,
        )
        err_box.pack(fill="x", padx=20, pady=30)

        ctk.CTkLabel(
            err_box,
            text=f"⚠️ Database Error: Unable to retrieve patient queue.\n{error_msg}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_DANGER_TEXT,
            justify="center",
        ).pack(padx=20, pady=16)

    def _get_urgency_badge_props(self, urgency: Optional[str]) -> tuple:
        """Returns visual styling for an urgency level."""
        if urgency == constants.TIER_URGENT:
            return "🔴 URGENT", theme.COLOR_URGENT_BG, theme.COLOR_URGENT_ACCENT
        elif urgency == constants.TIER_MODERATE:
            return "🟡 MODERATE", theme.COLOR_MODERATE_BG, theme.COLOR_MODERATE_ACCENT
        elif urgency == constants.TIER_ROUTINE:
            return "🟢 ROUTINE", theme.COLOR_ROUTINE_BG, theme.COLOR_ROUTINE_ACCENT
        else:
            return "⚪ PENDING", "#F1F5F9", theme.COLOR_TEXT_MUTED

    def _get_short_source_name(self, source: Optional[str]) -> str:
        """Returns a concise assessment source label for the table row."""
        if source == constants.SOURCE_SAFETY_RULE:
            return "Safety-Net Rule"
        elif source == constants.SOURCE_GEMINI:
            return "Contextual AI"
        elif source == constants.SOURCE_FALLBACK:
            return "Safe Fallback"
        return "Safety-Net"

    def _format_timestamp(self, raw_ts: Any) -> str:
        """Formats raw timestamp into a concise time string."""
        if not raw_ts:
            return "N/A"
        try:
            ts_str = str(raw_ts).strip()
            # If standard SQLite timestamp 'YYYY-MM-DD HH:MM:SS'
            if len(ts_str) >= 16:
                dt = datetime.strptime(ts_str[:19], "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%I:%M %p")
            return ts_str
        except Exception:
            return str(raw_ts)[:10]
