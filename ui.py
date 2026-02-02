import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os, json, uuid

# Install cookies manager first:
# pip install streamlit-cookies-manager
from streamlit_cookies_manager import EncryptedCookieManager

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

# --- Create folder to store user data ---
USER_DATA_DIR = "user_data"
os.makedirs(USER_DATA_DIR, exist_ok=True)

# --- Setup persistent cookies ---
cookies = EncryptedCookieManager(
    prefix="sac_dashboard_",
    password="my-very-secret-password",  # change this
)
if not cookies.ready():
    st.stop()  # wait until cookies load

# --- Get or create user_id cookie ---
if "user_id" in cookies:
    user_id = cookies["user_id"]
else:
    user_id = str(uuid.uuid4())
    cookies["user_id"] = user_id
    cookies.save()

USER_FILE = os.path.join(USER_DATA_DIR, f"user_{user_id}.json")

# --- Load user data safely ---
if os.path.exists(USER_FILE):
    try:
        with open(USER_FILE, "r") as f:
            user_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        user_data = {}
else:
    user_data = {}

st.session_state.selected_subjects = user_data.get("selected_subjects", [])
st.session_state.view_mode = user_data.get("view_mode", "Single subject")
st.session_state.year = user_data.get("year", 12)

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
        bg = "#d5f5e3"
    elif delta_days <= 3:
        bg = "#f39c12"
    else:
        bg = "#fcf3cf"
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
st.session_state.year = st.sidebar.selectbox(
    "Select your year:", [11, 12], index=[11, 12].index(st.session_state.year)
)
subjects = sorted(
    df[df["Year"] == str(st.session_state.year)]["subject"].unique(),
    key=subject_sort_key
)
st.session_state.view_mode = st.sidebar.radio(
    "View mode:", ["Single subject", "Selected subjects", "All subjects"],
    index=["Single subject", "Selected subjects", "All subjects"].index(st.session_state.view_mode)
)
subject = st.sidebar.selectbox("Select a subject:", subjects)
checked = st.sidebar.checkbox("Select this subject", value=subject in st.session_state.selected_subjects)
if checked and subject not in st.session_state.selected_subjects:
    st.session_state.selected_subjects.append(subject)
if not checked and subject in st.session_state.selected_subjects:
    st.session_state.selected_subjects.remove(subject)
if st.session_state.selected_subjects:
    st.sidebar.caption("Selected subjects:")
    for s in st.session_state.selected_subjects:
        st.sidebar.write("•", s)

# --- Save user data ---
with open(USER_FILE, "w") as f:
    json.dump({
        "selected_subjects": st.session_state.selected_subjects,
        "view_mode": st.session_state.view_mode,
        "year": st.session_state.year
    }, f)

# ======================================================
# SINGLE SUBJECT VIEW
# ======================================================
if st.session_state.view_mode == "Single subject":
    subject_df = df[df["subject"] == subject].sort_values("date")
    future = subject_df[subject_df["date"] >= today]

    if not future.empty:
        next_sac = future.iloc[0]["date"]
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,#f39c12,#e74c3c);
        color:#ffffff;padding:30px;border-radius:15px;
        text-align:center;font-size:36px;font-weight:bold;' >
        ⏳ Next SAC: {next_sac.strftime('%d/%m/%Y')} | {fancy_date(next_sac)}<br>
        <span style='font-size:48px;'>{countdown(next_sac)}</span>
        </div>
        """, unsafe_allow_html=True)

    # Subject expander
    with st.expander(f"📘 {subject}", expanded=True):
        for _, row in subject_df.iterrows():
            st.markdown(sac_card(row), unsafe_allow_html=True)

# ======================================================
# SELECTED SUBJECTS VIEW
# ======================================================
elif st.session_state.view_mode == "Selected subjects":
    selected_df = df[df["subject"].isin(st.session_state.selected_subjects)].sort_values("date")
    future = selected_df[selected_df["date"] >= today]

    # Next SAC hero card
    if not future.empty:
        next_row = future.iloc[0]
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,#8e44ad,#3498db);
        color:#ffffff;padding:30px;border-radius:15px;
        text-align:center;font-size:36px;font-weight:bold;' >
        ⏳ NEXT SAC (All Subjects)<br>
        {next_row['subject']} – {next_row['date'].strftime('%d/%m/%Y')}<br>
        <span style='font-size:48px;'>{countdown(next_row['date'])}</span>
        </div>
        """, unsafe_allow_html=True)

    # Overall progress
    total_sacs = len(selected_df)
    total_completed = sum(selected_df["date"] < today)
    overall_progress = int((total_completed / total_sacs) * 100) if total_sacs > 0 else 0
    if total_sacs > 0:
        st.markdown("## 🏆 Overall Progress for Selected Subjects")
        st.progress(overall_progress)
        st.caption(f"{total_completed}/{total_sacs} SACs completed across all selected subjects")

    # Each subject expander (auto-open)
    for subj in st.session_state.selected_subjects:
        subj_df = df[df["subject"] == subj].sort_values("date")
        num_completed = sum(subj_df["date"] < today)
        total_subj_sacs = len(subj_df)
        subj_progress = int((num_completed / total_subj_sacs) * 100) if total_subj_sacs > 0 else 0

        with st.expander(f"📘 {subj} ({num_completed}/{total_subj_sacs} completed)", expanded=True):
            st.progress(subj_progress)
            for _, row in subj_df.iterrows():
                st.markdown(sac_card(row), unsafe_allow_html=True)

    # --- Chronological SAC list for all selected subjects (auto-closed) ---
    if not selected_df.empty:  # make sure selected_df is defined in this scope
        st.markdown("---")  # horizontal line
        st.markdown("### **All SACs in Chronological Order**")  # bold heading
        with st.expander("📅 View All Selected SACs Chronologically", expanded=False):
            for _, row in selected_df.sort_values("date").iterrows():
                st.markdown(sac_card(row), unsafe_allow_html=True)

# ======================================================
# ALL SUBJECTS VIEW WITH YEAR FILTER AT TOP
# ======================================================
elif st.session_state.view_mode == "All subjects":
    st.markdown("### 🔎 Filter by Year")
    year_filter = st.selectbox("", ["All", 11, 12], index=["All", 11, 12].index("All"))

    if year_filter == "All":
        all_df = df.sort_values(["date", "subject"])
    else:
        all_df = df[df["Year"] == str(year_filter)].sort_values(["date", "subject"])

    future = all_df[all_df["date"] >= today]

    # Next SAC hero card
    if not future.empty:
        next_row = future.iloc[0]
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,#16a085,#1abc9c);
        color:#ffffff;padding:30px;border-radius:15px;
        text-align:center;font-size:36px;font-weight:bold;' >
        ⏳ NEXT SAC (All Subjects)<br>
        {next_row['subject']} – {next_row['date'].strftime('%d/%m/%Y')}<br>
        <span style='font-size:48px;'>{countdown(next_row['date'])}</span>
        </div>
        """, unsafe_allow_html=True)

    # Overall progress
    total_sacs = len(all_df)
    total_completed = sum(all_df["date"] < today)
    overall_progress = int((total_completed / total_sacs) * 100) if total_sacs > 0 else 0
    if total_sacs > 0:
        st.markdown("## 🏆 Overall Progress Across All Subjects")
        st.progress(overall_progress)
        st.caption(f"{total_completed}/{total_sacs} SACs completed in total")

    # Per-subject expanders
    for subj in sorted(all_df["subject"].unique(), key=subject_sort_key):
        subj_df = all_df[all_df["subject"] == subj].sort_values("date")
        num_completed = sum(subj_df["date"] < today)
        total_subj_sacs = len(subj_df)
        subj_progress = int((num_completed / total_subj_sacs) * 100) if total_subj_sacs > 0 else 0

        with st.expander(f"📘 {subj} ({num_completed}/{total_subj_sacs} completed)", expanded=True):
            st.progress(subj_progress)
            for _, row in subj_df.iterrows():
                st.markdown(sac_card(row), unsafe_allow_html=True)
