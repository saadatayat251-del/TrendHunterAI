import requests

# آدرسی که از هاگینگ فیس کپی کردی را اینجا جایگزین کن
# حتماً در انتها /scrape را داشته باشد
HF_PROXY_URL = "https://smithjan-trend-scraper-proxy.hf.space/scrape"

def scrape_social_media(expanded_keywords):
    """
    این تابع به اسپیس هاگینگ فیس ما وصل می‌شود تا دیتای شبکه‌های اجتماعی را 
    بدون فاش شدن آی‌پی سرور اصلی استخراج کند.
    """
    try:
        # چون کلمات گسترش یافته زیاد است، 3 کلمه مهم اول را برای سرچ می‌فرستیم
        keywords_list = expanded_keywords.split(',')[:3]
        search_query = " ".join(keywords_list)
        
        response = requests.get(HF_PROXY_URL, params={"keyword": search_query}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("raw_data", "دیتایی یافت نشد.")
        else:
            return f"Error from HF: {response.status_code}"
            
    except Exception as e:
        print(f"Scraping Error: {e}")
        return "خطا در استخراج دیتای خام."
