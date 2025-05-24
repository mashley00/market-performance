from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from geo_decay import router as geo_decay_router
from form_predict import router as form_router

# DB initializer
from campaign_db import init_db

app = FastAPI()

# Initialize DB on startup
init_db()

# Static assets (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register API routers
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(geo_decay_router)
app.include_router(form_router)

# Health check
@app.get("/")
def health_check():
    return {"message": "✅ Market Performance API is running"}

