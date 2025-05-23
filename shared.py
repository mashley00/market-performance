import pandas as pd

def load_insights():
    df = pd.read_csv(
        "https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv",
        encoding="utf-8"
    )
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)
    return df
