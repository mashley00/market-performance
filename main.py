from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from geo_decay import router as geo_decay_router

# DB Init
from campaign_db import init_db

app = FastAPI()

# Ensure DB tables exist at startup
init_db()

# Attach routers
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(geo_decay_router)

# Serve static files if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def health_check():
    return {"message": "✅ Market Performance API is running"}
