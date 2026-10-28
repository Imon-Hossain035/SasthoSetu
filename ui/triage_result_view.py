"""Triage Result View for SasthoSetu (Prompt 12).

Displays the dedicated Triage Assessment Result screen:
- Presents the outcome of the hybrid triage pipeline (Safety-Net + Gemini API).
- Supports all three clinical urgency tiers:
  - 🔴 URGENT (Deterministic Safety-Net Rule, Gemini Urgent, or Safe Fallback)
  - 🟡 MODERATE (Contextual AI evaluation for sub-acute complaints)
  - 🟢 ROUTINE (Contextual AI evaluation for mild/self-limiting complaints)
- Clearly indicates the Assessment Source (Safety-Net, Gemini, or Fallback).
- Enforces strict non-diagnostic, non-prescriptive medical safety disclaimers.
- Provides Back to Symptoms, Finish Assessment, and Start New Assessment controls.
"""

from typing import Any, Callable, Dict, Optional
import customtkinter as ctk

from core import constants, theme
from core.safety_rules import get_rule_readable_label


class TriageResultView(ctk.CTkFrame):
    """Dedicated Triage Result Screen presenting hybrid triage outcomes."""

    def __init__(
        self,
        master: Any,
        assessment_data: Optional[Dict[str, Any]],
        on_back_to_symptoms: Callable[[], None],
        on_finish_assessment: Callable[[], None],
        on_start_new_assessment: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.assessment_data = assessment_data or {}
        self.on_back_to_symptoms = on_back_to_symptoms
        self.on_finish_assessment = on_finish_assessment
        self.on_start_new_assessment = on_start_new_assessment

        # Extract assessment components
        self.patient = self.assessment_data.get("patient") or {}
        self.symptoms = self.assessment_data.get("symptoms") or {}
        self.triage = self.assessment_data.get("triage") or {}
        self.assessment_id = self.assessment_data.get("assessment_id")
        self.status = self.assessment_data.get("status", constants.STATUS_WAITING)

        # Check if assessment is valid
        if not self.assessment_data or not self.symptoms:
            self._build_empty_state_ui()
        else:
            self._build_result_ui()

    # =========================================================================
    # Empty State (When accessed without an active assessment)
    # =========================================================================

    def _build_empty_state_ui(self) -> None:
        """Renders a friendly empty/error state when no active assessment exists."""
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
        inner.pack(padx=40, pady=35, fill="both")

        badge = ctk.CTkLabel(
            inner,
            text="⚠️ No Active Assessment",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_MODERATE_ACCENT,
            fg_color=theme.COLOR_MODERATE_BG,
            corner_radius=6,
            padx=12,
            pady=4,
        )
        badge.pack(pady=(0, 12))

        title = ctk.CTkLabel(
            inner,
            text="No Assessment Found",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
        )
        title.pack(pady=(0, 8))

        desc = ctk.CTkLabel(
            inner,
            text="No active patient assessment was found in this session.\nPlease return home and start a new assessment.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_BODY,
            justify="center",
        )
        desc.pack(pady=(0, 20))

        btn_home = ctk.CTkButton(
            inner,
            text="Return to Patient Home",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=14, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=200,
            height=38,
            corner_radius=6,
            command=self.on_finish_assessment,
        )
        btn_home.pack()

    # =========================================================================
    # Full Result Screen UI
    # =========================================================================

    def _build_result_ui(self) -> None:
        """Constructs the full Triage Result Screen layout inside a scrollable container."""
        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=25, pady=(15, 15))

        urgency = self.triage.get("urgency")

        # ---------------------------------------------------------------------
        # 1. Header Section
        # ---------------------------------------------------------------------
        header_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 14))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Triage Assessment Result",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=24, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            header_frame,
            text="AI-Assisted Pre-Screening Triage Priority Evaluation",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
        )
        subtitle_lbl.pack(anchor="w")

        # ---------------------------------------------------------------------
        # 2. Primary Urgency Tier Card (URGENT / MODERATE / ROUTINE)
        # ---------------------------------------------------------------------
        if urgency == constants.TIER_URGENT or self.triage.get("matched", False):
            self._render_urgent_card(scroll_container)
        elif urgency == constants.TIER_MODERATE:
            self._render_moderate_card(scroll_container)
        elif urgency == constants.TIER_ROUTINE:
            self._render_routine_card(scroll_container)
        else:
            self._render_pending_card(scroll_container)

        # ---------------------------------------------------------------------
        # 3. Patient & Assessment Summary Card
        # ---------------------------------------------------------------------
        self._render_summary_card(scroll_container)

        # ---------------------------------------------------------------------
        # 4. Mandatory Medical Safety Disclaimer
        # ---------------------------------------------------------------------
        self._render_disclaimer_card(scroll_container, is_urgent=(urgency == constants.TIER_URGENT))

        # ---------------------------------------------------------------------
        # 5. Action / Navigation Buttons
        # ---------------------------------------------------------------------
        self._render_action_buttons(scroll_container)

    # =========================================================================
    # Tier Card Renders
    # =========================================================================

    def _render_urgent_card(self, parent: Any) -> None:
        """Renders the prominent high-urgency alert card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_CARD_BG,
            border_width=2,
            border_color=theme.COLOR_URGENT_ACCENT,
            corner_radius=10,
        )
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=24, pady=20, fill="both")

        # Top Tag Row: Urgent Badge + Assessment ID
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        urgent_badge = ctk.CTkLabel(
            top_row,
            text="🔴  URGENT  •  IMMEDIATE CLINICIAN ATTENTION REQUIRED",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_DANGER_TEXT,
            fg_color=theme.COLOR_URGENT_BG,
            corner_radius=6,
            padx=14,
            pady=6,
        )
        urgent_badge.pack(side="left")

        if self.assessment_id:
            id_lbl = ctk.CTkLabel(
                top_row,
                text=f"Assessment #{self.assessment_id}  |  Queue: {self.status}",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=theme.COLOR_TEXT_MUTED,
            )
            id_lbl.pack(side="right")

        # Heading & Assessment Source
        source = self.triage.get("source", constants.SOURCE_SAFETY_RULE)
        source_name = constants.SOURCE_DISPLAY_NAMES.get(source, "Automated Triage")

        if source == constants.SOURCE_SAFETY_RULE:
            alert_title = "Potential Emergency Warning Detected"
            alert_subtitle = "An acute emergency red flag was detected by the deterministic safety-net screening."
        elif source == constants.SOURCE_FALLBACK:
            alert_title = "Safe Fallback: Manual Clinician Review Required"
            alert_subtitle = "Automated contextual triage could not be completed. Defaulted safely to Urgent for clinician review."
        else:
            alert_title = "Urgent Clinical Attention Advised"
            alert_subtitle = "Contextual AI triage evaluated this presentation as requiring immediate clinician assessment."

        title_lbl = ctk.CTkLabel(
            inner,
            text=alert_title,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=theme.COLOR_DANGER_TEXT,
            anchor="w",
        )
        title_lbl.pack(anchor="w", pady=(0, 3))

        sub_lbl = ctk.CTkLabel(
            inner,
            text=alert_subtitle,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        )
        sub_lbl.pack(anchor="w", pady=(0, 6))

        # Assessment Source Tag
        src_lbl = ctk.CTkLabel(
            inner,
            text=f"Assessment Source: {source_name}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_PRIMARY_HOVER,
            anchor="w",
        )
        src_lbl.pack(anchor="w", pady=(0, 12))

        # Matched Safety Rules Section (if safety rule triggered)
        matched_rules = self.triage.get("matched_rules", [])
        if matched_rules:
            rules_box = ctk.CTkFrame(
                inner,
                fg_color=theme.COLOR_URGENT_BG,
                border_width=1,
                border_color=theme.COLOR_URGENT_BORDER,
                corner_radius=6,
            )
            rules_box.pack(fill="x", pady=(0, 12))

            rules_inner = ctk.CTkFrame(rules_box, fg_color="transparent")
            rules_inner.pack(padx=14, pady=10, fill="x")

            rules_title = ctk.CTkLabel(
                rules_inner,
                text="Safety Warnings Detected:",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=theme.COLOR_DANGER_TEXT,
                anchor="w",
            )
            rules_title.pack(anchor="w", pady=(0, 4))

            for rule_id in matched_rules:
                friendly_name = get_rule_readable_label(rule_id)
                r_item = ctk.CTkLabel(
                    rules_inner,
                    text=f"  • {friendly_name}",
                    font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                    text_color=theme.COLOR_DANGER_TEXT,
                    anchor="w",
                )
                r_item.pack(anchor="w", pady=1)

        # Conservative, Non-Diagnostic Reason
        reason_text = self.triage.get("reason", "Acute clinical presentation reported.")
        reason_lbl = ctk.CTkLabel(
            inner,
            text=f"Triage Reason: {reason_text}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
            wraplength=880,
            justify="left",
        )
        reason_lbl.pack(anchor="w", pady=(0, 12))

        # Immediate Professional Care Guidance Box
        advice_text = self.triage.get(
            "advice",
            "Please seek immediate professional medical attention. Do not delay emergency care while waiting for an automated assessment.",
        )
        guidance_box = ctk.CTkFrame(
            inner,
            fg_color="#FFF1F2",
            border_width=1,
            border_color="#FCA5A5",
            corner_radius=6,
        )
        guidance_box.pack(fill="x")

        guidance_inner = ctk.CTkFrame(guidance_box, fg_color="transparent")
        guidance_inner.pack(padx=14, pady=10, fill="x")

        g_title = ctk.CTkLabel(
            guidance_inner,
            text="Immediate Guidance:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_DANGER_TEXT,
            anchor="w",
        )
        g_title.pack(anchor="w", pady=(0, 2))

        g_msg = ctk.CTkLabel(
            guidance_inner,
            text=advice_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_DANGER_TEXT,
            anchor="w",
            justify="left",
            wraplength=860,
        )
        g_msg.pack(anchor="w")

    def _render_moderate_card(self, parent: Any) -> None:
        """Renders the Moderate urgency card (amber theme)."""
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_CARD_BG,
            border_width=2,
            border_color=theme.COLOR_MODERATE_ACCENT,
            corner_radius=10,
        )
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=24, pady=20, fill="both")

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        mod_badge = ctk.CTkLabel(
            top_row,
            text="🟡  MODERATE  •  TIMELY MEDICAL REVIEW RECOMMENDED",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_MODERATE_ACCENT,
            fg_color=theme.COLOR_MODERATE_BG,
            corner_radius=6,
            padx=14,
            pady=6,
        )
        mod_badge.pack(side="left")

        if self.assessment_id:
            id_lbl = ctk.CTkLabel(
                top_row,
                text=f"Assessment #{self.assessment_id}  |  Queue: {self.status}",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=theme.COLOR_TEXT_MUTED,
            )
            id_lbl.pack(side="right")

        title_lbl = ctk.CTkLabel(
            inner,
            text="Sub-Acute Symptoms Requiring Timely Clinical Review",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        title_lbl.pack(anchor="w", pady=(0, 3))

        source = self.triage.get("source", constants.SOURCE_GEMINI)
        source_name = constants.SOURCE_DISPLAY_NAMES.get(source, "Contextual AI")
        src_lbl = ctk.CTkLabel(
            inner,
            text=f"Assessment Source: {source_name}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_PRIMARY_HOVER,
            anchor="w",
        )
        src_lbl.pack(anchor="w", pady=(0, 12))

        # Triage Reason
        reason_text = self.triage.get("reason", "Symptoms require clinical assessment in a timely manner.")
        reason_lbl = ctk.CTkLabel(
            inner,
            text=f"Triage Reason: {reason_text}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
            wraplength=880,
            justify="left",
        )
        reason_lbl.pack(anchor="w", pady=(0, 12))

        # Guidance Box
        advice_text = self.triage.get(
            "advice",
            "Please consult with the telemedicine clinician during today's clinic schedule.",
        )
        g_box = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_MODERATE_BG,
            border_width=1,
            border_color=theme.COLOR_MODERATE_BORDER,
            corner_radius=6,
        )
        g_box.pack(fill="x")

        g_inner = ctk.CTkFrame(g_box, fg_color="transparent")
        g_inner.pack(padx=14, pady=10, fill="x")

        ctk.CTkLabel(
            g_inner,
            text="Clinical Guidance:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_MODERATE_ACCENT,
            anchor="w",
        ).pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            g_inner,
            text=advice_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
            justify="left",
            wraplength=860,
        ).pack(anchor="w")

    def _render_routine_card(self, parent: Any) -> None:
        """Renders the Routine urgency card (green theme)."""
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_CARD_BG,
            border_width=2,
            border_color=theme.COLOR_ROUTINE_ACCENT,
            corner_radius=10,
        )
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=24, pady=20, fill="both")

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        rtn_badge = ctk.CTkLabel(
            top_row,
            text="🟢  ROUTINE  •  STANDARD QUEUE ASSIGNMENT",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_ROUTINE_ACCENT,
            fg_color=theme.COLOR_ROUTINE_BG,
            corner_radius=6,
            padx=14,
            pady=6,
        )
        rtn_badge.pack(side="left")

        if self.assessment_id:
            id_lbl = ctk.CTkLabel(
                top_row,
                text=f"Assessment #{self.assessment_id}  |  Queue: {self.status}",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=theme.COLOR_TEXT_MUTED,
            )
            id_lbl.pack(side="right")

        title_lbl = ctk.CTkLabel(
            inner,
            text="Routine Non-Critical Symptoms",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        title_lbl.pack(anchor="w", pady=(0, 3))

        source = self.triage.get("source", constants.SOURCE_GEMINI)
        source_name = constants.SOURCE_DISPLAY_NAMES.get(source, "Contextual AI")
        src_lbl = ctk.CTkLabel(
            inner,
            text=f"Assessment Source: {source_name}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_PRIMARY_HOVER,
            anchor="w",
        )
        src_lbl.pack(anchor="w", pady=(0, 12))

        # Triage Reason
        reason_text = self.triage.get("reason", "Mild, non-critical presentation suitable for standard waiting queue.")
        reason_lbl = ctk.CTkLabel(
            inner,
            text=f"Triage Reason: {reason_text}",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
            wraplength=880,
            justify="left",
        )
        reason_lbl.pack(anchor="w", pady=(0, 12))

        # Guidance Box
        advice_text = self.triage.get(
            "advice",
            "Follow standard telemedicine queue. Seek prompt re-evaluation if symptoms worsen or change.",
        )
        g_box = ctk.CTkFrame(
            inner,
            fg_color=theme.COLOR_ROUTINE_BG,
            border_width=1,
            border_color=theme.COLOR_ROUTINE_BORDER,
            corner_radius=6,
        )
        g_box.pack(fill="x")

        g_inner = ctk.CTkFrame(g_box, fg_color="transparent")
        g_inner.pack(padx=14, pady=10, fill="x")

        ctk.CTkLabel(
            g_inner,
            text="Guidance & Next Steps:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_ROUTINE_ACCENT,
            anchor="w",
        ).pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            g_inner,
            text=advice_text,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
            justify="left",
            wraplength=860,
        ).pack(anchor="w")

    def _render_pending_card(self, parent: Any) -> None:
        """Renders the Further Assessment Required card when in pending state."""
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=10,
        )
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=24, pady=20, fill="both")

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        pending_badge = ctk.CTkLabel(
            top_row,
            text="🟡  Further Assessment Required",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            text_color=theme.COLOR_MODERATE_ACCENT,
            fg_color=theme.COLOR_MODERATE_BG,
            corner_radius=6,
            padx=14,
            pady=6,
        )
        pending_badge.pack(side="left")

        if self.assessment_id:
            id_lbl = ctk.CTkLabel(
                top_row,
                text=f"Assessment #{self.assessment_id}  |  Queue: {self.status}",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=theme.COLOR_TEXT_MUTED,
            )
            id_lbl.pack(side="right")

        ctk.CTkLabel(
            inner,
            text="Assessment Queued for Clinician Review",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=20, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            inner,
            text="No immediate rule-based emergency warning was detected. Case is awaiting clinical review.",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
        ).pack(anchor="w")

    # =========================================================================
    # Summary Card (Patient Demographics + Submitted Symptoms)
    # =========================================================================

    def _render_summary_card(self, parent: Any) -> None:
        """Renders demographic and intake information."""
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            corner_radius=10,
        )
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=24, pady=18, fill="both")

        lbl_section = ctk.CTkLabel(
            inner,
            text="Submitted Intake Information",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=theme.COLOR_TEXT_TITLE,
            anchor="w",
        )
        lbl_section.pack(anchor="w", pady=(0, 10))

        p_name = self.patient.get("name", "N/A")
        p_age = self.patient.get("age", "N/A")
        p_gender = self.patient.get("gender", "N/A")
        p_loc = self.patient.get("location", "N/A")

        self._add_row(inner, "Patient", f"{p_name} ({p_age} yrs, {p_gender})")
        self._add_row(inner, "Location", p_loc)

        s_desc = self.symptoms.get("description", "Not provided")
        self._add_row(inner, "Reported Symptoms", s_desc)

        dur_val = self.symptoms.get("duration_value")
        dur_unit = self.symptoms.get("duration_unit")
        dur_str = f"{dur_val} {dur_unit}" if dur_val else "Not specified"
        self._add_row(inner, "Duration", dur_str)

        sev = self.symptoms.get("severity") or "Not specified"
        self._add_row(inner, "Reported Severity", sev)

        add_info = self.symptoms.get("additional_info") or "None"
        self._add_row(inner, "Additional Information", add_info)

    def _add_row(self, parent: Any, label: str, value: str) -> None:
        """Helper to render a clean key-value row with wrap support."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)

        lbl = ctk.CTkLabel(
            row,
            text=f"{label}:",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED,
            width=160,
            anchor="nw",
        )
        lbl.pack(side="left", anchor="nw")

        val = ctk.CTkLabel(
            row,
            text=str(value),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.COLOR_TEXT_BODY,
            anchor="w",
            wraplength=700,
            justify="left",
        )
        val.pack(side="left", fill="x", expand=True)

    # =========================================================================
    # Disclaimer Box
    # =========================================================================

    def _render_disclaimer_card(self, parent: Any, is_urgent: bool) -> None:
        """Renders the required non-diagnostic safety disclaimer."""
        box = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_DANGER_BG if is_urgent else theme.COLOR_NOTICE_BG,
            border_width=1,
            border_color=theme.COLOR_DANGER_BORDER if is_urgent else theme.COLOR_NOTICE_BORDER,
            corner_radius=6,
        )
        box.pack(fill="x", pady=(0, 16))

        if is_urgent:
            msg = (
                "⚠️ Medical Safety Boundary: This is a triage priority alert, not a medical diagnosis.\n"
                "SasthoSetu is an academic decision-support prototype. Seek immediate professional medical attention for acute symptoms."
            )
            txt_color = theme.COLOR_DANGER_TEXT
        else:
            msg = (
                "ℹ️ Medical Safety Boundary: SasthoSetu is a decision-support prototype and does not provide clinical diagnoses.\n"
                "Attending physicians retain final authority over patient assessment, triage prioritization, and clinical treatment."
            )
            txt_color = theme.COLOR_NOTICE_TEXT

        ctk.CTkLabel(
            box,
            text=msg,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11, weight="bold" if is_urgent else "normal"),
            text_color=txt_color,
            justify="center",
        ).pack(padx=16, pady=8)

    # =========================================================================
    # Action Buttons
    # =========================================================================

    def _render_action_buttons(self, parent: Any) -> None:
        """Renders navigation controls: Back, Finish Assessment, Start New Assessment."""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(4, 15))

        btn_inner = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_inner.pack(anchor="center")

        btn_back = ctk.CTkButton(
            btn_inner,
            text="← Back to Symptoms",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color="transparent",
            text_color=theme.COLOR_TEXT_BODY,
            border_width=1,
            border_color=theme.COLOR_CARD_BORDER,
            hover_color=theme.COLOR_BG_MAIN,
            width=150,
            height=38,
            corner_radius=6,
            command=self.on_back_to_symptoms,
        )
        btn_back.pack(side="left", padx=8)

        btn_finish = ctk.CTkButton(
            btn_inner,
            text="✓ Finish Assessment",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_PRIMARY_TEXT,
            width=160,
            height=38,
            corner_radius=6,
            command=self.on_finish_assessment,
        )
        btn_finish.pack(side="left", padx=8)

        btn_new = ctk.CTkButton(
            btn_inner,
            text="+ Start New Assessment",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            fg_color="transparent",
            text_color=theme.COLOR_PRIMARY,
            border_width=1,
            border_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_NOTICE_BG,
            width=170,
            height=38,
            corner_radius=6,
            command=self.on_start_new_assessment,
        )
        btn_new.pack(side="left", padx=8)
