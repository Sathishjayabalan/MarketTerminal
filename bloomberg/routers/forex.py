from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.forex_client import get_rates
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/forex/rates", response_class=HTMLResponse)
async def forex_rates(request: Request):
    rates = get_rates()
    return templates.TemplateResponse("partials/forex.html", {
        "request": request,
        "rates": rates,
        "updated_at": datetime.datetime.now().strftime("%H:%M:%S"),
    })
