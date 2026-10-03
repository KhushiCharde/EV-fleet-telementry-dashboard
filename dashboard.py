import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Configure Streamlit page settings (title, icon, wide layout for dashboard)
st.set_page_config(
    page_title="EV Fleet Telemetry Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Dashboard header and description
st.title("⚡ EV Fleet Telemetry & Anomaly Analytics Engine")
st.markdown("Real-time battery temperature tracking, sensor noise filtering, and thermal spike detection.")

# Connect to the EV fleet telemetry database
conn = sqlite3.connect("ev_fleet.db")

# Create 4-column layout for summary metrics
col1, col2, col3, col4 = st.columns(4)

# Fetch summary statistics from database
total_records = pd.read_sql_query("SELECT COUNT(*) as count FROM fleet_telemetry", conn)['count'][0]
normal_records = pd.read_sql_query("SELECT COUNT(*) as count FROM fleet_telemetry WHERE status='NORMAL'", conn)['count'][0]
noise_records = pd.read_sql_query("SELECT COUNT(*) as count FROM fleet_telemetry WHERE status='NOISE'", conn)['count'][0]

# Calculate average battery temperature (only valid/normal readings)
avg_temp = pd.read_sql_query("SELECT ROUND(AVG(temperature), 2) as avg FROM fleet_telemetry WHERE status='NORMAL'", conn)['avg'][0]

# Display key metrics as cards
col1.metric("Total Telemetry Logs", total_records)
col2.metric("Valid Readings", normal_records)
col3.metric("Filtered Sensor Noise (>100°C)", noise_records, delta=f"{noise_records} Noise Alerts", delta_color="inverse")
col4.metric("Avg Battery Temp", f"{avg_temp} °C")

st.markdown("---")

# Section: Temperature trend line chart across all vehicles
st.subheader("📈 Vehicle Temperature Timeline")

df_telemetry = pd.read_sql_query("SELECT vehicle_id, timestamp, temperature, status FROM fleet_telemetry WHERE status IN ('NORMAL', 'THERMAL_ALERT') ORDER BY timestamp", conn)

# Plot temperature trends per vehicle using Plotly line chart
fig = px.line(
    df_telemetry, 
    x="timestamp", 
    y="temperature", 
    color="vehicle_id", 
    markers=True,
    title="Battery Temperature Trends Across Fleet (°C)",
    labels={"temperature": "Temperature (°C)", "timestamp": "Timestamp", "vehicle_id": "Vehicle"}
)
st.plotly_chart(fig, use_container_width=True)

# Section: Detect sudden thermal spikes using SQL window function (LAG)
st.subheader("🚨 Detected Thermal Spike Anomalies (Temp Rise ≥ 15°C)")

# Compare each reading with the previous reading per vehicle to catch sudden temp jumps
spike_query = """
WITH TempDiff AS (
    SELECT 
        vehicle_id, timestamp, temperature, speed, soc,
        LAG(temperature) OVER (PARTITION BY vehicle_id ORDER BY timestamp) as prev_temp
    FROM fleet_telemetry
    WHERE status IN ('NORMAL', 'THERMAL_ALERT')
)
SELECT 
    vehicle_id AS "Vehicle ID",
    timestamp AS "Timestamp",
    temperature AS "Current Temp (°C)",
    prev_temp AS "Previous Temp (°C)",
    (temperature - prev_temp) AS "Spike Jump (°C)"
FROM TempDiff
WHERE (temperature - prev_temp) >= 15;
"""

df_spikes = pd.read_sql_query(spike_query, conn)

# Show warning if anomalies found, else confirm all vehicles normal
if not df_spikes.empty:
    st.error("⚠️ Critical Thermal Spikes Identified in Fleet!")
    st.dataframe(df_spikes, use_container_width=True)
else:
    st.success("✅ All vehicles operating within normal thermal range. No spikes detected.")

# Section: Raw data table for full transparency/debugging
st.subheader("📋 Raw Filtered Database Records")
df_all = pd.read_sql_query("SELECT * FROM fleet_telemetry", conn)
st.dataframe(df_all, use_container_width=True)

# Close database connection
conn.close()