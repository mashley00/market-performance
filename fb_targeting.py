import os
import json
import logging
from datetime import date
from fastapi import APIRouter, HTTPException
import requests

from campaign_db import get_all_job_numbers, store_targeting_data

router = APIRouter()

# Facebook API setup
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise ValueError("FB_ACCESS_TOKEN environment variable is not set.")

GRAPH_API_VERSION = "v22.0"
BASE_URL = "https://graph.facebook.com"

@router.get("/fb-targeting")
def get_targeting_data():
    try:
        known_jobs = get_all_job_numbers()
        matched_jobs = 0
        targeting_results = []

        for job in known_jobs:
            campaign_id = job.get("campaign_id")
            job_number = job.get("job_number")

            if not campaign_id or not job_number:
                continue

            # Get all ad sets under this campaign
            adset_url = f"{BASE_URL}/{GRAPH_API_VERSION}/{campaign_id}/adsets"
            response = requests.get(adset_url, params={
                "access_token": ACCESS_TOKEN,
                "fields": "name,targeting"
            })
            response.raise_for_status()
            adsets = response.json().get("data", [])

            for adset in adsets:
                targeting = adset.get("targeting", {})
                geo = targeting.get("geo_locations", {})
                age_min = targeting.get("age_min", 0)
                age_max = targeting.get("age_max", 0)
                gender = targeting.get("genders", [])
                adset_id = adset.get("id")

                store_targeting_data(
                    job_number=job_number,
                    campaign_id=campaign_id,
                    adset_id=adset_id,
                    geo_locations=geo,
                    age_min=age_min,
                    age_max=age_max,
                    gender=",".join(map(str, gender)) if gender else None,
                    last_synced=str(date.today())
                )

                targeting_results.append({
                    "job_number": job_number,
                    "campaign_id": campaign_id,
                    "adset_id": adset_id,
                    "geo": geo
                })

                matched_jobs += 1

        return {
            "message": "Targeting data synced",
            "campaigns_matched": matched_jobs,
            "entries": targeting_results
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API targeting error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch targeting data")
