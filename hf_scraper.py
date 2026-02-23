import requests
import random

# اینجا بعداً آدرس اسپیس‌های رایگانی که در هاگینگ‌فیس می‌سازیم را قرار می‌دهیم
PROXITOK_SPACES = ["https://example-space1.hf.space"] 
SQUAWKER_SPACES = ["https://example-space2.hf.space"]

def scrape_social_media(expanded_keywords):
    """
    این تابع کلمات کلیدی گسترش یافته را می‌گیرد و از طریق پروکسی‌های هاگینگ فیس
    دیتای خام را استخراج می‌کند. 
    """
    # فعلاً برای اینکه سرور ران شود، یک دیتای شبیه‌سازی شده برمی‌گردانیم.
    # در فاز بعدی، کدهای اتصال به هاگینگ‌فیس را اینجا جایگزین می‌کنیم.
    mock_raw_data = f"Raw trending data scraped for: {expanded_keywords}. Lots of mentions about aesthetics, new fashion lines, and viral tiktok sounds."
    
    return mock_raw_data