import sqlite3
import json
from fastapi import APIRouter
from collections import defaultdict

router = APIRouter()
DB_FILE = "campaigns.db"

@router.get("/geo-decay")
def geo_decay():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Make sure your DB has this table and data
    cur.execute("SELECT job_number, geo_locations FROM targeting_data")
    targeting_rows = cur.fetchall()

    geo_zip_map = defaultdict(list)

    for job_number, geo_json in targeting_rows:
        try:
            geo = json.loads(geo_json)
            zips = geo.get("zips", [])
            for zip_code in zips:
                geo_zip_map[zip_code].append(job_number)
        except Exception as e:
            print(f"Failed to parse geo for job {job_number}: {e}")

    conn.close()

    return {
        "unique_zip_count": len(geo_zip_map),
        "total_job_mappings": sum(len(jobs) for jobs in geo_zip_map.values()),
        "example": dict(list(geo_zip_map.items())[:5])  # Show sample
    }
