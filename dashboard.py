import streamlit as st
import pandas as pd
import sqlite3
from streamlit_autorefresh import st_autorefresh
import requests

st.set_page_config(page_title="Goat Monitoring", layout="wide")
st.title("🐐 Farm Monitoring Dashboard")

# ----------------------------
# Auto refresh every 5 seconds
# ----------------------------
st_autorefresh(interval=5000, key="refresh")


# ----------------------------
# Load data from SQLite
# ----------------------------
#try:
#    conn = sqlite3.connect("goat.db")
#    df = pd.read_sql_query("SELECT * FROM goat_data", conn)
#    conn.close()
#except Exception as e:
#   st.error(f"DB error: {e}")
#    st.stop()

#if df.empty:
#    st.warning("Waiting for data...")
#    st.stop()

# ----------------------------
# Load data from Cloud API
# ----------------------------


try:
    url = "https://livestock-monitoring.onrender.com/data"
    response = requests.get(url)

    if response.status_code != 200:
        st.error("Failed to fetch data from server")
        st.stop()

    data = response.json()

    if not data:
        st.warning("Waiting for data...")
        st.stop()

    df = pd.DataFrame(data, columns=[
        "id", "goat_id", "temperature", "movement", "feed", "timestamp"
    ])
except Exception as e:
    st.error(f"API error: {e}")
    st.stop()


# Convert timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Get goat list
goat_ids = df['goat_id'].unique()


# ----------------------------
# 🟢 HERD OVERVIEW
# ----------------------------
st.subheader("🐄 Herd Overview")

cols = st.columns(len(goat_ids))

for i, goat in enumerate(goat_ids):
    goat_df = df[df['goat_id'] == goat].sort_values(by='timestamp')
    latest = goat_df.iloc[-1]

    # Simple health logic
    if latest['temperature'] > 40 or latest['movement'] < 5 or latest['feed'] < 200:
        cols[i].error(f"{goat}\n🔴 ALERT")
    else:
        cols[i].success(f"{goat}\n🟢 NORMAL")


# ----------------------------
# 🔍 GOAT DETAILS
# ----------------------------
st.subheader("🔍 Goat Details")

selected_goat = st.selectbox("Select Goat", goat_ids)

filtered_df = df[df['goat_id'] == selected_goat].copy()
filtered_df = filtered_df.sort_values(by='timestamp')

latest = filtered_df.iloc[-1]

col1, col2, col3 = st.columns(3)

col1.metric("Temperature (°C)", latest['temperature'])
col2.metric("Movement", latest['movement'])
col3.metric("Feed Intake", latest['feed'])


# ----------------------------
# 📈 CHARTS
# ----------------------------
st.subheader("📈 Trends")

st.line_chart(filtered_df.set_index('timestamp')[['temperature']])
st.line_chart(filtered_df.set_index('timestamp')[['movement']])
st.line_chart(filtered_df.set_index('timestamp')[['feed']])


# ----------------------------
# 📄 DATA TABLE
# ----------------------------
st.subheader("📄 Recent Data")

st.dataframe(filtered_df.tail(20))


# ----------------------------
# 🚨 ALERT HISTORY
# ----------------------------
st.subheader("🚨 Alert History")

try:
    conn = sqlite3.connect("goat.db")
    alert_df = pd.read_sql_query("SELECT * FROM alerts", conn)
    conn.close()

    if not alert_df.empty:
        alert_df['timestamp'] = pd.to_datetime(alert_df['timestamp'])
        st.dataframe(alert_df.sort_values(by='timestamp', ascending=False).head(20))
    else:
        st.info("No alerts yet")

except Exception:
    st.info("No alerts yet")
