from fastapi import APIRouter
from shared import load_events_from_s3

router = APIRouter()

@router.get("/fb-insights")
def fb_insights_summary():
    df = load_events_from_s3()

    # Example aggregation: average CPR and total registrants per topic
    summary = (
        df.groupby("seminar_topic")
        .agg(avg_cpr=("fb_cpr", "mean"), total_registrants=("gross_registrants", "sum"))
        .reset_index()
        .to_dict(orient="records")
    )
    return summary

