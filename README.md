# SasthoSetu (স্বাস্থ্যসেতু)

> **SasthoSetu is a Python-based Windows desktop application for AI-assisted patient triage and priority queue management in rural telemedicine settings.**

[![Target Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?logo=windows)](https://www.microsoft.com/windows)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-CustomTkinter-0D9488)](https://github.com/TomSchimansky/CustomTkinter)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)](https://www.sqlite.org/)
[![AI Integration](https://img.shields.io/badge/AI-Google%20Gemini%20API-4285F4?logo=google)](https://ai.google.dev/)
[![Project Type](https://img.shields.io/badge/Type-Academic%20Prototype-informational)](#-medical-safety-disclaimer)

---

## ⚠️ Medical Safety Disclaimer

> **IMPORTANT CLINICAL SAFETY BOUNDARY:**  
> **SasthoSetu is an academic clinical decision-support prototype. It is NOT a medical diagnostic system and does NOT replace a qualified physician or healthcare professional.**  
> - The software does **not** provide clinical diagnoses.
> - The software does **not** prescribe medications or medical treatments.
> - Automated triage classifications are strictly assistive priority estimates to help organize waiting queues.
> - The attending clinician always retains final, unquestioned authority on patient queueing, physical evaluation, and medical care.

---

## 📌 Problem Statement & Context

In rural Bangladesh, physician density is severely constrained—approximately **1.1 registered doctors per 10,000 population** in rural areas compared to 18.2 in urban metropolitan centers. While community clinics and telemedicine desks connect rural citizens to remote doctors, incoming patients are routinely queued on a strictly first-come, first-served (FIFO) basis.

Under FIFO ordering, an acutely ill patient experiencing emergency warning signs (e.g., severe dyspnea or acute chest pain) may wait hours behind individuals presenting mild, non-urgent complaints simply because they arrived later. 

**SasthoSetu (স্বাস্থ্যসেতু)** bridges this healthcare delivery gap by introducing an intelligent pre-consultation triage screening desk. It prioritizes waiting patients into structured urgency tiers so that limited clinician time is directed to life-threatening cases first.

---

## 🛠️ Technology Stack

- **Programming Language:** Python 3 (Tested on Python 3.10+)
- **Desktop UI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern, high-DPI Windows desktop interface)
- **Local Database:** SQLite3 with SHA-256 authentication and complete foreign key audit logs
- **Contextual AI Engine:** Google Gemini API (`google-genai` Python SDK)
- **Environment Management:** `python-dotenv` for local `.env` configuration
- **Version Control:** Git & GitHub
- **Application Packaging:** PyInstaller (Standalone Windows executable)

---

## ✨ Key Features

1. **Role-Based Authentication & Authorization**
   - Distinct portals for **Patient / Community Health Worker** and **Clinician / Telemedicine Doctor**.
   - SHA-256 password hashing and session-based route protection.

2. **Patient Demographics Intake**
   - Structured capture of patient full name, age (0–120), sex/gender, district/upazila, and optional contact phone.
   - Comprehensive input validation with field-level alerts.

3. **Multilingual Symptom Description**
   - Free-text intake of chief complaints supporting **English**, native **Bengali (বাংলা)**, and phonetic **Banglish**.
   - Duration value, duration unit (Hours, Days, Weeks, Months), severity scale, and relevant medical history.

4. **Deterministic Rule-Based Safety-Net Engine**
   - High-priority, deterministic safety-net screening for **10 emergency red-flag conditions**:
     - Acute Chest Pain / Suspected Cardiac Event
     - Severe Respiratory Distress / Stridor
     - Severe Uncontrolled Bleeding
     - Altered Mental State / Unconsciousness
     - Acute Stroke Symptoms (FAST criteria)
     - Severe Trauma / Major Fractures
     - Active Seizures / Convulsions
     - Anaphylaxis / Severe Allergic Reactions
     - Severe / Deep Thermal Burns
     - Acute Poisoning / Chemical Ingestion / Overdose
   - **Immutable Safety Rule:** If any red-flag rule matches, the case is immediately assigned `URGENT` and can **never** be downgraded by contextual AI.

5. **AI-Assisted Contextual Triage (Google Gemini)**
   - Sub-acute and ambiguous complaints without red flags are analyzed using Google Gemini.
   - Outputs structured, conservative triage urgency (`URGENT`, `MODERATE`, or `ROUTINE`) with clinical observations and non-diagnostic guidance.
   - **Safe Fallback:** If the network is offline or the Gemini API is unconfigured, unassessed cases automatically default to `URGENT` for mandatory clinician review.

6. **Priority-Based Patient Queue**
   - Queue is dynamically ordered by urgency tier:
     1. **URGENT** — First-In, First-Out (Oldest arrival first)
     2. **MODERATE** — First-In, First-Out (Oldest arrival first)
     3. **ROUTINE** — First-In, First-Out (Oldest arrival first)

7. **Interactive Clinician Dashboard & Clinical Review**
   - Real-time summary metric cards displaying active waiting counts by urgency tier.
   - Live search by patient name, ID, or location with support for English and Bengali script.
   - Urgency and consultation status filtering.
   - Modal inspection of complete patient demographics, original verbatim symptoms, and preserved automated triage logic.
   - Clinician review tools: Urgency Override with confirmation dialogs, clinical note logging, and status transitions (`Waiting` ➔ `In Consultation` ➔ `Completed`).

---

## 📂 Project Structure

```text
SasthoSetu/
├── main.py                     # Main application entry point and logger initialization
├── requirements.txt            # Python package dependencies
├── README.md                   # Comprehensive project documentation
├── .gitignore                  # Git ignore rules (protects .env, databases, build artifacts)
├── .env.example                # Safe environment configuration template
│
├── core/                       # Core system logic and constants
│   ├── constants.py            # System constants, urgency tiers, and status definitions
│   ├── theme.py                # Visual styling, healthcare color palette, and typography tokens
│   ├── priority_queue.py       # Urgency-tier and FIFO queue sorting algorithm
│   ├── safety_rules.py         # 10 deterministic emergency red-flag rules (English & Bangla)
│   └── triage_engine.py        # Hybrid triage controller (Safety-Net + Gemini fallback)
│
├── database/                   # SQLite persistence layer
│   ├── db.py                   # Schema initialization, CRUD operations, and audit logging
│   └── models.py               # Data models for Patient, TriageRecord, User, and AuditLog
│
├── services/                   # External services and business logic
│   ├── auth_service.py         # User registration, login verification, and session helpers
│   └── gemini_service.py       # Gemini API client, system prompts, and safe offline fallback
│
├── ui/                         # CustomTkinter graphical interface views
│   ├── app.py                  # Main window controller, persistent shell header/footer, and router
│   ├── auth_view.py            # Login and Registration cards
│   ├── role_view.py            # Role Selection portal
│   ├── patient_home_view.py    # Health Worker landing portal and triage category guides
│   ├── patient_info_view.py    # Patient demographics intake form
│   ├── symptom_intake_view.py  # Free-text symptom input with loading indicators
│   ├── triage_result_view.py   # Dedicated triage evaluation result screen
│   └── dashboard_view.py       # Clinician Dashboard, queue table, and Patient Review modal
│
├── utils/                      # Utilities and validation helpers
│   ├── validators.py           # Input sanitization and validation (demographics, symptoms, auth)
│   └── logger.py               # Privacy-conscious application logging
│
├── docs/                       # Project specifications & documentation
│   ├── SYSTEM_DOCUMENTATION.md # University-level technical specification report
│   ├── USER_GUIDE.md           # End-user operational & demonstration guide
│   ├── DEVELOPER_GUIDE.md      # Codebase walkthrough, architecture, and extension guide
│   ├── TESTING_REPORT.md       # Quality assurance verification and test report
│   ├── BUILD_GUIDE.md          # Setup, virtual environment, and PyInstaller build guide
│   ├── PROJECT_CONTEXT.md      # Problem statement, clinical context, and 22-step roadmap
│   └── DEVELOPMENT_RULES.md    # Development standards, safety boundaries, and constraints
│
└── assets/                     # Graphic resources and icons
    └── images/                 # Healthcare icons and illustrations
```

---

## 📚 Complete Project Documentation

For comprehensive technical specifications, manuals, and reports, refer to the [`docs/`](docs/) directory:

- 📖 [**System Documentation (`docs/SYSTEM_DOCUMENTATION.md`)**](docs/SYSTEM_DOCUMENTATION.md) — Comprehensive technical report, system architecture, database schema, and university project details.
- 🩺 [**User Guide (`docs/USER_GUIDE.md`)**](docs/USER_GUIDE.md) — Step-by-step walkthrough for health workers, clinicians, and academic evaluators.
- 💻 [**Developer Guide (`docs/DEVELOPER_GUIDE.md`)**](docs/DEVELOPER_GUIDE.md) — Codebase architecture, module walkthrough, and how to add new safety rules.
- 🧪 [**Testing Report (`docs/TESTING_REPORT.md`)**](docs/TESTING_REPORT.md) — Full test execution report covering 35 automated test cases, safety-net tests, and executable verification.
- 🔨 [**Build Guide (`docs/BUILD_GUIDE.md`)**](docs/BUILD_GUIDE.md) — Detailed instructions on virtual environment setup, dependencies, and PyInstaller `.exe` compilation.
- 📋 [**Project Context (`docs/PROJECT_CONTEXT.md`)**](docs/PROJECT_CONTEXT.md) — Problem statement, clinical motivation, and 22-step development roadmap.
- 🛡️ [**Development Rules (`docs/DEVELOPMENT_RULES.md`)**](docs/DEVELOPMENT_RULES.md) — Architectural invariants and medical safety guardrails.

---

## 🚀 Installation & Setup

### 1. Prerequisites
- **Windows 10 or 11** (64-bit recommended)
- **Python 3.10+** (Ensure **"Add Python to PATH"** is checked during installation)
- **Git** (for version control)

### 2. Clone the Repository
```powershell
git clone https://github.com/<YOUR_USERNAME>/SasthoSetu.git
cd SasthoSetu
```

### 3. Create a Virtual Environment
In PowerShell or Command Prompt:
```powershell
python -m venv .venv
```

Activate the virtual environment:
- **PowerShell:**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  *(Note: If PowerShell displays an execution policy error, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once).*
- **Command Prompt (CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🔑 Gemini API Configuration

SasthoSetu safely reads its Gemini API key from an environment variable or a local `.env` file.

1. Copy the provided `.env.example` template to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` in a text editor and add your Google Gemini API key:
   ```ini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

> 🔒 **Security Note:**  
> - `.env` is listed in `.gitignore` and is **never** committed to version control.  
> - **Offline / Keyless Operation:** If no Gemini API key is configured, SasthoSetu continues to operate safely: all deterministic safety-net rules still function, and any ambiguous non-emergency cases safely default to `URGENT` for clinician evaluation without crashing.

---

## ▶️ Running the Application

Ensure your virtual environment is active, then launch the application:
```powershell
python main.py
```

### Default Demo Accounts
For local testing and academic demonstration, the database initializes with two pre-configured accounts:
- **Clinician Account:** `clinician` / `doctor123`
- **Health Worker Account:** `worker` / `worker123`

You may also register new user accounts directly through the application's Registration screen.

---

## 🧪 Testing & Verification

Comprehensive test suites are included to verify functionality, validation, priority sorting, and medical safety rules:

```powershell
# Run validation and error-handling test suite (20 tests)
python test_prompt16.py

# Run comprehensive end-to-end integration test suite (15 sections)
python test_prompt17.py
```

---

## 📄 License & Academic Attribution
Developed as an academic software engineering and clinical informatics demonstration project.  
Designed specifically for rural community health clinics and telemedicine triage workflows in Bangladesh.
