from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import os

from agents import agent_gemini_expand, agent_sambanova_filter, agent_grok_analyze, agent_strategist
from telegram_bot import send_telegram_message
from hf_scraper import scrape_social_media

app = FastAPI(title="Trend Hunter AI Multi-Agent System")

class TrendRequest(BaseModel):
    domain: str
    keyword: str
    row_index: int

def run_multi_agent_pipeline(domain: str, keyword: str):
    send_telegram_message(f"🔍 <b>شکارچی بیدار شد!</b>\n🎯 هدف: {keyword}\n⏳ در حال ترجمه و اسکن جهانی...")
    
    try:
        # مرحله ۱: تبدیل کلمه فارسی به بهترین کوئری انگلیسی
        english_query = agent_gemini_expand(domain, keyword)
        english_query = english_query.replace('"', '').strip()
        
        # مرحله ۲: جستجو در اینترنت با کلمه انگلیسی از طریق هاگینگ فیس
        raw_data = scrape_social_media(english_query)
        if "Error" in raw_data or "خطا" in raw_data: 
            raw_data = "No live data found, use general knowledge."
        
        # مرحله ۳: تمیز کردن دیتا
        clean_data = agent_sambanova_filter(raw_data)
        
        # مرحله ۴: تحلیل نهایی
        final_report = agent_strategist(clean_data, keyword, english_query)
        
        # مرحله ۵: ارسال گزارش
        message = f"🔥 <b>گزارش ترند جهانی: {keyword}</b> 🔥\n(Search Query: {english_query})\n\n{final_report}"
        send_telegram_message(message)
        
    except Exception as e:
        send_telegram_message(f"⚠️ <b>خطا در سیستم:</b>\n{str(e)}")

@app.post("/api/start-hunt")
async def start_hunt(req: TrendRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_multi_agent_pipeline, req.domain, req.keyword)
    return {"status": "success", "message": f"Hunting started for {req.keyword}..."}

@app.get("/")
def home():
    return {"status": "alive", "message": "Bot is awake!"}

@app.get("/ping")
def ping():
    return {"status": "alive"}

if __name__ == "__main__":
    # مشکل پورت اینجا حل شد تا رندر ارور ندهد
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
