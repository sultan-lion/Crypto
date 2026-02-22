# main.py
from sources import (
    fetch_etf_net_flow_latest_musd,
    fetch_stablecoin_total_mcap_usd_and_7d_change_usd,
    fetch_vc_funding_rounds_last_7d_count,
    fetch_treasury_buy_signal_manual,
)
from scoring import total_score
from market_data import coin_levels
from telegram_push import send_telegram_message
from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    COINS,
    BUY_DAY_SCORE,
    SELL_DAY_SCORE,
    ATR_PERIOD,
    ATR_MULTIPLIER,
    R_MULTIPLIER,
    SMA_TREND_PERIOD,
    DCA_LEVELS_PCT,
)


def decide_day(score: int) -> str:
    if score >= BUY_DAY_SCORE:
        return "BUY DAY"
    if score <= SELL_DAY_SCORE:
        return "SELL / RISK-OFF DAY"
    return "HOLD DAY"


def trade_plan_for_coin(day_action: str, info: dict) -> str:
    entry = info["entry"]
    atr = info["atr"]
    trend = info["trend"]

    # Trend filter per coin
    if day_action == "BUY DAY" and trend != "UP":
        return f"{info['symbol']}: SKIP (trend DOWN vs SMA{SMA_TREND_PERIOD})"

    if day_action == "SELL / RISK-OFF DAY" and trend != "DOWN":
        return f"{info['symbol']}: HOLD/REDUCE (trend not DOWN vs SMA{SMA_TREND_PERIOD})"

    # BUY day = Long plan with Entry/SL/TP
    if day_action == "BUY DAY":
        sl = entry - (ATR_MULTIPLIER * atr)
        tp = entry + (R_MULTIPLIER * (entry - sl))
        dcas = [entry * (1 + p / 100.0) for p in DCA_LEVELS_PCT]
        dca_txt = ", ".join([f"{x:,.2f}" for x in dcas])

        return (
            f"{info['symbol']} 🟢 LONG\n"
            f"Entry (DCA): {dca_txt}\n"
            f"SL: {sl:,.2f} | TP: {tp:,.2f}\n"
            f"Trend: UP (Close > SMA{SMA_TREND_PERIOD}) | ATR{ATR_PERIOD}: {atr:,.2f}"
        )

    # SELL day = risk-off guidance (no shorts yet)
    if day_action == "SELL / RISK-OFF DAY":
        return (
            f"{info['symbol']} 🔴 RISK-OFF\n"
            f"Trend: DOWN (Close < SMA{SMA_TREND_PERIOD})\n"
            f"Action: reduce exposure / tighten stops / avoid new longs\n"
            f"ATR{ATR_PERIOD}: {atr:,.2f}"
        )

    # HOLD day
    return f"{info['symbol']} 🟡 HOLD (no new action)"


def main():
    # ---- Sentiment data
    etf_flow = fetch_etf_net_flow_latest_musd()
    stable_mcap, stable_change = fetch_stablecoin_total_mcap_usd_and_7d_change_usd()
    vc_count = fetch_vc_funding_rounds_last_7d_count()
    treasury_points = fetch_treasury_buy_signal_manual()

    score, breakdown = total_score(etf_flow, stable_change, vc_count, treasury_points)
    day_action = decide_day(score)

    # ---- Coin plans
    plans = []
    for sym in COINS:
        info = coin_levels(sym, SMA_TREND_PERIOD, ATR_PERIOD)
        plans.append(trade_plan_for_coin(day_action, info))

    # ---- Telegram message (HTML)
    header = f"Crypto Signal: {day_action} ({score}/100)\n"
    sentiment_block = (
        f"\nSentiment\n"
        f"- ETF 7d flow: {etf_flow:,.1f} US$m\n"
        f"- Stablecoin mcap: ${stable_mcap / 1e9:,.2f}B\n"
        f"- Stablecoin 7d: ${stable_change / 1e9:,.2f}B\n"
        f"- VC rounds (7d est): {vc_count}\n"
        f"- Breakdown: ETF {breakdown['etf']}/35 | Stable {breakdown['stable']}/30 | VC {breakdown['vc']}/15 | Treasury {breakdown['treasury']}/20\n"
    )
    plans_block = "\nCoin Plans\n" + "\n\n".join(plans)
    footer = "\n\nRules-based assistant — confirm manually before trading."
    text = header + sentiment_block + plans_block + footer

    send_telegram_message(
        bot_token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
        text=text
    )

    print("✅ Telegram message sent.")
    print(text)


if __name__ == "__main__":
    main()