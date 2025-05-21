import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fuzzywuzzy import fuzz
import logging

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MarketPerformance")

app = FastAPI()
templates = Jinja2Templates(directory="static")

# Load and preprocess dataset
try:
    df = pd.read_csv("static/all_events_23_25.csv")
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)

    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["city"] = df["city"].astype(str).str.strip().str.lower()
    df["state"] = df["state"].astype(str).str.strip().str.upper()
    df["topic"] = df["topic"].astype(str).str.strip().str.lower()

    logger.info(f"Loaded dataset: {df.shape}")
except Exception as e:
    logger.error("Error loading dataset.")
    raise e


def fuzzy_city_match(user_city, state):
    user_city = user_city.lower()
    candidates = df[df["state"] == state.upper()]["city"].unique()
    best_match = max(candidates, key=lambda x: fuzz.ratio(x.lower(), user_city))
    if fuzz.ratio(user_city, best_match) >= 75:
        return best_match
    return None


@app.get("/market.html", response_class=HTMLResponse)
async def get_market_form(request: Request):
    return templates.TemplateResponse("market_form.html", {"request": request})


@app.post("/market", response_class=HTMLResponse)
async def run_market_form(request: Request):
    form = await request.form()
    city = form.get("city", "").strip().lower()
    state = form.get("state", "").strip().upper()
    topic = form.get("topic", "").strip().lower()

    matched_city = fuzzy_city_match(city, state)
    if not matched_city:
        return templates.TemplateResponse("market_results.html", {
            "request": request,
            "error": f"No match found for city '{city.title()}', state '{state}'"
        })

    subset = df[(df["city"] == matched_city) & (df["state"] == state) & (df["topic"] == topic)]
    if subset.empty:
        return templates.TemplateResponse("market_results.html", {
            "request": request,
            "error": f"No events found for {matched_city.title()}, {state} for topic {topic.upper()}."
        })

    summary = {
        "city": matched_city.title(),
        "state": state,
        "topic": topic.upper(),
        "events": len(subset),
        "avg_cpr": round(subset["cpr"].mean(), 2),
        "avg_cpa": round(subset["cost_per_verified_hh"].mean(), 2),
        "avg_att_rate": round((subset["attended_hh"].sum() / subset["gross_registrants"].sum()) * 100, 1)
    }

    return templates.TemplateResponse("market_results.html", {
        "request": request,
        "summary": summary
    })




