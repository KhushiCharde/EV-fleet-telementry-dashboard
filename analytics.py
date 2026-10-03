import sqlite3

# Database Connection
conn = sqlite3.connect('ev_telemetry.db')
cursor = conn.cursor()

print("=" * 65)
print("             EV FLEET TELEMETRY ANALYTICS REPORT             ")
print("=" * 65)

# Query 1: Fleet Summary
query_summary = '''
SELECT 
    status,
    COUNT(*) as total_records,
    ROUND(AVG(battery_temp_c), 2) as avg_battery_temp,
    ROUND(AVG(speed_kmph), 2) as avg_speed
FROM telemetry_data
GROUP BY status;
'''
cursor.execute(query_summary)
print("\n1. FLEET STATUS BREAKDOWN:")
print(f"{'STATUS':<15} | {'RECORDS':<10} | {'AVG TEMP (°C)':<15} | {'AVG SPEED (km/h)':<15}")
print("-" * 65)
for row in cursor.fetchall():
    print(f"{row[0]:<15} | {row[1]:<10} | {row[2]:<15} | {row[3]:<15}")

# Query 2: High-Risk Vehicles
query_alerts = '''
SELECT 
    vehicle_id,
    COUNT(CASE WHEN status = 'THERMAL_ALERT' THEN 1 ELSE NULL END) as thermal_alerts_count,
    COUNT(CASE WHEN status = 'NOISE' THEN 1 ELSE NULL END) as sensor_noise_count,
    MAX(battery_temp_c) as max_recorded_temp
FROM telemetry_data
GROUP BY vehicle_id
HAVING thermal_alerts_count > 0 OR sensor_noise_count > 0;
'''
cursor.execute(query_alerts)
print("\n2. HIGH-RISK VEHICLES & ANOMALY SUMMARY:")
print(f"{'VEHICLE ID':<12} | {'ALERTS':<10} | {'NOISE LOGS':<12} | {'MAX TEMP (°C)':<15}")
print("-" * 65)
for row in cursor.fetchall():
    print(f"{row[0]:<12} | {row[1]:<10} | {row[2]:<12} | {row[3]:<15}")

# Query 3: Thermal Alert Log Details
query_alert_details = '''
SELECT 
    vehicle_id,
    timestamp,
    battery_temp_c,
    speed_kmph,
    soc_percent
FROM telemetry_data
WHERE status = 'THERMAL_ALERT'
ORDER BY timestamp DESC;
'''
cursor.execute(query_alert_details)
print("\n3. CRITICAL THERMAL SPIKE INCIDENTS DETAILED LOG:")
print(f"{'VEHICLE ID':<12} | {'TIMESTAMP':<20} | {'TEMP (°C)':<10} | {'SPEED':<8} | {'SOC (%)':<8}")
print("-" * 65)
for row in cursor.fetchall():
    print(f"{row[0]:<12} | {row[1]:<20} | {row[2]:<10} | {row[3]:<8} | {row[4]:<8}")

conn.close()