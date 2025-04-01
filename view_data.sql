SELECT 
    e.event_id,
    e.event_type,
    e.event_date,
    e.event_hour,
    e.location,
    w.temp_f,
    w.precip_prob,
    w.wind_speed,
    w.cloud_coverage,
    w.forecast_time
FROM events e
LEFT JOIN weather_forecasts w
    ON e.event_id = w.event_id
ORDER BY e.event_date, e.event_hour
LIMIT 20;
