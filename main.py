from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers
from campaign_db import router as campaign_db_router
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from geo_decay import router as geo_decay_router

app = FastAPI()

# Attach routes
app.include_router(campaign_db_router)
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(geo_decay_router)

# Optional: Serve static HTML/CSS if using UI
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root health check
@app.get("/")
def health_check():
    return {"message": "✅ Market Performance API is running"}

