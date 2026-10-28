"""Application constants for SasthoSetu.

Defines role identifiers, triage urgency tiers, page routes, and shared system constants.
"""

# --- Application Metadata ---
APP_VERSION = "Academic Prototype v1.0"
APP_STAGE = "Step 22 (Final University Submission Preparation)"

# Validation & Field Length Limits (Prompt 16)
MIN_PATIENT_AGE = 0
MAX_PATIENT_AGE = 120
MIN_PATIENT_NAME_LENGTH = 2
MAX_PATIENT_NAME_LENGTH = 100
MAX_LOCATION_LENGTH = 150
MAX_SYMPTOM_LENGTH = 1500
MAX_ADDITIONAL_INFO_LENGTH = 1000
MAX_CLINICIAN_NOTES_LENGTH = 2000
MIN_PASSWORD_LENGTH = 4
MAX_SEARCH_QUERY_LENGTH = 100

# --- Triage Assessment Sources (Prompt 12) ---
SOURCE_SAFETY_RULE = "safety_rule"
SOURCE_GEMINI = "gemini"
SOURCE_FALLBACK = "fallback"

SOURCE_DISPLAY_NAMES = {
    SOURCE_SAFETY_RULE: "Deterministic Safety-Net Rule",
    SOURCE_GEMINI: "Contextual AI (Gemini)",
    SOURCE_FALLBACK: "Safe Fallback (Manual Review Required)",
}

# --- User Roles ---
ROLE_PATIENT_HEALTH_WORKER = "patient_health_worker"
ROLE_CLINICIAN = "clinician"

ROLE_DISPLAY_NAMES = {
    ROLE_PATIENT_HEALTH_WORKER: "Patient / Health Worker",
    ROLE_CLINICIAN: "Clinician",
}

# --- Triage Urgency Tiers ---
TIER_URGENT = "URGENT"
TIER_MODERATE = "MODERATE"
TIER_ROUTINE = "ROUTINE"

# Intermediate evaluation states
STATE_PENDING_CONTEXTUAL_TRIAGE = "PENDING_CONTEXTUAL_TRIAGE"

# Queue / Assessment Statuses (Prompt 13 & 15)
STATUS_WAITING = "Waiting"
STATUS_IN_CONSULTATION = "In Consultation"
STATUS_COMPLETED = "Completed"
STATUS_REVIEWED = "Reviewed"  # Alias/legacy

CONSULTATION_STATUS_FLOW = [
    STATUS_WAITING,
    STATUS_IN_CONSULTATION,
    STATUS_COMPLETED,
]

# Clinician Review & Override Options (Prompt 15)
OVERRIDE_USE_AUTOMATED = "Use Automated Assessment"
CLINICIAN_OVERRIDE_OPTIONS = [
    OVERRIDE_USE_AUTOMATED,
    TIER_URGENT,
    TIER_MODERATE,
    TIER_ROUTINE,
]

# Priority Ordering Weights (Prompt 14)
# Lower integer represents higher urgency / earlier placement in the ascending queue
PRIORITY_URGENT = 1
PRIORITY_PENDING = 2
PRIORITY_MODERATE = 3
PRIORITY_ROUTINE = 4
PRIORITY_UNKNOWN = 5

PRIORITY_MAPPING = {
    TIER_URGENT: PRIORITY_URGENT,
    STATE_PENDING_CONTEXTUAL_TRIAGE: PRIORITY_PENDING,
    "PENDING": PRIORITY_PENDING,
    TIER_MODERATE: PRIORITY_MODERATE,
    TIER_ROUTINE: PRIORITY_ROUTINE,
}

TIER_DESCRIPTIONS = {
    TIER_URGENT: "Requires immediate clinician attention.",
    TIER_MODERATE: "Requires medical review in a timely manner.",
    TIER_ROUTINE: "Non-critical cases that can follow the standard queue.",
    STATE_PENDING_CONTEXTUAL_TRIAGE: "Awaiting contextual triage assessment.",
}

# --- Page Route Identifiers (Prompt 08 Navigation) ---
PAGE_WELCOME = "welcome"
PAGE_LOGIN = "login"
PAGE_REGISTER = "register"
PAGE_ROLE_SELECTION = "role_selection"
PAGE_PATIENT_HOME = "patient_home"
PAGE_PATIENT_INFO = "patient_info"
PAGE_SYMPTOM_INTAKE = "symptom_intake"
PAGE_TRIAGE_RESULT = "triage_result"
PAGE_TRIAGE_PLACEHOLDER = "triage_placeholder"  # Legacy alias retained for safety
PAGE_CLINICIAN_DASHBOARD = "clinician_dashboard"
PAGE_CLINICIAN_PLACEHOLDER = "clinician_placeholder"  # Legacy alias retained for safety
