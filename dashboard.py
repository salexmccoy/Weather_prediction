import os
import psycopg2
import pandas as pd
import streamlit as st
import altair as alt
from dotenv import load_dotenv

# Load DB credentials
load_dotenv("sql.env")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

# 🎨 Define a consistent color palette for event types
EVENT_COLORS = {
    "Farmers Market": "#1f77b4",
    "Outdoor Concert": "#ff7f0e",
    "Youth Sports": "#2ca02c",
    "Food Truck Rally": "#d62728"
}
event_color_scale = alt.Scale(
    domain=list(EVENT_COLORS.keys()),
    range=list(EVENT_COLORS.values())
)

# 📦 Load event + weather + actual + prediction data
@st.cache_data
def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = """
        SELECT 
            e.event_id,
            e.event_type,
            e.event_date,
            e.event_hour,
            e.location,
            w.temp_f,
            w.precip_prob,
            w.cloud_coverage,
            a.actual_turnout,
            p.predicted_turnout
        FROM events e
        JOIN weather_forecasts w ON e.event_id = w.event_id
        JOIN actuals a ON e.event_id = a.event_id
        JOIN predictions p ON e.event_id = p.event_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ────────────────────────────────────────────────────────────────

# Streamlit UI setup
st.set_page_config(page_title="Event Turnout Dashboard", layout="wide")
st.title("📊 Event Turnout Prediction Dashboard")

df = load_data()
df["event_date"] = pd.to_datetime(df["event_date"])  # Ensure datetime format

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    event_types = st.multiselect("Event Types", df["event_type"].unique(), default=df["event_type"].unique())
    date_range = st.date_input("Event Date Range", [df["event_date"].min(), df["event_date"].max()])

# Convert date input to pandas Timestamp
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

# Filter data
filtered = df[
    df["event_type"].isin(event_types) &
    (df["event_date"] >= start_date) &
    (df["event_date"] <= end_date)
]

# ────────────────────────────────────────────────────────────────

# 🎨 Event Type Color Legend
st.subheader("🎨 Event Type Legend")
legend_data = pd.DataFrame({"event_type": list(EVENT_COLORS.keys())})
legend_chart = alt.Chart(legend_data).mark_square(size=200).encode(
    y=alt.Y("event_type:N", axis=alt.Axis(title=None, labelLimit=100)),
    color=alt.Color("event_type:N", scale=event_color_scale, legend=None)
).properties(height=100)
st.altair_chart(legend_chart, use_container_width=False)

# ────────────────────────────────────────────────────────────────

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Events", len(filtered))
col2.metric("Avg Actual Turnout", int(filtered["actual_turnout"].mean()))
col3.metric("Avg Prediction Error", f'{(filtered["predicted_turnout"] - filtered["actual_turnout"]).abs().mean():.1f}')

# 📍 Predicted vs Actual Turnout
st.subheader("📍 Predicted vs Actual Turnout")
st.scatter_chart(filtered[["actual_turnout", "predicted_turnout"]])

# 🌦️ Weather vs Turnout Charts
st.subheader("🌦️ Turnout vs Weather Factors")

col1, col2 = st.columns(2)
with col1:
    st.write("Temp vs Actual Turnout")
    temp_chart = alt.Chart(filtered).mark_circle(size=80, opacity=0.7).encode(
        x=alt.X("temp_f:Q", title="Temperature (°F)"),
        y=alt.Y("actual_turnout:Q", title="Turnout"),
        color=alt.Color("event_type:N", scale=event_color_scale),
        tooltip=["event_type", "temp_f", "actual_turnout"]
    )
    st.altair_chart(temp_chart, use_container_width=True)

with col2:
    st.write("Precip. vs Actual Turnout")
    precip_chart = alt.Chart(filtered).mark_circle(size=80, opacity=0.7).encode(
        x=alt.X("precip_prob:Q", title="Precipitation Probability"),
        y=alt.Y("actual_turnout:Q", title="Turnout"),
        color=alt.Color("event_type:N", scale=event_color_scale),
        tooltip=["event_type", "precip_prob", "actual_turnout"]
    )
    st.altair_chart(precip_chart, use_container_width=True)

# 🎭 Boxplot by Event Type
st.subheader("🎭 Turnout by Event Type")

box_data = filtered[["event_type", "actual_turnout"]]
box_chart = alt.Chart(box_data).mark_boxplot(extent='min-max').encode(
    x=alt.X("event_type:N", title="Event Type"),
    y=alt.Y("actual_turnout:Q", title="Actual Turnout"),
    color=alt.Color("event_type:N", scale=event_color_scale, title="Event Type")
).properties(width=600)
st.altair_chart(box_chart, use_container_width=True)

# 📄 Raw Data
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered)
