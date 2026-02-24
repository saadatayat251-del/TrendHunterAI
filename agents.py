import requests
from key_rotator import openrouter_keys, gemini_keys, sambanova_keys, grok_keys
import google.generativeai as genai

# ==========================================
# تابع کمکی برای فراخوانی APIهای مشابه OpenRouter
# (این تابع هم برای گروک و هم برای استراتژیست استفاده می‌شود اما با کلیدهای جداگانه)
# ==========================================
def run_openrouter_style_api(prompt, models_list, key_manager, agent_name):
    # گرفتن کلید مخصوص همین ایجنت
    api_key = key_manager.get_next_key()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://trendhunter.ai", # هدر لازم برای برخی مدل‌های رایگان
        "X-Title": "TrendHunter"
    }
    
    # چرخش روی مدل‌های پیشنهادی شما
    for model in models_list:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            # ارسال درخواست
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
            
            # اگر این مدل کار نکرد، فقط چاپ کن و برو بعدی (بدون توقف)
            print(f"[{agent_name}] Model {model} failed with status {response.status_code}. Trying next...")
            
        except Exception as e:
            print(f"[{agent_name}] Connection error with {model}: {e}. Trying next...")
            continue
            
    # اگر تمام مدل‌ها شکست خوردند:
    return f"❌ خطا: تمام مدل‌های تعریف شده برای {agent_name} با شکست مواجه شدند."

# ==========================================
# 1. Gemini Agent (طبق دستور: gemini-2.5-flash)
# ==========================================
def agent_gemini_expand(domain, keyword):
    try:
        api_key = gemini_keys.get_next_key()
        genai.configure(api_key=api_key)
        # مدل درخواستی شما (اگر هنوز منتشر نشده باشد، به آخرین نسخه فلش سوییچ می‌کند)
        model = genai.GenerativeModel('gemini-2.5-flash') 
        prompt = f"من در حوزه '{domain}' کار میکنم. کلمه کلیدی من '{keyword}' است. 10 کلمه کلیدی مترادف انگلیسی، 10 هشتگ ترند جهانی و اصطلاحات تخصصی برای سرچ در یوتیوب و تیک تاک را به صورت یک لیست JSON بده."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ خطای جمینای: {str(e)}"

# ==========================================
# 3. Grok Agent (کلیدهای GROK_KEYS | مدل‌های خاص شما)
# ==========================================
def agent_grok_analyze(data):
    # دقیقاً مدل‌هایی که خواستی
    models = [
        "moonshotai/kimi-k2-instruct-0905",
        "llama-3.3-70b-versatile"
    ]
    prompt = f"تو متخصص شبکه های اجتماعی هستی. این دیتای خام را بررسی کن و بگو آیا این موضوع در توییتر و تیک تاک در حال وایرال شدن است یا نه؟ دیتا: {data}"
    
    # استفاده از کلیدهای اختصاصی گروک (GROK_KEYS)
    return run_openrouter_style_api(prompt, models, grok_keys, agent_name="Grok")

# ==========================================
# 4. Strategist Agent (کلیدهای OPENROUTER_KEYS | مدل‌های خاص شما)
# ==========================================
def agent_strategist(trend_data):
    # دقیقاً مدل‌هایی که خواستی به ترتیب
    models = [
        "tng/deepseek-r1t-chimera:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "meta-llama/llama-4-scout:free",
        "mistralai/mistral-small-3.2-24b-instruct:free",
        "deepseek/deepseek-chat"
    ]
    prompt = f"تو استراتژیست ارشد محتوا هستی. بر اساس این دیتا، وضعیت ترند در وب فارسی و انگلیسی، پیشبینی عمر ترند و پکیج محتوایی برای پلتفرم های مختلف را به فارسی روان و جذاب بنویس: {trend_data}"
    
    # استفاده از کلیدهای اختصاصی اوپن روتر (OPENROUTER_KEYS)
    return run_openrouter_style_api(prompt, models, openrouter_keys, agent_name="Strategist")

# ==========================================
# 5. SambaNova Agent (کلیدهای SAMBANOVA_KEYS | مدل‌های خاص شما)
# ==========================================
def agent_sambanova_filter(raw_data):
    api_key = sambanova_keys.get_next_key()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # دقیقاً مدل‌هایی که خواستی به ترتیب
    models = [
        "Meta-Llama-3.1-8B-Instruct",
        "Meta-Llama-3.1-70B-Instruct",
        "Meta-Llama-3.2-3B-Instruct"
    ]
    
    for model in models:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": f"این دیتای خام شبکه های اجتماعی است. فقط اطلاعات مفید را نگه دار و نویزها و تبلیغات فیک را حذف کن. خلاصه کن: {raw_data}"}]
        }
        try:
            # سامبانووا اندپوینت خاص خودش را دارد
            response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data:
                    return data['choices'][0]['message']['content']
            # اگر ارور داد برو بعدی
            print(f"[SambaNova] Model {model} failed ({response.status_code}). Trying next...")
        except Exception:
            continue
            
    return "❌ خطا: تمام مدل‌های سامبانووا پاسخ ندادند."
