from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import pandas as pd

# Initialize the router
router = APIRouter()

# Templates directory
templates = Jinja2Templates(directory="templates")

# Dataset loading (adjust path as needed)
DATA_FILE = "all_events_23_25.csv"

@router.get("/predict-form", response_class=HTMLResponse)
async def predict_form(request: Request):
    return templates.TemplateResponse("predict_form.html", {"request": request})

@router.post("/predict-form", response_class=HTMLResponse)
async def predict_submit(
    request: Request,
    topic: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    start_date: str = Form(...)
):
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=14)

        # Load CSV
        df = pd.read_csv(DATA_FILE)

        # Basic filtering logic (update as needed)
        filtered_df = df[
            (df["seminar_topic_code"] == topic)
            & (df["city"].str.lower() == city.lower())
            & (df["state"].str.lower() == state.lower())
        ]

        if filtered_df.empty:
            return templates.TemplateResponse("predict_result.html", {
                "request": request,
                "error": "No data found for this combination.",
                "results": None
            })

        avg_registrants = filtered_df["gross_registrants"].mean()

        return templates.TemplateResponse("predict_result.html", {
            "request": request,
            "results": round(avg_registrants, 2),
            "topic": topic,
            "city": city,
            "state": state,
            "start_date": start_date,
            "end_date": end_dt.strftime("%Y-%m-%d")
        })
    except Exception as e:
        return templates.TemplateResponse("predict_result.html", {
            "request": request,
            "error": str(e),
            "results": None
        })
