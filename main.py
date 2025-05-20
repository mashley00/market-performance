from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
import pandas as pd
import logging
from datetime import datetime, timedelta

# -------------------------
# Logging Configuration
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketPerformance")

# -------------------------
# Initialize FastAPI App
# -------------------------
app = FastAPI(title="Market Performance Tool", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------------------
# Load Dataset
# -------------------------
CSV_URL = "https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv"

try:
    df = pd.read_csv(CSV_URL, encoding="utf-8")
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["zip_code"] = df.get("zip_code", "").fillna("").astype(str).str.strip().str.zfill(5)
    logger.info(f"Loaded dataset: {df.shape}")
except Exception as e:
    logger.exception("Error loading dataset.")
    raise e

# -------------------------
# Topic Map
# -------------------------
TOPIC_MAP = {
    "TIR": "taxes_in_retirement_567",
    "EP": "estate_planning_567",
    "SS": "social_security_567"
}

# -------------------------
# Market Health Endpoint
# -------------------------
@app.get("/market-health", response_class=HTMLResponse)
async def market_health(
    zip: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    topic: Optional[str] = None
):
    reference_date = pd.Timestamp.today()
    topic_label = TOPIC_MAP.get(topic.upper()) if topic else None

    if zip:
        zip_str = str(zip).strip().zfill(5)
        filtered = df[df["zip_code"] == zip_str]
        area_label = f"ZIP Code {zip_str}"
    elif city and state:
        city_clean = city.strip().lower()
        state_clean = state.strip().upper()
        filtered = df[
            (df["city"].str.strip().str.lower() == city_clean) &
            (df["state"].str.strip().str.upper() == state_clean)
        ]
        area_label = f"{city.title()}, {state_clean}"
    else:
        return HTMLResponse("<h3>Error: Please provide either a ZIP code or city/state.</h3>")

    if topic_label:
        filtered = filtered[filtered["topic"] == topic_label]

    if filtered.empty:
        return HTMLResponse(f"<h3>No events found for {area_label}</h3>")

    last_event = filtered.sort_values("event_date", ascending=False).iloc[0]
    days_since_last = (reference_date - last_event["event_date"]).days
    count_30 = (filtered["event_date"] >= reference_date - timedelta(days=30)).sum()

    html = f"""
    <h2>📊 Market Health for {area_label}</h2>
    <p><b>Topic:</b> {topic or 'All Topics'}</p>
    <p><b>Most Recent Event:</b> {last_event['event_date'].strftime('%Y-%m-%d')}</p>
    <p><b>Days Since Last Event:</b> {days_since_last} days</p>
    <p><b>Events in Last 30 Days:</b> {count_30}</p>
    """
    return HTMLResponse(html)

# -------------------------
# CPR Prediction Endpoint
# -------------------------
@app.get("/predict-cpr", response_class=HTMLResponse)
async def predict_cpr(
    zip: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    topic: Optional[str] = None
):
    reference_date = pd.Timestamp.today()
    topic_upper = topic.upper() if topic else None
    topic_full = TOPIC_MAP.get(topic_upper) if topic_upper else None

    if zip:
        zip_str = str(zip).strip().zfill(5)
        filtered = df[df["zip_code"] == zip_str]
        area_label = f"ZIP Code {zip_str}"
    elif city and state:
        city_clean = city.strip().lower()
        state_clean = state.strip().upper()
        filtered = df[
            (df["city"].str.strip().str.lower() == city_clean) &
            (df["state"].str.strip().str.upper() == state_clean)
        ]
        area_label = f"{city.title()}, {state_clean}"
    else:
        return HTMLResponse("<h3>Error: Please provide either a ZIP code or city/state.</h3>")

    if topic_full:
        filtered = filtered[filtered["topic"] == topic_full]

    if filtered.empty:
        return HTMLResponse(f"<h3>No events found for {area_label}</h3>")

    last_event = filtered.sort_values("event_date", ascending=False).iloc[0]
    days_since_last = (reference_date - last_event["event_date"]).days


