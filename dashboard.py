import os
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ---------------- CONFIG ----------------
API_URL = os.getenv("API_URL", "http://127.0.0.1:5001/get-data")


st.set_page_config(page_title="🌱 Plant AI Dashboard", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background: rgba(255,255,255,0.05);
    box-shadow: 0px 0px 15px rgba(0,255,150,0.2);
    text-align: center;
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LANGUAGE ----------------
lang = st.sidebar.selectbox("🌍 Language", ["English", "Hindi", "Telugu"])

# ---------------- TITLE ----------------
st.title("🌱 Plant AI Dashboard")

# ---------------- SESSION STORAGE ----------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "time", "temperature", "humidity", "moisture", "signal"
    ])

# ---------------- FETCH DATA ----------------
def fetch_data():
    try:
        res = requests.get(API_URL, timeout=2)
        if res.status_code == 200:
            return res.json()
    except:
        return None

# ---------------- AUTO REFRESH ----------------
refresh = st.button("🔄 Refresh Data")

data = fetch_data()

# ---------------- FALLBACK DATA ----------------
if data is None:
    data = {
        "temperature": 30,
        "humidity": 50,
        "moisture": 40,
        "signal": 0.5
    }

# ---------------- STORE DATA ----------------
new_row = {
    "time": datetime.now(),
    "temperature": float(data["temperature"]),
    "humidity": float(data["humidity"]),
    "moisture": float(data["moisture"]),
    "signal": float(data.get("signal", 0))
}

st.session_state.data = pd.concat(
    [st.session_state.data, pd.DataFrame([new_row])],
    ignore_index=True
)

df = st.session_state.data.tail(50)

# ---------------- CARDS ----------------
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f'<div class="card">🌡 Temp<br>{data["temperature"]} °C</div>', unsafe_allow_html=True)
col2.markdown(f'<div class="card">💧 Humidity<br>{data["humidity"]} %</div>', unsafe_allow_html=True)
col3.markdown(f'<div class="card">🌱 Moisture<br>{data["moisture"]}</div>', unsafe_allow_html=True)
col4.markdown(f'<div class="card">📡 Bio Signal<br>{data.get("signal", 0)}</div>', unsafe_allow_html=True)

# ---------------- GRAPH ----------------
st.subheader("📊 Live Sensor Graph")

st.line_chart(
    df.set_index("time")[["temperature", "humidity", "moisture"]]
)

# ---------------- BIOSIGNAL GRAPH ----------------
st.subheader("📡 Bio Signal Analysis")

st.line_chart(
    df.set_index("time")[["signal"]]
)

# ---------------- AI ANALYSIS ----------------
st.subheader("🤖 AI Analysis")

issues = []
solutions = []

if data["moisture"] < 30:
    issues.append("Underwatering")
    solutions.append("Increase watering")

if data["temperature"] > 35:
    issues.append("Heat Stress")
    solutions.append("Provide shade")

if data["humidity"] < 40:
    issues.append("Low Humidity")
    solutions.append("Spray water")

if data.get("signal", 0) < 0.3:
    issues.append("Plant Stress Detected")
    solutions.append("Check nutrients & environment")

col5, col6 = st.columns(2)

with col5:
    st.markdown("### ⚠ Causes")
    if issues:
        for i in issues:
            st.write(f"• {i}")
    else:
        st.write("✅ Healthy")

with col6:
    st.markdown("### ✅ Solutions")
    if solutions:
        for s in solutions:
            st.write(f"• {s}")
    else:
        st.write("👍 No action needed")
