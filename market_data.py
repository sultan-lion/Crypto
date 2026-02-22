# market_data.py
import requests

BASE = "https://api.binance.com"

def fetch_klines(symbol: str, interval: str = "1d", limit: int = 220):
    url = f"{BASE}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def last_price(symbol: str) -> float:
    url = f"{BASE}/api/v3/ticker/price"
    r = requests.get(url, params={"symbol": symbol}, timeout=30)
    r.raise_for_status()
    return float(r.json()["price"])

def sma(values, period: int) -> float:
    if len(values) < period:
        raise ValueError("Not enough data for SMA")
    return sum(values[-period:]) / period

def atr(highs, lows, closes, period: int = 14) -> float:
    # True Range
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
        trs.append(tr)
    if len(trs) < period:
        raise ValueError("Not enough data for ATR")
    return sum(trs[-period:]) / period

def coin_levels(symbol: str, sma_period: int, atr_period: int):
    k = fetch_klines(symbol, "1d", max(atr_period + sma_period + 5, 220))

    closes = [float(x[4]) for x in k]
    highs  = [float(x[2]) for x in k]
    lows   = [float(x[3]) for x in k]

    entry = last_price(symbol)
    sma_val = sma(closes, sma_period)
    atr_val = atr(highs, lows, closes, atr_period)

    trend = "UP" if closes[-1] > sma_val else "DOWN"

    return {
        "symbol": symbol,
        "entry": entry,
        "close": closes[-1],
        "sma": sma_val,
        "atr": atr_val,
        "trend": trend
    }