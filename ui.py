import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

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

# --- Session state ---
if "selected_subjects" not in st.session_state:
    st.session_state.selected_subjects = []

# --- Subject ordering ---
ENGLISH = ["EAL", "ENG", "ENL", "LIT"]
MATHS = ["MAG", "MAM", "MAS"]

def subject_sort_key(subject):
    code = subject[2:]  # strip 11 / 12
    if code in ENGLISH:
        return (0, ENGLISH.index(code))
    if code in MATHS:
        return (1, MATHS.index(code))
    return (2, code)

# --- Sidebar ---
st.sidebar.header("Filter SACs")
year = st.sidebar.selectbox("Select your year:", [12,11])

view_mode = st.sidebar.radio(
    "View mode:",
    ["Single subject", "Selected subjects"]
)

subjects = sorted(
    df[df["Year"] == str(year)]["subject"].unique(),
    key=subject_sort_key
)

subject = st.sidebar.selectbox("Select your subject:", subjects)

# Checkbox for selection
checked = st.sidebar.checkbox(
    "Include this subject",
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

# --- Helper functions ---
def fancy_date(dt):
    day = dt.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return f"{day}{suffix} {dt.strftime('%B')}"

def countdown(dt):
    remaining = dt - today
    if remaining.total_seconds() <= 0:
        return "Completed"
    d = remaining.days
    h, r = divmod(remaining.seconds, 3600)
    m, s = divmod(r, 60)
    return f"{d}d {h}h {m}m {s}s"

# ======================================================
# SINGLE SUBJECT VIEW (UNCHANGED UI)
# ======================================================
if view_mode == "Single subject":

    subject_df = df[df["subject"] == subject].sort_values("date")
    future = subject_df[subject_df["date"] >= today]

    if not future.empty:
        next_sac = future.iloc[0]["date"]
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,#f39c12,#e74c3c);
        color:white;padding:30px;border-radius:15px;
        text-align:center;font-size:36px;font-weight:bold;' >
        ⏳ Next SAC: {next_sac.strftime('%d/%m/%Y')} | {fancy_date(next_sac)}<br>
        <span style='font-size:48px;'>{countdown(next_sac)}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📌 SAC List")

    for i, (_, row) in enumerate(subject_df.iterrows(), 1):
        bg = "#d5f5e3" if row["date"] < today else "#fcf3cf"
        st.markdown(f"""
        <div style='padding:15px;border-radius:12px;
        background:{bg};margin-bottom:10px;
        display:flex;justify-content:space-between;
        box-shadow:2px 2px 10px rgba(0,0,0,0.1);'>
        <strong style='color:#2c3e50'>{i}. {row['subject']}</strong>
        <span style='color:#2c3e50'>{row['date'].strftime('%d/%m/%Y')} | {fancy_date(row['date'])}</span>
        </div>
        """, unsafe_allow_html=True)
# ======================================================
# SELECTED SUBJECTS VIEW
# ======================================================
else:
    selected_df = df[df["subject"].isin(st.session_state.selected_subjects)].sort_values("date")
    future = selected_df[selected_df["date"] >= today]

    # --- Total progress across all selected subjects ---
    total_sacs = len(selected_df)
    total_completed = sum(selected_df["date"] < today)
    total_progress = int((total_completed / total_sacs) * 100) if total_sacs > 0 else 0

    if total_sacs > 0:
        st.markdown("## 🏆 Overall Progress for Selected Subjects")
        st.progress(total_progress)
        st.caption(f"{total_completed}/{total_sacs} SACs completed across all selected subjects")

    # --- Next SAC overall ---
    if not future.empty:
        next_row = future.iloc[0]
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,#8e44ad,#3498db);
        color:white;padding:30px;border-radius:15px;
        text-align:center;font-size:36px;font-weight:bold;' >
        ⏳ NEXT SAC (All Subjects)<br>
        {next_row['subject']} – {next_row['date'].strftime('%d/%m/%Y')}<br>
        <span style='font-size:48px;'>{countdown(next_row['date'])}</span>
        </div>
        """, unsafe_allow_html=True)

    # --- Individual subjects ---
    for subj in st.session_state.selected_subjects:
        st.markdown(f"## 📘 {subj}")
        subj_df = df[df["subject"] == subj].sort_values("date")

        # Subject-level progress
        num_completed = sum(subj_df["date"] < today)
        total_subj_sacs = len(subj_df)
        progress_percent = int((num_completed / total_subj_sacs) * 100) if total_subj_sacs > 0 else 0
        st.progress(progress_percent)
        st.caption(f"{num_completed}/{total_subj_sacs} SACs completed")

        for _, row in subj_df.iterrows():
            bg = "#d5f5e3" if row["date"] < today else "#fcf3cf"
            st.markdown(f"""
            <div style='padding:12px;border-radius:12px;
            background:{bg};margin-bottom:8px;
            display:flex;justify-content:space-between;
            box-shadow:1px 1px 6px rgba(0,0,0,0.1);'>
            <strong style='color:#2c3e50'>{row['subject']}</strong>
            <span style='color:#2c3e50'>{row['date'].strftime('%d/%m/%Y')} | {fancy_date(row['date'])}</span>
            </div>
            """, unsafe_allow_html=True)
