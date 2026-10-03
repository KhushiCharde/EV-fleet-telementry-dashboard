import sqlite3
import random
from datetime import datetime, timedelta

# Database Connection
conn = sqlite3.connect('ev_fleet.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS fleet_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT,
        timestamp TEXT,
        speed REAL,
        temperature REAL,
        soc REAL,
        status TEXT
    )
''')

# Mock Vehicles
vehicles = ['EV-101', 'EV-102', 'EV-103', 'EV-104']
start_time = datetime.now()

# Previous temperatures track karne ke liye (Thermal Spike check karne ke liye)
prev_sensor_data = {}

def process_telemetry(vehicle_id, timestamp, speed, temp, soc):
    status = 'NORMAL'
    
    # Rule 1: Noise Filtering (>100°C noise filtering)
    if temp > 100.0 or temp < -10.0:
        status = 'NOISE'
    
    # Rule 2: Thermal Spike Detection (>=15°C increase in <= 5 mins)
    elif vehicle_id in prev_sensor_data:
        last_temp, last_time = prev_sensor_data[vehicle_id]
        time_diff_mins = (timestamp - last_time).total_seconds() / 60.0
        temp_diff = temp - last_temp
        
        if time_diff_mins <= 5.0 and temp_diff >= 15.0:
            status = 'THERMAL_ALERT'
            print(f"🚨 ALERT! Thermal Spike in {vehicle_id}: +{temp_diff:.1f}°C in {time_diff_mins:.1f} mins!")

    # Update state for next check if not noise
    if status != 'NOISE':
        prev_sensor_data[vehicle_id] = (temp, timestamp)

    # Insert into Database
    cursor.execute('''
        INSERT INTO fleet_telemetry (vehicle_id, timestamp, speed, temperature, soc, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (vehicle_id, timestamp.strftime('%Y-%m-%d %H:%M:%S'), speed, temp, soc, status))

print("Processing EV Telemetry Data Pipeline...")

for i in range(50):
    v_id = random.choice(vehicles)
    current_time = start_time + timedelta(minutes=i*2)

    # Normal driving values
    speed = round(random.uniform(20.0, 80.0), 2)
    soc = max(10, 100 - (i * 2))

    # Trigger deliberate noise and thermal spike scenarios for testing
    if i == 15:
        temp = 150.0  # Sensor Noise
    elif i == 25:
        # Force a guaranteed spike for EV-101: baseline reading 2 mins ago, then +18°C now
        v_id = 'EV-101'
        last_t = prev_sensor_data.get('EV-101', (35.0, current_time))[0]
        prev_sensor_data['EV-101'] = (last_t, current_time - timedelta(minutes=2))
        temp = last_t + 18.0  # +18°C spike
    else:
        temp = round(random.uniform(30.0, 42.0), 2)

    process_telemetry(v_id, current_time, speed, temp, soc)

conn.commit()
conn.close()

print("Data Pipeline Executed Successfully! Telemetry stored in database.")