from fastapi import FastAPI
from fb_insights import router as fb_insights_router
from geo_decay import router as geo_decay_router
from predict import router as predict_router
from market import router as market_router

app = FastAPI()

# Register all routers
app.include_router(fb_insights_router)
app.include_router(geo_decay_router)
app.include_router(predict_router)
app.include_router(market_router)

@app.get("/")
def root():
    return {"message": "Welcome to the Marketing Performance API"}


