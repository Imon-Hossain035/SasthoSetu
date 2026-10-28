# SasthoSetu (স্বাস্থ্যসেতু) — Source Setup & Build Guide

> **Complete Instructions for Setting Up the Development Environment, Running from Source, and Compiling the Standalone Windows Executable.**

---

## 1. System Prerequisites

Before starting, ensure your Windows computer meets the following requirements:
- **Operating System:** Windows 10 or Windows 11 (64-bit).
- **Python:** Python 3.10 to 3.15 (64-bit recommended).  
  *Important:* When installing Python, ensure **"Add python.exe to PATH"** is checked.
- **Git for Windows:** Download and install from [git-scm.com](https://git-scm.com/download/win).
- **Text Editor / IDE:** Visual Studio Code, PyCharm, or any standard text editor.

---

## 2. Setting Up the Development Environment

### Step 1: Open PowerShell
Open PowerShell in the project root directory:
```powershell
cd c:\Users\USER\Desktop\Project\SasthoSetu
```

### Step 2: Create a Virtual Environment
Isolate project dependencies by creating a dedicated virtual environment named `.venv`:
```powershell
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
- **In PowerShell:**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  *(Note: If PowerShell displays an execution policy error like `running scripts is disabled on this system`, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once and try again).*
- **In Command Prompt (cmd.exe):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

Once activated, your command line prompt will be prefixed with `(.venv)`.

### Step 4: Install Dependencies
Install all required runtime and packaging packages:
```powershell
pip install -r requirements.txt
```

This installs:
- `customtkinter>=5.2.0` (GUI framework)
- `google-genai>=2.0.0` (Gemini API SDK)
- `python-dotenv>=1.0.0` (Environment configuration)
- `pyinstaller>=6.0.0` (Desktop application packaging)

---

## 3. Configuring the Gemini API Key

SasthoSetu reads its Gemini API key from a local `.env` file that is ignored by Git.

1. Create your `.env` file by copying the template:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` in Notepad:
   ```powershell
   notepad .env
   ```
3. Enter your Google Gemini API key:
   ```ini
   GEMINI_API_KEY=AIzaSyYourActualGeminiApiKeyHere
   ```
4. Save and close the file.

> 🔒 **Security Notice:**  
> Never commit `.env` or paste your real API key into public repositories. If no key is configured, SasthoSetu continues to operate safely in offline fallback mode.

---

## 4. Running the Application from Source

With your virtual environment active, run:
```powershell
python main.py
```

Expected Behavior:
- Application logs will initialize and display startup info in the console.
- SQLite database (`sasthosetu.db`) is automatically initialized if not already present.
- The desktop window (`1000x650`) appears centered on your screen displaying the Welcome screen.

---

## 5. Running the Verification Test Suites

Before packaging the application into an executable, execute the automated verification test suites:

```powershell
# 1. Run input validation and error handling test suite (20 tests)
python test_prompt16.py

# 2. Run end-to-end integration and medical safety suite (15 sections)
python test_prompt17.py
```

Both test suites should finish with `ALL TESTS PASSED SUCCESSFULLY!`.

---

## 6. Building the Standalone Executable (`SasthoSetu.exe`)

SasthoSetu includes a reproducible PyInstaller specification file: [`SasthoSetu.spec`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/SasthoSetu.spec).

### Build Command
Run PyInstaller using the `.spec` configuration:
```powershell
.\.venv\Scripts\pyinstaller.exe --noconfirm --clean SasthoSetu.spec
```

### What Happens During Build:
1. PyInstaller reads `SasthoSetu.spec`.
2. Packages `main.py` as the entry point.
3. Automatically bundles all CustomTkinter themes, fonts, vector rendering scripts, and JSON definitions via `collect_all("customtkinter")`.
4. Bundles `google-genai`, `dotenv`, and required Python shared libraries (`python315.dll`, `_tkinter.pyd`, `sqlite3`).
5. Disables the background command console (`console=False`) for a native desktop application experience.
6. Packages everything into a single portable binary named `SasthoSetu.exe`.

---

## 7. Locating the Output Executable

Upon build completion, the standalone executable is placed in:
```text
dist/
└── SasthoSetu.exe
```

A clean release package folder is also prepared at:
```text
SasthoSetu_Release/
├── SasthoSetu.exe
├── README.txt
└── .env.example
```

---

## 8. Testing the Packaged Executable

1. Navigate to the `SasthoSetu_Release/` directory.
2. Double-click `SasthoSetu.exe`.
3. Verify that:
   - The application opens without showing a black command console window.
   - The UI widgets and fonts render cleanly.
   - You can log in using `demo@sasthosetu.org` / `password123`.
   - `sasthosetu.db` and `sasthosetu.log` are automatically created in the release directory.
   - Closing and reopening the application preserves all entered data.

---

## 9. Troubleshooting Common Build Issues

| Issue / Symptom | Likely Cause | Solution |
|---|---|---|
| `CustomTkinter error: theme file not found` | CustomTkinter assets were omitted from the bundle | Ensure `collect_all("customtkinter")` is present in `SasthoSetu.spec` and rebuild using `--clean`. |
| Black console window opens behind app | `console=True` was configured | Set `console=False` in `SasthoSetu.spec` or pass `--windowed` to PyInstaller. |
| Changes to source code do not appear in EXE | PyInstaller used stale build caches | Run with the `--clean` flag: `pyinstaller --noconfirm --clean SasthoSetu.spec`. |
| Antivirus flags executable as false positive | UPX compression triggers heuristic scanners | Ensure `upx=False` is set in `SasthoSetu.spec`. |
| Database vanishes after closing the EXE | Database was written to temporary folder `sys._MEIPASS` | [`database/db.py`](file:///c:/Users/USER/Desktop/Project/SasthoSetu/database/db.py) uses `get_app_base_dir()` to place `sasthosetu.db` in `os.path.dirname(sys.executable)` rather than `_MEIPASS`. |
