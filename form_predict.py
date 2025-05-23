from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/predict-form", response_class=HTMLResponse)
def predict_form(request: Request):
    return templates.TemplateResponse("predict_form.html", {"request": request})

@router.post("/predict-form", response_class=HTMLResponse)
def predict_submit(
    request: Request,
    city: str = Form(...),
    state: str = Form(...),
    topic: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...)
):
    try:
        # Call backend API
        payload = {
            "city": city,
            "state": state,
            "topic": topic.upper(),
            "start_date": start_date,
            "end_date": end_date
        }
        response = requests.post("https://market-performance.onrender.com/predict-performance", json=payload)

        if response.status_code == 200:
            result = response.json()
            return templates.TemplateResponse("predict_result.html", {
                "request": request,
                "city": city,
                "state": state,
                "topic": topic.upper(),
                "start_date": start_date,
                "end_date": end_date,
                "result": result
            })
        else:
            return templates.TemplateResponse("predict_result.html", {
                "request": request,
                "error": f"API call failed with status {response.status_code}",
                "payload": payload
            })
    except Exception as e:
        return templates.TemplateResponse("predict_result.html", {
            "request": request,
            "error": str(e)
        })
