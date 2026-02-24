import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_message(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("--- بررسی اتصال تلگرام ---")
    if not token or not chat_id:
        print("❌ خطای قطعی: توکن یا آیدی تلگرام در تنظیمات Environment رندر وارد نشده است!")
        return False

    # پاک کردن فاصله‌های خالی احتمالی که موقع کپی کردن افتاده‌اند
    token = token.strip()
    chat_id = str(chat_id).strip()

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("✅ پیام با موفقیت به تلگرام ارسال شد!")
            return True
        else:
            print(f"❌ سرور تلگرام اجازه نداد! کد ارور {response.status_code} | دلیل: {response.text}")
            return False
    except Exception as e:
        print(f"❌ خطای اینترنت بین سرور رندر و تلگرام: {e}")
        return False
