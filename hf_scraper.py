import requests

# آدرس اسپیس هاگینگ فیس شما
HF_PROXY_URL = "https://smithjan-trend-scraper-proxy.hf.space/scrape"

def scrape_social_media(expanded_keywords):
    try:
        # ارسال مستقیم عبارت انگلیسی ساخته شده توسط هوش مصنوعی
        response = requests.get(HF_PROXY_URL, params={"keyword": expanded_keywords}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("raw_data", "دیتایی یافت نشد.")
        else:
            return f"Error from HF: {response.status_code}"
            
    except Exception as e:
        print(f"Scraping Error: {e}")
        return "خطا در استخراج دیتای خام."
