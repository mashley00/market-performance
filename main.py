from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
import logging

app = FastAPI()
templates = Jinja2Templates(directory="static")

# Remote dataset URL
DATA_URL = "https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv"

# Try to load the dataset
try:
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)
    df['city'] = df['city'].str.strip().str.lower()
    df['state'] = df['state'].str.strip().str.upper()
except Exception as e:
    logging.error("Error loading dataset.", exc_info=True)
    raise e

# Utility: Fuzzy match city name within same state
def fuzzy_match_city(input_city, state):
    possible_cities = df[df['state'] == state]['city'].unique()
    best_match, score = process.extractOne(input_city.lower(), possible_cities, scorer=fuzz.token_sort_ratio)
    return best_match if score >= 80 else None

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/market")
def get_market_health(city: str, state: str, topic: str):
    matched_city = fuzzy_match_city(city, state)
    if not matched_city:
        return JSONResponse({"error": f"No close match for city '{city}' in {state}."}, status_code=404)

    subset = df[
        (df['city'] == matched_city) &
        (df['state'] == state) &
        (df['seminar_topic_code'].str.upper() == topic.upper())
    ]

    if subset.empty:
        return JSONResponse({"error": f"No data found for {matched_city}, {state} and topic {topic}."}, status_code=404)

    stats = {
        "city": matched_city,
        "state": state,
        "topic": topic.upper(),
        "events": len(subset),
        "avg_cpr": round(subset['cpr'].mean(), 2),
        "avg_cpa": round(subset['cost_per_verified_hh'].mean(), 2),
        "avg_registrants": round(subset['gross_registrants'].mean(), 1)
    }

    return stats

@app.get("/predict")
def predict_registrations(impressions: float = 0, reach: float = 0, fb_reg: float = 0, fb_days: int = 0):
    try:
        output = {}

        if fb_reg and fb_days:
            output['14_day_projection_from_fb'] = round((fb_reg / fb_days) * 14, 2)

        if impressions:
            output['registrants_per_impression'] = round((fb_reg / impressions) * impressions, 2)

        if reach:
            output['registrants_per_reach'] = round((fb_reg / reach) * reach, 2)

        return output or {"message": "Insufficient data for prediction."}

    except Exception as e:
        logging.error("Prediction error", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)




