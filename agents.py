import requests
from key_rotator import openrouter_keys, gemini_keys, sambanova_keys
import google.generativeai as genai

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
            error_log.append(f"{model} -> {e}")
            continue
    raise Exception(f"خطای مدل‌های {agent_name}:\n" + "\n".join(error_log))

def agent_gemini_expand(domain, keyword):
    try:
        genai.configure(api_key=gemini_keys.get_next_key())
        model = genai.GenerativeModel('gemini-2.5-flash') 
        response = model.generate_content(f"حوزه: '{domain}'. کلمه: '{keyword}'. 10 کلمه مترادف و هشتگ ترند جهانی بده.")
        return response.text
    except Exception as e:
        return f"خطای جمینای: {str(e)}"

def agent_grok_analyze(data):
    models = ["moonshotai/moonshot-v1-8k", "meta-llama/llama-3.3-70b-instruct"]
    prompt = f"بررسی کن آیا این موضوع در توییتر/تیک‌تاک وایرال است؟ دیتا: {data}"
    return run_openrouter_request(prompt, models, openrouter_keys, "Grok_via_OpenRouter")

def agent_strategist(trend_data):
    models = ["deepseek/deepseek-r1:free", "nvidia/nemotron-3-8b-chat:free", "mistralai/mistral-small-24b-instruct-2501:free"]
    prompt = f"به عنوان استراتژیست، تحلیل ترند، عمر ترند و ایده محتوا به فارسی روان بنویس: {trend_data}"
    return run_openrouter_request(prompt, models, openrouter_keys, "Strategist")

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

