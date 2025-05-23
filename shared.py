import pandas as pd

def load_events_from_s3():
    """
    Load the latest events data from the AcquireUp S3 bucket.
    Automatically cleans and formats columns.
    """
    s3_url = "https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv"

    try:
        df = pd.read_csv(s3_url, encoding='utf-8')
        df.columns = (
            df.columns
            .str.lower()
            .str.replace(" ", "_")
            .str.replace(r"[^\w\s]", "", regex=True)
        )
        return df
    except Exception as e:
        raise RuntimeError(f"Error loading S3 CSV: {e}")
