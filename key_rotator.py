import os
import itertools
from dotenv import load_dotenv

load_dotenv()

class KeyManager:
    def __init__(self, env_var_name):
        self.env_var_name = env_var_name
        keys_string = os.getenv(env_var_name, "")
        keys_list = [k.strip() for k in keys_string.split(',') if k.strip()]
        
        if not keys_list:
            self.key_cycle = itertools.cycle(["MISSING"])
        else:
            self.key_cycle = itertools.cycle(keys_list)

    def get_next_key(self):
        key = next(self.key_cycle)
        if key == "MISSING":
            raise ValueError(f"❌ کلیدهای {self.env_var_name} در بخش Environment رندر وارد نشده‌اند!")
        return key

gemini_keys = KeyManager("GEMINI_KEYS")
openrouter_keys = KeyManager("OPENROUTER_KEYS")
sambanova_keys = KeyManager("SAMBANOVA_KEYS")
