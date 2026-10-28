# SasthoSetu — Project Context

## 1. Project Information
- **Project Name:** SasthoSetu
- **Project Type:** Windows Desktop Application
- **Main Purpose:** AI-assisted triage and priority queue management for rural telemedicine access in Bangladesh.

---

## 2. Problem Statement & Motivation
In rural Bangladesh, doctor availability is critically low (approximately 1.1 physicians per 10,000 population compared to 18.2 in urban areas). While government (DGHS) and commercial telemedicine channels exist, they process waiting patients on a strictly first-come, first-served (FIFO) basis. Patients experiencing critical, acute emergencies wait in the same queue behind routine, non-urgent complaints.

SasthoSetu addresses this ordering bottleneck by introducing a digital triage pre-screening desk in front of the telemedicine queue. It prioritizes patients based on urgency rather than arrival sequence.

---

## 3. Technology Stack
- **Programming Language:** Python 3
- **GUI Framework:** CustomTkinter (Modern Windows Desktop UI)
- **Local Database:** SQLite
- **AI / LLM Integration:** Google Gemini API
- **Version Control:** Git & GitHub
- **Application Packaging:** PyInstaller (Standalone Windows `.exe`)

---

## 4. Core Workflow
```
Patient / Community Health Worker
          │
          ▼
Patient Information Intake (Demographics, Contact, Location)
          │
          ▼
Symptom Description Intake (Free-text chief complaints)
          │
          ▼
Deterministic Rule-Based Safety-Net Check
(Emergency red flags: chest pain, severe dyspnea, acute bleeding, etc.)
          │
          ├──────────────────────────────────┐
          │ (Red flag detected)              │ (No red flag detected)
          ▼                                  ▼
Urgency: URGENT                   Gemini Contextual Triage Analysis
(Hard override, never downgraded)            │
          │                                  ▼
          │                       Classification Result:
          │                       URGENT / MODERATE / ROUTINE
          │                                  │
          └──────────────────┬───────────────┘
                             ▼
                  Store Case in SQLite Database
                             │
                             ▼
                     Clinician Dashboard
              (Prioritized Queue by Urgency Tier)
                             │
                             ▼
                 Physician Review & Consultation
```

---

## 5. Important Medical Safety Boundaries
SasthoSetu is an **academic decision-support prototype**, NOT a clinical diagnostic system.

Strict rules:
1. **No Diagnosis:** The system must never name, infer, or confirm disease diagnoses.
2. **No Prescription:** The system must never suggest medication, drug dosages, or medical therapies.
3. **No Doctor Replacement:** The tool assists health workers and physicians; it does not replace professional clinical evaluation.
4. **No Medical Certainty Claims:** AI-generated suggestions are probabilistic decision-support estimates.
5. **Clinician Final Authority:** The attending clinician or health worker retains full discretion to re-classify, override, and manage any patient case.
6. **Prominent Disclaimers:** All user interfaces must present visible medical disclaimers.

---

## 6. Urgency Classification Tiers
- 🔴 **URGENT:** High-risk, potentially life-threatening or acute conditions requiring immediate physician attention.
- 🟡 **MODERATE:** Sub-acute or symptomatic conditions requiring same-day clinical assessment.
- 🟢 **ROUTINE:** Minor, non-critical, or self-limiting complaints that can safely wait.

---

## 7. Fixed Development Roadmap

1. Project Setup + Basic Structure
2. Basic Desktop Window + Application Theme
3. Login / Register
4. User Roles
5. Patient Home Page
6. Patient Information Form
7. Symptom Intake Form
8. Navigation Between Pages
9. SQLite Database
10. Rule-Based Safety-Net Engine
11. Triage Result Screen
12. Gemini API Integration
13. Clinician Dashboard
14. Priority-Based Patient Sorting
15. Patient Details + Clinician Review
16. Validation + Error Handling
17. Testing + Debugging
18. Final UI Polishing
19. Git + GitHub Preparation
20. PyInstaller → Windows EXE
21. Final Documentation
22. Final University Submission Preparation

*Note: This roadmap is fixed unless the user explicitly requests a change.*
