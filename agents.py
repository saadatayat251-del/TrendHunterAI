import requests
import urllib.parse
from datetime import datetime
from key_rotator import openrouter_keys, sambanova_keys

# دریافت سال میلادی جاری (مثلا 2026)
current_year = datetime.now().year

# ==========================================
# تابع ارسال درخواست به OpenRouter
# ==========================================
def run_openrouter_request(prompt, models_list, key_manager, agent_name):
    api_key = key_manager.get_next_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    safe_models = ["google/gemini-2.0-flash-lite-preview-02-05:free", "meta-llama/llama-3.3-70b-instruct:free", "openrouter/free"]
    
    for model in safe_models:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.4}
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
# 1. تبدیل‌گر هوشمند (ساخت کوئری وایرال)
# ==========================================
def agent_gemini_expand(domain, keyword):
    prompt = f"""
    Act as a Viral Content Researcher.
    Current Year: {current_year}
    Input Keyword: "{keyword}" (Language: Persian).
    Domain: {domain}.

    Task:
    1. Translate the keyword to English.
    2. Create ONE search query for the LATEST trends in {current_year}.
    3. Use modifiers like "new {current_year}", "latest trends", "viral hacks".
    
    Example Input: کفش (Fashion)
    Example Output: best sneaker trends {current_year}

    Output ONLY the English query string. No explanations.
    """
    return run_openrouter_request(prompt, [], openrouter_keys, agent_name="Keyword_Translator")

# ==========================================
# 2. گروک (حذف شد)
# ==========================================
def agent_grok_analyze(data):
    return data

# ==========================================
# 3. استراتژیست محتوا (تحلیل الگوی روز + لینک‌های کامل)
# ==========================================
def agent_strategist(trend_data, persian_keyword, english_query):
    # ساخت لینک‌های تمام پلتفرم‌ها
    encoded_en = urllib.parse.quote(english_query)
    
    tiktok_link = f"https://www.tiktok.com/search?q={encoded_en}"
    twitter_link = f"https://twitter.com/search?q={encoded_en}&f=live" # فیلتر زنده
    youtube_link = f"https://www.youtube.com/results?search_query={encoded_en}"
    instagram_link = f"https://www.instagram.com/explore/search/keyword/?q={encoded_en}"
    gtrends_link = f"https://trends.google.com/trends/explore?q={encoded_en}&date=now%207-d" # ترند ۷ روز اخیر
    
    prompt = f"""
    You are a Global Trend Spotter.
    Current Year: {current_year}
    User's Topic: "{persian_keyword}"
    Search Query: "{english_query}"
    Raw Data: "{trend_data}"

    Mission:
    Identify the "Winning Content Format" right now in {current_year}.
    What are people watching TODAY regarding this topic?

    Report Structure (in Persian):

    📅 **وضعیت ترند (سال {current_year}):** (آیا الان داغ است؟)
    
    🔥 **فرمت برنده امروز:** (ویدیو باید چه شکلی باشد؟ آموزشی؟ طنز؟ ASMR؟)

    💡 **۳ ایده برای وایرال شدن:**
    1. 
    2. 
    3. 

    🔗 **لینک‌های رصد (فیلتر شده برای {current_year}):**
    🔹 تیک‌تاک: {tiktok_link}
    🔹 اینستاگرام: {instagram_link}
    🔹 یوتیوب: {youtube_link}
    🔹 توییتر: {twitter_link}
    🔹 گوگل ترندز: {gtrends_link}
    """
    
    return run_openrouter_request(prompt, [], openrouter_keys, agent_name="Strategist")

# ==========================================
# 4. سامبانووا (فیلتر)
# ==========================================
def agent_sambanova_filter(raw_data):
    if "Error" in raw_data or len(raw_data) < 10:
        return "No Data Found"
    
    headers = {"Authorization": f"Bearer {sambanova_keys.get_next_key()}", "Content-Type": "application/json"}
    models = ["Meta-Llama-3.1-70B-Instruct"]
    
    prompt = f"Analyze this social media text. Extract viral points relevant to {current_year}. Text: {raw_data[:2500]}"

    for model in models:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        try:
            response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception:
            continue
    return "No Data Scraped"
