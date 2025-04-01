SELECT 
    e.event_type, e.event_date, w.temp_f, w.precip_prob, a.actual_turnout
FROM events e
JOIN weather_forecasts w ON e.event_id = w.event_id
JOIN actuals a ON e.event_id = a.event_id
LIMIT 20;
