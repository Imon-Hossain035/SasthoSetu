# SasthoSetu (স্বাস্থ্যসেতু)
## An AI-Assisted Triage System for Rural Telemedicine Access

---

### Academic Project Report & System Documentation

| Field | Detail |
|---|---|
| **Project Title** | SasthoSetu: An AI-Assisted Triage System for Rural Telemedicine Access |
| **Project Type** | Windows Desktop Application (Clinical Decision-Support Prototype) |
| **Target Platform** | Windows 10 / Windows 11 (64-bit) |
| **Student Name** | _____________________________________________ |
| **Student ID** | _____________________________________________ |
| **Department** | Department of Computer Science and Engineering |
| **University** | _____________________________________________ |
| **Course Code & Title** | CSE _______: Final Year Design Project / Capstone Project |
| **Project Supervisor** | _____________________________________________ |
| **Academic Session** | 2025–2026 |
| **Current Prototype Version** | Academic Prototype v0.20 |

---

## ⚠️ Academic & Medical Safety Disclaimer

> **CRITICAL MEDICAL SAFETY NOTICE:**  
> **SasthoSetu is an academic clinical decision-support and queue prioritization prototype. It is NOT a medical diagnostic system and does NOT replace a licensed medical practitioner.**  
> - SasthoSetu does **not** generate clinical diagnoses, disease identifications, or diagnostic certainties.
> - SasthoSetu does **not** prescribe medications, pharmaceutical compounds, or treatment plans.
> - Triage urgency ratings (🔴 URGENT, 🟡 MODERATE, 🟢 ROUTINE) are preliminary decision-support recommendations designed solely to organize patient queues.
> - The attending physician or qualified health worker retains final, unquestioned authority over all clinical decisions, urgency categorizations, and patient care workflows.

---

## 1. Executive Summary

In rural Bangladesh, patient access to specialized healthcare is severely constrained by physician shortages and geographical isolation. Community telemedicine desks have emerged to connect rural patients with remote physicians. However, virtually all deployed rural telemedicine desks process incoming patients on an unweighted, first-come, first-served (FIFO) basis. Under strict FIFO queueing, an acutely deteriorating patient experiencing emergent warning signs (e.g., myocardial infarction, severe dyspnea, acute stroke, or poisoning) waits in the same sequential order behind individuals presenting minor, self-limiting ailments simply because they arrived later.

**SasthoSetu (স্বাস্থ্যসেতু — "Health Bridge")** is a standalone Windows desktop clinical decision-support application engineered to solve this ordering bottleneck. Positioned at the rural intake desk, SasthoSetu introduces an intelligent, two-tiered triage pre-screening engine:
1. **Deterministic Rule-Based Safety-Net Engine:** Immediately screens free-text complaints against 10 critical emergency categories (English, Bengali script `বাংলা`, and phonetic Banglish) without requiring internet connectivity. Any detected red flag is immediately locked to **URGENT** priority.
2. **Contextual AI Triage (Google Gemini API):** Evaluates non-emergency, sub-acute complaints using structured, conservative clinical decision-support logic to categorize cases into **URGENT**, **MODERATE**, or **ROUTINE** tiers. If network connectivity fails or API credentials are unconfigured, cases safely default to **URGENT** for clinician review rather than risking an unassessed case waiting as routine.
3. **Priority-Based Clinician Queue:** Dynamically sorts waiting patients by Urgency Tier first (Urgent ➔ Moderate ➔ Routine) and then by Arrival Timestamp (FIFO) within each tier.
4. **Clinician Authority & Audit Logging:** Provides remote doctors with complete demographic and symptom reviews, clinical note capture, manual urgency override capabilities, and persistent SQLite audit trails.

---

## 2. Problem Statement & Motivation

### 2.1 The Healthcare Disparity in Bangladesh
According to official healthcare workforce statistics from the Directorate General of Health Services (DGHS) and the World Health Organization (WHO):
- Bangladesh faces a critical physician shortage in rural regions, where approximately **70% of the national population resides**.
- Rural physician density averages approximately **1.1 registered doctors per 10,000 population**, contrasted with **18.2 doctors per 10,000 population** in metropolitan Dhaka.
- Community Clinics (CCs) and Union Health & Family Welfare Centres (UH&FWCs) are primarily staffed by Community Health Care Providers (CHCPs) or local volunteers with limited formal clinical triage training.

### 2.2 The Telemedicine Ordering Bottleneck
Government (DGHS 16263) and NGO-operated telemedicine portals connect rural intake booths to remote physicians. However, waiting lists are uniformly managed via **FIFO (First-In, First-Out)** arrival sequence:
1. **Inability to Self-Assess:** Rural patients frequently lack medical literacy to distinguish between benign discomfort and acute physiological danger.
2. **Delayed Emergency Interventions:** A patient presenting acute chest pain who arrives at 11:30 AM will wait behind ten patients with routine fungal infections or seasonal coughs who registered at 9:00 AM. In time-sensitive conditions (ischemic stroke, myocardial infarction, acute anaphylaxis), delays of 2–4 hours often result in preventable mortality or irreversible disability.
3. **Cognitive Overload for Clinicians:** Remote telemedicine doctors are faced with unstructured, unprioritized patient lists, making it difficult to allocate sufficient time to complex cases.

SasthoSetu directly resolves this problem by implementing automated pre-screening and priority-based queue management at the point of care.

---

## 3. Implemented Scope vs. Future Work

To maintain rigorous academic honesty, the following matrix distinguishes the functionality implemented and verified in the current prototype from conceptual features identified for future research.

### 3.1 Implemented & Verified Capabilities
- [x] **Standalone Windows Desktop Application:** Native GUI built with CustomTkinter (Python 3.10+).
- [x] **Secure User Authentication:** Login and Registration with salted SHA-256 password hashing.
- [x] **Role-Based Authorization:** Separate portals and route-level protection for Health Workers and Clinicians.
- [x] **Structured Patient Demographics Intake:** Name, Age (0–120), Sex/Gender, Location (District/Upazila), and optional Phone.
- [x] **Multilingual Free-Text Symptom Intake:** Comprehensive chief complaints in English, native Bengali (`বাংলা`), and Banglish.
- [x] **Deterministic Rule-Based Safety-Net:** 10 emergency red-flag rules with keyword and co-occurrence token matching.
- [x] **Immutable Safety Rule:** Hard rule prohibiting any downstream AI system from downgrading a safety-net URGENT match.
- [x] **Google Gemini API Integration:** Contextual triage using `google-genai` SDK with strict JSON schema validation.
- [x] **Safe Offline / Failure Fallback:** Automatic escalation to URGENT upon network loss, missing API key, or invalid JSON.
- [x] **Local SQLite Persistence:** Complete relational database (`users`, `patients`, `triage_records`, `audit_logs`).
- [x] **Priority Queue Sorting Engine:** Strict ordering: Urgent FIFO ➔ Moderate FIFO ➔ Routine FIFO.
- [x] **Clinician Dashboard:** Real-time counters, instant search, urgency/status filters, and prioritized queue table.
- [x] **Patient Review & Clinician Override:** Modal review dialog, clinical note logging, manual urgency override, and consultation lifecycle (`Waiting` ➔ `In Consultation` ➔ `Completed`).
- [x] **Standalone PyInstaller Executable:** Portable `SasthoSetu.exe` operating independently of Python or VS Code.

### 3.2 Future Work / Not Implemented in Current Version
The following concepts were identified during preliminary research but are **explicitly excluded** from the current release:
- ❌ **Automated SMS Notification Gateway:** Not implemented in this version (would require GSM hardware or paid SMS API gateway).
- ❌ **Live WebRTC Audio/Video Streaming:** SasthoSetu is a triage and queue prioritization desk; video consultations are assumed to occur over external telemedicine infrastructure.
- ❌ **Direct Integration with DGHS Electronic Health Records (EHR):** National DGHS API integration is planned for future institutional pilots.
- ❌ **Cloud Distributed Multi-Clinic Synchronization:** Current architecture utilizes a self-contained local SQLite database.
- ❌ **Biometric / IoT Vital Sign Device Integration:** Automated ingestion from Bluetooth pulse oximeters or blood pressure cuffs is reserved for future hardware prototypes.
- ❌ **Native Mobile Application (Android / iOS):** The current scope is exclusively a Windows desktop application.

---

## 4. System Architecture & Component Design

SasthoSetu is designed around a modular, layered architecture adhering to the Single Responsibility Principle:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER (ui/)                        │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐   │
│   │  Auth Views  │   │  Role View   │   │  Patient Intake & Triage │   │
│   │(Login/Reg.)  │   │ (Selection)  │   │  (Demographics, Symptoms)│   │
│   └──────────────┘   └──────────────┘   └──────────────────────────┘   │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │       Clinician Dashboard & Review Modal (Queue, Override)      │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
┌────────────────────────────────────▼───────────────────────────────────┐
│                    BUSINESS & TRIAGE CORE (core/)                      │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │       Hybrid Triage Engine (Safety-Net Priority Controller)     │   │
│   └──────────────┬─────────────────────────────────┬───────────────┘   │
│                  │                                 │                   │
│   ┌──────────────▼──────────────┐   ┌──────────────▼──────────────┐   │
│   │ Deterministic Safety-Net    │   │  Priority Queue Sorter      │   │
│   │ (10 Emergency Rule Matcher) │   │ (Urgency Tiers + FIFO Logic)│   │
│   └─────────────────────────────┘   └─────────────────────────────┘   │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
┌──────────────────▼──────────────┐   ┌──────────────▼───────────────────┐
│     SERVICE LAYER (services/)   │   │    DATABASE LAYER (database/)    │
│   ┌──────────────────────────┐  │   │  ┌──────────────────────────┐    │
│   │   Gemini API Service     │  │   │  │   SQLite Schema Manager  │    │
│   │ (Contextual LLM Triage)  │  │   │  │ (users, patients, triage)│    │
│   └──────────────────────────┘  │   │  └──────────────────────────┘    │
│   ┌──────────────────────────┐  │   │  ┌──────────────────────────┐    │
│   │   Auth & Session Service │  │   │  │  Audit Logger & Reviews  │    │
│   └──────────────────────────┘  │   │  └──────────────────────────┘    │
└─────────────────────────────────┘   └──────────────────────────────────┘
```

### 4.1 Layer Breakdown
1. **Presentation Layer (`ui/`):**
   - Built entirely in CustomTkinter with responsive layouts and unified healthcare styling.
   - Operates within a single root window controller ([`ui/app.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/ui/app.py)), unmounting and mounting views to prevent memory leaks and window-management glitches.
2. **Triage Core Layer (`core/`):**
   - [`core/safety_rules.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/core/safety_rules.py): Compiles deterministic red-flag keywords, token stems, and token co-occurrence pairs across 10 critical conditions.
   - [`core/triage_engine.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/core/triage_engine.py): Directs the triage pipeline, guaranteeing that safety-net emergencies bypass AI and remain unalterable.
   - [`core/priority_queue.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/core/priority_queue.py): Implements the multi-tiered FIFO patient queue sorting logic.
3. **Services Layer (`services/`):**
   - [`services/gemini_service.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/services/gemini_service.py): Wraps Google Gemini API interactions using the official `google-genai` SDK, sanitizes prompts, and implements timeout fallbacks.
   - [`services/auth_service.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/services/auth_service.py): Coordinates user verification and registration against database hashes.
4. **Database Layer (`database/`):**
   - [`database/db.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/database/db.py): Centralized SQLite manager enforcing foreign key constraints, atomic transactions, and parameterized SQL queries.
5. **Utility Layer (`utils/`):**
   - [`utils/validators.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/utils/validators.py): Field sanitization, duration extraction, phone validation, and text bounds checking.
   - [`utils/logger.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/utils/logger.py): Privacy-conscious technical logging to local log files and console.

---

## 5. Technology Stack Specification

| Category | Component / Tool | Version / Standard | Functional Purpose |
|---|---|---|---|
| **Programming Language** | Python | 3.10 to 3.15 (64-bit) | Core backend logic, triage algorithms, and data persistence |
| **Graphical User Interface** | CustomTkinter | `>=5.2.0` | Modern, high-DPI Windows desktop interface widgets |
| **Base GUI Toolkit** | Tkinter / Tcl-Tk | Included in standard Python | Windowing primitives, event loop, and font rendering |
| **Relational Database** | SQLite3 | 3.x (Standard library) | Local persistence for patients, triage records, and audit logs |
| **Password Security** | SHA-256 (`hashlib`) | FIPS 180-4 standard | Cryptographic hashing for user authentication |
| **AI / LLM Integration** | Google Gemini API | `google-genai>=2.0.0` | Contextual symptom triage for non-emergency sub-acute cases |
| **Environment Config** | `python-dotenv` | `>=1.0.0` | Secure environment variable injection from local `.env` |
| **Packaging & Executable** | PyInstaller | `>=6.0.0` | Standalone zero-dependency Windows `.exe` generation |
| **Version Control** | Git & GitHub | Git 2.x standard | Source-code tracking, branch management, and repository sync |

---

## 6. Detailed Functional Modules

### 6.1 Authentication & Role-Based Access Control (RBAC)
SasthoSetu enforces strict boundary separation between non-clinical intake workers and authorized clinical staff:
- **Patient / Community Health Worker:** Limited to patient registration, demographic data intake, symptom collection, and viewing the immediate triage result. Cannot access the Clinician Dashboard or modify existing records.
- **Clinician / Telemedicine Doctor:** Granted access to the prioritized patient queue, complete demographic and verbatim symptom histories, automated triage observations, clinician review note authoring, urgency overrides, and consultation status updates.
- **Route-Level Guards:** [`ui/app.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/ui/app.py#L173-L220) programmatically blocks unauthorized role navigation, automatically redirecting non-clinicians with an alert if clinician endpoints are requested.

### 6.2 Deterministic Safety-Net Red-Flag Engine (Layer 1)
To prevent lethal false negatives caused by LLM hallucination, API latency, or network loss, SasthoSetu incorporates a **hard deterministic safety net**. It evaluates symptom descriptions against 10 critical conditions:

| Rule Identifier | Clinical Condition | Triggers (English, Bengali Script, Banglish) |
|---|---|---|
| `chest_pain` | Acute Myocardial Infarction / Angina | `chest pain`, `pressure in chest`, `বুকে ব্যথা`, `buke betha`, `buk batha` |
| `respiratory_distress` | Severe Dyspnea / Stridor / Asthma Attack | `cannot breathe`, `shortness of breath`, `শ্বাসকষ্ট`, `shash kosto`, `dum bondho` |
| `severe_bleeding` | Hemorrhage / Uncontrolled Bleeding | `heavy bleeding`, `blood spurting`, `প্রচুর রক্তপাত`, `roktopat`, `rokto porche` |
| `loss_of_consciousness` | Coma / Fainting / Unresponsiveness | `unconscious`, `passed out`, `fainted`, `অজ্ঞান`, `beheosh`, `ogyan` |
| `stroke_signs` | Acute Cerebrovascular Accident (FAST) | `face drooping`, `slurred speech`, `মুখ বাঁকা`, `mukh baka`, `kotha bolte pare na` |
| `severe_trauma` | Major Road Accidents / Compound Fractures | `broken bone`, `major accident`, `হাড় ভেঙে`, `har venge`, `accident` |
| `seizure` | Active Convulsions / Status Epilepticus | `seizure`, `convulsion`, `ফিট`, `খিঁচুনি`, `khichuni`, `mrigi` |
| `severe_allergic_reaction`| Systemic Anaphylaxis | `swollen throat`, `cannot swallow`, `গলা ফুলে`, `gola fule`, `allergic reaction` |
| `severe_burns` | Major / Deep Thermal & Chemical Burns | `burns on face`, `charred skin`, `পুড়ে গেছে`, `pure geche`, `severe burn` |
| `poisoning_overdose` | Toxic Ingestion / Pesticide Overdose | `swallowed pesticide`, `ingested poison`, `বিষ খেয়েছে`, `bish kheyeche`, `kitnashok` |

**The Safety Rule Invariant:** If any trigger or co-occurrence token pair matches, the case is assigned `URGENT` immediately. The Gemini API is **never** invoked to alter or downgrade this determination.

### 6.3 Contextual AI Triage Engine (Layer 2)
When no emergency red flag is triggered, the symptom description is evaluated by Google Gemini via [`services/gemini_service.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/services/gemini_service.py).
- **System Constraints:** Instructs Gemini under zero-shot prompting to act strictly as a pre-screening triage assistant.
- **Strict Prohibition:** Prohibits naming diagnoses, offering prognoses, or prescribing drugs.
- **Structured Schema:** Enforces JSON responses strictly containing:
  - `urgency`: `URGENT`, `MODERATE`, or `ROUTINE`.
  - `reason`: Conservative clinical explanation of symptom severity.
  - `advice`: Non-prescriptive, supportive guidance directing the patient to clinical consultation.
- **Fail-Safe Mechanism:** If Gemini returns invalid JSON, encounters an HTTP timeout, or is unconfigured, the triage pipeline catches the exception, logs the event, and defaults the urgency to `URGENT` with the assessment source labeled as `Safe Fallback`.

### 6.4 Priority Queue & Sorting Algorithm
The clinician's waiting list is governed by [`core/priority_queue.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/core/priority_queue.py). The sorting algorithm maps effective urgency tiers to numerical ranks:

$$\text{Rank}(\text{Urgent}) = 1, \quad \text{Rank}(\text{Moderate}) = 2, \quad \text{Rank}(\text{Routine}) = 3, \quad \text{Rank}(\text{Pending}) = 4$$

Sorting operates via a composite key:
$$\text{SortKey}(P) = \left( \text{Rank}(P.\text{effective\_urgency}), \quad P.\text{arrival\_timestamp} \right)$$

This ensures that:
1. All `URGENT` cases appear at the top of the queue, ordered from oldest to newest arrival.
2. All `MODERATE` cases follow, also ordered oldest to newest.
3. All `ROUTINE` cases wait at the end of the queue.

### 6.5 Clinician Review & Override Mechanics
SasthoSetu is built on the core principle that **the software assists, but the doctor decides**:
- When reviewing a patient, the clinician can manually change the urgency tier (e.g., re-ranking a case from `ROUTINE` to `URGENT` based on subtle clinical indicators, or downgrading an AI recommendation after inspecting the patient).
- **Audit Preservation:** The original automated triage assessment (`urgency_level`, `triage_source`, `triage_reason`) is stored immutably in SQLite. The override is saved in distinct fields (`clinician_override_urgency`, `clinician_notes`, `reviewed_by`, `reviewed_at`), ensuring an uncompromised audit trail for legal and institutional evaluation.
- **Lifecycle Protection:** Once a consultation is marked `Completed`, it cannot be reopened or edited, preventing accidental tampering with archived records.

---

## 7. Database Architecture

The application uses an embedded SQLite database (`sasthosetu.db`) with relational integrity enforced via `PRAGMA foreign_keys = ON;`.

```text
┌──────────────────────┐             ┌──────────────────────────┐
│        users         │             │         patients         │
├──────────────────────┤             ├──────────────────────────┤
│ id (PK)              │             │ id (PK)                  │
│ full_name            │             │ name                     │
│ username (UNIQUE)    │             │ age                      │
│ password_hash        │             │ gender                   │
│ role                 │             │ location                 │
│ created_at           │             │ phone                    │
└──────────┬───────────┘             │ created_at               │
           │                         └─────────────┬────────────┘
           │                                       │ 1
           │                                       │
           │                                       │ N
           │                         ┌─────────────▼────────────┐
           │                         │      triage_records      │
           │                         ├──────────────────────────┤
           │                         │ id (PK)                  │
           │                         │ patient_id (FK)          │
           │                         │ symptoms                 │
           │                         │ symptom_duration         │
           │                         │ duration_unit            │
           │                         │ reported_severity        │
           │                         │ additional_information   │
           │                         │ urgency_level            │
           │                         │ triage_reason            │
           │                         │ triage_advice            │
           │                         │ matched_rules (JSON)     │
           │                         │ triage_source            │
           │                         │ clinician_override_urg...│
           │                         │ clinician_notes          │
           │                         │ reviewed_by              │
           │                         │ reviewed_at              │
           │                         │ status                   │
           │                         │ created_at               │
           │                         └─────────────┬────────────┘
           │                                       │ 1
           │                                       │
           │ 1                                     │ N
           ▼ N                                     ▼
┌───────────────────────────────────────────────────────────────┐
│                          audit_logs                           │
├───────────────────────────────────────────────────────────────┤
│ id (PK)                                                       │
│ record_id (FK -> triage_records)                              │
│ user_id (FK -> users, nullable)                               │
│ action                                                        │
│ details                                                       │
│ created_at                                                    │
└───────────────────────────────────────────────────────────────┘
```

---

## 8. Verification & Testing Summary

During Prompts 16, 17, and 20, extensive automated and manual tests were executed to verify system stability, error handling, priority queue sorting, and standalone binary execution:

| Test Suite / Phase | Verification Scope | Cases / Checks | Result |
|---|---|---|---|
| **Input Validation (`test_prompt16.py`)** | Boundary tests on age, name, phone, symptom text length (0 to >1500 chars), password length, and mismatch guards. | 20 Automated Tests | **100% PASS** |
| **Error Handling (`test_prompt16.py`)** | Database connection losses, simulated offline Gemini API, malformed API JSON, and double-submission locking. | Included in 20 Tests | **100% PASS** |
| **Emergency Safety Net (`test_prompt17.py`)** | Deterministic trigger testing on all 10 emergency red-flag conditions across English, Bengali, and Banglish. | 10 Clinical Rules | **100% PASS** |
| **AI Immutable Safety (`test_prompt17.py`)** | Verification that a safety-net URGENT case cannot be modified or downgraded by downstream AI routines. | Regression Tests | **100% PASS** |
| **Priority Queue Sorting (`test_prompt17.py`)** | Verification of multi-tier FIFO patient queue sorting (Urgent FIFO ➔ Moderate FIFO ➔ Routine FIFO). | Queue Matrix Test | **100% PASS** |
| **Clinician Review & Override (`test_prompt17.py`)** | Override persistence, status workflow (`Waiting` ➔ `In Consultation` ➔ `Completed`), and completed lock. | Audit Cycle Test | **100% PASS** |
| **PyInstaller Executable Packaging** | Standalone binary build (`SasthoSetu.exe`), CustomTkinter asset bundling, windowed mode, and execution outside IDE. | Standalone Folder Test | **100% PASS** |

---

## 9. Recommended University Demonstration Script

To present SasthoSetu effectively during a university examination or project defense, follow this step-by-step 15-minute demonstration sequence:

1. **System Introduction & Safety Boundaries (2 mins):**
   - Introduce the project title, problem statement, and rural doctor density disparity in Bangladesh.
   - Emphasize the core safety disclaimer: decision-support and queue sorting only; non-diagnostic and non-prescriptive.
2. **Launch Standalone Application (1 min):**
   - Double-click `SasthoSetu_Release/SasthoSetu.exe` directly from Windows Explorer (demonstrating zero reliance on Python, VS Code, or command terminals).
   - Point out the clean startup and windowed GUI presentation.
3. **Health Worker Intake Desk Workflow (4 mins):**
   - Log in using the Health Worker credentials (`testuser` / `password123`).
   - Navigate to **Patient Portal ➔ Start Assessment**.
   - Input synthetic patient information: `Abul Kashem`, Age: `58`, Sex: `Male`, Location: `Pirgachha, Rangpur`.
   - In **Symptom Intake**, enter an acute emergency description: `"Severe crushing chest pain and shortness of breath since 2 hours ago"` (or in Bengali: `"বুকে প্রচণ্ড চাপ আর শ্বাসকষ্ট"`).
   - Click **Run Triage Assessment ➔**.
   - Point out the loading indicator, the instantaneous local deterministic safety-net detection, and the prominent **🔴 URGENT** result screen indicating that emergency medical escalation is required.
4. **Clinician Telemedicine Portal Workflow (5 mins):**
   - Log out of the health worker account and log in as the Clinician (`demo@sasthosetu.org` / `password123`).
   - Show the **Clinician Dashboard**: highlight the live summary counter cards showing `Total Waiting: 1` and `🔴 Urgent: 1`.
   - Point out the patient queue table: `Abul Kashem` is positioned at `#1` with an `URGENT` red badge and `Safety-Net Rule` source tag.
   - Demonstrate the multilingual search filter by typing `Rangpur` or `Abul`.
5. **Clinician Review & Override Demonstration (2 mins):**
   - Click **Review** on the patient row to open the [`PatientDetailDialog`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/ui/dashboard_view.py#L149).
   - Highlight the preserved demographic details, verbatim reported symptoms, and permanent automated triage observations.
   - Enter a clinical note: `"Advising immediate ECG and emergency oxygen support at upazila health complex."`
   - Demonstrate the status progression by advancing from `Waiting` to `In Consultation` and completing the review.
6. **Persistence & Architecture Q&A (1 min):**
   - Close the executable and reopen it to show that all patient data, reviews, and audit logs persist intact in `sasthosetu.db`.

---

## 10. Conclusion

SasthoSetu successfully demonstrates that combining deterministic safety-net rule screening with contextual large language model analysis provides an effective, reliable, and medically conservative solution for clinical queue prioritization. By preventing critically ill rural patients from waiting behind routine cases, the application directly addresses one of the most critical structural challenges in rural telemedicine delivery.
