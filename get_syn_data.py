import random
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv("sql.env")


# DB config from environment
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

print("Connecting with:", DB_CONFIG)


EVENT_TYPES = ["Farmers Market", "Outdoor Concert", "Youth Sports", "Food Truck Rally"]
LOCATIONS = ["Springfield", "Fairview", "Rivertown", "Mapleton"]
HOURS = [9, 10, 11, 16, 17, 18]

def generate_events(n=100):
    events = []
    for _ in range(n):
        event_type = random.choice(EVENT_TYPES)
        location = random.choice(LOCATIONS)
        event_hour = random.choice(HOURS)

        future_date = datetime.today() + timedelta(days=random.randint(1, 30))
        event_date = future_date.date()

        events.append((event_type, event_date, event_hour, location))
    return events

def insert_events(events):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO events (event_type, event_date, event_hour, location)
            VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(insert_query, events)
        conn.commit()
        print(f"{cursor.rowcount} events inserted successfully.")
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error inserting events:", e)

if __name__ == "__main__":
    synthetic_events = generate_events(n=100)
    insert_events(synthetic_events)
