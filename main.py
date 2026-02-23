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
    # 0. اعلام بیداری به تلگرام
    send_telegram_message(f"🔍 <b>شکارچی بیدار شد!</b>\n🎯 هدف: {keyword}\n📂 حوزه: {domain}\n⏳ در حال تحلیل شبکه‌های جهانی...")
    
    try:
        # 1. Gemini: Expand Keywords
        expanded_kws = agent_gemini_expand(domain, keyword)
        
        # 2. HuggingFace Proxies: Scrape Data
        raw_data = scrape_social_media(expanded_kws)
        
        # 3. SambaNova: Filter Garbage
        clean_data = agent_sambanova_filter(raw_data)
        
        # 4. Grok: Real-time Viral Check
        grok_analysis = agent_grok_analyze(clean_data)
        
        # 5. OpenRouter (Strategist): Final Content Strategy
        final_prompt = f"Cleaned Data: {clean_data}\n\nGrok Viral Analysis: {grok_analysis}\n\nTranslate and analyze for Persian audience."
        final_report = agent_strategist(final_prompt)
        
        # 6. Send Final Result to Telegram
        message = f"🔥 <b>گزارش نهایی ترند: {keyword}</b> 🔥\n\n{final_report}"
        send_telegram_message(message)
        
    except Exception as e:
        send_telegram_message(f"❌ <b>خطا در پردازش:</b>\n{str(e)}")

@app.post("/api/start-hunt")
async def start_hunt(req: TrendRequest, background_tasks: BackgroundTasks):
    # اجرای پروسه در پس‌زمینه تا گوگل شیت تایم‌اوت ندهد
    background_tasks.add_task(run_multi_agent_pipeline, req.domain, req.keyword)
    return {"status": "success", "message": "Hunting started in background..."}

@app.get("/ping")
def ping():
    # این مسیر برای بیدار نگه داشتن سرور توسط Cron-job است
    return {"status": "alive", "message": "I am awake!"}

# این بخش برای تست روی سیستم خودت است (روی رندر نادیده گرفته می‌شود)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)