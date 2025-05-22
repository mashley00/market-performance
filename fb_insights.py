from fastapi import APIRouter, HTTPException
import requests
import logging
from datetime import date

router = APIRouter()

ACCESS_TOKEN = "REPLACE_WITH_YOUR_LONG_LIVED_TOKEN"
AD_ACCOUNT_ID = "act_177526423462639"
GRAPH_API_VERSION = "v22.0"
INSIGHTS_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{AD_ACCOUNT_ID}/insights"
ADSETS_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{AD_ACCOUNT_ID}/adsets"

FIELDS = "campaign_name,impressions,reach,spend"

@router.get("/fb-insights")
def get_fb_insights():
    try:
        response = requests.get(
            INSIGHTS_BASE_URL,
            params={
                "access_token": ACCESS_TOKEN,
                "time_range": {
                    "since": "2025-01-01",
                    "until": str(date.today())
                },
                "fields": FIELDS
            }
        )
        response.raise_for_status()
        return {"fb_insights": response.json().get("data", [])}
    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch FB data")

@router.get("/fb-geo-targeting")
def get_geo_targeting(limit: int = 50):
    try:
        response = requests.get(
            ADSETS_URL,
            params={
                "access_token": ACCESS_TOKEN,
                "fields": "id,name,targeting",
                "limit": limit
            }
        )
        response.raise_for_status()
        adsets = response.json().get("data", [])
        targeting_info = [
            {
                "id": ad["id"],
                "name": ad["name"],
                "targeting": ad.get("targeting", {}).get("geo_locations", {})
            }
            for ad in adsets
        ]
        return {"geo_targeting": targeting_info}
    except requests.exceptions.RequestException as e:
        logging.error(f"Geo-targeting fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch geo targeting data")

