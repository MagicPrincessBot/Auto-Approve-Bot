from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from configs import cfg
import sys

try:
    client = MongoClient(cfg.MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("✅ MongoDB connected successfully.")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

users    = client["main"]["users"]
groups   = client["main"]["groups"]
settings = client["main"]["settings"]  # stores bot-wide config (custom text, etc.)

# ──────────────────────────── users / groups ───────────────────────────────

def already_db(user_id: int) -> bool:
    return bool(users.find_one({"user_id": str(user_id)}))

def already_dbg(chat_id: int) -> bool:
    return bool(groups.find_one({"chat_id": str(chat_id)}))

def add_user(user_id: int):
    if not already_db(user_id):
        users.insert_one({"user_id": str(user_id)})

def remove_user(user_id: int):
    if already_db(user_id):
        users.delete_one({"user_id": str(user_id)})

def add_group(chat_id: int):
    if not already_dbg(chat_id):
        groups.insert_one({"chat_id": str(chat_id)})

def all_users() -> int:
    return users.count_documents({})

def all_groups() -> int:
    return groups.count_documents({})

# ──────────────────────────── custom welcome text ─────────────────────────

_WELCOME_KEY = "welcome_text"

def set_custom_text(text: str) -> None:
    """Save (or overwrite) the custom approval DM text in the DB."""
    settings.update_one(
        {"key": _WELCOME_KEY},
        {"$set": {"key": _WELCOME_KEY, "value": text}},
        upsert=True,
    )

def get_custom_text() -> str | None:
    """Return the stored custom text, or None if not set."""
    doc = settings.find_one({"key": _WELCOME_KEY})
    return doc["value"] if doc else None

def clear_custom_text() -> None:
    """Delete the custom text — bot falls back to the default message."""
    settings.delete_one({"key": _WELCOME_KEY})
