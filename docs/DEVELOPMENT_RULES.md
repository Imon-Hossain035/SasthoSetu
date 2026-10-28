# SasthoSetu — Development Rules

These rules govern all stages of design, code generation, and implementation for the SasthoSetu project.

---

## 1. Desktop Application Only
- SasthoSetu is exclusively a **Windows Desktop Application**.
- It must **NEVER** be converted into a web application.
- Do NOT use:
  - Flask
  - Django
  - FastAPI
  - React
  - Streamlit
  - Electron
  - Web views or HTML/CSS as the primary UI
- All UI development must use **Python with CustomTkinter**.

---

## 2. Technology Stack Integrity
The approved technology stack is:
- **Python 3**
- **CustomTkinter**
- **SQLite**
- **Gemini API**
- **Git & GitHub**
- **PyInstaller**

*Rule:* Do not introduce additional frameworks or dependencies unless there is a clear, unavoidable technical reason and explicit user approval.

---

## 3. Beginner-Friendly Code Standards
- Keep code simple, readable, and cleanly organized.
- Avoid unnecessarily complex design patterns, meta-programming, or obscure syntax.
- Use self-explanatory variable, function, and class names.
- Keep each module focused on a single responsibility.
- Add helpful, concise comments explaining why code exists.
- Avoid large monolithic files or bloated code blocks.

---

## 4. Step-by-Step Incremental Development
- Build strictly one step at a time, guided by the user's explicit prompts.
- **NEVER** jump ahead or automatically implement future roadmap steps.
- Wait for explicit user instruction before advancing to the next step.

---

## 5. Code Preservation & File Inspection
- Always inspect existing files before making edits.
- Understand the existing code and working state before adding new changes.
- Modify only the files required for the requested step.
- Preserve all working features and existing functionality.
- Do not rewrite entire files when targeted changes are sufficient.
- Check for obvious syntax and import errors after every change.

---

## 6. Clear Explanations After Each Step
After completing any step, provide an explanation covering:
1. Files and directories created or modified.
2. Purpose of each important file.
3. Commands the user needs to run.
4. Expected output and UI behavior.
5. Step-by-step instructions for testing the feature.
6. Known limitations or notes.

---

## 7. Medical Safety & Scope Boundaries
- SasthoSetu is an **academic decision-support / triage prototype**, NOT a diagnostic tool.
- The system must **never**:
  - Diagnose diseases.
  - Prescribe medicines or treatments.
  - Replace medical practitioners.
  - Claim clinical validation.
  - Present AI output as medically certain.
- Triage urgency tiers are strictly: **URGENT**, **MODERATE**, **ROUTINE**.
- The attending clinician is always the ultimate decision-maker.
- Prominent medical disclaimers must be visible on user-facing screens.

---

## 8. Hybrid Triage Logic & Safety-Net Priority
- The triage pipeline is strictly ordered:
  1. Patient / health worker enters symptom description.
  2. Deterministic rule-based safety-net check scans for emergency red flags.
  3. If a red flag is matched, the case is assigned **URGENT** immediately.
  4. If no red flag is triggered, the symptoms are evaluated by the **Gemini API** for contextual triage.
  5. The deterministic safety layer has absolute priority. The LLM must **never** downgrade a case marked URGENT by the safety net.

---

## 9. Security & API Key Protection
- **NEVER** hard-code API keys (such as Gemini API keys) in source files.
- Store secrets locally in `.env` files.
- **NEVER** commit `.env` or sensitive credentials to Git or GitHub.
- Keep `.env` strictly in `.gitignore`.

---

## 10. Scope Boundaries (No Feature Bloat)
Do not add unrequested features such as:
- Payment systems
- Live SMS / WhatsApp gateways
- Video consultation or calling
- Voice / audio recognition
- External hospital EHR integration
- Prescription generation
- Automated disease diagnosis

---

## 11. Architecture & Roadmap Stability
**Do not change the established project architecture, technology stack, or roadmap unless the user explicitly requests the change.**
