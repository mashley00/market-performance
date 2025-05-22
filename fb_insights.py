from fastapi import APIRouter, HTTPException
import requests
import logging
import os
import json
from datetime import date

router = APIRouter()

# Pull token securely from environment
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN") or "REPLACE_THIS_WITH_NEW_TOKEN"
AD_ACCOUNT_ID = "act_177526423462639"
GRAPH_API_VERSION = "v22.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{AD_ACCOUNT_ID}/insights"

FIELDS = "campaign_name,impressions,reach,spend"

@router.get("/fb-insights")
def get_fb_insights():
    try:
        time_range_json = json.dumps({
            "since": "2025-01-01",
            "until": str(date.today())
        })

        response = requests.get(
            BASE_URL,
            params={
                "access_token": ACCESS_TOKEN,
                "fields": FIELDS,
                "time_range": time_range_json
            }
        )
        response.raise_for_status()
        data = response.json()
        return {"fb_insights": data.get("data", [])}
    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch FB data")

