import os
import psycopg2
import pandas as pd
import joblib
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv("sql.env")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

MODEL_PATH = "turnout_model.pkl"
MODEL_VERSION = "v1.0"

def load_model():
    return joblib.load(MODEL_PATH)

def fetch_unpredicted_events():
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT 
            e.event_id,
            e.event_type,
            e.event_hour,
            w.temp_f,
            w.precip_prob,
            w.cloud_coverage
        FROM events e
        JOIN weather_forecasts w ON e.event_id = w.event_id
        WHERE e.event_id NOT IN (
            SELECT event_id FROM predictions
        )
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def store_predictions(predictions_df):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO predictions (
            event_id, predicted_turnout, model_version, prediction_time
        ) VALUES (%s, %s, %s, %s)
    """
    now = datetime.now()
    rows = [
        (row.event_id, int(row.predicted_turnout), MODEL_VERSION, now)
        for _, row in predictions_df.iterrows()
    ]
    cursor.executemany(insert_query, rows)
    conn.commit()
    print(f"✅ Stored {cursor.rowcount} predictions.")
    cursor.close()
    conn.close()

def main():
    model = load_model()
    df = fetch_unpredicted_events()

    if df.empty:
        print("🎉 No new events to predict.")
        return

    X = df.drop(columns=["event_id"])
    predictions = model.predict(X)
    df["predicted_turnout"] = predictions

    print(df[["event_id", "predicted_turnout"]].head())
    store_predictions(df)

if __name__ == "__main__":
    main()
