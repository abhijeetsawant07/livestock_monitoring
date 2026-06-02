import streamlit as st
import pandas as pd
import sqlite3
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Goat Monitoring", layout="wide")

st.title("🐐 Farm Monitoring Dashboard")

# ----------------------------
# Auto Refresh
# ----------------------------
st_autorefresh(interval=5000, key="refresh")

# ----------------------------
# Navigation
# ----------------------------
page = st.sidebar.radio(
    "Navigation",
    [
        "Farm Overview",
        "Animals",
        "Alerts"
    ]
)

# ----------------------------
# Load Goat Registry
# ----------------------------
try:
    conn = sqlite3.connect("goat.db")

    goats_df = pd.read_sql_query(
        "SELECT * FROM goats",
        conn
    )

    conn.close()

except Exception:
    goats_df = pd.DataFrame()

# ----------------------------
# Load Monitoring Data
# ----------------------------
df = pd.DataFrame()

try:
    url = "https://livestock-monitoring.onrender.com/data"

    response = requests.get(url, timeout=5)

    if response.status_code == 200:

        data = response.json()

        if data:
            df = pd.DataFrame(
                data,
                columns=[
                    "id",
                    "goat_id",
                    "temperature",
                    "movement",
                    "feed",
                    "timestamp"
                ]
            )

            df["timestamp"] = pd.to_datetime(df["timestamp"])

except Exception:
    pass


# =====================================================
# FARM OVERVIEW PAGE
# =====================================================
if page == "Farm Overview":

    st.header("🐄 Farm Overview")

    if df.empty:
        st.info("No monitoring data available yet.")
    else:

        goat_ids = df["goat_id"].unique()

        cols = st.columns(len(goat_ids))

        for i, goat in enumerate(goat_ids):

            goat_df = df[
                df["goat_id"] == goat
            ].sort_values(by="timestamp")

            latest = goat_df.iloc[-1]

            movement = latest["movement"]

            if movement < 3:
                cols[i].error(f"{goat}\n🔴 INACTIVE")

            elif movement < 8:
                cols[i].warning(f"{goat}\n🟡 LOW ACTIVITY")

            else:
                cols[i].success(f"{goat}\n🟢 NORMAL")

        st.subheader("📈 Recent Monitoring Data")

        st.dataframe(
            df.sort_values(
                by="timestamp",
                ascending=False
            ).head(20)
        )


# =====================================================
# ANIMALS PAGE
# =====================================================
elif page == "Animals":

    st.header("🐐 Animal Registry")

    if goats_df.empty:
        st.warning("No animals registered.")
    else:

        selected_goat = st.selectbox(
            "Select Animal",
            goats_df["goat_id"]
        )

        goat = goats_df[
            goats_df["goat_id"] == selected_goat
        ].iloc[0]

        st.subheader(f"🐐 {goat['name']}")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Breed:** {goat['breed']}")
            st.write(f"**Age:** {goat['age']} years")

        with col2:
            st.write(f"**Weight:** {goat['weight']} kg")
            st.write(f"**Gender:** {goat['gender']}")

        st.divider()

        st.subheader("📊 Current Health Status")

        if not df.empty:

            goat_data = df[
                df["goat_id"] == selected_goat
            ]

            if not goat_data.empty:

                latest = goat_data.sort_values(
                    by="timestamp"
                ).iloc[-1]

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Temperature",
                    latest["temperature"]
                )

                col2.metric(
                    "Movement",
                    latest["movement"]
                )

                col3.metric(
                    "Feed Intake",
                    latest["feed"]
                )

                if latest["movement"] < 3:
                    st.error(
                        "🔴 Goat inactive. Check immediately."
                    )

                elif latest["movement"] < 8:
                    st.warning(
                        "🟡 Goat activity is low."
                    )

                else:
                    st.success(
                        "🟢 Goat is healthy and active."
                    )

            else:
                st.info(
                    "No monitoring data available for this animal yet."
                )

        else:
            st.info(
                "Monitoring system not currently sending data."
            )

        st.divider()

        st.subheader("📋 Health History")

        try:

            conn = sqlite3.connect("goat.db")

            history_df = pd.read_sql_query(
                f"""
                SELECT *
                FROM health_events
                WHERE goat_id = '{selected_goat}'
                ORDER BY timestamp DESC
                """,
                conn
            )

            conn.close()

            if not history_df.empty:

                st.dataframe(
                    history_df[
                        [
                            "timestamp",
                            "event_type",
                            "description"
                        ]
                    ]
                )

            else:
                st.info(
                    "No health history available."
                )

        except Exception:
            st.info(
                "No health history available."
            )
# =====================================================
# ALERTS PAGE
# =====================================================
elif page == "Alerts":

    st.header("🚨 Alert History")

    try:

        conn = sqlite3.connect("goat.db")

        alert_df = pd.read_sql_query(
            "SELECT * FROM alerts",
            conn
        )

        conn.close()

        if not alert_df.empty:

            alert_df["timestamp"] = pd.to_datetime(
                alert_df["timestamp"]
            )

            st.dataframe(
                alert_df.sort_values(
                    by="timestamp",
                    ascending=False
                )
            )

        else:
            st.info("No alerts available.")

    except Exception:
        st.info("No alerts available.")
