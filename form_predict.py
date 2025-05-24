from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/predict-form", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("predict_form.html", {"request": request})

@router.post("/predict-form", response_class=HTMLResponse)
async def predict_submit(
    request: Request,
    city: str = Form(...),
    state: str = Form(...),
    topic: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...)
):
    # Replace with real model logic
    predicted_cpr = 4.21
    estimated_registrants = 38

    return templates.TemplateResponse("predict_result.html", {
        "request": request,
        "city": city,
        "state": state,
        "topic": topic,
        "start_date": start_date,
        "end_date": end_date,
        "predicted_cpr": predicted_cpr,
        "estimated_registrants": estimated_registrants
    })
