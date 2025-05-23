from fastapi import APIRouter
from shared import load_events_from_s3

router = APIRouter()

FB_TOKEN = "EAAQ7fq9y3V0BO66nsaF66pRaeQ71emyS4bT0EJbZAmghrANkWoCaNov68275ZCvnOYoDAbFDYZAMEZBLhdx86ATEfNVyxS19Tu5qZAdOqEpTAzIyvbheCeOPZBy7ZB2hJBcBGMXlEXiX3EobxPS8OG5pPjYfT8iJ5uEiNvbXIZCHkbuMFYp80gZDZD"

@router.get("/fb-targeting")
def targeting_preview():
    df = load_events_from_s3()

    recent = df.sort_values("event_date", ascending=False).head(5)
    return recent[["job_number", "venue", "city", "seminar_topic", "event_date"]].to_dict(orient="records")


    except Exception as e:
        logging.exception("Internal server error in /fb-targeting")
        return {"detail": "Internal Server Error"}
