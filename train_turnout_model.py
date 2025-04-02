import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score

import joblib

# Load environment variables
load_dotenv("sql.env")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT 
            e.event_type,
            e.event_hour,
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

def train_model(df):
    X = df.drop("actual_turnout", axis=1)
    y = df["actual_turnout"]

    # Define preprocessing
    numeric_features = ["event_hour", "temp_f", "precip_prob", "cloud_coverage"]
    categorical_features = ["event_type"]

    preprocessor = ColumnTransformer(transformers=[
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(), categorical_features)
    ])

    model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print("Model Evaluation:")
    print(f"MAE: {mean_absolute_error(y_test, preds):.2f}")
    print(f"R² Score: {r2_score(y_test, preds):.2f}")

    return model

if __name__ == "__main__":
    df = load_data()
    print(df.head())
    model = train_model(df)

    # Save trained model to file
    joblib.dump(model, "turnout_model.pkl")
    print("Model saved to turnout_model.pkl")
