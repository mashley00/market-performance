from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Market Tools")

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content="<h2>🏠 Welcome to Market Tools! Try /market.html or /predict.html</h2>")

@app.get("/market.html", response_class=HTMLResponse)
async def serve_market():
    with open("static/market.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/predict.html", response_class=HTMLResponse)
async def serve_predict():
    with open("static/predict.html", "r") as f:
        return HTMLResponse(content=f.read())

# Optional: expose the raw files if needed
app.mount("/static", StaticFiles(directory="static"), name="static")
