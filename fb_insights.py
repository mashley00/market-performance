from fastapi import APIRouter, HTTPException
import requests
import logging
from datetime import date
from campaign_db import CampaignInsight, SessionLocal
from sqlalchemy.exc import IntegrityError

router = APIRouter()

ACCESS_TOKEN = "REPLACE_THIS_WITH_NEW_TOKEN"
AD_ACCOUNT_ID = "act_177526423462639"
GRAPH_API_VERSION = "v22.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{AD_ACCOUNT_ID}/insights"

FIELDS = "campaign_name,impressions,reach,spend"
time_range = {
    "since": "2025-01-01",
    "until": str(date.today())
}

def parse_campaign_name(name):
    try:
        parts = name.split()
        return {
            "topic": parts[0],
            "city": parts[3].replace(",", ""),
            "state": parts[4],
            "first_event_date": parts[5].replace(".", "-"),
            "second_event_date": parts[6].replace(",", "-") if parts[6] != "M" else None,
            "client_name": parts[7] if parts[6] != "M" else parts[6],
            "num_events": int(parts[8]) if parts[6] != "M" else int(parts[7]),
            "target_registrations": int(parts[9]) if parts[6] != "M" else int(parts[8]),
            "target_attendees": int(parts[10]) if parts[6] != "M" else int(parts[9]),
            "job_number": parts[11] if parts[6] != "M" else parts[10],
            "target_cpr": float(parts[12].replace("$", "")) if parts[6] != "M" else float(parts[11].replace("$", ""))
        }
    except Exception as e:
        logging.error(f"Error parsing campaign name '{name}': {e}")
        return None

def save_campaign_to_db(parsed, metrics):
    db = SessionLocal()
    try:
        record = CampaignInsight(
            job_number=parsed["job_number"],
            topic=parsed["topic"],
            city=parsed["city"],
            state=parsed["state"],
            first_event_date=parsed["first_event_date"],
            second_event_date=parsed["second_event_date"],
            client_name=parsed["client_name"],
            num_events=parsed["num_events"],
            target_registrations=parsed["target_registrations"],
            target_attendees=parsed["target_attendees"],
            target_cpr=parsed["target_cpr"],
            campaign_name=metrics["campaign_name"],
            impressions=metrics["impressions"],
            reach=metrics["reach"],
            spend=metrics["spend"],
        )
        db.merge(record)
        db.commit()
    except IntegrityError:
        db.rollback()
    finally:
        db.close()

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
        data = response.json().get("data", [])

        for campaign in data:
            parsed = parse_campaign_name(campaign.get("campaign_name", ""))
            if parsed:
                save_campaign_to_db(parsed, campaign)

        return {"fb_insights": data}
    except requests.exceptions.RequestException as e:
        logging.error(f"Facebook API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch FB data")


