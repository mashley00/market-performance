# fb_insights.py

from fastapi import APIRouter, HTTPException
import requests
import logging
from datetime import date

router = APIRouter()

# 👇 Your actual credentials (move to env in prod!)
ACCESS_TOKEN = "REPLACE_THIS_WITH_NEW_TOKEN"
AD_ACCOUNT_ID = "act_177526423462639"

# 👇 Dynamically generated date range for 2025 YTD
START_DATE = "2025-01-01"
END_DATE = "2025-05-22"

@router.get("/fb-insights")
def fetch_fb_insights():
    url = f"https://graph.facebook.com/v22.0/{AD_ACCOUNT_ID}/insights"
    params = {
        "access_token": ACCESS_TOKEN,
        "time_range": {"since": START_DATE, "until": END_DATE},
        "fields": "campaign_name,impressions,reach,spend"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "data" not in data:
            raise HTTPException(status_code=400, detail="No insights returned.")

        return {"insights": data["data"]}

    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch FB data")

