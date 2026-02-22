# Crypto Sentiment Telegram Bot

A daily crypto trading assistant that analyzes market liquidity and institutional activity, then sends a clear trading plan to Telegram (BUY / HOLD / RISK-OFF + Entry / SL / TP).

This is **not a price prediction bot** — it is a rules-based decision support tool.

---

## What It Does

Every day the bot:

1. Collects market sentiment data
2. Calculates a market score (0–100)
3. Classifies the day:
   - BUY DAY
   - HOLD DAY
   - SELL / RISK-OFF DAY
4. Checks trend direction (SMA200)
5. Measures volatility (ATR14)
6. Generates a trading plan
7. Sends the result to Telegram

---

## Market Signals Used

The score is based on real capital flows:

- Spot Bitcoin ETF flows (institutional demand)
- Stablecoin market cap change (liquidity entering/leaving crypto)
- Crypto VC funding activity (long-term confidence)
- Digital asset treasury purchases (corporate adoption)

---

## Trading Logic

**Day Classification**

| Score | Action |
|------|------|
| ≥ 55 | BUY DAY |
| 36–54 | HOLD DAY |
| ≤ 35 | SELL / RISK-OFF |

**Trend Filter**
- Price > SMA200 → Long trades allowed
- Price < SMA200 → Avoid longs

**Risk Model (ATR14)**
- SL = Entry − (1.5 × ATR)
- TP ≈ 2R (twice the risk)

---

## Supported Coins
Configured in `config.py` (default):
BTCUSDT
ETHUSDT
SOLUSDT

---


---

## Installation

Clone the repo:

```bash
git clone https://github.com/sultan-lion/Crypto.git
cd Crypto

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

---

**Disclaimer**

For educational and decision-support purposes only.
Not financial advice. Always verify signals and manage risk.


