# Start Here — AuriShift

## 1. Open the correct folder

In VS Code, choose **File → Open Folder** and open the `AuriShift` folder containing `app.py`. Do not open `.venv` as the project folder.

## 2. Check Python

In the VS Code terminal, run:

```powershell
python --version
```

If it prints a version such as `Python 3.12.x`, continue. If it says Python cannot be found, install Python from [python.org](https://www.python.org/downloads/windows/), select **Add python.exe to PATH** during setup, then close and reopen VS Code.

## 3. Create the Python environment

Choose **Terminal → New Terminal** and run these commands one at a time:

```powershell
python -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, switch the VS Code terminal to Command Prompt and run `.venv\Scripts\activate.bat`.

## 4. Install packages

```powershell
python -m pip install -r requirements.txt
```

## 5. Start the app

```powershell
python -m streamlit run app.py
```

Open the **Local URL** shown in the terminal. You should see six tabs: Overview, Patient queue, Delivery tally, Doctor follow-ups, AI assistant, and Handoff.

## 6. Optional: turn on AI

The app works without AI. To enable the AI note and handoff drafts:

1. Get an OpenAI API key from your OpenAI API account. API use may incur charges depending on your account and usage.
2. In VS Code, make a copy of `.env.example` in the project folder and name the copy `.env`.
3. In `.env`, replace `put_your_key_here` with your key. Never paste the key into `app.py`, a screenshot, GitHub, or LinkedIn.
4. Stop and restart the app. The AI assistant tab should now allow draft generation.

When you click an AI draft button, the entered fictional note or aggregate shift counts are sent to the OpenAI API. The app requests `store=False`, which disables storage of the generated response for later API retrieval; it does not prevent transmission to the API. Use made-up examples only, never real patient details. Review every draft before use.

## Three-day beginner plan

- **Day 1:** Open the folder, install packages, run the app, and explore the patient queue, delivery tally, contact log, and handoff with the included `DEMO` examples.
- **Day 2:** Set up the optional API key if you have one. Try the AI note draft and AI shift overview with fictional text, then review and edit the outputs. If you do not have a key, complete the rest of the app and leave AI disabled.
- **Day 3:** Take screenshots with only the sample `DEMO` data, review the README and `.gitignore`, then publish the source files to GitHub. Do not upload `.env` or real health data.

This is a student prototype, not a clinical system. It does not triage, diagnose, recommend treatment, decide delivery mode, place calls, or replace official records.


