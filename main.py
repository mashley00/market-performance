from fastapi import FastAPI, Query
from typing import Optional
import uvicorn
from logic import load_data, predict_performance, assess_market_health

app = FastAPI(title="Market Performance Engine")

# Load your data file from S3 or local source at startup
df = load_data()

@app.get("/predict-performance")
def get_prediction(
    topic: str = Query(..., description="Seminar topic code (e.g., taxes_in_retirement_567)"),
    city: str = Query(..., description="City name"),
    state: str = Query(..., description="2-letter state abbreviation")
):
    return predict_performance(df, topic, city, state)

@app.get("/market-health")
def get_market_health(
    topic: str = Query(..., description="Seminar topic code"),
    city: str = Query(..., description="City name"),
    state: str = Query(..., description="State abbreviation")
):
    return assess_market_health(df, topic, city, state)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)


