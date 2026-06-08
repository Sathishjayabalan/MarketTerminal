from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from services.yfinance_client import get_quote
from models import PortfolioPosition
from database import engine

BASE_DIR = Path(__file__).resolve().parent.parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/portfolio", response_class=HTMLResponse)
async def get_portfolio(request: Request):
    with Session(engine) as session:
        positions = session.exec(select(PortfolioPosition)).all()
    enriched = []
    total_value = 0
    total_cost = 0
    for pos in positions:
        quote = get_quote(pos.symbol)
        current_price = quote["price"]
        current_value = current_price * pos.shares
        cost_basis = pos.avg_cost * pos.shares
        pnl = current_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis else 0
        total_value += current_value
        total_cost += cost_basis
        enriched.append({"id": pos.id, "symbol": pos.symbol, "shares": pos.shares,
            "avg_cost": pos.avg_cost, "current_price": round(current_price,2),
            "current_value": round(current_value,2), "pnl": round(pnl,2), "pnl_pct": round(pnl_pct,2)})
    return templates.TemplateResponse("partials/portfolio.html", {
        "request": request, "positions": enriched,
        "total_value": round(total_value,2), "total_pnl": round(total_value-total_cost,2),
    })

@router.post("/portfolio/add", response_class=HTMLResponse)
async def add_position(request: Request, symbol: str = Form(...), shares: float = Form(...), avg_cost: float = Form(...)):
    symbol = symbol.upper().strip()
    with Session(engine) as session:
        session.add(PortfolioPosition(symbol=symbol, shares=shares, avg_cost=avg_cost))
        session.commit()
    return await get_portfolio(request)

@router.post("/portfolio/remove", response_class=HTMLResponse)
async def remove_position(request: Request, position_id: int = Form(...)):
    with Session(engine) as session:
        pos = session.get(PortfolioPosition, position_id)
        if pos:
            session.delete(pos)
            session.commit()
    return await get_portfolio(request)
