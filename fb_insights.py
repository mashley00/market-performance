from fastapi import APIRouter, HTTPException
import requests
import logging
from datetime import date
from campaign_db import update_campaign_targets, get_all_job_numbers

router = APIRouter()

# Environment Config
import os
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = "act_177526423462639"
GRAPH_API_VERSION = "v22.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{AD_ACCOUNT_ID}/insights"

# Time range
time_range = {
    "since": "2025-01-01",
    "until": str(date.today())
}

# Fields for performance insights
INSIGHT_FIELDS = "campaign_name,campaign_id,impressions,reach,spend"

# --- Get Performance Insights ---
@router.get("/fb-insights")
def get_fb_insights():
    try:
        response = requests.get(
            BASE_URL,
            params={
                "access_token": ACCESS_TOKEN,
                "time_range": time_range,
                "fields": INSIGHT_FIELDS,
                "level": "campaign",
                "limit": 500
            }
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        return {"fb_insights": data}
    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch FB data")


# --- NEW: Get Targeting Details for a Campaign ---
@router.get("/fb-campaign-targeting")
def get_fb_campaign_targeting(campaign_id: str):
    try:
        response = requests.get(
            f"https://graph.facebook.com/{GRAPH_API_VERSION}/{campaign_id}",
            params={
                "access_token": ACCESS_TOKEN,
                "fields": "id,name,targeting"
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook Targeting API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch targeting data")


# --- Optional: Bulk Targeting Pull for All Jobs in DB ---
@router.get("/fb-sync-targeting")
def sync_all_targeting():
    try:
        job_numbers = get_all_job_numbers()
        synced = 0
        for job_id, campaign_id in job_numbers:
            targeting_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{campaign_id}"
            resp = requests.get(
                targeting_url,
                params={
                    "access_token": ACCESS_TOKEN,
                    "fields": "id,name,targeting"
                }
            )
            if resp.ok:
                targeting_info = resp.json().get("targeting", {})
                update_campaign_targets(job_id, targeting_info)
                synced += 1
        return {"message": f"Synced targeting data for {synced} campaigns."}
    except Exception as e:
        logging.error(f"Error syncing campaign targeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync targeting data")


