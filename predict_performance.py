from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from shared import load_events_from_s3
import pandas as pd

router = APIRouter()

class PredictionRequest(BaseModel):
    city: str
    state: str
    topic: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@router.post("/predict-performance")
def predict_performance(request: PredictionRequest):
    df = load_events_from_s3()

    # Normalize
    df["event_date"] = pd.to_datetime(df["event_date"])
    df["city"] = df["city"].str.lower()
    df["state"] = df["state"].str.lower()

    # Filter
    df_filtered = df[
        (df["seminar_topic"] == request.topic.upper()) &
        (df["city"] == request.city.lower()) &
        (df["state"] == request.state.lower())
    ]

    if request.start_date:
        df_filtered = df_filtered[df_filtered["event_date"] >= pd.to_datetime(request.start_date)]
    if request.end_date:
        df_filtered = df_filtered[df_filtered["event_date"] <= pd.to_datetime(request.end_date)]

    if df_filtered.empty:
        raise HTTPException(status_code=404, detail="No matching records found for prediction.")

    avg_cpr = round(df_filtered["fb_cpr"].mean(), 2)

    # Predict registrants: (FB registrants / FB days) * 14
    if "fb_registrants" in df_filtered.columns and "fb_days" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["fb_days"] > 0]
        df_filtered["daily_regs"] = df_filtered["fb_registrants"] / df_filtered["fb_days"]
        expected_regs = round(df_filtered["daily_regs"].mean() * 14)
    else:
        expected_regs = None

    return {
        "city": request.city,
        "state": request.state,
        "topic": request.topic,
        "avg_cpr": avg_cpr,
        "expected_fb_registrants": expected_regs
    }
