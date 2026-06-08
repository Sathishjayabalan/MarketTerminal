from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.yfinance_client import get_quote, get_history
import datetime, json

BASE_DIR = Path(__file__).resolve().parent.parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

INDIA_INDICES = [
    ("^NSEI","NIFTY 50"),("^BSESN","SENSEX"),("^NSEBANK","NIFTY BANK"),
    ("^CNXIT","NIFTY IT"),("^NSEMDCP100","NIFTY MIDCAP"),("^INDIAVIX","INDIA VIX"),
]
INFLUENCE_FACTORS = [
    ("USDINR=X","USD/INR"),("BZ=F","BRENT CRUDE"),("GC=F","GOLD"),
    ("^GSPC","S&P 500"),("^TNX","US 10Y YIELD"),
]

@router.get("/india/overview", response_class=HTMLResponse)
async def india_overview(request: Request):
    quotes = []
    for symbol, name in INDIA_INDICES:
        q = get_quote(symbol)
        q["name"] = name
        quotes.append(q)
    return templates.TemplateResponse("partials/india_overview.html", {
        "request": request, "quotes": quotes,
        "updated_at": datetime.datetime.now().strftime("%H:%M:%S"),
    })

@router.get("/india/detail", response_class=HTMLResponse)
async def india_detail(request: Request, symbol: str = "^NSEI", name: str = "NIFTY 50"):
    quote = get_quote(symbol)
    history = get_history(symbol, period="1d", interval="5m")
    factors = []
    for fsymbol, fname in INFLUENCE_FACTORS:
        f = get_quote(fsymbol)
        f["name"] = fname
        factors.append(f)
    return templates.TemplateResponse("partials/india_detail.html", {
        "request": request, "quote": quote, "name": name,
        "history_json": json.dumps(history), "factors": factors,
        "updated_at": datetime.datetime.now().strftime("%H:%M:%S"),
    })
