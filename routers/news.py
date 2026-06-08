from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.yfinance_client import get_news

BASE_DIR = Path(__file__).resolve().parent.parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/news/feed", response_class=HTMLResponse)
async def news_feed(request: Request):
    news = get_news()
    return templates.TemplateResponse("partials/news.html", {"request": request, "news": news})
