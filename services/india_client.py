import yfinance as yf
from cachetools import TTLCache
from threading import Lock
from datetime import datetime

_cache = TTLCache(maxsize=100, ttl=60)
_lock = Lock()

INDICES = [
    {"name": "NIFTY 50",        "symbol": "^NSEI",     "category": "Broad Market"},
    {"name": "SENSEX",          "symbol": "^BSESN",    "category": "Broad Market"},
    {"name": "NIFTY NEXT 50",   "symbol": "^NSMIDCP",  "category": "Broad Market"},
    {"name": "NIFTY 100",       "symbol": "^CNX100",   "category": "Broad Market"},
    {"name": "NIFTY 500",       "symbol": "^CNX500",   "category": "Broad Market"},
    {"name": "NIFTY MIDCAP 100","symbol": "^CNXMIDCAP","category": "Broad Market"},
    {"name": "NIFTY SMALLCAP",  "symbol": "^CNXSC",    "category": "Broad Market"},
    {"name": "NIFTY BANK",      "symbol": "^NSEBANK",  "category": "Sectoral"},
    {"name": "NIFTY IT",        "symbol": "^CNXIT",    "category": "Sectoral"},
    {"name": "NIFTY PHARMA",    "symbol": "^CNXPHARMA","category": "Sectoral"},
    {"name": "NIFTY AUTO",      "symbol": "^CNXAUTO",  "category": "Sectoral"},
    {"name": "NIFTY FMCG",      "symbol": "^CNXFMCG",  "category": "Sectoral"},
    {"name": "NIFTY METAL",     "symbol": "^CNXMETAL", "category": "Sectoral"},
    {"name": "NIFTY ENERGY",    "symbol": "^CNXENERGY","category": "Sectoral"},
    {"name": "NIFTY REALTY",    "symbol": "^CNXREALTY","category": "Sectoral"},
    {"name": "NIFTY PSU BANK",  "symbol": "^CNXPSUBANK","category": "Sectoral"},
    {"name": "INDIA VIX",       "symbol": "^INDIAVIX", "category": "Volatility"},
]

MACRO_FACTORS = [
    {"name": "USD/INR",           "symbol": "INR=X",    "impact": "HIGH", "direction": "inverse"},
    {"name": "Brent Crude",       "symbol": "BZ=F",     "impact": "HIGH", "direction": "inverse"},
    {"name": "Gold",              "symbol": "GC=F",     "impact": "MED",  "direction": "positive"},
    {"name": "S&P 500",           "symbol": "^GSPC",    "impact": "HIGH", "direction": "positive"},
    {"name": "Nasdaq",            "symbol": "^IXIC",    "impact": "HIGH", "direction": "positive"},
    {"name": "US 10Y Yield",      "symbol": "^TNX",     "impact": "MED",  "direction": "inverse"},
    {"name": "Hang Seng",         "symbol": "^HSI",     "impact": "MED",  "direction": "positive"},
    {"name": "DXY Dollar Index",  "symbol": "DX-Y.NYB", "impact": "HIGH", "direction": "inverse"},
]

def _fetch_quote(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if hist.empty:
            return {"price": 0, "change": 0, "change_pct": 0, "year_high": 0, "year_low": 0, "error": "No data"}
        last = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else last
        change = last - prev
        change_pct = (change / prev * 100) if prev else 0
        try:
            info = ticker.fast_info
            year_high = float(getattr(info, "year_high", 0) or 0)
            year_low = float(getattr(info, "year_low", 0) or 0)
        except Exception:
            year_high = year_low = 0
        return {"price": round(last, 2), "change": round(change, 2), "change_pct": round(change_pct, 2), "year_high": round(year_high, 2), "year_low": round(year_low, 2), "error": None}
    except Exception as e:
        return {"price": 0, "change": 0, "change_pct": 0, "year_high": 0, "year_low": 0, "error": str(e)[:50]}

def _get_sentiment(change_pct, direction):
    if direction == "inverse":
        if change_pct > 0.3: return "BEARISH"
        if change_pct < -0.3: return "BULLISH"
    else:
        if change_pct > 0.3: return "BULLISH"
        if change_pct < -0.3: return "BEARISH"
    return "NEUTRAL"

def get_all_indices():
    with _lock:
        if "indices" in _cache:
            return _cache["indices"]
    result = []
    for idx in INDICES:
        q = _fetch_quote(idx["symbol"])
        result.append({**idx, **q})
    with _lock:
        _cache["indices"] = result
    return result

def get_index_detail(symbol):
    cache_key = f"detail_{symbol}"
    with _lock:
        if cache_key in _cache:
            return _cache[cache_key]
    meta = next((i for i in INDICES if i["symbol"] == symbol), {"name": symbol, "symbol": symbol, "category": ""})
    quote = _fetch_quote(symbol)
    factors = []
    for f in MACRO_FACTORS:
        fq = _fetch_quote(f["symbol"])
        sentiment = _get_sentiment(fq.get("change_pct", 0), f["direction"])
        factors.append({**f, **fq, "sentiment": sentiment})
    detail = {**meta, **quote, "factors": factors, "as_of": datetime.now().strftime("%H:%M:%S IST")}
    with _lock:
        _cache[cache_key] = detail
    return detail
