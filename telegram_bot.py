import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_message(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # لاگ دقیق برای اینکه بفهمیم متغیرها لود شده‌اند یا نه
    if not token or not chat_id:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing in environment variables!")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"❌ Telegram API Error: {response.status_code} - {response.text}")
        else:
            print("✅ Telegram message sent successfully!")
            return True
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")
        return False
