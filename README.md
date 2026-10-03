# ⚡ EV Fleet Telemetry & Anomaly Analytics Engine

I built this project to get hands-on with something that genuinely interests me — how companies monitor electric vehicle fleets in real time and catch problems before they become expensive (or dangerous) failures. Battery overheating is one of the biggest safety concerns in EVs, so I wanted to simulate a system that could actually catch that kind of issue as it happens.

## What it does

The project simulates telemetry data (speed, battery temperature, state-of-charge) coming in from multiple EVs, stores it in a database, and then runs it through a detection system I built using SQL window functions. If any vehicle's battery temperature jumps by 15°C or more between readings, the system flags it immediately on a live dashboard.

It's not connected to real vehicles (I didn't have access to actual EV sensor data), but the pipeline and logic are built the way a real system would work — so swapping in real sensor data later wouldn't require rebuilding anything major.

## Tech I used

- **Python** — for the data pipeline and simulation logic
- **SQLite** — a lightweight database to store all the telemetry records
- **SQL window functions** (`LAG`, `PARTITION BY`) — this is the core logic that compares each new reading against the previous one, *per vehicle*
- **Pandas** — for querying and shaping the data
- **Streamlit** — to build the dashboard without writing any HTML/CSS
- **Plotly** — for the interactive temperature trend charts

## The part I'm most proud of

The anomaly detection query:

```sql
WITH TempDiff AS (
    SELECT 
        vehicle_id, timestamp, temperature,
        LAG(temperature) OVER (PARTITION BY vehicle_id ORDER BY timestamp) as prev_temp
    FROM fleet_telemetry
)
SELECT * FROM TempDiff WHERE (temperature - prev_temp) >= 15;
```

`LAG()` pulls the previous temperature reading so I can compare it to the current one. `PARTITION BY vehicle_id` was important to get right — without it, the system would end up comparing one vehicle's reading to a *different* vehicle's previous reading, which would make the whole thing meaningless. Getting this logic correct taught me a lot about how window functions actually work versus just copying syntax.

## What the dashboard shows

- Live summary metrics - total records, valid readings, filtered noise, average battery temp
- A temperature trend chart across all vehicles over time
- A real-time alert table that shows exactly which vehicle spiked, by how much, and when
- A raw data table for anyone who wants to dig into the full dataset

## How to run it

```bash
git clone https://github.com/KhushiCharde/EV-fleet-telementry-dashboard.git
pip install streamlit pandas plotly
python pipeline.py        # generates telemetry data
streamlit run dashboard.py   # launches the dashboard
```

## Project structure

```
├── pipeline.py       # generates and stores simulated telemetry data
├── dashboard.py       # Streamlit dashboard + anomaly detection logic
├── analytics.py       # additional analysis
├── ev_fleet.db         # SQLite database (created when you run pipeline.py)
└── README.md
```

## What I'd add if I kept building this

- Connect it to actual EV sensor data instead of simulated data
- Let users adjust the anomaly threshold instead of it being fixed at 15°C
- Move to PostgreSQL for handling a much larger fleet
- Deploy it properly so it's live instead of just running locally

## About me

I'm a final-year Computer Engineering student, and this was part of how I taught myself practical SQL and data pipeline work outside of coursework.
