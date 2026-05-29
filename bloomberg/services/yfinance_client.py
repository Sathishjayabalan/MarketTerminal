import yfinance as yf
from cachetools import TTLCache
from threading import Lock

_quote_cache = TTLCache(maxsize=200, ttl=30)
_history_cache = TTLCache(maxsize=50, ttl=300)
_lock = Lock()


def get_quote(symbol: str) -> dict:
    with _lock:
        if symbol in _quote_cache:
            return _quote_cache[symbol]
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        hist = ticker.history(period="2d", interval="1d")

        price = float(info.last_price) if info.last_price else 0.0
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price
        change = price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0.0

        result = {
            "symbol": symbol,
            "price": round(price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": int(info.three_month_average_volume or 0),
            "market_cap": int(info.market_cap or 0),
            "fifty_two_week_high": round(float(info.year_high or 0), 2),
            "fifty_two_week_low": round(float(info.year_low or 0), 2),
            "error": None,
        }
    except Exception as e:
        result = {
            "symbol": symbol,
            "price": 0,
            "change": 0,
            "change_pct": 0,
            "volume": 0,
            "market_cap": 0,
            "fifty_two_week_high": 0,
            "fifty_two_week_low": 0,
            "error": str(e),
        }

    with _lock:
        _quote_cache[symbol] = result
    return result


def get_history(symbol: str, period: str = "1d", interval: str = "5m") -> list[dict]:
    cache_key = f"{symbol}:{period}:{interval}"
    with _lock:
        if cache_key in _history_cache:
            return _history_cache[cache_key]
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        result = [
            {"time": int(idx.timestamp()), "value": round(float(row["Close"]), 2)}
            for idx, row in hist.iterrows()
        ]
    except Exception:
        result = []
    with _lock:
        _history_cache[cache_key] = result
    return result


def get_news(symbol: str = "") -> list[dict]:
    try:
        if symbol:
            ticker = yf.Ticker(symbol)
            news = ticker.news or []
        else:
            ticker = yf.Ticker("SPY")
            news = ticker.news or []

        result = []
        for item in news[:10]:
            content = item.get("content", {})
            result.append({
                "title": content.get("title", item.get("title", "No title")),
                "url": content.get("canonicalUrl", {}).get("url", "#"),
                "source": content.get("provider", {}).get("displayName", "Unknown"),
                "published": content.get("pubDate", ""),
            })
        return result
    except Exception:
        return []
