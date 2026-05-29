from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.yfinance_client import get_quote

router = APIRouter()
templates = Jinja2Templates(directory="templates")

_default_watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]


@router.get("/watchlist", response_class=HTMLResponse)
async def get_watchlist(request: Request):
    symbols = _default_watchlist[:]
    quotes = [get_quote(s) for s in symbols]
    return templates.TemplateResponse("partials/watchlist.html", {
        "request": request,
        "quotes": quotes,
    })


@router.post("/watchlist/add", response_class=HTMLResponse)
async def add_to_watchlist(request: Request, symbol: str = Form(...)):
    symbol = symbol.upper().strip()
    if symbol not in _default_watchlist:
        _default_watchlist.append(symbol)
    quotes = [get_quote(s) for s in _default_watchlist]
    return templates.TemplateResponse("partials/watchlist.html", {
        "request": request,
        "quotes": quotes,
    })


@router.post("/watchlist/remove", response_class=HTMLResponse)
async def remove_from_watchlist(request: Request, symbol: str = Form(...)):
    if symbol in _default_watchlist:
        _default_watchlist.remove(symbol)
    quotes = [get_quote(s) for s in _default_watchlist]
    return templates.TemplateResponse("partials/watchlist.html", {
        "request": request,
        "quotes": quotes,
    })
