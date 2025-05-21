from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import pandas as pd
import logging
from fuzzywuzzy import fuzz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketPerformance")

app = FastAPI(title="Market Health and CPR Prediction")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

CSV_URL = "https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv"

try:
    df = pd.read_csv(CSV_URL, encoding="utf-8")
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["event_day"] = df["event_date"].dt.day_name()
    df["event_time"] = df["event_time"].astype(str).str.strip()
    if "zip_code" not in df.columns:
        df["zip_code"] = ""
    df["zip_code"] = df["zip_code"].fillna("").astype(str).str.strip().str.zfill(5)
    logger.info(f"Loaded dataset: {df.shape}")
except Exception as e:
    logger.exception("Error loading dataset.")
    raise e

TOPIC_MAP = {
    "TIR": "taxes_in_retirement_567",
    "EP": "estate_planning_567",
    "SS": "social_security_567"
}

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/market.html", response_class=HTMLResponse)
async def serve_market():
    with open("static/market.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/predict.html", response_class=HTMLResponse)
async def serve_predict():
    with open("static/predict.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/market-health", response_class=HTMLResponse)
async def market_health(zip: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None, topic: Optional[str] = None):
    ref_date = pd.Timestamp.today()
    topic_full = TOPIC_MAP.get(topic.upper()) if topic else None
    result = df.copy()

    if topic_full:
        result = result[result['topic'] == topic_full]

    if zip:
        zip_code = str(zip).strip().zfill(5)
        result = result[result['zip_code'] == zip_code]
        area_label = f"ZIP Code {zip_code}"
    elif city and state:
        city_lower = city.strip().lower()
        state_upper = state.strip().upper()
        matches = [c for c in df[df['state'].str.upper() == state_upper]['city'].dropna().unique()
                   if fuzz.token_set_ratio(c.lower(), city_lower) >= 75]
        result = result[result['city'].str.lower().isin([m.lower() for m in matches]) & (result['state'].str.upper() == state_upper)]
        area_label = f"{', '.join(matches)} in {state_upper}"
    else:
        return HTMLResponse("<h3>Error: Please provide either a ZIP or City and State.</h3>", status_code=400)

    if result.empty:
        return HTMLResponse(f"<h3>No events found for {area_label}</h3>", status_code=404)

    recent = result[result['event_date'] >= ref_date - timedelta(days=30)]
    summary = result.groupby('topic').agg({
        'fb_cpr': 'mean',
        'gross_registrants': 'mean',
        'attended_hh': 'mean'
    }).reset_index()

    html = f"<h2>📊 Market Summary for {area_label}</h2>"
    html += f"<p>Total Events in Last 30 Days: {len(recent)}</p>"
    html += "<table border='1'><tr><th>Topic</th><th>Avg CPR</th><th>Avg Registrants</th><th>Avg Attendance</th></tr>"
    for _, row in summary.iterrows():
        html += f"<tr><td>{row['topic']}</td><td>${row['fb_cpr']:.2f}</td><td>{row['gross_registrants']:.1f}</td><td>{row['attended_hh']:.1f}</td></tr>"
    html += "</table>"
    return HTMLResponse(html)

@app.get("/predict-cpr", response_class=HTMLResponse)
async def predict_cpr(zip: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None, topic: Optional[str] = None):
    ref_date = pd.Timestamp.today()
    topic_upper = topic.upper() if topic else None
    topic_full = TOPIC_MAP.get(topic_upper) if topic_upper else None

    result = df.copy()
    if topic_full:
        result = result[result['topic'] == topic_full]

    if zip:
        zip_code = str(zip).strip().zfill(5)
        result = result[result['zip_code'] == zip_code]
        area_label = f"ZIP Code {zip_code}"
    elif city and state:
        city_lower = city.strip().lower()
        state_upper = state.strip().upper()
        matches = [c for c in df[df['state'].str.upper() == state_upper]['city'].dropna().unique()
                   if fuzz.token_set_ratio(c.lower(), city_lower) >= 75]
        result = result[result['city'].str.lower().isin([m.lower() for m in matches]) & (result['state'].str.upper() == state_upper)]
        area_label = f"{', '.join(matches)} in {state_upper}"
    else:
        return HTMLResponse("<h3>Error: Please provide either a ZIP or City and State.</h3>", status_code=400)

    if result.empty:
        return HTMLResponse(f"<h3>No events found for {area_label}</h3>", status_code=404)

    recent = result.sort_values(by="event_date", ascending=False).iloc[0]
    last_date = recent["event_date"]
    last_cpr = recent["fb_cpr"]
    days_since_last = (ref_date - last_date).days
    count_30 = len(result[result["event_date"] >= ref_date - timedelta(days=30)])

    fatigue_penalty = count_30 * 0.1
    rest_boost = min(days_since_last / 30, 1.0) * 0.2
    topic_factor = {"EP": 0.9, "SS": 0.85, "TIR": 1.15}.get(topic_upper, 1.0) if topic else 1.0

    delta = rest_boost - fatigue_penalty
    predicted_cpr = last_cpr * (1 + delta) * topic_factor

    trend_icon = "📉" if delta < 0 else "📈"
    trend_text = "Expected to decrease" if delta < 0 else "Expected to increase"

    html = f"""
    <h2>Predicted CPR for {area_label}</h2>
    <p><b>Topic:</b> {topic or 'All Topics'}</p>
    <p><b>Most Recent Event:</b> {last_date.strftime('%Y-%m-%d')}</p>
    <p><b>Days Since Last Event:</b> {days_since_last} days</p>
    <p><b>Events in Last 30 Days:</b> {count_30}</p>
    <p><b>Last Known CPR:</b> ${round(last_cpr, 2)}</p>
    <h3>{trend_icon} Predicted CPR: ${round(predicted_cpr, 2)}</h3>
    <p>{trend_text} by approx. {round(delta * 100, 1)}%</p>
    """
    return HTMLResponse(html)



