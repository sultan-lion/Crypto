Crypto Sentiment Telegram Bot

A rules-based crypto trading assistant that analyzes market liquidity and institutional activity, then sends a daily actionable trading plan (BUY / HOLD / RISK-OFF + Entry / SL / TP) directly to Telegram.

The system combines macro crypto signals (ETF flows, stablecoins, VC funding, treasuries) with market structure (trend + volatility) to produce a daily trading decision.

This is not a prediction bot.
It is a decision-support engine.

What the Bot Does

Every day the bot:

Collects crypto market sentiment data

Scores the overall market (0 → 100)

Determines the day type:

BUY DAY

HOLD DAY

SELL / RISK-OFF DAY

Checks trend direction per coin (SMA200)

Calculates volatility (ATR14)

Generates a trading plan:

Entry levels (DCA)

Stop Loss

Take Profit

Sends a formatted report to Telegram

Market Signals Used

The sentiment score is built from 4 liquidity indicators:

Indicator	What it Measures	Meaning
Spot ETF Flows	Institutional demand	Smart money entering/leaving BTC
Stablecoin Market Cap	Liquidity	Capital entering crypto ecosystem
Crypto VC Funding	Long-term confidence	Future cycle strength
Digital Asset Treasury Purchases	Corporate conviction	Balance-sheet adoption

These represent capital movement, not social media sentiment.

Trading Logic
Day Classification
Score	Action
≥ 55	BUY DAY
36-54	HOLD DAY
≤ 35	SELL / RISK-OFF
Trend Filter

Each coin must agree with the macro environment:

Price > SMA200 → Uptrend → Long allowed

Price < SMA200 → Downtrend → Long avoided

Volatility Model (ATR14)

ATR14 = average daily movement over last 14 days.

Used to calculate risk:

SL = Entry − (1.5 × ATR)
TP = Entry + (2 × Risk)

This prevents random stop losses due to normal volatility.

Coins Covered

Default:

BTCUSDT
ETHUSDT
SOLUSDT

You can edit in config.py.

Example Telegram Output

Crypto Signal: BUY DAY (62/100)

Sentiment
ETF flow: +1.2B
Stablecoins: +3.5B
VC funding: 7 rounds

BTCUSDT LONG
Entry: 63,500 / 62,900 / 62,200
SL: 61,750
TP: 67,100

ETHUSDT LONG
Entry: 3,180 / 3,140 / 3,100
SL: 3,020
TP: 3,520

Installation
1) Clone the repository
git clone https://github.com/sultan-lion/Crypto.git
cd Crypto
2) Create virtual environment

Windows:

python -m venv .venv
.venv\Scripts\activate

Mac/Linux:

python3 -m venv .venv
source .venv/bin/activate
3) Install dependencies
pip install -r requirements.txt
Telegram Setup
1) Create a Bot

Open Telegram → search BotFather

/newbot

Choose name and username (must end with "bot")

BotFather will give:

BOT_TOKEN
2) Start the bot

Open your bot chat and press Start
Send message: hi

3) Get Chat ID

Run:

python get_chat_id.py

Copy the printed chat_id.

Environment Variables

Create a file:

.env

Add:

TELEGRAM_BOT_TOKEN=YOUR_TOKEN
TELEGRAM_CHAT_ID=YOUR_CHAT_ID
Run the Bot

Manual run:

python main.py

You should instantly receive a Telegram message.

Automation (Daily Execution)

Recommended: Windows Task Scheduler

Run daily at 9 AM UAE time.

Program:

<path_to_venv>\Scripts\python.exe

Arguments:

main.py

Start in:

project folder

The bot will send a daily trading plan automatically.

File Structure
main.py               → Orchestrator
sources.py            → Sentiment data collectors
market_data.py        → Binance price + ATR + SMA
scoring.py            → Market scoring engine
telegram_push.py      → Telegram sender
config.py             → Strategy settings
.env                  → Secrets (not committed)
Disclaimer

This project is for educational and decision-support purposes only.

It does NOT:

predict prices

guarantee profits

replace risk management

Crypto markets are volatile.
Always verify signals and use proper position sizing.
