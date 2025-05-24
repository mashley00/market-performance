from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Load and normalize dataset
CSV_URL = "https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv"
df = pd.read_csv(CSV_URL, encoding='utf-8')
df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)

@router.get("/predict-form", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("predict_form.html", {"request": request})

@router.post("/predict-form", response_class=HTMLResponse)
async def predict_submit(
    request: Request,
    topic: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...)
):
    # Validate column name exists
    if 'topic' not in df.columns:
        return templates.TemplateResponse("predict_result.html", {
            "request": request,
            "city": city,
            "state": state,
            "topic": topic,
            "start_date": start_date,
            "end_date": end_date,
            "predicted_cpr": "N/A",
            "estimated_registrants": "N/A",
            "no_data": True,
            "error": "Column 'topic' not found in dataset."
        })

    # Filter data
    filtered_df = df[
        (df['city'].str.lower() == city.lower()) &
        (df['state'].str.lower() == state.lower()) &
        (df['topic'] == topic)
    ]

    if filtered_df.empty:
        return templates.TemplateResponse("predict_result.html", {
            "request": request,
            "city": city,
            "state": state,
            "topic": topic,
            "start_date": start_date,
            "end_date": end_date,
            "predicted_cpr": "N/A",
            "estimated_registrants": "N/A",
            "no_data": True
        })

    # Perform calculation
    avg_cpr = filtered_df['fb_cpr'].mean()
    estimated_registrants = (filtered_df['fb_registrants'] / filtered_df['fb_days']).mean() * 14

    return templates.TemplateResponse("predict_result.html", {
        "request": request,
        "city": city,
        "state": state,
        "topic": topic,
        "start_date": start_date,
        "end_date": end_date,
        "predicted_cpr": f"${avg_cpr:.2f}",
        "estimated_registrants": f"{estimated_registrants:.0f}",
        "no_data": False
    })

