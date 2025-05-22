from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Import routers
from geo_decay import router as geo_decay_router
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from campaign_db import router as campaign_db_router

app = FastAPI()

# Attach routers
app.include_router(geo_decay_router)
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(campaign_db_router)

# Serve static pages (if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Market Performance API is running"}
