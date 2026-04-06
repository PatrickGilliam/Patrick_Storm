import streamlit as st
import pandas as pd
import os
from datetime import datetime

TARGET_MILES = 3000
DATA_FILE = "running_tracker.csv"

st.set_page_config(page_title="Patrick & Storm Running Tracker", page_icon="🏃")

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

st.title("🏃 Patrick & Storm Running Tracker")
st.write("Run together across the distance from Kamloops, BC to Wesley Chapel, FL.")

df = load_data()
patrick_total, storm_total, combined_total, remaining = get_summary(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Patrick", f"{patrick_total:.2f} mi")
col2.metric("Storm", f"{storm_total:.2f} mi")
col3.metric("Combined", f"{combined_total:.2f} mi")
col4.metric("Remaining", f"{remaining:.2f} mi")

progress = min(combined_total / TARGET_MILES, 1.0)
st.progress(progress)
st.caption(f"{progress*100:.1f}% of the journey completed")

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
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
else:
    st.info("No runs added yet.")
