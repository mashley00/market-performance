from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Import all routers
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from geo_decay import router as geo_decay_router

# Ensure DB is initialized at startup
from campaign_db import init_db

# Initialize FastAPI app
app = FastAPI()

# Initialize database tables (campaign_targets, targeting_data)
init_db()

# Attach API routers
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(geo_decay_router)

# Serve static files from the 'static' folder (optional)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root health check
@app.get("/")
def health_check():
    return {"message": "✅ Market Performance API is running"}
