import requests
import urllib.parse
from datetime import datetime
from key_rotator import openrouter_keys, sambanova_keys

# دریافت جزئیات زمان جاری برای تزریق هوش زمانی به مدل‌ها
now = datetime.now()
current_year = now.year
current_date_full = now.strftime("%B %d, %Y")

# ==========================================
# تابع مرجع ارسال درخواست به OpenRouter (با چرخش کلید و مدل)
# ==========================================
def run_openrouter_request(prompt, models_list, key_manager, agent_name):
    api_key = key_manager.get_next_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://trendhunter.ai", # برای رعایت قوانین OpenRouter
        "X-Title": "TrendHunter"
    }
    
    # لیست مدل‌های مطمئن و رایگان برای تضمین پاسخگویی
    safe_models = [
        "google/gemini-2.0-flash-lite-preview-02-05:free", 
        "meta-llama/llama-3.3-70b-instruct:free", 
        "openrouter/free"
    ]
    
    for model in safe_models:
        payload = {
            "model": model, 
            "messages": [{"role": "user", "content": prompt}], 
            "temperature": 0.4
        }
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=45)
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
        except Exception:
            continue
    return "Error: No Response from AI Models"

# ==========================================
# ۱. مترجم و سازنده کوئری وایرال (رادار هوشمند)
# ==========================================
def agent_gemini_expand(domain, keyword):
    # این بخش کلمه فارسی را به بهترین جستجوی انگلیسی که "جدیدترین" نتایج را بیاورد تبدیل می‌کند
    prompt = f"""
    Act as a Global Viral Content Researcher.
    Today's Date: {current_date_full}
    
    Input: "{keyword}" (Domain: {domain})
    
    Task:
    1. Translate the keyword to its most effective English search term.
    2. Build ONE search query for TikTok/Twitter/Instagram that targets the MOST RECENT viral activity.
    3. If it's a fast topic (News/Tech), use "today" or "latest". If it's evergreen (Industry), use "2026 hacks/new".
    
    Output ONLY the English query string. No extra text.
    """
    return run_openrouter_request(prompt, [], openrouter_keys, agent_name="Keyword_Translator")

# ==========================================
# ۲. تحلیلگر استراتژیک (گزارش نهایی و لینک‌های جامع)
# ==========================================
def agent_strategist(trend_data, persian_keyword, english_query):
    # ساخت لینک‌های فوق‌هوشمند با فیلترهای زمانی
    encoded_en = urllib.parse.quote(english_query)
    
    tiktok_link = f"https://www.tiktok.com/search?q={encoded_en}"
    twitter_link = f"https://twitter.com/search?q={encoded_en}&f=live" # نمایش لحظه‌ای‌ترین توییت‌ها
    youtube_link = f"https://www.youtube.com/results?search_query={encoded_en}&sp=CAI%253D" # فیلتر مرتب‌سازی بر اساس تاریخ (Newest)
    instagram_link = f"https://www.instagram.com/explore/search/keyword/?q={encoded_en}" # جستجوی کلیدواژه‌ای دقیق اینستاگرام
    gtrends_link = f"https://trends.google.com/trends/explore?q={encoded_en}&date=now%207-d" # بازه ۷ روزه برای دیدن آخرین نوسان
    
    prompt = f"""
    You are a Global Trend Analyst. Today is {current_date_full}.
    Persian Topic: "{persian_keyword}"
    English Query: "{english_query}"
    Scraped Data: "{trend_data}"

    Mission:
    1. Find the LATEST wave of interest. Even if it happened 5 hours ago or last week.
    2. What is the current "Vibe" or "Viral Pattern" (ASMR, Educational, Scandal, Review)?
    3. If live data is weak, use your internal knowledge of {current_year} to provide the most recent global trend strategy for this topic.

    Report Structure (Strictly Persian):
    🔍 **آخرین وضعیت رصد شده:** (توضیح زمان دقیق و نوع برخورد مخاطب با موضوع)
    🔥 **تحلیل وایرال امروز:** (چرا این موضوع الان جذاب شده؟)
    💡 **۳ ایده طلایی برای محتوا:** (بر اساس جدیدترین الگوی وایرال جهانی)
    🎯 **قلاب (Hook) پیشنهادی:** (یک جمله اول ویدیو برای جذب فوری)
    """
    
    report_content = run_openrouter_request(prompt, [], openrouter_keys, agent_name="Strategist")
    
    # ترکیب گزارش با لینک‌های رصد مستقیم
    final_output = f"""
{report_content}

🔗 **لینک‌های رصد لحظه‌ای (آپدیت {current_year}):**
🔹 **اینستاگرام (Keyword Search):** {instagram_link}
🔹 **تیک‌تاک (Viral Feed):** {tiktok_link}
🔹 **یوتیوب (Newest Only):** {youtube_link}
🔹 **گوگل ترندز (Last 7 Days):** {gtrends_link}
🔹 **توییتر (Live News):** {twitter_link}
    """
    return final_output

# ==========================================
# ۳. فیلتر هوشمند سامبانووا (استخراج عصاره تازگی)
# ==========================================
def agent_sambanova_filter(raw_data):
    if "Error" in raw_data or len(raw_data) < 15:
        return "No Recent Live Data"
    
    headers = {
        "Authorization": f"Bearer {sambanova_keys.get_next_key()}", 
        "Content-Type": "application/json"
    }
    
    # تمرکز سامبانووا روی یافتن "جدیدترین" موضوعات در دیتای خام
    prompt = f"Identify the most recent significant event or viral theme from this data. Skip old news. Year: {current_year}. Text: {raw_data[:2800]}"

    payload = {
        "model": "Meta-Llama-3.1-70B-Instruct", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    try:
        response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
    except Exception:
        pass
    return "No Clear Trend Extracted"

# تابع کمکی برای حفظ ساختار قبلی در صورت نیاز
def agent_grok_analyze(data):
    return data
