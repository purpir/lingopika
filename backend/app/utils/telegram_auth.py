import hashlib
import hmac
import json
import urllib.parse
from typing import Optional, Dict

from app.config import settings


def validate_init_data(init_data: str, bot_token: str | None = None) -> Optional[Dict]:
    if not init_data:
        return None
    token = bot_token or settings.TELEGRAM_BOT_TOKEN
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        return None
    if "hash" not in parsed:
        return None
    received_hash = parsed.pop("hash")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, received_hash):
        if settings.DEBUG and not token:
            pass
        else:
            return None
    user_raw = parsed.get("user")
    if user_raw:
        try:
            parsed["user"] = json.loads(user_raw)
        except Exception:
            pass
    return parsed


def extract_telegram_user(init_data: str) -> Optional[Dict]:
    data = validate_init_data(init_data)
    if not data:
        return None
    return data.get("user") if isinstance(data.get("user"), dict) else None
