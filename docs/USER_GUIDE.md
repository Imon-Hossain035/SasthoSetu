# SasthoSetu (স্বাস্থ্যসেতু) — End-User & Demonstration Guide

> **A Step-by-Step Practical Guide for Academic Evaluators, Telemedicine Clinicians, and Community Health Workers.**

---

## ⚠️ Medical Safety Reminder
**SasthoSetu is an academic clinical decision-support and queue management prototype.**  
It assists in organizing patient lists by urgency. It does not replace physical examination, does not provide clinical diagnoses, and does not prescribe medications. Attending clinicians maintain ultimate authority.

---

## 1. Quick Start: Launching the Application

### Option A: Running the Standalone Executable (Recommended for Demonstrations)
No Python, terminal commands, or development tools are needed:
1. Locate the `SasthoSetu_Release/` folder (or `dist/`).
2. Double-click **`SasthoSetu.exe`**.
3. The desktop window (`1000x650`) will appear centered on your screen.

### Option B: Running from Source Code (For Developers)
1. Open PowerShell or Command Prompt in the project root directory.
2. Activate your Python virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Run the application:
   ```powershell
   python main.py
   ```

---

## 2. User Accounts & Login

When the application opens, you are presented with the **Welcome Screen**. Click **Get Started** to open the **Login Screen**.

### 2.1 Default Demo Credentials
For testing and evaluation, SasthoSetu initializes with pre-configured demo credentials:

| Role | Username | Password | Intended Workflow |
|---|---|---|---|
| **Clinician / Telemedicine Doctor** | `demo@sasthosetu.org` | `password123` | Patient queue, clinical reviews, priority overrides, and consultation status |
| **Patient / Community Health Worker** | `testuser` | `password123` | Intake desk, patient demographics registration, and symptom evaluation |

### 2.2 Registering a New Account
If you wish to create a custom account:
1. On the Login Screen, click **Register here**.
2. Enter your Full Name, unique Username, and Password (minimum 4 characters).
3. Confirm your password and click **Create Account**.
4. Log in with your new credentials.

---

## 3. Role Selection

After logging in, SasthoSetu presents the **Role Selection** portal:
- **Patient / Health Worker Card:** Select this to register incoming patients and submit triage symptom assessments.
- **Clinician Card:** Select this to open the doctor's prioritized queue dashboard.

> 🔒 **Role Guard:** You can switch roles at any time using the **Switch Role** button in the header bar. Non-clinician accounts are automatically blocked from accessing clinical dashboards.

---

## 4. Patient Intake & Triage Workflow (Health Worker)

### Step 1: Open Assessment
From the **Patient / Health Worker Home**, click **Start Assessment**.

### Step 2: Patient Demographics Form
Fill in the patient's basic information:
- **Patient Full Name (\*):** e.g., `Abul Kashem` or `Rokeya Begum`.
- **Age (\*):** Integer between `0` and `120`.
- **Sex / Gender (\*):** Select `Male`, `Female`, `Other`, or `Prefer not to say`.
- **District / Upazila (\*):** e.g., `Rangpur, Pirgachha` or `Kurigram, Chilmari`.
- **Phone Number:** Optional 11-digit mobile number (e.g., `01712345678`).
Click **Continue ➔**.

### Step 3: Symptom Intake Form
Describe the patient's complaints:
- **Describe Your Symptoms (\*):** Enter the patient's chief complaints.  
  *Language Support:* Native English, Bengali Unicode (`বুকে প্রচণ্ড চাপ আর শ্বাসকষ্ট`), or phonetic Banglish (`buke betha khub beshi`).
- **Symptom Duration:** e.g., `2` with unit `Hours`, `Days`, `Weeks`, or `Months`.
- **Reported Severity:** Select `Mild`, `Moderate`, or `Severe`.
- **Relevant Medical Background:** Note chronic conditions (e.g., `Hypertension, Diabetes`).
Click **Run Triage Assessment ➔**.

### Step 4: Triage Result Screen
The system runs the assessment and displays the result:
- **🔴 URGENT:** An acute emergency red flag or high-severity condition was detected. The patient must receive immediate medical attention.
- **🟡 MODERATE:** Sub-acute condition requiring timely evaluation during the clinical shift.
- **🟢 ROUTINE:** Minor, self-limiting complaint that can safely wait.

Click **Finish & Return to Home** to finalize the case, or **Start Another Patient Assessment** to intake the next patient.

---

## 5. Clinician Dashboard & Patient Review Workflow

### 5.1 Dashboard Overview
Log in with clinician credentials to open the **Clinician Dashboard**:
- **Summary Metrics Cards:** Displays live counts of waiting cases:
  - `Total Waiting`
  - `🔴 Urgent`
  - `🟡 Moderate`
  - `🟢 Routine`
  - `⚪ Pending`
- **Priority Queue Explanation Banner:** Explains the triage sorting rules for observers.
- **Search & Filter Bar:**
  - Type in the search box to filter instantly by Patient Name, ID, or Location (supports English and Bengali script).
  - Filter by specific urgency tiers (`URGENT`, `MODERATE`, `ROUTINE`).
  - Filter by consultation status (`Waiting`, `In Consultation`, `Completed`).
  - Click **🔄 Refresh** at any time to re-read the database.

### 5.2 Patient Queue Table
Patients are automatically ordered by:
1. `URGENT` cases first (oldest arrival first).
2. `MODERATE` cases second (oldest arrival first).
3. `ROUTINE` cases third (oldest arrival first).

### 5.3 Conducting a Patient Review
1. Click the **Review** button on any patient row (or double-click the row).
2. The **Patient Assessment & Clinician Review** modal window opens:
   - **Patient Demographics:** Review demographics, contact, and submission timestamp.
   - **Reported Symptoms:** Inspect verbatim chief complaints and reported duration.
   - **Automated Triage Assessment:** View the system's preserved assessment source (`Deterministic Safety-Net Rule` or `Contextual AI`), clinical observations, and conservative guidance.
   - **Triage Priority Override:** If your clinical evaluation differs from the automated assessment, choose a new urgency tier from the dropdown. (A confirmation dialog will prompt you to confirm the override).
   - **Consultation Status:** Move the case from `Waiting` ➔ `In Consultation` ➔ `Completed`.
   - **Clinician Review Notes:** Enter your medical impressions, diagnostic notes, or referral instructions.
3. Click **💾 Save Review**.
4. The dashboard updates immediately: the patient's queue position shifts according to the newly assigned effective urgency, and status counters recalculate in real-time.

---

## 6. Logging Out
Click the **Logout** button in the top navigation bar at any time to securely terminate the active session, clear cached patient data, and return to the Login screen.
