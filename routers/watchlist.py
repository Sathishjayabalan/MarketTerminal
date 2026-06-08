from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.yfinance_client import get_quote

BASE_DIR = Path(__file__).resolve().parent.parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
_watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]

@router.get("/watchlist", response_class=HTMLResponse)
async def get_watchlist(request: Request):
    quotes = [get_quote(s) for s in _watchlist[:]]
    return templates.TemplateResponse("partials/watchlist.html", {"request": request, "quotes": quotes})

@router.post("/watchlist/add", response_class=HTMLResponse)
async def add_to_watchlist(request: Request, symbol: str = Form(...)):
    symbol = symbol.upper().strip()
    if symbol not in _watchlist:
        _watchlist.append(symbol)
    quotes = [get_quote(s) for s in _watchlist]
    return templates.TemplateResponse("partials/watchlist.html", {"request": request, "quotes": quotes})

@router.post("/watchlist/remove", response_class=HTMLResponse)
async def remove_from_watchlist(request: Request, symbol: str = Form(...)):
    if symbol in _watchlist:
        _watchlist.remove(symbol)
    quotes = [get_quote(s) for s in _watchlist]
    return templates.TemplateResponse("partials/watchlist.html", {"request": request, "quotes": quotes})
