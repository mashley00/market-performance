from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers — only import actual API routers
from fb_insights import router as fb_insights_router
from fb_targeting import router as fb_targeting_router
from geo_decay import router as geo_decay_router

app = FastAPI()

# Attach API routers
app.include_router(fb_insights_router)
app.include_router(fb_targeting_router)
app.include_router(geo_decay_router)

# Serve static files (optional)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def health_check():
    return {"message": "✅ Market Performance API is running"}
