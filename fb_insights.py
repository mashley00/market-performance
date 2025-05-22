from fastapi import APIRouter, HTTPException
import requests
import logging
import os
from datetime import date

router = APIRouter()

# Secure token from environment
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = "act_177526423462639"
GRAPH_API_VERSION = "v22.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{AD_ACCOUNT_ID}/insights"

# YTD Date Range
TODAY = str(date.today())
TIME_RANGE = f'{{"since":"2025-01-01","until":"{TODAY}"}}'

# Requested fields
FIELDS = "campaign_name,campaign_id,impressions,reach,spend"

@router.get("/fb-insights")
def get_fb_insights():
    try:
        response = requests.get(
            BASE_URL,
            params={
                "access_token": ACCESS_TOKEN,
                "time_range": TIME_RANGE,
                "fields": FIELDS,
                "level": "campaign",
                "limit": 500
            }
        )
        response.raise_for_status()
        data = response.json()
        return {"fb_insights": data.get("data", [])}
    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch FB data")


