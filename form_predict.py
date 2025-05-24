from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/predict-form", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("predict_form.html", {"request": request})

@router.post("/predict-form", response_class=HTMLResponse)
async def predict_submit(request: Request):
    form_data = await request.form()
    
    # Extract values safely
    city = form_data.get("city")
    state = form_data.get("state")
    topic = form_data.get("topic")
    start_date = form_data.get("start_date")
    end_date = form_data.get("end_date")

    # Log what was received (for debugging)
    print("Form submission received:")
    print("City:", city, "State:", state, "Topic:", topic, "Start:", start_date, "End:", end_date)

    # Basic mock prediction logic (replace later)
    predicted_cpr = 17.45
    estimated_registrants = 51

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

