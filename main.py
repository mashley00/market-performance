from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from fuzzywuzzy import process
import logging
from fb_insights import router as fb_router
app.include_router(fb_router)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

logging.basicConfig(level=logging.INFO)

# Load dataset
try:
    df = pd.read_csv("https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv", encoding='utf-8')
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)
    df['city'] = df['city'].str.lower().str.strip()
    df['state'] = df['state'].str.upper().str.strip()
except Exception as e:
    logging.error("Error loading dataset.")
    raise e


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("market.html", {"request": request})


@app.get("/predict", response_class=HTMLResponse)
def predict_form(request: Request):
    return templates.TemplateResponse("predict.html", {"request": request})


@app.get("/market", response_class=HTMLResponse)
def market_form(request: Request):
    return templates.TemplateResponse("market.html", {"request": request})


@app.get("/market-health")
def get_market_health(city: str = "", state: str = "", topic: str = ""):
    city = city.lower().strip()
    state = state.upper().strip()
    topic = topic.strip().upper()

    cities_in_state = df[df['state'] == state]['city'].unique().tolist()
    best_match, score = process.extractOne(city, cities_in_state)
    filtered = df[(df['city'] == best_match) & (df['state'] == state)]

    if topic:
        filtered = filtered[filtered['seminar_topic'] == topic]

    if filtered.empty:
        return JSONResponse(status_code=404, content={"detail": f"No data for {city}, {state} ({topic})"})

    return {
        "city": best_match,
        "state": state,
        "topic": topic,
        "events": len(filtered),
        "avg_cpr": round(filtered['fb_cpr'].mean(), 2),
        "avg_cpa": round(filtered['cost_per_verified_hh'].mean(), 2),
        "avg_registrants": round(filtered['gross_registrants'].mean(), 2)
    }


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



