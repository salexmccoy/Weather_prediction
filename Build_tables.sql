CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    event_type TEXT,
    event_date DATE,
    event_hour INT,
    location TEXT
);

CREATE TABLE weather_forecasts (
    weather_id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(event_id),
    temp_f FLOAT,
    precip_prob FLOAT,
    wind_speed FLOAT,
    cloud_coverage INT,
    forecast_time TIMESTAMP
);

CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(event_id),
    predicted_turnout INT,
    model_version TEXT,
    prediction_time TIMESTAMP
);

CREATE TABLE actuals (
    event_id INT PRIMARY KEY REFERENCES events(event_id),
    actual_turnout INT
);
