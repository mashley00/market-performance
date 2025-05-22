import sqlite3
from typing import List, Dict

DATABASE = "campaign_insights.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS campaign_insights (
            job_number TEXT PRIMARY KEY,
            campaign_name TEXT,
            impressions INTEGER,
            reach INTEGER,
            spend REAL,
            frequency REAL,
            ctr REAL,
            complete_registrations INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def upsert_campaign_insight(insight: Dict):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO campaign_insights (
            job_number, campaign_name, impressions, reach, spend, frequency, ctr, complete_registrations
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_number) DO UPDATE SET
            campaign_name=excluded.campaign_name,
            impressions=excluded.impressions,
            reach=excluded.reach,
            spend=excluded.spend,
            frequency=excluded.frequency,
            ctr=excluded.ctr,
            complete_registrations=excluded.complete_registrations
    ''', (
        insight["job_number"],
        insight["campaign_name"],
        insight.get("impressions", 0),
        insight.get("reach", 0),
        insight.get("spend", 0.0),
        insight.get("frequency", 0.0),
        insight.get("ctr", 0.0),
        insight.get("complete_registrations", 0)
    ))
    conn.commit()
    conn.close()

def get_all_job_numbers() -> List[str]:
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT job_number FROM campaign_insights")
    job_numbers = [row[0] for row in c.fetchall()]
    conn.close()
    return job_numbers

def update_campaign_targets(new_data: List[Dict]):
    for entry in new_data:
        upsert_campaign_insight(entry)

