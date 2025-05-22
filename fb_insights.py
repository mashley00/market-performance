from fastapi import APIRouter, HTTPException
import requests
import logging
from datetime import date

router = APIRouter()

# Replace with your current long-lived token securely
ACCESS_TOKEN = "REPLACE_THIS_WITH_NEW_TOKEN"
AD_ACCOUNT_ID = "act_177526423462639"
GRAPH_API_VERSION = "v22.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{AD_ACCOUNT_ID}/insights"

# Calculate date range (you can adjust these dynamically if needed)
time_range = {
    "since": "2025-01-01",
    "until": str(date.today())  # today's date ensures full YTD
}

FIELDS = "campaign_name,impressions,reach,spend"

@router.get("/fb-insights")
def get_fb_insights():
    try:
        response = requests.get(
            BASE_URL,
            params={
                "access_token": ACCESS_TOKEN,
                "time_range": time_range,
                "fields": FIELDS
            }
        )
        response.raise_for_status()
        data = response.json()
        return {"fb_insights": data.get("data", [])}
    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch FB data")


