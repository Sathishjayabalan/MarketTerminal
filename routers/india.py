from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from services.india_client import get_all_indices, get_index_detail, INDICES

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter(prefix="/india", tags=["india"])

@router.get("/overview", response_class=HTMLResponse)
async def india_overview(request: Request):
    indices = get_all_indices()
    categories = {}
    for idx in indices:
        cat = idx.get("category", "Other")
        categories.setdefault(cat, []).append(idx)
    return templates.TemplateResponse("partials/india_overview.html", {
        "request": request, "categories": categories, "indices": indices,
    })

@router.get("/detail/{symbol:path}", response_class=HTMLResponse)
async def india_detail(request: Request, symbol: str):
    detail = get_index_detail(symbol)
    return templates.TemplateResponse("partials/india_detail.html", {
        "request": request, "detail": detail,
    })
