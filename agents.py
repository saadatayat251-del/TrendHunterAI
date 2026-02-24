import requests
from key_rotator import openrouter_keys, sambanova_keys
import google.generativeai as genai

# ==========================================
# تابع ارسال درخواست به OpenRouter
# ==========================================
def run_openrouter_request(prompt, models_list, key_manager, agent_name):
    api_key = key_manager.get_next_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    error_log = []
    for model in models_list:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=45)
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data:
                    return data['choices'][0]['message']['content']
            else:
                error_log.append(f"{model} -> {response.status_code}")
        except Exception as e:
            error_log.append(f"{model} -> {str(e)}")
            continue
            
    raise Exception(f"خطای مدل‌های {agent_name}:\n" + "\n".join(error_log))

# ==========================================
# 1. Keyword Expander (جایگزین جمینای)
# ==========================================
def agent_gemini_expand(domain, keyword):
    # استفاده از مسیریاب هوشمند و اتوماتیک اوپن‌روتر
    models = ["openrouter/free"]
    
    prompt = f"من در حوزه '{domain}' کار میکنم. کلمه کلیدی من '{keyword}' است. 10 کلمه کلیدی مترادف انگلیسی و 10 هشتگ ترند جهانی برای تیک تاک و توییتر بده (فقط خروجی را با فرمت JSON بده و هیچ توضیح اضافه‌ای ننویس)."
    
    return run_openrouter_request(prompt, models, openrouter_keys, agent_name="Keyword_Expander")

# ==========================================
# 2. Grok Analyzer (تحلیل وایرال)
# ==========================================
def agent_grok_analyze(data):
    models = ["openrouter/free"]
    prompt = f"بررسی کن آیا این موضوع در توییتر/تیک‌تاک وایرال است؟ دیتا: {data}"
    return run_openrouter_request(prompt, models, openrouter_keys, agent_name="Grok_via_OpenRouter")

# ==========================================
# 3. Strategist Agent (استراتژی نهایی)
# ==========================================
def agent_strategist(trend_data):
    models = ["openrouter/free"]
    prompt = f"به عنوان استراتژیست، تحلیل ترند، عمر ترند و ایده محتوا به فارسی روان بنویس: {trend_data}"
    return run_openrouter_request(prompt, models, openrouter_keys, agent_name="Strategist")

# ==========================================
# 4. SambaNova Agent (فیلتر دیتا)
# ==========================================
def agent_sambanova_filter(raw_data):
    headers = {"Authorization": f"Bearer {sambanova_keys.get_next_key()}", "Content-Type": "application/json"}
    models = ["Meta-Llama-3.1-8B-Instruct", "Meta-Llama-3.1-70B-Instruct"]
    
    for model in models:
        payload = {"model": model, "messages": [{"role": "user", "content": f"خلاصه کن و دیتای مفید را نگه دار: {raw_data}"}]}
        try:
            response = requests.post("https://api.sambanova.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except Exception:
            continue
    return "خطا: تمام مدل‌های سامبانووا پاسخ ندادند."
