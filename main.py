import sqlite3
import json
from datetime import datetime
from fastapi import APIRouter

DB_FILE = "campaigns.db"
router = APIRouter()

# -----------------------------
# 1. Initialize the database
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Table 1: FB Campaign to Job Number Mapping
    cur.execute("""
        CREATE TABLE IF NOT EXISTS campaign_targets (
            campaign_id TEXT PRIMARY KEY,
            campaign_name TEXT,
            job_number TEXT,
            city TEXT,
            state TEXT
        )
    """)

    # Table 2: Targeting data per job/ad set
    cur.execute("""
        CREATE TABLE IF NOT EXISTS targeting_data (
            job_number TEXT PRIMARY KEY,
            campaign_id TEXT,
            adset_id TEXT,
            geo_locations TEXT,
            age_min INTEGER,
            age_max INTEGER,
            gender TEXT,
            last_synced TEXT
        )
    """)

    conn.commit()
    conn.close()

# -----------------------------
# 2. Extract Job Number from FB Campaign Name
# -----------------------------
def extract_job_number(campaign_name):
    parts = campaign_name.split()
    for part in parts:
        if part.isdigit() and len(part) >= 5:
            return part
    return None

# -----------------------------
# 3. Match and Store Campaign Metadata
# -----------------------------
def update_campaign_targets(fb_data, known_jobs):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    for campaign in fb_data:
        name = campaign.get("campaign_name")
        campaign_id = campaign.get("campaign_id")
        if not name or not campaign_id:
            continue

        job_number = extract_job_number(name)
        city = state = None

        for job in known_jobs:
            if job_number == job.get("job_number"):
                city = job.get("city")
                state = job.get("state")
                break

        cur.execute("""
            INSERT OR REPLACE INTO campaign_targets
            (campaign_id, campaign_name, job_number, city, state)
            VALUES (?, ?, ?, ?, ?)
        """, (campaign_id, name, job_number, city, state))

    conn.commit()
    conn.close()

# -----------------------------
# 4. Get Known Jobs From DB
# -----------------------------
def get_all_job_numbers():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT job_number, campaign_id, city, state FROM campaign_targets")
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "job_number": row[0],
            "campaign_id": row[1],
            "city": row[2],
            "state": row[3]
        }
        for row in rows if row[0]
    ]

# -----------------------------
# 5. Store Ad Set Targeting Info
# -----------------------------
def store_targeting_data(job_number, campaign_id, adset_id, geo_locations, age_min, age_max, gender, last_synced):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO targeting_data
        (job_number, campaign_id, adset_id, geo_locations, age_min, age_max, gender, last_synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_number,
        campaign_id,
        adset_id,
        json.dumps(geo_locations),
        age_min,
        age_max,
        gender,
        last_synced
    ))

    conn.commit()
    conn.close()

# -----------------------------
# ✅ TEMP ROUTE TO INIT DB
# -----------------------------
@router.get("/init-db")
def initialize_database():
    init_db()
    return {"message": "Database initialized with campaign_targets and targeting_data tables."}
