import os
import json
import logging
from datetime import date
from fastapi import APIRouter, HTTPException
import requests

from campaign_db import get_all_job_numbers, update_campaign_targets

router = APIRouter()

# Load Facebook token
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise ValueError("FB_ACCESS_TOKEN environment variable is not set.")

AD_ACCOUNT_ID = "act_177526423462639"
GRAPH_API_VERSION = "v22.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{AD_ACCOUNT_ID}/insights"

# Full year-to-date range
time_range = {
    "since": "2025-01-01",
    "until": str(date.today())
}

FIELDS = "campaign_name,campaign_id,impressions,reach,spend"
LEVEL = "campaign"
LIMIT = 500

@router.get("/fb-insights")
def get_fb_insights():
    try:
        # Query Facebook Graph API
        response = requests.get(
            BASE_URL,
            params={
                "access_token": ACCESS_TOKEN,
                "fields": FIELDS,
                "level": LEVEL,
                "limit": LIMIT,
                "time_range": json.dumps(time_range)
            }
        )
        response.raise_for_status()
        fb_data = response.json().get("data", [])

        if not fb_data:
            return {"fb_insights": []}

        # Match campaigns to job numbers
        known_jobs = get_all_job_numbers()
        matched = update_campaign_targets(fb_data, known_jobs)

        return {
            "fb_insights": matched,
            "total_campaigns": len(fb_data),
            "matched": len(matched),
            "unmatched": len(fb_data) - len(matched)
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch FB data")

