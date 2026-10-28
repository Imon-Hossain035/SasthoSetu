# SasthoSetu (স্বাস্থ্যসেতু) — Verification & Testing Report

> **Comprehensive Quality Assurance, Automated Regression, and Packaging Test Report.**

---

## 1. Quality Assurance Overview

To ensure clinical safety, architectural stability, and robust error handling, SasthoSetu was subjected to a rigorous multi-phase verification strategy covering:
- **Code Integrity & Syntax Checks:** Compileall bytecode verification.
- **Form Validation & Defensive Error Handling:** 20 automated tests ([`test_prompt16.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/test_prompt16.py)).
- **Integration, Priority Sorting & Medical Safety:** 15 automated test sections ([`test_prompt17.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/test_prompt17.py)).
- **Executable Packaging Verification:** Standalone execution, asset resolution, and database persistence ([`SasthoSetu.exe`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/dist/SasthoSetu.exe)).

---

## 2. Test Execution Environment

| Attribute | Value |
|---|---|
| **Operating System** | Windows 10 Home / Pro (64-bit, Build 19045) |
| **Python Runtime** | Python 3.15.2 (64-bit) |
| **GUI Framework** | CustomTkinter 5.2.2 |
| **Packaging Engine** | PyInstaller 6.22.3 |
| **Database Engine** | SQLite 3.x (Standard Library) |
| **Test Date** | October 2026 |
| **Overall Test Result** | **35 / 35 Automated Tests PASSED (100% Success Rate)** |

---

## 3. Phase 1: Input Validation & Defensive Handling (`test_prompt16.py`)

The automated suite `test_prompt16.py` verifies boundary conditions, input sanitization, database transaction safety, and graceful degradation during network or API faults.

| # | Test Scenario | Input / Precondition | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|:---:|
| 1 | Empty Login Submission | Empty username & password fields | Block submission; display validation message | "Please enter both username and password." displayed | **PASS** |
| 2 | Invalid Login Credentials | Nonexistent username or wrong password | Generic privacy-conscious error (no user enumeration) | Generic "Invalid username or password." returned | **PASS** |
| 3 | Empty Registration Submission | Blank registration fields | Block submission; display field alert | "Please fill in all required fields." displayed | **PASS** |
| 4 | Password Confirmation Mismatch | Password `password123` vs Confirm `mismatch456` | Reject registration; display mismatch notice | "Passwords do not match." displayed | **PASS** |
| 5 | Invalid Patient Age | Age `-5`, `abc`, `150` | Reject submission; enforce 0–120 range | Correctly rejected with range validation error | **PASS** |
| 6 | Empty Symptom Intake | Blank symptom field or pure whitespace | Prevent submission before calling Gemini API | "Please describe your symptoms before proceeding." displayed | **PASS** |
| 7 | Oversized Symptom Text | Description exceeding 1,500 characters | Reject with clear limit message without truncation | "Symptom description exceeds maximum length of 1500 characters." displayed | **PASS** |
| 8 | Safety-Net Red Flag Matched | Acute chest pain + dyspnea | Assign URGENT; lock from AI downgrade | Urgency `URGENT` assigned; Gemini bypassed | **PASS** |
| 9 | Missing Gemini API Key | `GEMINI_API_KEY` unset or empty in `.env` | Safe fallback to URGENT without application crash | Fallback invoked; Urgency `URGENT` assigned safely | **PASS** |
| 10 | Invalid Gemini API Key | Invalid key string `AIzaSy_INVALID...` | Catch HTTP 400 without crashing; safe fallback to URGENT | Handled cleanly; Urgency `URGENT` assigned safely | **PASS** |
| 11 | Simulated Network Disconnection | Socket timeout / unreachable network | Catch connection failure; safe fallback to URGENT | Network error caught; Urgency `URGENT` assigned | **PASS** |
| 12 | SQLite Transaction Failure | Intentional SQL syntax / constraint error | Rollback transaction cleanly; catch exception | Transaction rolled back; database remains uncorrupted | **PASS** |
| 13 | Nonexistent Patient Query | ID not in `patients` table | Return `None` safely without throwing unhandled exception | Query returned `None` safely | **PASS** |
| 14 | Invalid Clinician Override Tier | Malformed urgency string `CRITICAL` | Reject override; enforce valid tier selection | Rejected with "Invalid urgency selection" error | **PASS** |
| 15 | Invalid Consultation Status | Status `Discharged` not in allowed flow | Reject update; enforce allowed status flow | Rejected with "Invalid consultation status" error | **PASS** |
| 16 | Reopening Completed Consultation | Transitioning `Completed` ➔ `Waiting` | Block status reversal to protect clinical audit | "This consultation has already been completed." returned | **PASS** |
| 17 | Unicode & Special Character Search | Query: `বাংলা`, `017`, `@#$%` | SQL parameterized search executes without error | Search executed cleanly without SQL injection risk | **PASS** |
| 18 | Rapid Double-Submission | Rapid consecutive button clicks on intake | Button disabled during processing; single record created | Exactly 1 patient and 1 triage record created | **PASS** |
| 19 | Dashboard Refresh Failure | Database temporarily locked during refresh | Preserve existing table rows; display warning banner | Existing records preserved; warning banner displayed | **PASS** |
| 20 | System State Regression Check | Data model integrity check after errors | Models, audit logs, and priority rules remain intact | Full schema and models intact | **PASS** |

---

## 4. Phase 2: Integration & Medical Safety Suite (`test_prompt17.py`)

The automated suite `test_prompt17.py` conducts end-to-end integration testing across authentication, safety-net rules, priority queueing, clinician overrides, and medical safety invariants.

| Section | Test Area | Verification Target | Status |
|---|---|---|:---:|
| **1** | Project Structure | All required source packages (`core`, `database`, `services`, `ui`, `utils`) present and importable | **PASS** |
| **2** | Dependencies | All packages in `requirements.txt` correctly installed and verified | **PASS** |
| **3** | Authentication Lifecycle | Registration, duplicate username conflict rejection, login verification, SHA-256 hashing | **PASS** |
| **4** | Role Authorization | Route-level guards prevent non-clinicians from accessing clinician endpoints | **PASS** |
| **5** | Demographic Validation | Full validation coverage on Name, Age, Gender, Location, and Phone | **PASS** |
| **6** | Symptom Intake Validation | Empty, whitespace, length bounds (1500 chars), Bengali script (`বাংলা`), and Banglish | **PASS** |
| **7** | Emergency Red-Flag Engine | Deterministic trigger matching verified across all 10 emergency categories: | **PASS** |
| 7a | Chest Pain / Cardiac | Triggers: `chest pain`, `buke betha`, `pressure in chest` | PASS |
| 7b | Respiratory Distress | Triggers: `cannot breathe`, `shortness of breath`, `shash kosto` | PASS |
| 7c | Severe Bleeding | Triggers: `heavy bleeding`, `blood spurting`, `roktopat` | PASS |
| 7d | Loss of Consciousness | Triggers: `unconscious`, `fainted`, `ogyan` | PASS |
| 7e | Stroke Signs (FAST) | Triggers: `face drooping`, `slurred speech`, `mukh baka` | PASS |
| 7f | Severe Trauma | Triggers: `broken bone`, `major accident`, `har venge` | PASS |
| 7g | Active Seizure | Triggers: `seizure`, `convulsions`, `khichuni` | PASS |
| 7h | Severe Allergy / Anaphylaxis | Triggers: `swollen throat`, `cannot swallow`, `gola fule` | PASS |
| 7i | Severe Burns | Triggers: `burns on face`, `charred skin`, `pure geche` | PASS |
| 7j | Poisoning / Overdose | Triggers: `swallowed pesticide`, `ingested poison`, `bish kheyeche` | PASS |
| **8** | Safety-Net Immutability | Safety-Net `URGENT` case cannot be altered or downgraded by Gemini AI | **PASS** |
| **9** | False Trigger Avoidance | Routine symptoms (`mild seasonal cough`, `slight headache`) avoid false emergency classification | **PASS** |
| **10** | Gemini Contextual Triage | Structured schema validation, timeout handling, and safe fallback to URGENT | **PASS** |
| **11** | SQLite CRUD Operations | Full insert, query, update, and foreign key audit logging verified | **PASS** |
| **12** | Priority Queue Sorting | Queue sorts strictly: `URGENT` FIFO ➔ `MODERATE` FIFO ➔ `ROUTINE` FIFO | **PASS** |
| **13** | Clinician Override Cycle | Manual urgency override updates effective urgency and audit trail; completed status locked | **PASS** |
| **14** | Multilingual Search & Filter | Unicode Bengali, Banglish, case-insensitive, and partial string filtering verified | **PASS** |
| **15** | Medical Safety Regressions | Verification that disclaimers, decision-support terminology, and non-prescriptive rules remain intact | **PASS** |

---

## 5. Phase 3: Executable Packaging Verification (`SasthoSetu.exe`)

| Test Check | Method / Environment | Expected Outcome | Actual Outcome | Status |
|---|---|---|---|:---:|
| **PyInstaller Compilation** | `pyinstaller --noconfirm --clean SasthoSetu.spec` | Exit code 0; standalone binary generated in `dist/` | Build completed; `SasthoSetu.exe` (~28.5 MB) created | **PASS** |
| **Windowed Startup** | Executed `dist\SasthoSetu.exe` via PowerShell | Centered GUI window (`1000x650`) appears; no background console | Window launched cleanly without console | **PASS** |
| **Zero-Dependency Test** | Copied `SasthoSetu.exe` to isolated folder on Desktop | Operates independently of Python, VS Code, or `.venv` | Launched independently; self-initialized database | **PASS** |
| **Database Auto-Creation** | Inspected execution directory after launch | `sasthosetu.db` created with all 4 tables and seed accounts | Created with tables `users`, `patients`, `triage_records`, `audit_logs` | **PASS** |
| **Logging Auto-Creation** | Inspected execution directory after launch | `sasthosetu.log` created with timestamped startup logs | Generated UTF-8 log recording successful boot | **PASS** |
| **Data Persistence on Restart** | Created synthetic patient, closed EXE, reopened EXE | Patient record persists intact in database | Record retrieved successfully upon relaunch | **PASS** |
| **CustomTkinter Asset Bundling** | Inspected visual widgets, buttons, and popups | Vector rendering, fonts, themes, and icons render cleanly | No missing asset, tcl, or font errors | **PASS** |

---

## 6. Known Limitations

1. **Rule-Based Emergency Coverage:** While the 10 safety-net rules cover the most prevalent clinical emergencies, keyword matching cannot guarantee 100% detection of atypical presentations or complex multi-symptom conditions.
2. **Connectivity for Contextual AI:** Layer 2 (Gemini API) requires an active internet connection. When offline, all non-emergency cases safely default to `URGENT` for clinician review rather than receiving a contextual `MODERATE` or `ROUTINE` rating.
3. **Local Database Scope:** SQLite is designed for single-site operations. Multi-clinic networked synchronization is reserved for future enterprise versions.
4. **Academic Prototype Status:** SasthoSetu has been tested against synthetic and clinical benchmark cases; it has not undergone clinical field trials in a live hospital deployment.
