from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/predict-form", response_class=HTMLResponse)
async def predict_form(request: Request):
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
    # Stub logic – replace with your actual prediction logic later
    predicted_cpr = "$10.25"
    estimated_registrants = 34

    results = {
        "city": city,
        "state": state,
        "topic": topic,
        "start_date": start_date,
        "end_date": end_date,
        "predicted_cpr": predicted_cpr,
        "estimated_registrants": estimated_registrants,
    }

    return templates.TemplateResponse("predict_result.html", {
        "request": request,
        "results": results
    })

