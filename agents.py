import requests
import urllib.parse
from key_rotator import openrouter_keys, sambanova_keys

# ==========================================
# تابع ارسال درخواست به OpenRouter
# ==========================================
def run_openrouter_request(prompt, models_list, key_manager, agent_name):
    api_key = key_manager.get_next_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # مدل‌های قدرتمند و رایگان
    safe_models = ["google/gemini-2.0-flash-lite-preview-02-05:free", "meta-llama/llama-3.3-70b-instruct:free", "openrouter/free"]
    
    for model in safe_models:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=45)
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data:
                    return data['choices'][0]['message']['content']
        except Exception:
            continue
    return "Error: No Response"

# ==========================================
# 1. مترجم و سازنده کوئری (هوش اصلی سیستم)
# ==========================================
def agent_gemini_expand(domain, keyword):
    # این تابع کلمه فارسی شما را می‌گیرد و بهترین عبارت انگلیسی برای سرچ در تیک‌تاک را می‌سازد
    prompt = f"""
    Act as a Search Engine Expert.
    Input Keyword: "{keyword}" (Language: Persian).
    Domain: {domain}.

    Task:
    1. Translate the keyword to its most popular English equivalent.
    2. Add 1 viral modifier (like 'hack', 'review', 'trend', 'problem').
    3. Output ONLY the final English search query string. Do NOT write anything else.
    
    Example Input: کرم ضد آفتاب
    Example Output: best sunscreen 2025 review
    """
    return run_openrouter_request(prompt, [], openrouter_keys, agent_name="Keyword_Translator")

# ==========================================
# 2. گروک (حذف شد - نیازی نیست)
# ==========================================
def agent_grok_analyze(data):
    return data

# ==========================================
# 3. تحلیلگر ترند (گزارش واقعیت)
# ==========================================
def agent_strategist(trend_data, original_keyword):
    # لینک‌های مستقیم برای اینکه خودت هم بتوانی چک کنی
    encoded_kw = urllib.parse.quote(original_keyword)
    tiktok_link = f"https://www.tiktok.com/search?q={encoded_kw}"
    twitter_link = f"https://twitter.com/search?q={encoded_kw}&src=typed_query"
    
    prompt = f"""
    تو یک تحلیلگر ترند خبری هستی. وظیفه تو بررسی دیتای استخراج شده از اینترنت است.
    موضوع اصلی: "{original_keyword}"
    دیتای خام اسکریپ شده: "{trend_data}"

    وظیفه:
    ۱. دیتای خام را بخوان. آیا مردم واقعاً دارند درباره این موضوع حرف می‌زنند؟
    ۲. اگر بله، دقیقاً چه می‌گویند؟ (دعواست؟ چالش جدید است؟ محصول جدید است؟)
    ۳. اگر دیتا ناقص یا خالی بود، صادقانه بگو "ترند خاصی یافت نشد" و الکی داستان نساز.

    خروجی را دقیقاً به این فرمت فارسی بنویس:

    📊 وضعیت واقعی ترند: (آیا الان وایرال است؟)
    
    🗣️ بحث اصلی چیه؟: (خلاصه اتفاقی که دارد می‌افتد - ۲ خط)

    🌍 سیگنال‌های دریافتی:
    - (نکته اول از دل دیتا)
    - (نکته دوم از دل دیتا)

    🔗 لینک‌های رصد دستی:
    تیک‌تاک: {tiktok_link}
    توییتر: {twitter_link}
    """
    
    return run_openrouter_request(prompt, [], openrouter_keys, agent_name="Trend_Analyst")

# ==========================================
# 4. سامبانووا (فیلتر زباله‌ها)
# ==========================================
def agent_sambanova_filter(raw_data):
    if "Error" in raw_data or len(raw_data) < 10:
        return "No Data Found"
        
    headers = {"Authorization": f"Bearer {sambanova_keys.get_next_key()}", "Content-Type": "application/json"}
    # مدل قوی‌تر برای سامبانووا
    models = ["Meta-Llama-3.1-70B-Instruct"]
    
    prompt = f"Extract the main topics and sentiments from this raw social media text. Ignore errors. Text: {raw_data[:2500]}"

    for model in models:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        try:
            response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception:
            continue
    return "No Data Scraped"
