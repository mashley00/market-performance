# fb_insights.py
import requests
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

router = APIRouter()

ACCESS_TOKEN = "EAAQ7fq9y3V0BO4v7VSDZBoSpTnuNKyvTGg90LxlGJKuZAmpHcZAfoaD73ydZAIIs1cNnS90MODaUK4EUZBNvT1m3aF1TcmBvSPCT1qg1Ufz7Vgf3Co0gGwa887mj6Rs83n6a61sx073mPZCNZAJpuGuoqiZAClQrajpjsBoXeoGJbbZC45B0MnoRzuQTKTfkZD"
AD_ACCOUNT_ID = "act_177526423462639"

@router.get("/fb-insights")
def get_fb_insights():
    since = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")
    until = datetime.utcnow().strftime("%Y-%m-%d")

    url = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}/insights"
    params = {
        "fields": "campaign_name,impressions,reach,spend,actions",
        "time_range": {"since": since, "until": until},
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch FB data")

    data = response.json().get("data", [])

    if not data:
        raise HTTPException(status_code=404, detail="No campaign data found")

    totals = {"impressions": 0, "reach": 0, "spend": 0, "registrations": 0}
    for entry in data:
        totals["impressions"] += int(entry.get("impressions", 0))
        totals["reach"] += int(entry.get("reach", 0))
        totals["spend"] += float(entry.get("spend", 0))

        actions = entry.get("actions", [])
        for act in actions:
            if act["action_type"] == "lead":
                totals["registrations"] += int(act["value"])

    return {
        "impressions": totals["impressions"],
        "reach": totals["reach"],
        "spend": round(totals["spend"], 2),
        "registrations": totals["registrations"],
        "fb_days": 14
    }
