from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/predict-form", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("predict_form.html", {"request": request})

@router.post("/predict-form", response_class=HTMLResponse)
async def form_post(request: Request, topic: str = Form(...), city: str = Form(...), state: str = Form(...), start_date: str = Form(...), end_date: str = Form(...)):
    payload = {
        "topic": topic,
        "city": city,
        "state": state,
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.post("https://market-performance.onrender.com/predict-performance", json=payload)
    result = response.json()
    return templates.TemplateResponse("predict_form.html", {"request": request, "result": result})
