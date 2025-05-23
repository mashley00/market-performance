from fastapi import APIRouter, HTTPException
import requests
import os
from dotenv import load_dotenv

router = APIRouter()
load_dotenv()

ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")  # Ensure this is defined in .env or Render secrets

@router.get("/fb-targeting")
def get_fb_targeting(job_id: str):
    try:
        adset_id = convert_job_to_adset_id(job_id)
        if not adset_id:
            raise HTTPException(status_code=404, detail="Adset ID not found for given job")

        url = f"https://graph.facebook.com/v22.0/{adset_id}/adsets"
        params = {
            "access_token": ACCESS_TOKEN,
            "fields": "name,targeting"
        }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Facebook API error: {response.text}")

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

def convert_job_to_adset_id(job_id):
    # Dummy logic, replace with real lookup or mapping if needed
    adset_lookup = {
        "118770": "120216353468830462",
        "118576": "120216372723070462",
        # Add more as needed
    }
    return adset_lookup.get(job_id)
