from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers import market, stocks, forex, news, watchlist, portfolio
from database import create_db_and_tables

app = FastAPI(title="Bloomberg Terminal")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(market.router)
app.include_router(stocks.router)
app.include_router(forex.router)
app.include_router(news.router)
app.include_router(watchlist.router)
app.include_router(portfolio.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
