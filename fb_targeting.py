import pandas as pd
import json
import logging
from fastapi import APIRouter
import requests
from shared import load_insights

router = APIRouter()

ACCESS_TOKEN = "EAAQ7fq9y3V0BO66nsaF66pRaeQ71emyS4bT0EJbZAmghrANkWoCaNov68275ZCvnOYoDAbFDYZAMEZBLhdx86ATEfNVyxS19Tu5qZAdOqEpTAzIyvbheCeOPZBy7ZB2hJBcBGMXlEXiX3EobxPS8OG5pPjYfT8iJ5uEiNvbXIZCHkbuMFYp80gZDZD"

@router.get("/fb-targeting")
def get_fb_targeting():
    try:
        df = load_insights()

        results = []
        seen = set()

        for _, row in df.iterrows():
            job_number = row.get("job_number")
            campaign_id = row.get("campaign_id")

            if not job_number or not isinstance(job_number, str):
                continue
            if job_number in seen:
                continue
            seen.add(job_number)

            if not campaign_id or not campaign_id.isdigit():
                continue

            url = f"https://graph.facebook.com/v22.0/{campaign_id}/adsets"
            params = {
                "access_token": ACCESS_TOKEN,
                "fields": "name,targeting"
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                for adset in data.get("data", []):
                    targeting = adset.get("targeting", {})
                    results.append({
                        "job_number": job_number,
                        "adset_name": adset.get("name"),
                        "targeting": targeting
                    })

            except requests.exceptions.RequestException as e:
                error_detail = e.response.text if hasattr(e, "response") and e.response else str(e)
                logging.error(f"Facebook API targeting error for job {job_number}: {error_detail}")
                continue

        return {"fb_targeting": results}

    except Exception as e:
        logging.exception("Internal server error in /fb-targeting")
        return {"detail": "Internal Server Error"}
