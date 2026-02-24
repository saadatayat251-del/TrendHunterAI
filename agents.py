import requests
from key_rotator import openrouter_keys, gemini_keys, sambanova_keys, grok_keys
import google.generativeai as genai

# ==========================================
# 1. Gemini Agent (گسترش کلمات)
# ==========================================
def agent_gemini_expand(domain, keyword):
    try:
        api_key = gemini_keys.get_next_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"من در حوزه '{domain}' کار میکنم. کلمه کلیدی من '{keyword}' است. 10 کلمه کلیدی مترادف انگلیسی، 10 هشتگ ترند جهانی و اصطلاحات تخصصی برای سرچ در یوتیوب و تیک تاک را به صورت یک لیست JSON بده."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ خطای جمینای: {str(e)}"

# ==========================================
# 2. OpenRouter Caller (هسته مرکزی فراخوانی مدل‌ها)
# ==========================================
def call_openrouter(prompt, models_list, agent_name="OpenRouter"):
    # استفاده از کلیدهای OpenRouter برای تمام مراحل
    api_key = openrouter_keys.get_next_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://trendhunter.ai", # برخی مدل‌های رایگان نیاز به این هدر دارند
        "X-Title": "TrendHunter"
    }
    
    for model in models_list:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            # تنظیمات برای مدل‌های رایگان جهت جلوگیری از خطا
            "temperature": 0.7,
            "max_tokens": 1000 
        }
        try:
            print(f"[{agent_name}] Testing model: {model} ...")
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=40)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
                else:
                     print(f"[{agent_name}] Model {model} empty response.")
            else:
                # لاگ کردن دقیق خطا برای دیباگ
                print(f"[{agent_name}] Model {model} Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"[{agent_name}] Connection error with {model}: {e}")
            continue
            
    return f"❌ خطای API: تمام مدل‌های {agent_name} شکست خوردند. لیست مدل‌ها را چک کنید."

# ==========================================
# 3. Grok Agent (تحلیل وایرال - با مدل‌های درخواستی شما)
# ==========================================
def agent_grok_analyze(data):
    # لیست اولویت‌بندی شده طبق دستور شما برای Grok
    models = [
        "moonshotai/kimi-k2-instruct-0905",  # اولویت اول شما
        "llama-3.3-70b-versatile",           # اولویت دوم شما
        "google/gemini-2.0-flash-exp:free",  # مدل پشتیبان (رایگان و قوی)
        "meta-llama/llama-3.2-3b-instruct:free" # مدل پشتیبان دوم
    ]
    prompt = f"تو متخصص شبکه های اجتماعی هستی. این دیتای خام را بررسی کن و بگو آیا این موضوع در توییتر و تیک تاک در حال وایرال شدن است یا نه؟ دیتا: {data}"
    return call_openrouter(prompt, models, agent_name="Grok")

# ==========================================
# 4. Strategist Agent (استراتژیست ارشد - با لیست جدید شما)
# ==========================================
def agent_strategist(trend_data):
    # لیست دقیق مدل‌های پیشنهادی شما
    models = [
        "tng/deepseek-r1t-chimera:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "mistralai/mistral-small-24b-instruct-2501:free", # اصلاح نام دقیق مسترال
        "meta-llama/llama-3.3-70b-instruct:free", # جایگزین لاما 4 (چون لاما 4 هنوز نیامده)
        "deepseek/deepseek-chat:free", # نسخه رایگان دیپ‌سیک
        "google/gemini-2.0-flash-exp:free" # سوپاپ اطمینان نهایی
    ]
    prompt = f"تو استراتژیست ارشد محتوا هستی. بر اساس این دیتا، وضعیت ترند در وب فارسی و انگلیسی، پیشبینی عمر ترند و پکیج محتوایی برای پلتفرم های مختلف را به فارسی روان و جذاب بنویس: {trend_data}"
    return call_openrouter(prompt, models, agent_name="Strategist")

# ==========================================
# 5. SambaNova Agent (فیلتر زباله)
# ==========================================
def agent_sambanova_filter(raw_data):
    try:
        api_key = sambanova_keys.get_next_key()
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        # مدل‌های جدید و فعال سامبانووا
        models = [
            "Meta-Llama-3.1-8B-Instruct",
            "Meta-Llama-3.1-70B-Instruct",
            "Meta-Llama-3.2-3B-Instruct"
        ]
        
        for model in models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": f"این دیتای خام است. فقط اطلاعات مفید را نگه دار و خلاصه کن: {raw_data}"}]
            }
            response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data:
                    return data['choices'][0]['message']['content']
            
        return "خطا در سامبانووا: هیچ مدلی پاسخ نداد."
    except Exception as e:
        return f"خطای اتصال سامبانووا: {str(e)}"
