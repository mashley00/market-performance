from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Routers
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from geo_decay import router as geo_decay_router
from form_predict import router as form_router

# DB initializer
from campaign_db import init_db

# ✅ MUST exist for Render/Uvicorn
app = FastAPI()

# Ensure database is initialized on boot
init_db()

# Mount static and template folders
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add routers
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(geo_decay_router)
app.include_router(form_router)

# Health check
@app.get("/")
def health_check():
    return {"message": "✅ Market Performance API is running"}

# Health check route
@app.get("/")
def health_check():
    return {"message": "✅ Market Performance API is running"}

