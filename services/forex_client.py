import httpx
from cachetools import TTLCache
from threading import Lock

_cache = TTLCache(maxsize=50, ttl=60)
_lock = Lock()
PAIRS = [("EUR","USD"),("GBP","USD"),("USD","JPY"),("USD","CNY"),("USD","CHF"),("AUD","USD")]

def get_rates() -> list[dict]:
    with _lock:
        if "rates" in _cache:
            return _cache["rates"]
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get("https://api.frankfurter.app/latest?from=EUR")
            data = resp.json()
            eur_rates = data.get("rates", {})
            eur_rates["EUR"] = 1.0
        result = []
        for base, quote in PAIRS:
            try:
                if base == "EUR": rate = eur_rates.get(quote, 0)
                elif quote == "EUR": rate = 1.0 / eur_rates.get(base, 1)
                else: rate = eur_rates.get(quote, 0) / eur_rates.get(base, 1)
                result.append({"pair": f"{base}/{quote}", "rate": round(rate,4), "error": None})
            except Exception as e:
                result.append({"pair": f"{base}/{quote}", "rate": 0, "error": str(e)})
        try:
            import yfinance as yf
            btc = yf.Ticker("BTC-USD")
            result.append({"pair": "BTC/USD", "rate": round(float(btc.fast_info.last_price),2), "error": None})
        except Exception:
            result.append({"pair": "BTC/USD", "rate": 0, "error": "unavailable"})
    except Exception as e:
        result = [{"pair": f"{b}/{q}", "rate": 0, "error": str(e)} for b, q in PAIRS]
    with _lock:
        _cache["rates"] = result
    return result
