import os
import psycopg2
import random
from dotenv import load_dotenv

load_dotenv("sql.env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

# Baseline attendance per event type
BASELINE_ATTENDANCE = {
    "Farmers Market": 200,
    "Outdoor Concert": 500,
    "Youth Sports": 150,
    "Food Truck Rally": 300
}

def simulate_turnout(event_type, temp, precip, clouds):
    base = BASELINE_ATTENDANCE.get(event_type, 100)
    modifier = 1.0

    # Temperature penalty
    if temp < 50 or temp > 85:
        modifier *= 0.75

    # Rain penalty
    if precip > 0.3:
        modifier *= random.uniform(0.4, 0.6)

    # Cloudiness
    if clouds > 75:
        modifier *= 0.9

    # Add noise
    noise = random.gauss(0, base * 0.1)
    turnout = int(base * modifier + noise)
    return max(turnout, 0)  # No negative turnout!

def simulate_and_insert_turnouts():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Join events + weather
    cursor.execute("""
        SELECT 
            e.event_id, e.event_type, 
            w.temp_f, w.precip_prob, w.cloud_coverage
        FROM events e
        JOIN weather_forecasts w ON e.event_id = w.event_id
        WHERE e.event_id NOT IN (SELECT event_id FROM actuals)
    """)
    rows = cursor.fetchall()

    for event_id, event_type, temp, precip, clouds in rows:
        turnout = simulate_turnout(event_type, temp, precip, clouds)
        cursor.execute(
            "INSERT INTO actuals (event_id, actual_turnout) VALUES (%s, %s)",
            (event_id, turnout)
        )
        print(f"✅ Simulated turnout {turnout} for event {event_id} ({event_type})")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    simulate_and_insert_turnouts()
