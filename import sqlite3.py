import sqlite3

# Connect to (or create) the EV telemetry database
conn = sqlite3.connect('ev_telemetry.db')
cursor = conn.cursor()

# Create table to store EV fleet telemetry records
cursor.execute('''
CREATE TABLE IF NOT EXISTS telemetry_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    speed_kmph REAL,
    battery_temp_c REAL,
    soc_percent INTEGER,
    status TEXT DEFAULT 'NORMAL'
)
''')

# Save changes and close connection
conn.commit()
conn.close()
print("Database and Table Created Successfully!")