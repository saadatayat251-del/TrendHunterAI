import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_message(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Telegram Token or Chat ID is missing!")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML" # برای اینکه بتونیم متن رو بولد و زیبا کنیم
    }
    
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")