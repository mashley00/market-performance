
import sqlite3

DB_FILE = "campaigns.db"

# Initialize table
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS campaign_targets (
            campaign_id TEXT PRIMARY KEY,
            campaign_name TEXT,
            job_number TEXT,
            city TEXT,
            state TEXT
        )
    """)
    conn.commit()
    conn.close()

# Extract job number from campaign name
def extract_job_number(campaign_name):
    parts = campaign_name.split()
    for part in parts:
        if part.isdigit() and len(part) >= 5:
            return part
    return None

# Add or update campaigns
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
            INSERT OR REPLACE INTO campaign_targets (campaign_id, campaign_name, job_number, city, state)
            VALUES (?, ?, ?, ?, ?)
        """, (campaign_id, name, job_number, city, state))

    conn.commit()
    conn.close()

def get_all_job_numbers():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT job_number, city, state FROM campaign_targets")
    rows = cur.fetchall()
    conn.close()

    return [
        {"job_number": row[0], "city": row[1], "state": row[2]}
        for row in rows if row[0]
    ]


