# sources.py
import re
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}


def _get_json(url: str):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def _get_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


# ---------------------------
# 1) Spot ETF flows (Institutional)
# ---------------------------
def fetch_etf_net_flow_latest_musd() -> float:
    """
    ETF FLOW SIGNAL (USD millions) using BOLD.report API.

    - btc-ff-culm7day = Bitcoin 7 day fund flow (BTC)
    - btc-price = BTC price (USD)

    Convert to USD and return in US$m.
    """
    url = "https://bold.report/api/v1/combined/all-latest.json"
    data = _get_json(url)

    flow_btc_7d = float(data["btc-ff-culm7day"])
    btc_price_usd = float(data["btc-price"])

    flow_usd = flow_btc_7d * btc_price_usd
    return flow_usd / 1e6


# ---------------------------
# 2) Stablecoin market cap (Liquidity)
# ---------------------------
def fetch_stablecoin_total_mcap_usd_and_7d_change_usd():
    """
    Robust stablecoin liquidity signal using DefiLlama stablecoin endpoints.

    Primary:
      - Pull historical totals from stablecoincharts/all
      - Return latest total + 7d change

    Fallback:
      - Pull current list of stablecoins from stablecoins/stablecoins
      - Sum estimated market caps
      - Return total, and 0.0 for 7d change (so pipeline continues)
    """
    chart_urls = [
        "https://stablecoins.llama.fi/stablecoincharts/all",
        "https://api.llama.fi/stablecoins/stablecoincharts/all",
    ]

    # Primary: historical chart series
    for url in chart_urls:
        try:
            series = _get_json(url)
            if isinstance(series, list) and len(series) > 10:
                points = []
                for it in series:
                    if not isinstance(it, dict):
                        continue
                    ts = it.get("date")
                    tc = it.get("totalCirculating", {})
                    if ts is None or not isinstance(tc, dict):
                        continue
                    val = tc.get("peggedUSD")
                    if val is None:
                        continue
                    try:
                        points.append((int(ts), float(val)))
                    except Exception:
                        pass

                points.sort(key=lambda x: x[0])
                if len(points) >= 8:
                    latest_ts, latest_total = points[-1]
                    target_ts = latest_ts - 7 * 24 * 3600
                    week_ago_ts, week_ago_total = min(points, key=lambda p: abs(p[0] - target_ts))
                    change_7d = latest_total - week_ago_total
                    return latest_total, change_7d
        except Exception:
            pass

    # Fallback: current stablecoin list
    list_urls = [
        "https://stablecoins.llama.fi/stablecoins/stablecoins",
        "https://api.llama.fi/stablecoins/stablecoins",
    ]

    for url in list_urls:
        try:
            coins = _get_json(url)
            if isinstance(coins, list) and len(coins) > 10:
                total = 0.0
                for c in coins:
                    if not isinstance(c, dict):
                        continue

                    if c.get("mcap") is not None:
                        try:
                            total += float(c["mcap"])
                            continue
                        except Exception:
                            pass

                    price = c.get("price")
                    circulating = c.get("circulating")
                    try:
                        if price is not None and circulating is not None:
                            total += float(price) * float(circulating)
                    except Exception:
                        pass

                if total > 0:
                    return total, 0.0
        except Exception:
            pass

    raise RuntimeError("Stablecoin endpoints unreachable or returned unexpected format.")


# ---------------------------
# 3) Crypto VC funding (Long-term cycle)
# ---------------------------
def fetch_vc_funding_rounds_last_7d_count() -> int:
    """
    Best-effort scrape for VC funding activity (CryptoRank can be dynamic).
    Returns a rough count of unique dates found in the last 7 days.
    If it fails, returns 0 (so the pipeline doesn't break).
    """
    url = "https://cryptorank.io/funding-rounds"
    try:
        html = _get_html(url)
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True)

        months = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        date_matches = re.findall(rf"{months}\s+\d{{1,2}},\s+\d{{4}}", text)
        unique_dates = sorted(set(date_matches))

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=7)

        cnt = 0
        for d in unique_dates:
            try:
                dt = datetime.strptime(d, "%b %d, %Y").replace(tzinfo=timezone.utc)
                if dt >= cutoff:
                    cnt += 1
            except Exception:
                pass

        return cnt
    except Exception:
        return 0


# ---------------------------
# 4) Digital Asset Treasury Purchases (Conviction)
# ---------------------------
def fetch_treasury_buy_signal_manual() -> int:
    """
    Manual placeholder for now.
    Return:
      20 = notable new treasury buy announced
      10 = neutral / no news
       0 = selling / negative
    """
    return 10