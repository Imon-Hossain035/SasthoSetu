"""Triage Engine for SasthoSetu (Prompt 12 & Prompt 16).

This module coordinates the multi-layer hybrid triage architecture:
1. Layer 1: Deterministic Rule-Based Safety-Net Engine.
   - Any acute emergency red flag triggers URGENT.
   - Immutable Priority Rule: Safety-net red flags can NEVER be downgraded by Gemini.
2. Layer 2: Contextual AI Triage via Google Gemini API.
   - Evaluates remaining sub-acute and non-emergency cases.
   - Classifies into URGENT, MODERATE, or ROUTINE.
   - Implements safe fallback to URGENT if API timeout, network failure, or error occurs.
3. Resilience & Error Handling:
   - Validates inputs before processing.
   - Wraps contextual analysis in exception guards guaranteeing patient safety is never compromised.
"""

from typing import Any, Dict, Optional

from core import constants
from core.safety_rules import (
    SAFETY_NET_URGENT_ADVICE,
    check_safety_rules,
    normalize_symptoms,
)
from services import gemini_service
from utils.logger import get_logger

log = get_logger("triage")


def run_rule_based_triage(symptoms: str) -> Dict[str, Any]:
    """Runs only the deterministic safety-net check on symptom text.

    Args:
        symptoms: Free-text symptom description in English, Bangla, or Banglish.

    Returns:
        Structured evaluation dict.
    """
    safety_result = check_safety_rules(symptoms)

    if safety_result["matched"]:
        log.info(f"Safety-net rule matched: {safety_result['matched_rule_ids']}")
        return {
            "matched": True,
            "urgency": constants.TIER_URGENT,
            "is_safety_net_override": True,
            "source": constants.SOURCE_SAFETY_RULE,
            "matched_rules": safety_result["matched_rule_ids"],
            "matched_rules_detail": safety_result["matched_rules"],
            "reason": safety_result["reason"],
            "advice": safety_result["advice"] or SAFETY_NET_URGENT_ADVICE,
            "status": constants.STATUS_WAITING,
            "engine_layer": "RULE_BASED_SAFETY_NET",
        }

    return {
        "matched": False,
        "urgency": None,
        "is_safety_net_override": False,
        "source": None,
        "pending_state": constants.STATE_PENDING_CONTEXTUAL_TRIAGE,
        "matched_rules": [],
        "matched_rules_detail": [],
        "reason": "No immediate rule-based emergency warning was detected.",
        "advice": None,
        "status": constants.STATUS_WAITING,
        "engine_layer": "PENDING_CONTEXTUAL_TRIAGE",
    }


def run_triage(
    symptoms: str,
    reported_severity: Optional[str] = None,
    duration_val: Optional[float] = None,
    duration_unit: Optional[str] = None,
    additional_info: Optional[str] = None,
    patient_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Executes the complete hybrid triage pipeline (Prompt 12 & 16).

    Pipeline Logic:
    1. Input Validation.
    2. Deterministic Safety-Net Check FIRST.
       If matched -> Returns URGENT immediately. Gemini is NEVER called.
    3. Contextual Gemini AI Check SECOND (if no emergency rule matched).
       Evaluates symptoms and assigns URGENT, MODERATE, or ROUTINE.
    4. Safe Fallback Handling.
       If any error occurs, defaults safely to URGENT for clinician review.

    Args:
        symptoms: Chief complaint / symptom description.
        reported_severity: User-reported severity ('Mild', 'Moderate', 'Severe').
        duration_val: Symptom duration numeric value.
        duration_unit: 'hours', 'days', 'weeks', 'months'.
        additional_info: Prior conditions, medications, or relevant background.
        patient_data: Basic demographics (age, gender, location).

    Returns:
        Structured triage output dictionary.
    """
    clean_symptoms = str(symptoms).strip() if symptoms else ""

    # -------------------------------------------------------------------------
    # Step 1: Run Deterministic Safety-Net Engine FIRST
    # -------------------------------------------------------------------------
    text_to_scan = f"{clean_symptoms} {additional_info or ''}".strip()
    safety_result = run_rule_based_triage(text_to_scan)

    # CRITICAL SAFETY RULE: Safety-net override has highest priority
    if safety_result["matched"]:
        result = {
            "urgency": constants.TIER_URGENT,
            "reason": safety_result["reason"],
            "advice": safety_result["advice"],
            "source": constants.SOURCE_SAFETY_RULE,
            "safety_rule_matched": True,
            "is_safety_net_override": True,
            "matched_rules": safety_result["matched_rules"],
            "matched_rules_detail": safety_result["matched_rules_detail"],
            "status": constants.STATUS_WAITING,
            "engine_layer": "RULE_BASED_SAFETY_NET",
            "is_fallback": False,
        }
    else:
        # ---------------------------------------------------------------------
        # Step 2: Contextual Triage via Gemini API (No emergency rule matched)
        # ---------------------------------------------------------------------
        try:
            symptom_payload = {
                "description": clean_symptoms,
                "duration_value": duration_val,
                "duration_unit": duration_unit,
                "severity": reported_severity,
                "additional_info": additional_info,
            }

            gemini_result = gemini_service.analyze_symptoms(
                patient_data=patient_data or {},
                symptom_data=symptom_payload,
            )

            result = {
                "urgency": gemini_result.get("urgency", constants.TIER_URGENT),
                "reason": gemini_result.get("reason", "Clinician review required."),
                "advice": gemini_result.get(
                    "advice", "Please seek professional medical consultation directly."
                ),
                "source": gemini_result.get("source", constants.SOURCE_GEMINI),
                "safety_rule_matched": False,
                "is_safety_net_override": False,
                "matched_rules": [],
                "matched_rules_detail": [],
                "status": constants.STATUS_WAITING,
                "engine_layer": "GEMINI_CONTEXTUAL_TRIAGE",
                "is_fallback": gemini_result.get("is_fallback", False),
            }
        except Exception as err:
            log.error(f"Unexpected error in contextual triage execution: {err}")
            # Robust, conservative medical fallback to URGENT
            result = {
                "urgency": constants.TIER_URGENT,
                "reason": "Contextual analysis encountered an unexpected error. Triaged safely as URGENT for mandatory clinician review.",
                "advice": "Please seek direct clinical evaluation promptly.",
                "source": constants.SOURCE_FALLBACK,
                "safety_rule_matched": False,
                "is_safety_net_override": False,
                "matched_rules": [],
                "matched_rules_detail": [],
                "status": constants.STATUS_WAITING,
                "engine_layer": "SAFE_FALLBACK",
                "is_fallback": True,
            }

    # Attach intake context metadata for audit trail
    result["input_summary"] = {
        "symptoms": clean_symptoms,
        "reported_severity": reported_severity,
        "duration_val": duration_val,
        "duration_unit": duration_unit,
        "additional_info": additional_info,
        "patient": patient_data,
    }

    return result
