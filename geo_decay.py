from fastapi import APIRouter
from shared import load_events_from_s3

router = APIRouter()

@router.get("/market-health")
def market_health(city: str, topic: str):
    df = load_events_from_s3()

    filtered = df[
        (df["city"].str.lower() == city.lower()) &
        (df["seminar_topic"].str.upper() == topic.upper())
    ]

    if filtered.empty:
        return {"city": city, "topic": topic, "status": "No data found."}

    avg_cpr = filtered["fb_cpr"].mean()
    avg_fulfillment = (filtered["attended_hh"] / (filtered["registration_max"] / 2.4)).mean()

    health_score = round((1 / avg_cpr * 0.5) + (avg_fulfillment * 0.5), 2)

    return {
        "city": city,
        "topic": topic,
        "avg_cpr": round(avg_cpr, 2),
        "avg_fulfillment": round(avg_fulfillment, 2),
        "health_score": health_score
    }
