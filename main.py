from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from geo_decay import router as geo_decay_router

# Shared S3 loader
from shared import load_events_from_s3

# ✅ MUST exist for Render/Uvicorn
app = FastAPI()

# Attach routers
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(geo_decay_router)

# Static files if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def health_check():
    return {"message": "✅ Market Performance API is running"}

@app.get("/debug-s3")
def debug_s3():
    df = load_events_from_s3()
    return df.head(5).to_dict(orient="records")
