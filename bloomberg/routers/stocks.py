from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.yfinance_client import get_quote, get_history, get_news
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/stocks/quote", response_class=HTMLResponse)
async def stock_quote(request: Request, symbol: str = "AAPL"):
    symbol = symbol.upper().strip()
    quote = get_quote(symbol)
    history = get_history(symbol, period="1d", interval="5m")
    news = get_news(symbol)[:5]

    return templates.TemplateResponse("partials/stock_quote.html", {
        "request": request,
        "quote": quote,
        "history_json": json.dumps(history),
        "news": news,
    })
