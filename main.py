from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Import routers
from geo_decay import router as geo_decay_router
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from campaign_db import router as campaign_db_router  # TEMP: to init DB

app = FastAPI()

# Attach routers
app.include_router(geo_decay_router)
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(campaign_db_router)  # TEMP: needed to hit /init-db

# Serve static files (if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Market Performance API is running"}
