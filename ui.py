import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- Auto-refresh every second ---
st_autorefresh(interval=1000, key="dashboard_refresh")

# --- Load CSV ---
df = pd.read_csv("sac_calendar.csv")
df['date'] = pd.to_datetime(df['date'])
df['Year'] = df['subject'].str[:2]  # Ensure 'Year' column exists

st.set_page_config(page_title="VCE SAC Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center; color:#2c3e50;'>📅 VCE SAC Dashboard</h1>", unsafe_allow_html=True)

# --- Sidebar filters ---
st.sidebar.header("Filter SACs")
year = st.sidebar.selectbox("Select your year:", [11, 12])
subjects = df[df['Year'] == str(year)]['subject'].unique()
subject = st.sidebar.selectbox("Select your subject:", subjects)

# --- Filter data ---
subject_df = df[df['subject'] == subject].sort_values("date")
num_sacs = len(subject_df)

# --- Helper function for fancy date ---
def fancy_date(dt):
    day = dt.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return f"{day}{suffix} {dt.strftime('%B')}"

# --- Countdown to next SAC ---
today = pd.Timestamp.now()
future_sacs = subject_df[subject_df['date'] >= today]

countdown_placeholder = st.empty()
if not future_sacs.empty:
    next_sac = future_sacs.iloc[0]['date']
    remaining = next_sac - today
    days = remaining.days
    hours, rem = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    countdown_placeholder.markdown(
        f"""
        <div style='
            background: linear-gradient(90deg, #f39c12, #e74c3c);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            box-shadow: 2px 2px 15px rgba(0,0,0,0.3);
        '>
            ⏳ Next SAC: {next_sac.strftime('%d/%m/%Y')} | {fancy_date(next_sac)}<br>
            <span style="font-size:48px;">{days}d {hours}h {minutes}m {seconds}s</span>
        </div>
        """, unsafe_allow_html=True
    )
else:
    countdown_placeholder.markdown(
        "<div style='background-color:#2ecc71; color:white; padding:30px; border-radius:15px; text-align:center; font-size:36px; font-weight:bold;'>🎉 All SACs Completed!</div>",
        unsafe_allow_html=True
    )

# --- Styled progress bar ---
completed_sacs = sum(subject_df['date'] < today)
progress_percent = int((completed_sacs / num_sacs) * 100) if num_sacs > 0 else 0

st.markdown(f"<h3 style='color:#34495e;'>Progress: {completed_sacs}/{num_sacs} SACs Completed</h3>", unsafe_allow_html=True)
st.progress(progress_percent)
# --- Display SACs in cards with numbering ---
st.markdown("<h3 style='color:#34495e;'>📌 SAC List</h3>", unsafe_allow_html=True)

for i, (_, row) in enumerate(subject_df.iterrows(), start=1):  # start=1 gives 1,2,3...
    # Different background for past/future SACs
    if row['date'] < today:
        bg_color = "#d5f5e3"  # light green for completed
    else:
        bg_color = "#fcf3cf"  # light yellow for upcoming

    st.markdown(
        f"""
        <div style='
            padding: 15px; 
            border: 2px solid #ccc; 
            border-radius: 12px; 
            margin-bottom: 10px; 
            background-color: {bg_color};
            color: #2c3e50;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        '>
            <span style='font-weight:bold; font-size:18px;'>{i}. {row['subject']}</span>
            <span style='font-size:16px;'> {row['date'].strftime('%d/%m/%Y')} | {fancy_date(row['date'])}</span>
        </div>
        """, unsafe_allow_html=True
    )
