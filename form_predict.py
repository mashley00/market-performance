from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from predict_performance import predict_performance  # your logic module

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/predict-form", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("predict_form.html", {"request": request})


@router.post("/predict-form", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    city: str = Form(...),
    state: str = Form(...),
    topic: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...)
):
    # Clean inputs
    topic = topic.upper().strip()
    city = city.strip()
    state = state.upper().strip()

    # Call prediction function
    results = predict_performance(city, state, topic, start_date, end_date)

    # Render results in a basic HTML page
    return templates.TemplateResponse("predict_result.html", {
        "request": request,
        "city": city,
        "state": state,
        "topic": topic,
        "start_date": start_date,
        "end_date": end_date,
        "results": results
    })
