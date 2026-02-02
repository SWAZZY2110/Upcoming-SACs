import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os, json, uuid, sqlite3

# --- Auto-refresh every second ---
st_autorefresh(interval=1000, key="dashboard_refresh")

# --- Load CSV ---
df = pd.read_csv("sac_calendar.csv")
df["date"] = pd.to_datetime(df["date"])
df["Year"] = df["subject"].str[:2]

# --- Page setup ---
st.set_page_config(page_title="VCE SAC Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center; color:#2c3e50;'>📅 VCE SAC Dashboard</h1>", unsafe_allow_html=True)

today = pd.Timestamp.now()

# --- Database setup ---
DB_FILE = "user_data.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS user_data (
    user_id TEXT PRIMARY KEY,
    year INTEGER,
    view_mode TEXT,
    selected_subjects TEXT
)
""")
conn.commit()

# --- User identification via cookie ---
if "user_id" not in st.session_state:
    if "user_id_cookie" in st.query_params:
        user_id = st.query_params["user_id_cookie"][0]

    else:
        user_id = str(uuid.uuid4())
    st.session_state.user_id = user_id

# --- Load user data from DB ---
c.execute("SELECT year, view_mode, selected_subjects FROM user_data WHERE user_id=?", (st.session_state.user_id,))
row = c.fetchone()
if row:
    st.session_state.year = row[0]
    st.session_state.view_mode = row[1]
    st.session_state.selected_subjects = json.loads(row[2])
else:
    st.session_state.year = 12
    st.session_state.view_mode = "Single subject"
    st.session_state.selected_subjects = []

# --- Subject ordering ---
ENGLISH = ["EAL", "ENG", "ENL", "LIT"]
MATHS = ["MAG", "MAM", "MAS"]

def subject_sort_key(subject):
    code = subject[2:]
    if code in ENGLISH:
        return (0, ENGLISH.index(code))
    if code in MATHS:
        return (1, MATHS.index(code))
    return (2, code)

# --- Helper functions ---
def fancy_date(dt):
    day = dt.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return f"{day}{suffix} {dt.strftime('%B')}"

def countdown(dt):
    remaining = dt - datetime.now()
    if remaining.total_seconds() <= 0:
        return "Completed"
    d = remaining.days
    h, r = divmod(remaining.seconds, 3600)
    m, s = divmod(r, 60)
    return f"{d}d {h}h {m}m {s}s"

def sac_card(row):
    delta_days = (row["date"] - datetime.now()).days
    if delta_days < 0:
        bg = "#d5f5e3"  # completed
    elif delta_days <= 3:
        bg = "#f39c12"  # urgent
    else:
        bg = "#fcf3cf"  # upcoming
    return f"""
    <div style='padding:12px;border-radius:12px;
    background:{bg};margin-bottom:8px;
    display:flex;justify-content:space-between;
    box-shadow:1px 1px 6px rgba(0,0,0,0.1);'>
    <strong style='color:#2c3e50'>{row['subject']}</strong>
    <span style='color:#2c3e50'>{row['date'].strftime('%d/%m/%Y')} | {fancy_date(row['date'])} | ⏳ {countdown(row['date'])}</span>
    </div>
    """

# --- Sidebar ---
st.sidebar.header("Filter SACs")

# Year select
st.session_state.year = st.sidebar.selectbox(
    "Select your year:", [12,11], index=[12,11].index(st.session_state.year)
)

# Subjects for that year
subjects = sorted(
    df[df["Year"] == str(st.session_state.year)]["subject"].unique(),
    key=subject_sort_key
)

# View mode
st.session_state.view_mode = st.sidebar.radio(
    "View mode:",
    ["Single subject", "Selected subjects", "All subjects"],
    index=["Single subject", "Selected subjects", "All subjects"].index(st.session_state.view_mode)
)

# Single subject select
subject = st.sidebar.selectbox("Select a subject:", subjects)

# Checkbox to include in selected subjects
checked = st.sidebar.checkbox(
    "Select this subject",
    value=subject in st.session_state.selected_subjects
)
if checked and subject not in st.session_state.selected_subjects:
    st.session_state.selected_subjects.append(subject)
if not checked and subject in st.session_state.selected_subjects:
    st.session_state.selected_subjects.remove(subject)

# Show selected subjects
if st.session_state.selected_subjects:
    st.sidebar.caption("Selected subjects:")
    for s in st.session_state.selected_subjects:
        st.sidebar.write("•", s)

# --- Save user data to DB ---
c.execute("""
INSERT INTO user_data(user_id, year, view_mode, selected_subjects)
VALUES (?, ?, ?, ?)
ON CONFLICT(user_id) DO UPDATE SET
    year=excluded.year,
    view_mode=excluded.view_mode,
    selected_subjects=excluded.selected_subjects
""", (
    st.session_state.user_id,
    st.session_state.year,
    st.session_state.view_mode,
    json.dumps(st.session_state.selected_subjects)
))
conn.commit()

# --- Determine subjects to show ---
if st.session_state.view_mode == "Single subject":
    subjects_to_show = [subject]
elif st.session_state.view_mode == "Selected subjects":
    subjects_to_show = st.session_state.selected_subjects
else:  # All subjects
    subjects_to_show = subjects

# ======================================================
# Display content
# ======================================================

# Find next SAC overall
all_selected_df = df[df["subject"].isin(subjects_to_show)].sort_values("date")
future = all_selected_df[all_selected_df["date"] >= today]
if not future.empty:
    next_row = future.iloc[0]
    st.markdown(f"""
    <div style='background:linear-gradient(90deg,#8e44ad,#3498db);
    color:#ffffff;padding:30px;border-radius:15px;
    text-align:center;font-size:36px;font-weight:bold;' >
    ⏳ NEXT SAC<br>
    {next_row['subject']} – {next_row['date'].strftime('%d/%m/%Y')}<br>
    <span style='font-size:48px;'>{countdown(next_row['date'])}</span>
    </div>
    """, unsafe_allow_html=True)

# Overall progress
total_sacs = len(all_selected_df)
total_completed = sum(all_selected_df["date"] < today)
overall_progress = int((total_completed / total_sacs) * 100) if total_sacs > 0 else 0
if total_sacs > 0:
    st.markdown("## 🏆 Overall Progress")
    st.progress(overall_progress)
    st.caption(f"{total_completed}/{total_sacs} SACs completed across all selected subjects")

# Display each subject individually with expander OPEN by default
for subj in subjects_to_show:
    subj_df = df[df["subject"] == subj].sort_values("date")
    num_completed = sum(subj_df["date"] < today)
    total_subj_sacs = len(subj_df)
    subj_progress = int((num_completed / total_subj_sacs) * 100) if total_subj_sacs > 0 else 0

    with st.expander(f"{subj} ({num_completed}/{total_subj_sacs} completed)", expanded=True):
        st.progress(subj_progress)
        for _, row in subj_df.iterrows():
            st.markdown(sac_card(row), unsafe_allow_html=True)

# Bottom chronological list of all selected SACs (collapsed by default)
st.markdown("---")
if st.session_state.selected_subjects:
    with st.expander("### 📋 All Selected SACs (Chronological)", expanded=False):
        for _, row in all_selected_df.iterrows():
            st.markdown(sac_card(row), unsafe_allow_html=True)
