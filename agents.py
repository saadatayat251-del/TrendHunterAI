import requests
from key_rotator import openrouter_keys, gemini_keys, sambanova_keys, grok_keys
import google.generativeai as genai

# ==========================================
# 1. Gemini
# ==========================================
def agent_gemini_expand(domain, keyword):
    try:
        api_key = gemini_keys.get_next_key()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"من در حوزه '{domain}' کار میکنم. کلمه کلیدی من '{keyword}' است. 10 کلمه کلیدی مترادف، هشتگ و اصطلاحات برای سرچ در شبکه های اجتماعی را با کاما جدا کن."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ خطای جمینای: {str(e)}"


# ==========================================
# 2. OpenRouter Caller (هسته مرکزی و مشترک با ایربگ قوی‌تر)
# ==========================================
def call_openrouter(prompt, models_list, agent_name="OpenRouter"):
    # اینجا فقط و فقط از متغیر OPENROUTER_KEYS استفاده می‌کنیم (چون می‌دانیم سالم است)
    api_key = openrouter_keys.get_next_key()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    for model in models_list:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
            print(f"[{agent_name}] Model {model} Error: {response.text}")
        except Exception as e:
            print(f"[{agent_name}] Connection error with {model}: {e}")
            continue
            
    return f"❌ خطای API: تمام مدل‌های {agent_name} شکست خوردند. مطمئن شوید در OPENROUTER_KEYS کلیدهای معتبر دارید."

# ==========================================
# 3. Grok (تحلیل وایرال)
# ==========================================
def agent_grok_analyze(data):
    # پایدارترین مدل‌های 100% رایگان
    models = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "qwen/qwen-2-7b-instruct:free"
    ]
    prompt = f"تو متخصص شبکه های اجتماعی هستی. این دیتای خام را بررسی کن و فقط بگو آیا در توییتر و تیک تاک پتانسیل وایرال شدن دارد یا نه؟ (کوتاه جواب بده). دیتا: {data}"
    return call_openrouter(prompt, models, agent_name="Grok")

# ==========================================
# 4. Strategist (استراتژیست ارشد)
# ==========================================
def agent_strategist(trend_data):
    # پایدارترین مدل‌های 100% رایگان برای تولید محتوای طولانی
    models = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free"
    ]
    prompt = f"تو استراتژیست ارشد محتوا هستی. بر اساس این دیتا، وضعیت ترند، پیشبینی عمر و پکیج محتوایی را به فارسی روان و جذاب بنویس: {trend_data}"
    return call_openrouter(prompt, models, agent_name="Strategist")
# ==========================================
# 5. SambaNova (فیلتر زباله) - آپدیت شده با مدل‌های جدید
# ==========================================
def agent_sambanova_filter(raw_data):
    try:
        api_key = sambanova_keys.get_next_key()
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        # لیست مدل‌های جدید، سریع و کاملاً رایگان سامبانووا
        models = [
            "Meta-Llama-3.1-8B-Instruct",   # فوق‌سریع برای فیلتر کردن
            "Meta-Llama-3.1-70B-Instruct",  # مدل قدرتمندتر
            "Meta-Llama-3.2-3B-Instruct"    # جدیدترین مدل سبک
        ]
        
        for model in models:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": f"این دیتای خام شبکه های اجتماعی است. فقط اطلاعات مفید را نگه دار و نویزها و تبلیغات فیک را حذف کن. خلاصه کن: {raw_data}"}]
            }
            
            response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
            else:
                # اگر این مدل 404 داد، پرینت می‌گیریم که در لاگ رندر ببینیم و می‌رویم سراغ مدل بعدی
                print(f"SambaNova Model {model} failed with status {response.status_code}")
                continue
                
        return f"❌ خطای سامبانووا: تمام مدل‌های رایگان تست شدند اما جواب ندادند. آخرین ارور: {response.status_code}"
    except Exception as e:
        return f"❌ خطای اتصال سامبانووا: {str(e)}"





