from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.yfinance_client import get_quote
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
INDICES = [("^GSPC","S&P 500"),("^IXIC","NASDAQ"),("^DJI","DOW"),("^VIX","VIX")]

@router.get("/market/overview", response_class=HTMLResponse)
async def market_overview(request: Request):
    quotes = []
    for symbol, name in INDICES:
        q = get_quote(symbol)
        q["name"] = name
        quotes.append(q)
    return templates.TemplateResponse("partials/market_overview.html", {
        "request": request, "quotes": quotes,
        "updated_at": datetime.datetime.now().strftime("%H:%M:%S"),
    })
