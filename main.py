import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
from fuzzywuzzy import fuzz
from typing import Optional

app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketPerformance")

# Load dataset (city-level only for now)
try:
    df_url = "https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv"
    df = pd.read_csv(df_url)
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)
    df["city"] = df["city"].str.strip().str.lower()
    df["state"] = df["state"].str.strip().str.upper()
    logger.info(f"Loaded dataset: {df.shape}")
except Exception as e:
    logger.error("Error loading dataset.")
    raise e

# Match helper
def fuzzy_city_match(input_city, state):
    input_city = input_city.lower()
    state_df = df[df["state"] == state.upper()]
    city_scores = state_df["city"].dropna().unique()
    best_match = max(city_scores, key=lambda x: fuzz.partial_ratio(x, input_city))
    return best_match

# Models
class MarketRequest(BaseModel):
    city: str
    state: str

class PredictRequest(BaseModel):
    city: str
    state: str
    topic: str
    event_date: Optional[str] = None  # ISO format

@app.get("/", response_class=HTMLResponse)
def root():
    return "<h2>Welcome to Market Performance API</h2>"

@app.get("/market.html", response_class=HTMLResponse)
def get_market_html():
    return open("static/market.html").read()

@app.get("/predict.html", response_class=HTMLResponse)
def get_predict_html():
    return open("static/predict.html").read()

@app.post("/market")
def market_health(request: MarketRequest):
    city = fuzzy_city_match(request.city, request.state)
    city_data = df[(df["city"] == city) & (df["state"] == request.state.upper())]

    if city_data.empty:
        raise HTTPException(status_code=404, detail="No data found for this market.")

    # Placeholder logic
    decay = 0.28
    recovery_rate = {"TIR": 0.16, "SS": 0.12, "EP": 0.14}
    soonest_recovery = "3 weeks (estimated)"

    return {
        "market": f"{city.title()}, {request.state.upper()}",
        "events": len(city_data),
        "topics": city_data["seminar_topic"].value_counts().to_dict(),
        "decay_level": decay,
        "recovery_rate": recovery_rate,
        "projected_cpr_under_60": soonest_recovery,
    }

@app.post("/predict")
def predict_performance(request: PredictRequest):
    city = fuzzy_city_match(request.city, request.state)
    topic = request.topic.upper()
    filtered = df[(df["city"] == city) & (df["state"] == request.state.upper()) & (df["seminar_topic"] == topic)]

    if filtered.empty:
        raise HTTPException(status_code=404, detail="No events found for this topic/market.")

    latest = filtered.sort_values("event_date", ascending=False).iloc[0]
    predicted_cpr = filtered["cpr"].mean()
    predicted_regs = filtered["gross_registrants"].mean()
    days_since = (pd.Timestamp.now() - pd.to_datetime(latest["event_date"])).days

    return {
        "venue": latest["venue"],
        "market": f"{city.title()}, {request.state.upper()}",
        "topic": topic,
        "event_date": request.event_date or "N/A",
        "days_since_last_use": days_since,
        "predicted_registrants": round(predicted_regs),
        "predicted_cpr": round(predicted_cpr, 2),
    }

# Static assets
app.mount("/static", StaticFiles(directory="static"), name="static")




