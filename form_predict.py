from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()  # <-- This is what `main.py` is trying to import
templates = Jinja2Templates(directory="templates")

@router.get("/predict-form", response_class=HTMLResponse)
async def predict_form(request: Request):
    return templates.TemplateResponse("predict_form.html", {"request": request})

@router.post("/predict-form", response_class=HTMLResponse)
async def predict_submit(
    request: Request,
    topic: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    start_date: str = Form(...)
):
    try:
        # Replace with your actual processing logic
        results = {
            "topic": topic,
            "city": city,
            "state": state,
            "start_date": start_date,
            "end_date": "calculated in backend"
        }
        return templates.TemplateResponse("predict_result.html", {
            "request": request,
            "results": results
        })
    except Exception as e:
        return templates.TemplateResponse("predict_result.html", {
            "request": request,
            "results": {"error": str(e)}
        })

