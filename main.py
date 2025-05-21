from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, Optional
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import logging
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketPerformance")

app = FastAPI(title="Market Performance API")

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
    df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    df['event_day'] = df['event_date'].dt.day_name()
    df['zip_code'] = df['zip_code'].fillna('').astype(str).str.strip().str.zfill(5)
    logger.info(f"Loaded dataset: {df.shape}")
except Exception as e:
    logger.exception("Error loading dataset.")
    raise e

TOPIC_MAP = {
    "TIR": "taxes_in_retirement_567",
    "EP": "estate_planning_567",
    "SS": "social_security_567"
}

def is_true(val):
    return str(val).strip().upper() == "TRUE"

def get_similar_cities(input_city, state, threshold=75):
    candidates = df[df['state'].str.upper() == state.upper()]['city'].dropna().unique()
    input_norm = input_city.strip().lower()
    matches = [
        city for city in candidates
        if fuzz.token_set_ratio(city.lower(), input_norm) >= threshold
    ]
    return list(set(matches))

@app.get("/market-health", response_class=HTMLResponse)
async def market_health(zip: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None, topic: Optional[str] = None):
    if not topic:
        return HTMLResponse("<p>⚠️ Topic is required.</p>")
    topic_full = TOPIC_MAP.get(topic.upper())
    if not topic_full:
        raise HTTPException(status_code=400, detail="Invalid topic code.")

    if zip:
        zip_str = zip.strip().zfill(5)
        region_df = df[(df['zip_code'] == zip_str) & (df['topic'] == topic_full)]
    elif city and state:
        matches = get_similar_cities(city, state)
        region_df = df[(df['city'].str.lower().isin([m.lower() for m in matches])) & (df['state'].str.upper() == state.upper()) & (df['topic'] == topic_full)]
    else:
        return HTMLResponse("<p>⚠️ Please provide either ZIP code or City + State.</p>")

    if region_df.empty:
        return HTMLResponse("<p>No matching events found for this market/topic.</p>")

    last_event = region_df.sort_values('event_date', ascending=False).iloc[0]
    last_cpr = last_event.get("fb_cpr", 0)
    last_date = last_event['event_date']
    days_since = (pd.Timestamp.today() - last_date).days

    decay = round(min(days_since / 60, 1.0), 2)
    recovery_rate = round(min(days_since / 90, 1.0), 2)

    soonest_window = 45 if last_cpr < 60 else int(days_since + (60 - days_since) / 2)

    html = f"""
    <h2>📍 Market Health Overview – {city or zip}, {state}</h2>
    <ul>
      <li><b>Topic:</b> {topic.upper()}</li>
      <li><b>Most Recent Event:</b> {last_date.strftime('%Y-%m-%d')}</li>
      <li><b>Days Since Last:</b> {days_since} days</li>
      <li><b>Current CPR:</b> ${round(last_cpr, 2)}</li>
      <li><b>Decay Level:</b> {int(decay * 100)}%</li>
      <li><b>Recovery Rate:</b> {int(recovery_rate * 100)}%</li>
      <li><b>📅 Projected Recovery:</b> In ~{soonest_window} days can reach &lt;$60 CPR with 50+ regs</li>
    </ul>
    """
    return HTMLResponse(html)

@app.get("/predict-cpr", response_class=HTMLResponse)
async def predict_cpr(zip: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None, topic: Optional[str] = None):
    topic_key = topic.upper() if topic else None
    topic_full = TOPIC_MAP.get(topic_key)

    if zip:
        zip_str = zip.strip().zfill(5)
        region_df = df[(df['zip_code'] == zip_str) & (df['topic'] == topic_full)]
    elif city and state:
        matches = get_similar_cities(city, state)
        region_df = df[(df['city'].str.lower().isin([m.lower() for m in matches])) & (df['state'].str.upper() == state.upper()) & (df['topic'] == topic_full)]
    else:
        return HTMLResponse("<p>⚠️ Must provide ZIP or City/State.</p>")

    if region_df.empty:
        return HTMLResponse("<p>❌ No events found for this area/topic.</p>")

    last_event = region_df.sort_values("event_date", ascending=False).iloc[0]
    last_date = last_event["event_date"]
    last_cpr = last_event["fb_cpr"]
    days_since = (pd.Timestamp.today() - last_date).days

    fatigue_penalty = len(region_df[region_df['event_date'] > pd.Timestamp.today() - pd.Timedelta(days=30)]) * 0.1
    rest_boost = min(days_since / 30, 1.0) * 0.2
    delta = rest_boost - fatigue_penalty
    topic_factor = {"EP": 0.9, "SS": 0.85, "TIR": 1.15}.get(topic_key, 1.0)
    predicted_cpr = last_cpr * (1 + delta) * topic_factor

    # Media Efficiency
    impressions = region_df["fb_impressions"].sum()
    registrants = region_df["fb_registrants"].sum()
    reach = region_df["fb_reach"].sum()
    frequency = impressions / reach if reach else float("inf")
    regs_per_1k = (registrants / impressions * 1000) if impressions else 0
    avg_cpm = region_df["fb_cpm"].mean()
    avg_cvr = (registrants / reach * 100) if reach else 0

    html = f"""
    <h2>📍 CPR Prediction – {city or zip}, {state} ({topic})</h2>
    <ul>
      <li><b>Last Used:</b> {last_date.strftime('%Y-%m-%d')}</li>
      <li><b>Days Since:</b> {days_since} days</li>
      <li><b>Last Known CPR:</b> ${round(last_cpr, 2)}</li>
      <li><b>Predicted CPR:</b> ${round(predicted_cpr, 2)} ({'📉 Lower' if delta < 0 else '📈 Higher'})</li>
    </ul>
    <h3>📊 Media Efficiency Overlay</h3>
    <ul>
      <li>Avg. CPM: ${round(avg_cpm, 2)}</li>
      <li>CVR: {round(avg_cvr, 1)}%</li>
      <li>Regs / 1k Impressions: {round(regs_per_1k, 1)}</li>
      <li>Media-Driven CPR: ${round(avg_cpm / (avg_cvr / 100), 2) if avg_cvr else '∞'}</li>
      <li>Frequency: {round(frequency, 1)}</li>
    </ul>
    <h4>🧠 Interpretation:</h4>
    <p>Your predicted CPR includes decay adjustments based on venue recency.<br>
    Historically, media-driven CPR in this market is ${round(last_cpr, 2)}, indicating efficiency if creative and targeting are on point.</p>

    <h4>📈 Budget Simulation:</h4>
    <p>With a $1,200 budget over 14 days, expect ~{int(1200 / predicted_cpr)} registrants based on historical CPM and CVR.</p>
    """
    return HTMLResponse(html)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/market.html", response_class=HTMLResponse)
async def serve_market():
    with open("static/market.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/predict.html", response_class=HTMLResponse)
async def serve_predict():
    with open("static/predict.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)




