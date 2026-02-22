import requests
from config import TELEGRAM_BOT_TOKEN

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
r = requests.get(url, timeout=30)
r.raise_for_status()
data = r.json()

print(data)

if data.get("result"):
    last = data["result"][-1]
    print("\nCHAT_ID =", last["message"]["chat"]["id"])
else:
    print("\nNo updates found. Send a message to your bot first.")