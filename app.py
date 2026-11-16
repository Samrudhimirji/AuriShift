import os
import streamlit as st
from datetime import date, datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="AuriShift | Nurse Shift Companion",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

PATIENT_TYPES = ["Maternity", "Accident", "Poisoning", "Alcohol-related", "Other"]
PATIENT_STATUSES = ["Waiting", "Under care", "For doctor review", "Transferred", "Discharged"]
CONTACT_STATUSES = ["Not contacted", "Contact attempted", "Reached", "Follow-up pending"]

SAMPLE_PATIENTS = [
    {"Demo ID": "DEMO-104", "Case type": "Maternity", "Arrival": "21:18", "Status": "Under care"},
    {"Demo ID": "DEMO-105", "Case type": "Accident", "Arrival": "21:42", "Status": "For doctor review"},
    {"Demo ID": "DEMO-106", "Case type": "Poisoning", "Arrival": "22:07", "Status": "Waiting"},
    {"Demo ID": "DEMO-107", "Case type": "Maternity", "Arrival": "22:31", "Status": "Under care"},
    {"Demo ID": "DEMO-108", "Case type": "Other", "Arrival": "23:05", "Status": "Waiting"},
    {"Demo ID": "DEMO-109", "Case type": "Alcohol-related", "Arrival": "23:26", "Status": "For doctor review"},
]
SAMPLE_DELIVERIES = [
    {"Demo mother ID": "DEMO-M21", "Boys": 1, "Girls": 0, "Not recorded": 0, "Time": "21:54"},
    {"Demo mother ID": "DEMO-M22", "Boys": 0, "Girls": 1, "Not recorded": 0, "Time": "22:46"},
    {"Demo mother ID": "DEMO-M23", "Boys": 1, "Girls": 1, "Not recorded": 0, "Time": "23:38"},
]
SAMPLE_CONTACTS = [
    {"Demo patient ID": "DEMO-105", "On-call role": "On-call doctor", "Reason": "Review requested", "Status": "Contact attempted", "Time": "21:49"},
    {"Demo patient ID": "DEMO-109", "On-call role": "On-call doctor", "Reason": "Update requested", "Status": "Follow-up pending", "Time": "23:32"},
]

for key, sample in (
    ("patients", SAMPLE_PATIENTS),
    ("deliveries", SAMPLE_DELIVERIES),
    ("contacts", SAMPLE_CONTACTS),
):
    if key not in st.session_state:
        st.session_state[key] = [dict(item) for item in sample]
if "staff_count" not in st.session_state:
    st.session_state.staff_count = 3
if "shift_date" not in st.session_state:
    st.session_state.shift_date = date.today()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --aqua:#63e2cf; --blue:#77aaff; --coral:#ff9e83; --ink:#edf6f6; --muted:#a7bdc4; }
.stApp { background: radial-gradient(ellipse at 12% 0%, #183b47 0%, #111f2b 38%, #0b121c 100%); color:var(--ink); font-family:'DM Sans',sans-serif; }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:1280px; padding-top:1.6rem; padding-bottom:3rem; }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#142a36,#101923); border-right:1px solid rgba(133,199,203,.16); }
.hero { position:relative; overflow:hidden; padding:1.65rem 1.8rem; margin-bottom:1rem; border:1px solid rgba(109,227,209,.23); border-radius:24px; background:linear-gradient(112deg,rgba(36,99,103,.55),rgba(22,45,61,.78)); box-shadow:0 22px 56px rgba(0,0,0,.22); }
.hero:after { content:'✧'; position:absolute; right:5%; top:-52px; font-size:190px; line-height:1; color:rgba(108,231,212,.08); }
.hero-kicker { color:var(--aqua); font-size:.75rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.45rem; }
.hero h1 { color:#f4fbfb; font-family:'Manrope',sans-serif; font-size:clamp(2rem,4vw,3rem); font-weight:800; letter-spacing:-.045em; margin:0; }
.hero p { color:#bfd1d3; margin:.55rem 0 0; font-size:1rem; }
.section-note { color:var(--muted); margin-top:-.5rem; margin-bottom:1.3rem; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(33,62,74,.94),rgba(19,37,51,.94)); border:1px solid rgba(132,199,202,.17); border-top:2px solid rgba(99,226,207,.72); padding:1rem 1.05rem; border-radius:17px; box-shadow:0 11px 30px rgba(0,0,0,.16); min-height:108px; }
div[data-testid="stMetricLabel"] { color:#afc4c7; font-weight:600; }
div[data-testid="stMetricValue"] { color:#f2fbfa; font-family:'Manrope',sans-serif; }
.stTabs [data-baseweb="tab-list"] { gap:.45rem; border-bottom:1px solid rgba(170,210,211,.17); }
.stTabs [data-baseweb="tab"] { height:3.15rem; padding:0 1rem; color:#b4c8cb; border-radius:12px 12px 0 0; font-weight:600; }
.stTabs [aria-selected="true"] { color:var(--aqua)!important; background:rgba(78,171,161,.13); }
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button { border-radius:11px; border:1px solid rgba(112,225,208,.36); background:linear-gradient(135deg,#218f88,#1c7182); color:white; font-weight:700; padding:.58rem 1rem; transition:transform .15s ease,filter .15s ease; }
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover { filter:brightness(1.12); transform:translateY(-1px); border-color:var(--aqua); color:white; }
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div { border-radius:10px!important; }
[data-testid="stDataFrame"] { border:1px solid rgba(137,197,198,.18); border-radius:13px; overflow:hidden; }
div[data-testid="stAlert"] { border-radius:12px; }
hr { border-color:rgba(170,210,211,.16); }
.small-muted { color:#8faab0; font-size:.82rem; }
.brand-mark { display:inline-grid; width:32px; height:32px; place-items:center; margin-right:8px; border-radius:10px; color:#0e2530; background:linear-gradient(135deg,#8af0db,#a4c5ff); font-weight:800; }
.soft-banner { padding:.7rem .9rem; border-radius:12px; background:rgba(99,226,207,.08); border:1px solid rgba(99,226,207,.16); color:#b7d2d3; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div><span class="brand-mark">A</span><strong style="font-size:1.15rem">AuriShift</strong></div>', unsafe_allow_html=True)
    st.caption("Nurse shift companion")
    st.divider()
    st.markdown("### Shift setup")
    st.session_state.shift_date = st.date_input("Shift date", value=st.session_state.shift_date)
    st.session_state.staff_count = st.number_input(
        "Staff on shift (demo)", min_value=1, max_value=50,
        value=int(st.session_state.staff_count), step=1,
    )
    st.metric("Patients per staff", round(len(st.session_state.patients) / st.session_state.staff_count, 1))
    st.divider()
    st.caption("Sample shift loaded · fictional demo IDs only")
    st.markdown('<p class="small-muted">No calls are placed. No diagnosis or treatment advice is provided.</p>', unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
  <div class="hero-kicker">Night shift workspace · {st.session_state.shift_date.strftime('%d %b %Y')}</div>
  <h1>✦ AuriShift</h1>
  <p>A calmer, clearer workspace for busy nursing shifts.</p>
</div>
""", unsafe_allow_html=True)
st.caption("Student project · Fictional sample data · Not for clinical use")

tab_overview, tab_patients, tab_births, tab_contacts, tab_ai, tab_handoff = st.tabs([
    "✦  Overview", "▤  Patient queue", "♡  Delivery tally", "↗  Doctor follow-ups", "✧  AI assistant", "⇢  Handoff"
])

# Shared counts for dashboard and handoff.
patient_count = len(st.session_state.patients)
delivery_count = len(st.session_state.deliveries)
boy_total = sum(int(record.get("Boys", 0)) for record in st.session_state.deliveries)
girl_total = sum(int(record.get("Girls", 0)) for record in st.session_state.deliveries)
not_recorded_total = sum(int(record.get("Not recorded", 0)) for record in st.session_state.deliveries)
newborn_total = boy_total + girl_total + not_recorded_total
pending_contacts = [record for record in st.session_state.contacts if record.get("Status") == "Follow-up pending"]

with tab_overview:
    st.subheader("Shift at a glance")
    st.markdown('<p class="section-note">Counts update from the demo records entered in the other tabs.</p>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Patients in queue", patient_count)
    c2.metric("Deliveries", delivery_count)
    c3.metric("Newborns", newborn_total)
    c4.metric("Doctor follow-ups", len(pending_contacts))
    c5.metric("Staff on shift", int(st.session_state.staff_count))

    left, right = st.columns([1.15, .85], gap="large")
    with left:
        st.markdown("### Live patient queue")
        if st.session_state.patients:
            st.dataframe(list(reversed(st.session_state.patients[-6:])), use_container_width=True, hide_index=True)
        else:
            st.info("The queue is empty. Add a fictional patient in Patient queue.")
        st.markdown("### Delivery totals")
        b1, b2, b3 = st.columns(3)
        b1.metric("Boy", boy_total)
        b2.metric("Girl", girl_total)
        b3.metric("Not recorded", not_recorded_total)
    with right:
        st.markdown("### Follow-up board")
        if pending_contacts:
            st.dataframe(list(reversed(pending_contacts)), use_container_width=True, hide_index=True)
        else:
            st.success("No demo follow-ups pending.")
        st.markdown("### Relative case mix")
        case_counts = {
            case_type: sum(1 for row in st.session_state.patients if row.get("Case type") == case_type)
            for case_type in PATIENT_TYPES
        }
        highest_case_count = max(case_counts.values(), default=0)
        for case_type, count in case_counts.items():
            if count:
                label_col, bar_col, count_col = st.columns([1, 1.4, .2])
                label_col.caption(case_type)
                bar_col.progress(count / highest_case_count)
                count_col.caption(str(count))
        st.markdown("### Latest activity")
        activity = []
        activity.extend([("Patient", row.get("Demo ID", ""), row.get("Arrival", "")) for row in st.session_state.patients])
        activity.extend([("Delivery", row.get("Demo mother ID", ""), row.get("Time", "")) for row in st.session_state.deliveries])
        activity.sort(key=lambda row: row[2], reverse=True)
        if activity:
            for kind, demo_id, timestamp in activity[:4]:
                st.write(f"**{timestamp}** · {kind} · `{demo_id}`")
        else:
            st.caption("New entries will appear here.")

with tab_patients:
    st.subheader("Patient queue")
    st.markdown('<p class="section-note">Use fictional IDs. This list helps organize entries; it does not assess clinical urgency.</p>', unsafe_allow_html=True)
    with st.form("patient_entry", clear_on_submit=True):
        p1, p2, p3 = st.columns([1, 1, 1])
        with p1:
            demo_id = st.text_input("Demo patient ID", placeholder="DEMO-110")
        with p2:
            case_type = st.selectbox("Case type", PATIENT_TYPES)
        with p3:
            patient_status = st.selectbox("Current workflow status", PATIENT_STATUSES)
        add_patient = st.form_submit_button("＋ Add to shift queue")
    if add_patient:
        if not demo_id.strip():
            st.warning("Enter a fictional demo ID first.")
        elif any(row.get("Demo ID", "").casefold() == demo_id.strip().casefold() for row in st.session_state.patients):
            st.warning("That demo ID is already in this shift list.")
        else:
            st.session_state.patients.append({
                "Demo ID": demo_id.strip(),
                "Case type": case_type,
                "Arrival": datetime.now().strftime("%H:%M"),
                "Status": patient_status,
            })
            st.success(f"{demo_id.strip()} added to the demo queue.")
            st.rerun()

    st.markdown("### Find a patient")
    f1, f2 = st.columns([1, 1])
    search = f1.text_input("Search by demo ID", placeholder="e.g. DEMO-10")
    filter_type = f2.selectbox("Filter by case type", ["All types"] + PATIENT_TYPES)
    visible_patients = [
        row for row in st.session_state.patients
        if search.casefold() in row.get("Demo ID", "").casefold()
        and (filter_type == "All types" or row.get("Case type") == filter_type)
    ]
    if visible_patients:
        st.dataframe(list(reversed(visible_patients)), use_container_width=True, hide_index=True)
    else:
        st.info("No matching demo patients.")

with tab_births:
    st.subheader("Delivery and newborn tally")
    st.markdown('<p class="section-note">Record a delivery episode and the number of newborns by category for shift totals.</p>', unsafe_allow_html=True)
    with st.form("delivery_entry", clear_on_submit=True):
        mother_id = st.text_input("Demo mother ID", placeholder="DEMO-M24")
        d1, d2, d3 = st.columns(3)
        boys = d1.number_input("Boys", min_value=0, max_value=4, value=0)
        girls = d2.number_input("Girls", min_value=0, max_value=4, value=0)
        unrecorded = d3.number_input("Not recorded", min_value=0, max_value=4, value=0)
        save_birth = st.form_submit_button("＋ Save delivery tally")
    if save_birth:
        if not mother_id.strip():
            st.warning("Enter a fictional demo mother ID first.")
        elif int(boys + girls + unrecorded) == 0:
            st.warning("Enter at least one newborn in the tally.")
        else:
            st.session_state.deliveries.append({
                "Demo mother ID": mother_id.strip(),
                "Boys": int(boys),
                "Girls": int(girls),
                "Not recorded": int(unrecorded),
                "Time": datetime.now().strftime("%H:%M"),
            })
            st.success("Delivery tally saved for this demo shift.")
            st.rerun()
    st.markdown("### Delivery entries")
    if st.session_state.deliveries:
        st.dataframe(list(reversed(st.session_state.deliveries)), use_container_width=True, hide_index=True)
    else:
        st.info("No demo delivery tallies yet.")
    x1, x2, x3, x4 = st.columns(4)
    x1.metric("Delivery episodes", len(st.session_state.deliveries))
    x2.metric("Boys", boy_total)
    x3.metric("Girls", girl_total)
    x4.metric("Total newborns", newborn_total)

with tab_contacts:
    st.subheader("Doctor contact and follow-up log")
    st.markdown('<p class="section-note">Record a contact attempt for handoff. This prototype does not place calls or send messages.</p>', unsafe_allow_html=True)
    with st.form("contact_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            contact_patient = st.text_input("Demo patient ID", placeholder="DEMO-105")
            doctor_role = st.text_input("On-call role", placeholder="On-call doctor")
        with c2:
            contact_status = st.selectbox("Contact status", CONTACT_STATUSES)
            reason = st.text_input("Short reason", placeholder="Review requested")
        save_contact = st.form_submit_button("＋ Save contact log")
    if save_contact:
        if not contact_patient.strip() or not reason.strip():
            st.warning("Enter a demo patient ID and a short fictional reason.")
        else:
            st.session_state.contacts.append({
                "Demo patient ID": contact_patient.strip(),
                "On-call role": doctor_role.strip() or "On-call doctor",
                "Reason": reason.strip(),
                "Status": contact_status,
                "Time": datetime.now().strftime("%H:%M"),
            })
            st.success("Demo contact log saved.")
            st.rerun()
    st.markdown("### Contact log")
    if st.session_state.contacts:
        st.dataframe(list(reversed(st.session_state.contacts)), use_container_width=True, hide_index=True)
    else:
        st.info("No contact log entries yet.")

with tab_ai:
    st.subheader("AI note and handoff assistant")
    st.markdown('<p class="section-note">AI can organize text and shift totals into a draft. It does not make care decisions.</p>', unsafe_allow_html=True)
    st.warning("Only use fictional, non-identifying demo text here. If enabled, text you submit is sent to the OpenAI API. Never enter real patient information.")
    api_key_ready = bool(os.getenv("OPENAI_API_KEY"))
    if not api_key_ready:
        st.info("AI is optional. To enable it, add your API key to a local .env file as described in START_HERE.md. The rest of the app works without AI.")
    model_name = os.getenv("OPENAI_MODEL", "gpt-5.5")

    st.markdown("### 1 · Structure a fictional note")
    raw_note = st.text_area(
        "Demo note",
        placeholder="Example: DEMO-105 arrived at 21:42 after an accident. Doctor contact attempted at 21:49. Review still pending.",
        height=120,
        key="ai_raw_note",
    )
    consent_note = st.checkbox("I confirm this is fictional demo text and may be sent to the AI service.", key="ai_note_consent")
    if st.button("✧ Draft structured note", disabled=not (api_key_ready and consent_note and raw_note.strip())):
        try:
            response = OpenAI().responses.create(
                model=model_name,
                instructions=(
                    "You format user-provided fictional shift notes into a concise, neutral handoff draft. "
                    "Do not diagnose, triage, recommend treatment, infer missing facts, or change meaning. "
                    "Use only supplied information. Mark absent information as 'Not provided'. "
                    "Use headings: Event, Details provided, Contact/follow-up, Information not provided. "
                    "The result is a draft that must be checked by a human nurse."
                ),
                input=raw_note,
                store=False,
                max_output_tokens=500,
            )
            st.session_state.ai_note_draft = response.output_text
            st.session_state.ai_note_review = response.output_text
        except Exception as exc:
            st.error(f"Could not create the draft ({type(exc).__name__}). Check the API setup and try again.")
    if st.session_state.get("ai_note_draft"):
        st.text_area("Editable AI draft — review before using", height=180, key="ai_note_review")

    st.divider()
    st.markdown("### 2 · Draft a shift overview from totals")
    st.caption("This sends only aggregate counts and category totals, not patient IDs or note text.")
    consent_summary = st.checkbox("I confirm these are fictional sample totals and may be sent to the AI service.", key="ai_summary_consent")
    if st.button("✧ Draft shift overview", disabled=not (api_key_ready and consent_summary)):
        category_counts = {}
        for item in st.session_state.patients:
            label = item.get("Case type", "Other")
            category_counts[label] = category_counts.get(label, 0) + 1
        aggregate = {
            "patient_count": len(st.session_state.patients),
            "delivery_episodes": len(st.session_state.deliveries),
            "newborn_total": newborn_total,
            "boy_total": boy_total,
            "girl_total": girl_total,
            "not_recorded_total": not_recorded_total,
            "pending_doctor_followups": len(pending_contacts),
            "patient_case_type_counts": category_counts,
        }
        try:
            response = OpenAI().responses.create(
                model=model_name,
                instructions=(
                    "Write a brief, neutral shift overview using only the supplied aggregate demo counts. "
                    "Do not interpret severity, make clinical recommendations, invent events, or identify people. "
                    "Label it as a draft for human review."
                ),
                input=str(aggregate),
                store=False,
                max_output_tokens=350,
            )
            st.session_state.ai_shift_draft = response.output_text
            st.session_state.ai_shift_review = response.output_text
        except Exception as exc:
            st.error(f"Could not create the draft ({type(exc).__name__}). Check the API setup and try again.")
    if st.session_state.get("ai_shift_draft"):
        st.text_area("Editable AI shift overview — review before using", height=140, key="ai_shift_review")

with tab_handoff:
    st.subheader("Shift handoff")
    st.markdown('<p class="section-note">Review a compact summary and export it for your portfolio demo.</p>', unsafe_allow_html=True)
    pending_contacts = [row for row in st.session_state.contacts if row.get("Status") == "Follow-up pending"]
    case_counts = {}
    for row in st.session_state.patients:
        case_counts[row.get("Case type", "Other")] = case_counts.get(row.get("Case type", "Other"), 0) + 1
    st.markdown("#### Shift totals")
    st.write(f"- Patients recorded: **{len(st.session_state.patients)}**")
    st.write(f"- Delivery episodes: **{len(st.session_state.deliveries)}**")
    st.write(f"- Newborns: **{newborn_total}** ({boy_total} boys, {girl_total} girls, {not_recorded_total} not recorded)")
    st.write(f"- Doctor follow-ups pending: **{len(pending_contacts)}**")
    st.markdown("#### Patient counts by case type")
    if case_counts:
        st.dataframe([{"Case type": key, "Count": value} for key, value in case_counts.items()], use_container_width=True, hide_index=True)
    st.markdown("#### Pending contacts")
    if pending_contacts:
        st.dataframe(pending_contacts, use_container_width=True, hide_index=True)
    else:
        st.success("No demo contact follow-ups pending.")
    handoff = f"""AURISHIFT — DEMO HANDOFF
Shift date: {st.session_state.shift_date.strftime('%d %b %Y')}

Patients recorded: {len(st.session_state.patients)}
Delivery episodes: {len(st.session_state.deliveries)}
Newborns: {newborn_total}
Boys: {boy_total}
Girls: {girl_total}
Not recorded: {not_recorded_total}
Doctor follow-ups pending: {len(pending_contacts)}

Patient counts by case type:
"""
    for case, count in case_counts.items():
        handoff += f"- {case}: {count}\n"
    handoff += "\nFictional sample/demo data only. Not for clinical use.\n"
    st.download_button("⬇ Download handoff summary", handoff, "aurishift_demo_handoff.txt", "text/plain")

st.divider()
with st.expander("Reset sample shift"):
    st.caption("This clears the temporary entries in the app session. Sample data will load again after restarting the app.")
    confirm_reset = st.checkbox("I understand this clears the current demo entries", key="confirm_reset")
    if st.button("Clear current shift", disabled=not confirm_reset):
        st.session_state.patients = []
        st.session_state.deliveries = []
        st.session_state.contacts = []
        st.rerun()

st.markdown('<p class="small-muted" style="text-align:center">Designed as a student prototype · Fictional records only · No clinical decisions or real contact</p>', unsafe_allow_html=True)
