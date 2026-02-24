import requests
import json
import time
from key_rotator import openrouter_keys, gemini_keys, sambanova_keys, grok_keys
import google.generativeai as genai

# ==========================================
# تابع ارسال درخواست به OpenRouter (با سیستم گزارش خطای دقیق)
# ==========================================
def run_openrouter_request(prompt, models_list, key_manager, agent_name):
    # گرفتن کلید
    api_key = key_manager.get_next_key()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://trendhunter.ai",
        "X-Title": "TrendHunter"
    }
    
    error_log = [] # ذخیره خطاها برای نمایش به شما
    
    for model in models_list:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        try:
            print(f"[{agent_name}] Testing: {model} ...")
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
            else:
                # خطای دقیق را ذخیره می‌کنیم
                error_msg = f"Model {model} -> Status: {response.status_code}, Error: {response.text[:200]}"
                print(f"❌ {error_msg}")
                error_log.append(error_msg)
                
        except Exception as e:
            error_log.append(f"Model {model} -> Connection Error: {str(e)}")
            continue
    
    # اگر به اینجا رسیدیم یعنی همه مدل‌ها شکست خوردند
    # تمام خطاها را برمی‌گردانیم تا در تلگرام ببینید مشکل کجاست
    errors_string = "\n".join(error_log)
    raise Exception(f"خطای مدل‌های {agent_name}:\n{errors_string}")

# ==========================================
# 1. Gemini (اصلاح نام مدل برای جلوگیری از خطا)
# ==========================================
def agent_gemini_expand(domain, keyword):
    try:
        api_key = gemini_keys.get_next_key()
        genai.configure(api_key=api_key)
        # مدل 2.5 هنوز API عمومی ندارد، ما از قوی‌ترین مدل موجود (2.0 Flash Exp) استفاده می‌کنیم
        model = genai.GenerativeModel('gemini-2.5-flash') 
        prompt = f"من در حوزه '{domain}' کار میکنم. کلمه کلیدی من '{keyword}' است. 10 کلمه کلیدی مترادف انگلیسی و 10 هشتگ ترند جهانی برای تیک تاک و توییتر بده (فرمت JSON)."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"خطای جمینای: {str(e)}"

# ==========================================
# 3. Grok Agent (با اصلاح نام مدل‌ها برای OpenRouter)
# ==========================================
def agent_grok_analyze(data):
    models = [
        "moonshotai/moonshot-v1-8k",
        "meta-llama/llama-3.3-70b-instruct",
        "google/gemini-2.0-flash-exp:free"
    ]
    
    prompt = f"تو متخصص شبکه های اجتماعی هستی. این دیتای خام را بررسی کن و بگو آیا این موضوع در توییتر و تیک تاک در حال وایرال شدن است یا نه؟ دیتا: {data}"
    
    # ❌ خطای قبلی اینجا بود: grok_keys
    # ✅ کد صحیح: openrouter_keys
    return run_openrouter_request(prompt, models, openrouter_keys, agent_name="Grok_via_OpenRouter")

# ==========================================
# 4. Strategist Agent (مدل‌های درخواستی شما)
# ==========================================
def agent_strategist(trend_data):
    models = [
        "deepseek/deepseek-r1:free",           # جایگزین chimera (چون chimera گاهی در دسترس نیست)
        "nvidia/nemotron-3-8b-chat:free",      # نسخه پایدار نموترون
        "mistralai/mistral-small-24b-instruct-2501:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-chat"
    ]
    prompt = f"تو استراتژیست ارشد محتوا هستی. تحلیل ترند، عمر ترند و ایده محتوا به فارسی روان: {trend_data}"
    
    return run_openrouter_request(prompt, models, openrouter_keys, agent_name="Strategist")

# ==========================================
# 5. SambaNova Agent (مدل‌های درخواستی شما)
# ==========================================
def agent_sambanova_filter(raw_data):
    api_key = sambanova_keys.get_next_key()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    models = [
        "Meta-Llama-3.1-8B-Instruct",
        "Meta-Llama-3.1-70B-Instruct",
        "Meta-Llama-3.2-3B-Instruct"
    ]
    
    for model in models:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": f"خلاصه کن و دیتای مفید را نگه دار: {raw_data}"}]
        }
        try:
            response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception:
            continue
            
    return "خطا: تمام مدل‌های سامبانووا پاسخ ندادند."

