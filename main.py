from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from geo_decay import router as geo_decay_router
from predict_performance import router as predict_performance_router

# DB initializer
from campaign_db import init_db

# ✅ MUST exist for Render/Uvicorn
app = FastAPI()

# Ensure database is initialized on boot
init_db()

# Attach API routers
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(geo_decay_router)
app.include_router(predict_performance_router)

# Optional: Static file mounting if you add frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check route
@app.get("/")
def health_check():
    return {"message": "✅ Market Performance API is running"}

