# SasthoSetu (স্বাস্থ্যসেতু) — Developer & Contributor Guide

> **Technical Architecture, Codebase Walkthrough, and Extension Manual for Software Engineers.**

---

## 1. Architectural Philosophy & Design Principles

SasthoSetu is engineered to be **reliable, maintainable, beginner-friendly, and strictly medically conservative**:
1. **Desktop Native (No Web Frameworks):** Implemented purely with CustomTkinter and Python 3. No local HTTP servers (Flask, FastAPI, Django) or Electron overhead.
2. **Deterministic Priority Over AI:** The rule-based safety net always has higher priority than the contextual LLM. An AI model can never override or downgrade an emergency red flag.
3. **Fail-Safe Design:** If an external dependency fails (network disconnect, invalid API response, missing environment key), the system safely defaults to `URGENT` for human clinician evaluation rather than failing silently or assuming the case is routine.
4. **Permanent Audit Preservation:** Automated triage recommendations and clinician overrides are recorded in separate database columns to ensure full legal and clinical auditability.
5. **Zero-Dependency Portable Distribution:** All filesystem paths automatically resolve relative to the executable (`sys.frozen`) or project root, ensuring that packaging via PyInstaller produces zero runtime errors.

---

## 2. Directory Structure & Module Breakdown

```text
SasthoSetu/
├── main.py                     # Application entry point and top-level exception handler
├── requirements.txt            # Python runtime dependencies
├── SasthoSetu.spec             # PyInstaller build specification
├── README.md                   # Repository overview & setup guide
├── .gitignore                  # Git tracking exclusion rules
├── .env.example                # Safe environment variable configuration template
│
├── core/                       # Core business logic and shared constants
│   ├── constants.py            # Enumerations, limits, urgency tiers, and status codes
│   ├── theme.py                # Visual design tokens, color palette, typography hierarchy
│   ├── safety_rules.py         # 10 deterministic emergency red-flag rules (English & Bengali)
│   ├── triage_engine.py        # Central hybrid triage coordinator
│   └── priority_queue.py       # Multi-tiered FIFO queue sorting algorithm
│
├── database/                   # Data persistence and SQLite operations
│   ├── db.py                   # Connection manager, schema migrations, CRUD, and audit logging
│   └── models.py               # Data class models (Patient, TriageRecord, User, AuditLog)
│
├── services/                   # External integrations and business services
│   ├── auth_service.py         # User registration, credential hashing, and authentication
│   └── gemini_service.py       # Google Gemini API integration and offline fallbacks
│
├── ui/                         # CustomTkinter graphical presentation layer
│   ├── app.py                  # Main window controller, persistent shell header/footer, and router
│   ├── auth_view.py            # Login and Registration views
│   ├── role_view.py            # Role Selection portal view
│   ├── patient_home_view.py    # Health Worker landing portal view
│   ├── patient_info_view.py    # Patient demographics intake form view
│   ├── symptom_intake_view.py  # Chief complaints intake form with loading spinner
│   ├── triage_result_view.py   # Dedicated triage assessment outcome view
│   └── dashboard_view.py       # Clinician queue table, filters, and Patient Review dialog
│
├── utils/                      # Shared helper utilities
│   ├── validators.py           # Sanitization and validation rules (names, age, symptoms)
│   └── logger.py               # Privacy-conscious application logger
│
├── docs/                       # Comprehensive project documentation
│   ├── SYSTEM_DOCUMENTATION.md # University-level technical specification
│   ├── USER_GUIDE.md           # End-user operational manual
│   ├── DEVELOPER_GUIDE.md      # This guide
│   ├── TESTING_REPORT.md       # QA verification and test suite results
│   ├── BUILD_GUIDE.md          # Packaging and executable creation instructions
│   ├── PROJECT_CONTEXT.md      # Background context and roadmap
│   └── DEVELOPMENT_RULES.md    # Development constraints and safety rules
│
└── assets/                     # Media resources and icons
    └── images/                 # Healthcare icons and illustrations
```

---

## 3. Key Subsystems & Implementation Details

### 3.1 Main Application Router (`ui/app.py`)
SasthoSetu avoids multi-window confusion by operating as a **Single-Window Application**:
- [`SasthoSetuApp`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/ui/app.py#L31) inherits from `ctk.CTk`.
- The top header (`_create_header()`) and bottom disclaimer (`_create_footer()`) remain permanently mounted.
- Dynamic pages are loaded into `self.main_container` via `show_page(page_name, **kwargs)`.
- When switching pages, `_clear_main_container()` destroys existing child widgets to free memory before instantiating the new view.

### 3.2 Hybrid Triage Pipeline (`core/triage_engine.py`)
```python
def run_triage(symptoms, reported_severity, duration_val, duration_unit, additional_info, patient_data):
    # Step 1: Deterministic Safety-Net Check
    is_emergency, matched_rules, rule_reasons = safety_rules.evaluate_symptoms(symptoms)
    
    if is_emergency:
        # Emergency Red Flag detected!
        # Do NOT call Gemini. Hard-lock to URGENT.
        return {
            "urgency": "URGENT",
            "source": "safety_rule",
            "matched_rules": matched_rules,
            "safety_rule_matched": True,
            ...
        }
    
    # Step 2: Contextual AI Triage (Gemini)
    # Only invoked if NO emergency red flag was detected
    return gemini_service.evaluate_contextual_triage(...)
```

### 3.3 Adding a New Emergency Safety-Net Rule
To introduce an additional emergency condition:
1. Open [`core/safety_rules.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/core/safety_rules.py).
2. Add a new dictionary entry to `EMERGENCY_RULES`:
   ```python
   "new_condition_id": {
       "name": "Human-Readable Condition Name",
       "reason": "Conservative clinical rationale explaining the emergency risk.",
       "advice": "Seek immediate professional medical care.",
       "keywords": [
           "english trigger 1", "english trigger 2",
           "বাংলা ট্রিগার", "banglish trigger"
       ],
       "co_occurrence_pairs": [
           (["trigger_a1", "trigger_a2"], ["trigger_b1", "trigger_b2"])
       ]
   }
   ```
3. Run the automated test suite (`python test_prompt17.py`) to confirm zero regressions.

### 3.4 Priority Queue Sorting (`core/priority_queue.py`)
Queue sorting is implemented via Python's standard `sorted()` with a composite tuple key:
```python
def sort_patients_by_priority(records):
    def sort_key(record):
        # 1. Effective urgency tier (Urgent=1, Moderate=2, Routine=3, Pending=4)
        urgency = get_effective_urgency(record)
        tier_rank = URGENCY_TIER_PRIORITY.get(urgency, 4)
        
        # 2. Arrival timestamp (FIFO tie-breaker)
        arrival = record.get("created_at") or "9999-99-99"
        
        return (tier_rank, arrival)

    return sorted(records, key=sort_key)
```

---

## 4. Coding Standards & Conventions

- **Type Annotations:** All functions and methods must use Python standard type hints (`typing.Optional`, `typing.Dict`, `typing.List`, `typing.Tuple`, `typing.Any`).
- **Docstrings:** Follow Google-style or PEP 257 docstrings for all modules, classes, and public functions.
- **Error Handling:** Avoid bare `except:`. Always catch specific exceptions (`sqlite3.Error`, `ValueError`, `json.JSONDecodeError`) or log unexpected exceptions before graceful fallback.
- **Privacy Standards:** **Never** write patient names, symptoms, passwords, or API keys into debug logs or console outputs. Log only record IDs, error classifications, and component timestamps.
- **Path Resolution:** Always construct filesystem paths through `get_app_base_dir()` in [`database/db.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/database/db.py) and [`utils/logger.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/utils/logger.py) to support both source execution and PyInstaller bundled execution.

---

## 5. Development Verification Workflow

Before committing any modifications:
1. **Syntax Check:**
   ```powershell
   python -m compileall .
   ```
2. **Automated Validation & Error Handling Suite:**
   ```powershell
   python test_prompt16.py
   ```
3. **End-to-End Triage & Medical Safety Suite:**
   ```powershell
   python test_prompt17.py
   ```
4. **GUI Launch Check:**
   ```powershell
   python main.py
   ```
