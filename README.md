# AuriShift — Nurse Shift Companion

A visual student prototype based on the night-shift workload described by a government-hospital staff nurse. It brings a fictional patient queue, delivery tally, doctor follow-up log, AI drafting tools, and shift handoff into one demo interface.

## Features

- **Overview:** shift totals, patient-per-staff context, latest activity, and follow-up board.
- **Patient queue:** add fictional IDs, track workflow status, search, and filter by case type.
- **Delivery tally:** record delivery episodes and newborn counts.
- **Doctor follow-ups:** log a contact status and reason; the app does not call or message anyone.
- **AI note draft:** format supplied fictional text as an editable handoff note. It is instructed not to diagnose, triage, infer missing facts, or recommend treatment.
- **AI shift overview:** turn aggregate counts into a short draft without sending patient IDs or note text.
- **Handoff:** review totals and download a text summary.
- **Portfolio-ready visuals:** responsive dark navy and teal dashboard, with synthetic `DEMO` records loaded on startup.

## Run in Visual Studio Code

See [START_HERE.md](START_HERE.md) for beginner setup and the three-day plan. The short version:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Optional AI setup

The AI tools use the OpenAI Python SDK and Responses API. Set `OPENAI_API_KEY` in a local `.env` file; `.gitignore` excludes it from source control. Set `OPENAI_MODEL` to a model available to your account, if needed. The app remains usable without AI.

When an AI button is clicked, entered fictional note text or aggregate shift counts are sent to the OpenAI API. Calls use `store=False` to disable storage of generated responses for later API retrieval. This does not mean the request stays on the user's computer. Never use real patient or hospital information. The generated output is an editable draft and must be reviewed.

## Safety and scope

This is an educational prototype, not an approved clinical system. It does not diagnose, triage, recommend treatment, determine delivery mode, contact clinicians, or replace official hospital records. Any evaluation in a health facility would require appropriate clinical, privacy, security, and institutional review.

