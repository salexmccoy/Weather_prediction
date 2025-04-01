import os
import psycopg2
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv("sql.env")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}
OWM_API_KEY = os.getenv("OWM_API_KEY")

# Fetch 5-day forecast for a city and match it to the event datetime
def get_forecast_for_event(city, event_datetime, api_key):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f"API error for {city}: {e}")
        return None

    forecast_data = response.json().get("list", [])
    best_match = None
    smallest_diff = timedelta.max

    for entry in forecast_data:
        forecast_time = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
        diff = abs(event_datetime - forecast_time)
        if diff < smallest_diff:
            smallest_diff = diff
            best_match = entry

    if best_match:
        return {
            "forecast_time": best_match["dt_txt"],
            "temp": best_match["main"]["temp"],
            "precip": best_match.get("pop", 0.0),
            "wind": best_match["wind"]["speed"],
            "clouds": best_match["clouds"]["all"]
        }
    return None

# Insert forecast into database
def insert_weather_forecast(conn, event_id, weather):
    cursor = conn.cursor()
    query = """
        INSERT INTO weather_forecasts (
            event_id, temp_f, precip_prob, wind_speed, cloud_coverage, forecast_time
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        event_id,
        weather["temp"],
        weather["precip"],
        weather["wind"],
        weather["clouds"],
        weather["forecast_time"]
    ))
    conn.commit()
    cursor.close()

# Main function to fetch and store weather forecasts
def fetch_and_store_forecasts():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT event_id, event_date, event_hour, location FROM events")
    events = cursor.fetchall()

    for event_id, event_date, event_hour, location in events:
        event_dt = datetime.combine(event_date, datetime.min.time()) + timedelta(hours=event_hour)
        forecast = get_forecast_for_event(location, event_dt, OWM_API_KEY)
        if forecast:
            insert_weather_forecast(conn, event_id, forecast)
            print(f"✅ Stored forecast for event {event_id} ({location} @ {event_dt})")
        else:
            print(f"❌ Could not fetch forecast for event {event_id} ({location})")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    fetch_and_store_forecasts()
