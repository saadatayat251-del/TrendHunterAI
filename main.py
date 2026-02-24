from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn

from agents import agent_gemini_expand, agent_sambanova_filter, agent_grok_analyze, agent_strategist
from telegram_bot import send_telegram_message
from hf_scraper import scrape_social_media

app = FastAPI(title="Trend Hunter AI Multi-Agent System")

class TrendRequest(BaseModel):
    domain: str
    keyword: str
    row_index: int

def run_multi_agent_pipeline(domain: str, keyword: str):
    send_telegram_message(f"🔍 <b>شکارچی بیدار شد!</b>\n🎯 هدف: {keyword}\n📂 حوزه: {domain}\n⏳ در حال تحلیل شبکه‌های جهانی...")
    
    try:
        # مرحله ۱
        expanded_kws = agent_gemini_expand(domain, keyword)
        if "خطا" in expanded_kws or "❌" in expanded_kws: raise Exception(f"گسترش کلمات متوقف شد: {expanded_kws}")
        
        # مرحله ۲
        raw_data = scrape_social_media(expanded_kws)
        if "Error" in raw_data or "خطا" in raw_data: raise Exception(f"سپر هاگینگ‌فیس دیتایی پیدا نکرد: {raw_data}")
        
        # مرحله ۳
        clean_data = agent_sambanova_filter(raw_data)
        if "خطا" in clean_data or "❌" in clean_data: raise Exception(f"فیلتر سامبانووا متوقف شد: {clean_data}")
        
        # مرحله ۴
        grok_analysis = agent_grok_analyze(clean_data)
        if "خطا" in grok_analysis or "❌" in grok_analysis: raise Exception(f"تحلیل گروک متوقف شد: {grok_analysis}")
        
        # مرحله ۵
        final_prompt = f"Cleaned Data: {clean_data}\n\nGrok Viral Analysis: {grok_analysis}\n\nTranslate and analyze for Persian audience."
        final_report = agent_strategist(final_prompt)
        if "خطا" in final_report or "❌" in final_report: raise Exception(f"استراتژیست متوقف شد: {final_report}")
        
        # مرحله ۶
        message = f"🔥 <b>گزارش نهایی ترند: {keyword}</b> 🔥\n\n{final_report}"
        send_telegram_message(message)
        
    except Exception as e:
        send_telegram_message(f"⚠️ <b>عملیات متوقف شد!</b>\n\n{str(e)}")

@app.post("/api/start-hunt")
async def start_hunt(req: TrendRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_multi_agent_pipeline, req.domain, req.keyword)
    return {"status": "success", "message": "Hunting started in background..."}

# اضافه شدن مسیر اصلی برای جلوگیری از خطای 404 در کرون‌جاب
@app.get("/")
def home():
    return {"status": "alive", "message": "TrendHunter Bot is running smoothly!"}

@app.get("/ping")
def ping():
    return {"status": "alive", "message": "I am awake!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
