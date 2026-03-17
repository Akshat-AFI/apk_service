import json
import os
from datetime import datetime
from typing import Any, Dict, List
from app.core.apk_config import settings

def ensure_dirs():
    os.makedirs(settings.APK_OUTPUT_DIR, exist_ok=True)

def read_apk_list() -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.exists(settings.APK_LIST_FILE):
        with open(settings.APK_LIST_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    with open(settings.APK_LIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_apk_list(data: Dict[str, List[Dict[str, Any]]]):
    with open(settings.APK_LIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def create_lock_payload(lang_id: str, draft: bool) -> Dict[str, Any]:
    """Creates a JSON object representing the current APK build lock."""
    return {
        "lang_id": lang_id,
        "draft": draft,
        "started": datetime.utcnow().isoformat()
    }

def write_lock(payload: Dict[str, Any]):
    with open(settings.LOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f)

def clear_lock():
    try:
        os.remove(settings.LOCK_FILE)
    except FileNotFoundError:
        pass
