import pandas as pd
import numpy as np

def load_data():
    url = "https://acquireup-venue-data.s3.us-east-2.amazonaws.com/all_events_23_25.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^\w\s]", "", regex=True)
    df['city'] = df['city'].str.strip().str.lower()
    df['state'] = df['state'].str.strip().str.upper()
    return df

def predict_performance(df, topic, city, state):
    city = city.lower().strip()
    state = state.upper().strip()

    df_filtered = df[
        (df["topic"] == topic) &
        (df["city"] == city) &
        (df["state"] == state) &
        (df["fb_cpr"].notna()) &
        (df["fb_registrants"].notna())
    ]

    if df_filtered.empty:
        return {"error": "No historical data found for this market/topic combination."}

    avg_cpr = df_filtered["fb_cpr"].mean()
    avg_fb_regs = df_filtered["fb_registrants"].mean()
    sample_size = len(df_filtered)

    return {
        "predicted_cpr": round(avg_cpr, 2),
        "predicted_fb_registrants": round(avg_fb_regs, 1),
        "events_sampled": sample_size
    }

def assess_market_health(df, topic, city, state):
    city = city.lower().strip()
    state = state.upper().strip()

    df_filtered = df[
        (df["topic"] == topic) &
        (df["city"] == city) &
        (df["state"] == state) &
        (df["fb_cpr"].notna()) &
        (df["fb_registrants"].notna()) &
        (df["fb_impressions"].notna()) &
        (df["fb_reach"].notna())
    ].copy()

    if df_filtered.empty:
        return {"error": "No valid records found for this market/topic."}

    df_filtered["regs_per_1k_impressions"] = (
        df_filtered["fb_registrants"] / df_filtered["fb_impressions"]
    ) * 1000
    df_filtered["regs_per_1k_reach"] = (
        df_filtered["fb_registrants"] / df_filtered["fb_reach"]
    ) * 1000
    df_filtered["frequency"] = df_filtered["fb_impressions"] / df_filtered["fb_reach"]

    metrics = {
        "market": f"{city.title()}, {state}",
        "topic": topic,
        "avg_cpr": round(df_filtered["fb_cpr"].mean(), 2),
        "avg_regs_per_1k_impressions": round(df_filtered["regs_per_1k_impressions"].mean(), 2),
        "avg_regs_per_1k_reach": round(df_filtered["regs_per_1k_reach"].mean(), 2),
        "avg_frequency": round(df_filtered["frequency"].mean(), 2),
        "events_sampled": len(df_filtered)
    }

    if metrics["avg_cpr"] > 60 and metrics["avg_regs_per_1k_impressions"] < 1.5:
        metrics["risk_level"] = "High (Saturation)"
    elif metrics["avg_cpr"] > 40:
        metrics["risk_level"] = "Moderate"
    else:
        metrics["risk_level"] = "Low"

    return metrics
