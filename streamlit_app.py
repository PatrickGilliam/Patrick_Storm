import streamlit as st
import pandas as pd
import os
from datetime import datetime

TARGET_MILES = 3000
DATA_FILE = "running_tracker.csv"

st.set_page_config(
    page_title="Patrick & Storm Running Tracker",
    page_icon="🏃",
    layout="wide"
)

def to_miles(distance, unit):
    if unit == "km":
        return distance * 0.621371
    return distance

def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["date", "person", "distance_input", "unit", "distance_miles"])
        df.to_csv(DATA_FILE, index=False)
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def add_run(person, distance, unit):
    df = load_data()
    miles = to_miles(distance, unit)

    new_row = pd.DataFrame([{
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "person": person,
        "distance_input": distance,
        "unit": unit,
        "distance_miles": miles
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)

def get_summary(df):
    patrick_total = df[df["person"] == "Patrick"]["distance_miles"].sum()
    storm_total = df[df["person"] == "Storm"]["distance_miles"].sum()
    combined_total = df["distance_miles"].sum()
    remaining = max(TARGET_MILES - combined_total, 0)
    return patrick_total, storm_total, combined_total, remaining

def render_cartoon_journey(patrick_total, storm_total, target):
    storm_progress = min(storm_total / target, 0.5)
    patrick_progress = min(patrick_total / target, 0.5)

    storm_left = 8 + storm_progress * 70
    patrick_left = 92 - patrick_progress * 70

    met = (patrick_total + storm_total) >= target

    if met:
        storm_left = 48
        patrick_left = 52

    st.markdown(f"""
    <style>
    .journey-card {{
        position: relative;
        width: 100%;
        height: 300px;
        border-radius: 30px;
        background: linear-gradient(180deg, #dff4ff 0%, #fff6ee 100%);
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.10);
        margin-top: 10px;
        margin-bottom: 20px;
    }}

    .journey-title {{
        text-align: center;
        font-size: 30px;
        font-weight: 800;
        padding-top: 18px;
        color: #2f2f2f;
    }}

    .route-line {{
        position: absolute;
        left: 8%;
        right: 8%;
        top: 58%;
        border-top: 6px dashed #8ecae6;
    }}

    .city-left, .city-right {{
        position: absolute;
        top: 71%;
        font-size: 18px;
        font-weight: 700;
        color: #444;
    }}

    .city-left {{
        left: 5%;
    }}

    .city-right {{
        right: 5%;
    }}

    .avatar {{
        position: absolute;
        top: 42%;
        transform: translateX(-50%);
        font-size: 46px;
        transition: left 0.6s ease-in-out;
    }}

    .name-label {{
        position: absolute;
        top: 31%;
        transform: translateX(-50%);
        font-size: 17px;
        font-weight: 800;
        color: #333;
    }}

    .storm {{
        left: {storm_left}%;
    }}

    .patrick {{
        left: {patrick_left}%;
    }}

    .heart {{
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        font-size: 42px;
    }}

    .meeting-text {{
        position: absolute;
        width: 100%;
        bottom: 18px;
        text-align: center;
        font-size: 19px;
        font-weight: 700;
        color: #444;
    }}

    .small-cloud {{
        position: absolute;
        font-size: 26px;
        opacity: 0.55;
    }}

    .cloud1 {{
        top: 14%;
        left: 14%;
    }}

    .cloud2 {{
        top: 18%;
        right: 18%;
    }}
    </style>

    <div class="journey-card">
        <div class="journey-title">Patrick & Storm Running to Each Other</div>

        <div class="small-cloud cloud1">☁️</div>
        <div class="small-cloud cloud2">☁️</div>

        <div class="route-line"></div>

        <div class="heart">❤️</div>

        <div class="name-label storm">Storm</div>
        <div class="avatar storm">🏃‍♀️</div>

        <div class="name-label patrick">Patrick</div>
        <div class="avatar patrick">🏃</div>

        <div class="city-left">📍 Kamloops, BC</div>
        <div class="city-right">📍 Wesley Chapel, FL</div>

        <div class="meeting-text">
            {"You made it to each other! 💕" if met else "Every run brings you closer 💫"}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.title("🏃 Patrick & Storm Running Tracker")
st.write("Track your runs as you move from Kamloops, BC and Wesley Chapel, FL toward each other.")

df = load_data()
patrick_total, storm_total, combined_total, remaining = get_summary(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Patrick", f"{patrick_total:.2f} mi")
col2.metric("Storm", f"{storm_total:.2f} mi")
col3.metric("Combined", f"{combined_total:.2f} mi")
col4.metric("Remaining", f"{remaining:.2f} mi")

progress = min(combined_total / TARGET_MILES, 1.0)
st.progress(progress)
st.caption(f"{progress * 100:.1f}% of the journey completed")

render_cartoon_journey(patrick_total, storm_total, TARGET_MILES)

st.subheader("Add a Run")

with st.form("run_form"):
    person = st.selectbox("Who ran?", ["Patrick", "Storm"])
    distance = st.number_input("Distance", min_value=0.0, step=0.1)
    unit = st.selectbox("Unit", ["miles", "km"])
    submitted = st.form_submit_button("Add Run")

    if submitted:
        if distance > 0:
            add_run(person, distance, unit)
            st.success(f"Added {distance} {unit} for {person}.")
            st.rerun()
        else:
            st.error("Please enter a distance greater than 0.")

st.subheader("Recent Runs")
if not df.empty:
    recent_df = df.sort_values("date", ascending=False).copy()
    st.dataframe(recent_df, use_container_width=True, hide_index=True)
else:
    st.info("No runs added yet.")
