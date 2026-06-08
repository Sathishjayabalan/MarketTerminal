import httpx
from cachetools import TTLCache
from threading import Lock

_cache = TTLCache(maxsize=50, ttl=30)
_lock = Lock()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

NSE_INDEX_MAP = {
    "NIFTY 50":      "NIFTY 50",
    "SENSEX":        "SENSEX",
    "NIFTY BANK":    "NIFTY BANK",
    "NIFTY IT":      "NIFTY IT",
    "NIFTY MIDCAP":  "NIFTY MIDCAP 100",
    "INDIA VIX":     "India VIX",
}

def _get_session():
    client = httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True)
    client.get("https://www.nseindia.com")
    return client

def get_all_indices() -> list[dict]:
    with _lock:
        if "indices" in _cache:
            return _cache["indices"]
    try:
        with _get_session() as client:
            resp = client.get("https://www.nseindia.com/api/allIndices")
            data = resp.json()
        all_idx = {item["index"]: item for item in data.get("data", [])}
        result = []
        for display_name, nse_name in NSE_INDEX_MAP.items():
            item = all_idx.get(nse_name)
            if item:
                last = float(item.get("last", 0))
                prev = float(item.get("previousClose", last))
                change = float(item.get("change", 0))
                change_pct = float(item.get("percentChange", 0))
                result.append({
                    "name": display_name,
                    "symbol": nse_name,
                    "price": round(last, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "year_high": float(item.get("yearHigh", 0)),
                    "year_low": float(item.get("yearLow", 0)),
                    "error": None,
                })
            else:
                result.append({"name": display_name, "symbol": nse_name,
                    "price": 0, "change": 0, "change_pct": 0,
                    "year_high": 0, "year_low": 0, "error": "N/A"})
    except Exception as e:
        result = [{"name": n, "symbol": s, "price": 0, "change": 0,
            "change_pct": 0, "year_high": 0, "year_low": 0, "error": str(e)[:40]}
            for n, s in NSE_INDEX_MAP.items()]
    with _lock:
        _cache["indices"] = result
    return result
