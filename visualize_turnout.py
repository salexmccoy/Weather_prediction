import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load DB credentials
load_dotenv("sql.env")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

# Connect and load event + weather + turnout data
def fetch_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT 
            e.event_type,
            e.event_date,
            w.temp_f,
            w.precip_prob,
            w.cloud_coverage,
            a.actual_turnout
        FROM events e
        JOIN weather_forecasts w ON e.event_id = w.event_id
        JOIN actuals a ON e.event_id = a.event_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Plotting functions
def plot_turnout(df):
    plt.figure(figsize=(10, 5))
    plt.scatter(df["temp_f"], df["actual_turnout"], alpha=0.6)
    plt.title("Turnout vs Temperature")
    plt.xlabel("Temperature (°F)")
    plt.ylabel("Actual Turnout")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.scatter(df["precip_prob"], df["actual_turnout"], alpha=0.6, color='orange')
    plt.title("Turnout vs Precipitation Probability")
    plt.xlabel("Precipitation Probability")
    plt.ylabel("Actual Turnout")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(10, 5))
    df.boxplot(column="actual_turnout", by="event_type", grid=False)
    plt.title("Turnout by Event Type")
    plt.suptitle("")  # Removes default title
    plt.xlabel("Event Type")
    plt.ylabel("Actual Turnout")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    df = fetch_data()
    print(df.head())
    plot_turnout(df)
