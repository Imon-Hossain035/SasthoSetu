"""Validation utility functions for SasthoSetu (Prompt 16).

Provides centralized, beginner-friendly validators for:
- Authentication forms (username, password, matching)
- Patient demographics (name, age, gender, location, phone)
- Clinical symptoms (presence, length limits, duration, severity)
- Clinician review (urgency overrides, note length, status transitions)
"""

import re
from typing import Any, Optional, Tuple
from core import constants

# Supported sex / gender choices
VALID_GENDERS = ["Male", "Female", "Other", "Prefer not to say"]

# Supported duration units
VALID_DURATION_UNITS = ["Hours", "Days", "Weeks", "Months"]

# Supported consultation statuses
VALID_STATUSES = [
    constants.STATUS_WAITING,
    constants.STATUS_IN_CONSULTATION,
    constants.STATUS_COMPLETED,
]

# Supported urgency tiers
VALID_URGENCY_TIERS = [
    constants.TIER_URGENT,
    constants.TIER_MODERATE,
    constants.TIER_ROUTINE,
]


def validate_required(value: Any, field_name: str = "Field") -> Tuple[bool, str]:
    """Validates that a field is not None and not purely whitespace."""
    if value is None:
        return False, f"Please fill in all required fields."
    if isinstance(value, str) and not value.strip():
        return False, f"Please fill in all required fields."
    return True, ""


def validate_name(name: Any) -> Tuple[bool, str]:
    """Validates patient or user full name."""
    if not name or not str(name).strip():
        return False, "Please enter the patient's name."

    clean = str(name).strip()
    if len(clean) < constants.MIN_PATIENT_NAME_LENGTH:
        return False, f"Name must be at least {constants.MIN_PATIENT_NAME_LENGTH} characters."
    if len(clean) > constants.MAX_PATIENT_NAME_LENGTH:
        return False, f"Name cannot exceed {constants.MAX_PATIENT_NAME_LENGTH} characters."

    return True, ""


def validate_age(age_val: Any) -> Tuple[bool, str, Optional[int]]:
    """Validates age value as a sensible integer between 0 and 120.

    Returns:
        (is_valid, error_message, parsed_int_or_None)
    """
    if age_val is None or str(age_val).strip() == "":
        return False, f"Please enter a valid age between {constants.MIN_PATIENT_AGE} and {constants.MAX_PATIENT_AGE}.", None

    try:
        val = int(str(age_val).strip())
        if val < constants.MIN_PATIENT_AGE or val > constants.MAX_PATIENT_AGE:
            return False, f"Please enter a valid age between {constants.MIN_PATIENT_AGE} and {constants.MAX_PATIENT_AGE}.", None
        return True, "", val
    except (ValueError, TypeError):
        return False, f"Please enter a valid age between {constants.MIN_PATIENT_AGE} and {constants.MAX_PATIENT_AGE}.", None


def validate_gender(gender: Any) -> Tuple[bool, str]:
    """Validates that selected gender is an approved option."""
    if not gender or str(gender).strip() in ("Select Gender", ""):
        return False, "Please select the patient's sex/gender."

    clean = str(gender).strip()
    if clean not in VALID_GENDERS:
        return False, "Please select a valid gender from the dropdown."

    return True, ""


def validate_location(location: Any) -> Tuple[bool, str]:
    """Validates patient district / upazila location."""
    if not location or not str(location).strip():
        return False, "Please enter the patient's location."

    clean = str(location).strip()
    if len(clean) > constants.MAX_LOCATION_LENGTH:
        return False, f"Location description cannot exceed {constants.MAX_LOCATION_LENGTH} characters."

    return True, ""


def validate_phone(phone: Optional[str]) -> Tuple[bool, str, Optional[str]]:
    """Validates Bangladesh-style phone input. Phone is optional for rural patients.

    Returns:
        (is_valid, error_message, clean_phone_or_None)
    """
    if not phone or str(phone).strip() in ("", "N/A"):
        return True, "", None

    clean = str(phone).strip()
    # Reject obviously invalid or malicious inputs
    # Allow digits, spaces, plus prefix, and hyphens (length 6 to 20)
    if not re.match(r"^\+?[0-9\s\-]{6,20}$", clean):
        return False, "Please enter a valid phone number or leave it blank.", None

    # Must contain between 6 and 15 digits
    digits_only = re.sub(r"\D", "", clean)
    if len(digits_only) < 6 or len(digits_only) > 15:
        return False, "Please enter a valid phone number or leave it blank.", None

    return True, "", clean


def validate_symptoms(
    symptoms: Any,
    max_length: int = constants.MAX_SYMPTOM_LENGTH,
) -> Tuple[bool, str]:
    """Validates that symptom description is present and within safe length limits."""
    if not symptoms or not str(symptoms).strip():
        return False, "Please describe the patient's symptoms."

    clean = str(symptoms).strip()
    if len(clean) > max_length:
        return False, "The symptom description is too long. Please provide a shorter description."

    return True, ""


def validate_duration(
    duration_val: Any, unit: Optional[str]
) -> Tuple[bool, str, Optional[float], Optional[str]]:
    """Validates symptom duration numeric value and unit if specified.

    Returns:
        (is_valid, error_message, parsed_float_or_None, parsed_unit_or_None)
    """
    if duration_val is None or str(duration_val).strip() == "":
        return True, "", None, None

    try:
        val = float(str(duration_val).strip())
        if val <= 0:
            return False, "Please enter a valid symptom duration.", None, None
        if val > 365:
            return False, "Please enter a valid symptom duration (maximum 365).", None, None

        clean_unit = str(unit).strip().capitalize() if unit else "Days"
        if clean_unit not in VALID_DURATION_UNITS:
            return False, "Please select a valid duration unit.", None, None

        return True, "", val, clean_unit
    except (ValueError, TypeError):
        return False, "Please enter a valid symptom duration.", None, None


def validate_urgency(urgency: Any) -> Tuple[bool, str]:
    """Validates triage urgency tier."""
    if not urgency:
        return False, "Triage urgency is required."

    clean = str(urgency).strip().upper()
    if clean not in VALID_URGENCY_TIERS and clean != constants.OVERRIDE_USE_AUTOMATED.upper():
        return False, "Invalid urgency tier."

    return True, ""


def validate_status(status: Any) -> Tuple[bool, str]:
    """Validates patient consultation status."""
    if not status:
        return False, "Consultation status is required."

    clean = str(status).strip()
    if clean not in VALID_STATUSES:
        return False, "Invalid consultation status."

    return True, ""


def validate_status_transition(current_status: str, new_status: str) -> Tuple[bool, str]:
    """Prevents invalid workflow transitions (e.g. accidentally reopening Completed cases)."""
    curr = str(current_status).strip()
    new_s = str(new_status).strip()

    if curr == constants.STATUS_COMPLETED and new_s != constants.STATUS_COMPLETED:
        return False, "This consultation has already been completed."

    return True, ""


def validate_clinician_notes(
    notes: Optional[str],
    max_length: int = constants.MAX_CLINICIAN_NOTES_LENGTH,
) -> Tuple[bool, str]:
    """Validates clinician review notes length."""
    if not notes or not str(notes).strip():
        return True, ""

    clean = str(notes).strip()
    if len(clean) > max_length:
        return False, f"Clinician notes cannot exceed {max_length} characters."

    return True, ""


def validate_username(username: Any) -> Tuple[bool, str]:
    """Validates username for authentication."""
    if not username or not str(username).strip():
        return False, "Please enter a username or email."

    clean = str(username).strip()
    if len(clean) < 3:
        return False, "Username must be at least 3 characters long."
    if len(clean) > 80:
        return False, "Username cannot exceed 80 characters."

    return True, ""


def validate_password(password: Any, min_length: int = constants.MIN_PASSWORD_LENGTH) -> Tuple[bool, str]:
    """Validates password length and format."""
    if not password or not str(password).strip():
        return False, "Please enter a password."

    clean = str(password).strip()
    if len(clean) < min_length:
        return False, f"Password must be at least {min_length} characters long."

    return True, ""


def validate_password_match(password: str, confirm_password: str) -> Tuple[bool, str]:
    """Validates that password confirmation matches."""
    if password != confirm_password:
        return False, "Passwords do not match."
    return True, ""
