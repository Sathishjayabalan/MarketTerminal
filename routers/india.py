from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.india_client import get_all_indices
from services.yfinance_client import get_quote, get_history
import datetime, json

BASE_DIR = Path(__file__).resolve().parent.parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

INFLUENCE_FACTORS = [
    ("USDINR=X","USD/INR"),("BZ=F","BRENT CRUDE"),("GC=F","GOLD"),
    ("^GSPC","S&P 500"),("^TNX","US 10Y YIELD"),
]

@router.get("/india/overview", response_class=HTMLResponse)
async def india_overview(request: Request):
    quotes = get_all_indices()
    return templates.TemplateResponse("partials/india_overview.html", {
        "request": request, "quotes": quotes,
        "updated_at": datetime.datetime.now().strftime("%H:%M:%S"),
    })

@router.get("/india/detail", response_class=HTMLResponse)
async def india_detail(request: Request, symbol: str = "NIFTY 50", name: str = "NIFTY 50"):
    indices = get_all_indices()
    quote = next((q for q in indices if q["name"] == name), None)
    if not quote:
        quote = {"name": name, "symbol": symbol, "price": 0, "change": 0,
                 "change_pct": 0, "year_high": 0, "year_low": 0, "error": "Not found"}
    factors = []
    for fsymbol, fname in INFLUENCE_FACTORS:
        f = get_quote(fsymbol)
        f["name"] = fname
        factors.append(f)
    return templates.TemplateResponse("partials/india_detail.html", {
        "request": request, "quote": quote, "name": name,
        "history_json": json.dumps([]),
        "factors": factors,
        "updated_at": datetime.datetime.now().strftime("%H:%M:%S"),
    })
