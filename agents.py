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
    
    for model in models_list:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3} # دمای پایین برای جلوگیری از چرت‌وپرت گویی
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=45)
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data:
                    return data['choices'][0]['message']['content']
        except Exception:
            continue
    raise Exception(f"خطای مدل‌های {agent_name}: هیچ پاسخی دریافت نشد.")

# ==========================================
# 1. Keyword Expander
# ==========================================
def agent_gemini_expand(domain, keyword):
    # استفاده از مدل‌های باهوش‌تر برای جلوگیری از گیج شدن
    models = ["meta-llama/llama-3.3-70b-instruct:free", "google/gemini-2.0-flash-lite-preview-02-05:free", "openrouter/free"]
    
    prompt = f"تو یک مترجم و متخصص سئو هستی. فقط و فقط 3 کلمه کلیدی مترادف یا مرتبط به انگلیسی برای عبارت '{keyword}' (در حوزه {domain}) تولید کن. کلمات را با کاما جدا کن. هیچ کلمه اضافه، سلام یا توضیحی ننویس!"
    
    return run_openrouter_request(prompt, models, openrouter_keys, agent_name="Keyword_Expander")

# ==========================================
# 2. Grok Analyzer (حذف شد و ادغام شد در استراتژیست)
# ==========================================
def agent_grok_analyze(data):
    # برای جلوگیری از حرف‌های اضافه، این مرحله را ساده کردیم
    return data

# ==========================================
# 3. Strategist Agent (مغز اصلی با دستورات به شدت سخت‌گیرانه)
# ==========================================
def agent_strategist(trend_data, original_keyword):
    models = ["meta-llama/llama-3.3-70b-instruct:free", "google/gemini-2.0-flash-lite-preview-02-05:free", "openrouter/free"]
    
    # ساخت لینک‌های جستجوی مستقیم برای کاربر
    encoded_kw = urllib.parse.quote(original_keyword)
    tiktok_link = f"https://www.tiktok.com/search?q={encoded_kw}"
    twitter_link = f"https://twitter.com/search?q={encoded_kw}&src=typed_query"
    
    prompt = f"""
    تو یک استراتژیست شبکه‌های اجتماعی ایرانی هستی. وظیفه تو تحلیل این دیتای خام است: "{trend_data}"
    موضوع اصلی سرچ شده این است: "{original_keyword}"

    قوانین به شدت مهم (اگر رعایت نکنی جریمه می‌شوی):
    ۱. اگر دیتای خام شامل جملاتی مثل "آماده پاسخگویی هستم"، "error"، یا دیتای بی‌معنی بود، اصلاً تحلیل نکن! فقط بنویس: "❌ دیتای وایرال خاصی برای این کلمه در شبکه‌های جهانی یافت نشد."
    ۲. به هیچ وجه داستان‌سرایی نکن و کلمات قلمبه سلمبه به کار نبر.
    ۳. دقیقاً در فرمت زیر پاسخ بده:

    وضعیت ترند: (آیا در توییتر/تیک‌تاک ترند است یا نه؟ در یک خط)
    
    ۳ ایده ساده و عملی برای ویدیو/محتوا:
    ۱. (ایده اول)
    ۲. (ایده دوم)
    ۳. (ایده سوم)

    🔗 لینک‌های رصد مستقیم شما:
    تیک‌تاک: {tiktok_link}
    توییتر(X): {twitter_link}
    """
    
    return run_openrouter_request(prompt, models, openrouter_keys, agent_name="Strategist")

# ==========================================
# 4. SambaNova Agent (فیلتر دیتا)
# ==========================================
def agent_sambanova_filter(raw_data):
    headers = {"Authorization": f"Bearer {sambanova_keys.get_next_key()}", "Content-Type": "application/json"}
    models = ["Meta-Llama-3.1-70B-Instruct", "Meta-Llama-3.1-8B-Instruct"]
    
    prompt = f"این متن خام از اینترنت است: '{raw_data}'. اگر متن شامل ارور، یا جملات هوش مصنوعی مثل 'من یک هوش مصنوعی هستم' است، فقط کلمه 'EMPTY' را برگردان. در غیر این صورت، فقط 3 نکته مهم آن را به فارسی خلاصه کن."

    for model in models:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
        try:
            response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception:
            continue
    return "EMPTY"
