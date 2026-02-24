import os
import itertools
from dotenv import load_dotenv

load_dotenv()

class KeyManager:
    def __init__(self, env_var_name):
        keys_string = os.getenv(env_var_name, "")
        keys_list = [k.strip() for k in keys_string.split(',') if k.strip()]
        if not keys_list:
            raise ValueError(f"No keys found for {env_var_name}")
        # ایجاد یک چرخه بی‌نهایت از کلیدها
        self.key_cycle = itertools.cycle(keys_list)

    def get_next_key(self):
        return next(self.key_cycle)

# ساخت منیجرها برای هر هوش مصنوعی
gemini_keys = KeyManager("GEMINI_KEYS")
openrouter_keys = KeyManager("OPENROUTER_KEYS")
sambanova_keys = KeyManager("SAMBANOVA_KEYS")
# گروک کاملا حذف شد
