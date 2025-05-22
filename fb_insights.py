from fastapi import APIRouter, HTTPException
import requests
import logging
import json

from campaign_db import get_all_job_numbers, insert_ad_targeting, get_all_targeting_campaign_ids

# Already defined earlier:
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
AD_ACCOUNT_ID = "act_177526423462639"
GRAPH_API_VERSION = "v22.0"
CAMPAIGN_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{AD_ACCOUNT_ID}/campaigns"

router = APIRouter()

@router.get("/fb-targeting")
def fetch_adset_targeting():
    if not ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Missing Facebook access token.")

    try:
        # Step 1: Get all campaigns
        campaign_response = requests.get(
            CAMPAIGN_BASE_URL,
            params={
                "access_token": ACCESS_TOKEN,
                "fields": "id,name",
                "limit": 100
            }
        )
        campaign_response.raise_for_status()
        campaigns = campaign_response.json().get("data", [])

        if not campaigns:
            return {"detail": "No campaigns found."}

        # Step 2: Prepare matching and deduping
        known_jobs = get_all_job_numbers()
        existing_ids = get_all_targeting_campaign_ids()
        stored = 0
        skipped = 0

        # Step 3: For each campaign, fetch adsets and store targeting
        for campaign in campaigns:
            campaign_id = campaign.get("id")
            campaign_name = campaign.get("name")

            if campaign_id in existing_ids:
                skipped += 1
                continue  # already stored

            adset_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{campaign_id}/adsets"
            adset_resp = requests.get(
                adset_url,
                params={
                    "access_token": ACCESS_TOKEN,
                    "fields": "id,name,targeting",
                    "limit": 10
                }
            )
            adset_resp.raise_for_status()
            adsets = adset_resp.json().get("data", [])

            if not adsets:
                continue  # no targeting to store

            # Step 4: Match to job number (fuzzy or substring match)
            job_number = next((j for j in known_jobs if j in campaign_name), None)

            for adset in adsets:
                targeting = adset.get("targeting")
                if targeting:
                    insert_ad_targeting(
                        campaign_id=campaign_id,
                        job_number=job_number,
                        targeting_json=json.dumps(targeting)
                    )
                    stored += 1

        return {
            "stored_campaigns": stored,
            "skipped_existing": skipped,
            "total_campaigns": len(campaigns)
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch targeting data")


