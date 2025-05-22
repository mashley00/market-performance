from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pandas as pd
from fuzzywuzzy import process
import logging

# Facebook and DB
from fb_insights import router as fb_router
from campaign_db import init_db

# Init FastAPI app
app = FastAPI(title="Market Performance API", version="1.0.0")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Static HTML forms support
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers
app.include_router(fb_router)

# Initialize local DB on startup
@app.on_event("startup")
def on_startup():
    init_db()

# --- Load dataset ---
try:
    df = pd.read_csv("https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv", encoding='utf-8')
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)
    df['city'] = df['city'].str.lower().str.strip()
    df['state'] = df['state'].str.upper().str.strip()
    logging.info("✅ Loaded dataset")
except Exception as e:
    logging.error("❌ Failed to load dataset.")
    raise e

# --- Market Health ---
@app.get("/market-health")
def get_market_health(city: str, state: str, topic: str):
    city = city.lower().strip()
    state = state.upper().strip()
    topic = topic.strip().upper()

    cities_in_state = df[df['state'] == state]['city'].unique().tolist()
    best_match, score = process.extractOne(city, cities_in_state)
    filtered = df[(df['city'] == best_match) & (df['state'] == state) & (df['seminar_topic'] == topic)]

    if filtered.empty:
        return JSONResponse(status_code=404, content={"detail": f"No data for {city}, {state} ({topic})"})

    avg_cpr = filtered['fb_cpr'].mean()
    avg_cpa = filtered['cost_per_verified_hh'].mean()
    avg_registrants = filtered['gross_registrants'].mean()

    return {
        "city": best_match,
        "state": state,
        "topic": topic,
        "events": len(filtered),
        "avg_cpr": round(avg_cpr, 2),
        "avg_cpa": round(avg_cpa, 2),
        "avg_registrants": round(avg_registrants, 2)
    }

# --- CPR Predictor ---
@app.get("/predict-cpr")
def predict_cpr(impressions: float = 10000, reach: float = 8000, fb_reg: int = 50, fb_days: int = 7):
    try:
        projection = (fb_reg / fb_days) * 14
        reg_per_impression = round((fb_reg / impressions) * impressions, 2) if impressions else 0
        reg_per_reach = round((fb_reg / reach) * reach, 2) if reach else 0

        return {
            "14_day_projection_from_fb": round(projection, 2),
            "registrants_per_impression": reg_per_impression,
            "registrants_per_reach": reg_per_reach
        }
    except ZeroDivisionError:
        return JSONResponse(status_code=400, content={"detail": "Invalid input. Division by zero."})

