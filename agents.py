import requests
from key_rotator import openrouter_keys, gemini_keys, sambanova_keys
import google.generativeai as genai

# ==========================================
# 1. Gemini Agent (Expand Keywords) - gemini-2.5-flash
# ==========================================
def agent_gemini_expand(domain, keyword):
    api_key = gemini_keys.get_next_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"من در حوزه '{domain}' کار میکنم. کلمه کلیدی من '{keyword}' است. 10 کلمه کلیدی مترادف انگلیسی، 10 هشتگ ترند جهانی و اصطلاحات تخصصی برای سرچ در یوتیوب و تیک تاک را به صورت یک لیست JSON بده."
    
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# 2. OpenRouter Caller (Base function with Fallback)
# ==========================================
def call_openrouter(prompt, models_list):
    api_key = openrouter_keys.get_next_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for model in models_list:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"Model {model} failed. Trying next...")
        except Exception as e:
            print(f"Error with {model}: {e}")
            continue
            
    return "خطا: تمام مدل‌های این ایجنت شکست خوردند."

# ==========================================
# 3. Grok Agent (Social Media Expert)
# ==========================================
def agent_grok_analyze(data):
    models = [
        "moonshotai/kimi-k2-instruct-0905",
        "llama-3.3-70b-versatile" # Added fallback as requested
    ]
    prompt = f"تو متخصص شبکه های اجتماعی هستی. این دیتای خام را بررسی کن و بگو آیا این موضوع در توییتر و تیک تاک در حال وایرال شدن است یا نه؟ دیتا: {data}"
    return call_openrouter(prompt, models)

# ==========================================
# 4. Strategist Agent (OpenRouter Top Tier)
# ==========================================
def agent_strategist(trend_data):
    models = [
        "tng/deepseek-r1t-chimera:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "meta-llama/llama-4-scout:free",
        "mistralai/mistral-small-3.2-24b-instruct:free",
        "deepseek/deepseek-chat"
    ]
    prompt = f"تو استراتژیست ارشد محتوا هستی. بر اساس این دیتا، وضعیت ترند در وب فارسی و انگلیسی، پیشبینی عمر ترند و پکیج محتوایی برای پلتفرم های مختلف را به فارسی روان و جذاب بنویس: {trend_data}"
    return call_openrouter(prompt, models)

# ==========================================
# 5. SambaNova Agent (Garbage Filter)
# ==========================================
def agent_sambanova_filter(raw_data):
    api_key = sambanova_keys.get_next_key()
    # SambaNova uses OpenAI compatible endpoint structure
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
         "model": "Meta-Llama-3-8B-Instruct", # مدل رایگان و سریع سامبانووا
         "messages": [{"role": "user", "content": f"این دیتای خام شبکه های اجتماعی است. فقط اطلاعات مفید را نگه دار و نویزها و تبلیغات فیک را حذف کن. خلاصه کن: {raw_data}"}]
    }
    response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']