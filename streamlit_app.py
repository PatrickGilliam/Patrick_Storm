import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

TARGET_MILES = 3000
DATA_FILE = "running_tracker.csv"

st.set_page_config(page_title="Patrick & Storm Running Tracker", page_icon="🏃", layout="wide")

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

def draw_journey(patrick_total, storm_total, target):
    fig, ax = plt.subplots(figsize=(12, 3))

    patrick_progress = min(patrick_total / target, 1.0)
    storm_progress = min(storm_total / target, 1.0)

    patrick_x = patrick_progress
    storm_x = 1 - storm_progress

    if patrick_x > storm_x:
        meet_x = 0.5 * (patrick_x + storm_x)
        patrick_x = meet_x
        storm_x = meet_x

    ax.plot([0, 1], [0.5, 0.5], linewidth=6)

    ax.scatter([0], [0.5], s=300, marker='s')
    ax.text(0, 0.62, "Kamloops, BC", ha="center", fontsize=11, fontweight="bold")

    ax.scatter([1], [0.5], s=300, marker='s')
    ax.text(1, 0.62, "Wesley Chapel, FL", ha="center", fontsize=11, fontweight="bold")

    ax.scatter([patrick_x], [0.45], s=500)
    ax.text(patrick_x, 0.33, "Patrick", ha="center", fontsize=11, fontweight="bold")

    ax.scatter([storm_x], [0.55], s=500)
    ax.text(storm_x, 0.67, "Storm", ha="center", fontsize=11, fontweight="bold")

    if patrick_x >= storm_x:
        ax.text(0.5, 0.15, "❤️ You made it to each other! ❤️", ha="center", fontsize=14, fontweight="bold")
    else:
        ax.text(0.5, 0.15, "Keep running toward each other!", ha="center", fontsize=12)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0, 1)
    ax.axis("off")

    return fig

def draw_contribution_chart(patrick_total, storm_total):
    fig, ax = plt.subplots(figsize=(4, 4))

    total = patrick_total + storm_total
    if total == 0:
        ax.text(0.5, 0.5, "No runs yet", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig

    ax.pie(
        [patrick_total, storm_total],
        labels=["Patrick", "Storm"],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"width": 0.45}
    )
    ax.set_title("Contribution Split")
    return fig

st.title("🏃 Patrick & Storm Running Tracker")
st.write("Running across the distance from Kamloops, BC to Wesley Chapel, FL.")

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

st.pyplot(draw_journey(patrick_total, storm_total, TARGET_MILES))

left, right = st.columns([1, 1])

with left:
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

with right:
    st.subheader("Who has contributed more?")
    st.pyplot(draw_contribution_chart(patrick_total, storm_total))

st.subheader("Recent Runs")
if not df.empty:
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
else:
    st.info("No runs added yet.")
