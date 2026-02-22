# telegram_push.py
import requests


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True
        # No parse_mode for now (plain text) to avoid Bad Request due to HTML tags
    }
    r = requests.post(url, json=payload, timeout=30)

    # Helpful debug if it fails again
    if r.status_code != 200:
        try:
            print("Telegram response:", r.json())
        except Exception:
            print("Telegram raw response:", r.text)

    r.raise_for_status()